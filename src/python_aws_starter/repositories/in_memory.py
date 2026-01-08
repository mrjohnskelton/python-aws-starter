"""Simple in-memory repository to support pivot demos and tests."""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import math

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

    # Search / filter capabilities
    def _text_match(self, haystack: str, query: str) -> bool:
        return query.lower() in (haystack or "").lower()

    def _parse_date(self, d: Optional[str]) -> Optional[datetime]:
        if not d:
            return None
        try:
            return datetime.fromisoformat(d)
        except Exception:
            try:
                return datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                return None

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Returns distance in kilometers between two coords
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def search_events(
        self,
        text: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        geography_id: Optional[str] = None,
        center_coord: Optional[Tuple[float, float]] = None,
        within_km: Optional[float] = None,
    ) -> List[Event]:
        """Search events by text, date range (ISO strings), geography id, or proximity.

        - `text`: substring search against title, description, and related people names
        - `start_date`/`end_date`: filter events whose range overlaps given range
        - `geography_id`: event has a location with this geography id
        - `center_coord` + `within_km`: event has at least one location within distance
        """
        results: List[Event] = []
        s_dt = self._parse_date(start_date)
        e_dt = self._parse_date(end_date)

        for ev in self.events.values():
            # text filter
            if text:
                text_lower = text.lower()
                matched = False
                if ev.title and self._text_match(ev.title, text_lower):
                    matched = True
                if not matched and ev.description and self._text_match(ev.description, text_lower):
                    matched = True
                if not matched:
                    for rp in getattr(ev, "related_people", []):
                        if getattr(rp, "name", None) and self._text_match(rp.name, text_lower):
                            matched = True
                            break
                if not matched:
                    continue

            # geography id filter
            if geography_id:
                found_geo = False
                for loc in getattr(ev, "locations", []):
                    if getattr(loc, "geography_id", None) == geography_id:
                        found_geo = True
                        break
                if not found_geo:
                    continue

            # date range overlap filter
            if s_dt or e_dt:
                ev_start = self._parse_date(getattr(ev.start_date, "start_date", None))
                ev_end = None
                if getattr(ev, "end_date", None):
                    ev_end = self._parse_date(getattr(ev.end_date, "start_date", None))
                if not ev_end:
                    ev_end = ev_start
                # if parsing failed, skip date filtering
                if ev_start:
                    if s_dt and ev_end < s_dt:
                        continue
                    if e_dt and ev_start > e_dt:
                        continue

            # proximity filter
            if center_coord and within_km is not None:
                latc, lonc = center_coord
                close = False
                for loc in getattr(ev, "locations", []):
                    lat = getattr(loc, "latitude", None)
                    lon = getattr(loc, "longitude", None)
                    if lat is None or lon is None:
                        continue
                    dist = self._haversine_km(latc, lonc, lat, lon)
                    if dist <= within_km:
                        close = True
                        break
                if not close:
                    continue

            results.append(ev)

        return results

    def search_people(self, text: Optional[str] = None, related_event_id: Optional[str] = None) -> List[Person]:
        results: List[Person] = []
        for p in self.people.values():
            if text:
                if not (
                    self._text_match(p.name, text)
                    or self._text_match(getattr(p, "description", ""), text)
                    or any(self._text_match(o, text) for o in getattr(p, "occupations", []))
                ):
                    continue

            if related_event_id:
                # ensure person appears in event
                found = False
                ev = self.get_event_by_id(related_event_id)
                if ev:
                    for rp in getattr(ev, "related_people", []):
                        if rp.person_id == p.id:
                            found = True
                            break
                if not found:
                    continue

            results.append(p)
        return results

    def search_geographies(self, text: Optional[str] = None, center_coord: Optional[Tuple[float, float]] = None, within_km: Optional[float] = None) -> List[Geography]:
        results: List[Geography] = []
        for g in self.geographies.values():
            if text and not (
                self._text_match(g.name, text) or self._text_match(getattr(g, "description", ""), text)
            ):
                continue

            if center_coord and within_km is not None:
                latc, lonc = center_coord
                coord = getattr(g, "center_coordinate", None)
                if not coord or getattr(coord, "latitude", None) is None or getattr(coord, "longitude", None) is None:
                    continue
                dist = self._haversine_km(latc, lonc, coord.latitude, coord.longitude)
                if dist > within_km:
                    continue

            results.append(g)

        return results

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
