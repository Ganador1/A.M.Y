"""
Tests for validation exceptions
"""
import pytest
from app.exceptions.validation.input import (
    InputValidationError,
    SchemaValidationError,
    ParameterValidationError
)
from app.exceptions.validation.output import (
    OutputValidationError,
    ResultValidationError
)
from app.exceptions.validation.ethics import (
    EthicsViolationError,
    SafetyError,
    ComplianceError
)
from app.exceptions.base import AtlasValidationError, AtlasSecurityError


class TestInputValidationExceptions:
    """Test input validation exceptions"""

    def test_input_validation_error_basic(self):
        """Test basic InputValidationError"""
        exc = InputValidationError("Invalid input")
        assert isinstance(exc, AtlasValidationError)
        assert exc.error_code == "InputValidationError"

    def test_schema_validation_error(self):
        """Test SchemaValidationError"""
        exc = SchemaValidationError(
            "Schema validation failed",
            details={
                "schema": "ExperimentRequest",
                "field": "temperature",
                "expected": "float > 0",
                "received": -273.15
            }
        )
        assert isinstance(exc, InputValidationError)
        assert exc.details["field"] == "temperature"

    def test_parameter_validation_error(self):
        """Test ParameterValidationError"""
        exc = ParameterValidationError(
            "Invalid parameter value",
            details={
                "parameter": "num_qubits",
                "value": 100,
                "min": 1,
                "max": 30,
                "error": "value_out_of_range"
            }
        )
        assert isinstance(exc, InputValidationError)
        assert exc.details["max"] == 30

    def test_input_validation_with_multiple_errors(self):
        """Test InputValidationError with multiple field errors"""
        exc = InputValidationError(
            "Multiple validation errors",
            details={
                "errors": [
                    {"field": "email", "error": "invalid_format"},
                    {"field": "age", "error": "out_of_range"},
                    {"field": "name", "error": "required"}
                ]
            }
        )
        assert len(exc.details["errors"]) == 3


class TestOutputValidationExceptions:
    """Test output validation exceptions"""

    def test_output_validation_error_basic(self):
        """Test basic OutputValidationError"""
        exc = OutputValidationError("Output validation failed")
        assert isinstance(exc, AtlasValidationError)

    def test_result_validation_error(self):
        """Test ResultValidationError"""
        exc = ResultValidationError(
            "Result format invalid",
            details={
                "expected_type": "dict",
                "received_type": "list",
                "operation": "protein_analysis"
            }
        )
        assert isinstance(exc, OutputValidationError)
        assert exc.details["expected_type"] == "dict"

    def test_output_validation_with_schema(self):
        """Test OutputValidationError with schema mismatch"""
        exc = OutputValidationError(
            "Response schema mismatch",
            details={
                "schema": "ExperimentResult",
                "missing_fields": ["hypothesis_id", "confidence"],
                "extra_fields": ["unknown_field"]
            }
        )
        assert "missing_fields" in exc.details
        assert len(exc.details["missing_fields"]) == 2


class TestEthicsExceptions:
    """Test ethics and safety exceptions"""

    def test_ethics_violation_error_basic(self):
        """Test basic EthicsViolationError"""
        exc = EthicsViolationError("Ethics check failed")
        assert isinstance(exc, AtlasSecurityError)

    def test_ethics_violation_with_policy(self):
        """Test EthicsViolationError with policy violation"""
        exc = EthicsViolationError(
            "Dual-use research detected",
            details={
                "policy": "dual_use_research",
                "risk_level": "high",
                "domain": "chemistry",
                "flagged_terms": ["explosive", "weaponization"]
            }
        )
        assert exc.details["risk_level"] == "high"
        assert len(exc.details["flagged_terms"]) == 2

    def test_safety_error(self):
        """Test SafetyError"""
        exc = SafetyError(
            "Unsafe parameter detected",
            details={
                "parameter": "reaction_temperature",
                "value": 2000,
                "safe_max": 1000,
                "risk": "thermal_runaway"
            }
        )
        assert isinstance(exc, EthicsViolationError)
        assert exc.details["risk"] == "thermal_runaway"

    def test_compliance_error(self):
        """Test ComplianceError"""
        exc = ComplianceError(
            "Regulatory compliance violation",
            details={
                "regulation": "GDPR",
                "violation": "data_retention_exceeded",
                "retention_days": 400,
                "max_allowed": 365
            }
        )
        assert isinstance(exc, EthicsViolationError)
        assert exc.details["regulation"] == "GDPR"


class TestValidationExceptionHierarchy:
    """Test validation exception hierarchy"""

    def test_input_validation_hierarchy(self):
        """Test input validation inheritance"""
        assert isinstance(SchemaValidationError("test"), InputValidationError)
        assert isinstance(ParameterValidationError("test"), InputValidationError)
        assert isinstance(InputValidationError("test"), AtlasValidationError)

    def test_output_validation_hierarchy(self):
        """Test output validation inheritance"""
        assert isinstance(ResultValidationError("test"), OutputValidationError)
        assert isinstance(OutputValidationError("test"), AtlasValidationError)

    def test_ethics_hierarchy(self):
        """Test ethics exception inheritance"""
        assert isinstance(SafetyError("test"), EthicsViolationError)
        assert isinstance(ComplianceError("test"), EthicsViolationError)
        assert isinstance(EthicsViolationError("test"), AtlasSecurityError)


class TestValidationUseCases:
    """Test real-world validation scenarios"""

    def test_pydantic_validation_wrapper(self):
        """Test wrapping Pydantic validation errors"""
        from pydantic import ValidationError as PydanticValidationError

        def validate_experiment(data: dict):
            # Simulate Pydantic validation failure
            raise SchemaValidationError(
                "Pydantic validation failed",
                details={
                    "schema": "ExperimentCreate",
                    "errors": [
                        {
                            "loc": ["temperature"],
                            "msg": "ensure this value is greater than 0",
                            "type": "value_error.number.not_gt"
                        }
                    ]
                }
            )

        with pytest.raises(SchemaValidationError) as exc_info:
            validate_experiment({"temperature": -10})

        assert "Pydantic" in exc_info.value.message

    def test_parameter_range_validation(self):
        """Test parameter range validation"""
        def validate_qubits(num_qubits: int):
            if num_qubits < 1 or num_qubits > 30:
                raise ParameterValidationError(
                    f"Invalid qubit count: {num_qubits}",
                    details={
                        "parameter": "num_qubits",
                        "value": num_qubits,
                        "valid_range": "1-30"
                    }
                )

        with pytest.raises(ParameterValidationError) as exc_info:
            validate_qubits(50)

        assert exc_info.value.details["value"] == 50

    def test_ethics_gate_validation(self):
        """Test ethics gate validation"""
        def check_research_ethics(hypothesis: str):
            dangerous_keywords = ["bioweapon", "nerve agent", "explosive"]

            for keyword in dangerous_keywords:
                if keyword.lower() in hypothesis.lower():
                    raise EthicsViolationError(
                        "Potentially harmful research detected",
                        details={
                            "flagged_keyword": keyword,
                            "policy": "dual_use_research_prevention",
                            "action": "blocked"
                        }
                    )

        with pytest.raises(EthicsViolationError) as exc_info:
            check_research_ethics("Design a nerve agent delivery system")

        assert exc_info.value.details["flagged_keyword"] == "nerve agent"
        assert exc_info.value.details["action"] == "blocked"
