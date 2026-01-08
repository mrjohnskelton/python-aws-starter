from typing import Optional
from fastapi import FastAPI, HTTPException, Query

from python_aws_starter.repositories.in_memory import InMemoryRepository
from tests.fixtures import sample_dataset as sd

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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    geography_id: Optional[str] = None,
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
    within_km: Optional[float] = None,
):
    center = None
    if center_lat is not None and center_lon is not None:
        center = (center_lat, center_lon)
    results = _repo.search_events(
        text=text,
        start_date=start_date,
        end_date=end_date,
        geography_id=geography_id,
        center_coord=center,
        within_km=within_km,
    )
    return [r.model_dump() for r in results]


@app.get("/search/people")
def search_people(text: Optional[str] = None, related_event_id: Optional[str] = None):
    results = _repo.search_people(text=text, related_event_id=related_event_id)
    return [r.model_dump() for r in results]


@app.get("/search/geographies")
def search_geographies(
    text: Optional[str] = None,
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
    within_km: Optional[float] = None,
):
    center = None
    if center_lat is not None and center_lon is not None:
        center = (center_lat, center_lon)
    results = _repo.search_geographies(text=text, center_coord=center, within_km=within_km)
    return [r.model_dump() for r in results]
