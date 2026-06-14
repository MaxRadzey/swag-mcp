import httpx
import pytest

from swag.exceptions import SpecFetchError
from swag.spec.fetch import fetch_spec_body


def test_fetch_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b'{"openapi": "3.0.0"}')

    client = httpx.Client(transport=httpx.MockTransport(handler))

    body = fetch_spec_body(client, "https://example.com/spec.json")

    assert body == b'{"openapi": "3.0.0"}'
    client.close()


def test_fetch_404_raises() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    with pytest.raises(SpecFetchError):
        fetch_spec_body(client, "https://example.com/missing.json")

    client.close()
