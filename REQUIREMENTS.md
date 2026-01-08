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
