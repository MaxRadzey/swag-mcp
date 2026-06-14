from swag.search.index import build_search_index
from swag.search.keyword import KeywordRetriever
from swag.search.models import OperationRecord
from swag.search.text import join_search_text


def _operation(
    operation_id: str,
    method: str,
    path: str,
    summary: str,
    description: str = "",
) -> OperationRecord:
    search_text = join_search_text(method, path, operation_id, summary, description)
    return OperationRecord(
        id=f"{method}:{path}",
        method=method,
        path=path,
        operation_id=operation_id,
        summary=summary,
        description=description,
        search_text=search_text,
    )


def test_keyword_retriever_ranks_strong_text_match_first() -> None:
    index = build_search_index(
        [
            _operation("createUser", "POST", "/users", "Create user"),
            _operation("listUsers", "GET", "/users", "Get users"),
            _operation("createAccount", "POST", "/accounts", "Create account"),
        ]
    )
    retriever = KeywordRetriever()

    candidates = retriever.retrieve("create user", index)

    assert candidates[0].operation.id == "POST:/users"
    assert {candidate.operation.id for candidate in candidates} == {
        "POST:/users",
        "POST:/accounts",
        "GET:/users",
    }
    assert candidates[0].matched_tokens == {"create", "user"}


def test_keyword_retriever_uses_rare_terms_as_stronger_signal() -> None:
    index = build_search_index(
        [
            _operation("createUser", "POST", "/users", "Create user"),
            _operation("getUser", "GET", "/users/{id}", "Get user"),
            _operation("refundUserOrder", "POST", "/orders/refunds", "Refund user order"),
        ]
    )
    retriever = KeywordRetriever()

    candidates = retriever.retrieve("refund user", index)

    assert candidates[0].operation.id == "POST:/orders/refunds"
    assert candidates[0].score_components["bm25"] > candidates[1].score_components["bm25"]


def test_keyword_retriever_returns_empty_for_unknown_query_terms() -> None:
    index = build_search_index([_operation("createUser", "POST", "/users", "Create user")])
    retriever = KeywordRetriever()

    assert retriever.retrieve("warehouse", index) == []
