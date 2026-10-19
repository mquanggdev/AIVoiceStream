from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Ocean Park Voice Agent"
    app_version: str = "3.0.0"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_host: str = "0.0.0.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    cors_origins: str = "http://localhost:3000"
    # Regex cho domain động (vd. preview Vercel: https://aivoicestream-.*\.vercel\.app)
    cors_origin_regex: str | None = None
    sqlalchemy_echo: bool = False

    # OpenRouter (một key cho LLM, STT, TTS, embedding)
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "https://ocean-park-voice.local"
    openrouter_app_name: str = "Ocean Park Voice Agent"
    # Ghi đè cho gateway OpenAI-compatible khác (tùy chọn)
    llm_api_key: str = ""
    llm_base_url: str = ""

    llm_model: str = "openai/gpt-4.1-mini"
    llm_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    llm_timeout_seconds: float = Field(default=30.0, ge=1.0)
    stt_model: str = "openai/whisper-large-v3-turbo"
    stt_language: str = "vi"
    tts_model: str = "elevenlabs/eleven-flash-v2.5"
    tts_voice: str = "sarah"
    tts_format: Literal["auto", "mp3", "pcm"] = "auto"  # auto: Gemini TTS → pcm (bọc WAV), còn lại → mp3
    embedding_model: str = "openai/text-embedding-3-small"

    # Cuộc gọi: trình duyệt ping mỗi ~20s; quá thời gian này không ping/không nói → đóng "abandoned"
    call_inactivity_timeout_sec: int = Field(default=90, ge=30, le=3600)
    call_sweep_interval_sec: int = Field(default=30, ge=5, le=600)

    # Agent
    agent_history_turns: int = Field(default=12, ge=2, le=40)
    agent_max_tool_rounds: int = Field(default=4, ge=1, le=8)

    # Database
    database_url: str = "sqlite:///./app.db"
    auto_create_tables: bool = True

    # Dữ liệu: bộ data được import khi khởi động nếu DB chưa có hoặc khác phiên bản
    dataset_dir: str = "cleaned_data/demo_v3"
    auto_import_dataset: bool = True
    recordings_dir: str = "data/recordings"
    # file: ghi ra recordings_dir; db: lưu trong bảng recording_blobs (host không có ổ đĩa bền, vd. Render free)
    recordings_storage: Literal["file", "db"] = "file"
    # Tự embed knowledge chunk còn thiếu khi khởi động (chạy nền, cần API key)
    auto_embed_knowledge: bool = False

    # Dashboard authentication
    jwt_secret_key: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    admin_email: str = "admin@oceanpark.vn"
    admin_password: str = "ChangeMe123!"
    admin_full_name: str = "Quản trị Ocean Park"

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Render/Heroku cấp postgres:// hoặc postgresql:// — chuyển sang driver psycopg 3 đã cài."""
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix):]
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """Return normalized origins for Starlette's CORS middleware."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def effective_api_key(self) -> str:
        return (self.llm_api_key or self.openrouter_api_key).strip()

    @property
    def effective_base_url(self) -> str:
        return (self.llm_base_url or self.openrouter_base_url).strip()

    @property
    def ai_configured(self) -> bool:
        return bool(self.effective_api_key)

    @model_validator(mode="after")
    def validate_deployment_security(self) -> "Settings":
        """Fail fast when staging/production is started with unsafe defaults."""
        if self.app_env not in {"staging", "production"}:
            return self

        errors: list[str] = []
        weak_jwt_secrets = {
            "development-only-change-me",
            "local-docker-secret-change-before-deploy",
            "replace-with-a-long-random-secret",
        }
        jwt_secret_lower = self.jwt_secret_key.lower()
        if (
            len(self.jwt_secret_key) < 32
            or self.jwt_secret_key in weak_jwt_secrets
            or "replace" in jwt_secret_lower
            or "change-me" in jwt_secret_lower
        ):
            errors.append("JWT_SECRET_KEY must be a unique secret of at least 32 characters")

        admin_password_lower = self.admin_password.lower()
        if self.admin_password in {"ChangeMe123!", "change-me", "password"} or any(
            marker in admin_password_lower for marker in ("replace", "change-me")
        ):
            errors.append("ADMIN_PASSWORD must not use a documented default")
        if self.admin_password and len(self.admin_password) < 12:
            errors.append("ADMIN_PASSWORD must contain at least 12 characters")

        if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            errors.append("DATABASE_URL must use PostgreSQL")
        if self.auto_create_tables:
            errors.append("AUTO_CREATE_TABLES must be false; use Alembic migrations")
        if self.app_env == "production" and any(
            origin == "*" or "localhost" in origin or "127.0.0.1" in origin
            for origin in self.cors_origin_list
        ):
            errors.append("CORS_ORIGINS must contain only production HTTPS domains")

        if errors:
            raise ValueError("Unsafe deployment configuration: " + "; ".join(errors))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
