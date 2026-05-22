from typing import Self

from pydantic import BaseModel, Field, model_validator

from swag.models.service_entry import ServiceEntry


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
