# Plausibility Scoring - Implementación Base
Fecha: 2025-09-14
Estado: ✅ Implementado (versión heurística + persistencia + integrado en feedback pipeline)

## Resumen
Servicio `plausibility_scoring_service.py` que calcula un score compuesto de plausibilidad para hipótesis científicas combinando:
- Cobertura estructural (título, descripción, variables, asunciones)
- Elementos cuantitativos presentes en descripción/resultados esperados
- Penalización por duplicación (vector store embebido hash-based)
- Ajuste por evidencia empírica (conteo + soporte promedio con factor log y ponderación)
- Pesos de dominio y de componentes (config YAML opcional)
- Persistencia en tabla `hypothesis_plausibility_metrics` si se proporciona `hypothesis_uuid`

## Componentes Principales
| Componente | Descripción | Rango |
|------------|-------------|-------|
| title_length | Valida longitud razonable | 0 / 1 |
| description_length | Descripción > 40 chars | 0 / 1 |
| variables_coverage | Variables no vacías y <=12 | -1 / 0 / 1 |
| quant_elements | Presencia de números/% | 0 / 1 |
| assumptions_present | >=1 asunción | 0 / 1 |
| duplication_penalty | Similitud alta en vector store | 0 / -1 / -2 |

Score bruto se recorta a [-2,5] y normaliza linealmente a [0,1]. Ajustes multiplicativos posteriores: evidencia y peso de dominio.

## Evidencia
- Tests unitarios: `tests/unit/test_plausibility_scoring_service.py`
- Persistencia confirmada (inserción en DB y recuperación de componentes)
- Ajuste por evidencia incrementa score (factor >1 cuando existe soporte)

## Extensibilidad Futura
1. Calibración ML (Logistic Regression ya soportada condicionalmente)
2. Añadir factores: novelty (embedding global), complexity_penalty (longitud + nº variables), risk_factor.
3. Integrar con feedback pipeline para emitir ACCURACY_SCORE/COHERENCE_SCORE derivados.

## Integración con Feedback Pipeline
El scoring se invoca ahora en tres momentos del ciclo de investigación:
1. Generación de hipótesis (plausibility_initial)
2. Post-análisis experimental (plausibility_analysis) fusionando composite con confidence del análisis
3. Validación final (plausibility_validation) reforzando métricas finales

Cada invocación inyecta señales derivadas (accuracy/coherence proxies) al Iterative Improvement Pipeline. El composite actúa como refuerzo de ACCURACY_SCORE y una media suavizada se usa como COHERENCE_SCORE.

## Hooks Pendientes
- Registrar métricas de distribución en endpoint `/metrics` una vez creado.

## Riesgos
- Simplificación embedding (hash) limita detección semántica real.
- Penalizaciones pueden dominar con datasets desbalanceados.

## Próximos Pasos
- Implementar capa de embeddings real (sentence-transformers) cuando se incorpore dependencia.
- Añadir validación cruzada de calibración ML.

---
Documento generado automáticamente.
