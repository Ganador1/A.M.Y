"""
Tests de Integración: Sistema Multi-Agente con Hugging Face

Tests comprehensivos para validar la integración de modelos cloud de
Hugging Face con el sistema multi-agente de AXIOM Atlas.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest,
    HFInferenceResponse
)
from app.services.huggingface_agent_wrapper import (
    HuggingFaceAgentWrapper,
    HybridAgentWrapper,
    create_agent_wrapper
)


class TestHuggingFaceProvider:
    """Tests para el proveedor de Hugging Face"""

    @pytest.fixture
    def provider(self):
        """Crear instancia del proveedor para tests"""
        return HuggingFaceProvider(
            api_key="test_key",
            cache_enabled=True,
            max_retries=2,
            timeout=30
        )

    def test_provider_initialization(self, provider):
        """Test: Inicialización correcta del proveedor"""
        assert provider.api_key == "test_key"
        assert provider.cache_enabled is True
        assert provider.max_retries == 2
        assert provider.timeout == 30

    def test_get_optimal_model_by_agent(self, provider):
        """Test: Selección de modelo por rol de agente"""
        model = provider.get_optimal_model(agent_role="bio_hypothesis")
        assert model == "microsoft/biogpt"

        model = provider.get_optimal_model(agent_role="orchestrator")
        assert model == "meta-llama/Meta-Llama-3.1-70B-Instruct"

    def test_get_optimal_model_by_domain(self, provider):
        """Test: Selección de modelo por dominio"""
        model = provider.get_optimal_model(domain="biology")
        assert model == "microsoft/biogpt"

        model = provider.get_optimal_model(domain="mathematics")
        assert model == "facebook/galactica-30b"

    def test_fallback_model_selection(self, provider):
        """Test: Selección de modelo de respaldo"""
        model = provider.get_optimal_model(domain="biology", use_fallback=True)
        assert model == "allenai/scibert_scivocab_uncased"

    def test_cache_key_generation(self, provider):
        """Test: Generación de claves de caché"""
        key1 = provider._get_cache_key("model1", "prompt1", {"temp": 0.7})
        key2 = provider._get_cache_key("model1", "prompt1", {"temp": 0.7})
        key3 = provider._get_cache_key("model1", "prompt2", {"temp": 0.7})

        assert key1 == key2  # Mismos parámetros = misma clave
        assert key1 != key3  # Diferentes prompts = diferentes claves

    @pytest.mark.asyncio
    async def test_generate_text_success(self, provider):
        """Test: Generación exitosa de texto"""
        request = HFInferenceRequest(
            model_id="gpt2",
            prompt="Test prompt",
            max_new_tokens=50,
            temperature=0.7
        )

        # Mock de la respuesta HTTP
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = [{
                "generated_text": "This is a test response"
            }]
            mock_response.raise_for_status = Mock()

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            response = await provider.generate_text(request)

            assert response.success is True
            assert response.generated_text == "This is a test response"
            assert response.model_id == "gpt2"

    @pytest.mark.asyncio
    async def test_generate_text_with_cache(self, provider):
        """Test: Uso de caché en generación"""
        request = HFInferenceRequest(
            model_id="gpt2",
            prompt="Cached prompt",
            max_new_tokens=50
        )

        # Simular respuesta en caché
        cache_key = provider._get_cache_key(
            request.model_id,
            request.prompt,
            {"max_new_tokens": request.max_new_tokens, "temperature": request.temperature, "top_p": request.top_p, "top_k": request.top_k}
        )

        provider.cache[cache_key] = {
            "response": {
                "success": True,
                "generated_text": "Cached response",
                "model_id": "gpt2"
            },
            "timestamp": asyncio.get_event_loop().time()
        }

        response = await provider.generate_text(request)

        assert response.generated_text == "Cached response"
        assert provider.metrics["cache_hits"] > 0

    def test_rate_limiting(self, provider):
        """Test: Rate limiting funciona correctamente"""
        # Llenar el historial de requests
        import time
        provider.request_history = [time.time()] * provider.max_requests_per_minute

        # Verificar que rate limit detecta límite alcanzado
        assert provider._check_rate_limit() is False

        # Limpiar y verificar que permite requests
        provider.request_history.clear()
        assert provider._check_rate_limit() is True

    def test_metrics_calculation(self, provider):
        """Test: Cálculo correcto de métricas"""
        # Simular algunas requests
        provider.metrics["total_requests"] = 10
        provider.metrics["successful_requests"] = 8
        provider.metrics["failed_requests"] = 2
        provider.metrics["cache_hits"] = 3
        provider.metrics["total_tokens"] = 5000
        provider.metrics["total_latency_ms"] = 8000

        metrics = provider.get_metrics()

        assert metrics["success_rate"] == 80.0
        assert metrics["cache_hit_rate"] == 30.0
        assert metrics["average_latency_ms"] == 1000.0


class TestHuggingFaceAgentWrapper:
    """Tests para el wrapper de agentes"""

    @pytest.mark.asyncio
    async def test_wrapper_initialization(self):
        """Test: Inicialización correcta del wrapper"""
        wrapper = HuggingFaceAgentWrapper(
            agent_role="bio_hypothesis",
            domain="biology"
        )

        assert wrapper.agent_role == "bio_hypothesis"
        assert wrapper.domain == "biology"
        assert wrapper.model_id == "microsoft/biogpt"

    @pytest.mark.asyncio
    async def test_wrapper_generate_async(self):
        """Test: Generación asíncrona"""
        wrapper = HuggingFaceAgentWrapper(agent_role="orchestrator")

        # Mock del provider
        with patch.object(
            wrapper.provider,
            'generate_for_agent',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = HFInferenceResponse(
                success=True,
                generated_text="Test response",
                model_id="test-model"
            )

            result = await wrapper.generate_async(
                prompt="Test prompt",
                max_new_tokens=100
            )

            assert result == "Test response"
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_wrapper_error_handling(self):
        """Test: Manejo de errores"""
        wrapper = HuggingFaceAgentWrapper(agent_role="reviewer")

        # Mock de error
        with patch.object(
            wrapper.provider,
            'generate_for_agent',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = HFInferenceResponse(
                success=False,
                generated_text="",
                model_id="test-model",
                error="API Error"
            )

            result = await wrapper.generate_async("Test prompt")

            assert "[ERROR: API Error]" in result


class TestHybridAgentWrapper:
    """Tests para el wrapper híbrido"""

    @pytest.mark.asyncio
    async def test_hybrid_wrapper_initialization(self):
        """Test: Inicialización del wrapper híbrido"""
        wrapper = HybridAgentWrapper(
            agent_role="bio_hypothesis",
            hf_model_id="microsoft/biogpt",
            ollama_model="mistral:7b",
            domain="biology"
        )

        assert wrapper.agent_role == "bio_hypothesis"
        assert wrapper.hf_wrapper.model_id == "microsoft/biogpt"

    @pytest.mark.asyncio
    async def test_hybrid_prefers_cloud(self):
        """Test: Preferencia por modelos cloud"""
        wrapper = HybridAgentWrapper(
            agent_role="orchestrator",
            prefer_cloud=True
        )

        # Mock HF exitoso
        with patch.object(
            wrapper.hf_wrapper,
            'generate'
        ) as mock_hf:
            mock_hf.return_value = "HF response"

            result = wrapper.generate("Test prompt")

            assert result == "HF response"
            mock_hf.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_fallback_to_ollama(self):
        """Test: Fallback a Ollama cuando HF falla"""
        wrapper = HybridAgentWrapper(
            agent_role="reviewer",
            ollama_model="qwen:7b",
            prefer_cloud=True
        )

        # Mock HF falla, Ollama éxito
        with patch.object(wrapper.hf_wrapper, 'generate') as mock_hf:
            with patch.object(wrapper.ollama_wrapper, 'generate') as mock_ollama:
                mock_hf.return_value = "[ERROR: HF failed]"
                mock_ollama.return_value = "Ollama response"

                result = wrapper.generate("Test prompt")

                assert result == "Ollama response"
                mock_ollama.assert_called_once()


class TestAgentFactory:
    """Tests para la factory function"""

    def test_create_huggingface_wrapper(self):
        """Test: Crear wrapper de Hugging Face"""
        wrapper = create_agent_wrapper(
            agent_role="bio_hypothesis",
            provider="huggingface",
            domain="biology"
        )

        assert isinstance(wrapper, HuggingFaceAgentWrapper)
        assert wrapper.agent_role == "bio_hypothesis"

    def test_create_hybrid_wrapper(self):
        """Test: Crear wrapper híbrido"""
        wrapper = create_agent_wrapper(
            agent_role="orchestrator",
            provider="hybrid"
        )

        assert isinstance(wrapper, HybridAgentWrapper)
        assert wrapper.agent_role == "orchestrator"

    def test_create_ollama_wrapper(self):
        """Test: Crear wrapper de Ollama"""
        with patch('app.services.huggingface_agent_wrapper.RoleLLMWrapper') as mock_ollama:
            wrapper = create_agent_wrapper(
                agent_role="publisher",
                provider="ollama",
                ollama_model="llama3:8b"
            )

            mock_ollama.assert_called_with("llama3:8b")

    def test_invalid_provider_raises_error(self):
        """Test: Provider inválido lanza excepción"""
        with pytest.raises(ValueError, match="Proveedor desconocido"):
            create_agent_wrapper(
                agent_role="orchestrator",
                provider="invalid_provider"
            )


@pytest.mark.integration
class TestMultiAgentWorkflow:
    """Tests de integración del workflow completo"""

    @pytest.mark.asyncio
    async def test_full_scientific_workflow(self):
        """Test: Workflow científico completo"""
        # Mock de todos los wrappers
        orchestrator = create_agent_wrapper("orchestrator", "huggingface")
        bio_hyp = create_agent_wrapper("bio_hypothesis", "huggingface")
        coder = create_agent_wrapper("physchem_coder", "huggingface")
        reviewer = create_agent_wrapper("reviewer", "huggingface")
        publisher = create_agent_wrapper("publisher", "huggingface")

        # Mock responses
        with patch.object(orchestrator.provider, 'generate_for_agent', new_callable=AsyncMock) as mock1, \
             patch.object(bio_hyp.provider, 'generate_for_agent', new_callable=AsyncMock) as mock2, \
             patch.object(coder.provider, 'generate_for_agent', new_callable=AsyncMock) as mock3, \
             patch.object(reviewer.provider, 'generate_for_agent', new_callable=AsyncMock) as mock4, \
             patch.object(publisher.provider, 'generate_for_agent', new_callable=AsyncMock) as mock5:

            mock1.return_value = HFInferenceResponse(success=True, generated_text='{"steps": ["step1", "step2"]}', model_id="test")
            mock2.return_value = HFInferenceResponse(success=True, generated_text='{"hypothesis": "test hyp"}', model_id="test")
            mock3.return_value = HFInferenceResponse(success=True, generated_text='Design plan...', model_id="test")
            mock4.return_value = HFInferenceResponse(success=True, generated_text='{"verdict": "approve"}', model_id="test")
            mock5.return_value = HFInferenceResponse(success=True, generated_text='Final report...', model_id="test")

            # Ejecutar workflow
            plan = await orchestrator.generate_async("Research goal", max_new_tokens=512)
            hypothesis = await bio_hyp.generate_async("Generate hypothesis", max_new_tokens=640)
            design = await coder.generate_async("Design experiment", max_new_tokens=700)
            review = await reviewer.generate_async("Review", max_new_tokens=480)
            report = await publisher.generate_async("Publish", max_new_tokens=700)

            # Verificar que todos los pasos se ejecutaron
            assert '{"steps": ["step1", "step2"]}' in plan
            assert '{"hypothesis": "test hyp"}' in hypothesis
            assert 'Design plan' in design
            assert '{"verdict": "approve"}' in review
            assert 'Final report' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
