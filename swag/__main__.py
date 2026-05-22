import uvicorn

from swag.config import Settings
from swag.server import run_stdio


def main() -> None:
    settings = Settings()
    if settings.transport == "http":
        uvicorn.run(
            "swag.asgi:app",
            host=settings.host,
            port=settings.port,
            factory=False,
        )
    else:
        run_stdio(settings)


if __name__ == "__main__":
    main()
