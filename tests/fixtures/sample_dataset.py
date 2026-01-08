"""Sample dataset for testing cross-dimensional pivots.

This file provides sample DataSource, Geography, Person and Event instances
that are interlinked to facilitate pivoting between dimensions.
"""
from datetime import datetime
from python_aws_starter.models.sources import DataSource, SourceType, SourceAttribution
from python_aws_starter.models.geography import Geography, GeographyType, Coordinate, TemporalGeography
from python_aws_starter.models.people import Person, OrganizationReference, PersonReference
from python_aws_starter.models.events import Event, DateRange, GeographicReference, PersonReference as EventPersonRef
from python_aws_starter.models.dimensions import Dimension, DimensionType, DimensionField

# Data sources
DATA_SOURCES = [
    DataSource(
        id="wikipedia",
        name="Wikipedia",
        source_type=SourceType.SCRAPED,
        trust_level=0.7,
        description="Public encyclopedia entries",
    ),
    DataSource(
        id="curated_internal",
        name="Curated Internal",
        source_type=SourceType.CURATED,
        trust_level=0.95,
        description="Provenance-controlled internal dataset",
    ),
    DataSource(
        id="user_submission",
        name="User Submission",
        source_type=SourceType.USER_GENERATED,
        trust_level=0.5,
        description="Contributions from power users pending review",
    ),
]

