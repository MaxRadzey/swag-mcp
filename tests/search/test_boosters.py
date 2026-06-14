from swag.search.boosters import BusinessRulesBooster, FieldWeightBooster
from swag.search.keyword import SearchCandidate
from swag.search.models import OperationRecord, SearchQuery
from swag.search.text import join_search_text, normalize_text


def _candidate(
    operation_id: str,
    method: str,
    path: str,
    summary: str,
    *,
    description: str = "",
    deprecated: bool = False,
) -> SearchCandidate:
    operation = OperationRecord(
        id=f"{method}:{path}",
        method=method,
        path=path,
        operation_id=operation_id,
        summary=summary,
        description=description,
        deprecated=deprecated,
        path_text=normalize_text(path),
        operation_id_text=normalize_text(operation_id),
        summary_text=normalize_text(summary),
        description_text=normalize_text(description),
        search_text=join_search_text(method, path, operation_id, summary, description),
    )
    return SearchCandidate(operation=operation)


def test_field_weight_booster_rewards_field_overlap() -> None:
    candidate = _candidate("createUser", "POST", "/users", "Create user")
    candidates = {candidate.operation.id: candidate}

    FieldWeightBooster().apply(candidates, SearchQuery(query="create user"))

    assert candidate.score_components["field_weight_boost"] > 0


def test_business_booster_penalizes_deprecated() -> None:
    candidate = _candidate("createLegacyUser", "POST", "/legacy/users", "Create user", deprecated=True)
    candidates = {candidate.operation.id: candidate}

    BusinessRulesBooster().apply(candidates, SearchQuery(query="create user"))

    assert candidate.score_components["business_boost"] < 0


def test_business_booster_penalizes_internal_path() -> None:
    candidate = _candidate("debugUser", "GET", "/debug/users/{id}", "Get user")
    candidates = {candidate.operation.id: candidate}

    BusinessRulesBooster().apply(candidates, SearchQuery(query="get user"))

    assert candidate.score_components["business_boost"] < 0
