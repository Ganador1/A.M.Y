# AXIOM META 4 - Arquitectura del Ecosistema

## Visión General por Capas (9)
| # | Capa | Responsabilidad | Estado | Documento Relacionado |
|---|------|-----------------|--------|-----------------------|
| 1 | Interface & API | Routers FastAPI, contratos REST | 95% | API_REFERENCE.md |
| 2 | Hypothesis Core | Ciclo hipótesis, persistencia | 60% | META4_INTEGRATION_INDEX.md |
| 3 | Domain Agents | Servicios científicos especializados | 150% | *Múltiples guías* |
| 4 | Workflow Orchestration | DAG ejecución, plantillas | 85% | META4_INTEGRATION_INDEX.md |
| 5 | Validation & Peer Review | Validaciones cruzadas, consenso | 40% | CROSS_VALIDATION_MATRIX_PLAN.md |
| 6 | Knowledge & RAG | Ontología, embeddings, búsqueda | 5% | KNOWLEDGE_GRAPH_BOOTSTRAP.md |
| 7 | Persistence & Provenance | DVC, MLflow, Blockchain, DB | 80% | DOCS_DVC_E2E.md / BLOCKCHAIN_VALIDATION_GUIDE.md |
| 8 | Publication & Reporting | Generación artículos, empaques | 0% | PUBLICATION_GENERATOR_PLAN.md |
| 9 | Monitoring, Ethics & Compliance | Métricas, alertas, riesgo | 30% | MONITORING_OBSERVABILITY_GUIDE.md / ETHICS_COMPLIANCE_PLAN.md |

## Diagrama Lógico (Texto)
```
[ Clients ]
    ↓
[ FastAPI Routers ] → Auth / Rate Limit → Logging
    ↓
[ Tool Adapter Layer (*futuro*) ]
    ↓
[ Domain Services ] ↔ [Workflow Orchestrator]
    ↓                           ↓
[ Validation Pipeline ]   [ Hypothesis Core ]
    ↓                           ↓
[ Integrity (Blockchain + Provenance) ]
    ↓
[ Storage: DB / DVC / MLflow / Artifacts ]
    ↓
[ Knowledge Graph (futuro) ] → [Publication Generator]
    ↘
    [ Monitoring & Ethics ]
```

## Flujos Clave
### 1. Ejecución Científica
Solicitud API → Orquestador → Servicios → Resultados → UQ + Robustez → Hash → Blockchain → Registro métrico.

### 2. Ciclo de Hipótesis
Crear hipótesis → Enriquecer evidencia (workflows) → Validación cruzada → Métricas consenso → Publicación (futuro).

### 3. Integridad Unificada
Generación artefactos → Hash BLAKE3 → Bloque validación → Anclaje (futuro Merkle) → Auditoría reproducibilidad.

## Puntos de Dolor Actuales
| Área | Problema | Impacto | Solución Propuesta |
|------|----------|---------|--------------------|
| Tool Interface | No existe capa adapter | Duplicación patrones | TOOL_ADAPTER_INTERFACE_SPEC.md |
| Cross Validation | No hay matriz central | Validación inconsistente | CROSS_VALIDATION_MATRIX_PLAN.md |
| Knowledge | Sin grafo/ontología | No reutilización conocimiento | KNOWLEDGE_GRAPH_BOOTSTRAP.md |
| Publicación | Ausente | Sin salida científica formal | PUBLICATION_GENERATOR_PLAN.md |
| Ética | Sin gating riesgo | Riesgo decisiones opacas | ETHICS_COMPLIANCE_PLAN.md |

## Métricas Arquitectónicas
| Métrica | Objetivo 2025Q4 | Fuente |
|---------|-----------------|--------|
| Tiempo medio workflow multi-servicio | < 2s | Profiler |
| % servicios compatibles Adapter | > 70% | Registro adapters |
| Validaciones cruzadas por hipótesis | ≥ 4 dominios | Hypothesis metrics |
| Integridad verificada (bloques) | ≥ 95% | Blockchain logs |
| Cobertura documentación | ≥ 90% directa+indirecta | Coverage doc |

## Roadmap Técnico Sintético
| Trimestre | Entrega Clave |
|-----------|---------------|
| 2025 Q4 | Tool Adapter + Cross Validation MVP |
| 2026 Q1 | Knowledge Graph + Publication MVP |
| 2026 Q2 | Scheduler recursos + Ethics gating |
| 2026 Q3 | Optimización adaptativa full stack |

---
Documento base. Actualizar conforme se completen planes específicos.
