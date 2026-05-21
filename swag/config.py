from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server configuration (env prefix: SWAG_)."""

    model_config = SettingsConfigDict(env_prefix="SWAG_", extra="ignore")

    server_name: str = "swag"
