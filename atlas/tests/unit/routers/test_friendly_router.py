"""
Tests para Friendly Router - Router amigable de interfaz de usuario
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.friendly import router


class TestFriendlyRouter:
    """Tests para Friendly Router"""

    def setup_method(self):
        """Setup para cada test"""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    def test_get_main_info_success(self):
        """Test: Obtención exitosa de información principal"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "categories" in data["data"]
        
        # Verificar que hay categorías
        categories = data["data"]["categories"]
        assert len(categories) > 0
        
        # Verificar estructura de categorías
        for category in categories:
            assert "name" in category
            assert "description" in category
            assert "endpoint" in category
            assert "functions" in category

    def test_get_help_category_success(self):
        """Test: Obtención exitosa de ayuda por categoría"""
        response = self.client.get("/help/arithmetic")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "category" in data["data"]
        assert "description" in data["data"]
        assert "endpoints" in data["data"]
        assert "examples" in data["data"]

    def test_get_help_category_not_found(self):
        """Test: Categoría de ayuda no encontrada"""
        response = self.client.get("/help/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_examples_success(self):
        """Test: Obtención exitosa de ejemplos"""
        response = self.client.get("/examples")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "examples" in data["data"]
        
        # Verificar estructura de ejemplos
        examples = data["data"]["examples"]
        assert len(examples) > 0
        
        for example in examples:
            assert "category" in example
            assert "title" in example
            assert "description" in example
            assert "request" in example
            assert "response" in example

    def test_get_quick_start_success(self):
        """Test: Obtención exitosa de guía de inicio rápido"""
        response = self.client.get("/quick-start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "steps" in data["data"]
        assert "examples" in data["data"]
        
        # Verificar estructura de pasos
        steps = data["data"]["steps"]
        assert len(steps) > 0
        
        for step in steps:
            assert "step" in step
            assert "title" in step
            assert "description" in step
            assert "action" in step

    def test_get_help_arithmetic_category(self):
        """Test: Ayuda específica para categoría arithmetic"""
        response = self.client.get("/help/arithmetic")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "arithmetic"
        assert "arithmetic" in data["data"]["description"].lower()

    def test_get_help_calculus_category(self):
        """Test: Ayuda específica para categoría calculus"""
        response = self.client.get("/help/calculus")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "calculus"
        assert "calculus" in data["data"]["description"].lower()

    def test_get_help_equations_category(self):
        """Test: Ayuda específica para categoría equations"""
        response = self.client.get("/help/equations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "equations"
        assert "equation" in data["data"]["description"].lower()

    def test_get_help_statistics_category(self):
        """Test: Ayuda específica para categoría statistics"""
        response = self.client.get("/help/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "statistics"
        assert "statistic" in data["data"]["description"].lower()

    def test_get_help_graphing_category(self):
        """Test: Ayuda específica para categoría graphing"""
        response = self.client.get("/help/graphing")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "graphing"
        assert "graph" in data["data"]["description"].lower()

    def test_get_help_advanced_algebra_category(self):
        """Test: Ayuda específica para categoría advanced_algebra"""
        response = self.client.get("/help/advanced_algebra")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "advanced_algebra"
        assert "algebra" in data["data"]["description"].lower()

    def test_get_help_differential_equations_category(self):
        """Test: Ayuda específica para categoría differential_equations"""
        response = self.client.get("/help/differential_equations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "differential_equations"
        assert "differential" in data["data"]["description"].lower()

    def test_get_help_linear_algebra_category(self):
        """Test: Ayuda específica para categoría linear_algebra"""
        response = self.client.get("/help/linear_algebra")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "linear_algebra"
        assert "linear" in data["data"]["description"].lower()

    def test_get_help_complex_analysis_category(self):
        """Test: Ayuda específica para categoría complex_analysis"""
        response = self.client.get("/help/complex_analysis")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "complex_analysis"
        assert "complex" in data["data"]["description"].lower()

    def test_get_help_topology_category(self):
        """Test: Ayuda específica para categoría topology"""
        response = self.client.get("/help/topology")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "topology"
        assert "topology" in data["data"]["description"].lower()

    def test_get_help_number_theory_category(self):
        """Test: Ayuda específica para categoría number_theory"""
        response = self.client.get("/help/number_theory")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "number_theory"
        assert "number" in data["data"]["description"].lower()

    def test_get_help_category_case_insensitive(self):
        """Test: Búsqueda de categoría case insensitive"""
        response = self.client.get("/help/ARITHMETIC")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "arithmetic"

    def test_get_help_category_with_spaces(self):
        """Test: Búsqueda de categoría con espacios"""
        response = self.client.get("/help/advanced%20algebra")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["category"] == "advanced_algebra"

    def test_get_examples_arithmetic(self):
        """Test: Ejemplos específicos para arithmetic"""
        response = self.client.get("/examples")
        
        assert response.status_code == 200
        data = response.json()
        examples = data["data"]["examples"]
        
        # Buscar ejemplo de arithmetic
        arithmetic_example = next((ex for ex in examples if ex["category"] == "arithmetic"), None)
        assert arithmetic_example is not None
        assert "request" in arithmetic_example
        assert "response" in arithmetic_example

    def test_get_examples_calculus(self):
        """Test: Ejemplos específicos para calculus"""
        response = self.client.get("/examples")
        
        assert response.status_code == 200
        data = response.json()
        examples = data["data"]["examples"]
        
        # Buscar ejemplo de calculus
        calculus_example = next((ex for ex in examples if ex["category"] == "calculus"), None)
        assert calculus_example is not None
        assert "request" in calculus_example
        assert "response" in calculus_example

    def test_get_quick_start_steps(self):
        """Test: Pasos de inicio rápido"""
        response = self.client.get("/quick-start")
        
        assert response.status_code == 200
        data = response.json()
        steps = data["data"]["steps"]
        
        # Verificar que hay pasos numerados
        for i, step in enumerate(steps):
            assert step["step"] == i + 1
            assert "title" in step
            assert "description" in step
            assert "action" in step

    def test_get_quick_start_examples(self):
        """Test: Ejemplos de inicio rápido"""
        response = self.client.get("/quick-start")
        
        assert response.status_code == 200
        data = response.json()
        examples = data["data"]["examples"]
        
        # Verificar estructura de ejemplos
        assert len(examples) > 0
        for example in examples:
            assert "title" in example
            assert "description" in example
            assert "request" in example
            assert "response" in example

    def test_response_structure_consistency(self):
        """Test: Consistencia de estructura de respuesta"""
        endpoints = ["/", "/help/arithmetic", "/examples", "/quick-start"]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estructura base
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert isinstance(data["success"], bool)
            assert isinstance(data["message"], str)
            assert isinstance(data["data"], dict)

    def test_error_handling_invalid_category(self):
        """Test: Manejo de errores para categoría inválida"""
        response = self.client.get("/help/invalid_category_123")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_error_handling_empty_category(self):
        """Test: Manejo de errores para categoría vacía"""
        response = self.client.get("/help/")
        
        # FastAPI debería manejar esto como 404
        assert response.status_code == 404

    def test_help_category_endpoints_structure(self):
        """Test: Estructura de endpoints en ayuda de categoría"""
        response = self.client.get("/help/arithmetic")
        
        assert response.status_code == 200
        data = response.json()
        endpoints = data["data"]["endpoints"]
        
        # Verificar estructura de endpoints
        assert len(endpoints) > 0
        for endpoint in endpoints:
            assert "method" in endpoint
            assert "path" in endpoint
            assert "description" in endpoint
            assert "parameters" in endpoint
            assert "response" in endpoint

    def test_help_category_examples_structure(self):
        """Test: Estructura de ejemplos en ayuda de categoría"""
        response = self.client.get("/help/arithmetic")
        
        assert response.status_code == 200
        data = response.json()
        examples = data["data"]["examples"]
        
        # Verificar estructura de ejemplos
        assert len(examples) > 0
        for example in examples:
            assert "title" in example
            assert "description" in example
            assert "request" in example
            assert "response" in example


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
