import json
from typing import Any

import yaml

from swag.exceptions import SpecDecodeError


def decode_spec_body(body: bytes) -> dict[str, Any]:
    """Decode a spec response body as a JSON or YAML object.

    JSON is attempted first (strict and fast); on failure the body is parsed as
    YAML (a JSON superset), which covers ``.yaml`` specs. The root must be a
    mapping.
    """
    data = _parse(body)
    if not isinstance(data, dict):
        msg = f"spec root must be a JSON/YAML object, got {type(data).__name__}"
        raise SpecDecodeError(msg)
    return data


def _parse(body: bytes) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        pass
    try:
        return yaml.safe_load(body)
    except yaml.YAMLError as exc:
        msg = "spec body is not valid JSON or YAML"
        raise SpecDecodeError(msg) from exc
