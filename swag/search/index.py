from collections import Counter, defaultdict
from dataclasses import dataclass

from swag.search.models import OperationRecord
from swag.search.text import tokenize_text


@dataclass(frozen=True)
class SearchIndex:
    """In-memory inverted index for operation search."""

    operations: dict[str, OperationRecord]
    term_frequencies: dict[str, Counter[str]]
    inverted_index: dict[str, set[str]]
    document_lengths: dict[str, int]
    average_document_length: float

    @property
    def document_count(self) -> int:
        return len(self.operations)

    def document_frequency(self, token: str) -> int:
        return len(self.inverted_index.get(token, set()))


def build_search_index(operations: list[OperationRecord]) -> SearchIndex:
    """Build an inverted index from searchable operation records."""
    operation_by_id = {operation.id: operation for operation in operations}
    term_frequencies: dict[str, Counter[str]] = {}
    inverted_index: dict[str, set[str]] = defaultdict(set)
    document_lengths: dict[str, int] = {}

    for operation in operations:
        tokens = tokenize_text(operation.search_text)
        term_frequency = Counter(tokens)
        term_frequencies[operation.id] = term_frequency
        document_lengths[operation.id] = len(tokens)
        for token in term_frequency:
            inverted_index[token].add(operation.id)

    average_document_length = (
        sum(document_lengths.values()) / len(document_lengths) if document_lengths else 0.0
    )

    return SearchIndex(
        operations=operation_by_id,
        term_frequencies=term_frequencies,
        inverted_index=dict(inverted_index),
        document_lengths=document_lengths,
        average_document_length=average_document_length,
    )
