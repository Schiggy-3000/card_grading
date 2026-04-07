from grade_mapping import map_to_standard, CGC_LABELS


def test_psa_overall_is_integer():
    result = map_to_standard({"centering": 9.0, "corners": 8.5, "edges": 9.0, "surface": 8.0}, "psa")
    assert isinstance(result["overall"], int)
    assert 1 <= result["overall"] <= 10
    assert result["label"] is None


def test_bgs_overall_is_half_point():
    result = map_to_standard({"centering": 9.0, "corners": 8.5, "edges": 9.0, "surface": 8.0}, "bgs")
    overall = result["overall"]
    assert isinstance(overall, float)
    assert (overall * 2) == int(overall * 2)  # must be a multiple of 0.5
    assert result["label"] is None


def test_cgc_has_label():
    result = map_to_standard({"centering": 9.0, "corners": 9.0, "edges": 9.0, "surface": 9.0}, "cgc")
    assert result["label"] is not None
    assert isinstance(result["label"], str)


def test_tag_overall_has_one_decimal():
    result = map_to_standard({"centering": 7.0, "corners": 6.5, "edges": 7.0, "surface": 6.0}, "tag")
    overall = result["overall"]
    assert isinstance(overall, float)
    assert round(overall, 1) == overall  # max 1 decimal


def test_output_contains_standard_field():
    for std in ("psa", "bgs", "cgc", "tag"):
        result = map_to_standard({"centering": 8.0, "corners": 8.0, "edges": 8.0, "surface": 8.0}, std)
        assert result["standard"] == std


def test_subgrades_pass_through():
    subgrades = {"centering": 8.5, "corners": 7.0, "edges": 9.0, "surface": 6.5}
    result = map_to_standard(subgrades, "psa")
    assert result["subgrades"] == subgrades


def test_all_low_scores_give_low_grade():
    result = map_to_standard({"centering": 2.0, "corners": 2.0, "edges": 2.0, "surface": 2.0}, "psa")
    assert result["overall"] <= 4


def test_all_high_scores_give_high_grade():
    result = map_to_standard({"centering": 9.5, "corners": 9.5, "edges": 9.5, "surface": 9.5}, "psa")
    assert result["overall"] >= 8
