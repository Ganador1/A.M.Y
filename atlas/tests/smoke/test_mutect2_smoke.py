from fastapi.testclient import TestClient
import importlib

app = importlib.import_module("app.main").app
client = TestClient(app)


def test_mutect2_validate_missing_paths():
    payload = {
        "tumor_bam": "/nope/tumor.bam",
        "normal_bam": "/nope/normal.bam",
        "reference_fasta": "/nope/GRCh38.fa",
        "output_dir": "/nope/out"
    }
    r = client.post("/api/genomics/mutect2/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is False
    assert len(data["errors"]) >= 1

