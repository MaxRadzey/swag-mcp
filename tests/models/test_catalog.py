import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from swag.models.catalog import Catalog


def test_valid_catalog_from_fixture(fixture_catalog_path: Path) -> None:
    raw = json.loads(fixture_catalog_path.read_text(encoding="utf-8"))
    catalog = Catalog.model_validate(raw)
    assert len(catalog.services) == 3
    assert catalog.services[0].id == "alpha-api"
    assert catalog.services[1].id == "beta-api"
    assert catalog.services[2].id == "gamma-api"


def test_duplicate_service_id_raises(fixture_catalog_path: Path) -> None:
    raw = json.loads(fixture_catalog_path.read_text(encoding="utf-8"))
    raw["services"][1]["id"] = raw["services"][0]["id"]
    with pytest.raises(ValidationError):
        Catalog.model_validate(raw)


def test_empty_services_raises() -> None:
    with pytest.raises(ValidationError):
        Catalog.model_validate({"services": []})
