"""Pydantic schemas cho API v3."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ── Auth ─────────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Voice ────────────────────────────────────────────────────────────────────


class TextTurnRequest(BaseModel):
    session_id: str
    text: str = Field(min_length=1, max_length=2000)
    with_audio: bool = False


class InterruptRequest(BaseModel):
    session_id: str
    turn_index: int = Field(ge=0)
    played_segments: int = Field(default=0, ge=0)


# ── Admin ────────────────────────────────────────────────────────────────────


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str | None
    phone: str
    need_summary: str | None
    interested_subdivision: str | None
    preferred_unit_type: str | None
    budget_max_vnd: int | None
    preferred_contact_time: str | None
    source: str
    status: str
    created_at: datetime
    updated_at: datetime


class CustomerUpdateRequest(BaseModel):
    status: str | None = Field(default=None, pattern="^(new|contacted|closed)$")
    need_summary: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    turn_index: int
    role: str
    content: str
    has_audio: bool
    meta: dict
    created_at: datetime


class ConversationSummary(BaseModel):
    id: int
    session_id: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_sec: float | None
    turn_count: int
    customer_id: int | None
    customer_name: str | None
    customer_phone: str | None
    data_version: str | None
    avg_first_audio_ms: int | None
    fact_check_mismatch: bool
    interrupted_turns: int
    cost_usd: float


class ConversationDetail(ConversationSummary):
    models: dict
    state: dict
    messages: list[MessageResponse]


class DatasetInfo(BaseModel):
    version: str
    is_demo: bool
    dataset_dir: str
    counts: dict
    notes: str | None
    embedding_model: str | None
    imported_at: datetime


class DashboardStats(BaseModel):
    total_calls: int
    active_calls: int
    total_customers: int
    calls_with_lead: int
    avg_turns: float
    avg_first_audio_ms: int | None
    fact_check_mismatch_turns: int
    total_cost_usd: float
    dataset: DatasetInfo | None
    ai_configured: bool
