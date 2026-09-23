> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="literature-service--hypothesis-validation"></a>
# Literature Service & Hypothesis Validation

<a id="alcance"></a>
## Scope
- Service: LiteratureService (`app/services/literature/literature_service.py`).
- Clients: `app/integrations/literature_clients.py`.
- Covered sources (unchanged): OpenAlex, Europe PMC, Semantic Scholar, Crossref, PubMed, arXiv, PatentsView, Materials Project, ChEMBL, UniProt, AlphaFold, ClinicalTrials.gov, RCSB PDB, NASA Exoplanet Archive.
- New sources: **Open Targets Platform (GraphQL v4)** and **GWAS Catalog (REST)**.

<a id="integraciones-nuevas"></a>
## New integrations
- **Open Targets Platform**
  - Endpoint: `https://api.platform.opentargets.org/api/v4/graphql`.
  - Methods: `search(query)` returns hits (id, name, entity, description). `get_associated_diseases(ensembl_id)` returns diseases with score.
  - Usage: enabled in `verify_hypothesis_plus` when the topic contains terms: target, disease, gene, drug, association, phenotype, mechanism, inhibitor.
- **GWAS Catalog**
  - Base endpoint: `https://www.ebi.ac.uk/gwas/rest/api`.
  - Method: `search_studies(query)` returns recent studies (limited to `size=k` and uses the HAL feed). Full HATEOAS pending.
  - Usage: enabled in `verify_hypothesis_plus` when the topic contains terms: gwas, variant, snp, trait, association, polymorphism, risk, locus, genotype.

<a id="flujo-verify_hypothesis_plus"></a>
## Flow `verify_hypothesis_plus`
1. Input: `{ action: "verify_hypothesis_plus", hypothesis: { title, variables? } }`.
2. Parallel queries (no await because they are synchronous) to base + conditional sources:
   - Always: academic literature (OpenAlex, Europe PMC, Semantic Scholar, Crossref, PubMed, arXiv), patents, materials, ChEMBL.
   - Conditional by heuristic: ClinicalTrials (clinical words), RCSB PDB and UniProt (protein/structure words), Exoplanets (astronomy words), Open Targets (target/disease words), GWAS (variant/trait words).
3. Scoring: heuristic `_score_support` (title token and variable matches) with limit 1.0.
4. Output: `support_score`, `reasons`, `sources` (top 5 per channel).

<a id="configuración-y-límites"></a>
## Configuration and limits
- HTTP retries and timeouts: `LIT_HTTP_TIMEOUT`, `LIT_HTTP_MAX_RETRIES`, `LIT_HTTP_BACKOFF`.
- Optional UA: `LIT_HTTP_UA`; OpenAlex mailto: `OPENALEX_MAILTO`; PubMed: `NCBI_TOOL`, `NCBI_EMAIL`, `NCBI_API_KEY`.
- Offline mode: `AXIOM_DISABLE_NET=1` returns `{"error": "network_disabled"}` and avoids calls.
- GWAS: the current search does not follow deep HAL links; the initial page limited to `size=k` is served.

<a id="pruebas"></a>
## Tests
- New clients (mocked):
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/integrations/test_new_literature_clients.py`
- Offline literature cache (regression):
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_literature_offline_cache.py`

<a id="pendientes--backlog"></a>
## Pending / backlog
- Expand GWAS to searches by SNP (e.g., `/singleNucleotidePolymorphisms/search/findByGene` and `/associations`).
- Add pagination and rate-limit awareness to Open Targets and GWAS.
- Optional: version results in the offline cache for both clients.
