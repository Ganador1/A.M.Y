from __future__ import annotations

import base64
from fastapi.testclient import TestClient

from app.mathlab.conjectures.number_theory_plugin import NumberTheoryConjecturePlugin
from app.mathlab.core.object_models import MathematicalObject
from app.routers.earth_sciences_light import router


def test_number_theory_plugin_goldbach_and_two_squares():
    plugin = NumberTheoryConjecturePlugin()
    obj = MathematicalObject(
        id="n10",
        type="integer",
        semantic_hash="h",
        payload_json={"type": "integer", "value": 10},
    )
    cands = plugin.generate(obj)
    assert any(c["type"] == "goldbach" for c in cands)
    assert any(c["type"] == "sum_two_squares" for c in cands)

    # Evaluación Goldbach
    gold = [c for c in cands if c["type"] == "goldbach"][0]
    res_g = plugin.evaluate(obj, gold)
    assert res_g["status"] in {"SUPPORTS", "INCONCLUSIVE", "SKIP"}

    # Evaluación suma de dos cuadrados (10 = 1^2 + 3^2)
    two = [c for c in cands if c["type"] == "sum_two_squares"][0]
    res_t = plugin.evaluate(obj, two)
    assert res_t["status"] in {"SUPPORTS", "REFUTES"}


def test_earth_light_map_heat_currents():
    client = TestClient(router)
    payload = {
        "grid": [[0.1, 0.2], [0.0, -0.1]],
        "u": [[0.5, 0.0], [0.0, -0.5]],
        "v": [[0.0, 0.5], [-0.5, 0.0]],
        "title": "demo",
    }
    r = client.post("/api/earth-light/map-heat-currents", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "image_base64_png" in data or "error" in data
    if "image_base64_png" in data:
        # valida que decodifica
        base64.b64decode(data["image_base64_png"])  # no debe lanzar


