import json
from typing import Any

from swag.exceptions import SpecDecodeError


def decode_spec_json(body: bytes) -> dict[str, Any]:
    """Decode spec response body as JSON object."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        msg = "spec body is not valid JSON"
        raise SpecDecodeError(msg) from exc
    if not isinstance(data, dict):
        msg = f"spec root must be a JSON object, got {type(data).__name__}"
        raise SpecDecodeError(msg)
    return data
