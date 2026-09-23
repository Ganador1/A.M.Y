> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="integración-de-fuentes-de-literatura-y-conocimiento"></a>
# Integration of Literature and Knowledge Sources

This document describes the clients and services for querying scientific literature and related sources (papers, arXiv, PubMed, Semantic Scholar, Crossref), patents (PatentsView), materials (Materials Project), and chemistry (ChEMBL).

<a id="variables-de-entorno"></a>
## Environment variables
- LIT_HTTP_TIMEOUT (seconds, default 10)
- LIT_HTTP_MAX_RETRIES (default 2)
- LIT_HTTP_BACKOFF (seconds, default 0.5)
- LIT_HTTP_UA (User-Agent, default "AXIOM-Atlas/1.0 (+https://example.org)")
- OPENALEX_MAILTO (email for OpenAlex)
- MATERIALS_PROJECT_API_KEY (required for Materials Project)

<a id="clientes-disponibles-appintegrationsliterature_clientspy"></a>
## Available clients (`app/integrations/literature_clients.py`)
- OpenAlexClient.search(query, per_page=10)
- SemanticScholarClient.search(query, limit=10, fields=...)
- CrossrefClient.search(query, rows=10)
- PubMedClient.search(query, db="pubmed", retmax=10)
- ArxivClient.search(query, max_results=10)
- PatentsViewClient.search(query, per_page=5)
- MaterialsProjectClient.search(formula, limit=5)
  - Uses header `X-API-KEY`.
  - If there are no results for `formula`, retries with derived `chemsys`.
- ChemblClient.search(query, limit=5)

<a id="facade"></a>
### Facade
- LiteratureFacade.unified_search(query, k=10): combines OpenAlex, Semantic Scholar, Crossref, PubMed, arXiv with deduplication.
- LiteratureFacade.search_patents(query, k=5)
- LiteratureFacade.search_materials(formula, k=5)
- LiteratureFacade.search_chembl(query, k=5)

<a id="servicio-appservicesliterature_servicepy"></a>
## Service (`app/services/literature_service.py`)
Supported actions:
- search_papers { query, k }
- search_arxiv { query, k }
- search_patents { query, k }
- search_materials { formula, k }
- search_chembl { query, k }
- verify_hypothesis { hypothesis|topic, k }
- verify_hypothesis_plus { hypothesis|topic, k }
  - Combines multiple sources (papers + arXiv + patents + materials + ChEMBL) and reports `support_score`, `reasons`, and `sources`.

<a id="agente-de-hipótesis-appservicesscientific_hypothesis_agentpy"></a>
## Hypothesis Agent (`app/services/scientific_hypothesis_agent.py`)
- New action: `verify_hypothesis_with_knowledge` that calls `verify_hypothesis_plus`.

<a id="ejemplos-rápidos"></a>
## Quick examples
```python
<a id="buscar-materiales-requiere-materials_project_api_key"></a>
# Buscar materiales (requiere MATERIALS_PROJECT_API_KEY)
await LiteratureService().process_request({
  "action": "search_materials", "formula": "LiCoO2", "k": 5
})

<a id="buscar-fármacos-en-chembl"></a>
# Buscar fármacos en ChEMBL
await LiteratureService().process_request({
  "action": "search_chembl", "query": "aspirin", "k": 5
})

<a id="verificación-ampliada"></a>
# Verificación ampliada
await LiteratureService().process_request({
  "action": "verify_hypothesis_plus", "topic": "LiFePO4 cathode stability", "k": 8
})
```

