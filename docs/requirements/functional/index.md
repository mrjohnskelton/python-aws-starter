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

### Entity Detail Panel
When a user selects a card from the search results, a detail panel appears below the list showing:
- **Full Entity Information**: Complete Wikidata entity data fetched via `/wikidata/entity/{qid}` endpoint
- **Multi-language Support**: Labels, descriptions, and aliases in all available languages
- **Property Claims**: Key Wikidata properties (P-codes) with their values (dates, coordinates, entity references, etc.)
- **Wikipedia Links**: Direct links to Wikipedia articles in all available languages
- **Structured Display**: Organized sections for easy reading and navigation
- **External Links**: Clickable links to Wikidata and Wikipedia pages

The detail panel automatically fetches full entity data when a Wikidata entity (QID) is detected, providing rich context beyond the lightweight search results.

## Related Documentation

- [Architecture Decision Records](../decisions/)
- [Data Models](../architecture/data-models.md)
- [API Design](../architecture/api-design.md)
