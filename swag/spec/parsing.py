from typing import Any

HTTP_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace"}


def string_list(value: Any) -> list[str]:
    """Return only the string items of ``value`` when it is a list, else ``[]``."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def optional_str(value: Any) -> str | None:
    """Return ``value`` when it is a non-empty string, else ``None``."""
    return value if isinstance(value, str) and value else None
