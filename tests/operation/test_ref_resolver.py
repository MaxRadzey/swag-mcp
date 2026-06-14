from swag.operation.ref_resolver import resolve_refs


def test_resolves_nested_openapi3_ref() -> None:
    root = {
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {"category": {"$ref": "#/components/schemas/Category"}},
                },
                "Category": {"type": "object", "properties": {"name": {"type": "string"}}},
            }
        }
    }

    resolved = resolve_refs({"$ref": "#/components/schemas/Pet"}, root)

    assert resolved["properties"]["category"]["properties"]["name"] == {"type": "string"}


def test_resolves_swagger2_definitions_ref() -> None:
    root = {"definitions": {"User": {"type": "object", "properties": {"id": {"type": "integer"}}}}}

    resolved = resolve_refs({"$ref": "#/definitions/User"}, root)

    assert resolved == {"type": "object", "properties": {"id": {"type": "integer"}}}


def test_breaks_self_referential_cycle() -> None:
    root = {
        "components": {
            "schemas": {
                "Node": {
                    "type": "object",
                    "properties": {"next": {"$ref": "#/components/schemas/Node"}},
                }
            }
        }
    }

    resolved = resolve_refs({"$ref": "#/components/schemas/Node"}, root)

    # The recursive child is left as an unexpanded ref instead of looping forever.
    assert resolved["properties"]["next"] == {"$ref": "#/components/schemas/Node"}


def test_keeps_external_ref_untouched() -> None:
    resolved = resolve_refs({"$ref": "common.yaml#/Pet"}, {})

    assert resolved == {"$ref": "common.yaml#/Pet"}


def test_keeps_missing_ref_untouched() -> None:
    resolved = resolve_refs({"$ref": "#/components/schemas/Missing"}, {"components": {"schemas": {}}})

    assert resolved == {"$ref": "#/components/schemas/Missing"}


def test_resolves_inside_lists() -> None:
    root = {"components": {"schemas": {"Tag": {"type": "string"}}}}

    resolved = resolve_refs({"allOf": [{"$ref": "#/components/schemas/Tag"}]}, root)

    assert resolved == {"allOf": [{"type": "string"}]}
