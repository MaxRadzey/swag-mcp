import json
from pathlib import Path

import httpx
import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from swag.app.gateway import SpecGateway
from swag.app.tools import register_tools
from swag.catalog.service import CatalogService
from swag.spec.service import SpecService


def _spec_body() -> bytes:
    return json.dumps(
        {
            "openapi": "3.0.0",
            "info": {"title": "Pets", "version": "1.0.0"},
            "paths": {
                "/pet": {
                    "post": {
                        "operationId": "addPet",
                        "summary": "Add a new pet to the store",
                        "tags": ["pet"],
                        "requestBody": {
                            "required": True,
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Pet"}}},
                        },
                        "responses": {"200": {"description": "ok"}},
                    },
                },
            },
            "components": {"schemas": {"Pet": {"type": "object", "properties": {"name": {"type": "string"}}}}},
        }
    ).encode()


def _build_mcp(fixture_catalog_path: Path) -> tuple[FastMCP, httpx.AsyncClient]:
    catalog = CatalogService(fixture_catalog_path)
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=_spec_body())))
    spec_search = SpecGateway(SpecService(catalog, client))
    mcp = FastMCP("test")
    register_tools(mcp, catalog=catalog, spec_search=spec_search)
    return mcp, client


async def test_full_flow_list_search_get(fixture_catalog_path: Path) -> None:
    mcp, client = _build_mcp(fixture_catalog_path)
    tools = mcp._tool_manager._tools

    services = tools["list_services"].fn()
    service_ids = {summary.id for summary in services}
    assert "alpha-api" in service_ids

    search = await tools["search_spec"].fn(service_id="alpha-api", query="add a new pet")
    top = search.hits[0]
    assert top.operation_id == "addPet"
    assert top.method == "POST"

    detail = await tools["get_operation"].fn(service_id="alpha-api", method=top.method, path=top.path)
    assert detail.request_body is not None
    assert detail.request_body.content[0].json_schema == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }
    await client.aclose()


async def test_search_spec_unknown_service_raises_tool_error(fixture_catalog_path: Path) -> None:
    mcp, client = _build_mcp(fixture_catalog_path)

    tool = mcp._tool_manager._tools["search_spec"]
    with pytest.raises(ToolError):
        await tool.fn(service_id="does-not-exist", query="anything")
    await client.aclose()
