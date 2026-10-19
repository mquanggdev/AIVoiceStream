import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.routes import router
from src.config import get_settings
from src.dataset.importer import embed_missing_chunks, ensure_dataset
from src.db.seed_admin import seed_admin
from src.db.session import get_engine, get_session_factory, init_database
from src.retrieval.knowledge import reset_index
from src.voice.pipeline import sweep_stale_calls

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("[START] %s in %s mode", settings.app_name, settings.app_env)
    if settings.auto_create_tables:
        init_database()
    with get_session_factory()() as session:
        seed_admin(session, settings)
        if settings.auto_import_dataset:
            version = ensure_dataset(session)
            if version is not None:
                logger.info("Dataset: %s (demo=%s)", version.version, version.is_demo)
    if not settings.ai_configured:
        logger.warning("OPENROUTER_API_KEY chưa được cấu hình: cuộc gọi voice sẽ không trả lời được")
    sweeper = asyncio.create_task(_sweep_calls_forever(settings.call_inactivity_timeout_sec, settings.call_sweep_interval_sec))
    embedder = asyncio.create_task(_embed_knowledge()) if settings.auto_embed_knowledge and settings.ai_configured else None
    yield
    if embedder is not None:
        embedder.cancel()
    sweeper.cancel()
    with suppress(asyncio.CancelledError):
        await sweeper


async def _embed_knowledge() -> None:
    """Embed chunk còn thiếu (lần deploy đầu); trong lúc chờ, tìm tài liệu dùng BM25."""
    try:
        with get_session_factory()() as session:
            count = await embed_missing_chunks(session)
        if count:
            reset_index()
            logger.info("Đã embed %d knowledge chunk", count)
    except Exception:  # noqa: BLE001 - lỗi embed không được làm sập server
        logger.exception("embed_missing_chunks failed")


async def _sweep_calls_forever(timeout_sec: int, interval_sec: int) -> None:
    """Đóng cuộc gọi treo (mất kết nối, beacon không tới) — chạy cả lúc khởi động để dọn cuộc treo từ trước."""
    while True:
        try:
            with get_session_factory()() as session:
                closed = sweep_stale_calls(session, timeout_sec)
            if closed:
                logger.info("Đã đóng %d cuộc gọi mất kết nối", closed)
        except Exception:  # noqa: BLE001 - tác vụ nền không được chết
            logger.exception("sweep_stale_calls failed")
        await asyncio.sleep(interval_sec)


settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Ocean Park Voice Agent API",
    description="Trợ lý tư vấn căn hộ Vinhomes Ocean Park bằng giọng nói",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Dev: chấp nhận mọi cổng localhost (FE có thể tự nhảy cổng khi 3000/3001 bận)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+" if settings.app_env == "development" else (settings.cors_origin_regex or None),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env, "app": settings.app_name}


@app.get("/ready")
async def ready():
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
