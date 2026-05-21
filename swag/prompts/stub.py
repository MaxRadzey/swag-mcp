from mcp.server.fastmcp import FastMCP

from swag.services.prompt_stub import build_stub_prompt


def register_stub_prompt(mcp: FastMCP) -> None:
    @mcp.prompt()
    def stub_prompt(topic: str = "general") -> str:
        """Stub prompt template."""
        return build_stub_prompt(topic)
