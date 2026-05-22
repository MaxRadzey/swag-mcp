from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Transport = Literal["stdio", "http"]

_DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


class Settings(BaseSettings):
    """Server configuration (env prefix: SWAG_)."""

    model_config = SettingsConfigDict(env_prefix="SWAG_", extra="ignore")

    server_name: str = "swag"
    transport: Transport = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000
    mcp_mount_path: str = "/mcp"
    catalog_path: Path = _DEFAULT_CATALOG_PATH
