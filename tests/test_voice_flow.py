"""Luồng cuộc gọi đầu-cuối với STT/TTS/LLM giả lập."""

import json

from src.agent.fact_check import SAFE_SENTENCE
from src.agent.llm import ScriptedStep


def _events(response) -> list[dict]:
    assert response.status_code == 200, response.text
    return [json.loads(line) for line in response.text.splitlines() if line.strip()]


def _start_call(client) -> str:
    events = _events(client.post("/api/v1/voice/calls"))
    assert events[0]["type"] == "call"
    assert any(e["type"] == "audio" for e in events)
    return events[0]["session_id"]


def _say(client, session_id: str, audio: bytes = b"RIFF....WAVEfake") -> list[dict]:
    return _events(
        client.post(
            "/api/v1/voice/turn",
            data={"session_id": session_id},
            files={"audio": ("turn.wav", audio, "audio/wav")},
        )
    )


def test_full_call_with_unit_lookup_and_lead_capture(client, fake_voice, admin_headers):
    session_id = _start_call(client)

    # Lượt 1: khách hỏi căn theo mã → agent gọi get_unit rồi trả lời bằng số liệu thật
    fake_voice.stt.transcripts = ["cho chị hỏi căn R1.03-1612 giá bao nhiêu"]
    from src.db.session import get_session_factory
    from src.retrieval.catalog import get_unit

    with get_session_factory()() as s:
        unit = get_unit(s, "R1.03-1612")
        price_text = f"{unit.price_vnd / 1e9:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " tỷ"
    fake_voice.script(
        ScriptedStep(tool_calls=[("get_unit", {"unit_code": "R1.03-1612"})]),
        ScriptedStep(text=f"Dạ căn R1.03-1612 có giá chủ nhà rao bán tham khảo là {price_text} ạ. Chị muốn xem thêm căn khác không ạ?"),
    )
    events = _say(client, session_id)
    types = [e["type"] for e in events]
    assert types[0] == "transcript" and events[0]["text"].startswith("cho chị hỏi")
    assert "tool" in types
    audio_events = [e for e in events if e["type"] == "audio"]
    assert audio_events[0]["filler"] is True  # câu lót phát trước khi tra dữ liệu
    assert len([e for e in audio_events if not e["filler"]]) == 2  # 2 câu trả lời, mỗi câu một audio
    assert types[-1] == "done"
    spoken_texts = fake_voice.tts_inner.texts
    assert any("tòa rờ một chấm không ba, tầng mười sáu, căn số một hai" in t for t in spoken_texts)

    # Lượt 2: khách đọc SĐT → agent đọc lại xác nhận (chưa lưu)
    fake_voice.stt.transcripts = ["chị tên Lan, số không chín một hai ba bốn năm sáu bảy tám"]
    fake_voice.script(ScriptedStep(text="Dạ em xin xác nhận chị Lan, số điện thoại 0912345678, đúng không ạ?"))
    _say(client, session_id)

    # Lượt 3: khách xác nhận → agent gọi save_customer_info
    fake_voice.stt.transcripts = ["đúng rồi em"]
    fake_voice.script(
        ScriptedStep(
            tool_calls=[
                (
                    "save_customer_info",
                    {"full_name": "Lan", "phone": "không chín một hai ba bốn năm sáu bảy tám",
                     "need_summary": "Quan tâm căn 2PN The Zenpark", "interested_subdivision": "zen park"},
                )
            ]
        ),
        ScriptedStep(text="Dạ em đã ghi nhận, chuyên viên sẽ liên hệ chị sớm ạ."),
    )
    _say(client, session_id)

    end_events = _events(client.post(f"/api/v1/voice/calls/{session_id}/end"))
    assert end_events[-1] == {"type": "done", "ended": True}

    # Admin thấy khách + cuộc gọi đầy đủ, phân biệt KHÁCH / AI, có ghi âm cả hai phía
    customers = client.get("/api/v1/admin/customers", headers=admin_headers).json()
    lan = next(c for c in customers if c["phone"] == "0912345678")
    assert lan["full_name"] == "Lan" and lan["interested_subdivision"] == "The Zenpark"

    calls = client.get("/api/v1/admin/conversations", headers=admin_headers).json()
    call = next(c for c in calls if c["session_id"] == session_id)
    assert call["status"] == "ended" and call["customer_phone"] == "0912345678"

    detail = client.get(f"/api/v1/admin/conversations/{call['id']}", headers=admin_headers).json()
    roles = [m["role"] for m in detail["messages"]]
    assert roles[0] == "ai" and "customer" in roles
    customer_msgs = [m for m in detail["messages"] if m["role"] == "customer"]
    assert all(m["has_audio"] for m in customer_msgs)
    ai_answer = next(m for m in detail["messages"] if m["role"] == "ai" and m["turn_index"] == 1 and not m["meta"].get("is_filler"))
    assert ai_answer["has_audio"] and ai_answer["meta"]["fact_check"] == "ok"
    assert ai_answer["meta"]["tool_calls"][0]["name"] == "get_unit"

    audio = client.get(f"/api/v1/admin/messages/{customer_msgs[0]['id']}/audio", headers=admin_headers)
    assert audio.status_code == 200 and audio.content.startswith(b"RIFF")

    export = client.get(f"/api/v1/admin/conversations/{call['id']}/export", headers=admin_headers).json()
    assert {t["speaker"] for t in export["turns"]} == {"KHÁCH", "AI"}


