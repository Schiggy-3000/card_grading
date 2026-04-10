import tempfile
import pytest
from playwright.sync_api import Page
from conftest import BASE_URL, mock_recognize_success, mock_grade_success, small_jpeg_bytes


def _upload(page: Page, testid: str):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator(f"[data-testid='upload-input-{testid}']").set_input_files(tmp)


def _do_identify(page: Page):
    mock_recognize_success(page)
    page.goto(BASE_URL + "/#/identify")
    page.locator("[data-testid='game-mtg']").click()
    _upload(page, "front")
    page.locator("[data-testid='identify-submit']").click()
    page.wait_for_selector("[data-testid='candidate-item']")
    page.locator("[data-testid='candidate-item']").first.click()
    page.wait_for_selector("[data-testid='card-detail']")


def _do_grade(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")


def test_history_page_empty_initially(page: Page):
    page.goto(BASE_URL + "/#/history")
    assert page.locator("[data-testid='history-empty']").is_visible()


def test_home_footer_shows_zero_initially(page: Page):
    page.goto(BASE_URL)
    assert "0" in page.locator("[data-testid='footer']").inner_text()


def test_identify_adds_history_entry(page: Page):
    _do_identify(page)
    # Navigate via hash change (not full reload) to preserve React in-memory state
    page.goto(BASE_URL + "/#/")
    footer = page.locator("[data-testid='footer']").inner_text()
    assert "1" in footer


def test_grade_adds_history_entry(page: Page):
    _do_grade(page)
    # Navigate via hash change (not full reload) to preserve React in-memory state
    page.goto(BASE_URL + "/#/")
    assert "1" in page.locator("[data-testid='footer']").inner_text()


def test_history_page_shows_entry_after_identify(page: Page):
    _do_identify(page)
    page.goto(BASE_URL + "/#/history")
    assert page.locator("[data-testid='history-entry']").count() == 1
    entry_text = page.locator("[data-testid='history-entry']").first.inner_text()
    assert "Identify" in entry_text or "identify" in entry_text.lower()
    assert "Black Lotus" in entry_text


def test_history_entry_shows_timestamp(page: Page):
    _do_identify(page)
    page.goto(BASE_URL + "/#/history")
    entry = page.locator("[data-testid='history-entry']").first.inner_text()
    # timestamp contains date digits e.g. "2026"
    assert "2026" in entry or ":" in entry  # ISO timestamp has colons


def test_history_clears_on_page_reload(page: Page):
    _do_identify(page)
    # Navigate via hash change to preserve state, then verify count before reload
    page.goto(BASE_URL + "/#/")
    assert "1" in page.locator("[data-testid='footer']").inner_text()
    # Full reload should clear in-memory sessionHistory
    page.reload()
    assert "0" in page.locator("[data-testid='footer']").inner_text()


def test_clicking_identify_entry_shows_card_detail(page: Page):
    _do_identify(page)
    page.goto(BASE_URL + "/#/history")
    page.locator("[data-testid='history-entry']").first.click()
    page.wait_for_selector("[data-testid='history-result']")
    assert "Black Lotus" in page.locator("[data-testid='history-result']").inner_text()


def test_clicking_grade_entry_shows_grade_result(page: Page):
    _do_grade(page)
    page.goto(BASE_URL + "/#/history")
    page.locator("[data-testid='history-entry']").first.click()
    page.wait_for_selector("[data-testid='history-result']")
    assert page.locator("[data-testid='grade-result']").is_visible()


def test_clicking_entry_twice_collapses_result(page: Page):
    _do_identify(page)
    page.goto(BASE_URL + "/#/history")
    entry = page.locator("[data-testid='history-entry']").first
    entry.click()
    page.wait_for_selector("[data-testid='history-result']")
    entry.click()
    assert not page.locator("[data-testid='history-result']").is_visible()
