import pytest

from src.core.phone import normalize_phone
from src.core.spoken import money_to_words, read_int, to_spoken, unit_code_spoken


@pytest.mark.parametrize(
    ("number", "words"),
    [
        (15, "mười lăm"),
        (21, "hai mươi mốt"),
        (24, "hai mươi tư"),
        (105, "một trăm lẻ năm"),
        (1050, "một nghìn không trăm năm mươi"),
        (2026, "hai nghìn không trăm hai mươi sáu"),
        (10_260_000_000, "mười tỷ hai trăm sáu mươi triệu"),
    ],
)
def test_read_int(number, words):
    assert read_int(number) == words


def test_money_and_unit_code_spoken():
    assert money_to_words(3_350_000_000) == "ba tỷ ba trăm năm mươi triệu"
    assert money_to_words(980_000_000) == "chín trăm tám mươi triệu"
    assert unit_code_spoken("R1.01-1205") == "tòa rờ một chấm không một, tầng mười hai, căn số không năm"


def test_to_spoken_full_sentence():
    spoken = to_spoken("Căn R1.01-1205 rộng 64,2 m², giá 3,35 tỷ, chiết khấu 9%. Căn 2PN+1. Số 0912345678.")
    assert "R1" not in spoken and "tỷ" in spoken
    assert "ba tỷ ba trăm năm mươi triệu" in spoken
    assert "sáu mươi tư phẩy hai mét vuông" in spoken
    assert "chín phần trăm" in spoken
    assert "hai phòng ngủ cộng một" in spoken
    assert "không chín một hai, ba bốn năm, sáu bảy tám" in spoken
    assert not any(ch.isdigit() for ch in spoken)


def test_to_spoken_strips_markdown():
    assert to_spoken("**Dạ** căn [C1] [link](/x) ạ\n- tiện ích") == "Dạ căn link ạ tiện ích"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("không chín một hai ba bốn năm sáu bảy tám", "0912345678"),
        ("0912 345 678", "0912345678"),
        ("+84 912 345 678", "0912345678"),
        ("09 88 77 66 55", "0988776655"),
    ],
)
def test_normalize_phone_ok(raw, expected):
    assert normalize_phone(raw) == (expected, None)


@pytest.mark.parametrize("raw", ["09123", "0123456789", "091234567890"])
def test_normalize_phone_invalid(raw):
    phone, error = normalize_phone(raw)
    assert phone is None and error
