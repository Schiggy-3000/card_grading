import json
import tempfile
import pytest
from playwright.sync_api import Page
from conftest import (
    BASE_URL, RECOGNIZE_API_URL, MOCK_CANDIDATES, mock_recognize_success,
    mock_recognize_ocr_failed, mock_network_error, small_jpeg_bytes, _fulfill_json,
)


def _upload_image(page: Page, testid: str):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator(f"[data-testid='upload-input-{testid}']").set_input_files(tmp)


def test_identify_page_has_game_selector(page: Page):
    page.goto(BASE_URL + "/#/identify")
    assert page.locator("[data-testid='game-mtg']").is_visible()
    assert page.locator("[data-testid='game-fab']").is_visible()


def test_submit_disabled_until_image_and_game_selected(page: Page):
    page.goto(BASE_URL + "/#/identify")
    btn = page.locator("[data-testid='identify-submit']")
    assert not btn.is_enabled()
    page.locator("[data-testid='game-mtg']").click()
    assert not btn.is_enabled()
    _upload_image(page, "front")
    assert btn.is_enabled()


def test_image_submit_shows_candidate_list(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-list']")
    assert page.locator("[data-testid='candidate-item']").count() >= 1


def test_candidate_shows_name_and_confidence(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-item']")
    first = page.locator("[data-testid='candidate-item']").first
    assert "Black Lotus" in first.inner_text()
    assert "%" in first.inner_text()  # confidence shown as percentage


def test_ocr_failed_shows_message_and_manual_search(page: Page):
    mock_recognize_ocr_failed(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='ocr-failed-msg']")
    assert page.locator("[data-testid='manual-search']").is_visible()


def test_low_confidence_shows_warning(page: Page):
    low_conf_candidates = [{**MOCK_CANDIDATES[0], "confidence": 0.1}]
    mock_recognize_success(page, candidates=low_conf_candidates, low_confidence=True)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='low-confidence-warning']")


def test_selecting_candidate_shows_card_detail(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-item']")
    page.locator("[data-testid='candidate-item']").first.click()
    page.wait_for_selector("[data-testid='card-detail']")
    detail = page.locator("[data-testid='card-detail']")
    assert "Black Lotus" in detail.inner_text()
    assert "9,999" in detail.inner_text()  # price shown


def test_fab_candidate_shows_price_not_available(page: Page):
    fab_candidates = [{**MOCK_CANDIDATES[0], "price_usd": None, "name": "Command and Conquer"}]
    mock_recognize_success(page, candidates=fab_candidates)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-fab']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-item']")
    page.locator("[data-testid='candidate-item']").first.click()
    detail = page.locator("[data-testid='card-detail']")
    assert "price not available" in detail.inner_text().lower()


def test_not_right_card_link_shows_manual_search(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-item']")
    page.locator("[data-testid='candidate-item']").first.click()
    page.locator("[data-testid='not-right-card']").click()
    assert page.locator("[data-testid='manual-search']").is_visible()


def test_manual_search_shows_results(page: Page):
    """Use a single page.route handler with a call counter to serve ocr_failed on the
    first POST (image submit) and candidates on the second POST (manual search submit).
    OPTIONS preflight requests are handled separately for CORS and don't increment the counter."""
    post_count = [0]
    def handle(route):
        if route.request.method == "OPTIONS":
            _fulfill_json(route, 200, "")
            return
        post_count[0] += 1
        if post_count[0] == 1:
            _fulfill_json(route, 200, json.dumps({"candidates": [], "ocr_failed": True, "low_confidence": False}))
        else:
            _fulfill_json(route, 200, json.dumps({"candidates": MOCK_CANDIDATES, "low_confidence": False}))
    page.route(RECOGNIZE_API_URL, handle)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='manual-search']")
    page.locator("[data-testid='manual-search-input']").fill("Black Lotus")
    page.locator("[data-testid='manual-search-submit']").click()
    page.wait_for_selector("[data-testid='candidate-list']")


def test_manual_search_zero_results_shows_message(page: Page):
    """Single route handler: first POST (image) → ocr_failed; second POST (manual search) → empty candidates."""
    post_count = [0]
    def handle(route):
        if route.request.method == "OPTIONS":
            _fulfill_json(route, 200, "")
            return
        post_count[0] += 1
        if post_count[0] == 1:
            _fulfill_json(route, 200, json.dumps({"candidates": [], "ocr_failed": True, "low_confidence": False}))
        else:
            _fulfill_json(route, 200, json.dumps({"candidates": [], "low_confidence": False}))
    page.route(RECOGNIZE_API_URL, handle)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='manual-search']")
    page.locator("[data-testid='manual-search-input']").fill("xyznonexistent")
    page.locator("[data-testid='manual-search-submit']").click()
    page.wait_for_selector("[data-testid='no-results-msg']")


def test_ocr_text_displayed_after_image_submit(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-list']")
    # Expand the OCR details element to make content accessible
    page.locator("details").evaluate("el => el.open = true")
    page.wait_for_selector("[data-testid='ocr-text']")
    ocr_text = page.locator("[data-testid='ocr-text']").inner_text()
    assert "Black Lotus" in ocr_text


def test_network_error_shows_retry_prompt(page: Page):
    mock_network_error(page, RECOGNIZE_API_URL)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload_image(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='error-retry']")
