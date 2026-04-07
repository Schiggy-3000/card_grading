from google.cloud import vision


def extract_text(image_bytes: bytes) -> str:
    """Send image bytes to Cloud Vision TEXT_DETECTION. Returns full extracted text."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    if response.error.message:
        raise RuntimeError(f"Vision API error: {response.error.message}")
    if not response.text_annotations:
        return ""
    return response.text_annotations[0].description


def first_line(text: str) -> str:
    """Return the first non-empty line of OCR output (usually the card name)."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""
