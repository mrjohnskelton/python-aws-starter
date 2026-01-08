"""Unit tests for data models."""

import pytest
from python_aws_starter.models.events import Event, DateRange
from python_aws_starter.models.people import Person
from python_aws_starter.models.geography import Geography, GeographyType
from python_aws_starter.models.dimensions import Dimension, DimensionType
from python_aws_starter.models.sources import DataSource, SourceType
from python_aws_starter.models.contributions import UserContribution, ContributionType


def test_event_creation():
    """Test creating an event."""
    event = Event(
        id="event_001",
        title="Test Event",
        description="A test event for validation",
        start_date=DateRange(start_date="2020-01-01"),
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert event.id == "event_001"
    assert event.title == "Test Event"
    assert event.created_by == "test_user"


def test_person_creation():
    """Test creating a person."""
    person = Person(
        id="person_001",
        name="Albert Einstein",
        description="Theoretical physicist",
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert person.id == "person_001"
    assert person.name == "Albert Einstein"


def test_geography_creation():
    """Test creating a geography."""
    geography = Geography(
        id="geo_001",
        name="France",
        geography_type=GeographyType.COUNTRY,
        description="European nation",
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert geography.id == "geo_001"
    assert geography.geography_type == GeographyType.COUNTRY


def test_dimension_creation():
    """Test creating a dimension."""
    dimension = Dimension(
        id="dim_001",
        name="Timeline",
        dimension_type=DimensionType.TIMELINE,
        description="Navigate by time",
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert dimension.name == "Timeline"
    assert dimension.dimension_type == DimensionType.TIMELINE


def test_data_source_creation():
    """Test creating a data source."""
    source = DataSource(
        id="source_wikipedia",
        name="Wikipedia",
        source_type=SourceType.SCRAPED,
        trust_level=0.7,
    )
    assert source.name == "Wikipedia"
    assert 0 <= source.trust_level <= 1


def test_event_with_multi_source():
    """Test event with multiple sources."""
    from python_aws_starter.models.sources import SourceAttribution

    event = Event(
        id="event_001",
        title="World War II",
        description="Major global conflict",
        start_date=DateRange(start_date="1939-09-01"),
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["title", "description"],
            ),
            SourceAttribution(
                source_id="bbc_history",
                source_name="BBC History",
                trust_level=0.85,
                fields_contributed=["dates", "key_figures"],
            ),
        ],
        created_by="data_importer",
        last_modified_by="data_importer",
    )
    assert len(event.sources) == 2
    assert event.sources[0].source_name == "Wikipedia"