# Geographies (7 examples)
GEOGRAPHIES = [
    Geography(
        id="geo_europe",
        name="Europe",
        geography_type=GeographyType.CONTINENT,
        description="Continent of Europe",
        center_coordinate=Coordinate(latitude=54.5260, longitude=15.2551),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_france",
        name="France",
        geography_type=GeographyType.COUNTRY,
        description="France",
        parent_geography_id="geo_europe",
        center_coordinate=Coordinate(latitude=46.2276, longitude=2.2137),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_paris",
        name="Paris",
        geography_type=GeographyType.CITY,
        description="Capital of France",
        parent_geography_id="geo_france",
        center_coordinate=Coordinate(latitude=48.8566, longitude=2.3522),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_normandy",
        name="Normandy",
        geography_type=GeographyType.REGION,
        description="Region in northern France",
        parent_geography_id="geo_france",
        center_coordinate=Coordinate(latitude=49.1829, longitude=-0.3707),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_uk",
        name="United Kingdom",
        geography_type=GeographyType.COUNTRY,
        description="United Kingdom",
        parent_geography_id="geo_europe",
        center_coordinate=Coordinate(latitude=55.3781, longitude=-3.4360),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_waterloo",
        name="Waterloo",
        geography_type=GeographyType.VILLAGE,
        description="Site of the Battle of Waterloo (modern Belgium)",
        parent_geography_id="geo_europe",
        center_coordinate=Coordinate(latitude=50.6806, longitude=4.4128),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Geography(
        id="geo_rome",
        name="Rome",
        geography_type=GeographyType.CITY,
        description="Ancient and modern capital of Italy",
        parent_geography_id="geo_europe",
        center_coordinate=Coordinate(latitude=41.9028, longitude=12.4964),
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
]

# People (7 examples)
PEOPLE = [
    Person(
        id="person_napoleon",
        name="Napoleon Bonaparte",
        description="French military leader and emperor",
        birth_date="1769-08-15",
        death_date="1821-05-05",
        birth_location="Ajaccio, Corsica",
        occupations=["military leader", "emperor"],
        nationalities=["French"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_churchill",
        name="Winston Churchill",
        description="British Prime Minister during WWII",
        birth_date="1874-11-30",
        death_date="1965-01-24",
        occupations=["politician", "writer"],
        nationalities=["British"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_joan",
        name="Joan of Arc",
        description="French heroine and military leader",
        birth_date="1412-01-06",
        death_date="1431-05-30",
        occupations=["military leader"],
        nationalities=["French"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_caesar",
        name="Julius Caesar",
        description="Roman general and statesman",
        birth_date="100-07-13",
        death_date="44-03-15",
        occupations=["general", "politician"],
        nationalities=["Roman"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_lincoln",
        name="Abraham Lincoln",
        description="16th President of the United States",
        birth_date="1809-02-12",
        death_date="1865-04-15",
        occupations=["politician"],
        nationalities=["American"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_cleopatra",
        name="Cleopatra VII",
        description="Last active ruler of the Ptolemaic Kingdom of Egypt",
        birth_date="69-01-01",
        death_date="30-08-12",
        occupations=["ruler"],
        nationalities=["Egyptian"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Person(
        id="person_hitler",
        name="Adolf Hitler",
        description="Leader of Nazi Germany",
        birth_date="1889-04-20",
        death_date="1945-04-30",
        occupations=["politician"],
        nationalities=["Austrian", "German"],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
]

# Events (7 examples) with cross references to PEOPLE and GEOGRAPHIES
EVENTS = [
    Event(
        id="event_french_revolution",
        title="French Revolution",
        description="Period of radical social and political change in France (1789–1799)",
        start_date=DateRange(start_date="1789-05-05", end_date="1799-11-09", precision="year"),
        locations=[GeographicReference(geography_id="geo_france", name="France")],
        related_people=[EventPersonRef(person_id="person_napoleon", name="Napoleon Bonaparte", role="Rising Leader")],
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["title", "dates", "description"],
                url="https://en.wikipedia.org/wiki/French_Revolution",
            )
        ],
        confidence=0.85,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_waterloo",
        title="Battle of Waterloo",
        description="Decisive battle near Waterloo in 1815 ending Napoleon's rule.",
        start_date=DateRange(start_date="1815-06-18", precision="day"),
        locations=[GeographicReference(geography_id="geo_waterloo", name="Waterloo")],
        related_people=[EventPersonRef(person_id="person_napoleon", name="Napoleon Bonaparte", role="Commander")],
        sources=[
            SourceAttribution(
                source_id="curated_internal",
                source_name="Curated Internal",
                trust_level=0.95,
                fields_contributed=["title", "dates"],
            )
        ],
        confidence=0.9,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_wwii",
        title="World War II",
        description="Global war from 1939 to 1945",
        start_date=DateRange(start_date="1939-09-01", end_date="1945-09-02", precision="day"),
        locations=[GeographicReference(geography_id="geo_europe", name="Europe"), GeographicReference(geography_id="geo_uk", name="United Kingdom")],
        related_people=[
            EventPersonRef(person_id="person_churchill", name="Winston Churchill", role="Allied Leader"),
            EventPersonRef(person_id="person_hitler", name="Adolf Hitler", role="Axis Leader"),
        ],
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["dates", "overview"],
                url="https://en.wikipedia.org/wiki/World_War_II",
            )
        ],
        confidence=0.95,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_hastings",
        title="Battle of Hastings",
        description="1066 battle leading to Norman conquest of England",
        start_date=DateRange(start_date="1066-10-14", precision="day"),
        locations=[GeographicReference(geography_id="geo_uk", name="England")],
        related_people=[],
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["title", "dates"],
            )
        ],
        confidence=0.8,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_fall_rome",
        title="Fall of the Western Roman Empire",
        description="Traditional date for the fall of Rome in 476 CE",
        start_date=DateRange(start_date="0476-09-04", precision="year"),
        locations=[GeographicReference(geography_id="geo_rome", name="Rome")],
        related_people=[EventPersonRef(person_id="person_caesar", name="Julius Caesar", role="Ancient Precursor")],
        sources=[
            SourceAttribution(
                source_id="curated_internal",
                source_name="Curated Internal",
                trust_level=0.9,
                fields_contributed=["title", "dates"],
            )
        ],
        confidence=0.7,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_american_cw",
        title="American Civil War",
        description="Civil war in the United States (1861–1865)",
        start_date=DateRange(start_date="1861-04-12", end_date="1865-05-09", precision="day"),
        locations=[],
        related_people=[EventPersonRef(person_id="person_lincoln", name="Abraham Lincoln", role="President")],
        sources=[
            SourceAttribution(
                source_id="wikipedia",
                source_name="Wikipedia",
                trust_level=0.7,
                fields_contributed=["dates", "overview"],
            )
        ],
        confidence=0.9,
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Event(
        id="event_cleopatra",
        title="Reign of Cleopatra VII",
        description="Period during which Cleopatra VII ruled Egypt",
        start_date=DateRange(start_date="-51-01-01", end_date="-30-08-12", precision="year"),
        locations=[GeographicReference(geography_id="geo_rome", name="Rome")],
        related_people=[EventPersonRef(person_id="person_cleopatra", name="Cleopatra VII", role="Ruler")],
        sources=[
            SourceAttribution(
                source_id="user_submission",
                source_name="User Submission",
                trust_level=0.5,
                fields_contributed=["dates", "biography"],
            )
        ],
        confidence=0.6,
        created_by="sample_user",
        last_modified_by="sample_user",
    ),
]

# Dimensions (example entries to map UI dimensions)
DIMENSIONS = [
    Dimension(
        id="dim_timeline",
        name="Timeline",
        dimension_type=DimensionType.TIMELINE,
        description="Navigate historical events by time",
        fields=[DimensionField(name="start_date", display_name="Start Date", field_type="date")],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Dimension(
        id="dim_geography",
        name="Geography",
        dimension_type=DimensionType.GEOGRAPHY,
        description="Navigate entities by geographic location",
        fields=[DimensionField(name="location", display_name="Location", field_type="geography")],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
    Dimension(
        id="dim_people",
        name="People",
        dimension_type=DimensionType.PEOPLE,
        description="Navigate historical figures",
        fields=[DimensionField(name="name", display_name="Name", field_type="string")],
        created_by="sample_data",
        last_modified_by="sample_data",
    ),
]

# Helper accessors
def get_event_by_id(eid: str) -> Event:
    return next(e for e in EVENTS if e.id == eid)

def get_person_by_id(pid: str) -> Person:
    return next(p for p in PEOPLE if p.id == pid)

def get_geo_by_id(gid: str) -> Geography:
    return next(g for g in GEOGRAPHIES if g.id == gid)


# Convenience list getters for tests and demo usage
def get_events() -> list:
    return list(EVENTS)


def get_people() -> list:
    return list(PEOPLE)


def get_geographies() -> list:
    return list(GEOGRAPHIES)
