from dataclasses import dataclass

from swag.exceptions import OperationNotFoundError
from swag.operation.detail import extract_operation_detail
from swag.operation.models import OperationDetail
from swag.search.engine import SearchEngine
from swag.search.extractors import extract_operations
from swag.search.index import SearchIndex, build_search_index
from swag.search.models import SearchQuery, SearchResponse
from swag.spec.models import ApiSpecDocument
from swag.spec.service import SpecService


@dataclass
class _IndexCacheEntry:
    document_identity: int
    index: SearchIndex


class SpecGateway:
    """Search operation indexes built from service OpenAPI/Swagger specs."""

    def __init__(self, spec_service: SpecService, search_engine: SearchEngine | None = None) -> None:
        self._spec_service = spec_service
        self._search_engine = search_engine or SearchEngine()
        self._index_cache: dict[str, _IndexCacheEntry] = {}

    async def search(self, service_id: str, query: SearchQuery) -> SearchResponse:
        document = await self._spec_service.get(service_id)
        index = self._index_for(service_id, document)
        hits = self._search_engine.search(index, query)
        return SearchResponse(
            service_id=service_id,
            query=query,
            hits=hits,
            total_candidates=index.document_count,
        )

    async def get_operation(self, service_id: str, method: str, path: str) -> OperationDetail:
        """Return the full contract of one operation (resolved ``$ref``)."""
        document = await self._spec_service.get(service_id)
        detail = extract_operation_detail(document, service_id, method, path)
        if detail is None:
            msg = f"operation not found: {method.upper()} {path} in service {service_id!r}"
            raise OperationNotFoundError(msg)
        return detail

    def _index_for(self, service_id: str, document: ApiSpecDocument) -> SearchIndex:
        cached = self._index_cache.get(service_id)
        if cached is not None and cached.document_identity == id(document):
            return cached.index

        operations = extract_operations(document)
        index = build_search_index(operations)
        self._index_cache[service_id] = _IndexCacheEntry(document_identity=id(document), index=index)
        return index
