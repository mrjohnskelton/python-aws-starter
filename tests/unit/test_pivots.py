"""Unit tests for pivot operations using the in-memory repository and sample fixtures."""
import pytest
from tests.fixtures import sample_dataset as sd
from python_aws_starter.repositories.in_memory import InMemoryRepository


@pytest.fixture
def repo():
    return InMemoryRepository(events=sd.EVENTS, people=sd.PEOPLE, geographies=sd.GEOGRAPHIES)


def test_get_events_by_person(repo):
    events = repo.get_events_by_person("person_napoleon")
    titles = {e.title for e in events}
    assert "French Revolution" in titles
    assert "Battle of Waterloo" in titles


def test_get_people_by_event(repo):
    people = repo.get_people_by_event("event_wwii")
    names = {p.name for p in people}
    assert "Winston Churchill" in names
    assert "Adolf Hitler" in names


def test_get_events_by_geo(repo):
    events = repo.get_events_by_geo("geo_waterloo")
    assert any(e.id == "event_waterloo" for e in events)


def test_pivot_router(repo):
    # people -> events
    res = repo.pivot("people", "events", "person_napoleon")
    assert any(e.id == "event_waterloo" for e in res)
    # events -> people
    res2 = repo.pivot("events", "people", "event_wwii")
    assert any(p.name == "Winston Churchill" for p in res2)


def test_geos_by_event(repo):
    geos = repo.get_geos_by_event("event_fall_rome")
    assert any(g.id == "geo_rome" for g in geos)
