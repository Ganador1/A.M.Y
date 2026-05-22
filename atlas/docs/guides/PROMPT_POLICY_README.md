## Prompt Registry & Policy Engine (MVP)

Este documento describe las nuevas capacidades introducidas:

### PromptRegistryService
Ubicación: `app/services/prompting/prompt_registry_service.py`

Funciones clave:
- `register(name, version, template, variables, metadata)` registra una plantilla versionada (Jinja2 StrictUndefined).
- `list()` y `get(name, version)` inspeccionan el repositorio.
- `render(name, version, context)` valida variables requeridas y produce el prompt final.
- Auditoría: cada render se agrega en `data/prompt_renders.jsonl` con hash y claves de contexto.

Uso previsto inmediato:
- Unificar prompts de: generación de hipótesis, revisión de literatura, peer review y refinamiento.
- Base para futura capa de A/B testing y ranking semántico.

### PolicyEngineService
Ubicación: `app/services/policy_engine_service.py`

Objetivo: centralizar la decisión de avance en el ciclo científico.

Entradas (scores esperados si disponibles):
`novelty, evidence_strength, methodological_rigor, reproducibility_likelihood, support_score, coverage, diversity`.

Configuración:
- Archivo opcional `policy_config.yaml` con:
  - `weights`: pesos por métrica.
  - `thresholds.approve` y `thresholds.refine`.
  - `required`: lista de métricas obligatorias.

Salida (`decide`):
```json
{
  "success": true,
  "decision": {
    "status": "approve|refine|reject",
    "score": 0.7123,
    "reasons": ["Score 0.712 >= approve 0.7"],
    "raw_scores": { ... },
    "timestamp": "..."
  }
}
```

Auditoría: cada decisión se anexa en `data/policy_decisions.jsonl`.

### Próximos Pasos (Planeado)
1. Integrar PromptRegistry en agentes actuales (reemplazar prompts inline).
2. Conectar PolicyEngine al loop de `research_cycle_manager` para gating automático.
3. Añadir normalización temporal (decay) para `support_score` y `confidence_score` en decisiones.
4. Introducir ranking semántico de herramientas y modelos para selección adaptativa.

### Tests
Ubicaciones:
- `tests/unit/test_prompt_registry_service.py`
- `tests/unit/test_policy_engine_service.py`

Todos los tests actuales pasan (ver CI / ejecución local). Se añadirá cobertura adicional cuando se integre al flujo principal.
