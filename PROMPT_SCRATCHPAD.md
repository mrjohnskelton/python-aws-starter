# Prompts & Notes

## Next Steps

### Functional Features

Get the timeline and map working better

~~Where a card has a start date and end date, use these to update the timeline for the selected card. For example, for a person these fields seem to be P569 or 'BIRTH DATE:' and P570 or DEATH DATE:'.  Other types of entry may have different start/end date codes/names but I want to pick them up wherever possible regardless of the type of entry (for example the Jurrasic Age was not born or died, but will have start/end dates with appropriate unit of magnitude as per original requirements).
Update the non-functional requirements markdown to reflect this feature.
Test and deploy these changes.~~

** Not working in every case, i.e. Napoleon Bonaparte doesn't change **
When a different card is selected in the front end then the timeline and map should also be updated to reflect the content of the selected card.
Update the functional requirements markdown to reflect this feature.
Test and deploy these changes.

** Finished Friday with this**
Update understanding of start/end dates.  Several wikidata fields are synonyms for start and end date and should be detected ass such so that we can overlay shared timelines or jump from one item to another based on overlapping or adjoining timeframes.  Capture the synonyms in a configuration file. We may also use this configuration file for other synonyms later.
As examples the following are all synonyms for start/end dates in this solution:
* P571 - Inception
* P1619 - Date of official opening
* P569 - Birth date
* P580 - Start Time (event)
* P585 - Point in time
* P570 - Deathdate
* P582 - End time
* P576 - Dissolved

There may be other codes which are also synonyms of start/end dates. If you can search for/find any then add them too.

Definitions of all of the above can be found at URLs of the form https://www.wikidata.org/wiki/Property:{Pnumber}, for example https://www.wikidata.org/wiki/Property:P571 for Inception.

Update the functionality to reconize the above synonyms as start/end dates for items.


Update the functional requirements markdown to reflect this feature.
Test and deploy these changes.


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

