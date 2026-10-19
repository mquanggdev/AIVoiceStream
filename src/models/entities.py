"""ORM schema v3 — Ocean Park Voice Agent.

- Catalog theo đặc tả `docs/data_spec_v3.md`: phân khu → tòa → căn, chính sách, knowledge.
- Cuộc gọi voice: `conversations` (1 cuộc gọi) + `messages` (mỗi lượt Khách/AI, kèm ghi âm).
- `customers`: thông tin khách để lại qua giọng nói, admin xem được.
"""

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Catalog ──────────────────────────────────────────────────────────────────


class DatasetVersion(Base):
    """Mỗi lần import một bộ data (demo hoặc thật)."""

    __tablename__ = "dataset_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(50), index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    dataset_dir: Mapped[str] = mapped_column(String(500))
    counts: Mapped[dict] = mapped_column(JSON, default=dict)
    project: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    embedding_model: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Subdivision(Base):
    __tablename__ = "subdivisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    parent_zone: Mapped[str | None] = mapped_column(String(255))
    developer: Mapped[str] = mapped_column(String(255))
    design_style: Mapped[str | None] = mapped_column(String(255))
    num_buildings: Mapped[int | None] = mapped_column(Integer)
    total_units: Mapped[int | None] = mapped_column(Integer)
    handover_status: Mapped[str] = mapped_column(String(30), default="unknown")
    handover_date: Mapped[str | None] = mapped_column(String(20))
    handover_standard: Mapped[str | None] = mapped_column(String(30))
    handover_standard_detail: Mapped[str | None] = mapped_column(Text)
    ownership: Mapped[str | None] = mapped_column(String(30))
    location_text: Mapped[str | None] = mapped_column(Text)
    internal_amenities: Mapped[list] = mapped_column(JSON, default=list)
    external_amenities: Mapped[list] = mapped_column(JSON, default=list)
    price_per_m2_min_vnd: Mapped[int | None] = mapped_column(BigInteger)
    price_per_m2_max_vnd: Mapped[int | None] = mapped_column(BigInteger)
    management_fee_per_m2_vnd: Mapped[int | None] = mapped_column(Integer)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    source_url: Mapped[str | None] = mapped_column(String(500))
    crawled_at: Mapped[str | None] = mapped_column(String(40))

    buildings: Mapped[list["Building"]] = relationship(back_populates="subdivision", cascade="all, delete-orphan")


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    num_floors: Mapped[int | None] = mapped_column(Integer)
    units_per_floor: Mapped[int | None] = mapped_column(Integer)
    num_elevators: Mapped[int | None] = mapped_column(Integer)
    handover_status: Mapped[str | None] = mapped_column(String(30))
    handover_date: Mapped[str | None] = mapped_column(String(20))
    source_url: Mapped[str | None] = mapped_column(String(500))

    subdivision: Mapped[Subdivision] = relationship(back_populates="buildings")


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        Index("ix_units_search", "subdivision_id", "unit_type", "status"),
        Index("ix_units_price", "price_vnd"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    unit_code_original: Mapped[str | None] = mapped_column(String(60))
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"))
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id", ondelete="CASCADE"), index=True)
    floor: Mapped[int] = mapped_column(Integer)
    floor_label: Mapped[str | None] = mapped_column(String(10))
    unit_type: Mapped[str] = mapped_column(String(20))
    bedrooms: Mapped[int | None] = mapped_column(Integer)
    bathrooms: Mapped[int | None] = mapped_column(Integer)
    area_gross_m2: Mapped[float | None] = mapped_column(Float)
    area_net_m2: Mapped[float] = mapped_column(Float)
    door_direction: Mapped[str | None] = mapped_column(String(4))
    balcony_direction: Mapped[str | None] = mapped_column(String(4))
    views: Mapped[list] = mapped_column(JSON, default=list)
    corner_unit: Mapped[bool] = mapped_column(Boolean, default=False)
    furnishing: Mapped[str | None] = mapped_column(String(30))
    price_vnd: Mapped[int | None] = mapped_column(BigInteger)
    price_includes_vat: Mapped[bool | None] = mapped_column(Boolean)
    price_includes_maintenance: Mapped[bool | None] = mapped_column(Boolean)
    price_type: Mapped[str | None] = mapped_column(String(30))
    price_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="unknown")
    source_url: Mapped[str | None] = mapped_column(String(500))

    subdivision: Mapped[Subdivision] = relationship()
    building: Mapped[Building] = relationship()


class SalesPolicy(Base):
    __tablename__ = "sales_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    subdivision_id: Mapped[int] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    policy_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    discount_percent: Mapped[float | None] = mapped_column(Float)
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(String(500))

    subdivision: Mapped[Subdivision] = relationship()


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    subdivision_id: Mapped[int | None] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    chunk_id: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("knowledge_docs.id", ondelete="CASCADE"), index=True)
    subdivision_id: Mapped[int | None] = mapped_column(ForeignKey("subdivisions.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(255))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list | None] = mapped_column(JSON)
    embedding_model: Mapped[str | None] = mapped_column(String(100))


# ── Admin ────────────────────────────────────────────────────────────────────


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="admin", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


# ── Khách hàng & cuộc gọi ────────────────────────────────────────────────────


class Customer(TimestampMixin, Base):
    """Khách để lại thông tin trong cuộc gọi. Định danh chính là số điện thoại."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    need_summary: Mapped[str | None] = mapped_column(Text)
    interested_subdivision: Mapped[str | None] = mapped_column(String(100))
    preferred_unit_type: Mapped[str | None] = mapped_column(String(20))
    budget_max_vnd: Mapped[int | None] = mapped_column(BigInteger)
    preferred_contact_time: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(30), default="voice")
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)  # new | contacted | closed

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="customer")


class Conversation(Base):
    """Một cuộc gọi voice."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), index=True)
    channel: Mapped[str] = mapped_column(String(20), default="voice")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)  # active | ended | abandoned
    data_version: Mapped[str | None] = mapped_column(String(50))
    models: Mapped[dict] = mapped_column(JSON, default=dict)
    state: Mapped[dict] = mapped_column(JSON, default=dict)  # hồ sơ khách tạm + ngữ cảnh tool gần nhất
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_sec: Mapped[float | None] = mapped_column(Float)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.id"
    )
    customer: Mapped[Customer | None] = relationship(back_populates="conversations")


class Message(Base):
    """Một lượt nói. role = customer | ai."""

    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_conversation_turn", "conversation_id", "turn_index"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"))
    turn_index: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    audio_path: Mapped[str | None] = mapped_column(String(500))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class RecordingBlob(Base):
    """Ghi âm lưu trong DB khi RECORDINGS_STORAGE=db; path trùng với messages.audio_path."""

    __tablename__ = "recording_blobs"

    path: Mapped[str] = mapped_column(String(500), primary_key=True)
    data: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
