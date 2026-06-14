from swag.search.engine import SearchEngine
from swag.search.index import build_search_index
from swag.search.models import OperationRecord, SearchQuery
from swag.search.text import join_search_text


def _operation(
    operation_id: str,
    method: str,
    path: str,
    summary: str,
    tags: list[str] | None = None,
) -> OperationRecord:
    return OperationRecord(
        id=f"{method}:{path}",
        method=method,
        path=path,
        operation_id=operation_id,
        summary=summary,
        tags=tags or [],
        search_text=join_search_text(method, path, operation_id, summary, " ".join(tags or [])),
    )


def test_method_boost_lifts_matching_method() -> None:
    index = build_search_index(
        [
            _operation("createUser", "POST", "/users", "Create user"),
            _operation("getUsers", "GET", "/users", "Get users"),
        ]
    )
    engine = SearchEngine()

    hits = engine.search(index, SearchQuery(query="user", method="POST"))

    assert hits[0].method == "POST"
    assert hits[1].method == "GET"
    assert hits[0].score > hits[1].score


def test_path_boost_lifts_exact_path_match() -> None:
    index = build_search_index(
        [
            _operation("createUser", "POST", "/users", "Create user"),
            _operation("createAdminUser", "POST", "/admin/users", "Create user"),
        ]
    )
    engine = SearchEngine()

    hits = engine.search(index, SearchQuery(query="create user", path="/users"))

    assert hits[0].path == "/users"
    assert hits[0].score > hits[1].score


def test_tag_boost_lifts_matching_tag() -> None:
    index = build_search_index(
        [
            _operation("loginUser", "POST", "/sessions", "Create session", ["auth"]),
            _operation("createUser", "POST", "/users", "Create user", ["users"]),
        ]
    )
    engine = SearchEngine()

    hits = engine.search(index, SearchQuery(query="create", tag="auth"))

    assert hits[0].operation_id == "loginUser"
    assert hits[0].score > hits[1].score


def test_structural_signal_can_return_hits_without_keyword_match() -> None:
    index = build_search_index([_operation("createUser", "POST", "/users", "Create user")])
    engine = SearchEngine()

    hits = engine.search(index, SearchQuery(query="warehouse", path="/users"))

    assert len(hits) == 1
    assert hits[0].path == "/users"
    assert hits[0].score >= 10.0
