"""Pydantic schemas for roaster API."""
from pydantic import BaseModel, Field, field_validator


class RoasterCreate(BaseModel):
    """Schema for creating a roaster."""
    name: str = Field(min_length=1, max_length=200)
    website: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=200)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("website must start with http:// or https://")
        return v


class RoasterSearchParams(BaseModel):
    """Schema for roaster search parameters."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)