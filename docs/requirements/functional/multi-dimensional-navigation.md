# Multi-Dimensional Navigation

## Overview

The application enables users to seamlessly navigate and pivot between different dimensions of historical data.

## Functional Requirements

### Available Dimensions

The application must support the following core dimensions:

1. **Timeline** - Navigate events by time period
2. **Geography** - Navigate events by location and spatial relationships
3. **People** - Navigate historical figures and their activities
4. **Events/Episodes** - Navigate historical events and their consequences
5. **Custom Dimensions** - System must be extensible for future dimensions (geology, spheres of influence, etc.)

### Pivoting Capabilities

Users must be able to pivot between dimensions while maintaining context. Examples:

**Timeline → Geography**
- "Which historical events affected France over time?"
- "Where were the continents during the Jurassic age?"

**Geography → Timeline**
- "What else happened in this region at different times?"
- "How have geology, geography, borders, or ruling systems changed?"

**People → Geography/Timeline**
- "What else did Napoleon do by geography or time?"
- "Where did Neanderthal peoples spread to?"

**Events → People/Geography**
- "How did front-lines change during World War I?"
- "How did the Babylonian empire expand over time?"

### Data-Driven Pivoting

- Pivoting must be based on available data and current context
- No need to cross-reference source data manually
- System must pre-compute dimensional relationships
- Users see only available pivot options for their current context

### Related Data Display

When viewing an entity (event, person, location), the system must:
- Show related entities in other dimensions
- Indicate relationship strength/confidence
- Allow drilling down into related data
- Maintain historical context across pivots

## Acceptance Criteria

- [ ] User can pivot from Timeline to Geography dimension
- [ ] User can pivot from Geography to People dimension
- [ ] User can pivot from People to Events dimension
- [ ] All pivots maintain search/filter context where applicable
- [ ] System displays only valid pivot options for current view
- [ ] Related data is fetched and displayed within 2 seconds
- [ ] Pivot history is maintained (user can navigate back)

## Technical Considerations

- Pre-compute dimensional relationships during data ingestion
- Implement efficient indexing for fast pivot queries
- Cache common pivot operations
- Consider dimensional denormalization for performance
