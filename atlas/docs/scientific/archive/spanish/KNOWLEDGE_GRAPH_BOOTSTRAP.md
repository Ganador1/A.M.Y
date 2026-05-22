# Knowledge Graph Bootstrap

## Objetivo
Establecer una base ligera (SQLite + FTS5) que permita construir progresivamente un grafo científico con hipótesis, artefactos, dominios y relaciones de validación.

## Modelo de Datos Inicial (Tablas / JSON)
| Entidad | Campos Clave | Descripción |
|---------|--------------|------------|
| node | id, type, label, metadata_json, created_at | Nodo genérico (hypothesis, dataset, model, metric) |
| edge | id, src_id, dst_id, type, weight, metadata_json, created_at | Relación dirigida |
| embedding (futuro) | node_id, vector, model_ref | Representación semántica |

Índices: FTS5 sobre (label, metadata_json) para búsqueda.

## Tipos de Nodo (Iteración 1)
- hypothesis
- service_output
- dataset
- model_artifact
- validation_result
- publication (futuro)

## Tipos de Edge (Iteración 1)
| Type | Semántica |
|------|-----------|
| derives_from | Un artefacto deriva de otro |
| supports | Evidencia apoya hipótesis |
| contradicts | Resultado contradice hipótesis |
| validated_by | Resultado validado por servicio |
| references | Publicación cita nodo |

## Ingesta Inicial
1. Exportar hipótesis existentes (tabla) → nodos
2. Recorrer `validation_history` → edges `supports` / `contradicts`
3. Añadir outputs recientes de workflows → service_output
4. Registrar artefactos DVC/MLflow como model_artifact

## API Planeada
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /kg/node | Crear nodo |
| POST | /kg/edge | Crear edge |
| GET | /kg/node/{id} | Obtener nodo |
| GET | /kg/search?q= | Búsqueda FTS |
| GET | /kg/subgraph?root=ID&depth=N | Subgrafo |

## Métricas
| Métrica | Objetivo |
|---------|----------|
| nodos_iniciales | ≥ 200 |
| edges_promedio_por_hipotesis | ≥ 5 |
| tiempo_busqueda_ms | < 50ms |
| completitud_relaciones_cruzadas | ≥ 60% |

## Roadmap
| Fase | Entrega |
|------|---------|
| F1 | Esquema + CRUD básico |
| F2 | Indexado FTS5 + búsqueda avanzada |
| F3 | Enriquecimiento automático (eventos) |
| F4 | Embeddings + similitud |
| F5 | Integración Publication Generator |

## Integraciones Clave
- Cross-Validation Matrix: fuentes para `supports / contradicts`
- UQ: anotaciones de incertidumbre en edges
- Integrity Pipeline: hash de snapshot grafo

## Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Explosión de nodos | Políticas retención / compresión |
| Rendimiento búsquedas | Índices + límites por página |
| Inconsistencia semántica | Lista controlada de types |

---
Bootstrap listo para implementación incremental.