def test_invented_unit_code_is_blocked(client, fake_voice):
    session_id = _start_call(client)
    fake_voice.script(ScriptedStep(text="Dạ căn ZZ9-9999 đang mở bán với giá 2 tỷ ạ."))
    events = _events(client.post("/api/v1/voice/text-turn", json={"session_id": session_id, "text": "có căn nào rẻ không"}))
    assert events[-1]["type"] == "done"
    speak = [e["text"] for e in events if e["type"] == "speak_text"]
    assert speak == [SAFE_SENTENCE]  # câu chứa mã căn bịa bị thay, không đọc cho khách


def test_invalid_phone_is_not_saved(client, fake_voice, admin_headers):
    session_id = _start_call(client)
    fake_voice.script(
        ScriptedStep(tool_calls=[("save_customer_info", {"full_name": "Nam", "phone": "09123"})]),
        ScriptedStep(text="Dạ số điện thoại hình như còn thiếu, anh đọc lại giúp em ạ."),
    )
    _events(client.post("/api/v1/voice/text-turn", json={"session_id": session_id, "text": "anh Nam 09123"}))
    model = fake_voice.models[-1]
    tool_message = next(m for m in model.calls[1] if m["role"] == "tool")
    assert '"saved": false' in tool_message["content"]
    customers = client.get("/api/v1/admin/customers", params={"search": "Nam"}, headers=admin_headers).json()
    assert customers == []


def test_empty_transcript_asks_to_repeat(client, fake_voice):
    session_id = _start_call(client)
    fake_voice.stt.transcripts = [""]
    events = _say(client, session_id)
    assert events[0] == {"type": "transcript", "turn_index": 1, "text": ""}
    assert any(e["type"] == "audio" for e in events)
    assert fake_voice.models == []  # không gọi LLM khi không nghe được gì


def test_admin_requires_auth(client):
    assert client.get("/api/v1/admin/stats").status_code == 401


def test_admin_stats(client, admin_headers):
    stats = client.get("/api/v1/admin/stats", headers=admin_headers).json()
    assert stats["dataset"]["is_demo"] is True
    assert stats["ai_configured"] is False


def test_hangup_beacon_closes_call_without_goodbye(client, fake_voice, admin_headers):
    session_id = _start_call(client)
    assert client.post(f"/api/v1/voice/calls/{session_id}/ping").json() == {"active": True}
    # sendBeacon gửi POST text/plain, không cần body
    response = client.post(f"/api/v1/voice/calls/{session_id}/hangup", content=b"", headers={"Content-Type": "text/plain"})
    assert response.status_code == 200
    assert client.post(f"/api/v1/voice/calls/{session_id}/ping").json() == {"active": False}
    calls = client.get("/api/v1/admin/conversations", headers=admin_headers).json()
    call = next(c for c in calls if c["session_id"] == session_id)
    assert call["status"] == "closed" and call["ended_at"]
    detail = client.get(f"/api/v1/admin/conversations/{call['id']}", headers=admin_headers).json()
    assert [m["meta"].get("kind") for m in detail["messages"]] == ["greeting"]  # không có câu tạm biệt


def test_sweeper_abandons_silent_calls(client, fake_voice, db):
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from src.models.entities import Conversation
    from src.voice.pipeline import sweep_stale_calls

    stale_id = _start_call(client)
    fresh_id = _start_call(client)
    stale = db.scalar(select(Conversation).where(Conversation.session_id == stale_id))
    stale.last_activity_at = datetime.now(UTC) - timedelta(minutes=5)
    db.commit()

    assert sweep_stale_calls(db, timeout_seconds=90) >= 1
    db.expire_all()
    stale = db.scalar(select(Conversation).where(Conversation.session_id == stale_id))
    fresh = db.scalar(select(Conversation).where(Conversation.session_id == fresh_id))
    assert stale.status == "abandoned" and stale.duration_sec is not None
    assert fresh.status == "active"
