# Project Requirements

This is an index of all project requirements. Detailed requirements are organized in the `docs/requirements/` directory.

## Quick Links

### Functional Requirements
- [Overview](docs/requirements/functional/index.md)
- [Multi-Dimensional Navigation](docs/requirements/functional/multi-dimensional-navigation.md)
- [Zoom Functionality](docs/requirements/functional/zoom-functionality.md)
- [Data Sourcing](docs/requirements/functional/data-sourcing.md)
- [User Contributions](docs/requirements/functional/user-contributions.md)

### Non-Functional Requirements
- [Overview](docs/requirements/non-functional/index.md)
- [User Experience](docs/requirements/non-functional/user-experience.md)
- [Performance](docs/requirements/non-functional/performance.md)
- [Browser Compatibility](docs/requirements/non-functional/browser-compatibility.md)
- [Technical Standards](docs/requirements/non-functional/technical-standards.md)
- [Scalability](docs/requirements/non-functional/scalability.md)
- [Security](docs/requirements/non-functional/security.md)

### Infrastructure
- [Infrastructure Requirements](docs/requirements/infrastructure.md)
- [Acceptance Criteria](docs/requirements/acceptance-criteria.md)

### Architecture & Decisions
- [Architecture Decision Records](docs/decisions/)

## Project Overview

The **Timeline Application** is a highly-interactive visual interface for exploring historical and geographical events across multiple dimensions (time, geography, people, events). Users can seamlessly pivot between dimensions, zoom to different levels of detail, and explore data from multiple curated, public, and user-contributed sources.

### Key Capabilities

1. **Multi-Dimensional Pivoting**: Navigate and pivot between timeline, geography, people, and events dimensions
2. **Hierarchical Zoom**: Explore data at different scales (from geological ages to milliseconds, villages to planetary)
3. **Multi-Source Integration**: Combine data from curated sources, public data, and user submissions
4. **User Contributions**: Enable power users to submit corrections and new data with a review workflow
5. **Random Entity Discovery**: Frontend automatically loads a random person entity (filtered by instance of Q5/human) from Wikidata on initial page load to provide immediate engagement with relevant content
6. **Entity Detail Panel**: Comprehensive detail view showing full Wikidata entity information (labels, descriptions, claims, Wikipedia links) when a card is selected

## Development Standards

- **Python**: 3.8+
- **Testing**: pytest (target ≥80% coverage)
- **Linting**: black / flake8 (recommended)
- **Frontend**: Modern JavaScript (TypeScript recommended)
- **CI/CD**: Automated testing and linting on all PRs

## How to Use This Documentation

1. **Finding Requirements**: Use the quick links above or browse `docs/requirements/`
2. **Tracking Changes**: See [CHANGELOG.md](CHANGELOG.md) for recent updates
3. **Adding Requirements**: Create detailed spec in appropriate directory
4. **Making Decisions**: Document in [docs/decisions/](docs/decisions/)
5. **Checking Progress**: See [Acceptance Criteria](docs/requirements/acceptance-criteria.md)

## Questions?

- Check the appropriate requirements document
- Review related ADRs in [docs/decisions/](docs/decisions/)
- Open an issue for clarification or updates

## Frontend: One-Page App (OPA) Requirement

We will provide a lightweight, accessible One-Page App (OPA) as a demo and reference implementation for the UI. The OPA serves two purposes: a) a minimal, production-adjacent UI for stakeholders to try pivot/search/zoom interactions and b) a canonical example demonstrating API usage for front-end developers.

Primary expectations for the OPA:

- Provide search UI to query dimensions (`/search/{dimension}`) and display results in an accessible grid/list.
- Provide pivot controls to switch from one dimension to another (`/pivot?from=...&to=...&id=...`).
- Provide Zoom controls to change result density/detail level; zoom levels should be exposed to users and affect rendered detail.
- **Auto-populate on load**: Automatically fetch and display a random person entity (filtered by instance of Q5/human) from Wikidata when the page first loads to avoid a blank initial state and provide relevant initial content.
- Accessibility: ARIA labels, keyboard navigation (tab/Enter), visible focus states, and sufficient color contrast.
- Lightweight and static: implementable with vanilla JS (no heavy framework required for demo) and runnable via a simple static server (`python -m http.server`) or embedded in the production frontend build.
- Configurable API base URL for local testing (default `http://localhost:8000`).

Acceptance criteria for the OPA:

1. Demonstrable search, pivot and zoom interactions against the running demo API.
2. Basic keyboard navigation and ARIA labels present for primary controls.
3. **Random entity displayed on initial page load** - frontend fetches from `/random` endpoint and displays result automatically.
4. Documentation in `frontend/README.md` describing how to run the demo and change the API base.
5. Example usage for developers: sample calls to `/search`, `/pivot`, and `/random` in the client code.

### OPA Widget Design: Timeline & Map Separation

The One-Page App includes two primary visualization widgets that should be presented separately to avoid overlap and provide distinct interaction patterns.

#### Timeline Widget (Gantt-Chart Style)

- Display events/episodes as horizontal bars positioned along a time axis.
- Show "milestone" events (single-date events) as point markers along the timeline.
- Bars should be color-coded by source trust level or custom color scheme.
- Clicking a bar or milestone should select the corresponding item in the grid below.
- Zoom controls should adjust the time scale (e.g., zoom out to centuries, zoom in to days).

#### Map Widget (Static Image with Pins)

- Use a static world map image (SVG or raster) as the background.
- Place pins/markers at geographic coordinates of events/locations.
- Pins should be clickable and show item title/description on hover or click.
- Should work without relying on tile-based mapping services (Leaflet, Mapbox).
- Color-code pins by dimension (events, people, geography) or trust level.

#### Layout

- Timeline and map should be displayed as separate, non-overlapping panels in the UI.
- Responsive: on smaller screens, stack vertically; on larger screens, side-by-side or stacked layout.
- Both widgets should update when users perform search, pivot, or zoom operations.

