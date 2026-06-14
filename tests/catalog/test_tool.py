from pathlib import Path

from mcp.server.fastmcp import FastMCP

from swag.catalog.service import CatalogService
from swag.catalog.tool import register_list_services_tool


def test_list_services_tool_returns_public_summaries(fixture_catalog_path: Path) -> None:
    catalog = CatalogService(fixture_catalog_path)
    mcp = FastMCP("test")
    register_list_services_tool(mcp, catalog)

    tool = mcp._tool_manager._tools["list_services"]
    result = tool.fn()

    expected = catalog.list_public()
    assert result == expected
    assert len(result) == 3
    assert [item.model_dump() for item in result] == [item.model_dump() for item in expected]
    assert all(set(item.model_dump().keys()) == {"id", "name", "description"} for item in result)
