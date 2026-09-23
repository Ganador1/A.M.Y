"""
Tests for domain-specific exceptions
"""
import pytest
from app.exceptions.domain.biology import BiologyError, ProteinAnalysisError
from app.exceptions.domain.chemistry import ChemistryError, MolecularError
from app.exceptions.domain.physics import PhysicsError, QuantumError
from app.exceptions.domain.mathematics import MathematicsError, SymbolicError
from app.exceptions.domain.medicine import MedicalError, DiagnosticError
from app.exceptions.domain.neuroscience import NeuroscienceError, BrainImagingError
from app.exceptions.domain.engineering import EngineeringError, MaterialsError
from app.exceptions.base import AtlasDomainError


class TestBiologyExceptions:
    """Test biology domain exceptions"""

    def test_biology_error_basic(self):
        """Test basic BiologyError creation"""
        exc = BiologyError("Biological analysis failed")
        assert isinstance(exc, AtlasDomainError)
        assert exc.error_code == "BiologyError"

    def test_protein_analysis_error(self):
        """Test ProteinAnalysisError"""
        exc = ProteinAnalysisError(
            "Failed to analyze protein",
            details={"uniprot_id": "P04637", "reason": "structure_unavailable"}
        )
        assert isinstance(exc, BiologyError)
        assert exc.details["uniprot_id"] == "P04637"

    def test_biology_error_with_gene_context(self):
        """Test BiologyError with gene analysis context"""
        exc = BiologyError(
            "Gene expression analysis failed",
            details={
                "gene_id": "BRCA1",
                "organism": "Homo sapiens",
                "analysis_type": "differential_expression"
            }
        )
        assert exc.details["gene_id"] == "BRCA1"
        assert exc.error_code == "BiologyError"


class TestChemistryExceptions:
    """Test chemistry domain exceptions"""

    def test_chemistry_error_basic(self):
        """Test basic ChemistryError creation"""
        exc = ChemistryError("Chemical computation failed")
        assert isinstance(exc, AtlasDomainError)
        assert exc.error_code == "ChemistryError"

    def test_molecular_error(self):
        """Test MolecularError"""
        exc = MolecularError(
            "Invalid SMILES string",
            details={"smiles": "CCO", "error": "parse_failed"}
        )
        assert isinstance(exc, ChemistryError)
        assert exc.details["smiles"] == "CCO"

    def test_chemistry_error_with_reaction(self):
        """Test ChemistryError with reaction context"""
        exc = ChemistryError(
            "Reaction simulation failed",
            details={
                "reactants": ["C2H5OH", "CH3COOH"],
                "products": ["C4H8O2", "H2O"],
                "temperature": 298.15
            }
        )
        assert len(exc.details["reactants"]) == 2


class TestPhysicsExceptions:
    """Test physics domain exceptions"""

    def test_physics_error_basic(self):
        """Test basic PhysicsError creation"""
        exc = PhysicsError("Physics simulation failed")
        assert isinstance(exc, AtlasDomainError)

    def test_quantum_error(self):
        """Test QuantumError"""
        exc = QuantumError(
            "Quantum circuit execution failed",
            details={
                "backend": "qasm_simulator",
                "qubits": 5,
                "circuit_depth": 10,
                "error": "insufficient_qubits"
            }
        )
        assert isinstance(exc, PhysicsError)
        assert exc.details["qubits"] == 5

    def test_quantum_error_serialization(self):
        """Test QuantumError serialization for API"""
        exc = QuantumError("Circuit failed", details={"circuit_id": "123"})
        result = exc.to_dict()
        assert result["error"] == "QuantumError"
        assert result["details"]["circuit_id"] == "123"


class TestMathematicsExceptions:
    """Test mathematics domain exceptions"""

    def test_mathematics_error_basic(self):
        """Test basic MathematicsError creation"""
        exc = MathematicsError("Mathematical computation failed")
        assert isinstance(exc, AtlasDomainError)

    def test_symbolic_error(self):
        """Test SymbolicError"""
        exc = SymbolicError(
            "Symbolic equation solving failed",
            details={
                "equation": "x**2 + 2*x + 1 = 0",
                "method": "solve",
                "error": "no_solution"
            }
        )
        assert isinstance(exc, MathematicsError)
        assert "equation" in exc.details

    def test_mathematics_error_with_matrix(self):
        """Test MathematicsError with matrix context"""
        exc = MathematicsError(
            "Matrix inversion failed",
            details={
                "matrix_size": (3, 3),
                "condition_number": 1e15,
                "error": "singular_matrix"
            }
        )
        assert exc.details["matrix_size"] == (3, 3)


