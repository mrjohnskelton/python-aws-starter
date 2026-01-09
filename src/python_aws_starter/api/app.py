import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from python_aws_starter.repositories.in_memory import InMemoryRepository
from python_aws_starter.config import config
from python_aws_starter.utils import wikidata as wd
from tests.fixtures import sample_dataset as sd

# Configure root logging early so repository modules use the same configuration.
numeric_level = getattr(logging, config.log_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Timeline Pivot API")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize a demo repository from test fixtures (suitable for local demo/dev)
_repo = InMemoryRepository(events=sd.get_events(), people=sd.get_people(), geographies=sd.get_geographies())


@app.get("/pivot")
def pivot(from_dim: str = Query(..., alias="from"), to_dim: str = Query(..., alias="to"), id: str = Query(...)):
    """Pivot from one dimension to another. Example: /pivot?from=people&to=events&id=person_napoleon"""
    res = _repo.pivot(from_dim, to_dim, id)
    if res is None:
        raise HTTPException(status_code=404, detail="No results")
    # serialize pydantic models
    return [r.model_dump() for r in res]


@app.get("/search/events")
def search_events(
    text: Optional[str] = None,
    q: Optional[str] = None,  # Accept 'q' parameter from frontend
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    geography_id: Optional[str] = None,
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
    within_km: Optional[float] = None,
):
    # Use 'q' if provided, otherwise 'text'
    search_query = q or text
    
    results = []
    
    # Search Wikidata if DATA_SOURCE is not "local" and we have a query
    if config.data_source != "local" and search_query:
        try:
            # Use native WikibaseEntity structure for Wikidata searches
            wikidata_results = wd.search_wikidata_entities_as_wikibase(search_query, limit=20)
            results.extend([r.model_dump() for r in wikidata_results])
            logger.info(f"Found {len(wikidata_results)} entities from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository (returns Event models)
    center = None
    if center_lat is not None and center_lon is not None:
        center = (center_lat, center_lon)
    local_results = _repo.search_events(
        text=search_query,
        start_date=start_date,
        end_date=end_date,
        geography_id=geography_id,
        center_coord=center,
        within_km=within_km,
    )
    results.extend([r.model_dump() for r in local_results])
    
    return results


@app.get("/search/people")
def search_people(
    text: Optional[str] = None,
    q: Optional[str] = None,  # Accept 'q' parameter from frontend
    related_event_id: Optional[str] = None,
):
    # Use 'q' if provided, otherwise 'text'
    search_query = q or text
    
    results = []
    
    # Search Wikidata if DATA_SOURCE is not "local" and we have a query
    if config.data_source != "local" and search_query:
        try:
            # Use native WikibaseEntity structure for Wikidata searches
            wikidata_results = wd.search_wikidata_entities_as_wikibase(search_query, limit=20)
            results.extend([r.model_dump() for r in wikidata_results])
            logger.info(f"Found {len(wikidata_results)} entities from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository (returns Person models)
    local_results = _repo.search_people(text=search_query, related_event_id=related_event_id)
    results.extend([r.model_dump() for r in local_results])
    
    return results


@app.get("/search/geographies")
def search_geographies(
    text: Optional[str] = None,
    q: Optional[str] = None,  # Accept 'q' parameter from frontend
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
    within_km: Optional[float] = None,
):
    # Use 'q' if provided, otherwise 'text'
    search_query = q or text
    
    results = []
    
    # Search Wikidata if DATA_SOURCE is not "local" and we have a query
    if config.data_source != "local" and search_query:
        try:
            # Use native WikibaseEntity structure for Wikidata searches
            wikidata_results = wd.search_wikidata_entities_as_wikibase(search_query, limit=20)
            results.extend([r.model_dump() for r in wikidata_results])
            logger.info(f"Found {len(wikidata_results)} entities from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository (returns Geography models)
    center = None
    if center_lat is not None and center_lon is not None:
        center = (center_lat, center_lon)
    local_results = _repo.search_geographies(text=search_query, center_coord=center, within_km=within_km)
    results.extend([r.model_dump() for r in local_results])
    
    return results


# Claims-based query endpoints
@app.get("/entity/{entity_id}/claims")
def get_entity_claims(entity_id: str, property_id: Optional[str] = None):
    """Get claims for an entity, optionally filtered by property ID.
    
    Example: /entity/person_napoleon/claims?property_id=P569
    """
    # Try to find entity in local repository
    entity = None
    
    # Check people
    person = _repo.get_person_by_id(entity_id)
    if person:
        entity = person
    else:
        # Check events
        event = _repo.get_event_by_id(entity_id)
        if event:
            entity = event
        else:
            # Check geographies
            geo = _repo.get_geo_by_id(entity_id)
            if geo:
                entity = geo
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    if property_id:
        claims = entity.get_claims(property_id)
        return {"entity_id": entity_id, "property_id": property_id, "claims": [c.model_dump() for c in claims]}
    else:
        return {"entity_id": entity_id, "claims": {pid: [c.model_dump() for c in claims] for pid, claims in entity.claims.items()}}


@app.get("/entity/{entity_id}/claim/{property_id}")
def get_entity_claim(entity_id: str, property_id: str):
    """Get the best claim for a specific property on an entity.
    
    Example: /entity/person_napoleon/claim/P569
    """
    # Try to find entity in local repository
    entity = None
    
    # Check people
    person = _repo.get_person_by_id(entity_id)
    if person:
        entity = person
    else:
        # Check events
        event = _repo.get_event_by_id(entity_id)
        if event:
            entity = event
        else:
            # Check geographies
            geo = _repo.get_geo_by_id(entity_id)
            if geo:
                entity = geo
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    claim = entity.get_best_claim(property_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"No claim found for property {property_id} on entity {entity_id}")
    
    return {"entity_id": entity_id, "property_id": property_id, "claim": claim.model_dump()}


@app.get("/wikidata/entity/{qid}")
def get_wikidata_entity_by_qid(qid: str):
    """Fetch full entity data from Wikidata by QID using REST API.
    
    This endpoint is used for linking - when you have a QID from a search result
    and need full entity data (claims, etc.). Initial searches should use the
    search endpoints which use Elasticsearch.
    
    Example: /wikidata/entity/Q123
    """
    try:
        # Extract QID if it's in the format "person_wikidata_Q123"
        if "_" in qid:
            parts = qid.split("_")
            qid = parts[-1] if parts[-1].startswith("Q") else qid
        
        # Fetch full entity using REST API
        entity_data = wd.get_wikidata_entity(qid)
        if not entity_data:
            raise HTTPException(status_code=404, detail=f"Entity {qid} not found in Wikidata")
        
        # Determine entity type and convert
        claims = entity_data.get("claims", {})
        instance_claims = claims.get("P31", [])
        
        # Check if it's a person
        is_person = False
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict) and inst_entity.get("id") == "Q5":  # human
                    is_person = True
                    break
            except (KeyError, TypeError):
                continue
        
        if is_person:
            person = wd.wikidata_to_person(entity_data, qid)
            if person:
                return person.model_dump()
        
        # Check if it's an event
        is_event = False
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    if inst_qid in ["Q1656682", "Q1190554", "Q1983062"]:  # event, occurrence, historical event
                        is_event = True
                        break
            except (KeyError, TypeError):
                continue
        
        if is_event:
            event = wd.wikidata_to_event(entity_data, qid)
            if event:
                return event.model_dump()
        
        # Check if it's a geography (has coordinates or geographic type)
        has_coords = "P625" in claims
        is_geo = False
        for inst_claim in instance_claims:
            try:
                inst_entity = inst_claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                if isinstance(inst_entity, dict):
                    inst_qid = inst_entity.get("id", "")
                    if inst_qid in ["Q6256", "Q515", "Q5107", "Q15284", "Q23442"]:  # geographic types
                        is_geo = True
                        break
            except (KeyError, TypeError):
                continue
        
        if is_geo or has_coords:
            geography = wd.wikidata_to_geography(entity_data, qid)
            if geography:
                return geography.model_dump()
        
        # If we can't determine type, return raw entity data
        return entity_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Wikidata entity {qid}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching entity: {str(e)}")


@app.get("/search/by-property")
def search_by_property(
    property_id: str = Query(..., description="Property ID to search (e.g., P569 for date of birth)"),
    value: Optional[str] = Query(None, description="Value to match (optional)"),
    entity_type: Optional[str] = Query(None, description="Entity type filter: 'person', 'event', or 'geography'"),
):
    """Search entities by property value.
    
    Example: /search/by-property?property_id=P569&value=1769-08-15
    """
    results = []
    
    # Search people
    if not entity_type or entity_type == "person":
        for person in _repo.list_people():
            claims = person.get_claims(property_id)
            if claims:
                if value:
                    # TODO: Implement value matching
                    pass
                results.append(person)
    
    # Search events
    if not entity_type or entity_type == "event":
        for event in _repo.list_events():
            claims = event.get_claims(property_id)
            if claims:
                if value:
                    # TODO: Implement value matching
                    pass
                results.append(event)
    
    # Search geographies
    if not entity_type or entity_type == "geography":
        for geo in _repo.list_geographies():
            claims = geo.get_claims(property_id)
            if claims:
                if value:
                    # TODO: Implement value matching
                    pass
                results.append(geo)
    
    return [r.model_dump() for r in results]
