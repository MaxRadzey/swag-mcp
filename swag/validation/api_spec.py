from typing import Any

from swag.exceptions import SpecValidationError
from swag.models.api_spec import ApiSpecDocument, SpecVersion


def _detect_spec_version(data: dict[str, Any]) -> SpecVersion:
    openapi = data.get("openapi")
    if openapi is not None and str(openapi).startswith("3."):
        return "openapi3"
    if data.get("swagger") == "2.0":
        return "swagger2"
    msg = "document root must be OpenAPI 3.x (openapi field) or Swagger 2.0 (swagger: '2.0')"
    raise SpecValidationError(msg)


def parse_api_spec_json(data: dict[str, Any]) -> ApiSpecDocument:
    """Validate spec root and build an ApiSpecDocument from a decoded JSON object."""
    spec_version = _detect_spec_version(data)
    return ApiSpecDocument(spec_version=spec_version, raw=data)