class TestMedicineExceptions:
    """Test medicine domain exceptions"""

    def test_medical_error_basic(self):
        """Test basic MedicalError creation"""
        exc = MedicalError("Medical imaging processing failed")
        assert isinstance(exc, AtlasDomainError)

    def test_diagnostic_error(self):
        """Test DiagnosticError"""
        exc = DiagnosticError(
            "Diagnostic analysis failed",
            details={
                "patient_id": "P12345",
                "modality": "CT",
                "body_part": "chest",
                "error": "low_quality_image"
            }
        )
        assert isinstance(exc, MedicalError)
        assert exc.details["modality"] == "CT"

    def test_medical_error_with_dicom(self):
        """Test MedicalError with DICOM context"""
        exc = MedicalError(
            "DICOM file parsing failed",
            details={
                "file_path": "/data/scan001.dcm",
                "sop_class_uid": "1.2.840.10008.5.1.4.1.1.2",
                "error": "missing_required_tags"
            }
        )
        assert "file_path" in exc.details


class TestNeuroscienceExceptions:
    """Test neuroscience domain exceptions"""

    def test_neuroscience_error_basic(self):
        """Test basic NeuroscienceError creation"""
        exc = NeuroscienceError("Neural network analysis failed")
        assert isinstance(exc, AtlasDomainError)

    def test_brain_imaging_error(self):
        """Test BrainImagingError"""
        exc = BrainImagingError(
            "fMRI preprocessing failed",
            details={
                "subject_id": "sub-001",
                "session": "ses-01",
                "task": "rest",
                "error": "motion_artifacts"
            }
        )
        assert isinstance(exc, NeuroscienceError)
        assert exc.details["task"] == "rest"


class TestEngineeringExceptions:
    """Test engineering domain exceptions"""

    def test_engineering_error_basic(self):
        """Test basic EngineeringError creation"""
        exc = EngineeringError("Engineering simulation failed")
        assert isinstance(exc, AtlasDomainError)

    def test_materials_error(self):
        """Test MaterialsError"""
        exc = MaterialsError(
            "Material property calculation failed",
            details={
                "material": "Ti-6Al-4V",
                "property": "yield_strength",
                "temperature": 300,
                "error": "insufficient_data"
            }
        )
        assert isinstance(exc, EngineeringError)
        assert exc.details["material"] == "Ti-6Al-4V"


class TestDomainExceptionHierarchy:
    """Test exception hierarchy and inheritance"""

    def test_all_inherit_from_domain_error(self):
        """Test that all domain exceptions inherit from AtlasDomainError"""
        exceptions = [
            BiologyError("test"),
            ChemistryError("test"),
            PhysicsError("test"),
            MathematicsError("test"),
            MedicalError("test"),
            NeuroscienceError("test"),
            EngineeringError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AtlasDomainError)

    def test_specialized_inherit_from_base_domain(self):
        """Test that specialized exceptions inherit from base domain exception"""
        assert isinstance(ProteinAnalysisError("test"), BiologyError)
        assert isinstance(MolecularError("test"), ChemistryError)
        assert isinstance(QuantumError("test"), PhysicsError)
        assert isinstance(SymbolicError("test"), MathematicsError)
        assert isinstance(DiagnosticError("test"), MedicalError)
        assert isinstance(BrainImagingError("test"), NeuroscienceError)
        assert isinstance(MaterialsError("test"), EngineeringError)

    def test_catch_with_base_domain_error(self):
        """Test catching domain-specific error with base AtlasDomainError"""
        with pytest.raises(AtlasDomainError):
            raise BiologyError("Test")

        with pytest.raises(AtlasDomainError):
            raise QuantumError("Test")


class TestDomainExceptionUseCases:
    """Test real-world use cases for domain exceptions"""

    def test_protein_analysis_pipeline_error(self):
        """Test protein analysis pipeline error handling"""
        def analyze_protein(uniprot_id: str):
            if not uniprot_id.startswith("P"):
                raise ProteinAnalysisError(
                    f"Invalid UniProt ID format: {uniprot_id}",
                    details={"uniprot_id": uniprot_id, "expected_format": "P[0-9]+"}
                )

        with pytest.raises(ProteinAnalysisError) as exc_info:
            analyze_protein("INVALID")

        assert "Invalid UniProt ID" in str(exc_info.value)
        assert exc_info.value.details["uniprot_id"] == "INVALID"

    def test_quantum_circuit_error(self):
        """Test quantum circuit execution error"""
        def execute_circuit(qubits: int):
            if qubits > 30:
                raise QuantumError(
                    f"Too many qubits requested: {qubits}",
                    details={"qubits_requested": qubits, "max_qubits": 30}
                )

        with pytest.raises(QuantumError) as exc_info:
            execute_circuit(50)

        assert exc_info.value.details["qubits_requested"] == 50

    def test_chemical_reaction_error(self):
        """Test chemical reaction simulation error"""
        def simulate_reaction(temperature: float):
            if temperature > 1000:
                raise ChemistryError(
                    "Temperature exceeds safe limits",
                    details={"temperature": temperature, "max_safe": 1000}
                )

        with pytest.raises(ChemistryError) as exc_info:
            simulate_reaction(1500)

        assert exc_info.value.details["temperature"] == 1500
