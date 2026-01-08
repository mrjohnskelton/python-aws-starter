# python-aws-starter

Starter Python project intended to later include Terraform for AWS infrastructure.

## What's here

- `src/python_aws_starter/` — main package
- `tests/` — pytest tests
- `pyproject.toml` — packaging metadata
- `requirements.txt` — python runtime/dev deps
- `REQUIREMENTS.md` — place to capture project requirements
- `.gitignore` — ignores common files and Terraform state

## Quick start

1. Create a virtual environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

## Run the demo API

### Option 1: Local (with virtualenv)

1. Start the sample API (uses test fixtures in `tests/fixtures`):

```bash
source .venv/bin/activate
./run_demo.sh
# then open http://127.0.0.1:8000/docs for OpenAPI UI
```

### Option 2: Docker (recommended)

1. Build and run the API in a container:

```bash
docker-compose up --build
# then open http://127.0.0.1:8000/docs for OpenAPI UI
```

2. To run without docker-compose:

```bash
docker build -t python-aws-starter .
docker run -p 8000:8000 python-aws-starter
```

### Full-stack demo (backend + frontend)

These steps run both the demo API and the static One-Page App (OPA) that uses the sample fixtures.

1. Start the backend API (docker-compose recommended):

```bash
# from project root
docker-compose up --build
```

2. In a second terminal, serve the frontend static files:

```bash
cd frontend
python3 -m http.server 8080
# then open http://localhost:8080 in your browser
```

3. In the SPA click "Load local sample data" to load the bundled sample dataset, or use the Search form to query the running API at `http://localhost:8000`.

Notes:

- The SPA is configured to fetch the API at `http://localhost:8000` by default. Edit `frontend/app.js` to change `API_BASE` if needed.
- To stop the demo, press `Ctrl+C` in the terminal running `docker-compose`, or run `docker-compose down`.

### Example requests

```bash
# Pivot people -> events
curl 'http://127.0.0.1:8000/pivot?from=people&to=events&id=person_napoleon'

# Search events near Paris
curl 'http://127.0.0.1:8000/search/events?center_lat=48.8566&center_lon=2.3522&within_km=20'
```

## Next steps

- Add Terraform under `infra/` or `terraform/` and include `.tf` modules for AWS.
- Add CI workflow for tests and linting.
