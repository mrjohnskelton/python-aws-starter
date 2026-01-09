"""Base model class for all entities."""

from datetime import datetime, timezone
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, ConfigDict
from .wikidata_meta import Claim, EntityLabels, EntityDescriptions


class BaseEntity(BaseModel):
    """Base entity model with common fields for all domain models.
    
    Now includes Wikidata-style claims structure for flexible property-value storage.
    """

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: str = Field(..., description="User or system that created this entity")
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    last_modified_by: str = Field(..., description="User or system that last modified this entity")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")
    
    # Wikidata-style claims structure
    claims: Dict[str, List[Claim]] = Field(
        default_factory=dict,
        description="Claims by property ID (Wikidata-style: property -> list of claims)"
    )
    labels: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Labels by language code (e.g., {'en': {'language': 'en', 'value': 'Napoleon'}})"
    )
    descriptions: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Descriptions by language code"
    )
    aliases: Dict[str, List[Dict[str, str]]] = Field(
        default_factory=dict,
        description="Aliases by language code"
    )
    
    def get_label(self, lang: str = "en") -> str:
        """Get label in specified language."""
        label_data = self.labels.get(lang, {})
        return label_data.get("value", "")
    
    def get_description(self, lang: str = "en") -> str:
        """Get description in specified language."""
        desc_data = self.descriptions.get(lang, {})
        return desc_data.get("value", "")
    
    def get_claims(self, property_id: str) -> List[Claim]:
        """Get all claims for a property."""
        return self.claims.get(property_id, [])
    
    def get_best_claim(self, property_id: str) -> Optional[Claim]:
        """Get the best (preferred or first normal) claim for a property."""
        claims = self.get_claims(property_id)
        if not claims:
            return None
        
        # Prefer preferred rank
        for claim in claims:
            if claim.rank == "preferred":
                return claim
        
        # Fall back to first normal rank
        for claim in claims:
            if claim.rank == "normal":
                return claim
        
        # Last resort: return first claim
        return claims[0] if claims else None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "entity_001",
                "created_at": "2026-01-08T10:00:00Z",
                "created_by": "system",
                "last_modified_at": "2026-01-08T10:00:00Z",
                "last_modified_by": "system",
            }
        }
    )
