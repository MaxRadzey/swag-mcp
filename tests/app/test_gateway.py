import json
from pathlib import Path

import httpx
import pytest

from swag.app.gateway import SpecGateway
from swag.catalog.service import CatalogService
from swag.exceptions import ServiceNotFoundError
from swag.search.models import SearchQuery
from swag.spec.service import SpecService


def _spec_body() -> bytes:
    return json.dumps(
        {
            "openapi": "3.0.0",
            "info": {"title": "Users", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                        "tags": ["users"],
                        "responses": {"201": {"description": "Created"}},
                    },
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List users",
                        "tags": ["users"],
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            },
        }
    ).encode()


def test_search_returns_ranked_hits(fixture_catalog_path: Path) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=_spec_body())))
    spec_service = SpecService(catalog, client)
    search_service = SpecGateway(spec_service)

    response = search_service.search("alpha-api", SearchQuery(query="create user", method="POST"))

    assert response.service_id == "alpha-api"
    assert response.total_candidates == 2
    assert response.hits[0].operation_id == "createUser"
    assert response.hits[0].method == "POST"
    client.close()


def test_search_reuses_spec_service_cache(fixture_catalog_path: Path) -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, content=_spec_body())

    catalog = CatalogService(fixture_catalog_path)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    spec_service = SpecService(catalog, client)
    search_service = SpecGateway(spec_service)

    search_service.search("alpha-api", SearchQuery(query="create user"))
    search_service.search("alpha-api", SearchQuery(query="list user"))

    assert call_count == 1
    client.close()


def test_search_unknown_service_raises(fixture_catalog_path: Path) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=_spec_body())))
    spec_service = SpecService(catalog, client)
    search_service = SpecGateway(spec_service)

    with pytest.raises(ServiceNotFoundError):
        search_service.search("unknown-api", SearchQuery(query="create user"))

    client.close()
