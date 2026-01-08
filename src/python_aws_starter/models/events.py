"""Models for historical and geographical events."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution


class DateRange(BaseModel):
    """Represents a range of dates with varying precision."""

    start_date: str = Field(..., description="ISO 8601 date or approximate date")
    end_date: Optional[str] = Field(None, description="ISO 8601 date or approximate date")
    precision: str = Field(
        default="day",
        description="Precision level: year, month, day, or era",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "1939-09-01",
                "end_date": "1945-09-02",
                "precision": "day",
            }
        }
    )


class PersonReference(BaseModel):
    """Reference to a person related to this event."""

    person_id: str = Field(..., description="Reference to Person.id")
    name: str = Field(..., description="Person's name")
    role: Optional[str] = Field(None, description="Role in this event")


class GeographicReference(BaseModel):
    """Reference to a geographic location related to this event."""

    geography_id: str = Field(..., description="Reference to Geography.id")
    name: str = Field(..., description="Geographic name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class Event(BaseEntity):
    """Represents a historical or geographical event."""

    title: str = Field(..., description="Title of the event")
    description: str = Field(..., description="Detailed description")
    start_date: DateRange = Field(..., description="When the event started")
    end_date: Optional[DateRange] = Field(None, description="When the event ended")
    locations: List[GeographicReference] = Field(
        default_factory=list, description="Geographic locations associated with event"
    )
    related_people: List[PersonReference] = Field(
        default_factory=list, description="People associated with this event"
    )
    
    # Multi-source tracking
    sources: List[SourceAttribution] = Field(
        default_factory=list, description="Which sources contributed data"
    )
    source_of_truth: Optional[str] = Field(
        None, description="Primary source when conflicts exist"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence level based on sources",
    )
    conflict_notes: Optional[str] = Field(
        None, description="Notes on conflicting data between sources"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "event_wwii_001",
                "title": "World War II",
                "description": "Major global conflict",
                "start_date": {
                    "start_date": "1939-09-01",
                    "end_date": "1945-09-02",
                    "precision": "day",
                },
                "locations": [
                    {
                        "geography_id": "geo_europe",
                        "name": "Europe",
                        "latitude": 54.5260,
                        "longitude": 15.2551,
                    }
                ],
                "sources": [],
                "confidence": 0.95,
            }
        }
    )
