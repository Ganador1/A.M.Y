> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="roadmap-expansión-dataset-plausibility-v4"></a>
# Roadmap Dataset Plausibility Expansion (v4+)

<a id="1-fuentes-externas-adicionales-prioridad--cobertura--campos-clave"></a>
## 1. Additional External Sources (Priority / Coverage / Key Fields)

| Source | Priority | Type | Key fields | Rate limiting / Notes |
|--------|-----------|------|--------------|-----------------------|
| Crossref REST | High | Metadata (multidisciplinary) | title, abstract (sometimes), DOI, issued, container-title, author, reference-count, funder | Respect polite pool with mailto, cursor pagination `rows` (<=1000) |
| Semantic Scholar | High | Metadata + citations | title, abstract, year, citationCount, influentialCitationCount, fieldsOfStudy, authors | Optional key (without key low limit); batch endpoint 100 IDs |
| bioRxiv / medRxiv | High | Biomedical preprints | title, abstract, date, category | Daily/monthly bulk CSV; paginate by date |
| ClinicalTrials.gov | Medium | Clinical trials | brief_title, detailed_description, condition, phase | JSON API; respect date_range filters |
| arXiv (paginated) | Medium | Physics / CS preprints | title, summary, categories, updated | Max 30000 via incremental pagination; respect 3 req/s |
| Patents (Lens.org / USPTO) | Medium | Patents | title, abstract, claims (limited) | Requires registration (Lens) |
| OpenAIRE | Medium | Open access metadata | title, description, subjects, bestaccessright | Use OAI-PMH; incremental harvesting |
| Grants (NIH ExPORTER, EU CORDIS) | Low | Funded projects | project title, abstract, startYear, funding | Annual bulk download |
| GitHub repos (topics) | Exploratory | Associated code | name, description, stars, topics | Search API rate limit (authenticated) |

<a id="2-mejores-prácticas-de-ingesta"></a>
## 2. Ingestion Best Practices

- Robust pagination: loop until exhaustion using cursors (Crossref), `cursor=*` with checkpoints.
- Rate limiting: wrapper with token bucket (e.g. polite: 1–2 rps), exponential backoff (retry 429, 5xx). Max retries 5.
- Local caching: `cache/RAW/<fuente>/<YYYYMMDD>/page_#.json` for reproducibility + SHA256 hash.
- Deduplication: preferred primary key `DOI`; fallback normalized hash: lower(title) + year → sha1.
- Incremental updates: store watermark per source (last timestamp / cursor) in `data/ingestion_state.json`.
- Structured logging: JSON lines in `logs/ingestion_<fecha>.log` with fields {source, page, fetched, retained, duplicates}.
- Normalization: cleaning pipeline (spaces, unicode NFC, truncate >10k chars, remove HTML tags).
- Validations: minimum abstract length 50 chars; language (langdetect fasttext) = en; stopwords ratio filter (0.2–0.8).
- Monitoring: Prometheus-friendly metrics (request counter, errors, average time, throughput). (Optional future).

<a id="3-estrategias-de-etiquetado-más-allá-heurística-actual"></a>
## 3. Labeling Strategies (Beyond current heuristic)

1. Weak Supervision (Snorkel): build LFs (keyword density, statistical numbers, patterns `p < 0.05`, citations `[0-9]`). Combine with mixture modeling.
2. Ensemble disagreement: lightweight models (LR, RF, MLP) and high-entropy examples for review (active learning batch ~200).
3. Prudent self-training: pseudo-label prob >=0.9 and <=0.1, max 2 rounds.
4. Distant supervision: high citationCount + quantitative terms ⇒ raise prob; hype + few figures ⇒ lower prob.
5. Noise filtering: Co-teaching / small-loss + sample weighting by confidence.

<a id="4-nuevas-features-propuestas"></a>
## 4. Proposed New Features

