"""Utility functions for working with Wikidata-style claims."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .wikidata_meta import (
    Claim,
    Snak,
    Datavalue,
    DatavalueType,
    SnakType,
    TimeValue,
    WikibaseEntityId,
    GlobeCoordinate,
)


# Common Wikidata property IDs
class Property:
    """Common Wikidata property IDs."""
    
    # Person properties
    DATE_OF_BIRTH = "P569"
    DATE_OF_DEATH = "P570"
    PLACE_OF_BIRTH = "P19"
    PLACE_OF_DEATH = "P20"
    OCCUPATION = "P106"
    COUNTRY_OF_CITIZENSHIP = "P27"
    INSTANCE_OF = "P31"
    
    # Event properties
    START_TIME = "P580"
    END_TIME = "P582"
    POINT_IN_TIME = "P585"
    LOCATION = "P276"
    INCEPTION = "P571"
    
    # Geography properties
    COORDINATE_LOCATION = "P625"
    
    # Common properties
    LABEL = "P1"  # Not a real property, but used for labels
    DESCRIPTION = "P2"  # Not a real property, but used for descriptions


def create_time_claim(property_id: str, date_str: str, precision: int = 11) -> Claim:
    """Create a time claim from an ISO date string.
    
    Args:
        property_id: Property ID (e.g., P569 for date of birth)
        date_str: ISO 8601 date string (e.g., "1769-08-15")
        precision: Precision level (9=year, 10=month, 11=day)
    
    Returns:
        Claim with time datavalue
    """
    # Convert ISO date to Wikidata time format
    if not date_str.startswith("+"):
        time_str = f"+{date_str}T00:00:00Z"
    else:
        time_str = f"{date_str}T00:00:00Z" if "T" not in date_str else date_str
    
    time_value = TimeValue(
        time=time_str,
        precision=precision,
        calendarmodel="http://www.wikidata.org/entity/Q1985727"
    )
    
    datavalue = Datavalue(
        type=DatavalueType.TIME,
        value=time_value
    )
    
    snak = Snak(
        snaktype=SnakType.VALUE,
        property=property_id,
        datavalue=datavalue
    )
    
    return Claim(
        mainsnak=snak,
        type="statement",
        rank="normal"
    )


def create_entity_claim(property_id: str, entity_id: str, entity_type: str = "item") -> Claim:
    """Create a claim with an entity reference.
    
    Args:
        property_id: Property ID
        entity_id: Entity ID (e.g., "Q123")
        entity_type: Entity type ("item" or "property")
    
    Returns:
        Claim with entity datavalue
    """
    entity_value = WikibaseEntityId(
        id=entity_id,
        entity_type=entity_type
    )
    
    datavalue = Datavalue(
        type=DatavalueType.WIKIBASE_ENTITY,
        value=entity_value
    )
    
    snak = Snak(
        snaktype=SnakType.VALUE,
        property=property_id,
        datavalue=datavalue
    )
    
    return Claim(
        mainsnak=snak,
        type="statement",
        rank="normal"
    )


def create_string_claim(property_id: str, value: str) -> Claim:
    """Create a claim with a string value.
    
    Args:
        property_id: Property ID
        value: String value
    
    Returns:
        Claim with string datavalue
    """
    datavalue = Datavalue(
        type=DatavalueType.STRING,
        value=value
    )
    
    snak = Snak(
        snaktype=SnakType.VALUE,
        property=property_id,
        datavalue=datavalue
    )
    
    return Claim(
        mainsnak=snak,
        type="statement",
        rank="normal"
    )


def create_coordinate_claim(property_id: str, latitude: float, longitude: float) -> Claim:
    """Create a claim with coordinate values.
    
    Args:
        property_id: Property ID (typically P625)
        latitude: Latitude
        longitude: Longitude
    
    Returns:
        Claim with coordinate datavalue
    """
    coord_value = GlobeCoordinate(
        latitude=latitude,
        longitude=longitude,
        globe="http://www.wikidata.org/entity/Q2"
    )
    
    datavalue = Datavalue(
        type=DatavalueType.GLOBE_COORDINATE,
        value=coord_value
    )
    
    snak = Snak(
        snaktype=SnakType.VALUE,
        property=property_id,
        datavalue=datavalue
    )
    
    return Claim(
        mainsnak=snak,
        type="statement",
        rank="normal"
    )


def extract_time_from_claim(claim: Claim) -> Optional[str]:
    """Extract ISO date string from a time claim.
    
    Args:
        claim: Claim with time datavalue
    
    Returns:
        ISO date string or None
    """
    if not claim.mainsnak.datavalue:
        return None
    
    if claim.mainsnak.datavalue.type != DatavalueType.TIME:
        return None
    
    time_value = claim.mainsnak.datavalue.value
    if isinstance(time_value, TimeValue):
        time_str = time_value.time
        # Remove + and T00:00:00Z
        if time_str.startswith("+"):
            time_str = time_str[1:]
        if "T" in time_str:
            time_str = time_str.split("T")[0]
        return time_str
    
    return None


def extract_entity_id_from_claim(claim: Claim) -> Optional[str]:
    """Extract entity ID from an entity claim.
    
    Args:
        claim: Claim with entity datavalue
    
    Returns:
        Entity ID or None
    """
    if not claim.mainsnak.datavalue:
        return None
    
    if claim.mainsnak.datavalue.type != DatavalueType.WIKIBASE_ENTITY:
        return None
    
    entity_value = claim.mainsnak.datavalue.value
    if isinstance(entity_value, WikibaseEntityId):
        return entity_value.id
    
    return None


def extract_string_from_claim(claim: Claim) -> Optional[str]:
    """Extract string value from a string claim.
    
    Args:
        claim: Claim with string datavalue
    
    Returns:
        String value or None
    """
    if not claim.mainsnak.datavalue:
        return None
    
    if claim.mainsnak.datavalue.type != DatavalueType.STRING:
        return None
    
    return str(claim.mainsnak.datavalue.value)


def extract_coordinate_from_claim(claim: Claim) -> Optional[tuple]:
    """Extract (latitude, longitude) from a coordinate claim.
    
    Args:
        claim: Claim with coordinate datavalue
    
    Returns:
        Tuple of (latitude, longitude) or None
    """
    if not claim.mainsnak.datavalue:
        return None
    
    if claim.mainsnak.datavalue.type != DatavalueType.GLOBE_COORDINATE:
        return None
    
    coord_value = claim.mainsnak.datavalue.value
    if isinstance(coord_value, GlobeCoordinate):
        return (coord_value.latitude, coord_value.longitude)
    
    return None
