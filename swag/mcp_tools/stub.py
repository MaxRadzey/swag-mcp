from mcp.server.fastmcp import FastMCP


def register_stub_tool(mcp: FastMCP) -> None:
    @mcp.tool()
    def stub_echo(message: str = "hello") -> str:
        """Stub tool: echoes the message with a prefix."""
        return message
