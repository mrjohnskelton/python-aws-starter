"""Models for dimensions that structure the timeline."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity


class DimensionType(str, Enum):
    """Type of dimension for navigation."""

    TIMELINE = "timeline"
    GEOGRAPHY = "geography"
    PEOPLE = "people"
    EVENTS = "events"
    CATEGORY = "category"
    CUSTOM = "custom"


class DimensionField(BaseModel):
    """Describes a field that can be filtered/pivoted on."""

    name: str = Field(..., description="Field name")
    display_name: str = Field(..., description="Human-readable name")
    field_type: str = Field(..., description="Data type: string, date, number, etc.")
    filterable: bool = Field(default=True, description="Can this be filtered?")
    sortable: bool = Field(default=True, description="Can this be sorted?")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional field metadata")


class Dimension(BaseEntity):
    """Represents a dimension for navigating the timeline."""

    name: str = Field(..., description="Name of the dimension")
    dimension_type: DimensionType = Field(..., description="Type of dimension")
    description: str = Field(..., description="Description of the dimension")
    
    icon: Optional[str] = Field(None, description="Icon or emoji for UI representation")
    color: Optional[str] = Field(None, description="Color code for UI representation")
    
    # Fields available in this dimension
    fields: List[DimensionField] = Field(
        default_factory=list, description="Fields that can be accessed in this dimension"
    )
    
    # Related dimensions
    pivot_to_dimensions: List[str] = Field(
        default_factory=list,
        description="List of dimension IDs you can pivot to from this one",
    )
    
    # Zoom capabilities
    supports_zoom: bool = Field(
        default=True, description="Can users zoom in/out on this dimension?"
    )
    zoom_levels: Optional[List[str]] = Field(
        None, description="Available zoom levels (e.g., ['year', 'decade', 'century'] for timeline)"
    )
    
    # Configuration
    is_custom: bool = Field(
        default=False, description="Is this a custom user-defined dimension?"
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None, description="Custom configuration for this dimension"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "dim_timeline",
                "name": "Timeline",
                "dimension_type": "timeline",
                "description": "Navigate historical events by time",
                "icon": "🕐",
                "color": "#FF6B6B",
                "fields": [
                    {
                        "name": "date",
                        "display_name": "Date",
                        "field_type": "date",
                        "filterable": True,
                        "sortable": True,
                    }
                ],
                "pivot_to_dimensions": ["dim_geography", "dim_people"],
                "supports_zoom": True,
                "zoom_levels": ["era", "century", "decade", "year", "month", "day"],
            }
        }
    )
