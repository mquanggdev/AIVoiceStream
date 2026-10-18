import pytest
from sqlalchemy import func, select

from src.dataset.importer import chunk_document, current_dataset
from src.dataset.loader import load_dataset
from src.dataset.validate import validate_dataset
from src.models.entities import KnowledgeChunk, Unit
from src.retrieval import catalog
from src.retrieval.knowledge import search_knowledge
from src.retrieval.resolver import normalize_unit_code, resolve_subdivision, resolve_subdivisions


def test_demo_dataset_passes_validation():
    report = validate_dataset(load_dataset("cleaned_data/demo_v3"))
    assert report.errors == []


def test_dataset_imported_on_startup(db):
    version = current_dataset(db)
    assert version is not None and version.is_demo
    assert db.scalar(select(func.count(Unit.id))) == version.counts["units"] > 10_000
    assert db.scalar(select(func.count(KnowledgeChunk.id))) >= 95


def test_chunk_document_keeps_title_and_splits_long_text():
    paragraphs = "\n".join(["câu " * 120] * 4)
    chunks = chunk_document("Tiêu đề", paragraphs, target_words=200)
    assert len(chunks) >= 2
    assert all(chunk.startswith("Tiêu đề.") for chunk in chunks)


@pytest.mark.parametrize(
    ("heard", "slug"),
    [
        ("dần pác", "the-zenpark"),
        ("zen park", "the-zenpark"),
        ("sa phia", "the-sapphire"),
        ("lếch sai", "masteri-lakeside"),
        ("giu rích", "the-zurich"),
        ("pa ri", "the-paris"),
        ("căn ở khu pavilion", "the-pavilion"),
    ],
)
def test_resolve_misheard_subdivision_names(db, heard, slug):
    assert resolve_subdivisions(db, heard)[0].slug == slug


def test_resolve_unknown_name_returns_nothing(db):
    assert resolve_subdivision(db, "Times City")[0] is None


@pytest.mark.parametrize("raw", ["R1.01-1205", "r1011205", "R1.01 1205"])
def test_normalize_unit_code(db, raw):
    assert normalize_unit_code(db, raw) == "R1.01-1205"


def test_search_units_respects_filters_and_exposes_spoken_price(db):
    sub, _ = resolve_subdivision(db, "zenpark")
    result = catalog.search_units(db, subdivision=sub, unit_type="2PN", budget_max=4_500_000_000, limit=5)
    assert result["total_matches"] > 0
    for unit in result["units"]:
        row = catalog.get_unit(db, unit["unit_code"])
        assert row.subdivision_id == sub.id and row.unit_type == "2PN" and row.status == "available"
        assert row.price_vnd <= 4_500_000_000 and unit["price_vnd"] == row.price_vnd
        assert unit["price_spoken"] and unit["price_text"].endswith("tỷ")
    prices = [u["price_vnd"] for u in result["units"]]
    assert prices == sorted(prices)


def test_active_policies_excludes_expired(db):
    sub, _ = resolve_subdivision(db, "lakeside")
    policies = catalog.active_policies(db, sub)
    titles = [p["title"] for p in policies["active_policies"]]
    assert "Ưu đãi mở bán quý 2/2026" not in titles  # hết hạn 2026-06-30
    assert policies["expired_or_not_started_count"] >= 1


async def test_knowledge_search_bm25_without_embeddings(db):
    results = await search_knowledge(db, "vườn Nhật hồ cá koi", use_embedding=False)
    assert any("zenpark" in r["chunk_id"] for r in results)
