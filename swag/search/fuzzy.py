from difflib import SequenceMatcher

from swag.search.index import SearchIndex
from swag.search.keyword import SearchCandidate
from swag.search.text import normalize_text, tokenize_text

DEFAULT_FUZZY_THRESHOLD = 0.62
FUZZY_SCORE_WEIGHT = 2.0


class FuzzyRetriever:
    """Fuzzy retrieval for typos and close operation/path names."""

    def __init__(self, *, threshold: float = DEFAULT_FUZZY_THRESHOLD) -> None:
        self._threshold = threshold

    def retrieve(self, query: str, index: SearchIndex) -> list[SearchCandidate]:
        normalized_query = normalize_text(query)
        if not normalized_query:
            return []

        query_tokens = set(tokenize_text(query))
        candidates: list[SearchCandidate] = []
        for operation in index.operations.values():
            field_values = [
                value
                for value in [
                    operation.operation_id_text,
                    operation.path_text,
                    operation.summary_text,
                    operation.tag_text,
                ]
                if value
            ]
            if not field_values:
                continue
            raw_score = max(
                self._ratio(normalized_query, value)
                for value in field_values
            )
            if raw_score < self._threshold:
                continue
            candidates.append(
                SearchCandidate(
                    operation=operation,
                    score_components={"fuzzy": raw_score * FUZZY_SCORE_WEIGHT},
                    matched_tokens=query_tokens,
                )
            )

        candidates.sort(key=lambda candidate: candidate.score_components["fuzzy"], reverse=True)
        return candidates

    def _ratio(self, left: str, right: str) -> float:
        return SequenceMatcher(None, left, right).ratio()
