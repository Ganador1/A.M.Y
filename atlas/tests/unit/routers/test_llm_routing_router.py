"""
Tests para LLM Routing Router - Router de enrutamiento de modelos de lenguaje
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.llm_routing import router, RouteRequest, RouteResponse


class TestLLMRoutingRouter:
    """Tests para LLM Routing Router"""

    def setup_method(self):
        """Setup para cada test"""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)

    def test_route_request_model(self):
        """Test: Modelo RouteRequest"""
        request = RouteRequest(
            prompt="Explica la teoría de la relatividad",
            domain="physics",
            priority="high"
        )
        
        assert request.prompt == "Explica la teoría de la relatividad"
        assert request.domain == "physics"
        assert request.priority == "high"

    def test_route_request_model_minimal(self):
        """Test: Modelo RouteRequest con campos mínimos"""
        request = RouteRequest(prompt="Hola mundo")
        
        assert request.prompt == "Hola mundo"
        assert request.domain is None
        assert request.priority == "normal"

    def test_route_request_validation(self):
        """Test: Validación del modelo RouteRequest"""
        # Prompt vacío debe fallar
        with pytest.raises(ValueError):
            RouteRequest(prompt="")
        
        # Prompt muy largo debe fallar
        with pytest.raises(ValueError):
            RouteRequest(prompt="x" * 10001)

    def test_route_response_model(self):
        """Test: Modelo RouteResponse"""
        response = RouteResponse(
            success=True,
            model_selected="gpt-4",
            provider="openai",
            estimated_cost=0.05,
            estimated_tokens=100,
            routing_reason="Model selected for complex reasoning",
            response={"content": "Test response"}
        )
        
        assert response.success is True
        assert response.model_selected == "gpt-4"
        assert response.provider == "openai"
        assert response.estimated_cost == 0.05
        assert response.estimated_tokens == 100
        assert response.routing_reason == "Model selected for complex reasoning"
        assert response.response == {"content": "Test response"}

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_success(self, mock_service):
        """Test: Enrutamiento exitoso de prompt"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-4",
            "tier": "high",
            "response": "Test response"
        }
        
        request_data = {
            "prompt": "Explica la teoría de la relatividad",
            "domain": "physics",
            "priority": "high"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model_selected"] == "gpt-4"
        assert data["provider"] == "auto"
        assert data["estimated_cost"] == 0.0
        assert data["estimated_tokens"] > 0
        assert "routing_reason" in data
        assert "response" in data

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_minimal_request(self, mock_service):
        """Test: Enrutamiento con request mínima"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-3.5-turbo",
            "tier": "medium",
            "response": "Simple response"
        }
        
        request_data = {
            "prompt": "Hola mundo"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model_selected"] == "gpt-3.5-turbo"
        assert data["provider"] == "auto"

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_service_error(self, mock_service):
        """Test: Error del servicio de enrutamiento"""
        # Mock del servicio que falla
        mock_service.route.side_effect = Exception("Service error")
        
        request_data = {
            "prompt": "Test prompt"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_route_prompt_invalid_request(self):
        """Test: Request inválida"""
        # Prompt vacío
        request_data = {
            "prompt": ""
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        assert response.status_code == 422

    def test_route_prompt_missing_prompt(self):
        """Test: Request sin prompt"""
        request_data = {}
        
        response = self.client.post("/llm-routing/route", json=request_data)
        assert response.status_code == 422

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_with_domain(self, mock_service):
        """Test: Enrutamiento con dominio específico"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "claude-3",
            "tier": "high",
            "response": "Domain-specific response"
        }
        
        request_data = {
            "prompt": "Solve this differential equation",
            "domain": "mathematics"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model_selected"] == "claude-3"
        
        # Verificar que se pasó el dominio al servicio
        mock_service.route.assert_called_once()
        call_args = mock_service.route.call_args
        assert call_args[0][0] == "Solve this differential equation"
        assert call_args[0][1]["domain"] == "mathematics"

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_with_priority(self, mock_service):
        """Test: Enrutamiento con prioridad"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-4",
            "tier": "high",
            "response": "High priority response"
        }
        
        request_data = {
            "prompt": "Urgent calculation",
            "priority": "urgent"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model_selected"] == "gpt-4"
        
        # Verificar que se pasó la prioridad al servicio
        mock_service.route.assert_called_once()
        call_args = mock_service.route.call_args
        assert call_args[0][0] == "Urgent calculation"
        assert call_args[0][1]["high_precision"] is True

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_normal_priority(self, mock_service):
        """Test: Enrutamiento con prioridad normal"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-3.5-turbo",
            "tier": "medium",
            "response": "Normal priority response"
        }
        
        request_data = {
            "prompt": "Regular question",
            "priority": "normal"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model_selected"] == "gpt-3.5-turbo"
        
        # Verificar que no se pasó high_precision
        mock_service.route.assert_called_once()
        call_args = mock_service.route.call_args
        assert call_args[0][0] == "Regular question"
        assert "high_precision" not in call_args[0][1]

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_estimated_tokens_calculation(self, mock_service):
        """Test: Cálculo de tokens estimados"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-4",
            "tier": "high",
            "response": "Test response"
        }
        
        request_data = {
            "prompt": "This is a test prompt with exactly 40 characters"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["estimated_tokens"] == 10  # 40 // 4

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_routing_reason(self, mock_service):
        """Test: Razón de enrutamiento"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-4",
            "tier": "high",
            "response": "Test response"
        }
        
        request_data = {
            "prompt": "Test prompt"
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "routing_reason" in data
        assert "tier" in data["routing_reason"]
        assert "high" in data["routing_reason"]

    def test_route_prompt_prompt_length_validation(self):
        """Test: Validación de longitud del prompt"""
        # Prompt muy largo
        request_data = {
            "prompt": "x" * 10001
        }
        
        response = self.client.post("/llm-routing/route", json=request_data)
        assert response.status_code == 422

    def test_route_prompt_prompt_length_boundary(self):
        """Test: Límite de longitud del prompt"""
        # Prompt en el límite
        request_data = {
            "prompt": "x" * 10000
        }
        
        with patch('app.routers.llm_routing.llm_routing_service') as mock_service:
            mock_service.route.return_value = {
                "chosen_model": "gpt-4",
                "tier": "high",
                "response": "Test response"
            }
            
            response = self.client.post("/llm-routing/route", json=request_data)
            assert response.status_code == 200

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_logging(self, mock_service):
        """Test: Logging del enrutamiento"""
        # Mock del servicio
        mock_service.route.return_value = {
            "chosen_model": "gpt-4",
            "tier": "high",
            "response": "Test response"
        }
        
        request_data = {
            "prompt": "Test prompt",
            "domain": "physics"
        }
        
        with patch('app.routers.llm_routing.logger') as mock_logger:
            response = self.client.post("/llm-routing/route", json=request_data)
            
            assert response.status_code == 200
            # Verificar que se llamó al logger
            assert mock_logger.info.called
            assert mock_logger.exception.not_called

    @patch('app.routers.llm_routing.llm_routing_service')
    def test_route_prompt_error_logging(self, mock_service):
        """Test: Logging de errores"""
        # Mock del servicio que falla
        mock_service.route.side_effect = Exception("Service error")
        
        request_data = {
            "prompt": "Test prompt"
        }
        
        with patch('app.routers.llm_routing.logger') as mock_logger:
            response = self.client.post("/llm-routing/route", json=request_data)
            
            assert response.status_code == 500
            # Verificar que se llamó al logger de errores
            assert mock_logger.exception.called

    def test_route_prompt_response_structure(self):
        """Test: Estructura de respuesta del enrutamiento"""
        with patch('app.routers.llm_routing.llm_routing_service') as mock_service:
            mock_service.route.return_value = {
                "chosen_model": "gpt-4",
                "tier": "high",
                "response": "Test response"
            }
            
            request_data = {
                "prompt": "Test prompt"
            }
            
            response = self.client.post("/llm-routing/route", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verificar estructura de respuesta
            assert "success" in data
            assert "model_selected" in data
            assert "provider" in data
            assert "estimated_cost" in data
            assert "estimated_tokens" in data
            assert "routing_reason" in data
            assert "response" in data
            
            # Verificar tipos
            assert isinstance(data["success"], bool)
            assert isinstance(data["model_selected"], str)
            assert isinstance(data["provider"], str)
            assert isinstance(data["estimated_cost"], float)
            assert isinstance(data["estimated_tokens"], int)
            assert isinstance(data["routing_reason"], str)
            assert isinstance(data["response"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
