"""Test initialization and common test utilities."""

import pytest


@pytest.fixture
def sample_event():
    """Sample event for testing."""
    from python_aws_starter.models.events import Event, DateRange

    return Event(
        id="test_event_001",
        title="Test Event",
        description="A test event",
        start_date=DateRange(start_date="2000-01-01", end_date=None),
        source_of_truth=None,
        conflict_notes=None,
        created_by="test",
        last_modified_by="test",
    )


@pytest.fixture
def sample_person():
    """Sample person for testing."""
    from python_aws_starter.models.people import Person

    return Person(
        id="test_person_001",
        name="Test Person",
        description="A test person",
        birth_date=None,
        death_date=None,
        birth_location=None,
        death_location=None,
        source_of_truth=None,
        conflict_notes=None,
        created_by="test",
        last_modified_by="test",
    )


@pytest.fixture
def sample_geography():
    """Sample geography for testing."""
    from python_aws_starter.models.geography import Geography, GeographyType

    return Geography(
        id="test_geo_001",
        name="Test Location",
        geography_type=GeographyType.CITY,
        description="A test location",
        center_coordinate=None,
        boundaries=None,
        parent_geography_id=None,
        climate=None,
        geology=None,
        source_of_truth=None,
        conflict_notes=None,
        created_by="test",
        last_modified_by="test",
    )
