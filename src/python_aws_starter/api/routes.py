"""Main API routes for the timeline application."""

from typing import List, Optional
from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    """Common query parameters for timeline API."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of records to return")
    dimension: Optional[str] = Field(None, description="Filter by dimension")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    search: Optional[str] = Field(None, description="Search query")


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[dict] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    meta: Optional[dict] = Field(None, description="Metadata (pagination, etc.)")


# TODO: Implement route handlers
# - GET /api/v1/events
# - GET /api/v1/events/{id}
# - POST /api/v1/events
# - PUT /api/v1/events/{id}
# - GET /api/v1/people
# - GET /api/v1/people/{id}
# - POST /api/v1/people
# - GET /api/v1/geography
# - GET /api/v1/geography/{id}
# - GET /api/v1/dimensions
# - POST /api/v1/contributions (user submissions)
# - GET /api/v1/contributions (pending reviews)
