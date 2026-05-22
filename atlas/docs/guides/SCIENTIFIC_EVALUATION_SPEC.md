# Scientific Evaluation Service Specification (v0)

## Objetivo
Unificar la evaluación cuantitativa de hipótesis / resultados científicos mediante un conjunto de sub-métricas normalizadas y un score compuesto trazable.

## Componentes Actuales
- novelty (0-1)
- evidence_strength (0-1)
- methodological_rigor (0-1) – heurística interna
- reproducibility_likelihood (0-1) – heurística interna

## Fórmula Compuesta (v0)
```
composite = 0.30 * novelty \
          + 0.30 * evidence_strength \
          + 0.25 * methodological_rigor \
          + 0.15 * reproducibility_likelihood
```
Pesos pensados para dar prioridad a (a) aportación nueva y (b) solidez empírica, manteniendo rigor y reproducibilidad influyentes pero ligeramente por debajo.

## Normalización
Cada sub-métrica se asegura en rango [0,1]. Valores fuera se “clamp” (min(max(x,0),1)).

## Heurísticas Internas (v0)
- methodological_rigor: penaliza alta complejidad sin justificación y baja cobertura de controles.
- reproducibility_likelihood: favorece menor número de pasos críticos, dependencia de herramientas estándar y claridad de variables.

## Integración con Hipótesis
Si se pasa `hypothesis_id` sin `novelty` o `evidence_strength`, se intenta:
- novelty ≈ min(1.0, 0.2 + 0.05 * n_variables)
- evidence_strength ≈ confidence_score (si existe en el registro de la hipótesis)
Esto permite evaluación rápida preliminar antes de cálculos más costosos.

## Campos de Salida
```json
{
  "inputs": { ... originales ... },
  "normalized": {"novelty":0.x, ...},
  "components": {
     "methodological_rigor": {... breakdown ...},
     "reproducibility_likelihood": {... breakdown ...}
  },
  "composite_score": 0.x,
  "weights": {"novelty":0.30, ...},
  "version": "v0"
}
```

## Errores y Validaciones
- Falta de métricas clave -> se infiere si hay `hypothesis_id`, de lo contrario `ValueError` descriptivo en futuras versiones.
- Rango inválido -> se corrige vía clamp y se expone valor corregido en `normalized`.

## Extensiones Planeadas (Roadmap)
1. Persistencia de snapshots (tabla evaluation_records) con fórmula versión.
2. Métrica de Robustness (variación bajo perturbaciones sintéticas).
3. Métrica de Statistical Power (si hay datos crudos disponibles).
4. Ajuste dinámico de pesos vía aprendizaje bayesiano.
5. Export a Decision Ledger (auto-log de evaluaciones > umbral).
6. API para comparar dos evaluaciones y generar explicación diferencial.

## Versionado
Cambios en pesos o incorporación de nuevas métricas incrementarán versión (v1, v2...). Se guardará `formula_hash` (sha256 de estructura pesos+componentes) para reproducibilidad.

## Ejemplo de Uso (pseudo)
```python
svc = ScientificEvaluationService()
res = svc.evaluate({"novelty":0.7, "evidence_strength":0.6})
print(res["composite_score"])  # ~0.65
```

## Notas
Este documento acompaña a la implementación inicial y debe actualizarse con cada cambio de pesos o nuevas métricas.
