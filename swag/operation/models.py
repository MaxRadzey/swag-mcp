from typing import Any

from pydantic import BaseModel, Field


class ParameterDetail(BaseModel):
    """One operation parameter with its resolved JSON Schema."""

    name: str
    location: str  # OpenAPI "in": query | path | header | cookie
    required: bool = False
    description: str | None = None
    json_schema: dict[str, Any] | None = None


class MediaTypeSchema(BaseModel):
    """Resolved schema for one request/response content type."""

    content_type: str
    json_schema: dict[str, Any] | None = None


class RequestBodyDetail(BaseModel):
    """Request body contract with resolved schemas per content type."""

    description: str | None = None
    required: bool = False
    content: list[MediaTypeSchema] = Field(default_factory=list)


class ResponseDetail(BaseModel):
    """One response (by status code) with resolved schemas per content type."""

    status_code: str
    description: str | None = None
    content: list[MediaTypeSchema] = Field(default_factory=list)


class OperationDetail(BaseModel):
    """Full contract of one API operation, returned by ``get_operation``."""

    service_id: str
    path: str
    method: str
    operation_id: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    deprecated: bool = False
    parameters: list[ParameterDetail] = Field(default_factory=list)
    request_body: RequestBodyDetail | None = None
    responses: list[ResponseDetail] = Field(default_factory=list)
