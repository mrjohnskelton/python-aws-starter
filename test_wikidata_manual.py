#!/usr/bin/env python3
"""Manual test script for Wikidata functionality."""

import sys
import os

# Temporarily modify sys.path to avoid import issues
sys.path.insert(0, 'src')

# Mock pytest to avoid import errors
class MockPytest:
    def fixture(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Replace pytest in sys.modules before any imports
sys.modules['pytest'] = MockPytest()

# Now import
from python_aws_starter.utils.wikidata import (
    search_wikidata_people,
    search_wikidata_events,
    search_wikidata_geographies
)
from python_aws_starter.models.claims_utils import Property

print("=" * 60)
print("Testing Wikidata Integration")
print("=" * 60)

# Test 1: Search for Napoleon
print("\n1. Searching for Napoleon...")
people = search_wikidata_people("Napoleon", limit=5)
print(f"   Found {len(people)} people")
if people:
    napoleon = None
    for person in people:
        if "napoleon" in person.name.lower() and "bonaparte" in person.name.lower():
            napoleon = person
            break
    
    if napoleon:
        print(f"   ✓ Found Napoleon: {napoleon.name}")
        print(f"   ID: {napoleon.id}")
        print(f"   Label: {napoleon.get_label()}")
        print(f"   Description: {napoleon.get_description()[:80]}...")
        
        # Check claims
        birth_date = napoleon.get_computed_birth_date()
        death_date = napoleon.get_computed_death_date()
        print(f"   Birth Date: {birth_date}")
        print(f"   Death Date: {death_date}")
        
        # Check claims structure
        birth_claims = napoleon.get_claims(Property.DATE_OF_BIRTH)
        print(f"   Birth Date Claims: {len(birth_claims)}")
        if birth_claims:
            claim = birth_claims[0]
            print(f"   Claim Property: {claim.mainsnak.property}")
            print(f"   Claim Type: {claim.mainsnak.datavalue.type if claim.mainsnak.datavalue else 'None'}")
    else:
        print(f"   First result: {people[0].name}")

# Test 2: Search for Waterloo
print("\n2. Searching for Waterloo...")
events = search_wikidata_events("Waterloo", limit=5)
print(f"   Found {len(events)} events")
if events:
    waterloo = events[0]
    print(f"   ✓ Found: {waterloo.title}")
    print(f"   ID: {waterloo.id}")
    print(f"   Label: {waterloo.get_label()}")
    print(f"   Description: {waterloo.get_description()[:80]}...")
    
    start_date = waterloo.get_computed_start_date()
    print(f"   Start Date: {start_date.start_date if start_date else 'None'}")

# Test 3: Search for France
print("\n3. Searching for France...")
geographies = search_wikidata_geographies("France", limit=5)
print(f"   Found {len(geographies)} geographies")
if geographies:
    france = geographies[0]
    print(f"   ✓ Found: {france.name}")
    print(f"   ID: {france.id}")
    print(f"   Label: {france.get_label()}")
    print(f"   Description: {france.get_description()[:80]}...")
    
    coord = france.get_computed_center_coordinate()
    if coord:
        print(f"   Coordinates: {coord.latitude}, {coord.longitude}")
    else:
        print(f"   Coordinates: Not available")

print("\n" + "=" * 60)
print("Tests Complete!")
print("=" * 60)
