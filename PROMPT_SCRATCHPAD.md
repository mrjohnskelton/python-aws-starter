# Prompts & Notes

## Next Steps

Mid-way through...
also change the code so check that WIKIDATA_LOG_BODY, DATA_LOG_BODY_MAX, DATA_SOURCE and LOG_LEVEL are defined in the main config.py file

based on our chat, what should the default values for the following be:WIKIDATA_LOG_BODY, DATA_LOG_BODY_MAX, DATA_SOURCE and LOG_LEVEL

The default values should be:
WIKIDATA_LOG_BODY: False — don't log full bodies by default.
DATA_LOG_BODY_MAX: 1000 — limit body logs to ~1KB (use 4096 if you prefer 4KB).
DATA_SOURCE: "local" — default to local/fixture data.
LOG_LEVEL: "INFO" — use INFO by default (DEBUG when DEBUG=true).


Next steps (optional): add caching, rate-limiting, richer claim-to-field mapping, and pivot support — want me to implement any of these?

## To Run Prompt

docker-compose up --build &
(cd frontend && python3 -m http.server 8080) &

## Total Scratchpad

what is the difference between the following commands: "git config pull.rebase false", "git config pull.rebase true" and "git config pull.ff only"