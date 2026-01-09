"""Wikidata search and data retrieval utilities.

This module provides both utility functions and a repository class for querying
Wikidata. Initial searches use the Elasticsearch-backed search API (wbsearchentities)
which returns lightweight results. Full entity data is fetched via REST API (wbgetentities)
only when needed for linking or detailed views.
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


def get_random_wikidata_entities(limit: int = 1, instance_of: Optional[str] = None) -> List[str]:
    """Get random Wikidata entity QIDs using SPARQL.
    
    Uses Wikidata Query Service to fetch random entities. Can optionally filter
    by instance of a specific class (e.g., Q5 for human, Q1656682 for event).
    
    Args:
        limit: Number of random entities to return
        instance_of: Optional QID to filter by instance of (e.g., "Q5" for human)
    
    Returns:
        List of entity QIDs (e.g., ["Q517", "Q123"])
    """
    import random
    
    # Build SPARQL query - use a simpler approach that's more reliable
    if instance_of:
        query = f"""
        SELECT ?item WHERE {{
            ?item wdt:P31 wd:{instance_of} .
            ?item wikibase:sitelinks ?sitelinks .
        }} LIMIT 1000
        """
    else:
        # Get items with sitelinks (more likely to have good data)
        query = """
        SELECT ?item WHERE {
            ?item wikibase:sitelinks ?sitelinks .
        } LIMIT 1000
        """
    
    try:
        headers = {
            "User-Agent": WIKIDATA_USER_AGENT,
            "Accept": "application/sparql-results+json"
        }
        params = {"query": query, "format": "json"}
        
        logger.debug("[wikidata] SPARQL random query -> url=%s", WIKIDATA_SPARQL_URL)
        response = requests.get(WIKIDATA_SPARQL_URL, params=params, headers=headers, timeout=15)
        logger.debug("[wikidata] SPARQL response status=%s", response.status_code)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", {}).get("bindings", [])
        
        if not results:
            logger.warning("[wikidata] SPARQL returned no results")
            return []
        
        # Randomly sample from results
        sampled = random.sample(results, min(limit, len(results)))
        
        qids = []
        for result in sampled:
            item_uri = result.get("item", {}).get("value", "")
            # Extract QID from URI (e.g., "http://www.wikidata.org/entity/Q517" -> "Q517")
            if "/entity/" in item_uri:
                qid = item_uri.split("/entity/")[-1]
                qids.append(qid)
        
        logger.info(f"[wikidata] SPARQL returned {len(qids)} random entities from {len(results)} total")
        return qids
    except Exception as e:
        logger.exception("[wikidata] SPARQL random query error: %s", e)
        # Fallback: use search API with common terms
        logger.info("[wikidata] Falling back to search API for random entity")
        try:
            # Search for common terms and pick random result
            common_terms = ["the", "a", "of", "in", "and"]
            term = random.choice(common_terms)
            search_results = search_wikidata_entities(term, limit=50)
            if search_results:
                sampled = random.sample(search_results, min(limit, len(search_results)))
                qids = [r.get("id", "") for r in sampled if r.get("id", "")]
                logger.info(f"[wikidata] Fallback search returned {len(qids)} entities")
                return qids
        except Exception as fallback_error:
            logger.exception("[wikidata] Fallback search also failed: %s", fallback_error)
        return []


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
    """Search Wikidata using Elasticsearch-backed search API.
    
    This uses the wbsearchentities action which queries Wikidata's Elasticsearch index.
    Returns lightweight search results without fetching full entity data.
    Use get_wikidata_entity() to fetch full entity data when you have a QID.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        entity_type: Optional entity type filter (e.g., "item")
    
    Returns:
        List of lightweight search result dictionaries with: id, label, description, aliases, match
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
        logger.debug("[wikidata] elasticsearch search -> url=%s params=%s", WIKIDATA_API_URL, params)
        response = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=10)
        logger.debug("[wikidata] search response status=%s", response.status_code)
        response.raise_for_status()
        data = response.json()
        
        if config.wikidata_log_body:
            _log_body(response.text, "search_response")
        
        logger.debug("[wikidata] search response keys=%s", list(data.keys()) if isinstance(data, dict) else None)
        entities = data.get("search", [])
        logger.info(f"[wikidata] elasticsearch search returned {len(entities)} results for query: {query}")
        return entities
    except Exception as e:
        logger.exception("[wikidata] elasticsearch search error: %s", e)
        return []


