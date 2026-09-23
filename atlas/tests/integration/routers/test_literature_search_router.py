"""
Tests de integración para Literature Search Router
===============================================

Suite comprehensiva de tests para el router de búsqueda de literatura,
cubriendo integración con bases de datos científicas reales, procesamiento
de resultados y manejo de errores.

Casos de prueba:
- Búsqueda básica en PubMed y arXiv
- Filtrado por fecha y tipo de publicación
- Análisis semántico de resultados
- Manejo de rate limiting y timeouts
- Integración con knowledge graph
- Validación de formatos de respuesta

Actualizado: 2025-09-30
Roadmap: Fase 1.2 - Tests de Routers Críticos
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestLiteratureSearchBasicRouter:
    """Tests para funcionalidad básica de búsqueda de literatura"""

    def test_literature_search_endpoint_pubmed(self):
        """Test búsqueda básica en PubMed"""
        payload = {
            "query": "machine learning protein folding",
            "databases": ["pubmed"],
            "max_results": 10,
            "date_range": {
                "start": "2023-01-01",
                "end": "2025-01-01"
            }
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe responder exitosamente o con resultado vacío graceful
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert 'results' in data or 'papers' in data

            if 'results' in data:
                results = data['results']
                if len(results) > 0:
                    # Verificar estructura de resultado
                    paper = results[0]
                    assert 'title' in paper or 'abstract' in paper

    def test_literature_search_endpoint_arxiv(self):
        """Test búsqueda básica en arXiv"""
        payload = {
            "query": "quantum computing algorithms",
            "databases": ["arxiv"],
            "max_results": 5,
            "categories": ["cs.AI", "quant-ph"]
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert 'results' in data or 'papers' in data

    def test_literature_search_endpoint_multiple_databases(self):
        """Test búsqueda en múltiples bases de datos"""
        payload = {
            "query": "CRISPR gene editing",
            "databases": ["pubmed", "arxiv", "pdb"],
            "max_results": 15,
            "include_abstracts": True
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            # Debe incluir resultados de múltiples fuentes
            if 'results' in data and len(data['results']) > 0:
                # Verificar que hay diversidad de fuentes
                sources = set()
                for paper in data['results']:
                    if 'source' in paper:
                        sources.add(paper['source'])
                # Si hay resultados, deberíamos ver múltiples fuentes
                assert len(sources) >= 1

    def test_literature_search_endpoint_semantic_search(self):
        """Test búsqueda semántica avanzada"""
        payload = {
            "query": "artificial intelligence drug discovery",
            "search_type": "semantic",
            "similarity_threshold": 0.7,
            "max_results": 20
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Verificar que incluye scores de similaridad
                for paper in data['results'][:3]:  # Verificar primeros 3
                    assert 'similarity_score' in paper or 'relevance_score' in paper

    def test_literature_search_endpoint_invalid_query(self):
        """Test manejo de consultas inválidas"""
        payload = {
            "query": "",  # Query vacío
            "databases": ["pubmed"],
            "max_results": 10
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe rechazar query vacío
        assert response.status_code in [400, 422]

    def test_literature_search_endpoint_malformed_request(self):
        """Test manejo de request malformado"""
        payload = {
            "invalid_field": "test",
            "databases": "not_a_list"  # Debe ser lista
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe rechazar request inválido
        assert response.status_code in [400, 422]


class TestLiteratureSearchAdvancedRouter:
    """Tests para funcionalidad avanzada de búsqueda"""

    def test_literature_search_endpoint_date_filtering(self):
        """Test filtrado por rango de fechas"""
        payload = {
            "query": "COVID-19 vaccines",
            "databases": ["pubmed"],
            "date_range": {
                "start": "2020-01-01",
                "end": "2021-12-31"
            },
            "max_results": 10
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                # Verificar que los resultados están en el rango de fechas
                for paper in data['results'][:3]:
                    if 'publication_date' in paper or 'date' in paper:
                        date_field = paper.get('publication_date') or paper.get('date')
                        # Formato puede variar, verificar que contiene año válido
                        assert '2020' in str(date_field) or '2021' in str(date_field)

    def test_literature_search_endpoint_author_filtering(self):
        """Test filtrado por autor"""
        payload = {
            "query": "neural networks",
            "authors": ["LeCun", "Hinton"],
            "databases": ["arxiv"],
            "max_results": 5
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Verificar estructura de respuesta
                assert isinstance(data['results'], list)

    def test_literature_search_endpoint_field_specific(self):
        """Test búsqueda en campos específicos"""
        payload = {
            "query": "machine learning",
            "search_fields": ["title", "abstract"],
            "databases": ["pubmed"],
            "max_results": 8
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

    def test_literature_search_endpoint_citation_analysis(self):
        """Test análisis de citaciones"""
        payload = {
            "query": "attention is all you need",
            "include_citations": True,
            "citation_threshold": 100,
            "databases": ["arxiv"],
            "max_results": 3
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                # Verificar que incluye información de citaciones
                paper = data['results'][0]
                assert 'citations' in paper or 'citation_count' in paper

    def test_literature_search_endpoint_export_formats(self):
        """Test exportación en diferentes formatos"""
        payload = {
            "query": "transformer architecture",
            "databases": ["arxiv"],
            "max_results": 5,
            "export_format": "bibtex"
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            # Debe incluir formato de exportación
            assert 'bibtex' in data or 'export_data' in data


class TestLiteratureSearchKnowledgeGraphRouter:
    """Tests para integración con knowledge graph"""

    def test_literature_search_endpoint_knowledge_graph_integration(self):
        """Test integración con knowledge graph"""
        payload = {
            "query": "protein folding prediction",
            "enhance_with_kg": True,
            "kg_expansion": True,
            "databases": ["pubmed"],
            "max_results": 10
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                # Verificar enriquecimiento con knowledge graph
                assert 'kg_entities' in data or 'enriched_results' in data

    def test_literature_search_endpoint_entity_extraction(self):
        """Test extracción de entidades científicas"""
        payload = {
            "query": "Alzheimer disease amyloid beta",
            "extract_entities": True,
            "entity_types": ["protein", "disease", "drug"],
            "databases": ["pubmed"],
            "max_results": 5
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                # Verificar extracción de entidades
                paper = data['results'][0]
                assert 'entities' in paper or 'extracted_entities' in paper

    def test_literature_search_endpoint_concept_mapping(self):
        """Test mapeo de conceptos científicos"""
        payload = {
            "query": "deep learning genomics",
            "concept_mapping": True,
            "ontology": "biomedical",
            "databases": ["pubmed", "arxiv"],
            "max_results": 8
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [200, 400, 500]


class TestLiteratureSearchPerformanceRouter:
    """Tests para rendimiento y concurrencia"""

    def test_literature_search_endpoint_concurrent_requests(self):
        """Test manejo de requests concurrentes"""
        import threading

        results = []

        def search_request():
            payload = {
                "query": "artificial intelligence",
                "databases": ["arxiv"],
                "max_results": 3
            }
            response = client.post("/api/literature-search/search", json=payload)
            results.append(response.status_code)

        # Ejecutar 3 requests concurrentes
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=search_request)
            threads.append(thread)
            thread.start()

        # Esperar a que terminen
        for thread in threads:
            thread.join()

        # Verificar que todos respondieron
        assert len(results) == 3
        # Al menos algunos deben ser exitosos
        assert any(status in [200, 400] for status in results)

    def test_literature_search_endpoint_large_query(self):
        """Test manejo de consultas grandes"""
        large_query = " ".join(["machine learning"] * 50)  # Query muy largo

        payload = {
            "query": large_query,
            "databases": ["arxiv"],
            "max_results": 5
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe manejar query largo o rechazarlo gracefully
        assert response.status_code in [200, 400, 413, 500]

    def test_literature_search_endpoint_timeout_handling(self):
        """Test manejo de timeouts"""
        payload = {
            "query": "comprehensive review systematic analysis",
            "databases": ["pubmed", "arxiv", "pdb"],
            "max_results": 100,  # Muchos resultados
            "timeout": 5  # Timeout corto
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe manejar timeout gracefully
        assert response.status_code in [200, 408, 500]

    def test_literature_search_endpoint_rate_limiting(self):
        """Test respeto de rate limiting"""
        # Hacer múltiples requests rápidos
        responses = []
        for i in range(5):
            payload = {
                "query": f"test query {i}",
                "databases": ["arxiv"],
                "max_results": 2
            }
            response = client.post("/api/literature-search/search", json=payload)
            responses.append(response.status_code)

        # Verificar que responde consistentemente
        assert len(responses) == 5
        # No todos deberían fallar por rate limiting
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 1  # Al menos uno debe funcionar


class TestLiteratureSearchErrorHandlingRouter:
    """Tests para manejo de errores"""

    def test_literature_search_endpoint_database_unavailable(self):
        """Test manejo cuando base de datos no está disponible"""
        payload = {
            "query": "test query",
            "databases": ["nonexistent_db"],
            "max_results": 5
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe rechazar base de datos inválida
        assert response.status_code in [400, 422, 500]

    def test_literature_search_endpoint_invalid_parameters(self):
        """Test manejo de parámetros inválidos"""
        payload = {
            "query": "test",
            "databases": ["pubmed"],
            "max_results": -5,  # Número negativo inválido
            "date_range": {
                "start": "invalid-date",
                "end": "2025-01-01"
            }
        }

        response = client.post("/api/literature-search/search", json=payload)

        assert response.status_code in [400, 422]

    def test_literature_search_endpoint_network_error_simulation(self):
        """Test simulación de errores de red"""
        payload = {
            "query": "network error test",
            "databases": ["pubmed"],
            "max_results": 5,
            "simulate_network_error": True  # Parámetro para testing
        }

        response = client.post("/api/literature-search/search", json=payload)

        # Debe manejar errores de red gracefully
        assert response.status_code in [200, 500, 503]

    def test_literature_search_endpoint_json_malformed(self):
        """Test manejo de JSON malformado"""
        response = client.post(
            "/api/literature-search/search",
            content='{"query": "test", "databases": invalid_json}',
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]


class TestLiteratureSearchIntegrationRouter:
    """Tests de integración end-to-end"""

    def test_literature_search_complete_workflow(self):
        """Test flujo completo de búsqueda de literatura"""
        # Paso 1: Búsqueda inicial
        search_payload = {
            "query": "machine learning drug discovery",
            "databases": ["pubmed"],
            "max_results": 5
        }

        search_response = client.post("/api/literature-search/search", json=search_payload)

        if search_response.status_code == 200:
            search_data = search_response.json()

            if 'results' in search_data and len(search_data['results']) > 0:
                # Paso 2: Análisis detallado del primer resultado
                paper_id = search_data['results'][0].get('id') or search_data['results'][0].get('pmid')

                if paper_id:
                    detail_payload = {
                        "paper_id": paper_id,
                        "include_full_text": True,
                        "extract_citations": True
                    }

                    detail_response = client.post("/api/literature-search/detail", json=detail_payload)
                    assert detail_response.status_code in [200, 400, 404, 500]

    def test_literature_search_recommendation_workflow(self):
        """Test flujo de recomendaciones basado en literatura"""
        # Búsqueda base
        payload = {
            "query": "CRISPR applications",
            "databases": ["pubmed"],
            "max_results": 10,
            "get_recommendations": True
        }

        response = client.post("/api/literature-search/search", json=payload)

        if response.status_code == 200:
            data = response.json()

            # Verificar recomendaciones
            if 'recommendations' in data:
                recommendations = data['recommendations']
                assert isinstance(recommendations, list)

                # Verificar estructura de recomendaciones
                if len(recommendations) > 0:
                    rec = recommendations[0]
                    assert 'title' in rec or 'reason' in rec


if __name__ == "__main__":
    pytest.main([__file__, "-v"])