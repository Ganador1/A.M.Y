"""Smoke tests para servicios del Agente 2 (biología/experimental).

Ejecutan rutas simuladas y ligeras para validar que las respuestas básicas
son exitosas y contienen campos esperados. Evitan dependencias externas.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_alphafold3_predict_structure():
    payload = {
        "sequence": "MKTVRQERLKSIVRILERSK",
        "options": {"include_pdb": True}
    }
    resp = client.post("/api/alphafold3/predict-structure", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "data" in data and "quality_assessment" in data["data"]


def test_neuro_light_bandpowers():
    payload = {
        "sampling_rate_hz": 1000.0,
        "data": [[0.0, 1.0, 0.0, -1.0], [0.1, 0.2, -0.1, -0.2]]
    }
    resp = client.post("/api/neuro-light/bandpowers", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    assert obj["n_channels"] == 2
    assert "aggregate" in obj


def test_lab_automation_pcr():
    samples = [
        {"id": "s1", "volume": 20},
        {"id": "s2", "volume": 25}
    ]
    resp = client.post("/api/lab-automation/pcr", json=samples)
    assert resp.status_code == 200
    obj = resp.json()
    assert obj["protocol"] == "PCR"
    assert obj["samples_processed"] == 2


def test_genomics_env():
    resp = client.get("/api/genomics/env")
    assert resp.status_code == 200
    obj = resp.json()
    assert "docker_available" in obj


def test_earth_light_seismic_analysis():
    payload = {"samples": [0.0, 0.5, -0.3, 0.8, -0.1], "sampling_rate_hz": 100.0}
    resp = client.post("/api/earth-light/seismic-analysis", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    assert "rms" in obj and "zero_crossing_rate_hz" in obj


def test_neuro_light_health():
    resp = client.get("/api/neuro-light/health")
    assert resp.status_code == 200
    obj = resp.json()
    assert obj["service"] == "NeuroscienceLightService"
    assert obj["status"] in {"healthy", "degraded"}


def test_earth_light_health():
    resp = client.get("/api/earth-light/health")
    assert resp.status_code == 200
    obj = resp.json()
    assert obj["service"] == "EarthSciencesLightService"
    assert obj["status"] in {"healthy", "degraded"}


def test_earth_light_map_heat():
    payload = {
        "grid": [[0.1, 0.2, 0.3], [0.0, -0.1, 0.05]],
        "cmap": "viridis",
        "title": "demo"
    }
    resp = client.post("/api/earth-light/map-heat", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    # Si matplotlib no está disponible, devolverá error claro; aceptar cualquiera determinísticamente
    assert ("image_base64_png" in obj and len(obj["image_base64_png"]) > 0) or ("error" in obj)


def test_earth_light_map_currents():
    payload = {
        "u": [[0.1, 0.2, 0.0], [0.0, -0.1, 0.05]],
        "v": [[0.0, -0.1, 0.1], [0.2, 0.0, -0.05]],
        "step": 1,
        "scale": 1.0,
        "title": "currents"
    }
    resp = client.post("/api/earth-light/map-currents", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    assert ("image_base64_png" in obj and len(obj["image_base64_png"]) > 0) or ("error" in obj)


def test_neuro_light_batch_bandpowers():
    payload = {
        "sampling_rate_hz": 1000,
        "datasets": [
            [[0,1,0,-1],[0.1,0.2,0.1,0.0]],
            [[0,1,0,-1,0,1],[0.2,0.1,0.0,-0.1,0.0,-0.2]]
        ]
    }
    resp = client.post("/api/neuro-light/batch-bandpowers", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    assert obj.get("count", 0) == 2


def test_cloud_lab_mock_mass_spec():
    resp = client.post("/api/cloud-lab/mass-spec/mock", params={"sample_id": "sample_1"})
    assert resp.status_code == 200
    obj = resp.json()
    assert obj["status"] == "completed"
    assert "peaks" in obj


def test_advanced_cloud_lab_protocols_and_submit():
    # Protocols list
    resp = client.get("/api/advanced-cloud-lab/protocols")
    assert resp.status_code == 200
    obj = resp.json()
    assert "available_protocols" in obj

    # Submit simple mass_spec_analysis
    payload = {
        "protocol_name": "mass_spec_analysis",
        "samples": [{"id": "s1", "volume_ul": 10.0, "sample_type": "protein"}],
        "parameters": {"ionization_mode": "ESI"}
    }
    resp = client.post("/api/advanced-cloud-lab/experiments/submit", json=payload)
    assert resp.status_code == 200
    obj = resp.json()
    assert "experiment_id" in obj and obj.get("status") in {"running", "submitted"}


def test_advanced_lab_templates_and_status():
    resp = client.get("/api/advanced-lab/protocols/templates")
    assert resp.status_code == 200
    obj = resp.json()
    assert "available_protocols" in obj


def test_neuro_light_bad_sampling_rate():
    payload = {"sampling_rate_hz": 0, "data": [[0, 1, 0, -1]]}
    resp = client.post("/api/neuro-light/bandpowers", json=payload)
    assert resp.status_code == 200
    assert "error" in resp.json()


def test_earth_light_bad_grid():
    payload = {"grid": [[1.0], [2.0]], "threshold": 0.05}
    resp = client.post("/api/earth-light/eddies-2d", json=payload)
    assert resp.status_code == 200
    assert "error" in resp.json()


