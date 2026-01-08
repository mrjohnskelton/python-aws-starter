from python_aws_starter.repositories.in_memory import InMemoryRepository
from tests.fixtures import sample_dataset as sd


def make_repo():
    return InMemoryRepository(events=sd.get_events(), people=sd.get_people(), geographies=sd.get_geographies())


def test_search_events_text():
    repo = make_repo()
    res = repo.search_events(text="Waterloo")
    ids = [e.id for e in res]
    assert "event_waterloo" in ids


def test_search_events_date_range():
    repo = make_repo()
    # Events in 1815 should include Waterloo
    res = repo.search_events(start_date="1815-01-01", end_date="1815-12-31")
    ids = [e.id for e in res]
    assert "event_waterloo" in ids


def test_search_events_geography():
    repo = make_repo()
    res = repo.search_events(geography_id="geo_rome")
    ids = [e.id for e in res]
    assert "event_fall_rome" in ids or "event_cleopatra" in ids


def test_search_geographies_proximity():
    repo = make_repo()
    # Near Paris coordinates should return Paris within 10 km
    res = repo.search_geographies(center_coord=(48.8566, 2.3522), within_km=10)
    ids = [g.id for g in res]
    assert "geo_paris" in ids


def test_search_people_by_text():
    repo = make_repo()
    res = repo.search_people(text="Napoleon")
    ids = [p.id for p in res]
    assert "person_napoleon" in ids
