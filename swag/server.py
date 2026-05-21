from typing import Literal

from mcp.server.fastmcp import FastMCP

from swag.config import Settings
from swag.prompts import register_prompts
from swag.tools import register_tools

Transport = Literal["stdio", "sse", "streamable-http"]


def create_server(settings: Settings | None = None) -> FastMCP:
    settings = settings or Settings()
    mcp = FastMCP(settings.server_name)
    register_tools(mcp)
    register_prompts(mcp)
    return mcp


def run(transport: Transport = "stdio") -> None:
    create_server().run(transport=transport)
