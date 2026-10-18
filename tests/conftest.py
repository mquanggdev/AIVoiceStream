"""Cấu hình test: DB SQLite tạm, data demo, không gọi API thật (STT/TTS/LLM giả lập)."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

_TMP = Path(tempfile.mkdtemp(prefix="voice_agent_test_"))
os.environ.update(
    {
        "APP_ENV": "test",
        "DATABASE_URL": f"sqlite:///{(_TMP / 'test.db').as_posix()}",
        "RECORDINGS_DIR": str(_TMP / "recordings"),
        "DATASET_DIR": "cleaned_data/demo_v3",
        "AUTO_IMPORT_DATASET": "true",
        "OPENROUTER_API_KEY": "",
        "LLM_API_KEY": "",
        "ADMIN_EMAIL": "admin@test.vn",
        "ADMIN_PASSWORD": "TestPassword123!",
    }
)

from fastapi.testclient import TestClient  # noqa: E402

from src.config import get_settings  # noqa: E402

get_settings.cache_clear()

from src.agent.llm import ScriptedChatModel, ScriptedStep  # noqa: E402
from src.api.voice import set_voice_deps  # noqa: E402
from src.db.session import get_session_factory  # noqa: E402
from src.main import app  # noqa: E402
from src.voice.pipeline import VoiceDeps  # noqa: E402
from src.voice.speech import CachedTTS, FakeSTT, FakeTTS  # noqa: E402


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE_AI_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="cần RUN_LIVE_AI_TESTS=1 và OPENROUTER_API_KEY")
    for item in items:
        if "live_ai" in item.keywords:
            item.add_marker(skip)


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_TMP, ignore_errors=True)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db(client):
    with get_session_factory()() as session:
        yield session


class FakeVoice:
    """Bộ STT/TTS/LLM giả lập; test đặt kịch bản trước mỗi lượt."""

    def __init__(self):
        self.stt = FakeSTT()
        self.tts_inner = FakeTTS()
        self.steps: list[ScriptedStep] = []
        self.models: list[ScriptedChatModel] = []

    def script(self, *steps: ScriptedStep) -> None:
        self.steps = list(steps)

    def model_factory(self):
        model = ScriptedChatModel(self.steps)
        self.steps = []
        self.models.append(model)
        return model


@pytest.fixture
def fake_voice(client):
    fake = FakeVoice()
    set_voice_deps(
        VoiceDeps(
            stt=fake.stt,
            tts=CachedTTS(fake.tts_inner, cache_dir=_TMP / "tts_cache"),
            model_factory=fake.model_factory,
            session_factory=get_session_factory(),
        )
    )
    yield fake
    set_voice_deps(None)


@pytest.fixture
def admin_headers(client):
    response = client.post("/api/v1/auth/login", json={"email": "admin@test.vn", "password": "TestPassword123!"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
