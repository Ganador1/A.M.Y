# syntax=docker/dockerfile:1.6
# Optional scientific integration image; build context must be atlas/.
# Example: docker build -f atlas/config/Dockerfile -t atlas-scientific atlas/
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates libffi-dev libssl-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements*.txt ./
COPY config/requirements.audit.txt ./requirements.audit.txt
# Some optional scientific packages need additional platform-specific libraries.
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt -r requirements.audit.txt
COPY . .
RUN mkdir -p mlruns data static/graphs

ENV MLFLOW_TRACKING_URI=file:/app/mlruns \
    STRICT_DATA_PATHS=0 \
    ALLOWED_DATA_ROOT=/app/data
EXPOSE 8000
# This retained integration script reports its own checks; it is not release CI.
CMD ["python", "tests/integration/test_meta4_real_data.py"]
