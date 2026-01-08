# Project Requirements

Use this file to capture functional, non-functional and infrastructure requirements.

## Functional Requirements

### Overall Description

This solution creates a highly-interactive visual timeline of historical and geographical events.  The solution enables the user to:
* View events/episodes of history, people, geography, geology, spheres of influence and other topics or categories as dimensions that can be navigated or pivotted between.
* Where meaningful and there is available data, to pivot between different dimensions (for example):
  *  Timeline - for example:
     *  Which historical events/episodes affected France over time?
     *  Where were the continents during the Jurrasic age?
  *  Geography - for example:
     *  What else happened in this region at different times?
     *  How have geology, geography, borders or ruling systems/famillies changed in this geography?
  *  People - for example: 
     *  What else did Napoleon do (by geography or time)?
     *  Where else did Neaderthal peoples spread to?
  *  Events/episodes in history - for example:
     *  How did the front-lines change during the first world war?
     *  How did the Babylonian empire expand over time?
* Where data provides he linkage, it should be possible to zoom in or out along any of the dimensions - for example:
  * Timeline - should be capable of zooming from geological ages to milliseconds (e.g. in the case of the first few moments of the Universe).
  * Geography - should be capable of zooming into a village or street and out to the whole Universe.
  * People - should be capable of zooming from a single figure (e.g. Adolf Hitler) through organisations (e.g. the National Socialist or Nazi party) through nationalities (e.g. German) or general tribes or regions (e.g. Europeans or Homo Sapiens).
  * Events/episodes in history - should be capable of zooming from an individual event (e.g. the assassination of Archduke Ferdinand) to consequence episodes (e.g. the First World War) and broader spans (e.g. Wiemar Germany).

## Non-Functional Requirements
- Python version: 3.8+
- Testing: pytest
- Linting: black / flake8 (optional)

## Overall Non-Functional Requirements

The User Interface and Experience must be engaging and intuitive to use.  The experience should be highly graphical and feel modern.

The interface must load and render very quickly with minimal processing time on the end-users device.

The interface should initially work in the main browsers (Chrome, Safari, Firefox, Edge) but should be capable of moving to an App delivery model for mobile platforms in the future.

It should be easy to add other dimensions in the future besides those describes already.

It should not be necessary to cross-reference source data to pivot between dimensions.  Pivoting should be done on the basis of available data based on the current context that each user is in.

## Infrastructure / Terraform Requirements
- AWS account details and region
- Managed resources (e.g., VPC, subnets, ECS/EKS, RDS)
- State backend (e.g., S3 + DynamoDB) — capture decisions here

## Acceptance Criteria
- 

## Notes
- Keep decisions and constraints here for future Terraform design.
