"""Pydantic schemas for coffee bean API."""
import uuid
from pydantic import BaseModel, Field


class BeanCreate(BaseModel):
    """Schema for creating a coffee bean."""
    name: str = Field(min_length=1, max_length=200)
    roaster_id: uuid.UUID | None = None
    roast_level: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    variety: str | None = Field(default=None, max_length=100)
    processing: str | None = Field(default=None, max_length=50)
    altitude: int | None = Field(default=None, ge=0, le=12000)
    producer: str | None = Field(default=None, max_length=200)
    farm: str | None = Field(default=None, max_length=200)
    region: str | None = Field(default=None, max_length=200)
    tasting_notes: list[str] | None = None
    acidity: int | None = Field(default=None, ge=1, le=5)
    sweetness: int | None = Field(default=None, ge=1, le=5)
    body: int | None = Field(default=None, ge=1, le=5)


class BeanSearchParams(BaseModel):
    """Schema for bean search parameters."""
    roast: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    roaster_id: uuid.UUID | None = None
    variety: str | None = Field(default=None, max_length=100)
    processing: str | None = Field(default=None, max_length=50)
    region: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)