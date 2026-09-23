from fastapi.testclient import TestClient

from app.routers.number_theory_conjectures import router


def test_evidence_batch_and_rank():
    client = TestClient(router)
    gen = client.post("/api/number-theory/conjectures/generate", json={"value": 20})
    assert gen.status_code == 200
    conj = gen.json().get("conjectures", [])

    eb = client.post("/api/number-theory/conjectures/evidence-batch", json={"conjectures": conj, "lower": 4, "upper": 100})
    assert eb.status_code == 200
    items = eb.json().get("items", [])
    # preparar para ranking
    rank_items = [it["for_ranking"] for it in items]
    rk = client.post("/api/number-theory/conjectures/rank", json={"items": rank_items})
    assert rk.status_code == 200
    data = rk.json()
    assert "ranked" in data


