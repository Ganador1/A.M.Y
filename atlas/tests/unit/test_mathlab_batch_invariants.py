from fastapi import FastAPI
from fastapi.testclient import TestClient
import time

# Importamos sólo el router de mathlab y la función específica que necesitamos
from app.routers.mathlab import router as mathlab_router
from app.routers.mathlab import _process_batch_invariants


def _build_minimal_app() -> TestClient:
    app = FastAPI()
    app.include_router(mathlab_router, prefix="/mathlab")
    return TestClient(app)


def test_batch_invariants_scheduler_smoke():
    client = _build_minimal_app()

    # Registrar 3 objetos: entero, grafo ER y entero negativo
    payloads = [
        {"type": "integer", "data": {"value": 840}},
        {"type": "graph", "data": {"graph_type": "erdos_renyi", "n": 20, "p": 0.2, "seed": 42}},
        {"type": "integer", "data": {"value": -105}},
    ]

    object_ids = []
    for p in payloads:
        r = client.post("/mathlab/objects/register", json=p)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "object_id" in body
        object_ids.append(body["object_id"])

    # Submit del job por lotes
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": object_ids, "chunk_size": 2})
    assert r.status_code == 200
    job_1 = r.json()
    assert "job_id" in job_1
    job_id = job_1["job_id"]

    # Re-Submit idéntico debe devolver el mismo job_id (idempotente)
    r2 = client.post("/mathlab/batch/invariants/submit", json={"object_ids": object_ids, "chunk_size": 2})
    assert r2.status_code == 200
    job_2 = r2.json()
    assert job_2["job_id"] == job_id

    # Polling hasta completar (timeout razonable)
    final = None
    for _ in range(300):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        j = s.json()
        if j.get("status") in {"completed", "failed"}:
            final = j
            break
    assert final is not None, "Timeout esperando que el job termine"
    assert final.get("status") == "completed", final
    assert final.get("processed") == final.get("total")
    assert isinstance(final.get("results"), list)


def test_batch_invariants_reports_missing_object():
    client = _build_minimal_app()

    # Registrar un objeto válido y armar una lista con uno inexistente
    r = client.post("/mathlab/objects/register", json={"type": "integer", "data": {"value": 12}})
    assert r.status_code == 200
    valid_id = r.json()["object_id"]

    missing_id = "nonexistent-123"
    r2 = client.post("/mathlab/batch/invariants/submit", json={"object_ids": [valid_id, missing_id], "chunk_size": 10})
    assert r2.status_code == 200
    job_id = r2.json()["job_id"]

    # Esperar a que termine
    for _ in range(200):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        if data.get("status") in {"completed", "failed"}:
            break

    assert data.get("status") == "completed", data
    # Debe haber al menos un error por el objeto faltante
    errors = data.get("errors") or []
    assert any(e.get("object_id") == missing_id for e in errors)


def test_batch_invariants_poll_timeout_short_window(monkeypatch):
    client = _build_minimal_app()

    # Parcheamos el worker para simular procesamiento lento y no finalizar dentro de la ventana de polling
    def slow_process(job_id: str, object_ids: list[str], chunk_size: int = 50):
        time.sleep(0.2)  # Simula un job que tarda más que nuestra ventana de polling
        # No cambia el estado del job; permanece en 'pending' y con progreso 0
    monkeypatch.setattr("app.routers.mathlab._process_batch_invariants", slow_process)

    # Registramos algunos números (payload barato) para construir un lote
    ids = []
    for v in [2, 3, 5]:
        r = client.post(f"/mathlab/numbers/register?value={v}")
        assert r.status_code == 200
        ids.append(r.json()["object_id"])  # mantener consistencia con endpoints

    # Enviamos el job
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": ids})
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Polling corto: esperamos que NO llegue a finished/failed en esta breve ventana
    deadline = time.time() + 0.05
    last_status = None
    while time.time() < deadline:
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        last_status = data["status"]
        if last_status in ("finished", "failed"):
            break
        time.sleep(0.005)

    # Debe estar pendiente o en progreso, pero no terminado
    assert last_status in ("pending", "running")


def test_batch_invariants_partial_error_invalid_payload():
    client = _build_minimal_app()

    # Registramos un grafo válido pequeño
    valid_graph = {
        "type": "graph",
        "nodes": [0, 1, 2],
        "edges": [[0, 1], [1, 2]],
        "directed": False,
    }
    r1 = client.post("/mathlab/objects/register", json=valid_graph)
    assert r1.status_code == 200
    gid_valid = r1.json()["object_id"]

    # Usamos un ID de objeto que no existe para forzar un error real
    invalid_id = "nonexistent-object-id-12345"

    # Enviamos ambos en el mismo job
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": [gid_valid, invalid_id]})
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Poll hasta finalizar
    for _ in range(200):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        if data["status"] in ("completed", "failed"):
            break
        time.sleep(0.005)

    assert data["status"] == "completed"
    assert data["total"] == 2
    # Debe haberse registrado al menos un error (el objeto inexistente)
    assert isinstance(data.get("errors"), list)
    assert len(data["errors"]) >= 1
    # Verificamos que el error sea por objeto no encontrado
    assert any("not found" in error.get("error", "").lower() for error in data["errors"])

    # Registramos un grafo inválido (payload vacío) que debe provocar error en invariants
    invalid_graph = {}
    r2 = client.post("/mathlab/objects/register", json={"type": "graph"})  # grafo sin datos
    assert r2.status_code == 200
    gid_invalid = r2.json()["object_id"]

    # Enviamos ambos en el mismo job
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": [gid_valid, gid_invalid]})
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Poll hasta finalizar
    for _ in range(200):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        if data["status"] in ("finished", "failed"):
            break
        time.sleep(0.005)

    assert data["status"] == "finished"
    assert data["total"] == 2
    # Debe haberse registrado al menos un error (el grafo inválido)
    assert isinstance(data.get("errors"), list)
    assert len(data["errors"]) >= 1


def test_batch_invariants_large_batch_numbers():
    client = _build_minimal_app()

    # Registramos un lote grande de números (invariantes baratos)
    n = 150
    ids = []
    for v in range(1, n + 1):
        r = client.post(f"/mathlab/numbers/register?value={v}")
        assert r.status_code == 200
        ids.append(r.json()["object_id"])

    # Enviamos job
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": ids})
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Poll hasta finalizar
    for _ in range(1000):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        if data["status"] in ("finished", "failed"):
            break
        time.sleep(0.005)

    assert data["status"] == "finished"
    assert data["total"] == n
    assert data["processed"] == n
    assert data.get("errors") in ([], None) or len(data.get("errors", [])) == 0