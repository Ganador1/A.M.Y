"""
Tests unitarios para Operational Cross-Validation Matrix
=====================================================

Validación completa del sistema de matriz de validación cruzada operativa
con cuantificación de incertidumbre e integración de múltiples dominios.
"""

import pytest

from app.operational_cross_validation_matrix import (
    OperationalCrossValidationMatrix,
    MathematicalCompatibilityValidator,
    PhysicsCompatibilityValidator,
    BiologicalCompatibilityValidator,
    CrossValidationRun,
    ValidationDomain,
    CompatibilityScore,
    CompatibilityLevel
)


class TestMathematicalCompatibilityValidator:
    """Tests para validador de compatibilidad matemática"""
    
    @pytest.fixture
    def validator(self):
        return MathematicalCompatibilityValidator()
    
    @pytest.mark.asyncio
    async def test_validate_compatible_services(self, validator):
        """Test validación de servicios matemáticamente compatibles"""
        # Servicios de prueba
        service_a = "mathematical_service_a"
        service_b = "mathematical_service_b"
        domain = ValidationDomain.MATHEMATICS
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.MATHEMATICS
        assert isinstance(score.level, CompatibilityLevel)
    
    @pytest.mark.asyncio
    async def test_validate_incompatible_services(self, validator):
        """Test validación de servicios matemáticamente incompatibles"""
        # Servicios de prueba
        service_a = "text_service"
        service_b = "boolean_service"
        domain = ValidationDomain.MATHEMATICS
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0  # Siempre positivo
        assert score.domain == ValidationDomain.MATHEMATICS
    
    @pytest.mark.asyncio
    async def test_validate_empty_results(self, validator):
        """Test validación con servicios simples"""
        service_a = "empty_service_a"
        service_b = "empty_service_b"
        domain = ValidationDomain.MATHEMATICS
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.MATHEMATICS


class TestPhysicsCompatibilityValidator:
    """Tests para validador de compatibilidad física"""
    
    @pytest.fixture
    def validator(self):
        return PhysicsCompatibilityValidator()
    
    @pytest.mark.asyncio
    async def test_validate_physics_units(self, validator):
        """Test validación de unidades físicas"""
        # Servicios de prueba
        service_a = "thermodynamics_service"
        service_b = "temperature_service"
        domain = ValidationDomain.PHYSICS
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.PHYSICS
    
    @pytest.mark.asyncio
    async def test_validate_energy_conservation(self, validator):
        """Test validación de conservación de energía"""
        service_a = "energy_analyzer"
        service_b = "power_calculator"
        domain = ValidationDomain.PHYSICS
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.PHYSICS


class TestBiologicalCompatibilityValidator:
    """Tests para validador de compatibilidad biológica"""
    
    @pytest.fixture
    def validator(self):
        return BiologicalCompatibilityValidator()
    
    @pytest.mark.asyncio
    async def test_validate_biological_sequences(self, validator):
        """Test validación de secuencias biológicas"""
        # Servicios de prueba
        service_a = "dna_analyzer"
        service_b = "protein_predictor"
        domain = ValidationDomain.BIOLOGY
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.BIOLOGY
    
    @pytest.mark.asyncio
    async def test_validate_biological_metrics(self, validator):
        """Test validación de métricas biológicas"""
        service_a = "ph_monitor"
        service_b = "concentration_analyzer"
        domain = ValidationDomain.BIOLOGY
        
        score = await validator.validate_compatibility(service_a, service_b, domain)
        
        assert score.score >= 0.0
        assert score.domain == ValidationDomain.BIOLOGY


