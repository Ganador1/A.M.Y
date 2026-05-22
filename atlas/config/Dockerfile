# syntax=docker/dockerfile:1.6
# Imagen base slim con Python 3.11
FROM python:3.11-slim

# Evitar prompts interactivos y configurar UTF-8
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Paquetes del sistema necesarios (build + runtimes típicos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar solo requirements primero para cachear pip install
COPY requirements.txt requirements.audit.txt ./

# Instalar dependencias de Python. Nota: Algunos paquetes pesados (gpaw, neuron, qutip)
# pueden requerir toolchains/BLAS específicos; si fallan, coméntalos en requirements
# o use una imagen científica (p. ej. mambaforge + conda). Para el pipeline básico
# y pruebas reales ya validadas, instalamos el set definido.
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Crear directorios de runtime
RUN mkdir -p mlruns data static/graphs

# Variables para servicios internos
ENV MLFLOW_TRACKING_URI=file:/app/mlruns \
    STRICT_DATA_PATHS=0 \
    ALLOWED_DATA_ROOT=/app/data

# Exponer puerto del servidor si se usa FastAPI
EXPOSE 8000

# Entrypoints de utilidad: por defecto, ejecutar pruebas de datos reales
# Se puede sobreescribir con: docker run ... python test_meta4_real_data.py
CMD ["python", "test_meta4_real_data.py"]
