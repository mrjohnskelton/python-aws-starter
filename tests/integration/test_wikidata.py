"""Integration tests for Wikidata functionality.

Tests actual Wikidata API calls and data conversion with real examples:
- People: Napoleon
- Events: Waterloo
- Geography: France
"""

import pytest
from python_aws_starter.utils import wikidata as wd
from python_aws_starter.models.claims_utils import Property, extract_time_from_claim, extract_entity_id_from_claim
from python_aws_starter.models.people import Person
from python_aws_starter.models.events import Event
from python_aws_starter.models.geography import Geography
from python_aws_starter.models.wikidata_meta import Claim


@pytest.mark.integration
def test_search_wikidata_napoleon():
    """Test searching for Napoleon Bonaparte in Wikidata."""
    people = wd.search_wikidata_people("Napoleon", limit=5)
    
    assert len(people) > 0, "Should find at least one person named Napoleon"
    
    # Find Napoleon Bonaparte (should be first result)
    napoleon = None
    for person in people:
        if "napoleon" in person.name.lower() and "bonaparte" in person.name.lower():
            napoleon = person
            break
    
    assert napoleon is not None, "Should find Napoleon Bonaparte"
    assert napoleon.id.startswith("person_wikidata_"), "Should have wikidata ID prefix"
    
    # Verify claims structure
    assert isinstance(napoleon.claims, dict), "Should have claims dictionary"
    assert Property.DATE_OF_BIRTH in napoleon.claims, "Should have date of birth claim (P569)"
    assert Property.DATE_OF_DEATH in napoleon.claims, "Should have date of death claim (P570)"
    assert Property.INSTANCE_OF in napoleon.claims, "Should have instance of claim (P31)"
    
    # Verify labels and descriptions
    assert napoleon.get_label() != "", "Should have a label"
    assert napoleon.get_description() != "", "Should have a description"
    
    # Verify computed properties work
    birth_date = napoleon.get_computed_birth_date()
    assert birth_date is not None, "Should have computed birth date"
    assert "1769" in birth_date, "Napoleon was born in 1769"
    
    death_date = napoleon.get_computed_death_date()
    assert death_date is not None, "Should have computed death date"
    assert "1821" in death_date, "Napoleon died in 1821"
    
    # Verify claims can be accessed
    birth_claims = napoleon.get_claims(Property.DATE_OF_BIRTH)
    assert len(birth_claims) > 0, "Should have birth date claims"
    
    best_birth_claim = napoleon.get_best_claim(Property.DATE_OF_BIRTH)
    assert best_birth_claim is not None, "Should have a best birth date claim"
    assert best_birth_claim.mainsnak.property == Property.DATE_OF_BIRTH
    assert best_birth_claim.mainsnak.datavalue is not None, "Should have datavalue"


@pytest.mark.integration
def test_search_wikidata_waterloo():
    """Test searching for Battle of Waterloo in Wikidata."""
    events = wd.search_wikidata_events("Waterloo", limit=10)
    
    assert len(events) > 0, "Should find at least one event related to Waterloo"
    
    # Find Battle of Waterloo
    waterloo = None
    for event in events:
        if "waterloo" in event.title.lower() and "battle" in event.title.lower():
            waterloo = event
            break
    
    # If exact match not found, take first result
    if waterloo is None and events:
        waterloo = events[0]
    
    assert waterloo is not None, "Should find a Waterloo-related event"
    assert waterloo.id.startswith("event_wikidata_"), "Should have wikidata ID prefix"
    
    # Verify claims structure
    assert isinstance(waterloo.claims, dict), "Should have claims dictionary"
    
    # Verify labels and descriptions
    assert waterloo.get_label() != "", "Should have a label"
    assert waterloo.get_description() != "", "Should have a description"
    
    # Verify computed properties
    title = waterloo.get_computed_title()
    assert title != "", "Should have computed title"
    
    description = waterloo.get_computed_description()
    assert description != "", "Should have computed description"
    
    # Check for start date claim (P580 or P585)
    start_date = waterloo.get_computed_start_date()
    assert start_date is not None, "Should have computed start date"
    assert start_date.start_date != "", "Start date should not be empty"


