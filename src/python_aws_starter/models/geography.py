"""Models for geographic entities and locations."""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution


class GeographyType(str, Enum):
    """Type of geographic entity."""

    CONTINENT = "continent"
    COUNTRY = "country"
    REGION = "region"
    PROVINCE = "province"
    CITY = "city"
    VILLAGE = "village"
    LANDMARK = "landmark"
    WATER_BODY = "water_body"
    MOUNTAIN = "mountain"
    OTHER = "other"


class Coordinate(BaseModel):
    """Geographic coordinate."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    elevation: Optional[float] = Field(None, description="Elevation in meters")


class TemporalGeography(BaseModel):
    """Geographic information that changes over time."""

    period_start: str = Field(..., description="Start date (ISO 8601)")
    period_end: Optional[str] = Field(None, description="End date (ISO 8601)")
    name: str = Field(..., description="Name during this period")
    alternate_names: List[str] = Field(default_factory=list, description="Alternate names")
    ruling_entity: Optional[str] = Field(None, description="Ruling country/empire")
    boundaries: Optional[dict] = Field(None, description="Geographic boundaries/geojson")


class GeographicReference(BaseModel):
    """Simple reference to a geographic location."""

    geography_id: str = Field(..., description="Reference to Geography.id")
    name: str = Field(..., description="Geographic name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class Geography(BaseEntity):
    """Represents a geographic location or region."""

    name: str = Field(..., description="Current or primary name")
    geography_type: GeographyType = Field(..., description="Type of geographic entity")
    alternate_names: List[str] = Field(default_factory=list, description="Alternate or historical names")
    
    description: str = Field(..., description="Description of the geography")
    
    # Current coordinates
    center_coordinate: Optional[Coordinate] = Field(None, description="Center point of the geography")
    boundaries: Optional[dict] = Field(None, description="Geographic boundaries (GeoJSON format)")
    
    # Hierarchical relationships
    parent_geography_id: Optional[str] = Field(
        None, description="Parent geography (e.g., continent for a country)"
    )
    child_geographies: List[str] = Field(
        default_factory=list, description="List of child geography IDs"
    )
    
    # Temporal variations
    temporal_variants: List[TemporalGeography] = Field(
        default_factory=list,
        description="How this geography's name, ruling entity, or boundaries changed over time",
    )
    
    # Climate and geology
    climate: Optional[str] = Field(None, description="Climate classification")
    geology: Optional[str] = Field(None, description="Geological information")
    
    # Multi-source tracking
    sources: List[SourceAttribution] = Field(
        default_factory=list, description="Which sources contributed data"
    )
    source_of_truth: Optional[str] = Field(None, description="Primary source when conflicts exist")
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
                "id": "geo_france",
                "name": "France",
                "geography_type": "country",
                "center_coordinate": {"latitude": 46.2276, "longitude": 2.2137},
                "parent_geography_id": "geo_europe",
                "climate": "temperate",
                "confidence": 0.99,
            }
        }
    )
