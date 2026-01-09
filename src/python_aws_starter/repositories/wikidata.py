"""Lightweight Wikidata-backed repository for demo searches.

This implements a minimal mapping from Wikidata search results and entity
JSON to the project's models. It is intentionally conservative: it fetches
labels, descriptions and basic claims (birth/death dates, coordinates) and
maps them to `Person`/`Geography`/`Event` objects for demo purposes.
"""
from typing import List, Optional, Tuple
import logging
import json
import requests

from python_aws_starter.models.people import Person
from python_aws_starter.models.events import Event, DateRange, GeographicReference, PersonReference
from python_aws_starter.models.geography import Geography, Coordinate
from python_aws_starter.config import config


logger = logging.getLogger("python_aws_starter.repositories.wikidata")


class WikidataRepository:
    def __init__(self, base_url: str, entity_url: str, limit: int = 10):
        self.base_url = base_url
        self.entity_url = entity_url
        self.limit = limit

    def _search_entities(self, text: str, limit: Optional[int] = None) -> List[dict]:
        if not text:
            return []
        params = {
            "action": "wbsearchentities",
            "search": text,
            "language": "en",
            "format": "json",
            "type": "item",
            "limit": limit or self.limit,
        }
        try:
            logger.debug("[wikidata] search -> url=%s params=%s", self.base_url, params)
            r = requests.get(self.base_url, params=params, timeout=10)
            logger.debug("[wikidata] response status=%s", r.status_code)
            r.raise_for_status()
            # attempt to capture and log a small portion of the body for debugging
            if config.wikidata_log_body:
                try:
                    text = r.text
                    logger.debug("[wikidata] response body (truncated): %s", text[:config.wikidata_log_body_max])
                except Exception:
                    logger.debug("[wikidata] response body not available as text")
            data = r.json()
            logger.debug("[wikidata] response keys=%s", list(data.keys()) if isinstance(data, dict) else None)
            return data.get("search", [])
        except Exception as e:
            logger.exception("[wikidata] search error: %s", e)
            return []

    def _fetch_entity(self, qid: str) -> Optional[dict]:
        if not qid:
            return None
        # Entity dumps are available at Special:EntityData/QID.json
        try:
            url = f"{self.entity_url}{qid}.json"
            logger.debug("[wikidata] fetch entity -> url=%s", url)
            r = requests.get(url, timeout=10)
            logger.debug("[wikidata] entity response status=%s", r.status_code)
            r.raise_for_status()
            if config.wikidata_log_body:
                try:
                    text = r.text
                    logger.debug("[wikidata] entity response body (truncated): %s", text[:config.wikidata_log_body_max])
                except Exception:
                    logger.debug("[wikidata] entity response body not available as text")
            j = r.json()
            logger.debug("[wikidata] entity keys=%s", list(j.keys()) if isinstance(j, dict) else None)
            return j.get("entities", {}).get(qid)
        except Exception:
            logger.exception("[wikidata] fetch entity error for %s", qid)
            return None

    def _parse_time(self, time_str: Optional[str]) -> Optional[str]:
        # Wikidata time strings look like '+1769-08-15T00:00:00Z'
        if not time_str:
            return None
        try:
            return time_str.lstrip("+").split("T")[0]
        except Exception:
            return None

    def _entity_to_person(self, entity: dict, search_hit: dict) -> Person:
        qid = entity.get("id") or search_hit.get("id")
        label = (entity.get("labels", {}) or {}).get("en", {}).get("value") or search_hit.get("label")
        desc = (entity.get("descriptions", {}) or {}).get("en", {}).get("value") or search_hit.get("description") or ""

        birth = None
        death = None
        claims = entity.get("claims", {}) if entity else {}
        if "P569" in claims:
            try:
                birth = self._parse_time(claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"])
            except Exception:
                birth = None
        if "P570" in claims:
            try:
                death = self._parse_time(claims["P570"][0]["mainsnak"]["datavalue"]["value"]["time"])
            except Exception:
                death = None

        person = Person(
            id=f"wikidata_{qid}",
            name=label or qid,
            birth_date=birth,
            death_date=death,
            birth_location=None,
            death_location=None,
            description=desc or "",
            occupations=[],
            nationalities=[],
            related_people=[],
            organizations=[],
            sources=[{"source": "wikidata", "url": f"{self.entity_url}{qid}"}],
            confidence=0.6,
        )
        return person

    def _entity_to_geography(self, entity: dict, search_hit: dict) -> Geography:
        qid = entity.get("id") or search_hit.get("id")
        label = (entity.get("labels", {}) or {}).get("en", {}).get("value") or search_hit.get("label")
        desc = (entity.get("descriptions", {}) or {}).get("en", {}).get("value") or search_hit.get("description") or ""

        coord = None
        claims = entity.get("claims", {}) if entity else {}
        if "P625" in claims:
            try:
                val = claims["P625"][0]["mainsnak"]["datavalue"]["value"]
                coord = Coordinate(latitude=val.get("latitude"), longitude=val.get("longitude"))
            except Exception:
                coord = None

        geo = Geography(
            id=f"wikidata_{qid}",
            name=label or qid,
            geography_type="other",
            alternate_names=[],
            description=desc or "",
            center_coordinate=coord,
            boundaries=None,
            parent_geography_id=None,
            child_geographies=[],
            temporal_variants=[],
            climate=None,
            geology=None,
            sources=[{"source": "wikidata", "url": f"{self.entity_url}{qid}"}],
            confidence=0.6,
        )
        return geo

    def _entity_to_event(self, entity: dict, search_hit: dict) -> Event:
        qid = entity.get("id") or search_hit.get("id")
        label = (entity.get("labels", {}) or {}).get("en", {}).get("value") or search_hit.get("label")
        desc = (entity.get("descriptions", {}) or {}).get("en", {}).get("value") or search_hit.get("description") or ""

        # Attempt to parse start/end if available (very best-effort)
        claims = entity.get("claims", {}) if entity else {}
        start = None
        end = None
        if "P580" in claims:  # start time
            try:
                start = self._parse_time(claims["P580"][0]["mainsnak"]["datavalue"]["value"]["time"])
            except Exception:
                start = None
        if "P582" in claims:  # end time
            try:
                end = self._parse_time(claims["P582"][0]["mainsnak"]["datavalue"]["value"]["time"])
            except Exception:
                end = None

        date_range = DateRange(start_date=start or "", end_date=end or None)

        evt = Event(
            id=f"wikidata_{qid}",
            title=label or qid,
            description=desc or "",
            start_date=date_range,
            end_date=None if not end else DateRange(start_date=end),
            locations=[],
            related_people=[],
            sources=[{"source": "wikidata", "url": f"{self.entity_url}{qid}"}],
            confidence=0.5,
        )
        return evt

    # Public API used by the FastAPI app
    def search_people(self, text: Optional[str] = None, related_event_id: Optional[str] = None) -> List[Person]:
        hits = self._search_entities(text, limit=self.limit)
        out: List[Person] = []
        for h in hits:
            qid = h.get("id")
            ent = self._fetch_entity(qid) or {}
            try:
                out.append(self._entity_to_person(ent, h))
            except Exception:
                continue
        return out

    def search_geographies(self, text: Optional[str] = None, center_coord: Optional[Tuple[float, float]] = None, within_km: Optional[float] = None) -> List[Geography]:
        hits = self._search_entities(text, limit=self.limit)
        out: List[Geography] = []
        for h in hits:
            qid = h.get("id")
            ent = self._fetch_entity(qid) or {}
            try:
                out.append(self._entity_to_geography(ent, h))
            except Exception:
                continue
        return out

    def search_events(self, text: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, geography_id: Optional[str] = None, center_coord: Optional[Tuple[float, float]] = None, within_km: Optional[float] = None) -> List[Event]:
        hits = self._search_entities(text, limit=self.limit)
        out: List[Event] = []
        for h in hits:
            qid = h.get("id")
            ent = self._fetch_entity(qid) or {}
            try:
                out.append(self._entity_to_event(ent, h))
            except Exception:
                continue
        return out

    # Pivot operations are not supported against Wikidata in this simple demo.
    def pivot(self, from_dim: str, to_dim: str, id_value: str):
        return []
