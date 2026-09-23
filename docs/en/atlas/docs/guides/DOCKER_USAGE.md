> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

Run in Docker
==================

- Build the image:
  docker build -t atlas-meta4:latest .

- Run tests with real data (default from CMD):
  docker run --rm -it atlas-meta4:latest

- Run the FastAPI server (if applicable):
  docker run --rm -it -p 8000:8000 \
    -e MLFLOW_TRACKING_URI=file:/app/mlruns \
    -v "$(pwd)/mlruns:/app/mlruns" \
    -v "$(pwd)/data:/app/data" \
    atlas-meta4:latest \
    uvicorn app.main:app --host 0.0.0.0 --port 8000

- Run the full AXIOM META 4 suite:
  docker run --rm -it atlas-meta4:latest python test_meta4_validation.py

Notes
-----
- Some heavy scientific packages may require additional toolchains. If the build fails due to native libs, use a Conda image (mambaforge) or temporarily comment out those packages.
- To enable DVC inside the container, mount .dvc/ and the binary if using an external wrapper; this project uses optional integration via CLI.
