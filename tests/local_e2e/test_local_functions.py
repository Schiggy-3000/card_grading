"""
Local end-to-end test: exercises both GCF handlers with real card images.
Requires GOOGLE_APPLICATION_CREDENTIALS to be set.
Run: GOOGLE_APPLICATION_CREDENTIALS=.credentials/... pytest tests/local_e2e/ -v -s
"""
import base64
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
MTG_FRONT = REPO_ROOT / "images" / "MTG" / "Black_Lotus_Unlimited_Front.jpg"
FAB_FRONT = REPO_ROOT / "images" / "FAB" / "Command_and_Conquer_The_Hunted_Extended_Art_Rainbow_Foil_Front.png"
FAB_BACK  = REPO_ROOT / "images" / "FAB" / "Command_and_Conquer_The_Hunted_Extended_Art_Rainbow_Foil_Back.png"
MTG_BACK  = REPO_ROOT / "images" / "MTG" / "Black_Lotus_Unlimited_Back.jpg"

RECOGNIZE_DIR = str(REPO_ROOT / "backend" / "recognize")
GRADE_DIR = str(REPO_ROOT / "backend" / "grade")


def _load_module(alias: str, file_path: Path, search_dir: str):
    """Load main.py from a specific directory under a unique alias to avoid sys.modules collisions."""
    if search_dir not in sys.path:
        sys.path.insert(0, search_dir)
    sys.modules.pop(alias, None)
    spec = importlib.util.spec_from_file_location(alias, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def make_request(body):
    req = MagicMock()
    req.method = "POST"
    req.get_json.return_value = body
    return req


def test_recognize_mtg_card_image():
    recognize = _load_module("recognize_main", Path(RECOGNIZE_DIR) / "main.py", RECOGNIZE_DIR).recognize
    image_b64 = base64.b64encode(MTG_FRONT.read_bytes()).decode()
    resp, status = recognize(make_request({"image": image_b64, "game": "mtg"}))
    body = resp.get_json()
    print(f"\nCandidates: {[c['name'] for c in body.get('candidates', [])]}")
    assert status == 200
    assert "candidates" in body


def test_recognize_manual_search_mtg():
    recognize = _load_module("recognize_main", Path(RECOGNIZE_DIR) / "main.py", RECOGNIZE_DIR).recognize
    resp, status = recognize(make_request({"query": "Black Lotus", "game": "mtg"}))
    body = resp.get_json()
    assert status == 200
    assert len(body["candidates"]) > 0
    assert body["candidates"][0]["name"] == "Black Lotus"


def test_recognize_fab_card_image():
    recognize = _load_module("recognize_main", Path(RECOGNIZE_DIR) / "main.py", RECOGNIZE_DIR).recognize
    image_b64 = base64.b64encode(FAB_FRONT.read_bytes()).decode()
    resp, status = recognize(make_request({"image": image_b64, "game": "fab"}))
    body = resp.get_json()
    print(f"\nCandidates: {[c['name'] for c in body.get('candidates', [])]}")
    assert status == 200


def test_grade_mtg_card():
    grade = _load_module("grade_main", Path(GRADE_DIR) / "main.py", GRADE_DIR).grade
    front_b64 = base64.b64encode(MTG_FRONT.read_bytes()).decode()
    back_b64  = base64.b64encode(MTG_BACK.read_bytes()).decode()
    resp, status = grade(make_request({"front": front_b64, "back": back_b64, "standard": "psa"}))
    body = resp.get_json()
    print(f"\nGrade result: {body}")
    assert status == 200
    assert isinstance(body["overall"], int)
    assert all(k in body["subgrades"] for k in ("centering", "corners", "edges", "surface"))
