from fastapi.testclient import TestClient


def test_mcp_mount_is_reachable(client: TestClient) -> None:
    response = client.get("/mcp")
    assert response.status_code != 404


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "swag"}
