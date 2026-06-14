from swag.search.text import join_search_text, normalize_text, split_identifier, tokenize_text


def test_split_identifier_handles_common_api_names() -> None:
    assert split_identifier("createUser") == "create User"
    assert split_identifier("create_user") == "create user"
    assert split_identifier("create-user") == "create user"


def test_tokenize_text_normalizes_paths_and_placeholders() -> None:
    assert tokenize_text("/api/v1/users/{id}") == ["v1", "user", "id"]


def test_tokenize_text_keeps_http_methods() -> None:
    assert tokenize_text("POST create user") == ["post", "create", "user"]


def test_normalize_text_removes_punctuation_and_stop_words() -> None:
    assert normalize_text("Create a new platform user.") == "create platform user"


def test_join_search_text_normalizes_multiple_fields() -> None:
    assert join_search_text("POST", "/users/{id}", "createUser") == "post user id create user"
