# Multi-stage build for python-aws-starter demo
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code and setup files
COPY src/ src/
COPY tests/fixtures/ tests/fixtures/
COPY pyproject.toml .

# Install the package in development mode
RUN python -m pip install --user -e .

# Set PATH to use local pip installs
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Run uvicorn
CMD ["uvicorn", "python_aws_starter.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
