import pytest

SAMPLE_FAB_CARD = {
    "unique_id": "abc123",
    "name": "Command and Conquer",
    "pitch": "1",
    "printing_unique_id": "xyz789",
    "set_id": "HNT",
    "edition": "First Edition",
    "foiling": "Rainbow Foil",
    "rarity": "Legendary",
    "image_url": "https://storage.googleapis.com/fabmaster/cardfaces/2024-HNT/EN/HNT260.png",
    "language": "EN",
}

SAMPLE_FAB_DATA = [SAMPLE_FAB_CARD] * 1  # real tests add more entries


def make_request(body, method="POST"):
    """Create a mock Flask request for GCF handler tests."""
    from unittest.mock import MagicMock
    req = MagicMock()
    req.method = method
    req.get_json.return_value = body
    return req
