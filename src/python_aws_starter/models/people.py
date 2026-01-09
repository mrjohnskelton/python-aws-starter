"""Models for people and figures in history."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .base import BaseEntity
from .sources import SourceAttribution
from .claims_utils import Property, extract_time_from_claim, extract_entity_id_from_claim


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
    """Represents a historical figure or person.
    
    Supports both traditional flat fields and Wikidata-style claims.
    When claims are present, computed properties read from claims.
    """

    name: str = Field(..., description="Person's name (or use labels from claims)")
    birth_date: Optional[str] = Field(None, description="Birth date (ISO 8601) - computed from claims if available")
    death_date: Optional[str] = Field(None, description="Death date (ISO 8601) - computed from claims if available")
    birth_location: Optional[str] = Field(None, description="Where they were born - computed from claims if available")
    death_location: Optional[str] = Field(None, description="Where they died - computed from claims if available")
    
    description: str = Field(..., description="Biography or description - computed from claims if available")
    occupations: List[str] = Field(
        default_factory=list, description="Professions or roles - computed from claims if available"
    )
    nationalities: List[str] = Field(
        default_factory=list, description="Nationalities or ethnic groups - computed from claims if available"
    )
    
    def get_computed_name(self) -> str:
        """Get name from label if available, otherwise use name field."""
        label = self.get_label()
        return label if label else self.name
    
    def get_computed_birth_date(self) -> Optional[str]:
        """Get birth date from claims (P569) if available."""
        claim = self.get_best_claim(Property.DATE_OF_BIRTH)
        if claim:
            return extract_time_from_claim(claim)
        return self.birth_date
    
    def get_computed_death_date(self) -> Optional[str]:
        """Get death date from claims (P570) if available."""
        claim = self.get_best_claim(Property.DATE_OF_DEATH)
        if claim:
            return extract_time_from_claim(claim)
        return self.death_date
    
    def get_computed_description(self) -> str:
        """Get description from claims if available."""
        desc = self.get_description()
        return desc if desc else self.description
    
    def get_occupations_from_claims(self) -> List[str]:
        """Get occupations from claims (P106)."""
        occupation_claims = self.get_claims(Property.OCCUPATION)
        # This would need entity resolution - simplified for now
        return self.occupations  # TODO: Implement full entity resolution
    
    def get_nationalities_from_claims(self) -> List[str]:
        """Get nationalities from claims (P27)."""
        nationality_claims = self.get_claims(Property.COUNTRY_OF_CITIZENSHIP)
        # This would need entity resolution - simplified for now
        return self.nationalities  # TODO: Implement full entity resolution
    
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
