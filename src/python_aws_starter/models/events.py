"""Models for historical and geographical events."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution
from .claims_utils import Property, extract_time_from_claim, extract_entity_id_from_claim, extract_coordinate_from_claim


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
    """Represents a historical or geographical event.
    
    Supports both traditional flat fields and Wikidata-style claims.
    When claims are present, computed properties read from claims.
    """

    title: str = Field(..., description="Title of the event (or use labels from claims)")
    description: str = Field(..., description="Detailed description - computed from claims if available")
    start_date: DateRange = Field(..., description="When the event started - computed from claims if available")
    end_date: Optional[DateRange] = Field(None, description="When the event ended - computed from claims if available")
    locations: List[GeographicReference] = Field(
        default_factory=list, description="Geographic locations - computed from claims if available"
    )
    related_people: List[PersonReference] = Field(
        default_factory=list, description="People associated with this event - computed from claims if available"
    )
    
    def get_computed_title(self) -> str:
        """Get title from label if available, otherwise use title field."""
        label = self.get_label()
        return label if label else self.title
    
    def get_computed_description(self) -> str:
        """Get description from claims if available."""
        desc = self.get_description()
        return desc if desc else self.description
    
    def get_computed_start_date(self) -> DateRange:
        """Get start date from claims using property synonyms configuration."""
        from python_aws_starter.models.property_synonyms import get_start_date_properties
        
        # Try all start date synonyms in priority order
        for prop_id in get_start_date_properties():
            claim = self.get_best_claim(prop_id)
            if claim:
                date_str = extract_time_from_claim(claim)
                if date_str:
                    return DateRange(start_date=date_str, precision="day" if len(date_str) >= 10 else "year")
        
        return self.start_date
    
    def get_computed_end_date(self) -> Optional[DateRange]:
        """Get end date from claims using property synonyms configuration."""
        from python_aws_starter.models.property_synonyms import get_end_date_properties
        
        # Try all end date synonyms in priority order
        for prop_id in get_end_date_properties():
            claim = self.get_best_claim(prop_id)
            if claim:
                date_str = extract_time_from_claim(claim)
                if date_str:
                    return DateRange(start_date=date_str, end_date=date_str, precision="day" if len(date_str) >= 10 else "year")
        return self.end_date
    
    def get_locations_from_claims(self) -> List[GeographicReference]:
        """Get locations from claims (P276)."""
        location_claims = self.get_claims(Property.LOCATION)
        locations = []
        for claim in location_claims:
            entity_id = extract_entity_id_from_claim(claim)
            if entity_id:
                # TODO: Resolve entity to get name and coordinates
                locations.append(GeographicReference(
                    geography_id=f"geo_{entity_id}",
                    name=entity_id  # Would need entity resolution
                ))
        return locations if locations else self.locations
    
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
