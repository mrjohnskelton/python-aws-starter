"""Models for tracking data sources and provenance."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SourceType(str, Enum):
    """Type of data source."""

    CURATED = "curated"
    USER_GENERATED = "user_generated"
    SCRAPED = "scraped"
    API = "api"


class DataSource(BaseModel):
    """Represents a data source for timeline information."""

    id: str = Field(..., description="Unique identifier for the source")
    name: str = Field(..., description="Human-readable name (e.g., Wikipedia, Internal)")
    source_type: SourceType = Field(..., description="Type of data source")
    trust_level: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Trust level from 0.0 (low) to 1.0 (curated)",
    )
    description: Optional[str] = Field(None, description="Description of the source")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    refresh_frequency: Optional[str] = Field(None, description="e.g., 'daily', 'manual'")
    base_url: Optional[str] = Field(None, description="Base URL for API or web sources")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "wikipedia",
                "name": "Wikipedia",
                "source_type": "scraped",
                "trust_level": 0.7,
                "description": "Data scraped from Wikipedia articles",
                "refresh_frequency": "weekly",
            }
        }
    )


class SourceAttribution(BaseModel):
    """Tracks which source contributed which fields to an entity."""

    source_id: str = Field(..., description="Reference to DataSource.id")
    source_name: str = Field(..., description="Human-readable source name")
    trust_level: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Trust level of this specific contribution",
    )
    fields_contributed: List[str] = Field(
        ..., description="List of fields contributed by this source"
    )
    external_id: Optional[str] = Field(
        None, description="ID in external system (e.g., Wikipedia article ID)"
    )
    url: Optional[str] = Field(None, description="Link to original source")
    last_verified: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_id": "wikipedia",
                "source_name": "Wikipedia",
                "trust_level": 0.7,
                "fields_contributed": ["title", "description", "start_date"],
                "external_id": "Q1234567",
                "url": "https://en.wikipedia.org/wiki/Example",
            }
        }
    )
