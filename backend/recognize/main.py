import base64
import json
from typing import Tuple

import functions_framework
from flask import Request, Response, make_response

from confidence import LOW_CONFIDENCE_THRESHOLD, score_from_ocr, score_from_query
from fab_lookup import search_fab
from mtg_lookup import search_mtg
from ocr import extract_text, first_line

_ALLOWED_GAMES = {"mtg", "fab"}


def _json(data: dict, status: int = 200) -> Response:
    return Response(json.dumps(data), status=status, mimetype="application/json")


def _add_cors(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@functions_framework.http
def recognize(request: Request) -> Tuple:
    if request.method == "OPTIONS":
        return _add_cors(make_response("", 204))
    if request.method != "POST":
        return _json({"error": "Method not allowed"}), 405

    data = request.get_json(silent=True) or {}
    game = data.get("game")
    if game not in _ALLOWED_GAMES:
        return _json({"error": f"game must be one of {sorted(_ALLOWED_GAMES)}"}), 400

    search_fn = search_mtg if game == "mtg" else search_fab

    # Manual search mode
    if "query" in data:
        query = str(data["query"]).strip()
        candidates = search_fn(query)
        for c in candidates:
            c["confidence"] = round(score_from_query(query, c["name"]), 4)
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        low_conf = all(c["confidence"] < LOW_CONFIDENCE_THRESHOLD for c in candidates) if candidates else False
        return _add_cors(_json({"candidates": candidates, "low_confidence": low_conf})), 200

    # Image recognition mode
    if "image" not in data:
        return _json({"error": "Must provide 'image' or 'query'"}), 400

    try:
        image_bytes = base64.b64decode(data["image"])
    except Exception:
        return _json({"error": "Invalid base64 image data"}), 400

    try:
        raw_text = extract_text(image_bytes)
    except RuntimeError:
        raw_text = ""

    if not raw_text:
        return _add_cors(_json({"candidates": [], "ocr_failed": True, "low_confidence": False})), 200

    card_name_guess = first_line(raw_text)
    candidates = search_fn(card_name_guess)

    for c in candidates:
        c["confidence"] = round(score_from_ocr(card_name_guess, c["name"]), 4)
    candidates.sort(key=lambda x: x["confidence"], reverse=True)

    low_conf = all(c["confidence"] < LOW_CONFIDENCE_THRESHOLD for c in candidates) if candidates else False
    return _add_cors(_json({"candidates": candidates, "low_confidence": low_conf})), 200
