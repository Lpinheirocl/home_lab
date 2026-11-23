from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResourceReference(BaseModel):
    resource_type: str = Field(min_length=1, max_length=40)
    resource_name: str = Field(min_length=1, max_length=253)
    namespace: str = Field(min_length=1, max_length=120)


class ApplicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    icon: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=80)
    namespace: str | None = Field(default=None, max_length=120)
    access_url: str | None = Field(default=None, max_length=500)
    favorite: bool = False
    visible: bool = True


class ApplicationCreate(ApplicationBase):
    discovery_source: str = Field(default="manual", max_length=40)
    resources: list[ResourceReference] = Field(default_factory=list, max_length=50)


class ApplicationUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    icon: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=80)
    namespace: str | None = Field(default=None, max_length=120)
    access_url: str | None = Field(default=None, max_length=500)
    favorite: bool | None = None
    visible: bool | None = None


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    discovery_source: str
    created_at: datetime
    updated_at: datetime
