from mcp.server.fastmcp import FastMCP

from swag.app.gateway import SpecGateway
from swag.catalog.service import CatalogService
from swag.catalog.tool import register_list_services_tool
from swag.operation.tool import register_get_operation_tool
from swag.search.tool import register_search_spec_tool


def register_tools(mcp: FastMCP, *, catalog: CatalogService, spec_search: SpecGateway) -> None:
    register_list_services_tool(mcp, catalog)
    register_search_spec_tool(mcp, spec_search)
    register_get_operation_tool(mcp, spec_search)
