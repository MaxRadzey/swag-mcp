from mcp.server.fastmcp import FastMCP

from swag.catalog.models import ServiceSummary
from swag.catalog.service import CatalogService


def register_list_services_tool(mcp: FastMCP, catalog: CatalogService) -> None:
    @mcp.tool()
    def list_services() -> list[ServiceSummary]:
        """List available API services (metadata only, no OpenAPI)."""
        return catalog.list_public()
