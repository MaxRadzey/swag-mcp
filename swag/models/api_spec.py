from typing import Any, Literal

from pydantic import BaseModel

SpecVersion = Literal["openapi3", "swagger2"]


class ApiSpecDocument(BaseModel):
    """Parsed OpenAPI or Swagger 2 document (content only, no fetch metadata)."""

    spec_version: SpecVersion
    raw: dict[str, Any]
