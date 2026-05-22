from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Transport = Literal["stdio", "http"]


class Settings(BaseSettings):
    """Server configuration (env prefix: SWAG_)."""

    model_config = SettingsConfigDict(env_prefix="SWAG_", extra="ignore")

    server_name: str = "swag"
    transport: Transport = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000
    mcp_mount_path: str = "/mcp"
