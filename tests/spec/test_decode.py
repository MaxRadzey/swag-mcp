import json
from pathlib import Path

import pytest

from swag.exceptions import SpecDecodeError
from swag.spec.decode import decode_spec_body


@pytest.fixture
def openapi3_fixture_path() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "specs" / "openapi3-minimal.json"


def test_decode_valid_json(openapi3_fixture_path: Path) -> None:
    data = decode_spec_body(openapi3_fixture_path.read_bytes())
    assert data["openapi"] == "3.0.0"


def test_decode_valid_yaml() -> None:
    body = b"openapi: 3.0.0\npaths:\n  /pets:\n    get:\n      summary: List pets\n"
    data = decode_spec_body(body)
    assert data["openapi"] == "3.0.0"
    assert data["paths"]["/pets"]["get"]["summary"] == "List pets"


def test_non_object_root_raises() -> None:
    with pytest.raises(SpecDecodeError):
        decode_spec_body(json.dumps(["a"]).encode())


def test_invalid_body_raises() -> None:
    with pytest.raises(SpecDecodeError):
        decode_spec_body(b"{ not: valid: json: or: yaml")
