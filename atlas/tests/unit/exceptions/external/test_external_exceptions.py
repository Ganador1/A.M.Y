"""
Tests for external service exceptions
"""
import pytest
from app.exceptions.external.llm import LLMError, OllamaError, OpenAIError
from app.exceptions.external.scientific_api import (
    ScientificAPIError,
    UniProtError,
    PubChemError,
    NCBIError
)
from app.exceptions.external.service import (
    ServiceUnavailableError,
    TimeoutError as AtlasTimeoutError,
    AuthenticationError
)
from app.exceptions.base import AtlasExternalError


class TestLLMExceptions:
    """Test LLM service exceptions"""

    def test_llm_error_basic(self):
        """Test basic LLMError creation"""
        exc = LLMError("Model inference failed")
        assert isinstance(exc, AtlasExternalError)
        assert exc.error_code == "LLMError"

    def test_ollama_error(self):
        """Test OllamaError"""
        exc = OllamaError(
            "Failed to connect to Ollama",
            details={
                "model": "llama3:8b",
                "endpoint": "http://localhost:11434",
                "error": "connection_refused"
            }
        )
        assert isinstance(exc, LLMError)
        assert exc.details["model"] == "llama3:8b"

    def test_openai_error(self):
        """Test OpenAIError"""
        exc = OpenAIError(
            "API rate limit exceeded",
            details={
                "model": "gpt-4",
                "tokens_requested": 8000,
                "limit": 10000,
                "retry_after": 60
            }
        )
        assert isinstance(exc, LLMError)
        assert exc.details["retry_after"] == 60

    def test_llm_error_with_prompt(self):
        """Test LLMError with prompt context"""
        exc = LLMError(
            "Generation failed",
            details={
                "prompt": "Generate hypothesis for...",
                "max_tokens": 2000,
                "temperature": 0.7,
                "error": "context_length_exceeded"
            }
        )
        assert "prompt" in exc.details
        assert exc.details["max_tokens"] == 2000


class TestScientificAPIExceptions:
    """Test scientific API exceptions"""

    def test_scientific_api_error_basic(self):
        """Test basic ScientificAPIError"""
        exc = ScientificAPIError("API request failed")
        assert isinstance(exc, AtlasExternalError)

    def test_uniprot_error(self):
        """Test UniProtError"""
        exc = UniProtError(
            "Protein not found",
            details={
                "uniprot_id": "P04637",
                "endpoint": "https://rest.uniprot.org/uniprotkb/P04637",
                "status_code": 404
            }
        )
        assert isinstance(exc, ScientificAPIError)
        assert exc.details["uniprot_id"] == "P04637"

    def test_pubchem_error(self):
        """Test PubChemError"""
        exc = PubChemError(
            "Compound search failed",
            details={
                "query": "aspirin",
                "search_type": "name",
                "error": "too_many_results"
            }
        )
        assert isinstance(exc, ScientificAPIError)
        assert exc.details["query"] == "aspirin"

    def test_ncbi_error(self):
        """Test NCBIError"""
        exc = NCBIError(
            "BLAST search timeout",
            details={
                "database": "nr",
                "query_length": 500,
                "timeout_seconds": 300
            }
        )
        assert isinstance(exc, ScientificAPIError)
        assert exc.details["database"] == "nr"


