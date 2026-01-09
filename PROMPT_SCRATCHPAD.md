# Prompts & Notes

## Next Steps

Mid-way through...
also change the code so check that WIKIDATA_LOG_BODY, DATA_LOG_BODY_MAX, DATA_SOURCE and LOG_LEVEL are defined in the main config.py file

Next steps (optional): add caching, rate-limiting, richer claim-to-field mapping, and pivot support — want me to implement any of these?

## To Run Prompt

docker-compose up --build &
(cd frontend && python3 -m http.server 8080) &