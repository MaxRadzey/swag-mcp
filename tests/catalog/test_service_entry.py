import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from swag.catalog.models import ServiceEntry


def test_valid_service_entry_from_fixture(fixture_catalog_path: Path) -> None:
    raw = json.loads(fixture_catalog_path.read_text(encoding="utf-8"))
    entry = ServiceEntry.model_validate(raw["services"][0])
    assert entry.id == "alpha-api"
    assert entry.name == "Alpha API"
    assert str(entry.spec_url) == "https://example.com/openapi/alpha-api.json"


def test_empty_id_raises() -> None:
    with pytest.raises(ValidationError):
        ServiceEntry.model_validate(
            {
                "id": "",
                "name": "Test",
                "description": "Desc",
                "spec_url": "https://example.com/openapi/test.json",
            }
        )


def test_empty_name_raises() -> None:
    with pytest.raises(ValidationError):
        ServiceEntry.model_validate(
            {
                "id": "test-api",
                "name": "",
                "description": "Desc",
                "spec_url": "https://example.com/openapi/test.json",
            }
        )


def test_invalid_spec_url_raises() -> None:
    with pytest.raises(ValidationError):
        ServiceEntry.model_validate(
            {
                "id": "test-api",
                "name": "Test",
                "description": "Desc",
                "spec_url": "not-a-url",
            }
        )
