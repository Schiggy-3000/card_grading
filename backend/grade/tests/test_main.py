import base64
from unittest.mock import patch
from tests.conftest import make_request

FAKE_B64 = base64.b64encode(b"fake").decode()
MOCK_SCORES = {"centering": 8.5, "corners": 7.0, "edges": 9.0, "surface": 7.5}
MOCK_REASONING = {
    "centering": "Good centering.",
    "corners": "Minor corner wear.",
    "edges": "Clean edges.",
    "surface": "Light scratching.",
}
MOCK_SIDE = {"subgrades": MOCK_SCORES, "reasoning": MOCK_REASONING, "bbox_image": ""}


def test_grade_returns_full_result():
    from main import grade
    with patch("main.analyze_with_reasoning", return_value=(MOCK_SIDE, MOCK_SIDE)):
        resp, status = grade(make_request({
            "front": FAKE_B64, "back": FAKE_B64, "standard": "psa"
        }))
    assert status == 200
    body = resp.get_json()
    assert "front" in body
    assert "back" in body
    assert "overall" in body["front"]
    assert "subgrades" in body["front"]
    assert "reasoning" in body["front"]
    assert "bbox_image" in body["front"]
    assert body["standard"] == "psa"


def test_missing_front_returns_400():
    from main import grade
    resp, status = grade(make_request({"back": FAKE_B64, "standard": "psa"}))
    assert status == 400


def test_missing_back_returns_400():
    from main import grade
    resp, status = grade(make_request({"front": FAKE_B64, "standard": "psa"}))
    assert status == 400


def test_invalid_standard_returns_400():
    from main import grade
    resp, status = grade(make_request({"front": FAKE_B64, "back": FAKE_B64, "standard": "xxx"}))
    assert status == 400


def test_all_four_standards_accepted():
    from main import grade
    for std in ("psa", "bgs", "cgc", "tag"):
        with patch("main.analyze_with_reasoning", return_value=(MOCK_SIDE, MOCK_SIDE)):
            resp, status = grade(make_request({"front": FAKE_B64, "back": FAKE_B64, "standard": std}))
        assert status == 200, f"Standard {std} returned {status}"


def test_non_post_returns_405():
    from main import grade
    resp, status = grade(make_request({}, method="GET"))
    assert status == 405
