"""Verify that the API modules send the correct JSON request shape to the GCF endpoints."""
import json
import tempfile
import pytest
from playwright.sync_api import Page
from conftest import BASE_URL, RECOGNIZE_API_URL, GRADE_API_URL, MOCK_CANDIDATES, MOCK_GRADE_RESULT, small_jpeg_bytes, _fulfill_json


def _upload(page: Page, testid: str):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator(f"[data-testid='upload-input-{testid}']").set_input_files(tmp)


def test_recognize_image_sends_image_and_game_fields(page: Page):
    captured = {}
    def handle_recognize(route):
        if route.request.method == "OPTIONS":
            _fulfill_json(route, 200, "")
            return
        captured.update(json.loads(route.request.post_data))
        _fulfill_json(route, 200, json.dumps({"candidates": MOCK_CANDIDATES, "low_confidence": False}))
    page.route(RECOGNIZE_API_URL, handle_recognize)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-list']")
    assert "image" in captured
    assert captured["game"] == "mtg"


def test_recognize_query_sends_query_and_game_fields(page: Page):
    """Uses the manual search path after OCR failure to trigger recognizeQuery."""
    captured = {}
    post_count = [0]
    def handle(route):
        if route.request.method == "OPTIONS":
            _fulfill_json(route, 200, "")
            return
        body = json.loads(route.request.post_data)
        post_count[0] += 1
        if post_count[0] == 1:
            # first POST: OCR image — return ocr_failed
            _fulfill_json(route, 200, json.dumps({"candidates": [], "ocr_failed": True, "low_confidence": False}))
        else:
            # second POST: manual search query
            captured.update(body)
            _fulfill_json(route, 200, json.dumps({"candidates": MOCK_CANDIDATES, "low_confidence": False}))
    page.route(RECOGNIZE_API_URL, handle)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='manual-search']")
    page.locator("[data-testid='manual-search-input']").fill("Black Lotus")
    page.locator("[data-testid='manual-search-submit']").click()
    page.wait_for_selector("[data-testid='candidate-list']")
    assert "query" in captured
    assert captured["game"] == "mtg"


def test_grade_sends_front_back_and_standard_fields(page: Page):
    captured = {}
    def handle_grade(route):
        if route.request.method == "OPTIONS":
            _fulfill_json(route, 200, "")
            return
        captured.update(json.loads(route.request.post_data))
        _fulfill_json(route, 200, json.dumps(MOCK_GRADE_RESULT))
    page.route(GRADE_API_URL, handle_grade)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    assert "front" in captured
    assert "back" in captured
    assert captured["standard"] == "psa"