def get_wikidata_entity(qid: str, use_entity_data: bool = False) -> Optional[Dict[str, Any]]:
    """Get full entity data from Wikidata by QID using REST API.
    
    This should be used for linking and detailed entity retrieval after you have a QID
    from a search result. Do not use this for initial searches - use search_wikidata_entities() instead.
    
    Args:
        qid: Wikidata entity QID (e.g., "Q123")
        use_entity_data: If True, use EntityData endpoint; otherwise use API endpoint
    
    Returns:
        Full entity dictionary with claims, labels, descriptions, etc., or None if not found
    """
    if not qid:
        return None
    
    if use_entity_data:
        # Use EntityData JSON endpoint (alternative method)
        entity_url = getattr(config, "wikidata_api", {}).get("entity_url", "https://www.wikidata.org/wiki/Special:EntityData/")
        try:
            url = f"{entity_url}{qid}.json"
            headers = {"User-Agent": WIKIDATA_USER_AGENT}
            logger.debug("[wikidata] fetch entity (REST) -> url=%s", url)
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
            "props": "labels|descriptions|claims|sitelinks|aliases",
            "languages": "en",
            "format": "json",
        }
        
        try:
            headers = {"User-Agent": WIKIDATA_USER_AGENT}
            logger.debug("[wikidata] fetch entity (REST) -> url=%s params=%s", WIKIDATA_API_URL, params)
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


def _search_hit_to_wikibase_entity(search_hit: Dict[str, Any]) -> "WikibaseEntity":
    """Convert a search hit to a lightweight WikibaseEntity model.
    
    This creates a WikibaseEntity from Elasticsearch search results, using only the data
    available in the search hit (label, description, aliases). This is the native Wikidata
    structure and doesn't force entities into Person/Event/Geography categories.
    """
    from python_aws_starter.models.wikidata_meta import WikibaseEntity
    
    qid = search_hit.get("id", "")
    label = search_hit.get("label", "")
    description = search_hit.get("description", "")
    aliases_data = search_hit.get("aliases", [])
    
    # Convert aliases to the expected format
    aliases = {}
    if aliases_data:
        aliases["en"] = [{"language": "en", "value": alias} for alias in aliases_data]
    
    entity = WikibaseEntity(
        id=qid,
        type="item",  # Most Wikidata entities are items
        labels={"en": {"language": "en", "value": label}} if label else {},
        descriptions={"en": {"language": "en", "value": description}} if description else {},
        aliases=aliases,
        claims={},  # Empty - fetch full entity if claims needed
    )
    return entity


def _search_hit_to_lightweight_person(search_hit: Dict[str, Any]) -> Person:
    """Convert a search hit to a lightweight Person model without fetching full entity.
    
    This creates a Person from Elasticsearch search results, using only the data
    available in the search hit (label, description, aliases).
    """
    qid = search_hit.get("id", "")
    label = search_hit.get("label", "")
    description = search_hit.get("description", "")
    
    now = datetime.now(timezone.utc)
    
    # Create lightweight person from search hit
    person = Person(
        id=f"person_wikidata_{qid}",
        name=label or qid,
        description=description or "",
        birth_date=None,
        death_date=None,
        birth_location=None,
        death_location=None,
        occupations=[],
        nationalities=[],
        created_by="wikidata_search",
        last_modified_by="wikidata_search",
        created_at=now,
        last_modified_at=now,
        labels={"en": {"language": "en", "value": label}} if label else {},
        descriptions={"en": {"language": "en", "value": description}} if description else {},
        aliases={},
        claims={},  # Empty - fetch full entity if claims needed
        sources=[SourceAttribution(
            source_id="wikidata_search",
            source_name="Wikidata Search",
            source_type=SourceType.SCRAPED,
            trust_level=0.7,
            fields_contributed=["name", "description"],
        )],
        confidence=0.7,
    )
    return person


