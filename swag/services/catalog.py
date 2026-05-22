import time
from pathlib import Path
from typing import Any

from swag.adapters.catalog_file import read_catalog_file
from swag.models.catalog import Catalog
from swag.models.service_entry import ServiceEntry
from swag.models.service_summary import ServiceSummary

DEFAULT_CATALOG_TTL_SECONDS = 600


class CatalogService:
    """Load and cache catalog entries from a catalog JSON file."""

    def __init__(self, path: Path, *, ttl_seconds: int = DEFAULT_CATALOG_TTL_SECONDS) -> None:
        self._path = path
        self._ttl_seconds = ttl_seconds
        self._cached_at: float | None = None
        self._cached_list: list[ServiceEntry] | None = None
        self._cached_dict: dict[str, ServiceEntry] | None = None

    def load(self) -> dict[str, ServiceEntry]:
        """Return services indexed by id (cached, refreshed on TTL expiry)."""
        self._ensure_fresh()
        return self._require_cached_dict()

    def load_list(self) -> list[ServiceEntry]:
        """Return services in catalog file order (same cache as ``load``)."""
        self._ensure_fresh()
        return self._require_cached_list()

    def list_public(self) -> list[ServiceSummary]:
        """Return agent-visible metadata only (no spec URLs or OpenAPI bodies)."""
        return [
            ServiceSummary(id=entry.id, name=entry.name, description=entry.description)
            for entry in self.load_list()
        ]

    def reload(self) -> None:
        """Drop cache and load catalog again."""
        self._invalidate()
        self._ensure_fresh()

    def parse(self, raw: dict[str, Any]) -> Catalog:
        """Validate and parse raw catalog JSON into models."""
        return Catalog.model_validate(raw)

    def index_by_id(self, catalog: Catalog) -> dict[str, ServiceEntry]:
        """Build a map for O(1) lookup by service id."""
        return {entry.id: entry for entry in catalog.services}

    def _is_cache_valid(self) -> bool:
        if self._cached_at is None or self._cached_list is None or self._cached_dict is None:
            return False
        return time.monotonic() - self._cached_at < self._ttl_seconds

    def _ensure_fresh(self) -> None:
        if not self._is_cache_valid():
            self._refresh()

    def _refresh(self) -> None:
        raw = read_catalog_file(self._path)
        catalog = self.parse(raw)
        self._cached_list = catalog.services
        self._cached_dict = self.index_by_id(catalog)
        self._cached_at = time.monotonic()

    def _invalidate(self) -> None:
        self._cached_at = None
        self._cached_list = None
        self._cached_dict = None

    def _require_cached_dict(self) -> dict[str, ServiceEntry]:
        if self._cached_dict is None:
            msg = "catalog dict cache is empty after refresh"
            raise RuntimeError(msg)
        return self._cached_dict

    def _require_cached_list(self) -> list[ServiceEntry]:
        if self._cached_list is None:
            msg = "catalog list cache is empty after refresh"
            raise RuntimeError(msg)
        return self._cached_list
