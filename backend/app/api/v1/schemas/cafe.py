"""Pydantic schemas for cafe API."""
import uuid
from pydantic import BaseModel, Field, field_validator


class CafeCreate(BaseModel):
    """Schema for creating a cafe."""
    name: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    website: str | None = Field(default=None, max_length=500)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("website must start with http:// or https://")
        return v


class CafeSearchParams(BaseModel):
    """Schema for cafe search parameters."""
    roast: str | None = Field(default=None, max_length=50)
    origin: str | None = Field(default=None, max_length=100)
    roaster_id: uuid.UUID | None = None
    name: str | None = Field(default=None, max_length=200)
    q: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class CafeInventoryAdd(BaseModel):
    """Schema for adding bean to cafe inventory."""
    bean_id: uuid.UUID


class NearbySearchParams(BaseModel):
    """Schema for nearby search parameters."""
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius: int = Field(default=5000, ge=100, le=50000)