def _search_hit_to_lightweight_event(search_hit: Dict[str, Any]) -> Event:
    """Convert a search hit to a lightweight Event model without fetching full entity.
    
    This creates an Event from Elasticsearch search results, using only the data
    available in the search hit (label, description, aliases).
    """
    qid = search_hit.get("id", "")
    label = search_hit.get("label", "")
    description = search_hit.get("description", "")
    
    now = datetime.now(timezone.utc)
    
    # Create lightweight event from search hit
    event = Event(
        id=f"event_wikidata_{qid}",
        title=label or qid,
        description=description or "",
        start_date=DateRange(start_date="", precision="unknown"),
        end_date=None,
        locations=[],
        related_people=[],
        created_by="wikidata_search",
        last_modified_by="wikidata_search",
        created_at=now,
        last_modified_at=now,
        labels={"en": {"language": "en", "value": label}} if label else {},
        descriptions={"en": {"language": "en", "value": description}} if description else {},
        aliases={},
        claims={},  # Empty - fetch full entity if claims needed
        sources=[SourceAttribution(
            source_id="wikidata_search",
            source_name="Wikidata Search",
            source_type=SourceType.SCRAPED,
            trust_level=0.7,
            fields_contributed=["title", "description"],
        )],
        confidence=0.7,
    )
    return event


def _search_hit_to_lightweight_geography(search_hit: Dict[str, Any]) -> Geography:
    """Convert a search hit to a lightweight Geography model without fetching full entity.
    
    This creates a Geography from Elasticsearch search results, using only the data
    available in the search hit (label, description, aliases).
    """
    qid = search_hit.get("id", "")
    label = search_hit.get("label", "")
    description = search_hit.get("description", "")
    
    now = datetime.now(timezone.utc)
    
    # Create lightweight geography from search hit
    geography = Geography(
        id=f"geo_wikidata_{qid}",
        name=label or qid,
        description=description or "",
        geography_type=GeographyType.OTHER,  # Unknown from search hit
        center_coordinate=None,  # Would need full entity for coordinates
        created_by="wikidata_search",
        last_modified_by="wikidata_search",
        created_at=now,
        last_modified_at=now,
        labels={"en": {"language": "en", "value": label}} if label else {},
        descriptions={"en": {"language": "en", "value": description}} if description else {},
        aliases={},
        claims={},  # Empty - fetch full entity if claims needed
        sources=[SourceAttribution(
            source_id="wikidata_search",
            source_name="Wikidata Search",
            source_type=SourceType.SCRAPED,
            trust_level=0.7,
            fields_contributed=["name", "description"],
        )],
        confidence=0.7,
    )
    return geography


def get_random_wikidata_entity(instance_of: Optional[str] = None) -> Optional["WikibaseEntity"]:
    """Get a single random Wikidata entity as WikibaseEntity.
    
    Uses SPARQL to get a random entity QID, then fetches full entity data
    and converts it to WikibaseEntity.
    
    Args:
        instance_of: Optional QID to filter by instance of (e.g., "Q5" for human)
    
    Returns:
        WikibaseEntity or None if no entity found
    """
    from python_aws_starter.models.wikidata_meta import WikibaseEntity
    
    # Get random QID using SPARQL
    qids = get_random_wikidata_entities(limit=1, instance_of=instance_of)
    if not qids:
        logger.warning("[wikidata] No random QIDs returned from SPARQL")
        return None
    
    qid = qids[0]
    logger.info(f"[wikidata] Got random QID: {qid}")
    
    # Fetch full entity data
    entity_data = get_wikidata_entity(qid)
    if not entity_data:
        logger.warning(f"[wikidata] Could not fetch entity data for QID: {qid}")
        return None
    
    # Convert to WikibaseEntity
    try:
        # Extract labels, descriptions, aliases, claims
        labels = entity_data.get("labels", {})
        descriptions = entity_data.get("descriptions", {})
        aliases = entity_data.get("aliases", {})
        claims_raw = entity_data.get("claims", {})
        
        # Convert claims to our Claim models
        claims = _convert_wikidata_claims_to_model_claims(claims_raw)
        
        entity = WikibaseEntity(
            id=qid,
            type=entity_data.get("type", "item"),
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            claims=claims,
            sitelinks=entity_data.get("sitelinks"),
            lastrevid=entity_data.get("lastrevid"),
            modified=entity_data.get("modified"),
        )
        
        logger.info(f"[wikidata] Successfully created WikibaseEntity for {qid}")
        return entity
    except Exception as e:
        logger.exception(f"[wikidata] Error converting entity {qid} to WikibaseEntity: {e}")
        return None


