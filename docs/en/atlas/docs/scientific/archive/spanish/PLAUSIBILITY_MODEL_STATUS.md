> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="estado-actual-del-modelo-de-plausibility-v2"></a>
# Current State of the Plausibility Model (v2)

<a id="resumen"></a>
## Summary
Migrated from the initial version (v1) with signal leakage to a v2 version:
- Removal of feature `confidence_score` (source of leakage).
- Weakly-supervised labeling by quantiles per domain (instead of global) to improve diversity.
- Inclusion of domain one-hot and diversity metrics (normalized entropy) for tracking.
- Service refactor removing recursion and stabilizing the feature pipeline.

<a id="artefactos-principales"></a>
## Main Artifacts
- Dataset v2: `data/plausibility_training_v2.jsonl` (180 rows)
- Legacy dataset v1: `data/plausibility_training.jsonl`
- Model: `models/plausibility_model.joblib`
- Scaler: `models/plausibility_scaler.joblib`
- Training metrics: `metrics/plausibility_training_metrics.json`
- Evaluation v2: `metrics/plausibility_eval_v2.json`
- Updated evaluation script: `evaluate_plausibility_model.py` (argument `--dataset`)

<a id="features-actuales-v2-18"></a>
## Current Features (v2 ~18)
Base heuristics + adjustments + domains (one-hot):
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
12-18. domain_{ai,biology,chemistry,energy,materials,medical,physics} (names may vary vs actual current dataset; adjust if different)

Note: `confidence_score` was removed. If it appears in the legacy dataset it is NOT used in v2 training.

<a id="métricas-v2"></a>
## Metrics (v2)
Training (see metrics file, possible moderate overfitting):
- AUC_train ≈ 0.9451
- Accuracy_train ≈ 0.9167
- F1_train ≈ 0.8148
- Brier_train ≈ 0.0892

Cross-validation (5 folds) – high variance (one weak fold):
- AUC_cv_range ≈ [0.788, 0.983]
- F1_cv_low_in_fold_min ≈ 0.34

Evaluation (re-score dataset v2 with service):
- AUC_eval ≈ 0.2852
- Accuracy_eval ≈ 0.2333
- F1_eval ≈ 0.3551
- Brier_eval ≈ 0.3595

The sharp drop in eval vs train/cv metrics indicates: (1) Labeling noise / instability, (2) Possible misalignment between heuristic and learned signal without the leakage feature, (3) Need for a real holdout and/or re-balance.

<a id="diversidad-de-dominios-dataset-v2"></a>
## Domain Diversity (dataset v2)
Distribution (domain_counts):
```
materials_science: 85
drug_discovery: 30
energy_storage: 60
neuroscience: 5
```
Normalized entropy ≈ 0.807 (over 4 domains with strong imbalance: materials & energy dominate, neuroscience underrepresented).

<a id="riesgos--observaciones-clave"></a>
## Risks / Key Observations
- High inter-fold variance: scarce data + severe imbalance.
- Weak labeling (quantiles) generates possibly noisy labels especially in minority domains.
- Lack of evaluation on a truly independent external set (current eval is re-score, not holdout).
- 'neuroscience' domain insufficient (n=5) produces instability.
- No post-training calibration (temperature placeholder not adjusted).

<a id="próximas-acciones-recomendadas-prioridad"></a>
## Recommended Next Actions (Priority)
1. Collect/Generate more examples in minority domains (>=30 each) to stabilize folds.
2. Create a holdout split stratified by domain and label before any tuning.
3. Introduce semantic embedding models (small sentence-transformers) for dense features and real similarity penalty.
4. Implement calibration (Isotonic or Platt) after defining holdout.
5. Analyze feature importance (permutation) and remove those that do not contribute.
6. Add human labels for a subset (ground-truth) and measure correlation with weak labels.
7. Version experiments (MLflow / JSON lineage) with config hash.
8. Re-balance: over/under sampling per domain or specific multi-field class-weight.
9. Consider conversion to an ordinal problem (low/medium/high) if the binary signal is too noisy.

<a id="checklist-estado-actualizado"></a>
## Updated Current State Checklist
- [x] Removal of signal leakage (confidence_score out of v2 features)
- [x] Service refactor (no recursion)
- [x] Dataset v2 generated
- [x] Model v2 training
- [x] Updated evaluation script (domains + entropy)
- [ ] Real stratified holdout
- [ ] Post-calibration (adjusted temperature / isotonic)
- [ ] Data augmentation for minority domains
- [ ] Real semantic embeddings
- [ ] Human validation labels
- [ ] MLflow tracking / experiment management

<a id="notas"></a>
## Notes
The low eval metrics confirm that the removed leakage was a dominant signal. It is preferable now to build authentic signal (semantic + structural) before superficial optimizations. Prioritize data quality and balance.
