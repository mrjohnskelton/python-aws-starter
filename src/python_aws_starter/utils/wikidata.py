"""Wikidata search and data retrieval utilities.

This module provides both utility functions and a repository class for querying
Wikidata and converting results to the project's domain models.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
import requests
from datetime import datetime, timezone

from python_aws_starter.config import config
from python_aws_starter.models.events import Event, DateRange, GeographicReference, PersonReference
from python_aws_starter.models.people import Person
from python_aws_starter.models.geography import Geography, GeographyType, Coordinate
from python_aws_starter.models.sources import SourceAttribution, SourceType
from python_aws_starter.models.wikidata_meta import (
    Claim, Snak, Datavalue, DatavalueType, SnakType,
    TimeValue, GlobeCoordinate, WikibaseEntityId, Qualifier, Reference
)

logger = logging.getLogger(__name__)

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# User-Agent header required by Wikidata API
WIKIDATA_USER_AGENT = "python-aws-starter/0.1.0 (https://github.com/mrjohnskelton/python-aws-starter; contact via GitHub)"


def _log_body(body: str, operation: str = "request") -> None:
    """Log request/response body if configured."""
    if config.wikidata_log_body:
        max_len = config.data_log_body_max
        body_str = str(body)
        if len(body_str) > max_len:
            logger.debug(f"Wikidata {operation} body (truncated to {max_len}): {body_str[:max_len]}...")
        else:
            logger.debug(f"Wikidata {operation} body: {body_str}")


def search_wikidata_entities(query: str, limit: int = 10, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search Wikidata for entities matching the query.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        entity_type: Optional entity type filter (e.g., "item")
    
    Returns:
        List of search result dictionaries
    """
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "limit": limit,
    }
    if entity_type:
        params["type"] = entity_type
    
    try:
        headers = {"User-Agent": WIKIDATA_USER_AGENT}
        logger.debug("[wikidata] search -> url=%s params=%s", WIKIDATA_API_URL, params)
        response = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=10)
        logger.debug("[wikidata] response status=%s", response.status_code)
        response.raise_for_status()
        data = response.json()
        
        if config.wikidata_log_body:
            _log_body(response.text, "search_response")
        
        logger.debug("[wikidata] response keys=%s", list(data.keys()) if isinstance(data, dict) else None)
        entities = data.get("search", [])
        return entities
    except Exception as e:
        logger.exception("[wikidata] search error: %s", e)
        return []


def get_wikidata_entity(qid: str, use_entity_data: bool = False) -> Optional[Dict[str, Any]]:
    """Get full entity data from Wikidata by QID.
    
    Args:
        qid: Wikidata entity QID (e.g., "Q123")
        use_entity_data: If True, use EntityData endpoint; otherwise use API endpoint
    
    Returns:
        Entity dictionary or None if not found
    """
    if not qid:
        return None
    
    if use_entity_data:
        # Use EntityData JSON endpoint (alternative method)
        entity_url = getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/Special:EntityData/")
        try:
            url = f"{entity_url}{qid}.json"
            headers = {"User-Agent": WIKIDATA_USER_AGENT}
            logger.debug("[wikidata] fetch entity -> url=%s", url)
            response = requests.get(url, headers=headers, timeout=10)
            logger.debug("[wikidata] entity response status=%s", response.status_code)
            response.raise_for_status()
            
            if config.wikidata_log_body:
                try:
                    text = response.text
                    logger.debug("[wikidata] entity response body (truncated): %s", text[:config.data_log_body_max])
                except Exception:
                    logger.debug("[wikidata] entity response body not available as text")
            
            data = response.json()
            logger.debug("[wikidata] entity keys=%s", list(data.keys()) if isinstance(data, dict) else None)
            return data.get("entities", {}).get(qid)
        except Exception as e:
            logger.exception("[wikidata] fetch entity error for %s: %s", qid, e)
            # Fallback to API endpoint
            return get_wikidata_entity(qid, use_entity_data=False)
    else:
        # Use API endpoint (default, more reliable)
        params = {
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels|descriptions|claims|sitelinks",
            "languages": "en",
            "format": "json",
        }
        
        try:
            headers = {"User-Agent": WIKIDATA_USER_AGENT}
            logger.debug("[wikidata] fetch entity -> url=%s params=%s", WIKIDATA_API_URL, params)
            response = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=10)
            logger.debug("[wikidata] entity response status=%s", response.status_code)
            response.raise_for_status()
            data = response.json()
            
            if config.wikidata_log_body:
                _log_body(response.text, "entity_response")
            
            logger.debug("[wikidata] entity keys=%s", list(data.keys()) if isinstance(data, dict) else None)
            entities = data.get("entities", {})
            return entities.get(qid)
        except Exception as e:
            logger.exception("[wikidata] fetch entity error for %s: %s", qid, e)
            return None


