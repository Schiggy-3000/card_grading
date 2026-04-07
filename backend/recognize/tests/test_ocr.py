from unittest.mock import MagicMock, patch


def _mock_vision_client(extracted_text: str):
    annotation = MagicMock()
    annotation.description = extracted_text
    response = MagicMock()
    response.error.message = ""
    response.text_annotations = [annotation]
    client = MagicMock()
    client.text_detection.return_value = response
    return client


def test_extract_text_returns_string():
    from ocr import extract_text
    client = _mock_vision_client("Black Lotus\n0\nMono Artifact")
    with patch("ocr.vision.ImageAnnotatorClient", return_value=client):
        result = extract_text(b"fake_image_bytes")
    assert isinstance(result, str)
    assert "Black Lotus" in result


def test_extract_text_returns_empty_string_when_no_annotations():
    from ocr import extract_text
    response = MagicMock()
    response.error.message = ""
    response.text_annotations = []
    client = MagicMock()
    client.text_detection.return_value = response
    with patch("ocr.vision.ImageAnnotatorClient", return_value=client):
        result = extract_text(b"fake_image_bytes")
    assert result == ""


def test_extract_text_raises_on_api_error():
    from ocr import extract_text
    response = MagicMock()
    response.error.message = "Permission denied"
    response.text_annotations = []
    client = MagicMock()
    client.text_detection.return_value = response
    with patch("ocr.vision.ImageAnnotatorClient", return_value=client):
        import pytest
        with pytest.raises(RuntimeError, match="Vision API error"):
            extract_text(b"fake_image_bytes")


def test_first_line_extraction():
    from ocr import first_line
    assert first_line("Black Lotus\n0\nMono Artifact") == "Black Lotus"
    assert first_line("") == ""
    assert first_line("Only one line") == "Only one line"
