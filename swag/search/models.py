from pydantic import BaseModel, Field, field_validator


class OperationRecord(BaseModel):
    """Search-ready representation of one API operation."""

    id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    method: str = Field(min_length=1)
    operation_id: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[str] = Field(default_factory=list)
    request_refs: list[str] = Field(default_factory=list)
    response_refs: list[str] = Field(default_factory=list)
    deprecated: bool = False

    path_text: str = ""
    operation_id_text: str = ""
    summary_text: str = ""
    description_text: str = ""
    tag_text: str = ""
    parameter_text: str = ""
    ref_text: str = ""
    search_text: str = ""


class SearchQuery(BaseModel):
    """Structured search parameters provided by the MCP tool."""

    query: str = ""
    method: str | None = None
    path: str | None = None
    path_prefix: str | None = None
    tag: str | None = None
    limit: int = Field(default=5, ge=1, le=25)

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class SearchHit(BaseModel):
    """Compact ranked operation returned to the LLM."""

    path: str
    method: str
    summary: str | None = None
    operation_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: float


class SearchResponse(BaseModel):
    """Search response for one service specification."""

    service_id: str
    query: SearchQuery
    hits: list[SearchHit]
    total_candidates: int
