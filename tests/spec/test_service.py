from pathlib import Path

import httpx
import pytest

from swag.catalog.service import CatalogService
from swag.exceptions import ServiceNotFoundError
from swag.spec.service import SpecService


@pytest.fixture
def openapi3_fixture_path() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "specs" / "openapi3-minimal.json"


@pytest.fixture
def spec_body(openapi3_fixture_path: Path) -> bytes:
    return openapi3_fixture_path.read_bytes()


def _make_spec_client(spec_body: bytes) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=spec_body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_get_fetches_and_parses_spec(
    fixture_catalog_path: Path,
    spec_body: bytes,
) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = _make_spec_client(spec_body)
    service = SpecService(catalog, client)

    doc = service.get("alpha-api")

    assert doc.spec_version == "openapi3"
    assert doc.raw["info"]["title"] == "Minimal API"
    client.close()


def test_get_uses_cache(fixture_catalog_path: Path, spec_body: bytes) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = _make_spec_client(spec_body)
    service = SpecService(catalog, client)

    first = service.get("alpha-api")
    second = service.get("alpha-api")

    assert first is second
    client.close()


def test_unknown_service_raises(fixture_catalog_path: Path, spec_body: bytes) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = _make_spec_client(spec_body)
    service = SpecService(catalog, client)

    with pytest.raises(ServiceNotFoundError):
        service.get("unknown-api")
    client.close()
