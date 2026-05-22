from fastapi.testclient import TestClient

from app.routers.number_theory_conjectures import router


def test_generate_and_evaluate_number_conjectures():
    client = TestClient(router)

    r = client.post("/api/number-theory/conjectures/generate", json={"value": 10})
    assert r.status_code == 200
    data = r.json()
    assert data["n"] == 10
    assert isinstance(data.get("conjectures"), list)

    if data["conjectures"]:
        conj = data["conjectures"][0]
        r2 = client.post("/api/number-theory/conjectures/evaluate", json={"value": 10, "conjecture": conj})
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["n"] == 10
        assert "result" in d2


