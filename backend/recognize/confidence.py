from difflib import SequenceMatcher

LOW_CONFIDENCE_THRESHOLD = 0.3


def score_from_ocr(ocr_first_line: str, card_name: str) -> float:
    """Fuzzy match ratio between first OCR line and a candidate card name."""
    return SequenceMatcher(
        None, ocr_first_line.lower(), card_name.lower()
    ).ratio()


def score_from_query(query: str, card_name: str) -> float:
    """Fuzzy match ratio for manual text search (no OCR component)."""
    return SequenceMatcher(None, query.lower(), card_name.lower()).ratio()
