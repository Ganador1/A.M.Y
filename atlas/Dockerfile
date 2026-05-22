# AXIOM META 4 - Dockerfile de Producción
# ======================================
# Multi-stage build para optimización de imagen
# Incluye todas las dependencias de Phase 3 + Phase 4

# Stage 1: Builder - Instala dependencias y compila
FROM python:3.13-slim as builder

# Configuración del entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema para compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash axiom

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para aprovechar cache de Docker)
COPY requirements.txt requirements.audit.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user -r requirements.audit.txt

# Instalar dependencias adicionales para Phase 4
RUN pip install --no-cache-dir --user \
    gunicorn==21.2.0 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    aiofiles==23.2.1 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-decouple==3.8 \
    alembic==1.13.1

# Stage 2: Runtime - Imagen final optimizada
FROM python:3.13-slim as runtime

# Configuración del entorno de producción
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/axiom/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Instalar dependencias del sistema runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    libffi8 \
    libssl3 \
    curl \
    procps \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash --uid 1001 axiom

# Configurar directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/axiom/.local
RUN chown -R axiom:axiom /home/axiom/.local

# Copiar código de la aplicación
COPY --chown=axiom:axiom . .

# Cambiar a usuario no-root
USER axiom

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando de inicio optimizado para producción
CMD ["gunicorn", \
     "main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50"]
