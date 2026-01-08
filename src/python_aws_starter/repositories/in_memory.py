"""Simple in-memory repository to support pivot demos and tests."""
from typing import List, Optional, Dict, Any
from python_aws_starter.models.events import Event
from python_aws_starter.models.people import Person
from python_aws_starter.models.geography import Geography


class InMemoryRepository:
    def __init__(self, events: List[Event], people: List[Person], geographies: List[Geography]):
        self.events = {e.id: e for e in events}
        self.people = {p.id: p for p in people}
        self.geographies = {g.id: g for g in geographies}

    # Basic getters
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        return self.events.get(event_id)

    def get_person_by_id(self, person_id: str) -> Optional[Person]:
        return self.people.get(person_id)

    def get_geo_by_id(self, geo_id: str) -> Optional[Geography]:
        return self.geographies.get(geo_id)

    # List operations
    def list_events(self) -> List[Event]:
        return list(self.events.values())

    def list_people(self) -> List[Person]:
        return list(self.people.values())

    def list_geographies(self) -> List[Geography]:
        return list(self.geographies.values())

    # Pivot helpers
    def get_events_by_person(self, person_id: str) -> List[Event]:
        result = []
        for e in self.events.values():
            for rp in getattr(e, "related_people", []):
                if rp.person_id == person_id:
                    result.append(e)
                    break
        return result

    def get_people_by_event(self, event_id: str) -> List[Person]:
        e = self.get_event_by_id(event_id)
        if not e:
            return []
        result = []
        for rp in getattr(e, "related_people", []):
            p = self.get_person_by_id(rp.person_id)
            if p:
                result.append(p)
        return result

    def get_events_by_geo(self, geo_id: str) -> List[Event]:
        result = []
        for e in self.events.values():
            for loc in getattr(e, "locations", []):
                if loc.geography_id == geo_id:
                    result.append(e)
                    break
        return result

    def get_geos_by_event(self, event_id: str) -> List[Geography]:
        e = self.get_event_by_id(event_id)
        if not e:
            return []
        result = []
        for loc in getattr(e, "locations", []):
            g = self.get_geo_by_id(loc.geography_id)
            if g:
                result.append(g)
        return result

    # Generic pivot: from dimension -> to dimension
    def pivot(self, from_dim: str, to_dim: str, id_value: str):
        """Simple pivot dispatcher. from_dim/to_dim in {"events","people","geographies"}.
        Returns list of target entities.
        """
        mapping = {
            ("people", "events"): self.get_events_by_person,
            ("events", "people"): self.get_people_by_event,
            ("geographies", "events"): self.get_events_by_geo,
            ("events", "geographies"): self.get_geos_by_event,
        }
        fn = mapping.get((from_dim, to_dim))
        if not fn:
            return []
        return fn(id_value)
