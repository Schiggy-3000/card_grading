import tempfile
import pytest
from playwright.sync_api import Page
from conftest import (
    BASE_URL, MOCK_GRADE_RESULT, mock_grade_success,
    mock_network_error, small_jpeg_bytes, GRADE_API_URL,
)


def _upload(page: Page, testid: str):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator(f"[data-testid='upload-input-{testid}']").set_input_files(tmp)


def test_grade_page_has_front_and_back_upload_zones(page: Page):
    page.goto(BASE_URL + "/#/grade")
    assert page.locator("[data-testid='upload-zone-front']").is_visible()
    assert page.locator("[data-testid='upload-zone-back']").is_visible()


def test_analyze_button_disabled_until_both_images_uploaded(page: Page):
    page.goto(BASE_URL + "/#/grade")
    btn = page.locator("[data-testid='grade-submit']")
    assert not btn.is_enabled()
    _upload(page, "front")
    assert not btn.is_enabled()
    _upload(page, "back")
    assert btn.is_enabled()


def test_analyze_button_disabled_with_only_back_uploaded(page: Page):
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "back")
    btn = page.locator("[data-testid='grade-submit']")
    assert not btn.is_enabled()


def test_grade_submit_shows_result(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")


def test_grade_result_shows_overall_grade(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    assert "8" in page.locator("[data-testid='overall-grade']").inner_text()


def test_grade_result_shows_all_subgrades(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    result = page.locator("[data-testid='grade-result']").inner_text().lower()
    for dim in ("centering", "corners", "edges", "surface"):
        assert dim in result


def test_grade_result_shows_reasoning(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    result_text = page.locator("[data-testid='grade-result']").inner_text()
    assert "centering is good" in result_text.lower()


def test_grade_result_shows_standard_label(page: Page):
    mock_grade_success(page)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    assert "psa" in page.locator("[data-testid='grade-result']").inner_text().lower()


def test_partial_subgrade_failure_shows_error_indicator(page: Page):
    """Spec: partial grading failure — show available sub-grades, error indicator for failed category."""
    partial_result = {
        **MOCK_GRADE_RESULT,
        "subgrades": {"centering": 8.5, "corners": None, "edges": 9.0, "surface": 7.5},
        "reasoning": {"centering": "Good.", "corners": None, "edges": "Clean.", "surface": "Light."},
    }
    mock_grade_success(page, result=partial_result)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    # Available sub-grades still shown
    assert "8.5" in page.locator("[data-testid='grade-result']").inner_text()
    # Failed category has error indicator
    assert page.locator("[data-testid='subgrade-error-corners']").is_visible()


def test_cgc_result_shows_label_string(page: Page):
    cgc_result = {**MOCK_GRADE_RESULT, "standard": "cgc", "overall": 8.0, "label": "Near Mint"}
    mock_grade_success(page, result=cgc_result)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='grade-result']")
    assert "Near Mint" in page.locator("[data-testid='grade-result']").inner_text()


def test_grade_network_error_shows_retry_prompt(page: Page):
    mock_network_error(page, GRADE_API_URL)
    page.goto(BASE_URL + "/#/grade")
    _upload(page, "front")
    _upload(page, "back")
    page.locator("[data-testid='grade-submit']").click()
    page.wait_for_selector("[data-testid='error-retry']")
