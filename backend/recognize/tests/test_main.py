import base64
from unittest.mock import patch, MagicMock
from tests.conftest import make_request

FAKE_IMAGE_B64 = base64.b64encode(b"fake_image_bytes").decode()

MOCK_CANDIDATES = [
    {
        "name": "Black Lotus", "edition": "Alpha", "foil": False,
        "language": "EN", "collector_number": "232",
        "image_url": "https://example.com/img.jpg",
        "price_usd": 9999.99, "confidence": 0.91,
    }
]


def test_image_mode_returns_candidates():
    from main import recognize
    with patch("main.extract_text", return_value="Black Lotus\n0"), \
         patch("main.search_mtg", return_value=MOCK_CANDIDATES):
        resp, status = recognize(make_request({"image": FAKE_IMAGE_B64, "game": "mtg"}))
    assert status == 200
    body = resp.get_json()
    assert "candidates" in body
    assert len(body["candidates"]) == 1


def test_manual_search_mode_returns_candidates():
    from main import recognize
    with patch("main.search_mtg", return_value=MOCK_CANDIDATES):
        resp, status = recognize(make_request({"query": "Black Lotus", "game": "mtg"}))
    assert status == 200
    assert "candidates" in resp.get_json()


def test_missing_game_returns_400():
    from main import recognize
    resp, status = recognize(make_request({"image": FAKE_IMAGE_B64}))
    assert status == 400


def test_invalid_game_returns_400():
    from main import recognize
    resp, status = recognize(make_request({"image": FAKE_IMAGE_B64, "game": "yugioh"}))
    assert status == 400


def test_neither_image_nor_query_returns_400():
    from main import recognize
    resp, status = recognize(make_request({"game": "mtg"}))
    assert status == 400


def test_low_confidence_warning_included():
    from main import recognize
    low_conf_candidates = [{**MOCK_CANDIDATES[0], "confidence": 0.1}]
    with patch("main.extract_text", return_value="Zzzz Qqqq\n0"), \
         patch("main.search_mtg", return_value=low_conf_candidates):
        resp, status = recognize(make_request({"image": FAKE_IMAGE_B64, "game": "mtg"}))
    body = resp.get_json()
    assert body.get("low_confidence") is True


def test_ocr_failure_returns_empty_candidates_with_flag():
    from main import recognize
    with patch("main.extract_text", return_value=""), \
         patch("main.search_mtg", return_value=[]):
        resp, status = recognize(make_request({"image": FAKE_IMAGE_B64, "game": "mtg"}))
    body = resp.get_json()
    assert status == 200
    assert body["candidates"] == []
    assert body.get("ocr_failed") is True


def test_non_post_returns_405():
    from main import recognize
    resp, status = recognize(make_request({}, method="GET"))
    assert status == 405
