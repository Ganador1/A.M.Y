"""
Medicine Registry - Sistema de registro y gestión de servicios médicos
====================================================================

Registry especializado para el dominio Medicine con capabilities médicas específicas,
session management para análisis clínicos continuos, y real-time processing.

Basado en la arquitectura ServiceRegistry de AXIOM con extensiones médicas.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import aiofiles

from app.infrastructure.service_registry_discovery import (
    ServiceRegistry, ServiceMetadata, ServiceCapability,
    CapabilityType, ServiceStatus, create_service_registry
)

logger = logging.getLogger(__name__)


class MedicalCapabilityType(Enum):
    """Tipos de capabilities específicas del dominio médico"""
    MEDICAL_IMAGING = "medical_imaging"
    GENOMIC_ANALYSIS = "genomic_analysis"
    PHARMACOGENOMICS = "pharmacogenomics"
    CLINICAL_DECISION_SUPPORT = "clinical_decision_support"
    BIOMECHANICAL_MODELING = "biomechanical_modeling"
    DIAGNOSTIC_ASSISTANCE = "diagnostic_assistance"
    THERAPEUTIC_PLANNING = "therapeutic_planning"
    REAL_TIME_MONITORING = "real_time_monitoring"
    MULTI_MODAL_ANALYSIS = "multi_modal_analysis"
    CLINICAL_VALIDATION = "clinical_validation"


class SessionStatus(Enum):
    """Estados de sesión médica"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class MedicalSession:
    """Sesión médica para análisis continuos"""
    session_id: str
    patient_id: Optional[str] = None
    session_type: str = "general"  # imaging, genomics, personalized, etc.
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Contexto médico
    clinical_context: Dict[str, Any] = field(default_factory=dict)
    active_analyses: List[str] = field(default_factory=list)
    results_cache: Dict[str, Any] = field(default_factory=dict)

    # Configuración de sesión
    real_time_enabled: bool = False
    auto_validation: bool = True
    session_metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Verifica si la sesión ha expirado"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def extend_session(self, hours: int = 24):
        """Extiende la duración de la sesión"""
        self.expires_at = datetime.now() + timedelta(hours=hours)
        self.last_activity = datetime.now()

    def add_analysis(self, analysis_id: str, analysis_type: str, parameters: Dict[str, Any]):
        """Añade un análisis a la sesión"""
        self.active_analyses.append(analysis_id)
        self.results_cache[analysis_id] = {
            'type': analysis_type,
            'parameters': parameters,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }
        self.last_activity = datetime.now()

    def complete_analysis(self, analysis_id: str, results: Dict[str, Any]):
        """Marca un análisis como completado y guarda resultados"""
        if analysis_id in self.results_cache:
            self.results_cache[analysis_id].update({
                'results': results,
                'completed_at': datetime.now().isoformat(),
                'status': 'completed'
            })
        self.last_activity = datetime.now()


@dataclass
class RealTimeStream:
    """Stream de datos médicos en tiempo real"""
    stream_id: str
    source: str  # 'medical_device', 'imaging_scanner', 'genomic_sequencer', etc.
    data_type: str  # 'ecg', 'mri_slice', 'dna_sequence', etc.
    session_id: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    # Configuración del stream
    sampling_rate: float = 1.0  # Hz
    buffer_size: int = 1000
    auto_analysis: bool = False

    # Estado del stream
    data_points_received: int = 0
    last_data_timestamp: Optional[datetime] = None
    stream_metadata: Dict[str, Any] = field(default_factory=dict)

    def update_activity(self):
        """Actualiza la actividad del stream"""
        self.last_data_timestamp = datetime.now()
        self.data_points_received += 1


