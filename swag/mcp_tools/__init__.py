from mcp.server.fastmcp import FastMCP

from swag.mcp_tools.list_services import register_list_services_tool
from swag.services.catalog import CatalogService


def register_tools(mcp: FastMCP, *, catalog: CatalogService) -> None:
    register_list_services_tool(mcp, catalog)
