"""Run Autonomous Hypothesis Pipeline

Este script demuestra un flujo extremo a extremo:
1. Generar razonamiento científico (scientific reasoning) para un problema.
2. Crear hipótesis persistente a partir de un resultado simulado.
3. Añadir evidencia inicial.
4. Añadir refinamiento.
5. Listar hipótesis y mostrar resumen.

Requisitos:
- Servidor FastAPI corriendo (app/main.py o main_refactored.py) en http://localhost:8000
- Endpoint /api/v1/scientific-ai/scientific-reasoning para razonamiento
- Router de persistencia: /api/v1/infrastructure/hypothesis-persistence/* (según registro automático)

"""
from __future__ import annotations
import json
import uuid
import http.client
from typing import Any, Dict

BASE_URL = "localhost:8002"

# Posibles prefijos (depende de cómo quedó montado el router). Intentamos ambos.
PERSISTENCE_BASES = [
    "/api/hypotheses",  # ruta visible en el servidor actual
    "/api/scientific-hypothesis",  # alternativa
    "/api/infrastructure/hypothesis-persistence",  # fallback
    "/api/hypothesis-persistence"  # otro fallback
]
SCIENTIFIC_AI_BASE = "/api/scientific-ai/api/v1/scientific-ai"

def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = http.client.HTTPConnection(BASE_URL, timeout=30)
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload)
    conn.request("POST", path, body=body, headers=headers)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    try:
        return json.loads(data)
    except Exception as e:  # pragma: no cover - robustez de red
        return {"success": False, "status": resp.status, "error": str(e), "raw": data}
    finally:
        conn.close()


def _get(path: str) -> Dict[str, Any]:
    conn = http.client.HTTPConnection(BASE_URL, timeout=30)
    conn.request("GET", path)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    try:
        return json.loads(data)
    except Exception as e:  # pragma: no cover - robustez de red
        return {"success": False, "status": resp.status, "error": str(e), "raw": data}
    finally:
        conn.close()


def choose_persistence_base() -> str:
    for base in PERSISTENCE_BASES:
        # quick heuristic: try list with limit=1
        res = _post(f"{base}/list", {"limit": 1})
        if isinstance(res, dict) and (res.get("success") or res.get("items") is not None or res.get("count") is not None):
            return base
    # default fallback
    return PERSISTENCE_BASES[0]


def run_pipeline():
    print("🚀 Iniciando pipeline autónomo de hipótesis")

    # 1. Scientific reasoning
    reasoning_payload = {"problem": "Analyze potential prime gap patterns under 10^5"}
    reasoning = _post(f"{SCIENTIFIC_AI_BASE}/scientific-reasoning", reasoning_payload)
    print("🧠 Razonamiento científico:", json.dumps(reasoning, indent=2)[:400], "...")

    # 2. Crear hipótesis usando campos derivados del reasoning
    hypothesis_uuid = str(uuid.uuid4())
    hypothesis_payload = {
        "title": "Patrones en gaps de primos",
        "description": "Exploración de estructura en la distribución de gaps de números primos bajo 100k",
        "domain": "mathematics",
        "variables": {"problem": reasoning_payload["problem"]},
        "assumptions": ["Distribución de primos conforme a modelo probabilístico clásico"],
        "expected_outcome": "Identificar tendencia estadística recurrente",
        "confidence_score": 0.15,
        "hypothesis_uuid": hypothesis_uuid,
    }

    persistence_base = choose_persistence_base()
    create_res = _post(f"{persistence_base}/create", hypothesis_payload)
    print("📌 Creación hipótesis:", create_res)
    if not create_res.get("success"):
        print("❌ No se pudo crear la hipótesis. Abortando.")
        return

    # 3. Añadir evidencia básica
    evidence_payload = {
        "hypothesis_uuid": hypothesis_uuid,
        "evidence_type": "literature",
        "details": {"source": "simulated_literature", "notes": "Referencias de distribución de primos"},
        "results": {"observed_pattern": "gap clustering partial"},
        "support_score": 0.3,
    }
    evidence_res = _post(f"{persistence_base}/add-evidence", evidence_payload)
    print("🔍 Evidencia añadida:", evidence_res)

    # 4. Refinamiento
    refinement_payload = {
        "hypothesis_uuid": hypothesis_uuid,
        "changes": {"added_analysis": "Preliminary statistical aggregation"},
        "confidence_delta": 0.05,
        "manual": True,
    }
    refinement_res = _post(f"{persistence_base}/add-refinement", refinement_payload)
    print("🧪 Refinamiento:", refinement_res)

    # 5. Listar hipótesis y obtener detalle
    list_res = _post(f"{persistence_base}/list", {"domain": "mathematics", "limit": 5})
    print("📄 Listado parcial:", json.dumps(list_res, indent=2)[:400], "...")

    get_res = _get(f"{persistence_base}/get/{hypothesis_uuid}")
    print("🔎 Detalle hipótesis:", json.dumps(get_res, indent=2)[:400], "...")

    print("✅ Pipeline autónomo completado (flujo mínimo demostrado)")


if __name__ == "__main__":
    run_pipeline()
