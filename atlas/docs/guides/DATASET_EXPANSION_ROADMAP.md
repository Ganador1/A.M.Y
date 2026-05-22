# Roadmap Expansión Dataset Plausibility (v4+)

## 1. Fuentes Externas Adicionales (Prioridad / Cobertura / Campos Clave)

| Fuente | Prioridad | Tipo | Campos clave | Rate limiting / Notas |
|--------|-----------|------|--------------|-----------------------|
| Crossref REST | Alta | Metadata (multidisciplina) | title, abstract (a veces), DOI, issued, container-title, author, reference-count, funder | Respetar polite pool con mailto, paginación cursor `rows` (<=1000) |
| Semantic Scholar | Alta | Metadata + citas | title, abstract, year, citationCount, influentialCitationCount, fieldsOfStudy, authors | Key opcional (sin key límite bajo); batch endpoint 100 IDs |
| bioRxiv / medRxiv | Alta | Preprints biomédicos | title, abstract, date, category | Bulk CSV diario/mes; paginar por fecha |
| ClinicalTrials.gov | Media | Ensayos clínicos | brief_title, detailed_description, condition, phase | API JSON; respetar filtros date_range |
| arXiv (paginado) | Media | Preprints físicos / CS | title, summary, categories, updated | Máx 30000 via paginado incremental; respetar 3 req/s |
| Patents (Lens.org / USPTO) | Media | Patentes | title, abstract, claims (limitado) | Requiere registro (Lens) |
| OpenAIRE | Media | Open access metadata | title, description, subjects, bestaccessright | Uso OAI-PMH; recolección incremental |
| Grants (NIH ExPORTER, EU CORDIS) | Baja | Proyectos financiados | project title, abstract, startYear, funding | Descarga bulk anual |
| GitHub repos (topics) | Exploratoria | Código asociado | name, description, stars, topics | Search API rate limit (autenticado) |

## 2. Mejores Prácticas de Ingesta

- Paginación robusta: bucle hasta agotamiento usando cursores (Crossref), `cursor=*` con checkpoints.
- Rate limiting: wrapper con token bucket (ej.  polite: 1–2 rps), backoff exponencial (retry 429, 5xx). Máx reintentos 5.
- Caching local: `cache/RAW/<fuente>/<YYYYMMDD>/page_#.json` para reproducibilidad + hash SHA256.
- Deduplicación: clave primaria preferida `DOI`; fallback hash normalizado: lower(title) + year → sha1.
- Incremental updates: almacenar watermark por fuente (último timestamp / cursor) en `data/ingestion_state.json`.
- Logging estructurado: JSON lines en `logs/ingestion_<fecha>.log` con campos {source, page, fetched, retained, duplicates}.
- Normalización: pipeline de limpieza (espacios, unicode NFC, truncar >10k chars, eliminar HTML tags).
- Validaciones: mínimo longitud abstract 50 chars; idioma (langdetect fasttext) = en; filtro stopwords ratio (0.2–0.8).
- Monitorización: métricas Prometheus-friendly (contador requests, errores, tiempo medio, throughput). (Opcional futuro).

## 3. Estrategias de Etiquetado (Más allá heurística actual)

1. Weak Supervision (Snorkel): construir LFs (keyword density, números estadísticos, patrones `p < 0.05`, citaciones `[0-9]`). Combinar con modelado de mezcla.
2. Ensemble disagreement: modelos ligeros (LR, RF, MLP) y ejemplos con alta entropía para revisión (active learning batch ~200).
3. Self-training prudente: pseudo-etiquetar prob >=0.9 y <=0.1, máximo 2 rondas.
4. Distant supervision: citationCount alto + términos cuantitativos ⇒ subir prob; hype + pocas cifras ⇒ bajar prob.
5. Noise filtering: Co-teaching / small-loss + sample weighting por confianza.

## 4. Nuevas Features Propuestas

