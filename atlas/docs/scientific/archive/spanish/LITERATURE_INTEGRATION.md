# Integración de Fuentes de Literatura y Conocimiento

Este documento describe los clientes y servicios para consultar literatura científica y fuentes afines (papers, arXiv, PubMed, Semantic Scholar, Crossref), patentes (PatentsView), materiales (Materials Project) y química (ChEMBL).

## Variables de entorno
- LIT_HTTP_TIMEOUT (segundos, por defecto 10)
- LIT_HTTP_MAX_RETRIES (por defecto 2)
- LIT_HTTP_BACKOFF (segundos, por defecto 0.5)
- LIT_HTTP_UA (User-Agent, por defecto "AXIOM-Atlas/1.0 (+https://example.org)")
- OPENALEX_MAILTO (correo para OpenAlex)
- MATERIALS_PROJECT_API_KEY (requerida para Materials Project)

## Clientes disponibles (`app/integrations/literature_clients.py`)
- OpenAlexClient.search(query, per_page=10)
- SemanticScholarClient.search(query, limit=10, fields=...)
- CrossrefClient.search(query, rows=10)
- PubMedClient.search(query, db="pubmed", retmax=10)
- ArxivClient.search(query, max_results=10)
- PatentsViewClient.search(query, per_page=5)
- MaterialsProjectClient.search(formula, limit=5)
  - Usa cabecera `X-API-KEY`.
  - Si no hay resultados por `formula`, reintenta con `chemsys` derivado.
- ChemblClient.search(query, limit=5)

### Facade
- LiteratureFacade.unified_search(query, k=10): combina OpenAlex, Semantic Scholar, Crossref, PubMed, arXiv con deduplicado.
- LiteratureFacade.search_patents(query, k=5)
- LiteratureFacade.search_materials(formula, k=5)
- LiteratureFacade.search_chembl(query, k=5)

## Servicio (`app/services/literature_service.py`)
Acciones soportadas:
- search_papers { query, k }
- search_arxiv { query, k }
- search_patents { query, k }
- search_materials { formula, k }
- search_chembl { query, k }
- verify_hypothesis { hypothesis|topic, k }
- verify_hypothesis_plus { hypothesis|topic, k }
  - Combina múltiples fuentes (papers + arXiv + patentes + materiales + ChEMBL) y reporta `support_score`, `reasons` y `sources`.

## Agente de Hipótesis (`app/services/scientific_hypothesis_agent.py`)
- Nueva acción: `verify_hypothesis_with_knowledge` que llama a `verify_hypothesis_plus`.

## Ejemplos rápidos
```python
# Buscar materiales (requiere MATERIALS_PROJECT_API_KEY)
await LiteratureService().process_request({
  "action": "search_materials", "formula": "LiCoO2", "k": 5
})

# Buscar fármacos en ChEMBL
await LiteratureService().process_request({
  "action": "search_chembl", "query": "aspirin", "k": 5
})

# Verificación ampliada
await LiteratureService().process_request({
  "action": "verify_hypothesis_plus", "topic": "LiFePO4 cathode stability", "k": 8
})
```