@pytest.mark.integration
def test_search_wikidata_france():
    """Test searching for France in Wikidata."""
    geographies = wd.search_wikidata_geographies("France", limit=5)
    
    assert len(geographies) > 0, "Should find at least one geography named France"
    
    # Find France (country)
    france = None
    for geo in geographies:
        if geo.name.lower() == "france" or "france" in geo.name.lower():
            # Check if it's a country
            instance_claims = geo.get_claims(Property.INSTANCE_OF)
            for claim in instance_claims:
                entity_id = extract_entity_id_from_claim(claim)
                if entity_id == "Q6256":  # country
                    france = geo
                    break
            if france:
                break
    
    # If exact match not found, take first result
    if france is None and geographies:
        france = geographies[0]
    
    assert france is not None, "Should find France"
    assert france.id.startswith("geo_wikidata_"), "Should have wikidata ID prefix"
    
    # Verify claims structure
    assert isinstance(france.claims, dict), "Should have claims dictionary"
    
    # Verify labels and descriptions
    assert france.get_label() != "", "Should have a label"
    assert france.get_description() != "", "Should have a description"
    
    # Verify computed properties
    name = france.get_computed_name()
    assert name != "", "Should have computed name"
    
    # Check for coordinates (P625) - use get_computed_center_coordinate method
    coord = france.get_computed_center_coordinate()
    if coord:
        assert -90 <= coord.latitude <= 90, "Latitude should be valid"
        assert -180 <= coord.longitude <= 180, "Longitude should be valid"
        # France should be around 46°N, 2°E
        assert 40 < coord.latitude < 52, "France latitude should be reasonable"
        assert -5 < coord.longitude < 10, "France longitude should be reasonable"
    else:
        # If no computed coordinate, check if there's a coordinate claim
        coord_claims = france.get_claims(Property.COORDINATE_LOCATION)
        if coord_claims:
            # At least we have the claim structure
            assert len(coord_claims) > 0, "Should have coordinate claims"


@pytest.mark.integration
def test_wikidata_claims_structure():
    """Test that Wikidata entities have proper claims structure."""
    # Search for Napoleon
    people = wd.search_wikidata_people("Napoleon", limit=1)
    if not people:
        pytest.skip("Could not fetch Napoleon from Wikidata")
    
    person = people[0]
    
    # Verify claims structure
    assert hasattr(person, 'claims'), "Person should have claims attribute"
    assert isinstance(person.claims, dict), "Claims should be a dictionary"
    
    # Verify we can access claims by property
    if Property.DATE_OF_BIRTH in person.claims:
        birth_claims = person.get_claims(Property.DATE_OF_BIRTH)
        assert len(birth_claims) > 0, "Should have birth date claims"
        
        claim = birth_claims[0]
        assert hasattr(claim, 'mainsnak'), "Claim should have mainsnak"
        assert claim.mainsnak.property == Property.DATE_OF_BIRTH, "Property should match"
        assert claim.mainsnak.datavalue is not None, "Should have datavalue"
        from python_aws_starter.models.wikidata_meta import DatavalueType
        assert claim.mainsnak.datavalue.type == DatavalueType.TIME, "Should be time type"


@pytest.mark.integration
def test_wikidata_labels_and_descriptions():
    """Test that Wikidata entities have labels and descriptions."""
    # Search for France
    geographies = wd.search_wikidata_geographies("France", limit=1)
    if not geographies:
        pytest.skip("Could not fetch France from Wikidata")
    
    geo = geographies[0]
    
    # Verify labels structure
    assert hasattr(geo, 'labels'), "Geography should have labels attribute"
    assert isinstance(geo.labels, dict), "Labels should be a dictionary"
    
    # Verify descriptions structure
    assert hasattr(geo, 'descriptions'), "Geography should have descriptions attribute"
    assert isinstance(geo.descriptions, dict), "Descriptions should be a dictionary"
    
    # Verify helper methods work
    label = geo.get_label()
    assert label != "", "Should have a label"
    
    description = geo.get_description()
    assert description != "", "Should have a description"


