"""
Tests for base exception framework
"""
import pytest
from app.exceptions.base import (
    AtlasException,
    AtlasValidationError,
    AtlasInfrastructureError,
    AtlasDomainError,
    AtlasExternalError,
    AtlasSecurityError,
)


class TestAtlasException:
    """Test base AtlasException functionality"""

    def test_basic_exception_creation(self):
        """Test creating exception with message only"""
        exc = AtlasException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.error_code == "AtlasException"

    def test_exception_with_error_code(self):
        """Test exception with custom error code"""
        exc = AtlasException("Test error", error_code="CUSTOM_001")
        assert exc.error_code == "CUSTOM_001"
        assert exc.message == "Test error"

    def test_exception_with_details(self):
        """Test exception with details dict"""
        details = {"field": "username", "value": "test", "reason": "invalid"}
        exc = AtlasException("Validation failed", details=details)
        assert exc.details == details
        assert exc.details["field"] == "username"

    def test_exception_with_cause(self):
        """Test exception chaining with cause"""
        original = ValueError("Original error")
        exc = AtlasException("Wrapped error", cause=original)
        assert exc.cause == original
        assert isinstance(exc.cause, ValueError)

    def test_exception_to_dict(self):
        """Test serialization to dict for API responses"""
        exc = AtlasException(
            "Test error",
            error_code="TEST_001",
            details={"key": "value"}
        )
        result = exc.to_dict()

        assert result["error"] == "TEST_001"
        assert result["message"] == "Test error"
        assert result["details"] == {"key": "value"}
        assert isinstance(result, dict)

    def test_exception_inheritance(self):
        """Test that exception can be caught as Exception"""
        with pytest.raises(Exception):
            raise AtlasException("Test")

        with pytest.raises(AtlasException):
            raise AtlasException("Test")


class TestAtlasExceptionSubclasses:
    """Test exception hierarchy subclasses"""

    def test_validation_error(self):
        """Test AtlasValidationError"""
        exc = AtlasValidationError("Invalid input")
        assert isinstance(exc, AtlasException)
        assert exc.error_code == "AtlasValidationError"

    def test_infrastructure_error(self):
        """Test AtlasInfrastructureError"""
        exc = AtlasInfrastructureError("Database connection failed")
        assert isinstance(exc, AtlasException)
        assert exc.error_code == "AtlasInfrastructureError"

    def test_domain_error(self):
        """Test AtlasDomainError"""
        exc = AtlasDomainError("Scientific computation failed")
        assert isinstance(exc, AtlasException)
        assert exc.error_code == "AtlasDomainError"

    def test_external_error(self):
        """Test AtlasExternalError"""
        exc = AtlasExternalError("API call failed")
        assert isinstance(exc, AtlasException)
        assert exc.error_code == "AtlasExternalError"

    def test_security_error(self):
        """Test AtlasSecurityError"""
        exc = AtlasSecurityError("Ethics violation detected")
        assert isinstance(exc, AtlasException)
        assert exc.error_code == "AtlasSecurityError"


class TestExceptionChaining:
    """Test exception chaining and cause tracking"""

    def test_chain_with_from(self):
        """Test exception chaining with 'from' keyword"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise AtlasException("Wrapped error", cause=e) from e
        except AtlasException as exc:
            assert exc.cause is not None
            assert isinstance(exc.cause, ValueError)
            assert str(exc.cause) == "Original error"

    def test_multiple_level_chaining(self):
        """Test multiple levels of exception chaining"""
        try:
            raise ValueError("Level 1")
        except ValueError as e1:
            try:
                raise AtlasException("Level 2", cause=e1)
            except AtlasException as e2:
                exc = AtlasException("Level 3", cause=e2)
                assert exc.cause.cause == e1


class TestExceptionDetails:
    """Test exception details handling"""

    def test_empty_details(self):
        """Test exception with no details"""
        exc = AtlasException("Error")
        assert exc.details == {}

    def test_complex_details(self):
        """Test exception with complex details structure"""
        details = {
            "request_id": "12345",
            "user": {"id": 1, "name": "test"},
            "context": {
                "service": "biology",
                "operation": "protein_analysis",
                "parameters": {"uniprot_id": "P04637"}
            }
        }
        exc = AtlasException("Operation failed", details=details)
        assert exc.details["request_id"] == "12345"
        assert exc.details["user"]["name"] == "test"
        assert exc.details["context"]["service"] == "biology"

    def test_details_in_to_dict(self):
        """Test that details are preserved in to_dict()"""
        details = {"operation": "test", "status": "failed"}
        exc = AtlasException("Error", details=details)
        result = exc.to_dict()
        assert result["details"] == details


class TestExceptionErrorCodes:
    """Test error code handling"""

    def test_default_error_code(self):
        """Test that default error code is class name"""
        exc = AtlasException("Test")
        assert exc.error_code == "AtlasException"

    def test_custom_error_code(self):
        """Test custom error code"""
        exc = AtlasException("Test", error_code="ATLAS_CUSTOM_001")
        assert exc.error_code == "ATLAS_CUSTOM_001"

    def test_error_code_in_to_dict(self):
        """Test error code in serialization"""
        exc = AtlasException("Test", error_code="TEST_CODE")
        result = exc.to_dict()
        assert result["error"] == "TEST_CODE"


class TestExceptionRaising:
    """Test raising and catching exceptions"""

    def test_raise_and_catch_specific(self):
        """Test raising and catching specific exception type"""
        with pytest.raises(AtlasValidationError) as exc_info:
            raise AtlasValidationError("Validation failed")

        assert "Validation failed" in str(exc_info.value)

    def test_raise_and_catch_base(self):
        """Test catching subclass with base class"""
        with pytest.raises(AtlasException):
            raise AtlasValidationError("Test")

    def test_exception_message_format(self):
        """Test exception message formatting"""
        exc = AtlasException(
            "Operation failed for user {user_id}",
            details={"user_id": 12345}
        )
        # Message should be stored as-is
        assert exc.message == "Operation failed for user {user_id}"
        # Details should contain the data
        assert exc.details["user_id"] == 12345
