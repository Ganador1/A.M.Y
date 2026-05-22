import pytest
from app.services.advanced_scientific_database_service import advanced_scientific_database_service

# Nota: se asume que la BD y tablas están inicializadas por la infraestructura existente de tests.
# Si fuera necesario un setup explícito, debería añadirse aquí.

@pytest.mark.asyncio
async def test_full_flow_advanced_service():
    svc = advanced_scientific_database_service

    # 1. Crear hipótesis
    create_resp = await svc.process_request({
        "action": "create_hypothesis",
        "title": "Interacción cuántica de prueba",
        "domain": "physics",
        "description": "Hipótesis de prueba para el servicio avanzado"
    })
    assert create_resp["success"], create_resp
    hyp_uuid = create_resp.get("hypothesis_uuid") or create_resp.get("hypothesis", {}).get("hypothesis_uuid")
    assert hyp_uuid

    # 2. Listar hipótesis
    list_resp = await svc.process_request({
        "action": "list_hypotheses",
        "limit": 10
    })
    assert list_resp["success"], list_resp
    assert any(item["hypothesis_uuid"] == hyp_uuid for item in list_resp["items"])  # type: ignore

    # 3. Obtener hipótesis
    get_resp = await svc.process_request({
        "action": "get_hypothesis",
        "hypothesis_uuid": hyp_uuid
    })
    assert get_resp["success"], get_resp

    # 4. Añadir evidencia
    evidence_resp = await svc.process_request({
        "action": "add_evidence",
        "hypothesis_uuid": hyp_uuid,
        "evidence_type": "literature",
        "details": {"paper": "Test Paper"},
        "results": {"finding": "positive"},
        "support_score": 0.8
    })
    assert evidence_resp["success"], evidence_resp

    # 5. Añadir refinamiento
    refinement_resp = await svc.process_request({
        "action": "add_refinement",
        "hypothesis_uuid": hyp_uuid,
        "changes": {"confidence_adjustment": 0.05},
        "confidence_delta": 0.05,
        "manual": True
    })
    assert refinement_resp["success"], refinement_resp

    # 6. Registrar modelo
    model_resp = await svc.process_request({
        "action": "register_model",
        "name": "test-model",
        "version": "1.0",
        "task": "classification"
    })
    assert model_resp["success"], model_resp

    # 7. Buscar (hypothesis)
    search_h = await svc.process_request({
        "action": "search",
        "target": "hypothesis",
        "query": "cuántica"
    })
    assert search_h["success"], search_h
    assert search_h["count"] >= 1

    # 8. Buscar (model)
    search_m = await svc.process_request({
        "action": "search",
        "target": "model",
        "query": "test-model"
    })
    assert search_m["success"], search_m
    assert any(r.get("kind") == "model" for r in search_m["results"])  # type: ignore

    # 9. Embedding stub
    embed_resp = await svc.process_request({
        "action": "embed_text",
        "text": "Prueba de embeddings",
        "dim": 16
    })
    assert embed_resp["success"], embed_resp
    assert embed_resp["dimension"] == 16
    assert len(embed_resp["embedding"]) == 16

    # 10. Health
    health_resp = await svc.process_request({"action": "health"})
    assert health_resp["success"], health_resp
    assert health_resp["status"] == "ok"
