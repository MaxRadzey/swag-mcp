import json
import shutil
from pathlib import Path

import pytest

from swag.services.catalog import CatalogService


def test_load_returns_three_services(fixture_catalog_path: Path) -> None:
    service = CatalogService(fixture_catalog_path)
    by_id = service.load()
    assert set(by_id.keys()) == {"alpha-api", "beta-api", "gamma-api"}
    assert by_id["alpha-api"].name == "Alpha API"


def test_load_list_preserves_file_order(fixture_catalog_path: Path) -> None:
    service = CatalogService(fixture_catalog_path)
    entries = service.load_list()
    assert [entry.id for entry in entries] == ["alpha-api", "beta-api", "gamma-api"]


def test_load_uses_cache(fixture_catalog_path: Path) -> None:
    service = CatalogService(fixture_catalog_path)
    first = service.load()
    second = service.load()
    assert first is second


def test_reload_picks_up_file_changes(fixture_catalog_path: Path, tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    shutil.copy(fixture_catalog_path, catalog_path)
    service = CatalogService(catalog_path)
    assert len(service.load()) == 3

    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    raw["services"] = raw["services"][:1]
    catalog_path.write_text(json.dumps(raw), encoding="utf-8")

    service.reload()
    by_id = service.load()
    assert set(by_id.keys()) == {"alpha-api"}


def test_cache_expires_after_ttl(
    fixture_catalog_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog_path = tmp_path / "catalog.json"
    shutil.copy(fixture_catalog_path, catalog_path)
    service = CatalogService(catalog_path, ttl_seconds=10)

    monotonic_values = iter([100.0, 120.0, 120.0])

    def fake_monotonic() -> float:
        return next(monotonic_values, 120.0)

    monkeypatch.setattr("swag.services.catalog.time.monotonic", fake_monotonic)
    first = service.load()

    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    raw["services"][0]["name"] = "Alpha API Updated"
    catalog_path.write_text(json.dumps(raw), encoding="utf-8")

    second = service.load()
    assert second is not first
    assert second["alpha-api"].name == "Alpha API Updated"
