from swag.search.engine import SearchEngine
from swag.search.fuzzy import FuzzyRetriever
from swag.search.index import build_search_index
from swag.search.models import OperationRecord, SearchQuery
from swag.search.text import join_search_text, normalize_text


def _operation(operation_id: str, method: str, path: str, summary: str) -> OperationRecord:
    return OperationRecord(
        id=f"{method}:{path}",
        method=method,
        path=path,
        operation_id=operation_id,
        summary=summary,
        path_text=normalize_text(path),
        operation_id_text=normalize_text(operation_id),
        summary_text=normalize_text(summary),
        search_text=join_search_text(method, path, operation_id, summary),
    )


def test_fuzzy_retriever_finds_operation_with_typo() -> None:
    index = build_search_index(
        [
            _operation("createUser", "POST", "/users", "Create user"),
            _operation("deleteOrder", "DELETE", "/orders/{id}", "Delete order"),
        ]
    )
    retriever = FuzzyRetriever()

    candidates = retriever.retrieve("cret usr", index)

    assert candidates[0].operation.id == "POST:/users"
    assert candidates[0].score_components["fuzzy"] > 0


def test_search_engine_unions_fuzzy_candidates_with_keyword_candidates() -> None:
    index = build_search_index([_operation("createUser", "POST", "/users", "Create user")])
    engine = SearchEngine()

    hits = engine.search(index, SearchQuery(query="cret usr"))

    # "cret usr" has no exact token match, so a hit can only come from fuzzy union.
    assert len(hits) == 1
    assert hits[0].operation_id == "createUser"
    assert hits[0].score > 0
