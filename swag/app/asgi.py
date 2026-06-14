from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import APIRouter, FastAPI

from swag.app.server import create_server
from swag.config import Settings

router = APIRouter(tags=["ops"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "swag"}


def create_app() -> FastAPI:
    settings = Settings()
    client = httpx.Client(timeout=settings.spec_fetch_timeout)

    mcp = create_server(settings, client=client)
    mcp_asgi = mcp.streamable_http_app()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        async with mcp.session_manager.run():
            yield
        client.close()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    app.mount(settings.mcp_mount_path, mcp_asgi)
    return app


app = create_app()