def _get_label(entity: Dict[str, Any], lang: str = "en", fallback: Optional[Dict[str, Any]] = None) -> str:
    """Extract label from Wikidata entity with fallback support."""
    labels = entity.get("labels", {})
    label = labels.get(lang, {}).get("value", "")
    
    # Fallback to search hit if provided
    if not label and fallback:
        label = fallback.get("label", "")
    
    return label or entity.get("id", "")


def _get_description(entity: Dict[str, Any], lang: str = "en", fallback: Optional[Dict[str, Any]] = None) -> str:
    """Extract description from Wikidata entity with fallback support."""
    descriptions = entity.get("descriptions", {})
    desc = descriptions.get(lang, {}).get("value", "")
    
    # Fallback to search hit if provided
    if not desc and fallback:
        desc = fallback.get("description", "")
    
    return desc


def _get_claim_value(claims: Dict[str, Any], prop: str) -> Optional[Any]:
    """Extract value from Wikidata claims."""
    if prop not in claims or not claims[prop]:
        return None
    try:
        mainsnak = claims[prop][0].get("mainsnak", {})
        if mainsnak.get("snaktype") != "value":
            return None
        datavalue = mainsnak.get("datavalue", {})
        return datavalue.get("value")
    except (KeyError, IndexError, TypeError):
        return None


def _parse_wikidata_date(date_value: Dict[str, Any]) -> Optional[str]:
    """Parse Wikidata time value to ISO date string.
    
    Handles both API format (dict with 'time' key) and EntityData format (direct string).
    """
    if not date_value:
        return None
    
    # Handle EntityData format (direct string)
    if isinstance(date_value, str):
        time_str = date_value
    else:
        # Handle API format (dict with 'time' key)
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


