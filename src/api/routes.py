"""Router tổng cho /api/v1."""

from fastapi import APIRouter

from src.api.admin import router as admin_router
from src.api.auth import router as auth_router
from src.api.voice import router as voice_router
from src.config import get_settings

router = APIRouter()
router.include_router(auth_router)
router.include_router(voice_router)
router.include_router(admin_router)


@router.get("/status")
async def api_status() -> dict:
    settings = get_settings()
    return {
        "status": "ready",
        "agent": f"{settings.app_name} v{settings.app_version}",
        "ai_configured": settings.ai_configured,
        "models": {"stt": settings.stt_model, "llm": settings.llm_model, "tts": settings.tts_model},
    }
