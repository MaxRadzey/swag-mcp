from pydantic import BaseModel, Field


class ServiceSummary(BaseModel):
    """Public catalog entry for agents (no spec URL or OpenAPI body)."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
