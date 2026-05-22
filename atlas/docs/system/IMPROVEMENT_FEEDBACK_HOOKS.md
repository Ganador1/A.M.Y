# Integración de Hooks de Feedback en ResearchCycleManager

Fecha: 2025-09-14
Estado: Implementado

## Objetivo
Registrar métricas normalizadas (accuracy, coherence, scientific_validity) en el pipeline de mejora iterativa al finalizar fases clave del ciclo de investigación para habilitar analítica longitudinal y recomendaciones de optimización.

## Fases Instrumentadas
| Fase | Método | Métrica Principal | Proxy Utilizado |
|------|--------|------------------|-----------------|
| hypothesis_generation | `_phase_hypothesis_generation` | accuracy, coherence | `confidence_score` de hipótesis (coherence = 0.9 * confidence) |
| literature_review | `_phase_literature_review` | accuracy, coherence | cobertura normalizada: `papers_found / 20` (cap 1.0) |
| analysis | `_phase_analysis` | accuracy, coherence | `analysis_result.confidence_score` (coherence = 0.95 * confidence) |
| validation | `_phase_validation` | accuracy, coherence, scientific_validity | `quality_score` (coherence = 0.97 * quality) |

## Implementación
Se añadió helper privado `_record_phase_feedback` que:
- Mapea fase → `AnalysisType` del pipeline iterativo.
- Normaliza valores a rango [0,1].
- Añade contexto (`cycle_id` como `trace_id`, dominio y research_question).
- Usa `getattr` defensivo para tolerar ausencia del módulo de mejora.

```python
await self._record_phase_feedback(cycle, phase="analysis", accuracy=conf, coherence=conf*0.95)
```

## Robustez
- Carga opcional del pipeline (`try/except`).
- Si no está disponible, los hooks son no‑ops silenciosos.
- Manejo de excepciones dentro del helper para no afectar el flujo principal.

## Impacto Esperado
- Activación temprana de cálculo de métricas agregadas tras >=5 muestras por tipo.
- Futuras optimizaciones basadas en correlación de parámetros (ya soportado por pipeline).
- Base para endpoint `/api/improvement/metrics/all` (tarea futura del sprint).

## Próximos Pasos Relacionados
1. Integrar plausibility scoring para enriquecer accuracy/coherence (tarea 2/3 del sprint).
2. Añadir Trace IDs formales y endpoint `/metrics` para visibilidad operacional.
3. Exponer endpoint consolidado de métricas públicas.

---
Documento generado automáticamente como parte del Sprint 1.
