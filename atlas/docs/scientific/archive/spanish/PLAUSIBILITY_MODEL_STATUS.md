# Estado Actual del Modelo de Plausibility (v2)

## Resumen
Se migró de la versión inicial (v1) con fuga de señal a una versión v2:
- Eliminación del feature `confidence_score` (fuente de leakage).
- Etiquetado weakly-supervised por cuantiles por dominio (en lugar de global) para mejorar diversidad.
- Inclusión de one-hot de dominio y métricas de diversidad (entropía normalizada) para seguimiento.
- Refactor del servicio eliminando recursión y estabilizando pipeline de features.

## Artefactos Principales
- Dataset v2: `data/plausibility_training_v2.jsonl` (180 filas)
- Dataset legado v1: `data/plausibility_training.jsonl`
- Modelo: `models/plausibility_model.joblib`
- Scaler: `models/plausibility_scaler.joblib`
- Métricas entrenamiento: `metrics/plausibility_training_metrics.json`
- Evaluación v2: `metrics/plausibility_eval_v2.json`
- Script evaluación actualizado: `evaluate_plausibility_model.py` (argumento `--dataset`)

## Features Actuales (v2 ~18)
Heurísticos base + ajustes + dominios (one-hot):
1. title_length
2. description_length
3. variables_coverage
4. quant_elements
5. assumptions_present
6. duplication_penalty
7. heuristic_composite
8. evidence_count_norm
9. refinement_count_norm
10. has_expected_outcome
11. text_length_ratio
12-18. domain_{ai,biology,chemistry,energy,materials,medical,physics} (nombres pueden variar vs dataset actual real; ajustar si difiere)

Nota: `confidence_score` fue removido. Si aparece en dataset legado NO se usa en entrenamiento v2.

## Métricas (v2)
Entrenamiento (ver archivo de métricas, posible sobreajuste moderado):
- AUC_train ≈ 0.9451
- Accuracy_train ≈ 0.9167
- F1_train ≈ 0.8148
- Brier_train ≈ 0.0892

Validación cruzada (5 folds) – alta varianza (un fold débil):
- AUC_cv_range ≈ [0.788, 0.983]
- F1_cv_bajo_en_fold_min ≈ 0.34

Evaluación (re-score dataset v2 con servicio):
- AUC_eval ≈ 0.2852
- Accuracy_eval ≈ 0.2333
- F1_eval ≈ 0.3551
- Brier_eval ≈ 0.3595

La caída fuerte de métricas eval vs train/cv indica: (1) Etiquetado noise / inestabilidad, (2) Posible desalineación entre heurístico y señal aprendida sin feature de fuga, (3) Necesidad de holdout real y/o re-balance.

## Diversidad de Dominios (dataset v2)
Distribución (domain_counts):
```
materials_science: 85
drug_discovery: 30
energy_storage: 60
neuroscience: 5
```
Entropía normalizada ≈ 0.807 (sobre 4 dominios con fuerte desequilibrio: materials & energy dominan, neuroscience subrepresentado).

## Riesgos / Observaciones Clave
- Alta varianza inter-fold: data escasa + desbalance severo.
- Etiquetado weak (cuantiles) genera etiquetas posiblemente ruidosas especialmente en dominios minoritarios.
- Falta de evaluación en conjunto externo verdaderamente independiente (actual eval es re-score, no holdout).
- Dominio 'neuroscience' insuficiente (n=5) produce inestabilidad.
- Sin calibración post-entrenamiento (temperature placeholder no ajustado).

## Próximas Acciones Recomendadas (Prioridad)
1. Recolectar/Generar más ejemplos en dominios minoritarios (>=30 cada uno) para estabilizar folds.
2. Crear split holdout estratificado por dominio y label antes de cualquier tuning.
3. Introducir modelos de embeddings semánticos (sentence-transformers pequeño) para features densas y similarity penalty real.
4. Implementar calibración (Isotonic o Platt) tras definir holdout.
5. Analizar importancia de features (permutation) y eliminar los que no contribuyen.
6. Agregar etiquetas humanas para un subconjunto (ground-truth) y medir correlación con weak labels.
7. Versionar experimentos (MLflow / JSON lineage) con hash de config.
8. Re-balance: over/under sampling por dominio o class-weight específico multi-campo.
9. Considerar conversión a problema ordinal (baja/ media/ alta) si la señal binaria es demasiado ruidosa.

## Checklist Estado Actualizado
- [x] Eliminación fuga de señal (confidence_score fuera de features v2)
- [x] Refactor servicio (sin recursión)
- [x] Dataset v2 generado
- [x] Entrenamiento modelo v2
- [x] Evaluación script actualizado (dominios + entropía)
- [ ] Holdout real estratificado
- [ ] Calibración posterior (temperature ajustada / isotonic)
- [ ] Aumento de datos dominios minoritarios
- [ ] Embeddings semánticos reales
- [ ] Etiquetas humanas de validación
- [ ] Tracking MLflow / experiment management

## Notas
Las métricas eval bajas confirman que el leakage removido era una señal dominante. Es preferible ahora construir señal auténtica (semántica + estructura) antes de optimizaciones superficiales. Priorizar calidad y balance de datos.
