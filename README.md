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

1. Start the sample API (uses test fixtures in `tests/fixtures`):

```bash
source .venv/bin/activate
./run_demo.sh
# then open http://127.0.0.1:8000/docs for OpenAPI UI
```

2. Example requests:

```bash
# Pivot people -> events
curl 'http://127.0.0.1:8000/pivot?from=people&to=events&id=person_napoleon'

# Search events near Paris
curl 'http://127.0.0.1:8000/search/events?center_lat=48.8566&center_lon=2.3522&within_km=20'
```

## Next steps

- Add Terraform under `infra/` or `terraform/` and include `.tf` modules for AWS.
- Add CI workflow for tests and linting.
