"""
Tests comprehensivos para MedicineRegistry
=========================================

Suite de testing completa para el sistema de registro médico especializado.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

from app.domains.medicine.registry import (
    MedicineRegistry, MedicalCapabilityType, MedicalSession,
    RealTimeStream, SessionStatus, get_medicine_registry
)
from app.infrastructure.service_registry_discovery import (
    ServiceMetadata, ServiceCapability, CapabilityType, ServiceStatus
)


class TestMedicineRegistry:
    """Test suite para MedicineRegistry core functionality"""

    @pytest.fixture
    def mock_base_registry(self):
        """Mock del ServiceRegistry base"""
        mock_registry = Mock()
        mock_registry.register_service = AsyncMock(return_value=True)
        return mock_registry

    @pytest.fixture
    async def medicine_registry(self, mock_base_registry):
        """Fixture para MedicineRegistry configurado"""
        registry = MedicineRegistry(base_registry=mock_base_registry)
        await registry.initialize()
        return registry

    @pytest.mark.asyncio
    async def test_initialization(self, medicine_registry):
        """Test inicialización del registry médico"""
        assert medicine_registry.base_registry is not None
        assert len(medicine_registry._medical_services) >= 4  # Auto-registered services
        assert medicine_registry.default_session_duration_hours == 24
        assert medicine_registry.max_concurrent_sessions == 100

    @pytest.mark.asyncio
    async def test_register_medical_service(self, medicine_registry):
        """Test registro de servicio médico"""
        # Crear capability médica
        capability = ServiceCapability(
            name="test_imaging_capability",
            type=CapabilityType.COMPUTATIONAL,
            description="Test medical imaging capability",
            input_schema={},
            output_schema={}
        )

        # Crear metadata del servicio
        service_metadata = ServiceMetadata(
            service_id="test_medical_service",
            name="Test Medical Service",
            version="1.0.0",
            description="Test service for medical domain",
            endpoint=None,
            capabilities=[capability],
            tags=["test", "medical"],
            health_status=ServiceStatus.HEALTHY
        )

        # Registrar servicio
        result = await medicine_registry.register_medical_service(service_metadata)

        assert result is True
        assert "test_medical_service" in medicine_registry._medical_services
        medicine_registry.base_registry.register_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_medical_session(self, medicine_registry):
        """Test creación de sesión médica"""
        patient_id = "TEST_PATIENT_001"
        session_type = "imaging_analysis"
        clinical_context = {"modality": "MRI", "body_part": "brain"}

        session = await medicine_registry.create_medical_session(
            session_type=session_type,
            patient_id=patient_id,
            clinical_context=clinical_context,
            duration_hours=48
        )

        assert isinstance(session, MedicalSession)
        assert session.patient_id == patient_id
        assert session.session_type == session_type
        assert session.clinical_context == clinical_context
        assert session.status == SessionStatus.ACTIVE

        # Verificar indexación por paciente
        assert patient_id in medicine_registry._patient_sessions
        assert session.session_id in medicine_registry._patient_sessions[patient_id]

    @pytest.mark.asyncio
    async def test_create_real_time_stream(self, medicine_registry):
        """Test creación de stream de tiempo real"""
        # Crear sesión primero
        session = await medicine_registry.create_medical_session(
            session_type="monitoring",
            patient_id="TEST_PATIENT_002"
        )

        # Crear stream
        stream = await medicine_registry.create_real_time_stream(
            source="ecg_monitor",
            data_type="ecg",
            session_id=session.session_id,
            auto_analysis=True
        )

        assert isinstance(stream, RealTimeStream)
        assert stream.source == "ecg_monitor"
        assert stream.data_type == "ecg"
        assert stream.session_id == session.session_id
        assert stream.auto_analysis is True
        assert stream.is_active is True

        # Verificar asociación con sesión
        assert session.session_id in medicine_registry._active_streams
        assert stream.stream_id in medicine_registry._active_streams[session.session_id]

    @pytest.mark.asyncio
    async def test_discover_medical_services(self, medicine_registry):
        """Test descubrimiento de servicios médicos"""
        services = await medicine_registry.discover_medical_services(
            capability=MedicalCapabilityType.MEDICAL_IMAGING,
            tags=["imaging"]
        )

        assert len(services) >= 1
        for service in services:
            assert isinstance(service, ServiceMetadata)
            assert "imaging" in service.tags

    @pytest.mark.asyncio
    async def test_process_real_time_data(self, medicine_registry):
        """Test procesamiento de datos en tiempo real"""
        # Crear stream
        stream = await medicine_registry.create_real_time_stream(
            source="pulse_oximeter",
            data_type="spo2"
        )

        # Simular datos
        test_data = {"spo2": 98, "heart_rate": 75, "timestamp": datetime.now()}

        # Procesar datos
        result = await medicine_registry.process_real_time_data(
            stream_id=stream.stream_id,
            data=test_data
        )

        assert "processed_at" in result
        assert result["data_type"] == "spo2"
        assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_validate_clinical_result(self, medicine_registry):
        """Test validación de resultados clínicos"""
        # Test validación de accuracy clínica
        result = {"clinical_accuracy_score": 0.92}
        validation = await medicine_registry.validate_clinical_result(
            result, validation_type="clinical_accuracy"
        )

        assert validation["passed"] is False  # Below 0.95 threshold
        assert validation["metrics"]["accuracy"] == 0.92
        assert len(validation["recommendations"]) > 0

        # Test validación de confianza diagnóstica
        result = {"diagnostic_confidence": 0.90}
        validation = await medicine_registry.validate_clinical_result(
            result, validation_type="diagnostic_confidence"
        )

        assert validation["passed"] is True  # Above 0.85 threshold
        assert validation["metrics"]["confidence"] == 0.90

    @pytest.mark.asyncio
    async def test_get_session_status(self, medicine_registry):
        """Test obtención de estado de sesión"""
        # Crear sesión con análisis
        session = await medicine_registry.create_medical_session(
            session_type="genomics",
            patient_id="TEST_PATIENT_003"
        )

        # Simular análisis activo
        session.add_analysis("analysis_001", "variant_calling", {"type": "WGS"})
        session.complete_analysis("analysis_001", {"variants_found": 4500000})

        # Obtener estado
        status = await medicine_registry.get_session_status(session.session_id)

        assert status["session_id"] == session.session_id
        assert status["patient_id"] == "TEST_PATIENT_003"
        assert status["status"] == "active"
        assert status["session_type"] == "genomics"
        assert status["completed_analyses"] == 1

    @pytest.mark.asyncio
    async def test_get_medical_registry_stats(self, medicine_registry):
        """Test estadísticas del registry médico"""
        # Crear algunas sesiones y streams
        await medicine_registry.create_medical_session("imaging", "PATIENT_001")
        await medicine_registry.create_medical_session("genomics", "PATIENT_002")

        stats = await medicine_registry.get_medical_registry_stats()

        assert stats["total_medical_services"] >= 4
        assert stats["active_sessions"] >= 2
        assert stats["total_sessions"] >= 2
        assert "capability_distribution" in stats
        assert stats["registry_health"] == "healthy"

    @pytest.mark.asyncio
    async def test_session_expiration(self, medicine_registry):
        """Test expiración de sesiones"""
        # Crear sesión con duración muy corta
        session = await medicine_registry.create_medical_session(
            session_type="test",
            patient_id="EXPIRE_TEST",
            duration_hours=0.001  # ~4 segundos
        )

        # Verificar que está activa
        assert session.status == SessionStatus.ACTIVE
        assert not session.is_expired()

        # Esperar expiración (simulada modificando expires_at)
        session.expires_at = datetime.now() - timedelta(minutes=1)

        # Verificar expiración
        assert session.is_expired()

        # Obtener estado (debería marcar como completada)
        status = await medicine_registry.get_session_status(session.session_id)
        assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_max_concurrent_sessions_limit(self, medicine_registry):
        """Test límite de sesiones concurrentes"""
        # Reducir límite temporalmente para el test
        original_limit = medicine_registry.max_concurrent_sessions
        medicine_registry.max_concurrent_sessions = 2

        try:
            # Crear sesiones hasta el límite
            await medicine_registry.create_medical_session("test", "PATIENT_1")
            await medicine_registry.create_medical_session("test", "PATIENT_2")

            # Intentar crear una más debería fallar
            with pytest.raises(RuntimeError, match="Maximum concurrent sessions"):
                await medicine_registry.create_medical_session("test", "PATIENT_3")

        finally:
            medicine_registry.max_concurrent_sessions = original_limit

    def test_generate_session_id(self, medicine_registry):
        """Test generación de IDs únicos de sesión"""
        session_id1 = medicine_registry._generate_session_id()
        session_id2 = medicine_registry._generate_session_id()

        assert session_id1 != session_id2
        assert session_id1.startswith("med_session_")
        assert session_id2.startswith("med_session_")

    def test_generate_stream_id(self, medicine_registry):
        """Test generación de IDs únicos de stream"""
        stream_id1 = medicine_registry._generate_stream_id()
        stream_id2 = medicine_registry._generate_stream_id()

        assert stream_id1 != stream_id2
        assert stream_id1.startswith("rt_stream_")
        assert stream_id2.startswith("rt_stream_")


class TestMedicalSession:
    """Test suite para MedicalSession"""

    @pytest.fixture
    def medical_session(self):
        """Fixture para MedicalSession"""
        return MedicalSession(
            session_id="test_session_001",
            patient_id="TEST_PATIENT",
            session_type="imaging",
            expires_at=datetime.now() + timedelta(hours=24)
        )

    def test_session_initialization(self, medical_session):
        """Test inicialización de sesión médica"""
        assert medical_session.session_id == "test_session_001"
        assert medical_session.patient_id == "TEST_PATIENT"
        assert medical_session.session_type == "imaging"
        assert medical_session.status == SessionStatus.ACTIVE
        assert not medical_session.is_expired()

    def test_extend_session(self, medical_session):
        """Test extensión de sesión"""
        original_expiry = medical_session.expires_at
        medical_session.extend_session(hours=48)

        assert medical_session.expires_at > original_expiry
        assert medical_session.last_activity > original_expiry

    def test_add_analysis(self, medical_session):
        """Test adición de análisis a sesión"""
        analysis_id = "analysis_test_001"
        analysis_type = "segmentation"
        parameters = {"modality": "CT", "region": "liver"}

        medical_session.add_analysis(analysis_id, analysis_type, parameters)

        assert analysis_id in medical_session.active_analyses
        assert analysis_id in medical_session.results_cache
        assert medical_session.results_cache[analysis_id]["type"] == analysis_type
        assert medical_session.results_cache[analysis_id]["status"] == "running"

    def test_complete_analysis(self, medical_session):
        """Test completar análisis en sesión"""
        analysis_id = "analysis_complete_test"
        medical_session.add_analysis(analysis_id, "classification", {})

        results = {"prediction": "benign", "confidence": 0.92}
        medical_session.complete_analysis(analysis_id, results)

        assert medical_session.results_cache[analysis_id]["status"] == "completed"
        assert medical_session.results_cache[analysis_id]["results"] == results
        assert "completed_at" in medical_session.results_cache[analysis_id]


class TestRealTimeStream:
    """Test suite para RealTimeStream"""

    @pytest.fixture
    def real_time_stream(self):
        """Fixture para RealTimeStream"""
        return RealTimeStream(
            stream_id="stream_test_001",
            source="test_device",
            data_type="vital_signs",
            session_id="session_001"
        )

    def test_stream_initialization(self, real_time_stream):
        """Test inicialización de stream"""
        assert real_time_stream.stream_id == "stream_test_001"
        assert real_time_stream.source == "test_device"
        assert real_time_stream.data_type == "vital_signs"
        assert real_time_stream.session_id == "session_001"
        assert real_time_stream.is_active is True
        assert real_time_stream.data_points_received == 0

    def test_update_activity(self, real_time_stream):
        """Test actualización de actividad del stream"""
        original_points = real_time_stream.data_points_received
        original_timestamp = real_time_stream.last_data_timestamp

        real_time_stream.update_activity()

        assert real_time_stream.data_points_received == original_points + 1
        assert real_time_stream.last_data_timestamp > original_timestamp


class TestMedicalCapabilityType:
    """Test suite para MedicalCapabilityType enum"""

    def test_capability_types(self):
        """Test tipos de capability médica"""
        assert MedicalCapabilityType.MEDICAL_IMAGING.value == "medical_imaging"
        assert MedicalCapabilityType.GENOMIC_ANALYSIS.value == "genomic_analysis"
        assert MedicalCapabilityType.PHARMACOGENOMICS.value == "pharmacogenomics"
        assert MedicalCapabilityType.CLINICAL_DECISION_SUPPORT.value == "clinical_decision_support"
        assert MedicalCapabilityType.BIOMECHANICAL_MODELING.value == "biomechanical_modeling"

    def test_all_capabilities_unique(self):
        """Test que todos los capabilities sean únicos"""
        values = [cap.value for cap in MedicalCapabilityType]
        assert len(values) == len(set(values))


class TestGlobalRegistryFunctions:
    """Test suite para funciones globales del registry"""

    @pytest.mark.asyncio
    async def test_get_medicine_registry_singleton(self):
        """Test que get_medicine_registry retorne singleton"""
        registry1 = await get_medicine_registry()
        registry2 = await get_medicine_registry()

        assert registry1 is registry2
        assert isinstance(registry1, MedicineRegistry)

    @pytest.mark.asyncio
    async def test_create_medical_session_convenience(self):
        """Test función de conveniencia para crear sesión"""
        from app.domains.medicine.registry import create_medical_session

        session = await create_medical_session(
            session_type="test_session",
            patient_id="CONVENIENCE_TEST"
        )

        assert isinstance(session, MedicalSession)
        assert session.session_type == "test_session"
        assert session.patient_id == "CONVENIENCE_TEST"

    @pytest.mark.asyncio
    async def test_discover_medical_services_convenience(self):
        """Test función de conveniencia para descubrir servicios"""
        from app.domains.medicine.registry import discover_medical_services

        services = await discover_medical_services(
            capability=MedicalCapabilityType.MEDICAL_IMAGING
        )

        assert isinstance(services, list)
        for service in services:
            assert isinstance(service, ServiceMetadata)


class TestRegistryPersistence:
    """Test suite para persistencia del registry"""

    @pytest.mark.asyncio
    async def test_save_and_load_state(self, tmp_path):
        """Test guardar y cargar estado del registry"""
        # Crear registry con path temporal
        registry = MedicineRegistry()
        registry.persistence_path = tmp_path / "test_registry_state.json"

        # Crear sesión para tener datos que persistir
        await registry.initialize()
        await registry.create_medical_session("test", "PERSIST_TEST")

        # Guardar estado
        await registry._save_state()

        # Verificar que el archivo fue creado
        assert registry.persistence_path.exists()

        # Cargar estado (simplificado en este test)
        await registry._load_state()


# Configuración de pytest
@pytest.mark.asyncio
async def test_full_integration_workflow():
    """Test de integración completa del workflow médico"""
    # Crear registry
    registry = MedicineRegistry()
    await registry.initialize()

    # 1. Crear sesión médica
    session = await registry.create_medical_session(
        session_type="comprehensive_analysis",
        patient_id="INTEGRATION_TEST_001",
        clinical_context={
            "diagnosis": "suspected_cancer",
            "modalities": ["CT", "MRI", "genomics"]
        }
    )

    # 2. Crear stream de monitoreo
    stream = await registry.create_real_time_stream(
        source="monitoring_system",
        data_type="vital_signs",
        session_id=session.session_id,
        auto_analysis=True
    )

    # 3. Procesar datos en tiempo real
    vital_data = {"heart_rate": 72, "blood_pressure": "120/80", "temperature": 36.5}
    processing_result = await registry.process_real_time_data(
        stream_id=stream.stream_id,
        data=vital_data
    )

    # 4. Simular análisis de imagen
    session.add_analysis("imaging_001", "tumor_detection", {"modality": "CT"})
    imaging_results = {"tumors_detected": 1, "largest_diameter_mm": 15.2, "confidence": 0.94}
    session.complete_analysis("imaging_001", imaging_results)

    # 5. Validar resultados clínicos
    validation = await registry.validate_clinical_result(
        imaging_results, validation_type="diagnostic_confidence"
    )

    # 6. Obtener estado final
    final_status = await registry.get_session_status(session.session_id)
    registry_stats = await registry.get_medical_registry_stats()

    # Verificaciones
    assert session.status == SessionStatus.ACTIVE
    assert stream.is_active
    assert processing_result["status"] == "processed"
    assert validation["passed"] is True
    assert final_status["completed_analyses"] == 1
    assert registry_stats["active_sessions"] >= 1

    print("✅ Integration test completed successfully!")


if __name__ == "__main__":
    # Ejecutar tests específicos
    pytest.main([__file__, "-v", "--tb=short"])
