import pytest
from playwright.sync_api import Page
from conftest import BASE_URL


def test_home_shows_identify_and_grade_cards(page: Page):
    page.goto(BASE_URL)
    assert page.locator("text=Identify").count() >= 1
    assert page.locator("text=Grade").count() >= 1


def test_identify_card_navigates_to_identify_page(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-tool='identify']").click()
    assert "identify" in page.url.lower()


def test_grade_card_navigates_to_grade_page(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-tool='grade']").click()
    assert "grade" in page.url.lower()


def test_settings_icon_opens_settings_panel(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-testid='settings-btn']").click()
    assert page.locator("[data-testid='settings-panel']").is_visible()


def test_settings_standard_defaults_to_psa(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-testid='settings-btn']").click()
    active = page.locator("[data-testid='settings-panel'] [aria-pressed='true']")
    assert active.inner_text().lower() == "psa"


def test_settings_standard_change_persists_on_reload(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-testid='settings-btn']").click()
    page.locator("[data-testid='std-cgc']").click()
    page.reload()
    page.locator("[data-testid='settings-btn']").click()
    active = page.locator("[data-testid='settings-panel'] [aria-pressed='true']")
    assert active.inner_text().lower() == "cgc"


def test_footer_shows_current_standard(page: Page):
    page.goto(BASE_URL)
    footer = page.locator("[data-testid='footer']")
    assert "psa" in footer.inner_text().lower()


def test_footer_shows_zero_history_initially(page: Page):
    page.goto(BASE_URL)
    footer = page.locator("[data-testid='footer']")
    assert "0" in footer.inner_text()
