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
        start_date=DateRange(start_date="2020-01-01", end_date=None),
        source_of_truth=None,
        conflict_notes=None,
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert event.id == "event_001"
    assert event.title == "Test Event"
    assert event.created_by == "test_user"
    # Verify claims structure exists
    assert isinstance(event.claims, dict)
    assert isinstance(event.labels, dict)


def test_person_creation():
    """Test creating a person."""
    person = Person(
        id="person_001",
        name="Albert Einstein",
        description="Theoretical physicist",
        birth_date=None,
        death_date=None,
        birth_location=None,
        death_location=None,
        source_of_truth=None,
        conflict_notes=None,
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert person.id == "person_001"
    assert person.name == "Albert Einstein"
    # Verify claims structure exists
    assert isinstance(person.claims, dict)
    assert isinstance(person.labels, dict)


def test_geography_creation():
    """Test creating a geography."""
    geography = Geography(
        id="geo_001",
        name="France",
        geography_type=GeographyType.COUNTRY,
        description="European nation",
        center_coordinate=None,
        boundaries=None,
        parent_geography_id=None,
        climate=None,
        geology=None,
        source_of_truth=None,
        conflict_notes=None,
        created_by="test_user",
        last_modified_by="test_user",
    )
    assert geography.id == "geo_001"
    assert geography.geography_type == GeographyType.COUNTRY
    # Verify claims structure exists
    assert isinstance(geography.claims, dict)
    assert isinstance(geography.labels, dict)


def test_dimension_creation():
    """Test creating a dimension."""
    dimension = Dimension(
        id="dim_001",
        name="Timeline",
        dimension_type=DimensionType.TIMELINE,
        description="Navigate by time",
        icon=None,
        color=None,
        zoom_levels=None,
        configuration=None,
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
        description=None,
        refresh_frequency=None,
        base_url=None,
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
        start_date=DateRange(start_date="1939-09-01", end_date=None),
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["title", "description"],
                external_id=None,
                url=None,
            ),
            SourceAttribution(
                source_id="bbc_history",
                source_name="BBC History",
                trust_level=0.85,
                fields_contributed=["dates", "key_figures"],
                external_id=None,
                url=None,
            ),
        ],
        source_of_truth=None,
        conflict_notes=None,
        created_by="data_importer",
        last_modified_by="data_importer",
    )
    assert len(event.sources) == 2
    assert event.sources[0].source_name == "Wikipedia"


def test_entity_with_claims():
    """Test entity with Wikidata-style claims."""
    from python_aws_starter.models.claims_utils import Property, create_time_claim
    
    person = Person(
        id="person_test",
        name="Test Person",
        description="A test person",
        created_by="test",
        last_modified_by="test",
        claims={
            Property.DATE_OF_BIRTH: [create_time_claim(Property.DATE_OF_BIRTH, "1990-01-01", precision=11)],
        },
        labels={"en": {"language": "en", "value": "Test Person"}},
    )
    
    assert person.get_label() == "Test Person"
    assert len(person.get_claims(Property.DATE_OF_BIRTH)) == 1
    assert person.get_computed_birth_date() == "1990-01-01"


def test_entity_claims_access():
    """Test accessing entity data through claims."""
    from python_aws_starter.models.claims_utils import Property, create_time_claim, create_coordinate_claim
    
    geography = Geography(
        id="geo_test",
        name="Test City",
        geography_type=GeographyType.CITY,
        description="A test city",
        created_by="test",
        last_modified_by="test",
        claims={
            Property.COORDINATE_LOCATION: [create_coordinate_claim(Property.COORDINATE_LOCATION, 40.7128, -74.0060)],
        },
        labels={"en": {"language": "en", "value": "Test City"}},
    )
    
    assert geography.get_label() == "Test City"
    coord = geography.get_computed_center_coordinate()
    assert coord is not None
    assert coord.latitude == 40.7128
    assert coord.longitude == -74.0060
