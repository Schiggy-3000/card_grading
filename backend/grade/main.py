import base64
import json
from typing import Tuple

import functions_framework
from flask import Request, Response, make_response

from defect_detection import analyze_with_reasoning
from grade_mapping import map_to_standard

_ALLOWED_STANDARDS = {"psa", "bgs", "cgc", "tag"}


def _json(data: dict, status: int = 200) -> Response:
    return Response(json.dumps(data), status=status, mimetype="application/json")


def _add_cors(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@functions_framework.http
def grade(request: Request) -> Tuple:
    if request.method == "OPTIONS":
        return _add_cors(make_response("", 204))
    if request.method != "POST":
        return _json({"error": "Method not allowed"}), 405

    data = request.get_json(silent=True) or {}
    standard = data.get("standard", "").lower()
    if standard not in _ALLOWED_STANDARDS:
        return _json({"error": f"standard must be one of {sorted(_ALLOWED_STANDARDS)}"}), 400
    if "front" not in data:
        return _json({"error": "Missing required field: front"}), 400
    if "back" not in data:
        return _json({"error": "Missing required field: back"}), 400

    try:
        front_bytes = base64.b64decode(data["front"])
        back_bytes = base64.b64decode(data["back"])
    except Exception:
        return _json({"error": "Invalid base64 image data"}), 400

    try:
        subgrades, reasoning = analyze_with_reasoning(front_bytes, back_bytes)
    except Exception as e:
        return _json({"error": f"Image analysis failed: {str(e)}"}), 500

    result = map_to_standard(subgrades, standard)
    result["reasoning"] = reasoning

    return _add_cors(_json(result)), 200
