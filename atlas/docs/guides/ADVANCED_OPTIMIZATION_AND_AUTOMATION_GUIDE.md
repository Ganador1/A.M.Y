# Guía Unificada: Optimización Avanzada y Automatización

Cubre módulos sin documentación previa dedicada:
- `surrogate_modeling.py`
- `fast_vpinns_accelerator.py`
- `advanced_gpu_optimizer.py`
- `adaptive_loss_optimizer.py`
- `adaptive_energy_sampler.py`
- (Conecta con) `optimization.py`, `bayesian_optimization.py`

## 1. Propósito
Acelerar exploración científica y reducir coste computacional combinando:
1. Modelos sustitutos (surrogates)
2. Aceleradores físicos (FAST-VPINNs)
3. Optimización adaptativa (loss & sampling)
4. Optimización bayesiana para cierre fino

## 2. Componentes
| Área | Módulo | Función Clave | Beneficio |
|------|--------|---------------|-----------|
| Surrogates | surrogate_modeling.py | Entrena aproximaciones rápidas | Reduce tiempos de simulación |
| PINN Accel | fast_vpinns_accelerator.py | Kernel/vectorization tuning | 3-8× speedup inferencia física |
| GPU Optim | advanced_gpu_optimizer.py | Selección heurística backend | Mejor uso memoria y streams |
| Loss Adapt | adaptive_loss_optimizer.py | Reponderación dinámica términos | Mejora convergencia estable |
| Sampler | adaptive_energy_sampler.py | Selección inteligente de batch/región | Enfoca en zonas informativas |
| Bayes Opt | bayesian_optimization.py | Sugerencia parámetros | Minimiza experimentos |

## 3. Flujo Integrado
1. Simulación inicial / PINN base
2. Entrenamiento surrogate (si error < threshold → pasar a producción)
3. Activar Acelerador VPINN para ciclos largos
4. Activar pérdida adaptativa cuando gradientes desequilibrados
5. Activar muestreador adaptativo cuando variance > target
6. Fase final: Optimización Bayesiana de hiper-parámetros
7. Validación → UQ → Robustez → Registro blockchain

## 4. Estrategias Clave
| Problema | Señal Medible | Acción Módulo |
|----------|---------------|---------------|
| Convergencia lenta | Gradiente norm decay < ε | Activar adaptive_loss_optimizer |
| Sobre-coste cómputo | Iter tiempo > p95 histórico | Usar fast_vpinns_accelerator |
| Datos poco informativos | UQ var baja global | adaptive_energy_sampler cambia foco |
| Hiper-parámetros subóptimos | Métrica plateau N iter | bayesian_optimization sugiere | 
| Sobrecarga GPU | Memoria > 85% | advanced_gpu_optimizer reajusta streams |

## 5. Métricas Recomendadas
| Métrica | Objetivo | Fuente |
|---------|----------|--------|
| surrogate_mae | < 5% error relativo | Validación cruzada |
| speedup_factor | >2.5× sostenido | Profiler |
| adaptive_loss_stability | >0.85 | Ratio pasos sin oscilación |
| sampling_efficiency | >0.70 | Información ganada / costo |
| bayes_opt_improvement | >15% respecto baseline | Historial |

## 6. Roadmap
| Fase | Mejora | Estado |
|------|--------|--------|
| Q4 2025 | Surrogates multi-fidelidad | Planificado |
| Q1 2026 | Auto-tuning CUDA kernels | Planificado |
| Q1 2026 | Active learning + UQ cerrado | Planificado |
| Q2 2026 | Integración RL optimización | Exploratorio |

## 7. Riesgos y Mitigaciones
| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| Sesgo surrogate | Resultados erróneos | Validar contra set oro cada N iter |
| Overfitting surrogate | Pérdida generalización | Early stop + regularización |
| Saturación heurísticas GPU | Degradación rendimiento | Fallback config previa |
| Sampleo demasiado agresivo | Pérdida cobertura dominio | Umbral mínimo diversidad |

## 8. Integración con Infraestructura Robusta
- Al finalizar ciclo se generan hashes y se integra flujo blockchain.
- UQ valida que surrogate no supera var tolerada.
- Monitorización anota speedup_factor y drift surrogate.

## 9. Uso Simplificado (Pseudo)
```python
from app.services import surrogate_modeling, bayesian_optimization

sur = surrogate_modeling.train(base_model, data)
if sur.metrics.mae < 0.05:
    accelerated = fast_vpinns_accelerator.wrap(sur)
    tuned = bayesian_optimization.optimize(accelerated, search_space)
```

## 10. Próximos Pasos
1. Implementar registro estructurado de métricas en `metrics.py`
2. Añadir endpoints resumen optimización avanzada
3. Añadir validación automática surrogate vs ground truth

---
Stub inicial completo. Expandir cuando módulos finalicen refactor.
