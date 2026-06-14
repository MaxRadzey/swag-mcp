# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync --group dev          # install all dependencies including dev
task test                    # run pytest
task check                   # ruff + mypy
task ruff                    # lint only (no fix)
task ruff-fix                # lint with auto-fix
task mypy                    # type-check
task pre-commit-install      # install git hooks (ruff + mypy run before each commit)
uv run pre-commit run --all-files  # run all hooks manually
```

Run a single test file:
```bash
uv run pytest tests/search/test_engine.py
```

Run the server locally (HTTP on :8000, with hot-reload):
```bash
docker compose up --build                # task up / task down
```

## Architecture

The project is an MCP server that lets AI agents search OpenAPI/Swagger specs without receiving the full spec document. The agent first `search_spec`s to find operations, then `get_operation`s to pull one operation's full contract (parameters, request body, responses) so it can build a request itself — the server never calls the target API.

**The code is organized into vertical feature packages** — each is self-contained (its own `models` / `service` / `tool`):
- `swag/catalog/` — the registry of services (`list_services`): `models`, `source` (read catalog.json), `service` (`CatalogService`), `tool`.
- `swag/spec/` — fetch + decode + validate + cache of the **raw** OpenAPI/Swagger document: `models` (`ApiSpecDocument`), `fetch`, `decode`, `validate`, `parsing` (shared spec-reading helpers: `HTTP_METHODS`, `optional_str`, `string_list`), `service` (`SpecService`).
- `swag/search/` — the BM25 search index + ranking (`search_spec`): `models` (`OperationRecord`, `SearchQuery`, `SearchHit`, `SearchResponse`), `text`, `extractors`, `index`, `keyword`, `fuzzy`, `boosters`, `engine`, `tool`.
- `swag/operation/` — one operation's full contract (`get_operation`): `models` (`OperationDetail` + sub-models), `detail`, `ref_resolver`, `tool`.
- `swag/app/` — composition root: `gateway` (`SpecGateway` orchestrator), `tools` (`register_tools`), `server` (FastMCP factory), `asgi` (FastAPI app).
- Shared at the root: `config.py`, `exceptions.py`, `mcp_instructions.py`.

Dependency direction is top-down (no cycles): `app` → `{catalog, search, operation, spec}`; `search`/`operation` → `spec`; `spec/service` → `catalog/service`. The feature `tool.py` modules receive their service via DI (constructed in `app/server.py`), so the only upward import is the `SpecGateway` type annotation in `search/tool.py` and `operation/tool.py`.

**Request flow for `search_spec`:**

```
MCP tool handler (search/tool.py)
  → SpecGateway (app/gateway.py)            # cache + orchestration
    → SpecService (spec/service.py)         # fetch + cache spec document
      → spec/fetch.py + spec/decode.py      # HTTP fetch, then JSON-or-YAML decode
    → extract_operations (search/extractors.py)  # parse OpenAPI paths → OperationRecord list
    → build_search_index (search/index.py)       # build in-memory BM25 inverted index
    → SearchEngine.search (search/engine.py)     # rank and return SearchHit list
```

**Request flow for `get_operation`:**

```
MCP tool handler (operation/tool.py)
  → SpecGateway.get_operation (app/gateway.py)        # reuses cached spec document
    → extract_operation_detail (operation/detail.py)  # pick one method+path
      → resolve_refs (operation/ref_resolver.py)      # inline local $ref (cycle-safe)
    → OperationDetail (operation/models.py)           # full contract DTO
```

**Search pipeline** (`SearchEngine`): combines keyword retrieval (BM25 via `KeywordRetriever`) and fuzzy retrieval (`FuzzyRetriever`) into a unified candidate set, then applies a chain of boosters (`MethodBooster`, `PathBooster`, `TagBooster`, `FieldWeightBooster`, `BusinessRulesBooster`) that mutate `score_components` in-place. Final score is the sum of all components. If no candidates are found but a structural signal (method/path/tag filter) exists, all operations are returned for filtering.

**Catalog** (`data/catalog.json`) is read by `CatalogService` via `catalog/source.py`. It maps `service_id → {name, description, spec_url}`. The spec bodies are fetched on demand (JSON or YAML) and cached by `SpecService` keyed by `service_id`.

**`SpecGateway` double-caches**: the raw spec document (in `SpecService`) and the built `SearchIndex` (keyed by `id()` of the document object — cache invalidates automatically when a new fetch replaces the document).

**Three MCP tools registered at startup** (`app/tools.py`):
- `list_services` — returns catalog summaries (no spec bodies)
- `search_spec` — runs the full search pipeline for one service; returns compact `SearchHit`s
- `get_operation` — returns one operation's full contract with local `$ref` resolved
- Tool handlers wrap domain `SwagError`s in `mcp.server.fastmcp.exceptions.ToolError` so the agent gets a clean message instead of a raw traceback.

**Server** (`swag/app/asgi.py`): `create_app()` mounts the FastMCP app under `SWAG_MCP_MOUNT_PATH` (default `/mcp`) into a FastAPI app that also serves `GET /health`, and exposes the result as `app` for `uvicorn swag.app.asgi:app`. The FastAPI lifespan owns the `httpx.Client` lifecycle (timeout from `SWAG_SPEC_FETCH_TIMEOUT`, closed on shutdown). There is a single transport — HTTP; the server runs as a container both locally (Docker, hot-reload) and in production.

## Key conventions

- **Strict mypy** — all new code must be fully typed; no `Any` leakage beyond adapter boundaries.
- **Ruff rules**: E, F, I (isort), UP, B, SIM; line length 120.
- `OperationRecord` (a pydantic model) carries pre-computed `search_text` (joined, normalized) built once in `search/extractors.py`. Treat it as read-only after construction.
- `SearchCandidate` (in `search/keyword.py`) is the mutable working object during ranking; `SearchHit` is the compact output DTO sent to the agent (no internal `score_components`/`matched_tokens` — only the final `score`).
- Boosters receive `dict[str, SearchCandidate]` and mutate `candidate.score_components` in-place — they do not return a new collection.
- `get_operation` returns resolved JSON Schema as `dict[str, Any]` under the field name `json_schema` (the name `schema` is avoided because it shadows a pydantic `BaseModel` attribute).
