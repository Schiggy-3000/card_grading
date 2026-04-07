from confidence import score_from_ocr, score_from_query, LOW_CONFIDENCE_THRESHOLD


def test_exact_match_gives_high_score():
    assert score_from_ocr("Black Lotus", "Black Lotus") > 0.9


def test_one_char_difference_gives_high_score():
    # "Black Lorus" vs "Black Lotus" — OCR noise on aged cards
    assert score_from_ocr("Black Lorus", "Black Lotus") > 0.8


def test_completely_wrong_gives_low_score():
    assert score_from_ocr("Zzzz Qqqqq", "Black Lotus") < 0.3


def test_manual_search_exact_match():
    assert score_from_query("Black Lotus", "Black Lotus") == 1.0


def test_manual_search_partial_match():
    score = score_from_query("Black Lotus", "Black Lotus Alpha Edition")
    assert 0.5 < score < 1.0


def test_low_confidence_threshold_constant_exists():
    assert LOW_CONFIDENCE_THRESHOLD == 0.3
