"""
Integration tests for exception propagation through the stack
"""
import pytest
from app.exceptions.domain.biology import BiologyError, ProteinAnalysisError
from app.exceptions.domain.physics import QuantumError
from app.exceptions.infrastructure.database import DatabaseError
from app.exceptions.external.llm import OllamaError


class TestExceptionPropagation:
    """Test exception propagation from service → router → API"""

    def test_domain_exception_preserves_context(self):
        """Test that domain exceptions preserve context through layers"""

        # Simulate service layer
        def service_layer():
            raise ProteinAnalysisError(
                "Protein structure prediction failed",
                details={
                    "uniprot_id": "P04637",
                    "algorithm": "AlphaFold2",
                    "confidence": 0.65
                }
            )

        # Simulate router layer
        def router_layer():
            try:
                service_layer()
            except ProteinAnalysisError as e:
                # Router re-raises with additional context
                raise ProteinAnalysisError(
                    f"API Error: {e.message}",
                    details={**e.details, "endpoint": "/api/biology/protein/predict"},
                    cause=e
                ) from e

        # Test propagation
        with pytest.raises(ProteinAnalysisError) as exc_info:
            router_layer()

        exc = exc_info.value
        assert exc.details["uniprot_id"] == "P04637"
        assert exc.details["endpoint"] == "/api/biology/protein/predict"
        assert exc.cause is not None

    def test_exception_chaining_multiple_layers(self):
        """Test exception chaining through multiple layers"""

        def database_layer():
            raise DatabaseError(
                "Connection failed",
                details={"host": "localhost", "port": 5432}
            )

        def service_layer():
            try:
                database_layer()
            except DatabaseError as e:
                raise BiologyError(
                    "Failed to fetch protein data",
                    details={"uniprot_id": "P12345"},
                    cause=e
                ) from e

        def router_layer():
            try:
                service_layer()
            except BiologyError as e:
                # Final layer adds API context
                raise BiologyError(
                    "API request failed",
                    details={**e.details, "status_code": 500},
                    cause=e
                ) from e

        with pytest.raises(BiologyError) as exc_info:
            router_layer()

        # Verify chain: router -> service -> database
        exc = exc_info.value
        assert exc.details["status_code"] == 500
        assert exc.cause is not None
        assert isinstance(exc.cause.cause, DatabaseError)

    def test_external_exception_wrapping(self):
        """Test wrapping external exceptions in domain exceptions"""

        def external_service():
            raise OllamaError(
                "Model not available",
                details={"model": "llama3:8b"}
            )

        def service_layer():
            try:
                external_service()
            except OllamaError as e:
                # Wrap in domain exception
                raise BiologyError(
                    "Hypothesis generation failed",
                    details={"reason": "llm_unavailable"},
                    cause=e
                ) from e

        with pytest.raises(BiologyError) as exc_info:
            service_layer()

        # Original exception preserved in chain
        assert isinstance(exc_info.value.cause, OllamaError)


class TestExceptionSerialization:
    """Test exception serialization for API responses"""

    def test_to_dict_includes_all_context(self):
        """Test that to_dict includes all relevant context"""
        exc = ProteinAnalysisError(
            "Analysis failed",
            error_code="PROTEIN_001",
            details={
                "uniprot_id": "P04637",
                "step": "structure_prediction",
                "confidence": 0.45
            }
        )

        result = exc.to_dict()

        assert result["error"] == "PROTEIN_001"
        assert result["message"] == "Analysis failed"
        assert result["details"]["uniprot_id"] == "P04637"
        assert result["details"]["step"] == "structure_prediction"

    def test_nested_exception_serialization(self):
        """Test serialization with cause chain"""
        db_error = DatabaseError("Connection lost")
        bio_error = BiologyError("Data fetch failed", cause=db_error)

        result = bio_error.to_dict()

        assert result["error"] == "BiologyError"
        assert result["message"] == "Data fetch failed"
        # to_dict doesn't include cause, but it's preserved in exception


class TestExceptionInContextManagers:
    """Test exceptions in async context managers"""

    def test_exception_in_context_manager(self):
        """Test exception handling in context manager"""

        class ResourceManager:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is QuantumError:
                    # Log but don't suppress
                    return False
                return False

            def execute(self):
                raise QuantumError(
                    "Circuit execution failed",
                    details={"qubits": 5, "depth": 10}
                )

        with pytest.raises(QuantumError) as exc_info:
            with ResourceManager() as rm:
                rm.execute()

        assert exc_info.value.details["qubits"] == 5


class TestExceptionErrorCodes:
    """Test error code consistency across layers"""

    def test_error_codes_are_unique(self):
        """Test that different exception types have different error codes"""
        exc1 = BiologyError("Test")
        exc2 = QuantumError("Test")
        exc3 = DatabaseError("Test")

        assert exc1.error_code != exc2.error_code
        assert exc2.error_code != exc3.error_code
        assert exc1.error_code == "BiologyError"
        assert exc2.error_code == "QuantumError"
        assert exc3.error_code == "DatabaseError"

    def test_custom_error_codes_preserved(self):
        """Test that custom error codes are preserved"""
        exc = BiologyError(
            "Test",
            error_code="BIO_CUSTOM_001"
        )

        assert exc.error_code == "BIO_CUSTOM_001"

        # Serialization preserves custom code
        result = exc.to_dict()
        assert result["error"] == "BIO_CUSTOM_001"
