import json
from pathlib import Path
from typing import Any


def read_catalog_file(path: Path) -> dict[str, Any]:
    """Read catalog JSON from disk (HTTP adapter later)."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        msg = f"catalog root must be a JSON object, got {type(data).__name__}"
        raise TypeError(msg)
    return data
