import httpx
from mcp.server.fastmcp import FastMCP

from swag.app.gateway import SpecGateway
from swag.app.tools import register_tools
from swag.catalog.service import CatalogService
from swag.config import Settings
from swag.mcp_instructions import SERVER_INSTRUCTIONS
from swag.spec.service import SpecService


def create_server(settings: Settings, *, client: httpx.Client) -> FastMCP:
    catalog = CatalogService(settings.catalog_path)
    spec_service = SpecService(catalog, client)

    spec_search = SpecGateway(spec_service)

    mcp = FastMCP(
        settings.server_name,
        instructions=SERVER_INSTRUCTIONS,
        host=settings.host,
        port=settings.port,
        streamable_http_path="/",
        json_response=True,
        stateless_http=True,
    )

    register_tools(mcp, catalog=catalog, spec_search=spec_search)

    return mcp
