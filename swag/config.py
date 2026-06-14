from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


class Settings(BaseSettings):
    """Server configuration (env prefix: SWAG_)."""

    model_config = SettingsConfigDict(env_prefix="SWAG_", extra="ignore")

    server_name: str = "swag"
    host: str = "0.0.0.0"
    port: int = 8000
    mcp_mount_path: str = "/mcp"
    catalog_path: Path = _DEFAULT_CATALOG_PATH
    spec_fetch_timeout: float = 15.0
