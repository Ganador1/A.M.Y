# Atlas service image. Build with the atlas/ directory as the context.
# Optional scientific dependencies and live deployment require separate validation.
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev libffi-dev libssl-dev curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# requirements.txt includes the other requirements-*.txt files.
COPY requirements*.txt ./
COPY config/requirements.audit.txt ./requirements.audit.txt
RUN python -m venv /opt/atlas-venv
ENV PATH="/opt/atlas-venv/bin:$PATH"
# Resolve the audit constraints and service dependencies together; a later install
# must not silently replace their versions with an older second set of pins.
RUN pip install --no-cache-dir -r requirements.txt -r requirements.audit.txt \
    gunicorn 'uvicorn[standard]' aiofiles 'python-jose[cryptography]' \
    'passlib[bcrypt]' python-decouple

FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/atlas-venv/bin:$PATH" \
    PYTHONPATH="/app"

RUN apt-get update && apt-get install -y \
    libpq5 libffi8 libssl3 curl procps netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
RUN useradd --create-home --shell /bin/bash --uid 1001 axiom
WORKDIR /app
COPY --from=builder /opt/atlas-venv /opt/atlas-venv
COPY --chown=axiom:axiom . .
USER axiom

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["gunicorn", "main_refactored:app", "--bind", "0.0.0.0:8000", \
     "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", \
     "--max-requests", "1000", "--max-requests-jitter", "50"]
