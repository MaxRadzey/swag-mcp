# swag

MCP server (Python, [FastMCP](https://github.com/modelcontextprotocol/python-sdk)).

## Local run

| Mode | When | Who starts the process |
|------|------|------------------------|
| **stdio** (default) | MCP в Cursor через `command` / `args` | **Cursor** сам запускает `python -m swag` |
| **stdio** (manual) | Отладка транспорта без IDE | Вы в терминале |
| **http** | Remote MCP, как на проде, но локально | Вы в терминале или Docker |
| **Docker** | HTTP + healthcheck, ближе к деплою | `docker compose` |

`run_stdio()` в [`swag/server.py`](swag/server.py) — только stdio-режим. На проде не используется.

### stdio + Cursor (основной локальный путь)

`SWAG_TRANSPORT` по умолчанию `stdio`. Сервер **вручную поднимать не нужно** — достаточно прописать MCP в Cursor (см. ниже). IDE запустит процесс при подключении к серверу.

Для отладки в терминале:

```bash
uv run python -m swag
# то же: uv run swag
```

Процесс ждёт JSON-RPC на stdin; в обычном shell он «висит» без вывода — это нормально.

### HTTP (локально, без Docker)

Как задеплоенный инстанс: FastAPI + MCP на `/mcp`. Сервер нужно **запустить самому**:

```bash
SWAG_TRANSPORT=http uv run python -m swag
```

Проверка:

```bash
curl http://localhost:8000/health
# MCP для Cursor: http://localhost:8000/mcp
```

## Docker (local)

Образ только собирает зависимости; запуск — через `docker-compose.yml` (для прода будет отдельная конфигурация).

```bash
docker compose up --build
```

```bash
curl http://localhost:8000/health
```

## Cursor

### Local stdio

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

### Remote HTTP (Docker or `SWAG_TRANSPORT=http`)

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

| Tool        | Description                          |
| ----------- | ------------------------------------ |
| `stub_echo` | Stub: returns `[stub] {message}`     |

## Prompts

| Prompt       | Description                                      |
| ------------ | ------------------------------------------------ |
| `stub_prompt` | Stub template with optional `topic` argument    |

## Configuration

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `SWAG_TRANSPORT` | `stdio` | `stdio` or `http` |
| `SWAG_HOST` | `0.0.0.0` | HTTP bind host |
| `SWAG_PORT` | `8000` | HTTP port |
| `SWAG_MCP_MOUNT_PATH` | `/mcp` | MCP Streamable HTTP mount path |

## Layout

```
swag/
  config.py      # settings
  server.py      # FastMCP factory + stdio run
  http/          # FastAPI app, health, MCP mount
  tools/         # MCP tool handlers (transport)
  prompts/       # MCP prompt handlers (transport)
  services/      # business logic
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
