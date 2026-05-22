from pydantic import BaseModel, Field, HttpUrl


class ServiceEntry(BaseModel):
    """One service in the catalog (metadata + link to OpenAPI JSON)."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    spec_url: HttpUrl
