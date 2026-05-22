import json
from pathlib import Path

import pytest

from swag.adapters.spec_json import decode_spec_json
from swag.exceptions import SpecDecodeError


@pytest.fixture
def openapi3_fixture_path() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "specs" / "openapi3-minimal.json"


def test_decode_valid_json(openapi3_fixture_path: Path) -> None:
    body = openapi3_fixture_path.read_bytes()
    data = decode_spec_json(body)
    assert data["openapi"] == "3.0.0"


def test_invalid_json_raises() -> None:
    with pytest.raises(SpecDecodeError):
        decode_spec_json(b"not json")


def test_non_object_root_raises() -> None:
    with pytest.raises(SpecDecodeError):
        decode_spec_json(json.dumps(["a"]).encode())