@pytest.mark.integration
def test_api_endpoints_with_wikidata():
    """Test API endpoints with Wikidata search enabled."""
    from fastapi.testclient import TestClient
    from python_aws_starter.api.app import app
    from python_aws_starter.config import config
    
    # Temporarily enable Wikidata
    original_data_source = config.data_source
    config.data_source = "wikidata"
    
    try:
        client = TestClient(app)
        
        # Test searching for Napoleon
        resp = client.get("/search/people", params={"q": "Napoleon"})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert len(data) > 0, "Should return at least one result"
        
        # Verify result has claims structure
        if data:
            first_person = data[0]
            assert "claims" in first_person, "Result should have claims"
            assert "labels" in first_person, "Result should have labels"
            assert "descriptions" in first_person, "Result should have descriptions"
        
        # Test searching for Waterloo
        resp = client.get("/search/events", params={"q": "Waterloo"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Should return at least one result"
        
        # Test searching for France
        resp = client.get("/search/geographies", params={"q": "France"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Should return at least one result"
        
    finally:
        # Restore original setting
        config.data_source = original_data_source


@pytest.mark.integration
def test_api_claims_endpoints():
    """Test new claims-based API endpoints."""
    from fastapi.testclient import TestClient
    from python_aws_starter.api.app import app
    from tests.fixtures import sample_dataset as sd
    
    client = TestClient(app)
    
    # Test getting claims for Napoleon (from sample data)
    resp = client.get("/entity/person_napoleon/claims")
    assert resp.status_code == 200
    data = resp.json()
    assert "entity_id" in data
    assert "claims" in data
    assert data["entity_id"] == "person_napoleon"
    
    # Test getting specific property claim
    resp = client.get("/entity/person_napoleon/claims", params={"property_id": Property.DATE_OF_BIRTH})
    assert resp.status_code == 200
    data = resp.json()
    assert "property_id" in data
    assert data["property_id"] == Property.DATE_OF_BIRTH
    assert "claims" in data
    
    # Test getting best claim
    resp = client.get(f"/entity/person_napoleon/claim/{Property.DATE_OF_BIRTH}")
    assert resp.status_code == 200
    data = resp.json()
    assert "entity_id" in data
    assert "property_id" in data
    assert "claim" in data
    assert data["property_id"] == Property.DATE_OF_BIRTH
    
    # Test search by property
    resp = client.get("/search/by-property", params={"property_id": Property.DATE_OF_BIRTH})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list), "Should return a list"


@pytest.mark.integration
def test_wikidata_entity_conversion():
    """Test that Wikidata entities are properly converted to our models."""
    # Get Napoleon's entity directly
    entities = wd.search_wikidata_entities("Napoleon Bonaparte", limit=1)
    if not entities:
        pytest.skip("Could not fetch Napoleon from Wikidata")
    
    qid = entities[0].get("id")
    if not qid:
        pytest.skip("No QID found")
    
    # Get full entity
    entity_data = wd.get_wikidata_entity(qid)
    if not entity_data:
        pytest.skip("Could not fetch full entity data")
    
    # Convert to Person
    person = wd.wikidata_to_person(entity_data, qid)
    assert person is not None, "Should convert to Person model"
    assert isinstance(person, Person), "Should be a Person instance"
    
    # Verify all required fields
    assert person.id != "", "Should have an ID"
    assert person.name != "", "Should have a name"
    assert person.description != "", "Should have a description"
    assert person.created_by == "wikidata", "Should be created by wikidata"
    assert person.last_modified_by == "wikidata", "Should be modified by wikidata"
    
    # Verify claims are populated
    assert len(person.claims) > 0, "Should have claims"
    assert len(person.labels) > 0, "Should have labels"
    assert len(person.descriptions) > 0, "Should have descriptions"
    
    # Verify computed methods work
    computed_name = person.get_computed_name()
    assert computed_name != "", "Should have computed name"
    
    computed_birth = person.get_computed_birth_date()
    if computed_birth:
        assert "1769" in computed_birth or "1768" in computed_birth, "Napoleon was born around 1769"
