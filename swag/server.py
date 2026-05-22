from mcp.server.fastmcp import FastMCP

from swag.config import Settings
from swag.prompts import register_prompts
from swag.tools import register_tools


def create_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or Settings()
    mcp = FastMCP(
        settings.server_name,
        host=settings.host,
        port=settings.port,
        streamable_http_path="/",
        json_response=True,
        stateless_http=True,
    )
    register_tools(mcp)
    register_prompts(mcp)
    return mcp


def run_stdio(settings: Settings | None = None) -> None:
    """Run MCP over stdio — transport for local IDE integration."""
    create_server(settings).run(transport="stdio")
