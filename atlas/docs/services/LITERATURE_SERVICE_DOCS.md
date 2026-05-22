# Literature Service & Hypothesis Validation

## Alcance
- Servicio: LiteratureService (`app/services/literature/literature_service.py`).
- Clientes: `app/integrations/literature_clients.py`.
- Fuentes cubiertas (sin cambios): OpenAlex, Europe PMC, Semantic Scholar, Crossref, PubMed, arXiv, PatentsView, Materials Project, ChEMBL, UniProt, AlphaFold, ClinicalTrials.gov, RCSB PDB, NASA Exoplanet Archive.
- Fuentes nuevas: **Open Targets Platform (GraphQL v4)** y **GWAS Catalog (REST)**.

## Integraciones nuevas
- **Open Targets Platform**
  - Endpoint: `https://api.platform.opentargets.org/api/v4/graphql`.
  - Métodos: `search(query)` devuelve hits (id, name, entity, description). `get_associated_diseases(ensembl_id)` devuelve enfermedades con score.
  - Uso: activado en `verify_hypothesis_plus` cuando el tópico contiene términos: target, disease, gene, drug, association, phenotype, mechanism, inhibitor.
- **GWAS Catalog**
  - Endpoint base: `https://www.ebi.ac.uk/gwas/rest/api`.
  - Método: `search_studies(query)` devuelve los estudios recientes (se limita a `size=k` y usa el feed HAL). HATEOAS completo pendiente.
  - Uso: activado en `verify_hypothesis_plus` cuando el tópico contiene términos: gwas, variant, snp, trait, association, polymorphism, risk, locus, genotype.

## Flujo `verify_hypothesis_plus`
1. Entrada: `{ action: "verify_hypothesis_plus", hypothesis: { title, variables? } }`.
2. Consultas paralelas (sin await porque son sincrónicas) a fuentes base + condicionales:
   - Siempre: literatura académica (OpenAlex, Europe PMC, Semantic Scholar, Crossref, PubMed, arXiv), patentes, materiales, ChEMBL.
   - Condicionales por heurística: ClinicalTrials (palabras clínicas), RCSB PDB y UniProt (palabras proteína/estructura), Exoplanets (palabras astronomía), Open Targets (palabras diana/enfermedad), GWAS (palabras variante/trait).
3. Scoring: heurística `_score_support` (coincidencias de tokens del título y variables) con límite 1.0.
4. Salida: `support_score`, `reasons`, `sources` (top 5 por canal).

## Configuración y límites
- Retries y timeouts HTTP: `LIT_HTTP_TIMEOUT`, `LIT_HTTP_MAX_RETRIES`, `LIT_HTTP_BACKOFF`.
- UA opcional: `LIT_HTTP_UA`; OpenAlex mailto: `OPENALEX_MAILTO`; PubMed: `NCBI_TOOL`, `NCBI_EMAIL`, `NCBI_API_KEY`.
- Modo offline: `AXIOM_DISABLE_NET=1` devuelve `{"error": "network_disabled"}` y evita llamadas.
- GWAS: la búsqueda actual no sigue enlaces HAL profundos; se sirve la página inicial limitada a `size=k`.

## Pruebas
- Clientes nuevos (mocked):
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/integrations/test_new_literature_clients.py`
- Caché offline de literatura (regresión):
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_literature_offline_cache.py`

## Pendientes / backlog
- Expandir GWAS a búsquedas por SNP (e.g., `/singleNucleotidePolymorphisms/search/findByGene` y `/associations`).
- Añadir paginación y rate-limit awareness a Open Targets y GWAS.
- Opcional: versionar resultados en caché offline para ambos clientes.
