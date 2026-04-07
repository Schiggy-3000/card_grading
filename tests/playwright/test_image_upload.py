import tempfile
from pathlib import Path
import pytest
from playwright.sync_api import Page
from conftest import BASE_URL, small_jpeg_bytes


def _goto_identify(page: Page):
    page.goto(BASE_URL + "/#/identify")


def test_upload_input_accepts_valid_jpeg(page: Page):
    _goto_identify(page)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator("[data-testid='upload-input-front']").set_input_files(tmp)
    assert page.locator("[data-testid='upload-zone-front'] [data-testid='file-name']").is_visible()


def test_upload_rejects_unsupported_type(page: Page):
    _goto_identify(page)
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
        f.write(b"GIF87a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;")
        tmp = f.name
    page.locator("[data-testid='upload-input-front']").set_input_files(tmp)
    error = page.locator("[data-testid='upload-zone-front'] [role='alert']")
    assert error.is_visible()
    assert "format" in error.inner_text().lower()


def test_upload_rejects_oversized_file(page: Page):
    _goto_identify(page)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        # Write 11 MB of zeros (exceeds 10 MB limit)
        f.write(bytes(11 * 1024 * 1024))
        tmp = f.name
    page.locator("[data-testid='upload-input-front']").set_input_files(tmp)
    error = page.locator("[data-testid='upload-zone-front'] [role='alert']")
    assert error.is_visible()
    assert "large" in error.inner_text().lower()


def test_upload_zone_shows_hint_before_file(page: Page):
    _goto_identify(page)
    hint = page.locator("[data-testid='upload-zone-front'] [data-testid='upload-hint']")
    assert hint.is_visible()


def test_upload_zone_shows_filename_after_valid_upload(page: Page):
    _goto_identify(page)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(small_jpeg_bytes())
        tmp = f.name
    page.locator("[data-testid='upload-input-front']").set_input_files(tmp)
    file_name = page.locator("[data-testid='upload-zone-front'] [data-testid='file-name']")
    assert file_name.is_visible()
    assert ".jpg" in file_name.inner_text()