class MedicineRegistry:
    """
    Registry especializado del dominio Medicine

    Extiende ServiceRegistry con:
    - Medical session managemen
    - Real-time medical data processing
    - Clinical validation workflows
    - Medical capability discovery
    """

    def __init__(self, base_registry: Optional[ServiceRegistry] = None):
        self.base_registry = base_registry
        self._medical_services: Dict[str, ServiceMetadata] = {}
        self._medical_sessions: Dict[str, MedicalSession] = {}
        self._real_time_streams: Dict[str, RealTimeStream] = {}

        # Índices médicos especializados
        self._capability_index: Dict[str, Set[str]] = {
            cap.value: set() for cap in MedicalCapabilityType
        }
        self._patient_sessions: Dict[str, List[str]] = {}  # patient_id -> session_ids
        self._active_streams: Dict[str, List[str]] = {}    # session_id -> stream_ids

        # Configuración médica
        self.default_session_duration_hours = 24
        self.max_concurrent_sessions = 100
        self.real_time_buffer_size = 10000
        self.validation_thresholds = {
            'clinical_accuracy': 0.95,
            'diagnostic_confidence': 0.85,
            'imaging_quality': 0.90
        }

        # Path para persistencia
        self.persistence_path = Path("data/medicine_registry_state.json")
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("MedicineRegistry initialized")

    async def initialize(self):
        """Inicialización asíncrona del registry"""
        if self.base_registry is None:
            self.base_registry = await create_service_registry()

        # Cargar estado persistido
        await self._load_state()

        # Auto-registrar servicios médicos
        await self._auto_register_medical_services()

        # Iniciar limpieza de sesiones expiradas
        asyncio.create_task(self._cleanup_expired_sessions())

        logger.info("MedicineRegistry fully initialized")

    async def register_medical_service(self, service_metadata: ServiceMetadata) -> bool:
        """Registra un servicio médico"""
        try:
            # Registrar en base registry
            if self.base_registry:
                await self.base_registry.register_service(service_metadata)

            # Registrar localmente
            self._medical_services[service_metadata.service_id] = service_metadata

            # Actualizar índices médicos
            for capability in service_metadata.capabilities:
                if hasattr(MedicalCapabilityType, capability.type.name):
                    cap_type = MedicalCapabilityType(capability.type.value)
                    self._capability_index[cap_type.value].add(service_metadata.service_id)

            await self._save_state()

            logger.info("Medical service registered: %s", service_metadata.service_id)
            return True

        except (OSError, ValueError, RuntimeError) as e:
            logger.error("Failed to register medical service %s: %s", service_metadata.service_id, e)
            return False

    async def create_medical_session(self,
                                   session_type: str,
                                   patient_id: Optional[str] = None,
                                   clinical_context: Optional[Dict[str, Any]] = None,
                                   duration_hours: Optional[int] = None) -> MedicalSession:
        """Crea una nueva sesión médica"""

        # Verificar límite de sesiones concurrentes
        active_sessions = [s for s in self._medical_sessions.values()
                          if s.status == SessionStatus.ACTIVE]
        if len(active_sessions) >= self.max_concurrent_sessions:
            raise RuntimeError(f"Maximum concurrent sessions ({self.max_concurrent_sessions}) reached")

        # Crear sesión
        session_id = self._generate_session_id()
        duration = duration_hours or self.default_session_duration_hours

        session = MedicalSession(
            session_id=session_id,
            patient_id=patient_id,
            session_type=session_type,
            clinical_context=clinical_context or {},
            expires_at=datetime.now() + timedelta(hours=duration)
        )

        # Registrar sesión
        self._medical_sessions[session_id] = session

        # Indexar por paciente si corresponde
        if patient_id:
            if patient_id not in self._patient_sessions:
                self._patient_sessions[patient_id] = []
            self._patient_sessions[patient_id].append(session_id)

        await self._save_state()

        logger.info("Medical session created: %s for patient %s", session_id, patient_id)
        return session

    async def create_real_time_stream(self,
                                    source: str,
                                    data_type: str,
                                    session_id: Optional[str] = None,
                                    auto_analysis: bool = False) -> RealTimeStream:
        """Crea un stream de datos médicos en tiempo real"""

        stream_id = self._generate_stream_id()

        stream = RealTimeStream(
            stream_id=stream_id,
            source=source,
            data_type=data_type,
            session_id=session_id,
            auto_analysis=auto_analysis,
            buffer_size=self.real_time_buffer_size
        )

        # Registrar stream
        self._real_time_streams[stream_id] = stream

        # Asociar con sesión si corresponde
        if session_id and session_id in self._medical_sessions:
            if session_id not in self._active_streams:
                self._active_streams[session_id] = []
            self._active_streams[session_id].append(stream_id)

            # Habilitar real-time en la sesión
            self._medical_sessions[session_id].real_time_enabled = True

        logger.info("Real-time stream created: %s from %s", stream_id, source)
        return stream

    async def discover_medical_services(self,
                                      capability: MedicalCapabilityType,
                                      tags: Optional[List[str]] = None,
                                      patient_context: Optional[Dict[str, Any]] = None) -> List[ServiceMetadata]:
        """Descubre servicios médicos por capability"""

        matching_services = []

        # Buscar por capability médica
        service_ids = self._capability_index.get(capability.value, set())

        for service_id in service_ids:
            if service_id in self._medical_services:
                service = self._medical_services[service_id]

                # Filtrar por tags si se especifican
                if tags and not any(tag in service.tags for tag in tags):
                    continue

                # Validar contexto del paciente si es necesario
                if patient_context and not self._validate_patient_context(service, patient_context):
                    continue

                matching_services.append(service)

        logger.info("Found %d services for capability %s", len(matching_services), capability.value)
        return matching_services

    async def process_real_time_data(self,
                                   stream_id: str,
                                   data: Any,
                                   timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Procesa datos médicos en tiempo real"""

        if stream_id not in self._real_time_streams:
            raise ValueError(f"Stream {stream_id} not found")

        stream = self._real_time_streams[stream_id]

        if not stream.is_active:
            raise ValueError(f"Stream {stream_id} is not active")

        # Actualizar actividad del stream
        stream.update_activity()

        # Procesar datos según el tipo
        processing_result = await self._process_stream_data(stream, data, timestamp)

        # Auto-análisis si está habilitado
        if stream.auto_analysis and stream.session_id:
            analysis_result = await self._trigger_auto_analysis(stream, data, processing_result)
            processing_result['auto_analysis'] = analysis_result

        return processing_result

    async def validate_clinical_result(self,
                                     result: Dict[str, Any],
                                     validation_type: str = "accuracy") -> Dict[str, Any]:
        """Valida resultado clínico contra thresholds"""

        validation_result = {
            'validation_type': validation_type,
            'timestamp': datetime.now().isoformat(),
            'passed': False,
            'metrics': {},
            'recommendations': []
        }

        threshold = self.validation_thresholds.get(validation_type, 0.85)

        # Extraer métricas relevantes del resultado
        if validation_type == "clinical_accuracy":
            accuracy = result.get('accuracy', result.get('clinical_accuracy_score', 0.0))
            validation_result['metrics']['accuracy'] = accuracy
            validation_result['passed'] = accuracy >= threshold

            if not validation_result['passed']:
                validation_result['recommendations'].append(
                    f"Clinical accuracy {accuracy:.3f} below threshold {threshold:.3f}"
                )

        elif validation_type == "diagnostic_confidence":
            confidence = result.get('confidence', result.get('diagnostic_confidence', 0.0))
            validation_result['metrics']['confidence'] = confidence
            validation_result['passed'] = confidence >= threshold

            if not validation_result['passed']:
                validation_result['recommendations'].append(
                    "Consider additional tests or expert consultation"
                )

        elif validation_type == "imaging_quality":
            quality_metrics = result.get('quality', {})
            if isinstance(quality_metrics, dict):
                snr = quality_metrics.get('snr', 0.0)
                cnr = quality_metrics.get('cnr', 0.0)
                overall_quality = (snr + cnr) / 2.0
            else:
                overall_quality = float(quality_metrics) if quality_metrics else 0.0

            validation_result['metrics']['overall_quality'] = overall_quality
            validation_result['passed'] = overall_quality >= threshold

        return validation_result

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Obtiene estado completo de una sesión médica"""

        if session_id not in self._medical_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._medical_sessions[session_id]

        # Verificar expiración
        if session.is_expired() and session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.COMPLETED
            await self._save_state()

        # Obtener streams activos
        active_streams = []
        if session_id in self._active_streams:
            for stream_id in self._active_streams[session_id]:
                if stream_id in self._real_time_streams:
                    stream = self._real_time_streams[stream_id]
                    active_streams.append({
                        'stream_id': stream_id,
                        'source': stream.source,
                        'data_type': stream.data_type,
                        'data_points': stream.data_points_received,
                        'is_active': stream.is_active
                    })

        return {
            'session_id': session_id,
            'patient_id': session.patient_id,
            'status': session.status.value,
            'session_type': session.session_type,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expires_at': session.expires_at.isoformat() if session.expires_at else None,
            'active_analyses': len(session.active_analyses),
            'completed_analyses': len([r for r in session.results_cache.values()
                                     if r.get('status') == 'completed']),
            'active_streams': active_streams,
            'real_time_enabled': session.real_time_enabled
        }

    async def get_medical_registry_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del registry médico"""

        active_sessions = [s for s in self._medical_sessions.values()
                          if s.status == SessionStatus.ACTIVE]
        active_streams = [s for s in self._real_time_streams.values() if s.is_active]

        capability_stats = {}
        for cap_type, service_ids in self._capability_index.items():
            capability_stats[cap_type] = len(service_ids)

        return {
            'total_medical_services': len(self._medical_services),
            'active_sessions': len(active_sessions),
            'total_sessions': len(self._medical_sessions),
            'active_streams': len(active_streams),
            'total_streams': len(self._real_time_streams),
            'patients_with_sessions': len(self._patient_sessions),
            'capability_distribution': capability_stats,
            'validation_thresholds': self.validation_thresholds,
            'registry_health': 'healthy' if len(active_sessions) < self.max_concurrent_sessions else 'at_capacity'
        }

    def _generate_session_id(self) -> str:
        """Genera ID único para sesión médica"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"med_session_{timestamp}_{random_suffix}"

    def _generate_stream_id(self) -> str:
        """Genera ID único para stream de datos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"rt_stream_{timestamp}_{random_suffix}"

    def _validate_patient_context(self, service: ServiceMetadata, context: Dict[str, Any]) -> bool:
        """Valida contexto del paciente para un servicio"""
        # Implementar validaciones específicas según el servicio
        # Por ejemplo, verificar edad para servicios pediátricos, etc.
        # Por ahora retorna True (placeholder para implementación futura)
        return True

    async def _process_stream_data(self, stream: RealTimeStream, data: Any, timestamp: Optional[datetime]) -> Dict[str, Any]:
        """Procesa datos de stream en tiempo real"""
        processing_timestamp = timestamp or datetime.now()

        # Procesamiento básico según tipo de datos
        if stream.data_type == 'ecg':
            return await self._process_ecg_data(data, processing_timestamp)
        elif stream.data_type == 'mri_slice':
            return await self._process_mri_slice(data, processing_timestamp)
        elif stream.data_type == 'dna_sequence':
            return await self._process_dna_sequence(data, processing_timestamp)
        else:
            return {
                'processed_at': processing_timestamp.isoformat(),
                'data_type': stream.data_type,
                'status': 'processed',
                'metadata': {'raw_data_size': len(str(data))}
            }

    async def _process_ecg_data(self, data: Any, timestamp: datetime) -> Dict[str, Any]:
        """Procesa datos ECG en tiempo real"""
        # Simulación de procesamiento ECG
        return {
            'processed_at': timestamp.isoformat(),
            'data_type': 'ecg',
            'heart_rate': 72,  # Simulado
            'rhythm': 'normal_sinus',
            'anomalies_detected': [],
            'quality_score': 0.95
        }

    async def _process_mri_slice(self, data: Any, timestamp: datetime) -> Dict[str, Any]:
        """Procesa slice de MRI en tiempo real"""
        return {
            'processed_at': timestamp.isoformat(),
            'data_type': 'mri_slice',
            'slice_quality': 0.92,
            'contrast_score': 0.88,
            'artifacts_detected': False
        }

    async def _process_dna_sequence(self, data: Any, timestamp: datetime) -> Dict[str, Any]:
        """Procesa secuencia de DNA en tiempo real"""
        return {
            'processed_at': timestamp.isoformat(),
            'data_type': 'dna_sequence',
            'sequence_length': len(str(data)),
            'quality_score': 0.94,
            'variants_detected': 0
        }

    async def _trigger_auto_analysis(self, stream: RealTimeStream, data: Any, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger análisis automático basado en datos de stream"""
        # Implementar lógica de auto-análisis
        return {
            'auto_analysis_triggered': True,
            'analysis_type': f"{stream.data_type}_analysis",
            'triggered_at': datetime.now().isoformat()
        }

    async def _auto_register_medical_services(self):
        """Auto-registro de servicios médicos conocidos"""
        medical_services = [
            {
                'service_id': 'advanced_medical_imaging',
                'name': 'Advanced Medical Imaging Service',
                'capabilities': [MedicalCapabilityType.MEDICAL_IMAGING, MedicalCapabilityType.CLINICAL_VALIDATION],
                'tags': ['imaging', 'dicom', 'nifti', 'segmentation']
            },
            {
                'service_id': 'genomics_analysis',
                'name': 'Advanced Genomics Service',
                'capabilities': [MedicalCapabilityType.GENOMIC_ANALYSIS, MedicalCapabilityType.PHARMACOGENOMICS],
                'tags': ['genomics', 'variants', 'cancer', 'deepvariant']
            },
            {
                'service_id': 'personalized_medicine',
                'name': 'Personalized Medicine Service',
                'capabilities': [MedicalCapabilityType.PHARMACOGENOMICS, MedicalCapabilityType.THERAPEUTIC_PLANNING],
                'tags': ['personalized', 'pgx', 'drugs', 'precision']
            },
            {
                'service_id': 'biomechanics_modeling',
                'name': 'Biomechanics Service',
                'capabilities': [MedicalCapabilityType.BIOMECHANICAL_MODELING],
                'tags': ['biomechanics', 'movement', 'musculoskeletal']
            }
        ]

        for service_config in medical_services:
            # Crear capabilities
            capabilities = []
            for cap_type in service_config['capabilities']:
                capability = ServiceCapability(
                    name=f"{cap_type.value}_capability",
                    type=CapabilityType.COMPUTATIONAL,  # Usar tipo computacional genérico
                    description=f"Medical capability: {cap_type.value}",
                    input_schema={},
                    output_schema={}
                )
                capabilities.append(capability)

            # Crear metadata del servicio
            service_metadata = ServiceMetadata(
                service_id=service_config['service_id'],
                name=service_config['name'],
                version="1.0.0",
                description=f"Medical service: {service_config['name']}",
                endpoint=None,  # Se configurará cuando se registre el endpoint real
                capabilities=capabilities,
                tags=service_config['tags'],
                health_status=ServiceStatus.HEALTHY
            )

            await self.register_medical_service(service_metadata)

    async def _cleanup_expired_sessions(self):
        """Limpieza periódica de sesiones expiradas"""
        while True:
            try:
                expired_sessions = []

                for session_id, session in self._medical_sessions.items():
                    if session.is_expired() and session.status == SessionStatus.ACTIVE:
                        session.status = SessionStatus.COMPLETED
                        expired_sessions.append(session_id)

                if expired_sessions:
                    logger.info("Cleaned up %d expired sessions", len(expired_sessions))
                    await self._save_state()

                # Esperar 1 hora antes de la siguiente limpieza
                await asyncio.sleep(3600)

            except (OSError, ValueError, RuntimeError) as e:
                logger.error("Error during session cleanup: %s", e)
                await asyncio.sleep(600)  # Esperar 10 minutos en caso de error

    async def _save_state(self):
        """Guarda estado del registry a disco"""
        try:
            state = {
                'medical_services': {
                    service_id: {
                        'service_id': service.service_id,
                        'name': service.name,
                        'version': service.version,
                        'description': service.description,
                        'tags': service.tags,
                        'health_status': service.health_status.value
                    }
                    for service_id, service in self._medical_services.items()
                },
                'medical_sessions': {
                    session_id: {
                        'session_id': session.session_id,
                        'patient_id': session.patient_id,
                        'session_type': session.session_type,
                        'status': session.status.value,
                        'created_at': session.created_at.isoformat(),
                        'expires_at': session.expires_at.isoformat() if session.expires_at else None,
                        'clinical_context': session.clinical_context,
                        'real_time_enabled': session.real_time_enabled
                    }
                    for session_id, session in self._medical_sessions.items()
                },
                'real_time_streams': {
                    stream_id: {
                        'stream_id': stream.stream_id,
                        'source': stream.source,
                        'data_type': stream.data_type,
                        'session_id': stream.session_id,
                        'is_active': stream.is_active,
                        'data_points_received': stream.data_points_received
                    }
                    for stream_id, stream in self._real_time_streams.items()
                },
                'saved_at': datetime.now().isoformat()
            }

            with aiofiles.open(self.persistence_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

        except (OSError, ValueError, TypeError) as e:
            logger.error("Failed to save registry state: %s", e)

    async def _load_state(self):
        """Carga estado del registry desde disco"""
        try:
            if not self.persistence_path.exists():
                logger.info("No previous medicine registry state found")
                return

            with aiofiles.aiofiles.open(self.persistence_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Restaurar sesiones (simplificado para este ejemplo)
            sessions_data = state.get('medical_sessions', {})
            for session_id, _ in sessions_data.items():
                # Reconstruir sesión básica (sin toda la funcionalidad por simplicidad)
                logger.info("Loaded session: %s", session_id)

            logger.info("Loaded medicine registry state with %d sessions", len(sessions_data))

        except (OSError, ValueError, TypeError) as e:
            logger.error("Failed to load registry state: %s", e)


# Instancia global del registry médico
medicine_registry: Optional[MedicineRegistry] = None


async def get_medicine_registry() -> MedicineRegistry:
    """Factory function para obtener instancia del registry médico"""
    global medicine_registry

    if medicine_registry is None:
        medicine_registry = MedicineRegistry()
        await medicine_registry.initialize()

    return medicine_registry


# Funciones de conveniencia para uso directo
async def create_medical_session(session_type: str, patient_id: Optional[str] = None, **kwargs) -> MedicalSession:
    """Crea sesión médica usando el registry global"""
    registry = await get_medicine_registry()
    return await registry.create_medical_session(session_type, patient_id, **kwargs)


async def discover_medical_services(capability: MedicalCapabilityType, **kwargs) -> List[ServiceMetadata]:
    """Descubre servicios médicos usando el registry global"""
    registry = await get_medicine_registry()
    return await registry.discover_medical_services(capability, **kwargs)


async def process_real_time_medical_data(stream_id: str, data: Any, **kwargs) -> Dict[str, Any]:
    """Procesa datos médicos en tiempo real usando el registry global"""
    registry = await get_medicine_registry()
    return await registry.process_real_time_data(stream_id, data, **kwargs)
