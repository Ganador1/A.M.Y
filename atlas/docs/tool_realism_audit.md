# Tool Realism Audit

Atlas ahora distingue entre rutas que producen evidencia científica real y rutas que solo aportan contexto, heurística o fallbacks.

## Categorías

- `real_remote`: evidencia obtenida desde APIs, bases de datos o servicios científicos reales.
- `real_local`: computación científica real ejecutada localmente, por ejemplo Qiskit, SciPy o validación estadística.
- `heuristic`: razonamiento asistido por LLM o síntesis que no constituye medición directa.
- `fallback`: degradación controlada cuando una integración real no está disponible.
- `mock`: demos o simulaciones simplificadas que no deben contarse como evidencia.
- `auxiliary`: herramientas útiles para visualización o inventario, pero no para corroborar hipótesis.
- `unavailable`: dependencia o endpoint no disponible.

## Métricas nuevas

El orquestador mantiene métricas nominales para compatibilidad y añade métricas centradas en evidencia real:

- `support_score`: soporte ajustado por realismo. Solo cuenta `real_remote` y `real_local`.
- `nominal_support_score`: soporte heredado, antes de descontar heurísticas y fallbacks.
- `real_coverage`: proporción de rutas exitosas que aportaron evidencia real.
- `real_weighted_coverage`: cobertura ponderada usando solo evidencia real.
- `tool_realism_score`: fracción ponderada de ejecuciones exitosas que fueron realmente científicas.
- `tier_counts`: conteo por categoría de realismo.

## Mejoras implementadas en esta pasada

- `ToolEvidenceOrchestratorService` etiqueta cada tool call con `evidence_tier`, `counts_as_real_evidence`, `realism_factor` y `classification_reason`.
- `MultiAgentCoordinator` incluye esas métricas en artefactos, papers y smokes.
- `scripts/run_ollama_cloud_research_smoke.py` exporta un breakdown completo de realismo por herramienta.
- `MatplotlibService` fuerza la carga del `matplotlib` real desde `site-packages` en vez del stub local del repo.
- `LiteratureFacade` hace lo mismo antes de invocar `mp-api`, evitando falsos fallos por shadowing local.

## Estado actual

- `PaperQA2` sigue en modo `atlas_fallback` salvo que se conecte y configure el backend real del paquete `paper-qa`.
- `MatterGen`, `MatterSim` y `AlphaGenome` siguen preparados como adapters HTTP, pero no cuentan como evidencia real hasta que sus endpoints estén configurados y respondan.
- Las rutas de razonamiento científico con LLM siguen siendo útiles para planificar, pero ya no inflan el `support_score` de evidencia.

## Smoke recomendado

```bash
"/Volumes/Ganador disk/atlas/.venv_new/bin/python" scripts/run_ollama_cloud_research_smoke.py \
  --domain quantum_computing \
  --output logs/agents/ollama_cloud_smoke_realism.json
```

Revisar en el JSON:

- `support_score` vs `nominal_support_score`
- `tool_realism_score`
- `tier_counts`
- `tool_realism_breakdown`
