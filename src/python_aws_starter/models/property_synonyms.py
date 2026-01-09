"""Configuration for Wikidata property synonyms.

This module defines synonyms for various property types, particularly date-related
properties that can be treated as start dates or end dates. This allows the system
to recognize multiple Wikidata properties as equivalent for timeline operations.

Property definitions can be found at: https://www.wikidata.org/wiki/Property:{Pnumber}
"""

from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class PropertySynonym:
    """Represents a property ID and its description."""
    property_id: str
    description: str
    url: str


# Start date synonyms - properties that indicate when something begins
START_DATE_PROPERTIES: List[PropertySynonym] = [
    PropertySynonym(
        property_id="P571",
        description="Inception - when an entity came into existence",
        url="https://www.wikidata.org/wiki/Property:P571"
    ),
    PropertySynonym(
        property_id="P1619",
        description="Date of official opening - when something was officially opened",
        url="https://www.wikidata.org/wiki/Property:P1619"
    ),
    PropertySynonym(
        property_id="P569",
        description="Date of birth - when a person was born",
        url="https://www.wikidata.org/wiki/Property:P569"
    ),
    PropertySynonym(
        property_id="P580",
        description="Start time - when an event or period begins",
        url="https://www.wikidata.org/wiki/Property:P580"
    ),
    PropertySynonym(
        property_id="P585",
        description="Point in time - a specific moment in time",
        url="https://www.wikidata.org/wiki/Property:P585"
    ),
    PropertySynonym(
        property_id="P1319",
        description="Earliest date - the earliest possible date",
        url="https://www.wikidata.org/wiki/Property:P1319"
    ),
    PropertySynonym(
        property_id="P2031",
        description="Work period (start) - when a work period began",
        url="https://www.wikidata.org/wiki/Property:P2031"
    ),
    PropertySynonym(
        property_id="P1249",
        description="Time of earliest written record - earliest documented date",
        url="https://www.wikidata.org/wiki/Property:P1249"
    ),
]

# End date synonyms - properties that indicate when something ends
END_DATE_PROPERTIES: List[PropertySynonym] = [
    PropertySynonym(
        property_id="P570",
        description="Date of death - when a person died",
        url="https://www.wikidata.org/wiki/Property:P570"
    ),
    PropertySynonym(
        property_id="P582",
        description="End time - when an event or period ends",
        url="https://www.wikidata.org/wiki/Property:P582"
    ),
    PropertySynonym(
        property_id="P576",
        description="Dissolved, abolished or demolished - when something was dissolved",
        url="https://www.wikidata.org/wiki/Property:P576"
    ),
    PropertySynonym(
        property_id="P2669",
        description="Terminated - when something was terminated",
        url="https://www.wikidata.org/wiki/Property:P2669"
    ),
    PropertySynonym(
        property_id="P1326",
        description="Latest date - the latest possible date",
        url="https://www.wikidata.org/wiki/Property:P1326"
    ),
    PropertySynonym(
        property_id="P2032",
        description="Work period (end) - when a work period ended",
        url="https://www.wikidata.org/wiki/Property:P2032"
    ),
]

# Combined sets for easy lookup
START_DATE_PROPERTY_IDS: Set[str] = {prop.property_id for prop in START_DATE_PROPERTIES}
END_DATE_PROPERTY_IDS: Set[str] = {prop.property_id for prop in END_DATE_PROPERTIES}

# All date-related properties (for general date extraction)
ALL_DATE_PROPERTY_IDS: Set[str] = START_DATE_PROPERTY_IDS | END_DATE_PROPERTY_IDS


def get_start_date_properties() -> List[str]:
    """Get list of property IDs that represent start dates."""
    return list(START_DATE_PROPERTY_IDS)


def get_end_date_properties() -> List[str]:
    """Get list of property IDs that represent end dates."""
    return list(END_DATE_PROPERTY_IDS)


def is_start_date_property(property_id: str) -> bool:
    """Check if a property ID represents a start date."""
    return property_id in START_DATE_PROPERTY_IDS


def is_end_date_property(property_id: str) -> bool:
    """Check if a property ID represents an end date."""
    return property_id in END_DATE_PROPERTY_IDS


def is_date_property(property_id: str) -> bool:
    """Check if a property ID represents any date-related property."""
    return property_id in ALL_DATE_PROPERTY_IDS


def get_property_info(property_id: str) -> Dict[str, str]:
    """Get information about a property ID."""
    # Check start date properties
    for prop in START_DATE_PROPERTIES:
        if prop.property_id == property_id:
            return {
                "property_id": prop.property_id,
                "description": prop.description,
                "url": prop.url,
                "type": "start_date"
            }
    
    # Check end date properties
    for prop in END_DATE_PROPERTIES:
        if prop.property_id == property_id:
            return {
                "property_id": prop.property_id,
                "description": prop.description,
                "url": prop.url,
                "type": "end_date"
            }
    
    return {
        "property_id": property_id,
        "description": "Unknown property",
        "url": f"https://www.wikidata.org/wiki/Property:{property_id}",
        "type": "unknown"
    }
