from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.genomics import router as genomics_router

app = FastAPI()
app.include_router(genomics_router)
client = TestClient(app)


def test_env_check():
    r = client.get("/api/genomics/env")
    assert r.status_code == 200
    data = r.json()
    assert 'docker_available' in data


def test_validate_inputs_missing():
    # Use non-existing paths to exercise validation path
    payload = {"bam_file": "/nope/sample.bam", "reference_fasta": "/nope/GRCh38.fa", "output_dir": "/nope/out"}
    r = client.post("/api/genomics/deepvariant/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False
    assert len(data["errors"]) >= 1


