from mcp.server.fastmcp import FastMCP

from swag.mcp_tools.stub import register_stub_tool


def register_tools(mcp: FastMCP) -> None:
    register_stub_tool(mcp)
