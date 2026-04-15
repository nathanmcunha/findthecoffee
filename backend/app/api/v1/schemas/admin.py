"""Pydantic schemas for admin API."""
from pydantic import BaseModel, Field


class CurationUpdate(BaseModel):
    """Schema for updating curation fields on a venue.

    All fields optional — partial updates supported.
    """
    is_curator_pick: bool | None = None
    source_attribution: str | None = Field(default=None, max_length=500)


class CurationResponse(BaseModel):
    """Schema for curation update response."""
    status: str
    id: str
    is_curator_pick: bool
    source_attribution: str | None