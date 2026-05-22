# AXIOM META 4 - Uncertainty Quantification Guide

## 1. Purpose
To provide quantitative and reproducible estimates of uncertainty for PINN solutions and scientific models, allowing for:
- Evaluating prediction reliability.
- Prioritizing domain regions for adaptive refinement.
- Integrating physical + statistical validation pipelines.
- Informing risk-based clinical/industrial decisions.

## 2. Components
| Component | File | Function | Status |
|-----------|------|----------|--------|
| UncertaintyQuantificationService | `app/uncertainty_quantification.py` | Main orchestration | Active |
| FiducialInferenceQuantifier | idem | Parametric perturbations | Implemented |
| BootstrapQuantifier | idem | Resampling with replacement | Implemented |
| (Dropout / Ensemble) | idem | Additional methods | Pending stub |
| Scientific AI Integration | `app/services/scientific_ai.py` | API exposure | Integrated |

## 3. Supported Methods
| Method | Technique | Recommended Use | Advantages | Limitations |
|--------|-----------|-----------------|------------|-------------|
| Fiducial | Pseudo-Bayesian perturbation | Smooth PDEs | Fast, stable | Simplified approximation |
| Bootstrap | Statistical resampling | Noisy data / robustness | Percentile intervals | Costly if N is large |
| (Dropout) | MC Dropout | Trained NN models | Scalable | Requires configured training |
| (Ensemble) | Multiple models | High criticality | Better calibrated estimation | Training cost |

## 4. Operational Workflow
1. Define configuration (pde_type, method, num_samples, etc.).
2. Generate test points (or provide `test_points`).
3. Execute quantification -> produces prediction distribution.
4. Calculate metrics: variance, entropy, coverage, sharpness, calibration error.
5. Integrate into validation / adaptive refinement selection.

## 5. Request Example (Fiducial)
```json
{
  "method": "fiducial",
  "pde_type": "heat",
  "num_samples": 500,
  "confidence_level": 0.95,
  "num_test_points": 400
}
```

## 6. Key Metrics
| Metric | Definition | Interpretation |
|--------|------------|----------------|
| prediction_variance | Mean ensemble variance | Global uncertainty |
| coefficient_of_variation | mean(std/|mean|) | Relative stability |
| entropy_uncertainty | Normalized std entropy | Information dispersion |
| sharpness | Mean std | Intrinsic precision (lower is better) |
| calibration_error | Expected std deviation | Calibration quality |
| coverage_probability | % within interval | Should be ≈ confidence level |
| reliability_score | Internal consistency | >0.8 desirable |

## 7. Execution via Service
The service is invoked within `scientific_ai` (under the `uncertainty_quantification` operation).

CLI Example (pseudo):
```python
from app.uncertainty_quantification import UncertaintyQuantificationService
svc = UncertaintyQuantificationService()
result = await svc.process_request({"method":"bootstrap","pde_type":"burgers","bootstrap_iterations":80})
```

## 8. Usage Patterns
| Scenario | Method | Suggested Config |
|----------|--------|------------------|
| Rapid screening | fiducial | num_samples=200 |
| Robust evaluation | bootstrap | bootstrap_iterations=200 |
| Critical deployment (future) | ensemble | ensemble_size=5-10 |
| PINN models with dropout (future) | dropout | dropout_rate=0.05-0.1 |

## 9. Integration with Quality and Validation
| System | Integration | Benefit |
|--------|-------------|---------|
| Blockchain Validation | Hash + validation only if reliability > 0.7 | Avoids storing weak results |
| Integrity Verification | Verifies statistical coherence | Mitigates silent errors |
| Monitoring | Metrics exposure | Degradation trends |
| Scientific AI | Adaptive point selection | Improves efficiency |

## 10. Evolutionary Roadmap
| Phase | Improvement | Status |
|-------|-------------|--------|
| 1 | Fiducial + Bootstrap | Done |
| 2 | Monte Carlo Dropout | Pending |
| 3 | Heterogeneous Ensembles | Pending |
| 4 | Multi-fidelity UQ | Design |
| 5 | Active Learning (acq fn) | Planned |

## 11. Best Practices
- Use bootstrap for domains with discontinuities.
- Validate that `coverage_probability` ≈ expected level (alert if < 0.85 * target).
- Record configurations for reproducibility.
- Keep `test_points` for later analysis.

## 12. Current Limitations
- Simulated PINN models (mock) when real training is unavailable.
- Dropout / Ensemble not yet implemented.
- No full Bayesian calibration.

## 13. Recommended Acceptance Metrics
| Metric | Initial Threshold |
|--------|-------------------|
| reliability_score | ≥ 0.75 |
| coverage_probability | ≥ 0.90 for 0.95 nominal |
| calibration_error | ≤ 0.15 |
| coefficient_of_variation | ≤ 0.4 |

## 14. Executive Summary
The UQ module adds a critical layer of quantitative confidence that allows for prioritizing verification, improving interpretability, and enabling adaptive pipelines. it is an essential component for regulated deployments and environments where traceability and explainability are mandatory.

---
**Status**: Active | **Maturity**: Initial Robust | **Next Priority**: Implement Monte Carlo Dropout + Ensembles.
