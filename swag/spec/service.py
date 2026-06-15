import asyncio
import time
from dataclasses import dataclass

import httpx

from swag.catalog.service import CatalogService
from swag.exceptions import ServiceNotFoundError
from swag.spec.decode import decode_spec_body
from swag.spec.fetch import fetch_spec_body
from swag.spec.models import ApiSpecDocument
from swag.spec.validate import parse_api_spec_json

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
        client: httpx.AsyncClient,
        *,
        ttl_seconds: int = DEFAULT_SPEC_TTL_SECONDS,
    ) -> None:
        self._catalog = catalog
        self._client = client

        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, _CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get(self, service_id: str) -> ApiSpecDocument:
        """Return spec for service id (cached, refreshed on TTL expiry)."""
        return await self._ensure_fresh(service_id)

    def _is_cache_valid(self, entry: _CacheEntry) -> bool:
        return time.monotonic() - entry.cached_at < self._ttl_seconds

    def _lock_for(self, service_id: str) -> asyncio.Lock:
        lock = self._locks.get(service_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[service_id] = lock
        return lock

    async def _ensure_fresh(self, service_id: str) -> ApiSpecDocument:
        entry = self._cache.get(service_id)
        if entry is not None and self._is_cache_valid(entry):
            return entry.document

        async with self._lock_for(service_id):
            entry = self._cache.get(service_id)
            if entry is not None and self._is_cache_valid(entry):
                return entry.document

            catalog_entry = self._catalog.load().get(service_id)
            if catalog_entry is None:
                msg = f"service not found in catalog: {service_id}"
                raise ServiceNotFoundError(msg)

            body = await fetch_spec_body(self._client, str(catalog_entry.spec_url))
            raw = decode_spec_body(body)
            document = parse_api_spec_json(raw)
            self._cache[service_id] = _CacheEntry(document=document, cached_at=time.monotonic())
            return document
