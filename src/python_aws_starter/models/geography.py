"""Models for geographic entities and locations."""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution
from .claims_utils import Property, extract_coordinate_from_claim, extract_entity_id_from_claim


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
    """Represents a geographic location or region.
    
    Supports both traditional flat fields and Wikidata-style claims.
    When claims are present, computed properties read from claims.
    """

    name: str = Field(..., description="Current or primary name (or use labels from claims)")
    geography_type: GeographyType = Field(..., description="Type of geographic entity - computed from claims if available")
    alternate_names: List[str] = Field(default_factory=list, description="Alternate or historical names - from aliases if available")
    
    description: str = Field(..., description="Description of the geography - computed from claims if available")
    
    # Current coordinates
    center_coordinate: Optional[Coordinate] = Field(None, description="Center point - computed from claims (P625) if available")
    boundaries: Optional[dict] = Field(None, description="Geographic boundaries (GeoJSON format)")
    
    # Hierarchical relationships
    parent_geography_id: Optional[str] = Field(
        None, description="Parent geography - computed from claims if available"
    )
    child_geographies: List[str] = Field(
        default_factory=list, description="List of child geography IDs"
    )
    
    def get_computed_name(self) -> str:
        """Get name from label if available, otherwise use name field."""
        label = self.get_label()
        return label if label else self.name
    
    def get_computed_description(self) -> str:
        """Get description from claims if available."""
        desc = self.get_description()
        return desc if desc else self.description
    
    def get_computed_center_coordinate(self) -> Optional[Coordinate]:
        """Get coordinates from claims (P625) if available."""
        claim = self.get_best_claim(Property.COORDINATE_LOCATION)
        if claim:
            coords = extract_coordinate_from_claim(claim)
            if coords:
                lat, lon = coords
                return Coordinate(latitude=lat, longitude=lon)
        return self.center_coordinate
    
    def get_computed_alternate_names(self) -> List[str]:
        """Get alternate names from aliases if available."""
        aliases = []
        for lang_aliases in self.aliases.values():
            for alias in lang_aliases:
                if isinstance(alias, dict) and "value" in alias:
                    aliases.append(alias["value"])
        return aliases if aliases else self.alternate_names
    
    def get_geography_type_from_claims(self) -> GeographyType:
        """Get geography type from claims (P31: instance of)."""
        instance_claims = self.get_claims(Property.INSTANCE_OF)
        for claim in instance_claims:
            entity_id = extract_entity_id_from_claim(claim)
            if entity_id:
                # Map common Wikidata types to GeographyType
                if entity_id == "Q6256":  # country
                    return GeographyType.COUNTRY
                elif entity_id in ["Q515", "Q15284"]:  # city, settlement
                    return GeographyType.CITY
                elif entity_id == "Q5107":  # continent
                    return GeographyType.CONTINENT
        return self.geography_type
    
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
