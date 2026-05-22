from mcp.server.fastmcp import FastMCP

from swag.config import Settings
from swag.mcp_instructions import SERVER_INSTRUCTIONS
from swag.mcp_tools import register_tools
from swag.services.catalog import CatalogService


def create_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or Settings()
    catalog = CatalogService(settings.catalog_path)

    mcp = FastMCP(
        settings.server_name,
        instructions=SERVER_INSTRUCTIONS,
        host=settings.host,
        port=settings.port,
        streamable_http_path="/",
        json_response=True,
        stateless_http=True,
    )

    register_tools(mcp, catalog=catalog)

    return mcp


def run_stdio(settings: Settings | None = None) -> None:
    """Run MCP over stdio — transport for local IDE integration."""
    create_server(settings).run(transport="stdio")