def _convert_wikidata_claim_to_claim(wikidata_claim: Dict[str, Any]) -> Optional[Claim]:
    """Convert a raw Wikidata claim dictionary to our Claim model."""
    try:
        mainsnak_data = wikidata_claim.get("mainsnak", {})
        if not mainsnak_data:
            return None
        
        snaktype = SnakType(mainsnak_data.get("snaktype", "value"))
        property_id = mainsnak_data.get("property", "")
        
        # Convert datavalue
        datavalue = None
        if snaktype == SnakType.VALUE and "datavalue" in mainsnak_data:
            wd_datavalue = mainsnak_data["datavalue"]
            value_type = wd_datavalue.get("type", "")
            value_data = wd_datavalue.get("value", {})
            
            if value_type == "time":
                time_value = TimeValue(
                    time=value_data.get("time", ""),
                    timezone=value_data.get("timezone", 0),
                    before=value_data.get("before", 0),
                    after=value_data.get("after", 0),
                    precision=value_data.get("precision", 11),
                    calendarmodel=value_data.get("calendarmodel", "http://www.wikidata.org/entity/Q1985727")
                )
                datavalue = Datavalue(type=DatavalueType.TIME, value=time_value)
            elif value_type == "wikibase-entityid":
                entity_value = WikibaseEntityId(
                    id=value_data.get("id", ""),
                    entity_type=value_data.get("entity-type", "item")
                )
                datavalue = Datavalue(type=DatavalueType.WIKIBASE_ENTITY, value=entity_value)
            elif value_type == "globecoordinate":
                coord_value = GlobeCoordinate(
                    latitude=value_data.get("latitude", 0),
                    longitude=value_data.get("longitude", 0),
                    precision=value_data.get("precision"),
                    globe=value_data.get("globe", "http://www.wikidata.org/entity/Q2")
                )
                datavalue = Datavalue(type=DatavalueType.GLOBE_COORDINATE, value=coord_value)
            elif value_type == "string":
                datavalue = Datavalue(type=DatavalueType.STRING, value=value_data)
            else:
                # Fallback: store as dict
                datavalue = Datavalue(type=DatavalueType(value_type) if hasattr(DatavalueType, value_type.upper().replace("-", "_")) else DatavalueType.STRING, value=value_data)
        
        snak = Snak(
            snaktype=snaktype,
            property=property_id,
            datavalue=datavalue,
            datatype=mainsnak_data.get("datatype")
        )
        
        # Convert qualifiers
        qualifiers = None
        qualifiers_order = None
        if "qualifiers" in wikidata_claim:
            qualifiers = {}
            qualifiers_order = []
            for prop, qual_list in wikidata_claim["qualifiers"].items():
                qualifiers[prop] = []
                for qual_data in qual_list:
                    qual_snaktype = SnakType(qual_data.get("snaktype", "value"))
                    qual_datavalue = None
                    if qual_snaktype == SnakType.VALUE and "datavalue" in qual_data:
                        # Similar conversion as above (simplified)
                        qual_datavalue = Datavalue(type=DatavalueType.STRING, value=qual_data["datavalue"].get("value", {}))
                    qualifiers[prop].append(Qualifier(
                        property=prop,
                        snaktype=qual_snaktype,
                        datavalue=qual_datavalue
                    ))
                qualifiers_order.append(prop)
        
        # Convert references (simplified)
        references = None
        if "references" in wikidata_claim:
            references = []
            for ref_data in wikidata_claim["references"]:
                ref_snaks = {}
                for prop, snak_list in ref_data.get("snaks", {}).items():
                    ref_snaks[prop] = []
                    for snak_data in snak_list:
                        ref_snak = Snak(
                            snaktype=SnakType(snak_data.get("snaktype", "value")),
                            property=prop,
                            datavalue=None  # Simplified
                        )
                        ref_snaks[prop].append(ref_snak)
                references.append(Reference(
                    snaks=ref_snaks,
                    snaks_order=ref_data.get("snaks-order", [])
                ))
        
        return Claim(
            id=wikidata_claim.get("id"),
            mainsnak=snak,
            type=wikidata_claim.get("type", "statement"),
            rank=wikidata_claim.get("rank", "normal"),
            qualifiers=qualifiers,
            qualifiers_order=qualifiers_order,
            references=references
        )
    except Exception as e:
        logger.error(f"Error converting Wikidata claim: {e}")
        return None


def _convert_wikidata_claims(wikidata_claims: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Claim]]:
    """Convert a dictionary of Wikidata claims to our Claim models."""
    converted = {}
    for property_id, claim_list in wikidata_claims.items():
        converted[property_id] = []
        for claim_data in claim_list:
            claim = _convert_wikidata_claim_to_claim(claim_data)
            if claim:
                converted[property_id].append(claim)
    return converted


def wikidata_to_event(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Event]:
    """Convert Wikidata entity to Event model."""
    try:
        title = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit) or title
        
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
            try:
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
            except (KeyError, IndexError, TypeError):
                continue
        
        # Create source attribution
        entity_url = getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/")
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["title", "description", "start_date", "locations"],
            external_id=qid,
            url=f"{entity_url}{qid}" if entity_url.endswith("/") else f"{entity_url}/{qid}"
        )
        
        now = datetime.now(timezone.utc)
        
        # Convert Wikidata claims to our Claim models
        converted_claims = _convert_wikidata_claims(claims)
        
        # Get labels and descriptions
        labels = {}
        descriptions = {}
        for lang, label_data in entity.get("labels", {}).items():
            labels[lang] = {"language": lang, "value": label_data.get("value", "")}
        for lang, desc_data in entity.get("descriptions", {}).items():
            descriptions[lang] = {"language": lang, "value": desc_data.get("value", "")}
        
        event = Event(
            id=f"event_wikidata_{qid}",
            title=title,
            description=description,
            start_date=start_date,
            end_date=DateRange(start_date=end_date_str, end_date=end_date_str) if end_date_str else None,
            locations=locations,
            sources=[source],
            confidence=0.7,
            created_at=now,
            created_by="wikidata",
            last_modified_at=now,
            last_modified_by="wikidata",
            claims=converted_claims,
            labels=labels,
            descriptions=descriptions
        )
        
        return event
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Event: {e}")
        return None


