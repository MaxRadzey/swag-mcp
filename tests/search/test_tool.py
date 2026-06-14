import json
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

from swag.app.gateway import SpecGateway
from swag.app.tools import register_tools
from swag.catalog.service import CatalogService
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
                },
            },
        }
    ).encode()


def test_search_spec_tool_returns_ranked_hits(fixture_catalog_path: Path) -> None:
    catalog = CatalogService(fixture_catalog_path)
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=_spec_body())))
    spec_service = SpecService(catalog, client)
    spec_search = SpecGateway(spec_service)
    mcp = FastMCP("test")
    register_tools(mcp, catalog=catalog, spec_search=spec_search)

    tool = mcp._tool_manager._tools["search_spec"]
    result = tool.fn(service_id="alpha-api", query="create user", method="POST")

    assert result.service_id == "alpha-api"
    assert result.hits[0].operation_id == "createUser"
    assert result.hits[0].method == "POST"
    assert result.total_candidates == 1
    client.close()