class TestServiceExceptions:
    """Test generic service exceptions"""

    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError"""
        exc = ServiceUnavailableError(
            "Service temporarily unavailable",
            details={
                "service": "quantum_simulator",
                "status": "maintenance",
                "estimated_recovery": "2025-01-01T12:00:00Z"
            }
        )
        assert isinstance(exc, AtlasExternalError)
        assert exc.details["service"] == "quantum_simulator"

    def test_timeout_error(self):
        """Test AtlasTimeoutError"""
        exc = AtlasTimeoutError(
            "Request timeout",
            details={
                "endpoint": "/api/simulate",
                "timeout_seconds": 30,
                "elapsed_seconds": 35
            }
        )
        assert isinstance(exc, AtlasExternalError)
        assert exc.details["timeout_seconds"] == 30

    def test_authentication_error(self):
        """Test AuthenticationError"""
        exc = AuthenticationError(
            "Invalid API key",
            details={
                "service": "materials_project",
                "error": "invalid_credentials"
            }
        )
        assert isinstance(exc, AtlasExternalError)
        assert exc.details["service"] == "materials_project"


class TestExternalExceptionHierarchy:
    """Test external exception hierarchy"""

    def test_all_inherit_from_external_error(self):
        """Test that all inherit from AtlasExternalError"""
        exceptions = [
            LLMError("test"),
            ScientificAPIError("test"),
            ServiceUnavailableError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AtlasExternalError)

    def test_specialized_inherit_from_base(self):
        """Test specialized exceptions inherit from base"""
        assert isinstance(OllamaError("test"), LLMError)
        assert isinstance(OpenAIError("test"), LLMError)
        assert isinstance(UniProtError("test"), ScientificAPIError)
        assert isinstance(PubChemError("test"), ScientificAPIError)
        assert isinstance(NCBIError("test"), ScientificAPIError)
        assert isinstance(AtlasTimeoutError("test"), AtlasExternalError)
        assert isinstance(AuthenticationError("test"), AtlasExternalError)


class TestExternalExceptionUseCases:
    """Test real-world use cases"""

    def test_ollama_retry_scenario(self):
        """Test Ollama retry with backoff"""
        def call_ollama(attempt=1, max_attempts=3):
            if attempt < max_attempts:
                raise OllamaError(
                    f"Connection failed (attempt {attempt})",
                    details={
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "backoff_seconds": attempt * 2
                    }
                )
            return {"response": "success"}

        with pytest.raises(OllamaError) as exc_info:
            call_ollama(attempt=2)

        assert exc_info.value.details["backoff_seconds"] == 4

    def test_scientific_api_fallback(self):
        """Test fallback to alternative API"""
        def fetch_protein(uniprot_id: str, use_cache=True):
            if use_cache:
                raise UniProtError(
                    "Primary API unavailable",
                    details={
                        "uniprot_id": uniprot_id,
                        "fallback": "local_database"
                    }
                )
            return {"protein": "from_db"}

        with pytest.raises(UniProtError) as exc_info:
            fetch_protein("P04637")

        # Should fallback to local database
        assert exc_info.value.details["fallback"] == "local_database"

    def test_timeout_with_context(self):
        """Test timeout with request context"""
        def long_running_request():
            raise AtlasTimeoutError(
                "Quantum simulation timeout",
                details={
                    "operation": "VQE_optimization",
                    "qubits": 20,
                    "iterations_completed": 50,
                    "iterations_total": 100,
                    "timeout_seconds": 300
                }
            )

        with pytest.raises(AtlasTimeoutError) as exc_info:
            long_running_request()

        # Can resume from iteration 50
        assert exc_info.value.details["iterations_completed"] == 50

    def test_authentication_error_handling(self):
        """Test API key authentication error"""
        def authenticate_api(api_key: str):
            if not api_key.startswith("sk-"):
                raise AuthenticationError(
                    "Invalid API key format",
                    details={
                        "expected_prefix": "sk-",
                        "provided_length": len(api_key)
                    }
                )

        with pytest.raises(AuthenticationError) as exc_info:
            authenticate_api("invalid_key")

        assert exc_info.value.details["expected_prefix"] == "sk-"


class TestExternalExceptionSerialization:
    """Test serialization for API responses"""

    def test_llm_error_to_dict(self):
        """Test LLMError serialization"""
        exc = OllamaError(
            "Model not available",
            error_code="OLLAMA_MODEL_404",
            details={"model": "mistral:7b", "available_models": ["llama3:8b"]}
        )
        result = exc.to_dict()

        assert result["error"] == "OLLAMA_MODEL_404"
        assert result["message"] == "Model not available"
        assert result["details"]["model"] == "mistral:7b"

    def test_api_error_with_retry_info(self):
        """Test API error with retry information"""
        exc = ScientificAPIError(
            "Rate limit exceeded",
            details={
                "retry_after": 120,
                "limit": 100,
                "requests_made": 150
            }
        )
        result = exc.to_dict()

        # Client can extract retry_after from details
        assert result["details"]["retry_after"] == 120

    def test_timeout_error_serialization(self):
        """Test timeout error for client handling"""
        exc = AtlasTimeoutError(
            "Request timeout",
            details={
                "timeout_seconds": 30,
                "can_retry": True,
                "partial_results": {"completed": 70}
            }
        )
        result = exc.to_dict()

        assert result["details"]["can_retry"] is True
        assert result["details"]["partial_results"]["completed"] == 70