def search_wikidata_entities_as_wikibase(query: str, limit: int = 10) -> List["WikibaseEntity"]:
    """Search Wikidata using Elasticsearch and return native WikibaseEntity models.
    
    This is the recommended approach for Wikidata searches - returns entities in their
    native structure without forcing them into Person/Event/Geography categories.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of lightweight WikibaseEntity models from search results
    """
    from python_aws_starter.models.wikidata_meta import WikibaseEntity
    
    # Use Elasticsearch search API
    search_results = search_wikidata_entities(query, limit=limit)
    entities = []
    
    for search_hit in search_results:
        qid = search_hit.get("id", "")
        if not qid:
            continue
        
        # Create lightweight WikibaseEntity from search hit
        entity = _search_hit_to_wikibase_entity(search_hit)
        entities.append(entity)
    
    logger.info(f"[wikidata] elasticsearch search returned {len(entities)} entities for query: {query}")
    return entities


def search_wikidata_people(query: str, limit: int = 10) -> List[Person]:
    """Search Wikidata for people using Elasticsearch, returning lightweight results.
    
    DEPRECATED: Use search_wikidata_entities_as_wikibase() for native Wikidata structure.
    This function is kept for backward compatibility but forces entities into Person model.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of lightweight Person models from search results
    """
    # Use Elasticsearch search API
    search_results = search_wikidata_entities(query, limit=limit * 2)  # Get more to filter
    people = []
    
    for search_hit in search_results:
        qid = search_hit.get("id", "")
        if not qid:
            continue
        
        # Create lightweight person from search hit
        # We don't fetch full entity data here - that's done only when needed for linking
        person = _search_hit_to_lightweight_person(search_hit)
        people.append(person)
        
        if len(people) >= limit:
            break
    
    logger.info(f"[wikidata] elasticsearch search returned {len(people)} people for query: {query}")
    return people


def search_wikidata_events(query: str, limit: int = 10) -> List[Event]:
    """Search Wikidata for events using Elasticsearch, returning lightweight results.
    
    This uses the Elasticsearch-backed search API and returns lightweight Event models
    without fetching full entity data. Use get_wikidata_entity_by_qid() to fetch full
    entity data when needed for linking.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of lightweight Event models from search results
    """
    # Use Elasticsearch search API
    search_results = search_wikidata_entities(query, limit=limit * 2)  # Get more to filter
    events = []
    
    for search_hit in search_results:
        qid = search_hit.get("id", "")
        if not qid:
            continue
        
        # Create lightweight event from search hit
        # We don't fetch full entity data here - that's done only when needed for linking
        event = _search_hit_to_lightweight_event(search_hit)
        events.append(event)
        
        if len(events) >= limit:
            break
    
    logger.info(f"[wikidata] elasticsearch search returned {len(events)} events for query: {query}")
    return events


