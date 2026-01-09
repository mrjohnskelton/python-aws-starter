"""Wikidata meta model - core structures for claims, statements, and datavalues.

This module implements the Wikidata data model structure:
- Claims/Statements: property-value pairs with qualifiers and references
- Snaks: property-value pairs (the core building block)
- Datavalues: typed values (time, quantity, string, entity, etc.)
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class SnakType(str, Enum):
    """Type of snak (property-value pair)."""
    
    VALUE = "value"  # Has a value
    NOVALUE = "novalue"  # Known to have no value
    SOMEVALUE = "somevalue"  # Has some value but unknown


class DatavalueType(str, Enum):
    """Type of datavalue in Wikidata."""
    
    TIME = "time"
    QUANTITY = "quantity"
    STRING = "string"
    MONOLINGUAL_TEXT = "monolingualtext"
    WIKIBASE_ENTITY = "wikibase-entityid"
    GLOBE_COORDINATE = "globecoordinate"
    COMMONS_MEDIA = "commonsMedia"
    URL = "url"
    EXTERNAL_ID = "external-id"


class TimeValue(BaseModel):
    """Wikidata time value."""
    
    time: str = Field(..., description="ISO 8601 time string (e.g., '+1769-08-15T00:00:00Z')")
    timezone: int = Field(default=0, description="Timezone offset in minutes")
    before: int = Field(default=0, description="Before this many units")
    after: int = Field(default=0, description="After this many units")
    precision: int = Field(..., description="Precision: 9=year, 10=month, 11=day, etc.")
    calendarmodel: str = Field(default="http://www.wikidata.org/entity/Q1985727", description="Calendar model URI")


class QuantityValue(BaseModel):
    """Wikidata quantity value."""
    
    amount: str = Field(..., description="Amount as string (e.g., '+123')")
    unit: str = Field(default="1", description="Unit URI (1 = dimensionless)")
    upperBound: Optional[str] = Field(None, description="Upper bound")
    lowerBound: Optional[str] = Field(None, description="Lower bound")


class GlobeCoordinate(BaseModel):
    """Wikidata globe coordinate."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    precision: Optional[float] = Field(None, description="Precision in degrees")
    globe: str = Field(default="http://www.wikidata.org/entity/Q2", description="Globe URI (Q2 = Earth)")


class MonolingualText(BaseModel):
    """Wikidata monolingual text."""
    
    text: str = Field(..., description="The text")
    language: str = Field(..., description="Language code (e.g., 'en')")


class WikibaseEntityId(BaseModel):
    """Wikidata entity ID reference."""
    
    id: str = Field(..., description="Entity ID (e.g., 'Q123', 'P456')")
    entity_type: str = Field(default="item", description="Type: 'item' or 'property'")


class Datavalue(BaseModel):
    """Wikidata datavalue - a typed value."""
    
    type: DatavalueType = Field(..., description="Type of the value")
    value: Union[
        TimeValue,
        QuantityValue,
        GlobeCoordinate,
        MonolingualText,
        WikibaseEntityId,
        str,
        Dict[str, Any]
    ] = Field(..., description="The actual value (type depends on type field)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "time",
                "value": {
                    "time": "+1769-08-15T00:00:00Z",
                    "precision": 11,
                    "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                }
            }
        }
    )


class Snak(BaseModel):
    """Wikidata snak - a property-value pair."""
    
    snaktype: SnakType = Field(..., description="Type of snak")
    property: str = Field(..., description="Property ID (e.g., 'P569' for date of birth)")
    datavalue: Optional[Datavalue] = Field(None, description="The value (if snaktype is 'value')")
    datatype: Optional[str] = Field(None, description="Data type of the property")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "snaktype": "value",
                "property": "P569",
                "datavalue": {
                    "type": "time",
                    "value": {
                        "time": "+1769-08-15T00:00:00Z",
                        "precision": 11
                    }
                }
            }
        }
    )


class Reference(BaseModel):
    """Wikidata reference - source citation for a statement."""
    
    snaks: Dict[str, List[Snak]] = Field(default_factory=dict, description="Property-snak mapping")
    snaks_order: List[str] = Field(default_factory=list, description="Order of properties")
    hash: Optional[str] = Field(None, description="Reference hash")


class Qualifier(BaseModel):
    """Wikidata qualifier - additional property-value pair that qualifies a statement."""
    
    property: str = Field(..., description="Property ID")
    snaktype: SnakType = Field(..., description="Type of snak")
    datavalue: Optional[Datavalue] = Field(None, description="The value")
    hash: Optional[str] = Field(None, description="Qualifier hash")


class Claim(BaseModel):
    """Wikidata claim - a statement about an entity (property-value with qualifiers and references)."""
    
    id: Optional[str] = Field(None, description="Claim ID (guid)")
    mainsnak: Snak = Field(..., description="Main property-value pair")
    type: str = Field(default="statement", description="Type: 'statement', 'claim', etc.")
    rank: str = Field(default="normal", description="Rank: 'preferred', 'normal', 'deprecated'")
    qualifiers: Optional[Dict[str, List[Qualifier]]] = Field(None, description="Qualifiers by property")
    qualifiers_order: Optional[List[str]] = Field(None, description="Order of qualifier properties")
    references: Optional[List[Reference]] = Field(None, description="References/sources")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mainsnak": {
                    "snaktype": "value",
                    "property": "P569",
                    "datavalue": {
                        "type": "time",
                        "value": {
                            "time": "+1769-08-15T00:00:00Z",
                            "precision": 11
                        }
                    }
                },
                "type": "statement",
                "rank": "normal"
            }
        }
    )


class Statement(BaseModel):
    """Wikidata statement - a claim with its ID (alias for Claim with ID)."""
    
    id: str = Field(..., description="Statement ID (guid)")
    mainsnak: Snak = Field(..., description="Main property-value pair")
    type: str = Field(default="statement", description="Type")
    rank: str = Field(default="normal", description="Rank")
    qualifiers: Optional[Dict[str, List[Qualifier]]] = Field(None, description="Qualifiers")
    qualifiers_order: Optional[List[str]] = Field(None, description="Qualifier order")
    references: Optional[List[Reference]] = Field(None, description="References")


class EntityLabels(BaseModel):
    """Entity labels in multiple languages."""
    
    labels: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Language code -> {language, value}"
    )


class EntityDescriptions(BaseModel):
    """Entity descriptions in multiple languages."""
    
    descriptions: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Language code -> {language, value}"
    )


class EntityAliases(BaseModel):
    """Entity aliases in multiple languages."""
    
    aliases: Dict[str, List[Dict[str, str]]] = Field(
        default_factory=dict,
        description="Language code -> list of {language, value}"
    )


class WikibaseEntity(BaseModel):
    """Core Wikidata entity structure with claims."""
    
    id: str = Field(..., description="Entity ID (QID or PID)")
    type: str = Field(..., description="Entity type: 'item' or 'property'")
    labels: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Labels by language code"
    )
    descriptions: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Descriptions by language code"
    )
    aliases: Dict[str, List[Dict[str, str]]] = Field(
        default_factory=dict,
        description="Aliases by language code"
    )
    claims: Dict[str, List[Claim]] = Field(
        default_factory=dict,
        description="Claims by property ID"
    )
    sitelinks: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Sitelinks (links to Wikipedia articles)"
    )
    lastrevid: Optional[int] = Field(None, description="Last revision ID")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    
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
