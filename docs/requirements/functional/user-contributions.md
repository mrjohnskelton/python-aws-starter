# User Contributions and Crowdsourcing

## Overview

The system enables power users and contributors to submit new data and corrections, which are tracked, reviewed, and integrated based on merit and authority.

## Functional Requirements

### Contribution Types

Users can contribute:

1. **New Entries**
   - Create entirely new events, people, or locations
   - Provide sources and justification
   - Initial status: Pending review

2. **Edits and Corrections**
   - Modify existing data
   - Track original vs. modified values
   - Provide change justification
   - Initial status: Pending review

3. **Source Additions**
   - Add new sources to existing entities
   - Link to additional references
   - Initial status: Pending review

4. **Conflict Resolution**
   - Suggest which source to prioritize when conflicts exist
   - Provide reasoning
   - Initial status: Pending review

### Contribution Workflow

1. **Submission**
   - User submits contribution with justification
   - System validates format and completeness
   - Contribution stored as pending

2. **Review Process**
   - Curation team/moderators review contributions
   - Can approve, reject, or request clarification
   - Comments and feedback provided

3. **Approval/Integration**
   - Approved contributions merged into canonical data
   - User credited in attribution
   - Contribution history preserved

4. **Rejection**
   - Rejected contributions marked as such
   - Reasoning provided to user
   - Can be resubmitted with changes

### Contributor Reputation

Future enhancement: Track contributor quality metrics

- Acceptance rate of contributions
- Domain expertise (areas of contribution)
- Peer review ratings
- Awards/recognition

### Access Control

- Public read-only access to data
- Authenticated access required for contributions
- Moderation/curation role for review
- Admin role for final approval/integration

## Acceptance Criteria

- [ ] Users can submit new entries
- [ ] Users can propose edits to existing data
- [ ] All submissions include change justification
- [ ] Moderators can review pending contributions
- [ ] Contributions can be approved or rejected
- [ ] Contribution history is preserved
- [ ] Users are credited for accepted contributions
- [ ] Original data is preserved (version control)
- [ ] Rejection includes explanatory feedback

## Technical Considerations

- Implement version control for all entities
- Track full edit history with attribution
- Separate pending vs. approved data in queries
- Implement soft deletes for data provenance
- Consider decoupled moderation queue
- Implement user authentication and authorization
