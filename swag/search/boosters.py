from typing import Protocol

from swag.search.keyword import SearchCandidate
from swag.search.models import SearchQuery
from swag.search.text import tokenize_text

METHOD_MATCH_BOOST = 3.0
METHOD_MISMATCH_PENALTY = -0.5
PATH_EXACT_BOOST = 10.0
PATH_PREFIX_BOOST = 4.0
PATH_CONTAINS_BOOST = 2.0
TAG_MATCH_BOOST = 3.0
DEPRECATED_PENALTY = -5.0
INTERNAL_PATH_PENALTY = -2.0


class SearchBooster(Protocol):
    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        """Apply score components to candidates."""
        ...


class MethodBooster:
    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        if query.method is None:
            return
        for candidate in candidates.values():
            candidate.score_components["method_boost"] = (
                METHOD_MATCH_BOOST
                if candidate.operation.method == query.method
                else METHOD_MISMATCH_PENALTY
            )


class PathBooster:
    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        if query.path is None and query.path_prefix is None:
            return
        for candidate in candidates.values():
            boost = 0.0
            if query.path is not None:
                boost += self._path_boost(candidate.operation.path, query.path)
            if query.path_prefix is not None and candidate.operation.path.startswith(query.path_prefix):
                boost += PATH_PREFIX_BOOST
            if boost:
                candidate.score_components["path_boost"] = boost

    def _path_boost(self, operation_path: str, query_path: str) -> float:
        if operation_path == query_path:
            return PATH_EXACT_BOOST
        if query_path in operation_path:
            return PATH_CONTAINS_BOOST
        return 0.0


class TagBooster:
    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        query_tokens = set(tokenize_text(query.query))
        requested_tag = query.tag.lower() if query.tag is not None else None
        for candidate in candidates.values():
            tags = {tag.lower() for tag in candidate.operation.tags}
            tag_tokens = set(tokenize_text(" ".join(candidate.operation.tags)))
            if requested_tag is not None and requested_tag in tags:
                candidate.score_components["tag_boost"] = TAG_MATCH_BOOST
            elif query_tokens & tag_tokens:
                candidate.score_components["tag_boost"] = TAG_MATCH_BOOST / 2


class FieldWeightBooster:
    """Boost matches in concise fields more than long descriptions."""

    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        query_tokens = set(tokenize_text(query.query))
        if not query_tokens:
            return
        for candidate in candidates.values():
            boost = 0.0
            boost += self._overlap_boost(query_tokens, candidate.operation.path_text, 0.8)
            boost += self._overlap_boost(query_tokens, candidate.operation.operation_id_text, 0.7)
            boost += self._overlap_boost(query_tokens, candidate.operation.summary_text, 0.5)
            boost += self._overlap_boost(query_tokens, candidate.operation.description_text, 0.15)
            boost += self._overlap_boost(query_tokens, candidate.operation.parameter_text, 0.4)
            if boost:
                candidate.score_components["field_weight_boost"] = boost

    def _overlap_boost(self, query_tokens: set[str], field_text: str, weight: float) -> float:
        if not field_text:
            return 0.0
        return len(query_tokens & set(tokenize_text(field_text))) * weight


class BusinessRulesBooster:
    def apply(self, candidates: dict[str, SearchCandidate], query: SearchQuery) -> None:
        for candidate in candidates.values():
            boost = 0.0
            if candidate.operation.deprecated:
                boost += DEPRECATED_PENALTY
            if "/internal/" in candidate.operation.path or "/debug/" in candidate.operation.path:
                boost += INTERNAL_PATH_PENALTY
            if boost:
                candidate.score_components["business_boost"] = boost
