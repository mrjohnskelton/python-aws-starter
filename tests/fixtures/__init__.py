"""Test fixtures and sample data."""

import pytest
from datetime import datetime
from python_aws_starter.models.events import Event, DateRange
from python_aws_starter.models.people import Person
from python_aws_starter.models.geography import Geography, GeographyType, Coordinate
from python_aws_starter.models.sources import DataSource, SourceAttribution, SourceType


@pytest.fixture
def wikipedia_source():
    """Wikipedia data source."""
    return DataSource(
        id="wikipedia",
        name="Wikipedia",
        source_type=SourceType.SCRAPED,
        trust_level=0.7,
        description="Data scraped from Wikipedia",
    )


@pytest.fixture
def bbc_source():
    """BBC History data source."""
    return DataSource(
        id="bbc_history",
        name="BBC History",
        source_type=SourceType.CURATED,
        trust_level=0.9,
        description="Historical data from BBC",
    )


@pytest.fixture
def sample_event_wwii():
    """Sample World War II event."""
    return Event(
        id="event_wwii",
        title="World War II",
        description="Major global military conflict spanning 1939-1945",
        start_date=DateRange(start_date="1939-09-01", precision="day"),
        end_date=DateRange(start_date="1945-09-02", precision="day"),
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["title", "description"],
                url="https://en.wikipedia.org/wiki/World_War_II",
            )
        ],
        created_by="data_importer",
        last_modified_by="data_importer",
    )


@pytest.fixture
def sample_person_churchill():
    """Sample person: Winston Churchill."""
    return Person(
        id="person_churchill",
        name="Winston Churchill",
        birth_date="1874-11-30",
        death_date="1965-01-24",
        birth_location="Woodstock, England",
        description="British statesman and military officer",
        occupations=["politician", "military officer", "author"],
        nationalities=["British"],
        created_by="data_importer",
        last_modified_by="data_importer",
    )


@pytest.fixture
def sample_geography_uk():
    """Sample geography: United Kingdom."""
    return Geography(
        id="geo_uk",
        name="United Kingdom",
        geography_type=GeographyType.COUNTRY,
        description="Island nation in northwestern Europe",
        center_coordinate=Coordinate(latitude=55.3781, longitude=-3.4360),
        climate="temperate oceanic",
        created_by="data_importer",
        last_modified_by="data_importer",
    )


@pytest.fixture
def sample_geography_france():
    """Sample geography: France."""
    return Geography(
        id="geo_france",
        name="France",
        geography_type=GeographyType.COUNTRY,
        description="Western European nation",
        center_coordinate=Coordinate(latitude=46.2276, longitude=2.2137),
        parent_geography_id="geo_europe",
        climate="temperate",
        created_by="data_importer",
        last_modified_by="data_importer",
    )
