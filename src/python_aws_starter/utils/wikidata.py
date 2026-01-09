"""Wikidata search and data retrieval utilities."""

import logging
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from python_aws_starter.config import config
from python_aws_starter.models.events import Event, DateRange, GeographicReference, PersonReference
from python_aws_starter.models.people import Person
from python_aws_starter.models.geography import Geography, GeographyType, Coordinate
from python_aws_starter.models.sources import SourceAttribution, SourceType

logger = logging.getLogger(__name__)

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"


def _log_body(body: str, operation: str = "request") -> None:
    """Log request/response body if configured."""
    if config.wikidata_log_body:
        max_len = config.data_log_body_max
        body_str = str(body)
        if len(body_str) > max_len:
            logger.debug(f"Wikidata {operation} body (truncated to {max_len}): {body_str[:max_len]}...")
        else:
            logger.debug(f"Wikidata {operation} body: {body_str}")


def search_wikidata_entities(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search Wikidata for entities matching the query."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "limit": limit,
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if config.wikidata_log_body:
            _log_body(response.text, "search_response")
        
        entities = data.get("search", [])
        return entities
    except Exception as e:
        logger.error(f"Error searching Wikidata: {e}")
        return []


def get_wikidata_entity(qid: str) -> Optional[Dict[str, Any]]:
    """Get full entity data from Wikidata by QID."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|descriptions|claims|sitelinks",
        "languages": "en",
        "format": "json",
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if config.wikidata_log_body:
            _log_body(response.text, "entity_response")
        
        entities = data.get("entities", {})
        return entities.get(qid)
    except Exception as e:
        logger.error(f"Error fetching Wikidata entity {qid}: {e}")
        return None


def _get_label(entity: Dict[str, Any], lang: str = "en") -> str:
    """Extract label from Wikidata entity."""
    labels = entity.get("labels", {})
    return labels.get(lang, {}).get("value", "")


def _get_description(entity: Dict[str, Any], lang: str = "en") -> str:
    """Extract description from Wikidata entity."""
    descriptions = entity.get("descriptions", {})
    return descriptions.get(lang, {}).get("value", "")


def _get_claim_value(claims: Dict[str, Any], prop: str) -> Optional[Any]:
    """Extract value from Wikidata claims."""
    if prop not in claims:
        return None
    mainsnak = claims[prop][0].get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    datavalue = mainsnak.get("datavalue", {})
    return datavalue.get("value")


def _parse_wikidata_date(date_value: Dict[str, Any]) -> Optional[str]:
    """Parse Wikidata time value to ISO date string."""
    if not date_value:
        return None
    time_str = date_value.get("time", "")
    if not time_str:
        return None
    # Wikidata dates are like "+1769-08-15T00:00:00Z"
    # Remove the + and T00:00:00Z part
    if time_str.startswith("+"):
        time_str = time_str[1:]
    if "T" in time_str:
        time_str = time_str.split("T")[0]
    return time_str


def wikidata_to_event(entity: Dict[str, Any], qid: str) -> Optional[Event]:
    """Convert Wikidata entity to Event model."""
    try:
        title = _get_label(entity)
        description = _get_description(entity) or title
        
        claims = entity.get("claims", {})
        
        # Get start date (P580: start time, P585: point in time)
        start_date_str = None
        for prop in ["P580", "P585"]:
            date_val = _get_claim_value(claims, prop)
            if date_val:
                start_date_str = _parse_wikidata_date(date_val)
                break
        
        if not start_date_str:
            # Try to get from inception (P571)
            date_val = _get_claim_value(claims, "P571")
            if date_val:
                start_date_str = _parse_wikidata_date(date_val)
        
        if not start_date_str:
            start_date_str = "0000-01-01"  # Default fallback
        
        # Get end date (P582: end time)
        end_date_str = None
        date_val = _get_claim_value(claims, "P582")
        if date_val:
            end_date_str = _parse_wikidata_date(date_val)
        
        start_date = DateRange(
            start_date=start_date_str,
            end_date=end_date_str,
            precision="day" if len(start_date_str) >= 10 else "year"
        )
        
        # Get location (P276: location)
        locations = []
        location_claims = claims.get("P276", [])
        for loc_claim in location_claims[:1]:  # Take first location
            loc_entity = loc_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(loc_entity, dict):
                loc_qid = loc_entity.get("id", "")
                loc_entity_data = get_wikidata_entity(loc_qid)
                if loc_entity_data:
                    loc_name = _get_label(loc_entity_data)
                    # Try to get coordinates
                    loc_coords = loc_entity_data.get("claims", {}).get("P625", [])
                    lat, lon = None, None
                    if loc_coords:
                        coord_val = loc_coords[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
                        if isinstance(coord_val, dict):
                            lat = coord_val.get("latitude")
                            lon = coord_val.get("longitude")
                    
                    locations.append(GeographicReference(
                        geography_id=f"geo_{loc_qid}",
                        name=loc_name,
                        latitude=lat,
                        longitude=lon
                    ))
        
        # Create source attribution
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["title", "description", "start_date", "locations"],
            external_id=qid,
            url=f"https://www.wikidata.org/wiki/{qid}"
        )
        
        event = Event(
            id=f"event_wikidata_{qid}",
            title=title,
            description=description,
            start_date=start_date,
            end_date=DateRange(start_date=end_date_str, end_date=end_date_str) if end_date_str else None,
            locations=locations,
            sources=[source],
            confidence=0.7,
            created_at=datetime.now(),
            created_by="wikidata"
        )
        
        return event
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Event: {e}")
        return None


def wikidata_to_person(entity: Dict[str, Any], qid: str) -> Optional[Person]:
    """Convert Wikidata entity to Person model."""
    try:
        name = _get_label(entity)
        description = _get_description(entity) or name
        
        claims = entity.get("claims", {})
        
        # Get birth date (P569)
        birth_date = None
        birth_val = _get_claim_value(claims, "P569")
        if birth_val:
            birth_date = _parse_wikidata_date(birth_val)
        
        # Get death date (P570)
        death_date = None
        death_val = _get_claim_value(claims, "P570")
        if death_val:
            death_date = _parse_wikidata_date(death_val)
        
        # Get occupations (P106: occupation)
        occupations = []
        occ_claims = claims.get("P106", [])
        for occ_claim in occ_claims[:5]:  # Limit to 5
            occ_entity = occ_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(occ_entity, dict):
                occ_qid = occ_entity.get("id", "")
                occ_entity_data = get_wikidata_entity(occ_qid)
                if occ_entity_data:
                    occ_name = _get_label(occ_entity_data)
                    if occ_name:
                        occupations.append(occ_name)
        
        # Get nationality (P27: country of citizenship)
        nationalities = []
        nat_claims = claims.get("P27", [])
        for nat_claim in nat_claims[:3]:  # Limit to 3
            nat_entity = nat_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(nat_entity, dict):
                nat_qid = nat_entity.get("id", "")
                nat_entity_data = get_wikidata_entity(nat_qid)
                if nat_entity_data:
                    nat_name = _get_label(nat_entity_data)
                    if nat_name:
                        nationalities.append(nat_name)
        
        # Create source attribution
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["name", "description", "birth_date", "death_date", "occupations", "nationalities"],
            external_id=qid,
            url=f"https://www.wikidata.org/wiki/{qid}"
        )
        
        person = Person(
            id=f"person_wikidata_{qid}",
            name=name,
            description=description,
            birth_date=birth_date,
            death_date=death_date,
            occupations=occupations,
            nationalities=nationalities,
            sources=[source],
            confidence=0.7,
            created_at=datetime.now(),
            created_by="wikidata"
        )
        
        return person
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Person: {e}")
        return None


def wikidata_to_geography(entity: Dict[str, Any], qid: str) -> Optional[Geography]:
    """Convert Wikidata entity to Geography model."""
    try:
        name = _get_label(entity)
        description = _get_description(entity) or name
        
        claims = entity.get("claims", {})
        
        # Get coordinates (P625)
        center_coordinate = None
        coord_claims = claims.get("P625", [])
        if coord_claims:
            coord_val = coord_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(coord_val, dict):
                lat = coord_val.get("latitude")
                lon = coord_val.get("longitude")
                if lat is not None and lon is not None:
                    center_coordinate = Coordinate(latitude=lat, longitude=lon)
        
        # Determine geography type (P31: instance of)
        geography_type = GeographyType.OTHER  # Default
        instance_claims = claims.get("P31", [])
        for inst_claim in instance_claims:
            inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(inst_entity, dict):
                inst_qid = inst_entity.get("id", "")
                # Map common Wikidata types to our GeographyType
                if inst_qid in ["Q6256"]:  # country
                    geography_type = GeographyType.COUNTRY
                elif inst_qid in ["Q515", "Q15284"]:  # city, settlement
                    geography_type = GeographyType.CITY
                elif inst_qid in ["Q5107"]:  # continent
                    geography_type = GeographyType.CONTINENT
                break
        
        # Create source attribution
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["name", "description", "center_coordinate", "geography_type"],
            external_id=qid,
            url=f"https://www.wikidata.org/wiki/{qid}"
        )
        
        geography = Geography(
            id=f"geo_wikidata_{qid}",
            name=name,
            description=description,
            geography_type=geography_type,
            center_coordinate=center_coordinate,
            sources=[source],
            confidence=0.7,
            created_at=datetime.now(),
            created_by="wikidata"
        )
        
        return geography
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Geography: {e}")
        return None


def search_wikidata_events(query: str, limit: int = 10) -> List[Event]:
    """Search Wikidata for events and return Event models."""
    entities = search_wikidata_entities(query, limit)
    events = []
    
    for entity in entities:
        qid = entity.get("id", "")
        entity_type = entity.get("concepturi", "").split("/")[-1] if entity.get("concepturi") else ""
        
        # Get full entity data
        full_entity = get_wikidata_entity(qid)
        if not full_entity:
            continue
        
        # Check if it's an event type (instance of: Q1656682 event, Q1190554 occurrence, etc.)
        claims = full_entity.get("claims", {})
        instance_claims = claims.get("P31", [])
        is_event = False
        for inst_claim in instance_claims:
            inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(inst_entity, dict):
                inst_qid = inst_entity.get("id", "")
                if inst_qid in ["Q1656682", "Q1190554", "Q1983062"]:  # event, occurrence, historical event
                    is_event = True
                    break
        
        if is_event:
            event = wikidata_to_event(full_entity, qid)
            if event:
                events.append(event)
        else:
            # Try to convert anyway if query matches
            event = wikidata_to_event(full_entity, qid)
            if event:
                events.append(event)
    
    return events


def search_wikidata_people(query: str, limit: int = 10) -> List[Person]:
    """Search Wikidata for people and return Person models."""
    entities = search_wikidata_entities(query, limit)
    people = []
    
    for entity in entities:
        qid = entity.get("id", "")
        
        # Get full entity data
        full_entity = get_wikidata_entity(qid)
        if not full_entity:
            continue
        
        # Check if it's a person (instance of: Q5 human)
        claims = full_entity.get("claims", {})
        instance_claims = claims.get("P31", [])
        is_person = False
        for inst_claim in instance_claims:
            inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(inst_entity, dict):
                inst_qid = inst_entity.get("id", "")
                if inst_qid == "Q5":  # human
                    is_person = True
                    break
        
        if is_person:
            person = wikidata_to_person(full_entity, qid)
            if person:
                people.append(person)
    
    return people


def search_wikidata_geographies(query: str, limit: int = 10) -> List[Geography]:
    """Search Wikidata for geographic locations and return Geography models."""
    entities = search_wikidata_entities(query, limit)
    geographies = []
    
    for entity in entities:
        qid = entity.get("id", "")
        
        # Get full entity data
        full_entity = get_wikidata_entity(qid)
        if not full_entity:
            continue
        
        # Check if it's a geographic location
        claims = full_entity.get("claims", {})
        has_coords = "P625" in claims  # Has coordinates
        instance_claims = claims.get("P31", [])
        is_geo = False
        
        for inst_claim in instance_claims:
            inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(inst_entity, dict):
                inst_qid = inst_entity.get("id", "")
                # Common geographic types
                if inst_qid in ["Q6256", "Q515", "Q5107", "Q15284", "Q23442"]:  # country, city, continent, settlement, administrative territorial entity
                    is_geo = True
                    break
        
        if is_geo or has_coords:
            geography = wikidata_to_geography(full_entity, qid)
            if geography:
                geographies.append(geography)
    
    return geographies
