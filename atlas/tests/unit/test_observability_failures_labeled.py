import asyncio
import pytest

from app.services.research_cycle_manager import ResearchCycleManager
from app.observability.metrics import reset_metrics, scrape
import app.observability.metrics as metrics_mod


@pytest.mark.asyncio
async def test_failures_labeled_counter():
    """Fuerza un fallo en hypothesis_generation inyectando domain inválido y verifica labels en failures."""
    reset_metrics()
    mgr = ResearchCycleManager()

    # Domain no soportado dispara error temprano (sin ciclo). Probamos diferente: provocar fallo generando hipótesis.
    # Para provocar fallo: pasar research_question vacía -> start_research_cycle rechaza. Necesitamos un fallo interno.
    # Estrategia: usar domain válido pero monkeypatch a agente para lanzar excepción.
    orig = mgr.hypothesis_agent.process_request

    async def boom(payload):
        if payload.get("action") == "generate_hypothesis":
            raise Exception("forced")
        return await orig(payload)

    mgr.hypothesis_agent.process_request = boom  # type: ignore

    resp = await mgr.start_research_cycle({
        "research_question": "RQ",
        "domain": "materials_science",
        "max_iterations": 0,
    })
    assert resp["success"]

    # Esperar a que la tarea async ejecute y falle
    # Esperar a que el contador etiquetado aparezca en estructura interna
    found = False
    for _ in range(50):
        await asyncio.sleep(0.1)
        series = metrics_mod._COUNTERS.get("atlas_phase_failures_total", {})
        for labelset, val in series.items():
            if dict(labelset).get("phase") == "hypothesis_generation" and dict(labelset).get("domain") == "materials_science" and val >= 1:
                found = True
                break
        if found:
            break
    assert found, "No se observó contador etiquetado de fallo hypothesis_generation"

    # Scrape sanity: debe contener bloque de failures
    assert "# HELP atlas_phase_failures_total" in scrape()
