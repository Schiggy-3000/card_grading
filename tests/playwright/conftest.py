import json
import os
import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route

# rstrip("/") normalizes the URL so tests can safely concatenate "/#/..." paths.
# E.g. BASE_URL + "/#/identify" → ".../card_grading/#/identify" (not ".../card_grading//#/identify").
# Vite dev server serves the app at both ".../card_grading" and ".../card_grading/" without redirect.
BASE_URL = os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:5173/card_grading/").rstrip("/")
_RECOGNIZE_API_BASE = os.getenv("VITE_RECOGNIZE_URL", "http://localhost:8081").rstrip("/")
RECOGNIZE_API_URL = _RECOGNIZE_API_BASE + "/**"
_GRADE_API_BASE = os.getenv("VITE_GRADE_URL", "http://localhost:8082").rstrip("/")
GRADE_API_URL = _GRADE_API_BASE + "/**"

# Playwright does NOT auto-add CORS headers to synthetic responses, so cross-origin
# route.fulfill() calls require explicit CORS headers — otherwise the browser validates
# and blocks the response. r.abort() bypasses this check (no response to validate).
_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _fulfill_json(route, status: int, body: str) -> None:
    """Fulfill a route with JSON + CORS headers. Handles OPTIONS preflight automatically."""
    if route.request.method == "OPTIONS":
        route.fulfill(status=200, headers=_CORS_HEADERS)
        return
    route.fulfill(
        status=status,
        content_type="application/json",
        headers=_CORS_HEADERS,
        body=body,
    )

MOCK_CANDIDATES = [
    {
        "name": "Black Lotus",
        "edition": "Limited Edition Alpha",
        "foil": False,
        "language": "EN",
        "collector_number": "232",
        "image_url": "https://cards.scryfall.io/normal/front/b/d/bd8fa327-7f94-4dc6-b75a-e82f84f83eba.jpg",
        "price_usd": 9999.99,
        "confidence": 0.94,
    }
]

_MOCK_GRADE_SIDE = {
    "overall": 8,
    "label": None,
    "subgrades": {
        "centering": 8.5,
        "corners": 7.0,
        "edges": 9.0,
        "surface": 7.5,
    },
    "reasoning": {
        "centering": "Centering is good — margins are nearly equal.",
        "corners": "Minor corner wear visible.",
        "edges": "Edges are clean with no visible nicks.",
        "surface": "Light surface scratching under close inspection.",
    },
    "bbox_image": "",
}

MOCK_GRADE_RESULT = {
    "standard": "psa",
    "front": {**_MOCK_GRADE_SIDE},
    "back": {**_MOCK_GRADE_SIDE, "overall": 7},
}


@pytest.fixture
def page_at_home(page: Page):
    page.goto(BASE_URL)
    return page


def mock_recognize_success(page: Page, candidates=None, low_confidence=False):
    payload = {
        "candidates": candidates or MOCK_CANDIDATES,
        "low_confidence": low_confidence,
        "ocr_text": "Black Lotus\nSorcery\nDestroy all lands.\n0",
    }
    page.route(RECOGNIZE_API_URL, lambda r: _fulfill_json(r, 200, json.dumps(payload)))


def mock_recognize_ocr_failed(page: Page):
    payload = {"candidates": [], "ocr_failed": True, "low_confidence": False}
    page.route(RECOGNIZE_API_URL, lambda r: _fulfill_json(r, 200, json.dumps(payload)))


def mock_grade_success(page: Page, result=None):
    page.route(GRADE_API_URL, lambda r: _fulfill_json(r, 200, json.dumps(result or MOCK_GRADE_RESULT)))


def mock_network_error(page: Page, url_pattern: str):
    page.route(url_pattern, lambda r: r.abort())


def small_jpeg_bytes():
    """Minimal valid JPEG (1x1 pixel white)."""
    return bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
        0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
        0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
        0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
        0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
        0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
        0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
        0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD2,
        0x8A, 0x28, 0x03, 0xFF, 0xD9,
    ])
