from typing import Self

from pydantic import BaseModel, Field, HttpUrl, model_validator


class ServiceEntry(BaseModel):
    """One service in the catalog (metadata + link to OpenAPI JSON)."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    spec_url: HttpUrl


class ServiceSummary(BaseModel):
    """Public catalog entry for agents (no spec URL or OpenAPI body)."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class Catalog(BaseModel):
    """Root document: list of services from catalog.json / registry."""

    services: list[ServiceEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_service_ids(self) -> Self:
        ids = [service.id for service in self.services]
        if len(ids) != len(set(ids)):
            msg = "duplicate service id in catalog"
            raise ValueError(msg)
        return self
