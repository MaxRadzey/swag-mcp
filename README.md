# swag

MCP server (Python, [FastMCP](https://github.com/modelcontextprotocol/python-sdk)).

## Run

```bash
uv run python -m swag
```

## Cursor

Add to MCP settings:

```json
{
  "mcpServers": {
    "swag": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/swag", "run", "python", "-m", "swag"]
    }
  }
}
```

## Tools

| Tool        | Description                          |
| ----------- | ------------------------------------ |
| `stub_echo` | Stub: returns `[stub] {message}`     |

## Prompts

| Prompt       | Description                                      |
| ------------ | ------------------------------------------------ |
| `stub_prompt` | Stub template with optional `topic` argument    |

## Layout

```
swag/
  config.py      # settings
  server.py      # FastMCP app + run
  tools/         # MCP tool handlers (transport)
  prompts/       # MCP prompt handlers (transport)
  services/      # business logic
```
