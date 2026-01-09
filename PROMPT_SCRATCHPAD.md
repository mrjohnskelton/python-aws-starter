# Prompts & Notes

## Next Steps

### Functional Features

Add a 'detail panel' to the front end, this should go below the list/cards section.  There should be a single detail panel which shows the details returned from wikidata for the selected card.
If you need to make any back-end changes to support this then do so (for example if detail fields have not been passed through yet).
Update the functional requirements markdown to reflect this feature.
Deploy the new features.


Change the initial random result to only return a 'person' type result. I think this can be done by filtering by instance of a class (e.g., Q5 for human)
Update the functional requirements markdown to reflect this feature.

Get the timeline and map working better

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

