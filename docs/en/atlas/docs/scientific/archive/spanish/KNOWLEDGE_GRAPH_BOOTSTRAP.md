> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="knowledge-graph-bootstrap"></a>
# Knowledge Graph Bootstrap

<a id="objetivo"></a>
## Objective
Establish a lightweight base (SQLite + FTS5) that allows progressively building a scientific graph with hypotheses, artifacts, domains, and validation relationships.

<a id="modelo-de-datos-inicial-tablas--json"></a>
## Initial Data Model (Tables / JSON)
| Entity | Key Fields | Description |
|---------|--------------|------------|
| node | id, type, label, metadata_json, created_at | Generic node (hypothesis, dataset, model, metric) |
| edge | id, src_id, dst_id, type, weight, metadata_json, created_at | Directed relationship |
| embedding (future) | node_id, vector, model_ref | Semantic representation |

Indexes: FTS5 on (label, metadata_json) for search.

<a id="tipos-de-nodo-iteración-1"></a>
## Node Types (Iteration 1)
- hypothesis
- service_output
- dataset
- model_artifact
- validation_result
- publication (future)

<a id="tipos-de-edge-iteración-1"></a>
## Edge Types (Iteration 1)
| Type | Semantics |
|------|-----------|
| derives_from | One artifact derives from another |
| supports | Evidence supports hypothesis |
| contradicts | Result contradicts hypothesis |
| validated_by | Result validated by service |
| references | Publication cites node |

<a id="ingesta-inicial"></a>
## Initial Ingestion
1. Export existing hypotheses (table) → nodes
2. Traverse `validation_history` → edges `supports` / `contradicts`
3. Add recent workflow outputs → service_output
4. Register DVC/MLflow artifacts as model_artifact

<a id="api-planeada"></a>
## Planned API
| Method | Route | Description |
|--------|-------|-------------|
| POST | /kg/node | Create node |
| POST | /kg/edge | Create edge |
| GET | /kg/node/{id} | Get node |
| GET | /kg/search?q= | FTS search |
| GET | /kg/subgraph?root=ID&depth=N | Subgraph |

<a id="métricas"></a>
## Metrics
| Metric | Target |
|---------|----------|
| initial_nodes | ≥ 200 |
| average_edges_per_hypothesis | ≥ 5 |
| search_time_ms | < 50ms |
| cross_relationship_completeness | ≥ 60% |

<a id="roadmap"></a>
## Roadmap
| Phase | Deliverable |
|------|---------|
| F1 | Schema + basic CRUD |
| F2 | FTS5 indexing + advanced search |
| F3 | Automatic enrichment (events) |
| F4 | Embeddings + similarity |
| F5 | Publication Generator Integration |

<a id="integraciones-clave"></a>
## Key Integrations
- Cross-Validation Matrix: sources for `supports / contradicts`
- UQ: uncertainty annotations on edges
- Integrity Pipeline: graph snapshot hash

<a id="riesgos"></a>
## Risks
| Risk | Mitigation |
|--------|-----------|
| Node explosion | Retention / compression policies |
| Search performance | Indexes + per-page limits |
| Semantic inconsistency | Controlled list of types |

---
Bootstrap ready for incremental implementation.
