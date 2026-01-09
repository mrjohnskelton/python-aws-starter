# Prompts & Notes

## Next Steps

### Functional Features

Get the timeline and map working better

Where a card has a start date and end date, use these to update the timeline for the selected card. For example, for a person these fields seem to be P569 or 'BIRTH DATE:' and P570 or DEATH DATE:'.  Other types of entry may have different start/end date codes/names but I want to pick them up wherever possible regardless of the type of entry (for example the Jurrasic Age was not born or died, but will have start/end dates with appropriate unit of magnitude as per original requirements).
Update the non-functional requirements markdown to reflect this feature.


### Non-Functional Features


Add caching so that if the user goes 'back' we don't have to requery Wikidata.  
Update the non-functional requirements markdown to reflect this feature.


Include rate limiting capability to stop the user performing more than one wikidata search every 5 seconds.
Update the non-functional requirements markdown to reflect this feature.

Add a 'detail panel' to the front end, this should go below the list/cards section.  There should be a single detail panel which shows the details returned from wikidata for the selected card.
Update the functional requirements markdown to reflect this feature.


### Housekeeping

Review the local test data interfaces and data to check that it supports all the front-end features that are now avialbale and it compatible with the 'live' seaerch of wikidata.







## To Run Prompt

docker-compose up --build &
(cd frontend && python3 -m http.server 8080) &



## Total Scratchpad

