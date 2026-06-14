import httpx

from swag.exceptions import SpecFetchError


def fetch_spec_body(client: httpx.Client, url: str) -> bytes:
    """GET spec document bytes from URL."""
    try:
        response = client.get(url)
    except httpx.HTTPError as exc:
        msg = f"failed to fetch spec from {url}"
        raise SpecFetchError(msg) from exc
    if response.status_code >= 400:
        msg = f"spec fetch failed with status {response.status_code} for {url}"
        raise SpecFetchError(msg)
    return response.content
