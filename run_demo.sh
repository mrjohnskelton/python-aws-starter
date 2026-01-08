#!/usr/bin/env bash
# Run the demo FastAPI app using the project's virtualenv
set -euo pipefail
DIR=$(cd "$(dirname "$0")" && pwd)
source "$DIR/.venv/bin/activate"
# Launch uvicorn with the app module
exec uvicorn python_aws_starter.api.app:app --host 127.0.0.1 --port 8000 --reload
