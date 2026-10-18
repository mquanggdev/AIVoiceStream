"""Import một bộ data v3 vào DB: thay thế toàn bộ catalog, chunk và (tùy chọn) embed knowledge."""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from src.config import get_settings
from src.dataset.loader import Dataset, load_dataset
from src.dataset.validate import validate_dataset
from src.models.entities import (
    Building,
    DatasetVersion,
    KnowledgeChunk,
    KnowledgeDoc,
    SalesPolicy,
    Subdivision,
    Unit,
)

logger = logging.getLogger(__name__)

CHUNK_TARGET_WORDS = 220


class DatasetValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("Data không hợp lệ:\n" + "\n".join(errors[:30]))
        self.errors = errors


def _bool(value) -> bool | None:
    if value in (None, ""):
        return None
    return str(value).strip().lower() in ("true", "1", "yes")


def _int(value) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def _float(value) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _date(value) -> date | None:
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def chunk_document(title: str, content: str, target_words: int = CHUNK_TARGET_WORDS) -> list[str]:
    """Chia theo đoạn văn, gộp đến ~target_words; mỗi chunk có tiêu đề để giữ ngữ cảnh."""
    paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    words = 0
    for paragraph in paragraphs:
        size = len(paragraph.split())
        if current and words + size > target_words:
            chunks.append(" ".join(current))
            # overlap: giữ lại đoạn cuối để chunk sau không mất mạch
            current, words = [current[-1]], len(current[-1].split())
        current.append(paragraph)
        words += size
    if current:
        chunks.append(" ".join(current))
    return [f"{title}. {chunk}" for chunk in chunks]


def current_dataset(session: Session) -> DatasetVersion | None:
    return session.scalar(
        select(DatasetVersion).where(DatasetVersion.is_active.is_(True)).order_by(DatasetVersion.id.desc())
    )


