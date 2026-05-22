Ejecutar en Docker
==================

- Build de la imagen:
  docker build -t atlas-meta4:latest .

- Correr pruebas con datos reales (por defecto del CMD):
  docker run --rm -it atlas-meta4:latest

- Correr el servidor FastAPI (si aplica):
  docker run --rm -it -p 8000:8000 \
    -e MLFLOW_TRACKING_URI=file:/app/mlruns \
    -v "$(pwd)/mlruns:/app/mlruns" \
    -v "$(pwd)/data:/app/data" \
    atlas-meta4:latest \
    uvicorn app.main:app --host 0.0.0.0 --port 8000

- Ejecutar el suite completo AXIOM META 4:
  docker run --rm -it atlas-meta4:latest python test_meta4_validation.py

Notas
-----
- Algunos paquetes científicos pesados pueden requerir toolchains adicionales. Si el build falla por libs nativas, use una imagen Conda (mambaforge) o comente temporalmente esos paquetes.
- Para habilitar DVC dentro del contenedor, monte .dvc/ y el binario si usa wrapper externo; este proyecto usa integración opcional vía CLI.
