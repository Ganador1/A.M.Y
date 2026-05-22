# Unified Policy Engine Design

## Objetivo
Sistema centralizado y configurable para tomar decisiones sobre hipótesis científicas y ciclos de investigación. Proporciona salidas explicables (status + razones + contribuciones) y desacopla la lógica de negocio de los pesos/umbrales mediante un archivo YAML versionado.

## Estados de Decisión
- **halt**: detener inmediatamente (riesgo alto o valor compuesto muy bajo)
- **approve**: continuar / promover al siguiente paso
- **refine**: requiere ajustes moderados antes de promover
- **reject**: no procede (insuficiente o contradictorio)

Orden de precedencia: `halt > approve > refine > reject`.

## Métricas Soportadas (ejemplos actuales)
| Métrica | Sentido | Peso (ejemplo) | Notas |
|---------|---------|----------------|-------|
| novelty | + | 0.15 | Innovación perceived |
| evidence_strength | + | 0.20 | Calidad y cantidad de evidencia |
| reproducibility_risk | - | -0.20 | Riesgo (menor mejor) |
| coverage | + | 0.10 | Cobertura de variables/claves |
| diversity | + | 0.05 | Variedad de fuentes/ángulos |
| consistency | + | 0.10 | Coherencia interna |
| peer_review | + | 0.15 | Validación comunitaria |
| methodological_rigor | + | 0.10 | Calidad metodológica |
| safety | + | 0.05 | Riesgos éticos / seguridad |

Los pesos se pueden ajustar en `config/policy_engine_config.yaml`.

## Configuración YAML
```yaml
version: 1
weights: {...}
thresholds:
  approve:
    composite_min: 0.62
    max_reproducibility_risk: 0.50
  refine:
    composite_min: 0.45
    composite_max: 0.65
  halt:
    composite_max: 0.30
    min_reproducibility_risk: 0.80
normalization:
  missing_score_policy: treat_as_neutral
caps:
  max_positive: 1.0
  min_negative: -1.0
logging:
  decisions_path: data/policy_decisions.jsonl
  include_deltas: true
```

### Semántica de Umbrales
- `halt.composite_max`: si el score normalizado cae por debajo ⇒ halt.
- `halt.min_reproducibility_risk`: si el riesgo supera este umbral ⇒ halt.
- `approve.composite_min`: mínimo para aprobar (si no se disparó halt y se cumple el riesgo máximo opcional).
- `refine`: banda intermedia. Si no entra a approve y `composite` dentro del rango ⇒ refine.
- Else ⇒ reject.

## Cálculo del Composite
1. Recorrer métricas definidas en `weights`.
2. Para cada métrica presente: `contrib = peso * valor_capeado`.
3. Sumar contribuciones y normalizar por suma de pesos absolutos:  
   \( composite = \frac{\sum (w_i * v_i)}{\sum |w_i|} \).
4. Métricas ausentes: ignoradas (neutral) salvo política futura distinta.
5. Caps garantizan valores en [-1,1] antes de multiplicar.

## Proceso de Decisión
1. Evaluar reglas de `halt` primero (baja energía y safety-first).
2. Evaluar aprobación con constraints de riesgo.
3. Evaluar rango de refinamiento.
4. Fallback a rechazo.

## Output Estructurado
```json
{
  "status": "approve",
  "composite": 0.625,
  "reasons": ["composite_ok:0.625>=0.62", "repro_risk_ok:0.200<=0.5"],
  "raw_scores": {"novelty":0.8,...},
  "contributions": {"novelty":0.12,"evidence_strength":0.18,...},
  "ordered_factors": ["evidence_strength","peer_review",...],
  "timestamp": "2025-09-14T...",
  "config_version": 1
}
```
`ordered_factors` ordena por |contribución| para explicar dominancia.

## Logging
Formato JSONL en `data/policy_decisions.jsonl` (append-only). Permite:
- Auditoría histórica
- Análisis estadístico / tuning offline
- Detección de drift en distribución de métricas

## Integración en el Agente
El wrapper `policy_decide` dentro de `ScientificHypothesisAgent` expone acción `policy_decide`:
```python
agent.policy_decide({
  "scores": {"novelty":0.8, ...},
  "hypothesis_id": "..."  # opcional
})
```
Esto enriquece con `hypothesis_id` el log para correlacionar decisiones con trayectorias.

## Ejemplo Rápido
```
python - <<'PY'
from app.services.policy_engine_service import policy_engine_service
print(policy_engine_service.decide({
  'novelty':0.7,'evidence_strength':0.8,'reproducibility_risk':0.3,
  'coverage':0.6,'diversity':0.5,'consistency':0.7,'peer_review':0.75,
  'methodological_rigor':0.7,'safety':0.9
}))
PY
```

## Estrategia de Tuning
1. Recolectar N decisiones reales.
2. Calcular distribución de `composite` y tasas (approve/refine/halt/reject).
3. Ajustar `approve.composite_min` buscando target p.ej. 15-25% refine, <10% halt.
4. Ajustar pesos incrementando magnitud de métricas infrarepresentadas (p.ej. safety) sin sobrepasar saturación.
5. Añadir test unitarios para nuevos casos límite.

## Extensiones Planeadas
| Feature | Descripción | Prioridad |
|---------|-------------|-----------|
| Temporal decay | Penalizar hipótesis envejecidas sin nueva evidencia | Media |
| Causal justification | Generar explicación textual chain-of-thought resumida | Alta |
| Dynamic weight adaptation | Reentrenar pesos con feedback humano | Media |
| Semantic similarity guard | Detectar duplicados / near-duplicates y ajustar novelty | Media |
| Risk decomposition | Separar reproducibility_risk en subcomponentes | Baja |
| Config hot-reload API | Endpoint para refrescar config sin reinicio | Media |

## Testing
Archivo: `tests/unit/test_unified_policy_engine.py` cubre:
- approve pathway
- refine band
- halt por riesgo alto
- halt/reject por composite bajo
- logging JSONL

## Buenas Prácticas
- Mantener pesos normalizados (suma de absolutos ≈ 1) para estabilidad interpretativa.
- Acompañar cambios de umbral con ajuste de tests.
- Analizar outliers regularmente (|contrib| dominante > 0.5) ⇒ reconsiderar peso.

## Roadmap Siguiente Iteración
1. Añadir métricas derivadas (e.g. `evidence_velocity`).
2. Persistir versión de plantilla de prompt usada en la hipótesis para correlación.
3. Dashboard ligero (notebook) para histograma de composite y tasas de decisión.

---
**Estado Actual:** Implementación baseline operativa y testeada (5 tests). Lista para integración en flujos avanzados y tuning iterativo.