def import_dataset(session: Session, ds: Dataset, *, skip_validation: bool = False) -> DatasetVersion:
    if not skip_validation:
        report = validate_dataset(ds)
        if not report.ok:
            raise DatasetValidationError(report.errors)

    # Xóa catalog cũ (thứ tự theo khóa ngoại)
    for model in (KnowledgeChunk, KnowledgeDoc, SalesPolicy, Unit, Building, Subdivision):
        session.execute(delete(model))
    session.flush()

    sub_ids: dict[str, int] = {}
    for order, item in enumerate(ds.subdivisions, start=1):
        sub = Subdivision(
            slug=item["subdivision_slug"],
            name=item["name"],
            aliases=item.get("aliases") or [],
            parent_zone=item.get("parent_zone"),
            developer=item.get("developer") or "",
            design_style=item.get("design_style"),
            num_buildings=item.get("num_buildings"),
            total_units=item.get("total_units"),
            handover_status=item.get("handover_status") or "unknown",
            handover_date=item.get("handover_date"),
            handover_standard=item.get("handover_standard"),
            handover_standard_detail=item.get("handover_standard_detail"),
            ownership=item.get("ownership"),
            location_text=item.get("location_text"),
            internal_amenities=item.get("internal_amenities") or [],
            external_amenities=item.get("external_amenities") or [],
            price_per_m2_min_vnd=item.get("price_per_m2_min_vnd"),
            price_per_m2_max_vnd=item.get("price_per_m2_max_vnd"),
            management_fee_per_m2_vnd=item.get("management_fee_per_m2_vnd"),
            display_order=order,
            source_url=item.get("source_url"),
            crawled_at=item.get("crawled_at"),
        )
        session.add(sub)
        session.flush()
        sub_ids[sub.slug] = sub.id

    building_ids: dict[str, int] = {}
    for item in ds.buildings:
        building = Building(
            code=item["building_code"],
            subdivision_id=sub_ids[item["subdivision_slug"]],
            aliases=item.get("aliases") or [],
            num_floors=item.get("num_floors"),
            units_per_floor=item.get("units_per_floor"),
            num_elevators=item.get("num_elevators"),
            handover_status=item.get("handover_status"),
            handover_date=item.get("handover_date"),
            source_url=item.get("source_url"),
        )
        session.add(building)
        session.flush()
        building_ids[building.code] = building.id

    unit_rows = [
        {
            "unit_code": row["unit_code"],
            "unit_code_original": row.get("unit_code_original") or None,
            "subdivision_id": sub_ids[row["subdivision_slug"]],
            "building_id": building_ids[row["building_code"]],
            "floor": int(row["floor"]),
            "floor_label": row.get("floor_label") or None,
            "unit_type": row["unit_type"],
            "bedrooms": _int(row.get("bedrooms")),
            "bathrooms": _int(row.get("bathrooms")),
            "area_gross_m2": _float(row.get("area_gross_m2")),
            "area_net_m2": float(row["area_net_m2"]),
            "door_direction": row.get("door_direction") or None,
            "balcony_direction": row.get("balcony_direction") or None,
            "views": [v for v in (row.get("views") or "").split("|") if v],
            "corner_unit": bool(_bool(row.get("corner_unit"))),
            "furnishing": row.get("furnishing") or None,
            "price_vnd": _int(row.get("price_vnd")),
            "price_includes_vat": _bool(row.get("price_includes_vat")),
            "price_includes_maintenance": _bool(row.get("price_includes_maintenance")),
            "price_type": row.get("price_type") or None,
            "price_date": _date(row.get("price_date")),
            "status": row.get("status") or "unknown",
            "source_url": row.get("source_url"),
        }
        for row in ds.units
    ]
    for start in range(0, len(unit_rows), 2000):
        session.execute(insert(Unit), unit_rows[start : start + 2000])

    for item in ds.sales_policies:
        session.add(
            SalesPolicy(
                policy_id=item["policy_id"],
                subdivision_id=sub_ids[item["subdivision_slug"]],
                policy_type=item.get("policy_type") or "other",
                title=item["title"],
                content=item["content"],
                discount_percent=item.get("discount_percent"),
                valid_from=_date(item.get("valid_from")),
                valid_to=_date(item.get("valid_to")),
                source_url=item.get("source_url"),
            )
        )

    chunk_count = 0
    for item in ds.knowledge_docs:
        slug = item.get("subdivision_slug")
        doc = KnowledgeDoc(
            doc_id=item["doc_id"],
            subdivision_id=sub_ids.get(slug) if slug else None,
            topic=item.get("topic") or "overview",
            title=item["title"],
            content=item["content"],
            source_url=item.get("source_url"),
        )
        session.add(doc)
        session.flush()
        for index, text in enumerate(chunk_document(doc.title, doc.content)):
            session.add(
                KnowledgeChunk(
                    chunk_id=f"{doc.doc_id}#{index}",
                    doc_id=doc.id,
                    subdivision_id=doc.subdivision_id,
                    topic=doc.topic,
                    title=doc.title,
                    chunk_index=index,
                    content=text,
                )
            )
            chunk_count += 1

    session.execute(update(DatasetVersion).values(is_active=False))
    version = DatasetVersion(
        version=ds.version,
        is_demo=ds.is_demo,
        dataset_dir=str(ds.root).replace("\\", "/"),
        counts={
            "subdivisions": len(ds.subdivisions),
            "buildings": len(ds.buildings),
            "units": len(ds.units),
            "sales_policies": len(ds.sales_policies),
            "knowledge_docs": len(ds.knowledge_docs),
            "knowledge_chunks": chunk_count,
        },
        project=ds.project,
        notes=ds.manifest.get("notes"),
        is_active=True,
    )
    session.add(version)
    session.commit()
    logger.info("Imported dataset %s (%s units, %s chunks)", ds.version, len(ds.units), chunk_count)
    return version


async def embed_missing_chunks(session: Session) -> int:
    """Tính embedding cho chunk chưa có (hoặc khác model). Trả về số chunk đã embed."""
    from src.ai.embeddings import embed_texts

    model = get_settings().embedding_model
    chunks = list(
        session.scalars(
            select(KnowledgeChunk).where(
                (KnowledgeChunk.embedding.is_(None)) | (KnowledgeChunk.embedding_model != model)
            )
        ).all()
    )
    if not chunks:
        return 0
    vectors = await embed_texts([chunk.content for chunk in chunks])
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk.embedding = vector
        chunk.embedding_model = model
    version = current_dataset(session)
    if version is not None:
        version.embedding_model = model
    session.commit()
    return len(chunks)


def ensure_dataset(session: Session) -> DatasetVersion | None:
    """Gọi khi khởi động: import bộ data cấu hình nếu DB chưa có hoặc khác phiên bản."""
    settings = get_settings()
    active = current_dataset(session)
    try:
        ds = load_dataset(settings.dataset_dir)
    except FileNotFoundError as exc:
        logger.warning("Không tìm thấy dataset: %s", exc)
        return active
    if active is not None and active.version == ds.version and active.dataset_dir == str(ds.root).replace("\\", "/"):
        return active
    return import_dataset(session, ds)
