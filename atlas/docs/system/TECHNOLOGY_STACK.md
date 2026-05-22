# Technology Stack Detallado

## Capas Principales
| Capa | Herramientas / Libs | Rol |
|------|---------------------|-----|
| Orquestación | Python 3.13, Asyncio | Flujo principal |
| API / Servicios | (Potencial FastAPI), routers internos | Exposición lógica |
| Cómputo Científico | NumPy, SciPy, SymPy, scikit-learn, PyTorch | Núcleo analítico |
| Optimización | Bayesian (propio), Surrogates, Adaptive Loss | Eficiencia y tuning |
| GPU / Aceleración | CUDA (detección), PyTorch backend | Paralelismo |
| Distribuido | Gestión interna (distributed_manager.py) | Escalado horizontal |
| Observabilidad | Métricas personalizadas, logging estructurado | Visibilidad |
| Integridad | Hashing SHA256, Blockchain simulado | Trazabilidad |
| Datos | Archivos locales + potencial SQLite/Parquet | Persistencia ligera |
| Conocimiento | Plan: SQLite FTS5 + embeddings | Búsqueda semántica |
| Publicación | Generador IMRaD (plan) | Difusión reproducible |

## Versionado y Compatibilidad (Objetivos)
| Componente | Versión Objetivo | Notas |
|-----------|------------------|-------|
| Python | 3.13.x | Baseline actual |
| NumPy | >=1.26 | Consistencia con PyTorch |
| PyTorch | 2.x | GPU y kernels |
| SciPy | >=1.11 | Funciones avanzadas |
| scikit-learn | >=1.4 | Modelos base |
| SymPy | >=1.12 | Álgebra simbólica |

## Patrones Arquitectónicos
| Patrón | Uso |
|--------|-----|
| Strategy | Selección de optimizadores |
| Observer | Alertas y métricas |
| Adapter (plan) | Interfaz homogénea servicios |
| Pipeline | Flujo datos-modelo-publicación |
| Command (implícito) | Operaciones científicas discretas |

## Seguridad y Cumplimiento
- Hash de configuraciones
- Validación de integridad en cadena
- Plan: capas de roles + registro ético

## Observabilidad
| Métrica | Fuente |
|--------|--------|
| latency_stage | performance_profiler |
| gpu_utilization | gpu_manager |
| robustness_score | robustness_metrics |
| integrity_hash_mismatch | integrity_verification |

## Roadmap Técnico
| Fase | Entrega |
|------|---------|
| Q4 2025 | Tool Adapter + Unified Integrity Flow |
| Q1 2026 | Knowledge Embeddings + Meta Learning |
| Q2 2026 | Edge Deploy + Advanced Scheduling |

## Déficits Actuales
| Área | Gap | Mitigación |
|------|-----|-----------|
| Persistencia robusta | Falta DB transaccional | Evaluar PostgreSQL opcional |
| Scheduling | No hay cola formal | Añadir lightweight scheduler |
| Autenticación | No implementada | Integrar capa tokens |
| Métricas estándar | Sin OpenTelemetry | Evaluar exportador OTLP |

---
Documento inicial del stack completado.
