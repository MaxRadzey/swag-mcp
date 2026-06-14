from swag.operation.detail import extract_operation_detail
from swag.spec.models import ApiSpecDocument


def _openapi3_document() -> ApiSpecDocument:
    return ApiSpecDocument(
        spec_version="openapi3",
        raw={
            "openapi": "3.0.0",
            "paths": {
                "/pets/{petId}": {
                    "parameters": [
                        {"name": "petId", "in": "path", "required": True, "schema": {"type": "integer"}},
                    ],
                    "put": {
                        "operationId": "updatePet",
                        "summary": "Update a pet",
                        "tags": ["pets"],
                        "parameters": [
                            {"name": "verbose", "in": "query", "schema": {"type": "boolean"}},
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/Pet"}},
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "ok",
                                "content": {
                                    "application/json": {"schema": {"$ref": "#/components/schemas/Pet"}},
                                },
                            },
                            "404": {"description": "missing"},
                        },
                    },
                },
            },
            "components": {
                "schemas": {
                    "Pet": {"type": "object", "properties": {"name": {"type": "string"}}},
                },
            },
        },
    )


def test_openapi3_operation_detail() -> None:
    detail = extract_operation_detail(_openapi3_document(), "petstore", "PUT", "/pets/{petId}")

    assert detail is not None
    assert detail.service_id == "petstore"
    assert detail.method == "PUT"
    assert detail.operation_id == "updatePet"
    assert {(p.name, p.location, p.required) for p in detail.parameters} == {
        ("petId", "path", True),
        ("verbose", "query", False),
    }
    assert detail.request_body is not None
    assert detail.request_body.required is True
    # $ref to Pet is resolved inline.
    assert detail.request_body.content[0].json_schema == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }
    responses = {r.status_code: r for r in detail.responses}
    assert responses["200"].content[0].json_schema == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }
    assert responses["404"].content == []


def test_swagger2_operation_detail() -> None:
    document = ApiSpecDocument(
        spec_version="swagger2",
        raw={
            "swagger": "2.0",
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "parameters": [
                            {"name": "limit", "in": "query", "type": "integer"},
                            {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/User"}},
                        ],
                        "responses": {
                            "201": {"description": "created", "schema": {"$ref": "#/definitions/User"}},
                        },
                    },
                },
            },
            "definitions": {"User": {"type": "object", "properties": {"id": {"type": "integer"}}}},
        },
    )

    detail = extract_operation_detail(document, "users", "post", "/users")

    assert detail is not None
    # body parameter becomes the request body, not a plain parameter.
    assert [p.name for p in detail.parameters] == ["limit"]
    assert detail.parameters[0].json_schema == {"type": "integer"}
    assert detail.request_body is not None
    assert detail.request_body.required is True
    assert detail.request_body.content[0].json_schema == {
        "type": "object",
        "properties": {"id": {"type": "integer"}},
    }
    assert detail.responses[0].content[0].json_schema == {
        "type": "object",
        "properties": {"id": {"type": "integer"}},
    }


def test_operation_level_parameter_overrides_path_level() -> None:
    document = ApiSpecDocument(
        spec_version="openapi3",
        raw={
            "openapi": "3.0.0",
            "paths": {
                "/items": {
                    "parameters": [{"name": "scope", "in": "query", "schema": {"type": "string"}, "required": False}],
                    "get": {
                        "parameters": [
                            {"name": "scope", "in": "query", "schema": {"type": "string"}, "required": True},
                        ],
                        "responses": {},
                    },
                },
            },
        },
    )

    detail = extract_operation_detail(document, "svc", "GET", "/items")

    assert detail is not None
    assert len(detail.parameters) == 1
    assert detail.parameters[0].required is True


def test_returns_none_for_missing_operation() -> None:
    document = _openapi3_document()

    assert extract_operation_detail(document, "petstore", "DELETE", "/pets/{petId}") is None
    assert extract_operation_detail(document, "petstore", "PUT", "/nope") is None
    assert extract_operation_detail(document, "petstore", "FETCH", "/pets/{petId}") is None
