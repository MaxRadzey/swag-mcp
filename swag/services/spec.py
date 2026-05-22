import time
from dataclasses import dataclass

import httpx

from swag.adapters.spec_http import fetch_spec_body
from swag.adapters.spec_json import decode_spec_json
from swag.exceptions import ServiceNotFoundError
from swag.models.api_spec import ApiSpecDocument
from swag.services.catalog import CatalogService
from swag.validation.api_spec import parse_api_spec_json

DEFAULT_SPEC_TTL_SECONDS = 1800


@dataclass
class _CacheEntry:
    document: ApiSpecDocument
    cached_at: float


class SpecService:
    """Fetch, parse, and cache OpenAPI/Swagger specs by catalog service id."""

    def __init__(
        self,
        catalog: CatalogService,
        client: httpx.Client,
        *,
        ttl_seconds: int = DEFAULT_SPEC_TTL_SECONDS,
    ) -> None:
        self._catalog = catalog
        self._client = client

        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, _CacheEntry] = {}

    def get(self, service_id: str) -> ApiSpecDocument:
        """Return spec for service id (cached, refreshed on TTL expiry)."""
        return self._ensure_fresh(service_id)

    def load(self) -> dict[str, ApiSpecDocument]:
        """Return all currently cached specs keyed by service id."""
        return {service_id: entry.document for service_id, entry in self._cache.items()}

    def reload(self, service_id: str | None = None) -> None:
        """Drop cache for one id or all ids."""
        if service_id is None:
            self._cache.clear()
            return
        self._cache.pop(service_id, None)

    def _is_cache_valid(self, entry: _CacheEntry) -> bool:
        return time.monotonic() - entry.cached_at < self._ttl_seconds

    def _ensure_fresh(self, service_id: str) -> ApiSpecDocument:
        entry = self._cache.get(service_id)
        if entry is not None and self._is_cache_valid(entry):
            return entry.document

        catalog_entry = self._catalog.load().get(service_id)
        if catalog_entry is None:
            msg = f"service not found in catalog: {service_id}"
            raise ServiceNotFoundError(msg)

        body = fetch_spec_body(self._client, str(catalog_entry.spec_url))
        raw = decode_spec_json(body)
        document = parse_api_spec_json(raw)
        self._cache[service_id] = _CacheEntry(document=document, cached_at=time.monotonic())
        return document
