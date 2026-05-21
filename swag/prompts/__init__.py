from mcp.server.fastmcp import FastMCP

from swag.prompts.stub import register_stub_prompt


def register_prompts(mcp: FastMCP) -> None:
    register_stub_prompt(mcp)