- Embeddings: Sentence-BERT (all-mpnet-base-v2) → vector 768 (PCA a 64).
- Citation features: citationCount, log(1+cit), referenceCount, ratio influential/total.
- Novelty: distancia coseno mínima a k vecinos (index FAISS).
- Redundancy / diversity: cluster ID (HDBSCAN) + tamaño cluster.
- Keyword sections: regex ("method", "results", "conclusion").
- Numeric richness: conteo tokens numéricos / total; conteo porcentajes.
- Temporal: year, age, decaimiento `exp(-age/τ)`.
- Journal / source quality proxy: reference-count, funder presence, prestige list.
- Linguistic: lexical diversity, Flesch Reading Ease, avg sentence length.
- Claim hedging vs hype: conteos (suggests, may, potential) vs (breakthrough, revolutionary).
- Domain alignment: similitud coseno embedding vs centroid dominio.

## 5. Roadmap Fases y Métricas

### Fase 0 (Actual)

- Dataset v3 (500) + baseline multi-model AUC=0.81.

### Fase 1 (Infra Ingesta) (ETA 3-4 días)

- Implementar módulos `ingestion/<fuente>.py` con paginación, cache y estado.
- Integrar Crossref y Semantic Scholar (meta + citas).
- Objetivo: +3k nuevos registros limpios.
- Métricas: coverage dominios entropía_norm >=0.92, duplicados <2%.

### Fase 2 (Features & Re-entrenamiento) (ETA 3 días)

- Agregar embeddings + citation & numeric features.
- Retrain; objetivo AUC valid >=0.84, Brier <=0.15.
- Guardar Feature Store minimal (parquet) + script reproducible.

### Fase 3 (Etiquetado Avanzado) (ETA 4-5 días)

- Implementar Snorkel LFs + label model.
- Active learning primer ciclo: 300 ejemplos alta entropía (simular oro).
- Objetivo: lift AUC +0.02 (>=0.86), calibración ECE <=0.06.

### Fase 4 (Escalado & Calidad) (ETA 1 semana)

- Añadir bioRxiv/medRxiv + ClinicalTrials + arXiv paginado.
- Index FAISS para novelty & redundancy sampling.
- Objetivo: dataset ~15k registros, entropía_norm >=0.94.

### Fase 5 (Robustez y Mantenimiento) (ETA continuo)

- Monitoreo métricas ingestion.
- Retraining programado mensual incremental.
- Evaluación drift (JS divergence embedding centroid trimestral).

## 6. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Rate limit / bloqueo | Alto | Backoff + User-Agent claro + mailto, cache fuerte |
| Duplicados ocultos (títulos ligeros) | Medio | Fuzzy dedup (Levenshtein <0.1 ratio) pre-merge |
| Label noise alto | Alto | Snorkel + co-teaching + weighting |
| Desbalance dominio futuro | Medio | Sampler estratificado + quotas mínimas |
| Crecimiento feature set ⇒ sobreajuste | Medio | Regularización + ablation + Shapley |
| Coste embeddings | Bajo | Batch adaptativo + cache embeddings |
| Drift semántico temporal | Medio | Sliding window retrain + monitoreo |

## 7. Métricas de Éxito Agregadas

- AUC valid objetivo final ≥0.87.
- Entropía dominio normalizada ≥0.94.
- ECE ≤0.05 tras calibración (Platt / Isotonic).
- Duplicados (DOI / hash título-año) <1%.
- Coverage citas: ≥85% instancias con citationCount disponible.

## 8. Próximos Pasos Inmediatos

1. Crear carpeta `ingestion/` y esqueleto `base_fetcher.py`.
2. Implementar Crossref + caching.
3. Añadir persistencia estado y script `update_dataset.py`.
4. Añadir extracción embeddings (`build_features_v4.py`).
5. Preparar primer experimento Fase 1.

---
Documento autogenerado fecha actual.
