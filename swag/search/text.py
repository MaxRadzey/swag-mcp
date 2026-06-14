import re

_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")

STOP_WORDS = {
    "a",
    "an",
    "and",
    "api",
    "by",
    "for",
    "in",
    "new",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def split_identifier(value: str) -> str:
    """Split common API identifiers before tokenization."""
    return _CAMEL_BOUNDARY_RE.sub(" ", value).replace("_", " ").replace("-", " ")


def tokenize_text(value: str) -> list[str]:
    """Normalize text into lowercase search tokens."""
    split_value = split_identifier(value)
    normalized = _NON_WORD_RE.sub(" ", split_value.lower())
    return [_normalize_token(token) for token in normalized.split() if token and token not in STOP_WORDS]


def normalize_text(value: str) -> str:
    """Return a stable normalized string for fuzzy matching and indexing."""
    return " ".join(tokenize_text(value))


def join_search_text(*values: str | None) -> str:
    """Normalize and concatenate multiple search fields."""
    tokens: list[str] = []
    for value in values:
        if value:
            tokens.extend(tokenize_text(value))
    return " ".join(tokens)


def _normalize_token(token: str) -> str:
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token
