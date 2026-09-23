import asyncio
import re
import pytest

from app.services.research_cycle_manager import ResearchCycleManager
from app.observability.metrics import reset_metrics, scrape


@pytest.mark.asyncio
async def test_active_cycles_gauge_increments_and_decrements():
    """Verifica que atlas_active_cycles gauge sube al iniciar y baja al completar/fallar.

    Escenario:
      - max_iterations=0 fuerza salida rápida tras generar hipótesis (ciclo corto)
      - Se esperan dos series: sin labels y con label domain.
    """
    reset_metrics()
    mgr = ResearchCycleManager()

    # Inicia ciclo (async create_task interno). Domain soportado.
    resp = await mgr.start_research_cycle({
        "research_question": "Test gauge",
        "domain": "materials_science",
        "max_iterations": 0,  # refinamiento prácticamente inmediato
        "convergence_threshold": 0.9,
    })
    assert resp["success"]

    # Esperar a que al menos llegue a la fase inicial y gauge se incremente
    await asyncio.sleep(0.1)
    text = scrape()
    # Debe existir gauge con valor 1 (global y etiquetado)
    assert "# TYPE atlas_active_cycles gauge" in text
    assert re.search(r"atlas_active_cycles 1(\.0)?", text)
    assert re.search(r"atlas_active_cycles\{domain=\"materials_science\"\} 1(\.0)?", text)

    # Esperar a finalización (corto, ya que max_iterations=0 reduce loop)
    for _ in range(50):  # ~5s worst-case
        await asyncio.sleep(0.1)
        text = scrape()
        # Cuando termine debe decrementar a 0
        if re.search(r"atlas_active_cycles 0(\.0)?", text):
            break
    else:
        pytest.fail("Gauge no volvió a 0 tras esperar")

    # Validar también serie etiquetada volvió a 0
    assert re.search(r"atlas_active_cycles 0(\.0)?", text)
    assert re.search(r"atlas_active_cycles\{domain=\"materials_science\"\} 0(\.0)?", text)

    # No debe haber valores negativos
    assert not re.search(r"atlas_active_cycles -", text)