def search_wikidata_geographies(query: str, limit: int = 10) -> List[Geography]:
    """Search Wikidata for geographies using Elasticsearch, returning lightweight results.
    
    This uses the Elasticsearch-backed search API and returns lightweight Geography models
    without fetching full entity data. Use get_wikidata_entity_by_qid() to fetch full
    entity data when needed for linking.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    
    Returns:
        List of lightweight Geography models from search results
    """
    # Use Elasticsearch search API
    search_results = search_wikidata_entities(query, limit=limit * 2)  # Get more to filter
    geographies = []
    
    for search_hit in search_results:
        qid = search_hit.get("id", "")
        if not qid:
            continue
        
        # Create lightweight geography from search hit
        # We don't fetch full entity data here - that's done only when needed for linking
        geography = _search_hit_to_lightweight_geography(search_hit)
        geographies.append(geography)
        
        if len(geographies) >= limit:
            break
    
    logger.info(f"[wikidata] elasticsearch search returned {len(geographies)} geographies for query: {query}")
    return geographies


def get_wikidata_entity_by_qid(qid: str) -> Optional[Dict[str, Any]]:
    """Get full entity data by QID for linking purposes.
    
    This is a convenience wrapper around get_wikidata_entity() for when you have
    a QID and need full entity data (claims, etc.) for linking or detailed views.
    
    Args:
        qid: Wikidata QID (e.g., "Q123" or "person_wikidata_Q123")
    
    Returns:
        Full entity dictionary or None
    """
    # Extract QID if it's in the format "person_wikidata_Q123"
    if "_" in qid:
        parts = qid.split("_")
        qid = parts[-1] if parts[-1].startswith("Q") else qid
    
    return get_wikidata_entity(qid)