- Embeddings: Sentence-BERT (all-mpnet-base-v2) → vector 768 (PCA to 64).
- Citation features: citationCount, log(1+cit), referenceCount, influential/total ratio.
- Novelty: minimum cosine distance to k neighbors (FAISS index).
- Redundancy / diversity: cluster ID (HDBSCAN) + cluster size.
- Keyword sections: regex ("method", "results", "conclusion").
- Numeric richness: numeric token count / total; percentage count.
- Temporal: year, age, decay `exp(-age/τ)`.
- Journal / source quality proxy: reference-count, funder presence, prestige list.
- Linguistic: lexical diversity, Flesch Reading Ease, avg sentence length.
- Claim hedging vs hype: counts (suggests, may, potential) vs (breakthrough, revolutionary).
- Domain alignment: embedding cosine similarity vs domain centroid.

<a id="5-roadmap-fases-y-métricas"></a>
## 5. Roadmap Phases and Metrics

<a id="fase-0-actual"></a>
### Phase 0 (Current)

- Dataset v3 (500) + multi-model baseline AUC=0.81.

<a id="fase-1-infra-ingesta-eta-3-4-días"></a>
### Phase 1 (Ingestion Infra) (ETA 3-4 days)

- Implement `ingestion/<fuente>.py` modules with pagination, cache, and state.
- Integrate Crossref and Semantic Scholar (meta + citations).
- Goal: +3k new clean records.
- Metrics: domain coverage entropy_norm >=0.92, duplicates <2%.

<a id="fase-2-features--re-entrenamiento-eta-3-días"></a>
### Phase 2 (Features & Retraining) (ETA 3 days)

- Add embeddings + citation & numeric features.
- Retrain; goal valid AUC >=0.84, Brier <=0.15.
- Save minimal Feature Store (parquet) + reproducible script.

<a id="fase-3-etiquetado-avanzado-eta-4-5-días"></a>
### Phase 3 (Advanced Labeling) (ETA 4-5 days)

- Implement Snorkel LFs + label model.
- First active learning cycle: 300 high-entropy examples (simulate gold).
- Goal: AUC lift +0.02 (>=0.86), ECE calibration <=0.06.

<a id="fase-4-escalado--calidad-eta-1-semana"></a>
### Phase 4 (Scaling & Quality) (ETA 1 week)

- Add bioRxiv/medRxiv + ClinicalTrials + paginated arXiv.
- FAISS index for novelty & redundancy sampling.
- Goal: dataset ~15k records, entropy_norm >=0.94.

<a id="fase-5-robustez-y-mantenimiento-eta-continuo"></a>
### Phase 5 (Robustness and Maintenance) (ETA continuous)

- Monitor ingestion metrics.
- Scheduled monthly incremental retraining.
- Drift evaluation (JS divergence embedding centroid quarterly).

<a id="6-riesgos-y-mitigaciones"></a>
## 6. Risks and Mitigations

| Risk | Impact | Mitigation |
|--------|---------|------------|
| Rate limit / blocking | High | Backoff + clear User-Agent + mailto, strong cache |
| Hidden duplicates (light titles) | Medium | Fuzzy dedup (Levenshtein <0.1 ratio) pre-merge |
| High label noise | High | Snorkel + co-teaching + weighting |
| Future domain imbalance | Medium | Stratified sampler + minimum quotas |
| Feature set growth ⇒ overfitting | Medium | Regularization + ablation + Shapley |
| Embedding cost | Low | Adaptive batch + embedding cache |
| Temporal semantic drift | Medium | Sliding window retrain + monitoring |

<a id="7-métricas-de-éxito-agregadas"></a>
## 7. Aggregated Success Metrics

- Final target valid AUC ≥0.87.
- Normalized domain entropy ≥0.94.
- ECE ≤0.05 after calibration (Platt / Isotonic).
- Duplicates (DOI / title-year hash) <1%.
- Citation coverage: ≥85% instances with citationCount available.

<a id="8-próximos-pasos-inmediatos"></a>
## 8. Immediate Next Steps

1. Create folder `ingestion/` and skeleton `base_fetcher.py`.
2. Implement Crossref + caching.
3. Add state persistence and script `update_dataset.py`.
4. Add embedding extraction (`build_features_v4.py`).
5. Prepare first Phase 1 experiment.

---
Auto-generated document current date.
