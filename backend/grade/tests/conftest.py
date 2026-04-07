from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
MTG_FRONT = REPO_ROOT / "images" / "MTG" / "Black_Lotus_Unlimited_Front.jpg"
MTG_BACK  = REPO_ROOT / "images" / "MTG" / "Black_Lotus_Unlimited_Back.jpg"
FAB_FRONT = REPO_ROOT / "images" / "FAB" / "Command_and_Conquer_The_Hunted_Extended_Art_Rainbow_Foil_Front.png"
FAB_BACK  = REPO_ROOT / "images" / "FAB" / "Command_and_Conquer_The_Hunted_Extended_Art_Rainbow_Foil_Back.png"


@pytest.fixture
def mtg_front_bytes():
    return MTG_FRONT.read_bytes()


@pytest.fixture
def mtg_back_bytes():
    return MTG_BACK.read_bytes()


@pytest.fixture
def fab_front_bytes():
    return FAB_FRONT.read_bytes()


def make_request(body, method="POST"):
    from unittest.mock import MagicMock
    req = MagicMock()
    req.method = method
    req.get_json.return_value = body
    return req