# Keep the old conversion functions for when we do fetch full entities
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
    
    Args:
        date_value: Wikidata time value dict with 'time' field
    
    Returns:
        ISO date string (YYYY-MM-DD) or None
    """
    if not date_value or not isinstance(date_value, dict):
        return None
    
    time_str = date_value.get("time", "")
    if not time_str:
        return None
    
    # Wikidata time format: +1769-08-15T00:00:00Z
    # Extract date part
    if time_str.startswith("+"):
        time_str = time_str[1:]
    if "T" in time_str:
        time_str = time_str.split("T")[0]
    
    return time_str


def _convert_wikidata_claims_to_model_claims(wikidata_claims: Dict[str, Any]) -> Dict[str, List[Claim]]:
    """Converts raw Wikidata claims to our Claim models."""
    from python_aws_starter.models.claims_utils import Property
    
    model_claims: Dict[str, List[Claim]] = {}
    for prop_id, statements_data in wikidata_claims.items():
        model_claims[prop_id] = []
        for statement_data in statements_data:
            try:
                mainsnak_data = statement_data.get("mainsnak", {})
                datavalue_data = mainsnak_data.get("datavalue", {})
                
                snak_type = SnakType(mainsnak_data.get("snaktype", "value"))
                datavalue_type = DatavalueType(datavalue_data.get("type")) if datavalue_data else None

                value = None
                if datavalue_type == DatavalueType.TIME:
                    value = TimeValue(**datavalue_data.get("value", {}))
                elif datavalue_type == DatavalueType.WIKIBASE_ENTITY:
                    value = WikibaseEntityId(**datavalue_data.get("value", {}))
                elif datavalue_type == DatavalueType.STRING:
                    value = datavalue_data.get("value")
                elif datavalue_type == DatavalueType.MONOLINGUAL_TEXT:
                    from python_aws_starter.models.wikidata_meta import MonolingualText
                    value = MonolingualText(**datavalue_data.get("value", {}))
                elif datavalue_type == DatavalueType.GLOBE_COORDINATE:
                    value = GlobeCoordinate(**datavalue_data.get("value", {}))

                snak = Snak(
                    snaktype=snak_type,
                    property=mainsnak_data.get("property"),
                    datavalue=Datavalue(type=datavalue_type, value=value) if datavalue_type else None,
                    hash=mainsnak_data.get("hash")
                )
                
                # Create claim directly
                claim = Claim(
                    mainsnak=snak,
                    type=statement_data.get("type", "statement"),
                    rank=statement_data.get("rank", "normal"),
                    id=statement_data.get("id")
                )
                model_claims[prop_id].append(claim)
            except Exception as e:
                logger.warning(f"Failed to convert Wikidata claim for property {prop_id}: {e}")
    return model_claims


def wikidata_to_person(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Person]:
    """Convert full Wikidata entity to Person model.
    
    Use this when you have fetched full entity data via get_wikidata_entity().
    For initial searches, use search_wikidata_people() which returns lightweight results.
    """
    try:
        name = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit)
        
        claims = entity.get("claims", {})
        
        # Extract dates
        birth_date = None
        death_date = None
        birth_date_val = _get_claim_value(claims, "P569")
        if birth_date_val:
            birth_date = _parse_wikidata_date(birth_date_val)
        
        death_date_val = _get_claim_value(claims, "P570")
        if death_date_val:
            death_date = _parse_wikidata_date(death_date_val)
        
        # Extract occupations (simplified - would need entity resolution)
        occupations = []
        occ_claims = claims.get("P106", [])
        for occ_claim in occ_claims[:5]:  # Limit to 5
            try:
                occ_entity = occ_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(occ_entity, dict):
                    # Would need to resolve entity to get label
                    occupations.append(occ_entity.get("id", ""))
            except (KeyError, TypeError):
                continue
        
        # Extract nationalities (simplified)
        nationalities = []
        nat_claims = claims.get("P27", [])
        for nat_claim in nat_claims[:3]:  # Limit to 3
            try:
                nat_entity = nat_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(nat_entity, dict):
                    nationalities.append(nat_entity.get("id", ""))
            except (KeyError, TypeError):
                continue
        
        now = datetime.now(timezone.utc)
        source = SourceAttribution(
            source_id="wikidata",
            source_name="Wikidata",
            source_type=SourceType.SCRAPED,
            trust_level=0.8,
            fields_contributed=["name", "description", "dates", "occupations"],
            url=f"https://www.wikidata.org/wiki/{qid}",
        )
        
        # Convert labels, descriptions, aliases
        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})
        
        person = Person(
            id=f"person_wikidata_{qid}",
            name=name,
            description=description,
            birth_date=birth_date,
            death_date=death_date,
            birth_location=None,
            death_location=None,
            occupations=occupations,
            nationalities=nationalities,
            created_by="wikidata",
            last_modified_by="wikidata",
            created_at=now,
            last_modified_at=now,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            claims=_convert_wikidata_claims_to_model_claims(claims),
            sources=[source],
            confidence=0.8,
        )
        
        return person
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Person: {e}")
        return None


def wikidata_to_event(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Event]:
    """Convert full Wikidata entity to Event model.
    
    Use this when you have fetched full entity data via get_wikidata_entity().
    For initial searches, use search_wikidata_events() which returns lightweight results.
    """
    try:
        title = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit)
        
        claims = entity.get("claims", {})
        
        # Extract dates
        start_date = None
        end_date = None
        
        # Try P580 (start time)
        start_val = _get_claim_value(claims, "P580")
        if start_val:
            start_date = _parse_wikidata_date(start_val)
        
        # Try P585 (point in time) if no start time
        if not start_date:
            point_val = _get_claim_value(claims, "P585")
            if point_val:
                start_date = _parse_wikidata_date(point_val)
        
        # Try P571 (inception) if still no start time
        if not start_date:
            inception_val = _get_claim_value(claims, "P571")
            if inception_val:
                start_date = _parse_wikidata_date(inception_val)
        
        # End time
        end_val = _get_claim_value(claims, "P582")
        if end_val:
            end_date = _parse_wikidata_date(end_val)
        
        # Create date range
        date_range = DateRange(
            start_date=start_date or "",
            end_date=end_date or start_date or "",
            precision="day" if start_date and len(start_date) >= 10 else "year"
        )
        
        # Extract locations (simplified)
        locations = []
        loc_claims = claims.get("P276", [])
        for loc_claim in loc_claims[:5]:
            try:
                loc_entity = loc_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(loc_entity, dict):
                    loc_qid = loc_entity.get("id", "")
                    locations.append(GeographicReference(
                        geography_id=f"geo_wikidata_{loc_qid}",
                        name=loc_qid
                    ))
            except (KeyError, TypeError):
                continue
        
        now = datetime.now(timezone.utc)
        source = SourceAttribution(
            source_id="wikidata",
            source_name="Wikidata",
            source_type=SourceType.SCRAPED,
            trust_level=0.8,
            fields_contributed=["title", "description", "dates", "locations"],
            url=f"https://www.wikidata.org/wiki/{qid}",
        )
        
        # Convert labels, descriptions, aliases
        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})
        
        event = Event(
            id=f"event_wikidata_{qid}",
            title=title,
            description=description,
            start_date=date_range,
            end_date=DateRange(start_date=end_date or "", end_date=end_date or "") if end_date else None,
            locations=locations,
            related_people=[],
            created_by="wikidata",
            last_modified_by="wikidata",
            created_at=now,
            last_modified_at=now,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            claims=_convert_wikidata_claims_to_model_claims(claims),
            sources=[source],
            confidence=0.8,
        )
        
        return event
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Event: {e}")
        return None


def wikidata_to_geography(entity: Dict[str, Any], qid: str, search_hit: Optional[Dict[str, Any]] = None) -> Optional[Geography]:
    """Convert full Wikidata entity to Geography model.
    
    Use this when you have fetched full entity data via get_wikidata_entity().
    For initial searches, use search_wikidata_geographies() which returns lightweight results.
    """
    try:
        name = _get_label(entity, fallback=search_hit)
        description = _get_description(entity, fallback=search_hit)
        
        claims = entity.get("claims", {})
        
        # Extract coordinates
        coord = None
        coord_val = _get_claim_value(claims, "P625")
        if coord_val and isinstance(coord_val, dict):
            lat = coord_val.get("latitude")
            lon = coord_val.get("longitude")
            if lat is not None and lon is not None:
                coord = Coordinate(latitude=lat, longitude=lon)
        
        # Determine geography type from instance of claims
        geo_type = GeographyType.OTHER
        instance_claims = claims.get("P31", [])
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    if inst_qid == "Q6256":  # country
                        geo_type = GeographyType.COUNTRY
                        break
                    elif inst_qid in ["Q515", "Q15284"]:  # city, settlement
                        geo_type = GeographyType.CITY
                        break
                    elif inst_qid == "Q5107":  # continent
                        geo_type = GeographyType.CONTINENT
                        break
            except (KeyError, TypeError):
                continue
        
        now = datetime.now(timezone.utc)
        source = SourceAttribution(
            source_id="wikidata",
            source_name="Wikidata",
            source_type=SourceType.SCRAPED,
            trust_level=0.8,
            fields_contributed=["name", "description", "coordinates", "type"],
            url=f"https://www.wikidata.org/wiki/{qid}",
        )
        
        # Convert labels, descriptions, aliases
        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})
        
        geography = Geography(
            id=f"geo_wikidata_{qid}",
            name=name,
            description=description,
            geography_type=geo_type,
            center_coordinate=coord,
            created_by="wikidata",
            last_modified_by="wikidata",
            created_at=now,
            last_modified_at=now,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            claims=_convert_wikidata_claims_to_model_claims(claims),
            sources=[source],
            confidence=0.8,
        )
        
        return geography
    except Exception as e:
        logger.error(f"Error converting Wikidata entity to Geography: {e}")
        return None


# Repository class for repository pattern support
class WikidataRepository:
    """Repository class for Wikidata-backed searches.
    
    This implements a repository pattern interface that uses Elasticsearch-backed
    search for initial queries and REST API for entity retrieval by QID.
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
        """Search for people in Wikidata using Elasticsearch."""
        if not text:
            return []
        return search_wikidata_people(text, limit=self.limit)
    
    def search_geographies(
        self,
        text: Optional[str] = None,
        center_coord: Optional[Tuple[float, float]] = None,
        within_km: Optional[float] = None
    ) -> List[Geography]:
        """Search for geographies in Wikidata using Elasticsearch.
        
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
        """Search for events in Wikidata using Elasticsearch.
        
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
