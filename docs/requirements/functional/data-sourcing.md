# Data Sourcing Requirements

## Overview

The application integrates data from multiple sources with varying levels of trust and authority, requiring tracking of provenance and handling of conflicts.

## Functional Requirements

### Data Sources

The system must support data from:

1. **Curated/Self-Created Data**
   - Data created and maintained by the project team
   - Highest trust level (0.9-1.0)
   - Examples: Custom timelines, internal datasets

2. **Publicly Available Data**
   - Data from reputable public sources
   - Medium-high trust level (0.7-0.9)
   - Examples: Wikipedia, academic databases, historical records
   - May require web scraping or API integration

3. **User-Submitted Data**
   - Data entered by power users
   - Medium trust level (0.4-0.7)
   - Requires review/curation before full integration
   - Examples: Personal research, corrections, additional context

### Source Attribution

Every data point must track its origin:

- Source identification (name, ID, type)
- Trust level
- Fields contributed by each source
- External reference (e.g., Wikipedia article ID)
- URL to original source
- Last verification date

### Conflict Resolution

When sources provide conflicting data:

1. **Confidence Aggregation**
   - Calculate combined confidence from all sources
   - Weight by trust level
   - Display to user with confidence indicator

2. **Primary Source Designation**
   - Allow curation team to designate authoritative source for conflicts
   - Document reasoning for choice

3. **Conflict Notation**
   - Display all conflicting versions to user
   - Show which sources provided which versions
   - Indicate trust levels for each version

4. **User Contribution Workflow**
   - Users can suggest corrections
   - Changes flagged for review by curators
   - Approved changes update canonical data
   - Rejected changes with explanation

### Data Quality Tracking

Each entity must track:

- Validation status (unverified, pending review, peer-reviewed, curated)
- Requires manual review flag
- Review notes and comments
- Known issues or caveats
- Last validation date and who validated

## Acceptance Criteria

- [ ] System tracks source for every data field
- [ ] Confidence level is calculated and displayed
- [ ] Conflicting sources are identified and noted
- [ ] Users can view all source versions when conflicts exist
- [ ] User contributions are tracked and attributable
- [ ] Curation team can review and approve contributions
- [ ] Data quality status is visible to users
- [ ] Source trust level influences search/ranking

## Technical Considerations

- Implement denormalized source tracking to avoid complex joins
- Cache source attribution with entity data
- Implement audit trails for all changes
- Version data entities to track changes over time
- Consider time-series storage for temporal variants (e.g., country borders)
