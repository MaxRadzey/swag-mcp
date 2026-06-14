from typing import Any

_INTERNAL_PREFIX = "#/"


def resolve_refs(node: Any, root: dict[str, Any]) -> Any:
    """Recursively inline local ``$ref`` pointers within a schema node.

    Supports OpenAPI 3 (``#/components/schemas/X``) and Swagger 2
    (``#/definitions/X``) by walking the JSON pointer from ``root``. Cycles are
    broken by leaving an already-expanded ``$ref`` (on the current branch)
    untouched. External refs (not starting with ``#/``) are left as-is.
    """
    return _resolve(node, root, frozenset())


def _resolve(node: Any, root: dict[str, Any], seen: frozenset[str]) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            if not ref.startswith(_INTERNAL_PREFIX) or ref in seen:
                return {"$ref": ref}
            target = _lookup_pointer(ref, root)
            if target is None:
                return {"$ref": ref}
            return _resolve(target, root, seen | {ref})
        return {key: _resolve(value, root, seen) for key, value in node.items()}
    if isinstance(node, list):
        return [_resolve(item, root, seen) for item in node]
    return node


def _lookup_pointer(ref: str, root: dict[str, Any]) -> Any | None:
    current: Any = root
    for raw_token in ref[len(_INTERNAL_PREFIX) :].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            return None
        current = current[token]
    return current
