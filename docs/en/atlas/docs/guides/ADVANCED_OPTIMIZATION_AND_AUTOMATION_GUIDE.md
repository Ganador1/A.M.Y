> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-unificada-optimización-avanzada-y-automatización"></a>
# Unified Guide: Advanced Optimization and Automation

Covers modules without prior dedicated documentation:
- `surrogate_modeling.py`
- `fast_vpinns_accelerator.py`
- `advanced_gpu_optimizer.py`
- `adaptive_loss_optimizer.py`
- `adaptive_energy_sampler.py`
- (Connects with) `optimization.py`, `bayesian_optimization.py`

<a id="1-propósito"></a>
## 1. Purpose
Accelerate scientific exploration and reduce computational cost by combining:
1. Surrogate models
2. Physical accelerators (FAST-VPINNs)
3. Adaptive optimization (loss & sampling)
4. Bayesian optimization for fine closure

<a id="2-componentes"></a>
## 2. Components
| Area | Module | Key Function | Benefit |
|------|--------|---------------|-----------|
| Surrogates | surrogate_modeling.py | Trains fast approximations | Reduces simulation times |
| PINN Accel | fast_vpinns_accelerator.py | Kernel/vectorization tuning | 3-8× physical inference speedup |
| GPU Optim | advanced_gpu_optimizer.py | Heuristic backend selection | Better memory and stream usage |
| Loss Adapt | adaptive_loss_optimizer.py | Dynamic term reweighting | Improves stable convergence |
| Sampler | adaptive_energy_sampler.py | Intelligent batch/region selection | Focuses on informative zones |
| Bayes Opt | bayesian_optimization.py | Parameter suggestion | Minimizes experiments |

<a id="3-flujo-integrado"></a>
## 3. Integrated Flow
1. Initial simulation / base PINN
2. Surrogate training (if error < threshold → move to production)
3. Activate VPINN Accelerator for long cycles
4. Activate adaptive loss when gradients are unbalanced
5. Activate adaptive sampler when variance > target
6. Final phase: Bayesian hyperparameter optimization
7. Validation → UQ → Robustness → Blockchain logging

<a id="4-estrategias-clave"></a>
## 4. Key Strategies
| Problem | Measurable Signal | Module Action |
|----------|---------------|---------------|
| Slow convergence | Gradient norm decay < ε | Activate adaptive_loss_optimizer |
| Compute overcost | Iter time > historical p95 | Use fast_vpinns_accelerator |
| Uninformative data | Low global UQ var | adaptive_energy_sampler changes focus |
| Suboptimal hyperparameters | Metric plateau N iter | bayesian_optimization suggests | 
| GPU overload | Memory > 85% | advanced_gpu_optimizer readjusts streams |

<a id="5-métricas-recomendadas"></a>
## 5. Recommended Metrics
| Metric | Objective | Source |
|---------|----------|--------|
| surrogate_mae | < 5% relative error | Cross-validation |
| speedup_factor | >2.5× sustained | Profiler |
| adaptive_loss_stability | >0.85 | Ratio of steps without oscillation |
| sampling_efficiency | >0.70 | Information gained / cost |
| bayes_opt_improvement | >15% vs baseline | History |

<a id="6-roadmap"></a>
## 6. Roadmap
| Phase | Improvement | Status |
|------|--------|--------|
| Q4 2025 | Multi-fidelity surrogates | Planned |
| Q1 2026 | Auto-tuning CUDA kernels | Planned |
| Q1 2026 | Active learning + closed UQ | Planned |
| Q2 2026 | RL optimization integration | Exploratory |

<a id="7-riesgos-y-mitigaciones"></a>
## 7. Risks and Mitigations
| Risk | Impact | Mitigation |
|--------|---------|-----------|
| Surrogate bias | Erroneous results | Validate against gold set every N iter |
| Surrogate overfitting | Loss of generalization | Early stop + regularization |
| GPU heuristic saturation | Performance degradation | Fallback to previous config |
| Overly aggressive sampling | Loss of domain coverage | Minimum diversity threshold |

<a id="8-integración-con-infraestructura-robusta"></a>
## 8. Integration with Robust Infrastructure
- At the end of the cycle, hashes are generated and integrated into the blockchain flow.
- UQ validates that the surrogate does not exceed tolerated var.
- Monitoring records speedup_factor and surrogate drift.

<a id="9-uso-simplificado-pseudo"></a>
## 9. Simplified Use (Pseudo)
```python
from app.services import surrogate_modeling, bayesian_optimization

sur = surrogate_modeling.train(base_model, data)
if sur.metrics.mae < 0.05:
    accelerated = fast_vpinns_accelerator.wrap(sur)
    tuned = bayesian_optimization.optimize(accelerated, search_space)
```

<a id="10-próximos-pasos"></a>
## 10. Next Steps
1. Implement structured metric logging in `metrics.py`
2. Add advanced optimization summary endpoints
3. Add automatic surrogate vs ground truth validation

---
Initial stub complete. Expand when modules finish refactoring.
