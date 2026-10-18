"""API trang admin: thống kê, danh sách cuộc gọi (kèm ghi âm), khách để lại thông tin, xuất JSON đánh giá."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from src.api.dependencies import get_current_user
from src.config import get_settings
from src.dataset.importer import current_dataset
from src.db.session import get_db
from src.models.entities import Conversation, Customer, DatasetVersion, Message, User
from src.models.schemas import (
    ConversationDetail,
    ConversationSummary,
    CustomerResponse,
    CustomerUpdateRequest,
    DashboardStats,
    DatasetInfo,
    MessageResponse,
)
from src.voice.pipeline import sweep_stale_calls
from src.voice.recordings import resolve_recording

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_user)])

def _close_stale_calls(db: Session) -> None:
    sweep_stale_calls(db, get_settings().call_inactivity_timeout_sec)


def _dataset_info(version: DatasetVersion | None) -> DatasetInfo | None:
    if version is None:
        return None
    return DatasetInfo(
        version=version.version,
        is_demo=version.is_demo,
        dataset_dir=version.dataset_dir,
        counts=version.counts or {},
        notes=version.notes,
        embedding_model=version.embedding_model,
        imported_at=version.imported_at,
    )


def _ai_messages(conversation: Conversation) -> list[Message]:
    return [m for m in conversation.messages if m.role == "ai" and not (m.meta or {}).get("is_filler")]


COST_KEYS = ("llm_cost_usd", "stt_cost_usd", "tts_cost_usd_est")


def _call_cost(conversation: Conversation) -> float:
    """Tổng chi phí AI của cuộc gọi (LLM + STT chính xác, TTS ước tính)."""
    return round(
        sum(float((m.meta or {}).get(key) or 0) for m in conversation.messages for key in COST_KEYS), 6
    )


def _summary(conversation: Conversation) -> dict:
    ai_messages = _ai_messages(conversation)
    first_audio = [m.meta.get("first_audio_ms") for m in ai_messages if (m.meta or {}).get("first_audio_ms")]
    return {
        "id": conversation.id,
        "session_id": conversation.session_id,
        "status": conversation.status,
        "started_at": conversation.started_at,
        "ended_at": conversation.ended_at,
        "duration_sec": conversation.duration_sec,
        "turn_count": conversation.turn_count,
        "customer_id": conversation.customer_id,
        "customer_name": conversation.customer.full_name if conversation.customer else None,
        "customer_phone": conversation.customer.phone if conversation.customer else None,
        "data_version": conversation.data_version,
        "avg_first_audio_ms": round(sum(first_audio) / len(first_audio)) if first_audio else None,
        "fact_check_mismatch": any((m.meta or {}).get("fact_check") == "mismatch" for m in ai_messages),
        "interrupted_turns": sum(1 for m in ai_messages if (m.meta or {}).get("interrupted")),
        "cost_usd": _call_cost(conversation),
    }


def _message(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        turn_index=message.turn_index,
        role=message.role,
        content=message.content,
        has_audio=bool(message.audio_path),
        meta=message.meta or {},
        created_at=message.created_at,
    )


def _conversation_query():
    return select(Conversation).options(selectinload(Conversation.messages), selectinload(Conversation.customer))


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)) -> DashboardStats:
    _close_stale_calls(db)
    conversations = list(db.scalars(_conversation_query()).all())
    summaries = [_summary(c) for c in conversations]
    first_audio = [s["avg_first_audio_ms"] for s in summaries if s["avg_first_audio_ms"]]
    mismatch_turns = sum(
        1 for c in conversations for m in _ai_messages(c) if (m.meta or {}).get("fact_check") == "mismatch"
    )
    return DashboardStats(
        total_calls=len(conversations),
        active_calls=sum(1 for c in conversations if c.status == "active"),
        total_customers=db.scalar(select(func.count(Customer.id))) or 0,
        calls_with_lead=sum(1 for c in conversations if c.customer_id),
        avg_turns=round(sum(c.turn_count for c in conversations) / len(conversations), 1) if conversations else 0,
        avg_first_audio_ms=round(sum(first_audio) / len(first_audio)) if first_audio else None,
        fact_check_mismatch_turns=mismatch_turns,
        total_cost_usd=round(sum(_call_cost(c) for c in conversations), 4),
        dataset=_dataset_info(current_dataset(db)),
        ai_configured=get_settings().ai_configured,
    )


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    status: str | None = None,
    has_customer: bool | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    _close_stale_calls(db)
    query = _conversation_query().order_by(Conversation.id.desc())
    if status:
        query = query.where(Conversation.status == status)
    if has_customer is True:
        query = query.where(Conversation.customer_id.is_not(None))
    elif has_customer is False:
        query = query.where(Conversation.customer_id.is_(None))
    return [_summary(c) for c in db.scalars(query.offset(offset).limit(limit)).all()]


def _get_conversation(db: Session, conversation_id: int) -> Conversation:
    conversation = db.scalar(_conversation_query().where(Conversation.id == conversation_id))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc gọi")
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> dict:
    conversation = _get_conversation(db, conversation_id)
    return {
        **_summary(conversation),
        "models": conversation.models or {},
        "state": conversation.state or {},
        "messages": [_message(m) for m in conversation.messages],
    }


@router.get("/conversations/{conversation_id}/export", summary="Xuất JSON một cuộc gọi để đánh giá offline")
def export_conversation(conversation_id: int, db: Session = Depends(get_db)) -> dict:
    conversation = _get_conversation(db, conversation_id)
    return {
        "conversation": {
            **_summary(conversation),
            "models": conversation.models,
            "final_state": conversation.state,
        },
        "turns": [
            {
                "turn_index": m.turn_index,
                "speaker": "KHÁCH" if m.role == "customer" else "AI",
                "text": m.content,
                "audio_file": m.audio_path,
                "is_filler": bool((m.meta or {}).get("is_filler")),
                "meta": m.meta,
                "created_at": m.created_at.isoformat(),
            }
            for m in conversation.messages
        ],
    }


@router.get("/messages/{message_id}/audio", summary="Tải file ghi âm của một lượt")
def message_audio(message_id: int, db: Session = Depends(get_db)) -> FileResponse:
    message = db.get(Message, message_id)
    if message is None or not message.audio_path:
        raise HTTPException(status_code=404, detail="Lượt này không có ghi âm")
    path = resolve_recording(message.audio_path)
    if path is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy file ghi âm")
    media_type = {"wav": "audio/wav", "mp3": "audio/mpeg", "webm": "audio/webm", "ogg": "audio/ogg"}.get(
        path.suffix.lstrip("."), "application/octet-stream"
    )
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.get("/customers", response_model=list[CustomerResponse])
def list_customers(
    search: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Customer]:
    query = select(Customer).order_by(Customer.updated_at.desc(), Customer.id.desc())
    if status:
        query = query.where(Customer.status == status)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Customer.full_name.ilike(pattern), Customer.phone.ilike(pattern)))
    return list(db.scalars(query.limit(limit)).all())


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> dict:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    conversations = db.scalars(
        _conversation_query().where(Conversation.customer_id == customer.id).order_by(Conversation.id.desc())
    ).all()
    return {
        "customer": CustomerResponse.model_validate(customer).model_dump(),
        "conversations": [_summary(c) for c in conversations],
    }


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer
