import time
from pathlib import Path

from swag.catalog.models import Catalog, ServiceEntry, ServiceSummary
from swag.catalog.source import read_catalog_file

DEFAULT_CATALOG_TTL_SECONDS = 600


class CatalogService:
    """Load and cache catalog entries from a catalog JSON file."""

    def __init__(self, path: Path, *, ttl_seconds: int = DEFAULT_CATALOG_TTL_SECONDS) -> None:
        self._path = path
        self._ttl_seconds = ttl_seconds
        self._cached_at: float | None = None
        self._cached_dict: dict[str, ServiceEntry] | None = None

    def load(self) -> dict[str, ServiceEntry]:
        """Return services indexed by id (cached, refreshed on TTL expiry)."""
        self._ensure_fresh()
        return self._require_cached_dict()

    def load_list(self) -> list[ServiceEntry]:
        """Return services in catalog file order (derived from the id index)."""
        return list(self.load().values())

    def list_public(self) -> list[ServiceSummary]:
        """Return agent-visible metadata only (no spec URLs or OpenAPI bodies)."""
        return [
            ServiceSummary(id=entry.id, name=entry.name, description=entry.description)
            for entry in self.load_list()
        ]

    def _is_cache_valid(self) -> bool:
        if self._cached_at is None or self._cached_dict is None:
            return False
        return time.monotonic() - self._cached_at < self._ttl_seconds

    def _ensure_fresh(self) -> None:
        if not self._is_cache_valid():
            self._refresh()

    def _refresh(self) -> None:
        raw = read_catalog_file(self._path)
        catalog = Catalog.model_validate(raw)
        self._cached_dict = {entry.id: entry for entry in catalog.services}
        self._cached_at = time.monotonic()

    def _require_cached_dict(self) -> dict[str, ServiceEntry]:
        if self._cached_dict is None:
            msg = "catalog dict cache is empty after refresh"
            raise RuntimeError(msg)
        return self._cached_dict
