import math
from dataclasses import dataclass, field

from swag.search.index import SearchIndex
from swag.search.models import OperationRecord
from swag.search.text import tokenize_text


@dataclass
class SearchCandidate:
    """Internal mutable score container used by the ranking pipeline."""

    operation: OperationRecord
    score_components: dict[str, float] = field(default_factory=dict)
    matched_tokens: set[str] = field(default_factory=set)

    @property
    def final_score(self) -> float:
        return sum(self.score_components.values())


class KeywordRetriever:
    """BM25 keyword retrieval over a SearchIndex."""

    def __init__(self, *, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b

    def retrieve(self, query: str, index: SearchIndex, *, limit: int | None = None) -> list[SearchCandidate]:
        query_tokens = tokenize_text(query)
        if not query_tokens or index.document_count == 0:
            return []

        candidate_ids: set[str] = set()
        for token in query_tokens:
            candidate_ids.update(index.inverted_index.get(token, set()))

        candidates: list[SearchCandidate] = []
        for operation_id in candidate_ids:
            score = self._score_document(operation_id, query_tokens, index)
            if score <= 0:
                continue
            matched_tokens = {
                token
                for token in query_tokens
                if index.term_frequencies[operation_id].get(token, 0) > 0
            }
            candidates.append(
                SearchCandidate(
                    operation=index.operations[operation_id],
                    score_components={"bm25": score},
                    matched_tokens=matched_tokens,
                )
            )

        candidates.sort(key=lambda candidate: candidate.score_components["bm25"], reverse=True)
        return candidates[:limit] if limit is not None else candidates

    def _score_document(self, operation_id: str, query_tokens: list[str], index: SearchIndex) -> float:
        score = 0.0
        document_length = index.document_lengths[operation_id]
        if document_length == 0:
            return score

        for token in query_tokens:
            term_frequency = index.term_frequencies[operation_id].get(token, 0)
            if term_frequency == 0:
                continue
            document_frequency = index.document_frequency(token)
            inverse_document_frequency = math.log(
                1 + (index.document_count - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            denominator = term_frequency + self._k1 * (
                1 - self._b + self._b * document_length / index.average_document_length
            )
            score += inverse_document_frequency * (term_frequency * (self._k1 + 1)) / denominator

        return score
