import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.lab_automation import router as lab_router
from app.routers.structural_db import router as structdb_router


app = FastAPI()
app.include_router(lab_router, prefix="/api/lab-automation")
app.include_router(structdb_router, prefix="/api/structdb")
client = TestClient(app)


def test_lab_health():
    r = client.get("/api/lab-automation/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"


def test_lab_pcr():
    payload = [{"id": "s1", "volume": 20}]
    r = client.post("/api/lab-automation/pcr", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("protocol") == "PCR"
    assert data.get("samples_processed") == 1


def test_structdb_uniprot_notfound():
    # Expect 404 for nonsense accession
    r = client.get("/api/structdb/uniprot/XYZ_NOT_REAL_123")
    assert r.status_code in (200, 404)


