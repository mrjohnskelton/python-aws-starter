from fastapi.testclient import TestClient
from python_aws_starter.api.app import app


client = TestClient(app)


def test_pivot_people_to_events():
    resp = client.get("/pivot", params={"from": "people", "to": "events", "id": "person_napoleon"})
    assert resp.status_code == 200
    data = resp.json()
    ids = [d["id"] for d in data]
    assert "event_waterloo" in ids or "event_french_revolution" in ids


def test_search_events_api_text():
    resp = client.get("/search/events", params={"text": "Waterloo"})
    assert resp.status_code == 200
    data = resp.json()
    ids = [d["id"] for d in data]
    assert "event_waterloo" in ids


def test_search_geographies_api_proximity():
    resp = client.get(
        "/search/geographies",
        params={"center_lat": 48.8566, "center_lon": 2.3522, "within_km": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    ids = [d["id"] for d in data]
    assert "geo_paris" in ids
