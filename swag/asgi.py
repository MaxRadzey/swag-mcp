from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from swag.config import Settings
from swag.server import create_server

router = APIRouter(tags=["ops"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "swag"}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    mcp = create_server(settings)
    mcp_asgi = mcp.streamable_http_app()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        async with mcp.session_manager.run():
            yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    app.mount(settings.mcp_mount_path, mcp_asgi)
    return app


app = create_app()