def wikidata_to_person(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Person]:
    """Convert Wikidata entity to Person model."""
    try:
        name = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit) or name
        
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
            try:
                occ_entity = occ_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(occ_entity, dict):
                    occ_qid = occ_entity.get("id", "")
                    occ_entity_data = get_wikidata_entity(occ_qid)
                    if occ_entity_data:
                        occ_name = _get_label(occ_entity_data)
                        if occ_name:
                            occupations.append(occ_name)
            except (KeyError, IndexError, TypeError):
                continue
        
        # Get nationality (P27: country of citizenship)
        nationalities = []
        nat_claims = claims.get("P27", [])
        for nat_claim in nat_claims[:3]:  # Limit to 3
            try:
                nat_entity = nat_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(nat_entity, dict):
                    nat_qid = nat_entity.get("id", "")
                    nat_entity_data = get_wikidata_entity(nat_qid)
                    if nat_entity_data:
                        nat_name = _get_label(nat_entity_data)
                        if nat_name:
                            nationalities.append(nat_name)
            except (KeyError, IndexError, TypeError):
                continue
        
        # Create source attribution
        entity_url = getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/")
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["name", "description", "birth_date", "death_date", "occupations", "nationalities"],
            external_id=qid,
            url=f"{entity_url}{qid}" if entity_url.endswith("/") else f"{entity_url}/{qid}"
        )
        
        now = datetime.now(timezone.utc)
        
        # Convert Wikidata claims to our Claim models
        converted_claims = _convert_wikidata_claims(claims)
        
        # Get labels and descriptions
        labels = {}
        descriptions = {}
        for lang, label_data in entity.get("labels", {}).items():
            labels[lang] = {"language": lang, "value": label_data.get("value", "")}
        for lang, desc_data in entity.get("descriptions", {}).items():
            descriptions[lang] = {"language": lang, "value": desc_data.get("value", "")}
        
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
            created_at=now,
            created_by="wikidata",
            last_modified_at=now,
            last_modified_by="wikidata",
            claims=converted_claims,
            labels=labels,
            descriptions=descriptions
        )
        
        return person
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Person: {e}")
        return None


