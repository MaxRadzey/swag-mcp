# swag

MCP server (Python, [FastMCP](https://github.com/modelcontextprotocol/python-sdk)).

## Run

The only runtime mode is an HTTP server: FastAPI + MCP on `/mcp` and `GET /health`. Locally it runs via Docker; in production the same image runs (`uv run uvicorn swag.app.asgi:app`).

### Local (Docker)

```bash
docker compose up --build
```

Compose mounts `./swag` into the container and runs uvicorn with `--reload`, so code changes are picked up without rebuilding the image.

Check:

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"swag"}
# MCP for Cursor: http://localhost:8000/mcp
```

## Cursor

Connect to the running server over HTTP:

```json
{
  "mcpServers": {
    "swag": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Tools

| Tool | Description |
| ---- | ----------- |
| `list_services` | Returns `id`, `name`, `description` for each registered API (no OpenAPI bodies or spec URLs) |
| `search_spec` | Searches a selected service spec and returns compact ranked operation hits (`method`, `path`, `summary`, `score`) |
| `get_operation` | Returns one operation's full contract for a chosen `method`+`path`: parameters, request body, and responses, with local `$ref` schemas resolved inline |

On MCP `initialize`, the server sends **instructions** telling the agent to call `list_services` first, pick a `service_id` from `name`/`description`, then `search_spec` with the user's action/entity query and any clear method/path/tag hints, and finally `get_operation` on the chosen hit to fetch the details needed to build a request.

`search_spec` does not return the full OpenAPI document. It builds an in-memory search index from the selected spec (JSON or YAML) and returns top operation candidates; `get_operation` then returns the self-contained contract of a single operation. The server never calls the target API itself.

## Configuration

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `SWAG_HOST` | `0.0.0.0` | HTTP bind host |
| `SWAG_PORT` | `8000` | HTTP port |
| `SWAG_MCP_MOUNT_PATH` | `/mcp` | MCP Streamable HTTP mount path |
| `SWAG_CATALOG_PATH` | `data/catalog.json` | Path to the services catalog JSON |
| `SWAG_SPEC_FETCH_TIMEOUT` | `15.0` | HTTP timeout (seconds) for fetching a spec document |

## Layout

The code is organized into vertical feature packages: each package is
self-contained (its own `models` / `service` / `tool`).

```
swag/
  config.py             # settings
  exceptions.py         # SwagError hierarchy
  mcp_instructions.py   # server instructions for agents
  catalog/              # services registry (list_services): models, source, service, tool
  spec/                 # raw OpenAPI/Swagger document: models, fetch, decode, validate, parsing, service
  search/               # search index + ranking (search_spec): models, text, extractors,
                        #   index, keyword, fuzzy, boosters, engine, tool
  operation/            # full contract of a single operation (get_operation): models, detail, ref_resolver, tool
  app/                  # composition root: gateway (orchestrator), tools, server (FastMCP), asgi (FastAPI)
data/
  catalog.json          # production catalog (URLs only)
```

## Development

Install dev dependencies and pre-commit hooks (runs ruff + mypy from `pyproject.toml` before each commit):

```bash
uv sync --group dev
task pre-commit-install
# or: uv run pre-commit install
```

| Task | Description |
| ---- | ----------- |
| `task test` | Run pytest |
| `task up` | `docker compose up --build` |
| `task down` | `docker compose down` |
| `task ruff` | Ruff check (no auto-fix) |
| `task ruff-fix` | Ruff check with `--fix` |
| `task mypy` | Mypy type check |
| `task check` | Ruff + mypy |
| `task pre-commit-install` | Install git hooks |

Run all hooks manually:

```bash
uv run pre-commit run --all-files
```

Requires [go-task](https://taskfile.dev): `brew install go-task` (or see project docs).

## Tests

```bash
uv run pytest
# or: task test
```
