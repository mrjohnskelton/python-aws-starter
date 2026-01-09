# Functional Requirements

This directory contains the detailed functional requirements for the timeline application.

## Overview

The solution creates a highly-interactive visual timeline of historical and geographical events, enabling users to explore data across multiple dimensions with seamless pivoting and zooming capabilities.

## Core Capabilities

1. **[Multi-Dimensional Navigation](./multi-dimensional-navigation.md)** - View and pivot between dimensions (timeline, geography, people, events)
2. **[Zoom Functionality](./zoom-functionality.md)** - Navigate data hierarchies within each dimension
3. **[Data Sourcing](./data-sourcing.md)** - Integrate data from multiple sources (curated, user-generated, scraped)
4. **[User Contributions](./user-contributions.md)** - Enable power users to submit and manage data
5. **Entity Detail Panel** - Display comprehensive Wikidata entity details when a card is selected, including labels, descriptions, aliases, claims, and Wikipedia links

## Key Features

### Dimensional Pivoting
Users can answer questions like:
- "Which historical events affected France over time?"
- "What else happened in this region at different times?"
- "What did Napoleon do across geography and time?"
- "How did front-lines change during World War I?"

### Hierarchical Zoom
Users can navigate at different levels of detail:
- **Timeline**: From geological ages to milliseconds
- **Geography**: From villages to planetary scale
- **People**: From individuals to entire civilizations
- **Events**: From individual events to eras

### Random Entity Discovery
On initial page load, the frontend automatically displays a random person entity from Wikidata:
- **Person Filtering**: Uses SPARQL query with `instance_of=Q5` filter to only return human/person entities
- **Immediate Engagement**: Prevents blank initial state by showing a person entity immediately
- **Consistent Experience**: Users always start with a person entity, making the initial experience more predictable and relevant

### Entity Detail Panel
When a user selects a card from the search results, a detail panel appears below the list showing:
- **Full Entity Information**: Complete Wikidata entity data fetched via `/wikidata/entity/{qid}` endpoint
- **Multi-language Support**: Labels, descriptions, and aliases in all available languages
- **Property Claims**: Key Wikidata properties (P-codes) with their values (dates, coordinates, entity references, etc.)
- **Wikipedia Links**: Direct links to Wikipedia articles in all available languages
- **Structured Display**: Organized sections for easy reading and navigation
- **External Links**: Clickable links to Wikidata and Wikipedia pages

The detail panel automatically fetches full entity data when a Wikidata entity (QID) is detected, providing rich context beyond the lightweight search results.

### Synchronized Visualizations
When a user selects a different card, both the timeline and map visualizations automatically update to reflect the selected card's content:

- **Timeline Updates**: 
  - Extracts start/end dates from Wikidata claims using property synonyms or traditional fields
  - Highlights the selected card's date range on the timeline with enhanced visual styling
  - Updates immediately when selection changes

- **Map Updates**:
  - Extracts coordinates from Wikidata claims (P625 for geographies) or location references
  - Highlights the selected card's location with a larger, more prominent pin
  - Supports multiple coordinate sources: claims, computed_center_coordinate, center_coordinate, or locations array
  - Updates immediately when selection changes

- **Real-time Synchronization**: Both visualizations update simultaneously when a card is selected, providing immediate visual feedback and context about the selected entity's temporal and geographic position.

### Date Property Synonyms
The system recognizes multiple Wikidata properties as synonyms for start and end dates, enabling comprehensive timeline operations across different entity types:

- **Configuration-Based**: Date property synonyms are defined in a centralized configuration file (`property_synonyms.py`), making it easy to add or modify recognized date properties
- **Start Date Synonyms**: The system recognizes multiple properties as start dates:
  - P571 (Inception), P1619 (Date of official opening), P569 (Birth date), P580 (Start time), P585 (Point in time), P1319 (Earliest date), P2031 (Work period start), P1249 (Time of earliest written record)
- **End Date Synonyms**: The system recognizes multiple properties as end dates:
  - P570 (Death date), P582 (End time), P576 (Dissolved), P2669 (Terminated), P1326 (Latest date), P2032 (Work period end)
- **Flexible Timeline Operations**: This synonym system enables:
  - Overlaying shared timelines across different entity types (people, events, organizations, etc.)
  - Jumping from one item to another based on overlapping or adjoining timeframes
  - Consistent date extraction regardless of entity type (e.g., Jurassic Age start/end dates work the same as person birth/death dates)
- **Extensibility**: The configuration file can be extended with additional property synonyms for other use cases in the future

## Related Documentation

- [Architecture Decision Records](../decisions/)
- [Data Models](../architecture/data-models.md)
- [API Design](../architecture/api-design.md)
