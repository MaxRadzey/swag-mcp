import json
from pathlib import Path

import pytest

from swag.exceptions import SpecValidationError
from swag.validation.api_spec import parse_api_spec_json


@pytest.fixture
def openapi3_fixture_path() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "specs" / "openapi3-minimal.json"


@pytest.fixture
def swagger2_fixture_path() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "specs" / "swagger2-minimal.json"


def test_parse_openapi3(openapi3_fixture_path: Path) -> None:
    data = json.loads(openapi3_fixture_path.read_text(encoding="utf-8"))
    doc = parse_api_spec_json(data)
    assert doc.spec_version == "openapi3"
    assert doc.raw["openapi"] == "3.0.0"


def test_parse_swagger2(swagger2_fixture_path: Path) -> None:
    data = json.loads(swagger2_fixture_path.read_text(encoding="utf-8"))
    doc = parse_api_spec_json(data)
    assert doc.spec_version == "swagger2"
    assert doc.raw["swagger"] == "2.0"


def test_invalid_root_raises() -> None:
    with pytest.raises(SpecValidationError):
        parse_api_spec_json({"title": "not a spec"})
