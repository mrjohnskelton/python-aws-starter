import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query

from python_aws_starter.repositories.in_memory import InMemoryRepository
from python_aws_starter.config import config
from python_aws_starter.utils import wikidata as wd
from tests.fixtures import sample_dataset as sd

# Configure root logging early so repository modules use the same configuration.
numeric_level = getattr(logging, config.log_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Timeline Pivot API")

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
            wikidata_results = wd.search_wikidata_events(search_query, limit=20)
            results.extend(wikidata_results)
            logger.info(f"Found {len(wikidata_results)} events from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository
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
    results.extend(local_results)
    
    return [r.model_dump() for r in results]


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
            wikidata_results = wd.search_wikidata_people(search_query, limit=20)
            results.extend(wikidata_results)
            logger.info(f"Found {len(wikidata_results)} people from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository
    local_results = _repo.search_people(text=search_query, related_event_id=related_event_id)
    results.extend(local_results)
    
    return [r.model_dump() for r in results]


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
            wikidata_results = wd.search_wikidata_geographies(search_query, limit=20)
            results.extend(wikidata_results)
            logger.info(f"Found {len(wikidata_results)} geographies from Wikidata for query: {search_query}")
        except Exception as e:
            logger.error(f"Error searching Wikidata: {e}")
    
    # Also search local repository
    center = None
    if center_lat is not None and center_lon is not None:
        center = (center_lat, center_lon)
    local_results = _repo.search_geographies(text=search_query, center_coord=center, within_km=within_km)
    results.extend(local_results)
    
    return [r.model_dump() for r in results]
