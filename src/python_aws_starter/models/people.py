"""Models for people and figures in history."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution


class PersonReference(BaseModel):
    """Reference to another person (e.g., parent, colleague)."""

    person_id: str = Field(..., description="Reference to Person.id")
    name: str = Field(..., description="Person's name")
    relationship: Optional[str] = Field(None, description="Type of relationship")


class OrganizationReference(BaseModel):
    """Reference to an organization a person is/was part of."""

    organization_id: str = Field(..., description="Organization identifier")
    name: str = Field(..., description="Organization name")
    role: Optional[str] = Field(None, description="Role in the organization")
    start_date: Optional[str] = Field(None, description="When they joined")
    end_date: Optional[str] = Field(None, description="When they left")


class Person(BaseEntity):
    """Represents a historical figure or person."""

    name: str = Field(..., description="Person's name")
    birth_date: Optional[str] = Field(None, description="Birth date (ISO 8601)")
    death_date: Optional[str] = Field(None, description="Death date (ISO 8601)")
    birth_location: Optional[str] = Field(None, description="Where they were born")
    death_location: Optional[str] = Field(None, description="Where they died")
    
    description: str = Field(..., description="Biography or description")
    occupations: List[str] = Field(
        default_factory=list, description="Professions or roles (e.g., 'military leader', 'scientist')"
    )
    nationalities: List[str] = Field(
        default_factory=list, description="Nationalities or ethnic groups"
    )
    
    related_people: List[PersonReference] = Field(
        default_factory=list, description="Related people"
    )
    organizations: List[OrganizationReference] = Field(
        default_factory=list, description="Organizations they were part of"
    )
    
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
                "id": "person_napoleon",
                "name": "Napoleon Bonaparte",
                "birth_date": "1769-08-15",
                "death_date": "1821-05-05",
                "birth_location": "Ajaccio, Corsica",
                "occupations": ["military leader", "emperor"],
                "nationalities": ["French", "Corsican"],
                "confidence": 0.99,
            }
        }
    )
