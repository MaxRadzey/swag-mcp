from swag.search.extractors import extract_operations
from swag.spec.models import ApiSpecDocument


def test_extracts_openapi3_operations() -> None:
    document = ApiSpecDocument(
        spec_version="openapi3",
        raw={
            "openapi": "3.0.0",
            "info": {"title": "Users", "version": "1.0.0"},
            "paths": {
                "/users/{id}": {
                    "parameters": [{"name": "id", "in": "path"}],
                    "get": {
                        "operationId": "getUser",
                        "summary": "Get user",
                        "description": "Returns platform user by id",
                        "tags": ["users"],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"},
                                    },
                                },
                            },
                        },
                    },
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                        "tags": ["users"],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CreateUserRequest"},
                                },
                            },
                        },
                        "responses": {},
                    },
                },
            },
        },
    )

    operations = extract_operations(document)

    assert [operation.id for operation in operations] == ["GET:/users/{id}", "POST:/users/{id}"]
    get_user = operations[0]
    assert get_user.method == "GET"
    assert get_user.path == "/users/{id}"
    assert get_user.operation_id == "getUser"
    assert get_user.parameters == ["id path"]
    assert get_user.response_refs == ["#/components/schemas/User"]
    assert "user id" in get_user.path_text
    assert "get user" in get_user.operation_id_text
    assert "platform user id" in get_user.search_text

    create_user = operations[1]
    assert create_user.request_refs == ["#/components/schemas/CreateUserRequest"]


def test_extracts_swagger2_operations() -> None:
    document = ApiSpecDocument(
        spec_version="swagger2",
        raw={
            "swagger": "2.0",
            "info": {"title": "Users", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                        "tags": ["users"],
                        "deprecated": True,
                        "parameters": [
                            {
                                "name": "body",
                                "in": "body",
                                "schema": {"$ref": "#/definitions/CreateUserRequest"},
                            },
                        ],
                        "responses": {
                            "201": {"schema": {"$ref": "#/definitions/User"}},
                        },
                    },
                },
            },
        },
    )

    operations = extract_operations(document)

    assert len(operations) == 1
    operation = operations[0]
    assert operation.id == "POST:/users"
    assert operation.deprecated is True
    assert operation.parameters == ["body body"]
    assert operation.request_refs == ["#/definitions/CreateUserRequest"]
    assert operation.response_refs == ["#/definitions/User"]
