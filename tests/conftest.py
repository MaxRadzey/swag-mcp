from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from swag.app.asgi import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def fixture_catalog_path() -> Path:
    return Path(__file__).parent / "fixtures" / "catalog.json"
