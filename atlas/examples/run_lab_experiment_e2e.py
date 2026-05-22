"""
AXIOM Lab E2E Runner (sin HTTP)
Genera una hipótesis con el propio laboratorio y ejecuta un ciclo de investigación completo.
Guarda un reporte JSON en lab_experiment_result.json
"""

import asyncio
import json
import os
from datetime import datetime

# Desactivar DB para entorno local si no está disponible
os.environ.setdefault("ENABLE_DATABASE", "false")
os.environ.setdefault("SKIP_DB_INIT", "1")

from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from app.services.research_cycle_manager import ResearchCycleManager


async def run_experiment():
    agent = ScientificHypothesisAgent()
    manager = ResearchCycleManager()

    domain = "materials_science"
    research_question = "How to improve thermal conductivity in composite materials?"

    # 1) Generar hipótesis
    gen = await agent.process_request({
        "action": "generate_hypothesis",
        "domain": domain,
        "research_question": research_question,
        "context_data": {"material": "polymer composite"}
    })
    assert gen.get("success"), f"Hypothesis generation failed: {gen}"
    hypothesis_id = gen["hypothesis_id"]

    # 2) Iniciar ciclo sobre esa hipótesis usando el manager de ciclos completo
    #    Aquí usamos el ResearchCycleManager que vuelve a generar hipótesis internamente.
    #    Para asegurar continuidad, usamos la ruta de manager con la misma pregunta y dominio.
    cycle_start = await manager.process_request({
        "action": "start_research_cycle",
        "research_question": research_question,
        "domain": domain,
        "max_iterations": 2,
        "convergence_threshold": 0.75,
    })
    assert cycle_start.get("success"), f"Cycle start failed: {cycle_start}"
    cycle_id = cycle_start["cycle_id"]

    # 3) Esperar a que el ciclo termine (manager ejecuta async create_task)
    #    Hacemos polling del estado hasta COMPLETED o FAILED.
    status = None
    for _ in range(120):  # ~120s máx
        st = manager.get_cycle_status({"cycle_id": cycle_id})
        if not st.get("success"):
            await asyncio.sleep(1)
            continue
        status = st.get("status")
        if status in ("completed", "failed"):
            break
        await asyncio.sleep(1)

    # 4) Obtener resultados completos
    results = manager.get_cycle_results({"cycle_id": cycle_id})

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "domain": domain,
        "research_question": research_question,
        "generated_hypothesis": gen,
        "cycle_status": status,
        "cycle_results": results,
    }

    with open("lab_experiment_result.json", "w") as f:
        json.dump(payload, f, indent=2)

    print("✅ Experimento de laboratorio completado.")
    print("📄 Reporte: lab_experiment_result.json")


if __name__ == "__main__":
    asyncio.run(run_experiment())
