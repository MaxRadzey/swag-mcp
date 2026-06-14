from pathlib import Path

import pytest

from swag.config import Settings


def test_defaults() -> None:
    settings = Settings()
    assert settings.mcp_mount_path == "/mcp"
    assert settings.port == 8000
    assert settings.spec_fetch_timeout == 15.0


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWAG_MCP_MOUNT_PATH", "/api/mcp")
    monkeypatch.setenv("SWAG_PORT", "9001")
    monkeypatch.setenv("SWAG_SPEC_FETCH_TIMEOUT", "5")
    monkeypatch.setenv("SWAG_CATALOG_PATH", "/tmp/custom-catalog.json")

    settings = Settings()

    assert settings.mcp_mount_path == "/api/mcp"
    assert settings.port == 9001
    assert settings.spec_fetch_timeout == 5.0
    assert settings.catalog_path == Path("/tmp/custom-catalog.json")
