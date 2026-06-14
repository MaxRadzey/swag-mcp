from swag.search.boosters import (
    BusinessRulesBooster,
    FieldWeightBooster,
    MethodBooster,
    PathBooster,
    SearchBooster,
    TagBooster,
)
from swag.search.fuzzy import FuzzyRetriever
from swag.search.index import SearchIndex
from swag.search.keyword import KeywordRetriever, SearchCandidate
from swag.search.models import SearchHit, SearchQuery


class SearchEngine:
    """Ranking pipeline over an already-built SearchIndex."""

    def __init__(
        self,
        keyword_retriever: KeywordRetriever | None = None,
        fuzzy_retriever: FuzzyRetriever | None = None,
        boosters: list[SearchBooster] | None = None,
    ) -> None:
        self._keyword_retriever = keyword_retriever or KeywordRetriever()
        self._fuzzy_retriever = fuzzy_retriever or FuzzyRetriever()
        self._boosters = boosters or [
            MethodBooster(),
            PathBooster(),
            TagBooster(),
            FieldWeightBooster(),
            BusinessRulesBooster(),
        ]

    def search(self, index: SearchIndex, query: SearchQuery) -> list[SearchHit]:
        candidates = self._initial_candidates(index, query)
        for booster in self._boosters:
            booster.apply(candidates, query)
        ranked = sorted(
            candidates.values(),
            key=lambda candidate: (candidate.final_score, candidate.operation.method, candidate.operation.path),
            reverse=True,
        )
        return [self._to_hit(candidate) for candidate in ranked[: query.limit]]

    def _initial_candidates(self, index: SearchIndex, query: SearchQuery) -> dict[str, SearchCandidate]:
        candidates = {
            candidate.operation.id: candidate
            for candidate in self._keyword_retriever.retrieve(query.query, index)
        }
        for fuzzy_candidate in self._fuzzy_retriever.retrieve(query.query, index):
            candidate = candidates.get(fuzzy_candidate.operation.id)
            if candidate is None:
                candidates[fuzzy_candidate.operation.id] = fuzzy_candidate
                continue
            candidate.score_components.update(fuzzy_candidate.score_components)
            candidate.matched_tokens.update(fuzzy_candidate.matched_tokens)
        if not candidates and self._has_structural_signal(query):
            return {
                operation.id: SearchCandidate(operation=operation, score_components={"bm25": 0.0})
                for operation in index.operations.values()
            }
        return candidates

    def _to_hit(self, candidate: SearchCandidate) -> SearchHit:
        return SearchHit(
            path=candidate.operation.path,
            method=candidate.operation.method,
            summary=candidate.operation.summary,
            operation_id=candidate.operation.operation_id,
            tags=candidate.operation.tags,
            score=round(candidate.final_score, 6),
        )

    def _has_structural_signal(self, query: SearchQuery) -> bool:
        return any([query.method, query.path, query.path_prefix, query.tag])