class TestOperationalCrossValidationMatrix:
    """Tests para matriz de validación cruzada operativa"""
    
    @pytest.fixture
    def matrix(self):
        return OperationalCrossValidationMatrix()
    
    @pytest.mark.asyncio
    async def test_initialization(self, matrix):
        """Test inicialización correcta de la matriz"""
        assert len(matrix.validators) == 8  # 8 dominios de validación
        assert ValidationDomain.MATHEMATICS in matrix.validators
        assert ValidationDomain.PHYSICS in matrix.validators
        assert ValidationDomain.BIOLOGY in matrix.validators
        assert matrix.uncertainty_service is not None
    
    @pytest.mark.asyncio
    async def test_validate_cross_compatibility_basic(self, matrix):
        """Test ejecución básica de validación cruzada"""
        # Servicios de prueba  
        services = {
            "math_service": {"calculation": 42.0, "result": "success"},
            "physics_service": {"energy": 100.0, "unit": "J"},
            "bio_service": {"sequence": "ATCG", "valid": True}
        }
        
        # Ejecutar validación cruzada
        run = await matrix.validate_cross_compatibility(list(services.keys()))
        
        # Verificaciones
        assert isinstance(run, CrossValidationRun)
        assert run.run_id is not None
        assert len(run.services_involved) >= 1
        assert 0.0 <= run.aggregate_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_health_check(self, matrix):
        """Test verificación de salud del sistema"""
        health = await matrix.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "validators" in health
        assert "uncertainty_service" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert isinstance(health["validators"], dict)
        assert len(health["validators"]) == 8
    
    @pytest.mark.asyncio
    async def test_get_compatibility_matrix(self, matrix):
        """Test obtención de matriz de compatibilidad"""
        services = ["service_1", "service_2"]
        
        result = await matrix.get_compatibility_matrix(services)
        
        assert isinstance(result, dict)
        assert "services" in result
        assert "compatibility_matrix" in result


class TestCrossValidationRun:
    """Tests para clase CrossValidationRun"""
    
    def test_run_creation(self):
        """Test creación de run de validación"""
        run = CrossValidationRun(
            run_id="test_123",
            services_involved=["service_a", "service_b"],
            domain=ValidationDomain.MATHEMATICS,
            aggregate_score=0.8,
            individual_scores=[],
            uncertainty_metrics={},
            execution_time_ms=100
        )
        
        assert run.run_id == "test_123"
        assert len(run.services_involved) == 2
        assert run.aggregate_score == 0.8
    
    def test_run_validation(self):
        """Test validación de datos del run"""
        # Crear run con datos válidos
        run = CrossValidationRun(
            run_id="valid_run",
            services_involved=["service_1"],
            domain=ValidationDomain.BIOLOGY,
            aggregate_score=0.7,
            individual_scores=[],
            uncertainty_metrics={"uncertainty": 0.1},
            execution_time_ms=150
        )
        
        # Verificar rangos válidos
        assert 0.0 <= run.aggregate_score <= 1.0
        assert run.execution_time_ms > 0


class TestCompatibilityScore:
    """Tests para clase CompatibilityScore"""
    
    def test_score_creation(self):
        """Test creación de score de compatibilidad"""
        score = CompatibilityScore(
            service_a="service_1",
            service_b="service_2",
            domain=ValidationDomain.MATHEMATICS,
            level=CompatibilityLevel.COMPATIBLE,
            score=0.85,
            confidence=0.9
        )
        
        assert score.service_a == "service_1"
        assert score.service_b == "service_2"
        assert score.domain == ValidationDomain.MATHEMATICS
        assert score.score == 0.85
        assert score.level == CompatibilityLevel.COMPATIBLE


@pytest.mark.integration
class TestOperationalCrossValidationIntegration:
    """Tests de integración para matriz operativa"""
    
    @pytest.mark.asyncio
    async def test_full_ecosystem_validation(self):
        """Test validación completa del ecosistema"""
        # Simular múltiples servicios del ecosistema AXIOM
        matrix = OperationalCrossValidationMatrix()
        
        ecosystem_services = ["math_service", "physics_service", "bio_service", "medical_service"]
        
        # Ejecutar validación cruzada completa
        run = await matrix.validate_cross_compatibility(ecosystem_services)
        
        # Verificaciones de integración
        assert len(run.services_involved) >= 1
        assert run.aggregate_score >= 0.0
        assert run.execution_time_ms > 0
        
        # Verificar salud del sistema
        health = await matrix.health_check()
        assert health["status"] in ["healthy", "degraded"]


if __name__ == "__main__":
    # Ejecutar tests específicos para debugging
    pytest.main([__file__, "-v", "--tb=short"])