def wikidata_to_geography(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Geography]:
    """Convert Wikidata entity to Geography model."""
    try:
        name = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit) or name
        
        claims = entity.get("claims", {})
        
        # Get coordinates (P625)
        center_coordinate = None
        coord_claims = claims.get("P625", [])
        if coord_claims:
            try:
                coord_val = coord_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(coord_val, dict):
                    lat = coord_val.get("latitude")
                    lon = coord_val.get("longitude")
                    if lat is not None and lon is not None:
                        center_coordinate = Coordinate(latitude=lat, longitude=lon)
            except (KeyError, IndexError, TypeError):
                pass
        
        # Determine geography type (P31: instance of)
        geography_type = GeographyType.OTHER  # Default
        instance_claims = claims.get("P31", [])
        for inst_claim in instance_claims:
            try:
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
            except (KeyError, IndexError, TypeError):
                continue
        
        # Create source attribution
        entity_url = getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/")
        source = SourceAttribution(
            source_id="wikipedia",
            source_name="Wikipedia",
            trust_level=0.7,
            fields_contributed=["name", "description", "center_coordinate", "geography_type"],
            external_id=qid,
            url=f"{entity_url}{qid}" if entity_url.endswith("/") else f"{entity_url}/{qid}"
        )
        
        now = datetime.now(timezone.utc)
        
        # Convert Wikidata claims to our Claim models
        converted_claims = _convert_wikidata_claims(claims)
        
        # Get labels and descriptions
        labels = {}
        descriptions = {}
        for lang, label_data in entity.get("labels", {}).items():
            labels[lang] = {"language": lang, "value": label_data.get("value", "")}
        for lang, desc_data in entity.get("descriptions", {}).items():
            descriptions[lang] = {"language": lang, "value": desc_data.get("value", "")}
        
        geography = Geography(
            id=f"geo_wikidata_{qid}",
            name=name,
            description=description,
            geography_type=geography_type,
            center_coordinate=center_coordinate,
            sources=[source],
            confidence=0.7,
            created_at=now,
            created_by="wikidata",
            last_modified_at=now,
            last_modified_by="wikidata",
            claims=converted_claims,
            labels=labels,
            descriptions=descriptions
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
        if not qid:
            continue
        
        # Get full entity data
        full_entity = get_wikidata_entity(qid)
        if not full_entity:
            continue
        
        # Check if it's an event type (instance of: Q1656682 event, Q1190554 occurrence, etc.)
        claims = full_entity.get("claims", {})
        instance_claims = claims.get("P31", [])
        is_event = False
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    if inst_qid in ["Q1656682", "Q1190554", "Q1983062"]:  # event, occurrence, historical event
                        is_event = True
                        break
            except (KeyError, IndexError, TypeError):
                continue
        
        if is_event:
            event = wikidata_to_event(full_entity, qid, search_hit=entity)
            if event:
                events.append(event)
        else:
            # Try to convert anyway if query matches (fallback)
            event = wikidata_to_event(full_entity, qid, search_hit=entity)
            if event:
                events.append(event)
    
    return events


def search_wikidata_people(query: str, limit: int = 10) -> List[Person]:
    """Search Wikidata for people and return Person models."""
    entities = search_wikidata_entities(query, limit)
    people = []
    
    for entity in entities:
        qid = entity.get("id", "")
        if not qid:
            continue
        
        # Get full entity data
        full_entity = get_wikidata_entity(qid)
        if not full_entity:
            continue
        
        # Check if it's a person (instance of: Q5 human)
        claims = full_entity.get("claims", {})
        instance_claims = claims.get("P31", [])
        is_person = False
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    if inst_qid == "Q5":  # human
                        is_person = True
                        break
            except (KeyError, IndexError, TypeError):
                continue
        
        if is_person:
            person = wikidata_to_person(full_entity, qid, search_hit=entity)
            if person:
                people.append(person)
    
    return people


def search_wikidata_geographies(query: str, limit: int = 10) -> List[Geography]:
    """Search Wikidata for geographic locations and return Geography models."""
    entities = search_wikidata_entities(query, limit)
    geographies = []
    
    for entity in entities:
        qid = entity.get("id", "")
        if not qid:
            continue
        
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
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    # Common geographic types
                    if inst_qid in ["Q6256", "Q515", "Q5107", "Q15284", "Q23442"]:  # country, city, continent, settlement, administrative territorial entity
                        is_geo = True
                        break
            except (KeyError, IndexError, TypeError):
                continue
        
        if is_geo or has_coords:
            geography = wikidata_to_geography(full_entity, qid, search_hit=entity)
            if geography:
                geographies.append(geography)
    
    return geographies


# Repository class for repository pattern support
class WikidataRepository:
    """Repository class for Wikidata-backed searches.
    
    This implements a repository pattern interface that wraps the utility functions,
    providing compatibility with repository-based code while using the comprehensive
    conversion functions from this module.
    """
    
    def __init__(self, base_url: Optional[str] = None, entity_url: Optional[str] = None, limit: int = 10, use_entity_data: bool = False):
        """Initialize Wikidata repository.
        
        Args:
            base_url: Wikidata API base URL (defaults to standard API URL)
            entity_url: EntityData URL for alternative endpoint (optional)
            limit: Default limit for searches
            use_entity_data: If True, prefer EntityData endpoint over API endpoint
        """
        self.base_url = base_url or WIKIDATA_API_URL
        self.entity_url = entity_url or getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/Special:EntityData/")
        self.limit = limit
        self.use_entity_data = use_entity_data
    
    def search_people(self, text: Optional[str] = None, related_event_id: Optional[str] = None) -> List[Person]:
        """Search for people in Wikidata."""
        if not text:
            return []
        return search_wikidata_people(text, limit=self.limit)
    
    def search_geographies(
        self,
        text: Optional[str] = None,
        center_coord: Optional[Tuple[float, float]] = None,
        within_km: Optional[float] = None
    ) -> List[Geography]:
        """Search for geographies in Wikidata.
        
        Note: center_coord and within_km filtering not yet implemented for Wikidata.
        """
        if not text:
            return []
        return search_wikidata_geographies(text, limit=self.limit)
    
    def search_events(
        self,
        text: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        geography_id: Optional[str] = None,
        center_coord: Optional[Tuple[float, float]] = None,
        within_km: Optional[float] = None
    ) -> List[Event]:
        """Search for events in Wikidata.
        
        Note: Date and location filtering not yet implemented for Wikidata.
        """
        if not text:
            return []
        return search_wikidata_events(text, limit=self.limit)
    
    def pivot(self, from_dim: str, to_dim: str, id_value: str):
        """Pivot operations are not supported against Wikidata in this implementation.
        
        Returns empty list.
        """
        return []
