#!/usr/bin/env python3
"""
Test simple para probar batch invariants sin dependencias complejas.
"""

import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.mathlab import router as mathlab_router

def test_batch_invariants_partial_error():
    """Test que verifica que el batch invariants maneja correctamente errores parciales."""
    
    # Crear app minimal
    app = FastAPI()
    app.include_router(mathlab_router, prefix='/mathlab')
    client = TestClient(app)

    # Registrar un grafo válido pequeño
    valid_graph = {
        "type": "graph",
        "nodes": [0, 1, 2],
        "edges": [[0, 1], [1, 2]],
        "directed": False,
    }
    r1 = client.post("/mathlab/objects/register", json=valid_graph)
    assert r1.status_code == 200
    gid_valid = r1.json()["object_id"]
    print(f"Valid graph ID: {gid_valid}")

    # Usamos un ID de objeto que no existe para forzar un error real
    invalid_id = "nonexistent-object-id-12345"

    # Enviamos ambos en el mismo job
    r = client.post("/mathlab/batch/invariants/submit", json={"object_ids": [gid_valid, invalid_id]})
    assert r.status_code == 200
    job_id = r.json()["job_id"]
    print(f"Job ID: {job_id}")

    # Poll hasta finalizar
    for i in range(50):
        s = client.get(f"/mathlab/batch/invariants/status/{job_id}")
        assert s.status_code == 200
        data = s.json()
        print(f"Poll {i}: {data['status']}")
        if data["status"] in ("completed", "failed"):
            break
        time.sleep(0.1)

    print(f"Final status: {data}")
    
    assert data["status"] == "completed"
    assert data["total"] == 2
    # Debe haberse registrado al menos un error (el objeto inexistente)
    assert isinstance(data.get("errors"), list)
    assert len(data["errors"]) >= 1
    # Verificamos que el error sea por objeto no encontrado
    assert any("not found" in error.get("error", "").lower() for error in data["errors"])
    
    print("✅ Test passed!")

if __name__ == "__main__":
    test_batch_invariants_partial_error()