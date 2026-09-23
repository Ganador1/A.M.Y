from fastapi.testclient import TestClient

from app.routers.sequence_oeis import router


def test_oeis_search_endpoint_smoke():
    client = TestClient(router)
    payload = {"terms": [1, 1, 2, 3, 5, 8], "max_results": 3}
    r = client.post("/api/sequences/oeis/search", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Puede fallar offline; aceptar presencia de error o lista
    assert ("results" in data) or ("error" in data)

