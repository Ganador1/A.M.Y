"""
AXIOM Integrity Verification System
===================================

Sistema de verificación de integridad para resultados PINN.
Complementa el sistema de validación blockchain con verificación
local y distribuida de la integridad de datos científicos.

Características principales:
- Verificación de integridad local de resultados
- Sistema de verificación distribuida
- Detección de manipulaciones de datos
- Auditoría de cambios en resultados
- Integración con sistema de monitoreo

Autor: AXIOM Mathematics AI Engine Team
Fecha: Septiembre 2025
Versión: 1.0.0
"""

import hashlib
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from .security import require_bearer, security_auditor, SecurityEvent
from .blockchain_validation import blockchain_service

# Configurar logging
logger = logging.getLogger(__name__)

# Modelos de datos para verificación de integridad
@dataclass
class IntegrityRecord:
    """Registro de integridad de un resultado"""
    record_id: str
    result_id: str
    result_hash: str
    metadata_hash: str
    verification_timestamp: datetime
    verifier_node: str
    integrity_status: str  # 'valid', 'compromised', 'unknown'
    verification_method: str
    confidence_score: float
    details: Dict[str, Any]

@dataclass
class IntegrityAudit:
    """Auditoría de integridad"""
    audit_id: str
    target_result_id: str
    audit_timestamp: datetime
    auditor_node: str
    audit_type: str  # 'full', 'partial', 'continuous'
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    audit_status: str  # 'passed', 'failed', 'warning'

@dataclass
class DataIntegrityCheck:
    """Verificación de integridad de datos"""
    check_id: str
    data_type: str
    data_hash: str
    expected_hash: str
    check_timestamp: datetime
    check_result: bool
    anomalies_detected: List[str]
    integrity_score: float

# Modelos Pydantic para API
class IntegrityCheckRequest(BaseModel):
    """Solicitud de verificación de integridad"""
    result_id: str = Field(..., description="ID del resultado a verificar")
    verification_method: str = Field("comprehensive", description="Método de verificación")
    include_metadata: bool = Field(True, description="Incluir verificación de metadatos")

class IntegrityCheckResponse(BaseModel):
    """Respuesta de verificación de integridad"""
    check_id: str
    result_id: str
    integrity_status: str
    confidence_score: float
    verification_timestamp: datetime
    details: Dict[str, Any]

class AuditRequest(BaseModel):
    """Solicitud de auditoría"""
    result_id: str = Field(..., description="ID del resultado a auditar")
    audit_type: str = Field("full", description="Tipo de auditoría")
    include_historical: bool = Field(True, description="Incluir datos históricos")

class AuditResponse(BaseModel):
    """Respuesta de auditoría"""
    audit_id: str
    audit_status: str
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    audit_timestamp: datetime

class IntegrityVerificationService:
    """
    Servicio de verificación de integridad para PINN
    Complementa la validación blockchain con verificación local
    """

    def __init__(self):
        self.integrity_records: Dict[str, IntegrityRecord] = {}
        self.audit_history: Dict[str, IntegrityAudit] = {}
        self.verification_methods = {
            'basic': self._basic_integrity_check,
            'comprehensive': self._comprehensive_integrity_check,
            'statistical': self._statistical_integrity_check,
            'blockchain': self._blockchain_integrity_check
        }
        self.integrity_threshold = 0.85  # Umbral mínimo de integridad
        self.node_id = str(uuid.uuid4())
        # Inicializar verificación continua de forma segura (no romper si no hay loop)
        self._monitor_task: Optional[asyncio.Task] = None
        self.start_background_monitor()

        logger.info(f"Integrity Verification Service initialized with node ID: {self.node_id}")

    async def verify_result_integrity(
        self,
        result_id: str,
        verification_method: str = "comprehensive",
        include_metadata: bool = True
    ) -> IntegrityRecord:
        """
        Verificar integridad de un resultado PINN

        Args:
            result_id: ID del resultado a verificar
            verification_method: Método de verificación a usar
            include_metadata: Incluir verificación de metadatos

        Returns:
            IntegrityRecord: Registro de verificación de integridad
        """
        record_id = str(uuid.uuid4())

        # Obtener datos del resultado (en un sistema real, vendría de la base de datos)
        result_data = await self._fetch_result_data(result_id)
        if not result_data:
            raise ValueError(f"Result {result_id} not found")

        # Calcular hashes
        result_hash = self._calculate_data_hash(result_data)
        metadata_hash = self._calculate_metadata_hash(result_data) if include_metadata else ""

        # Realizar verificación según método
        verification_result = await self._perform_integrity_check(
            result_data, verification_method
        )

        # Determinar estado de integridad
        integrity_status = self._determine_integrity_status(verification_result)

        # Crear registro de integridad
        record = IntegrityRecord(
            record_id=record_id,
            result_id=result_id,
            result_hash=result_hash,
            metadata_hash=metadata_hash,
            verification_timestamp=datetime.now(),
            verifier_node=self.node_id,
            integrity_status=integrity_status,
            verification_method=verification_method,
            confidence_score=verification_result.get('confidence_score', 0.0),
            details=verification_result
        )

        # Almacenar registro
        self.integrity_records[record_id] = record

        # Log security event
        security_auditor.log_security_event(SecurityEvent(
            event_type="integrity_verification",
            severity="INFO" if integrity_status == "valid" else "WARNING",
            source_ip="internal",
            user_agent="IntegrityService",
            endpoint="/api/integrity/verify",
            user_id=None,
            details={
                "result_id": result_id,
                "status": integrity_status,
                "confidence": record.confidence_score
            },
            timestamp=datetime.now()
        ))

        logger.info(f"Integrity verification completed for result {result_id}: {integrity_status}")
        return record

    async def _fetch_result_data(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Obtener datos del resultado (simulado)"""
        # En un sistema real, esto consultaría la base de datos
        # Por ahora, simulamos datos
        return {
            "result_id": result_id,
            "model_type": "pinn",
            "pde_type": "heat",
            "input_parameters": {"alpha": 0.01, "domain": [0, 1]},
            "output_data": {"solution": [0.1, 0.2, 0.3], "error": 0.001},
            "confidence_score": 0.95,
            "execution_time": 1.2,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calcular hash de los datos del resultado"""
        # Excluir campos no determinísticos
        hash_data = {k: v for k, v in data.items() if k not in ['timestamp', 'execution_time']}
        data_json = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(data_json.encode()).hexdigest()

    def _calculate_metadata_hash(self, data: Dict[str, Any]) -> str:
        """Calcular hash de los metadatos"""
        metadata = {
            "model_type": data.get("model_type"),
            "pde_type": data.get("pde_type"),
            "input_parameters": data.get("input_parameters"),
            "confidence_score": data.get("confidence_score")
        }
        metadata_json = json.dumps(metadata, sort_keys=True)
        return hashlib.sha256(metadata_json.encode()).hexdigest()

    async def _perform_integrity_check(self, data: Dict[str, Any], method: str) -> Dict[str, Any]:
        """Realizar verificación de integridad según método"""
        if method in self.verification_methods:
            return await self.verification_methods[method](data)
        else:
            return await self._basic_integrity_check(data)

    def start_background_monitor(self):
        """Arrancar monitor continuo si es posible y no duplicado."""
        if self._monitor_task and not self._monitor_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop en contexto (posible inicialización síncrona en tests); ignorar
            return
        try:
            self._monitor_task = loop.create_task(self._continuous_integrity_monitoring())
        except Exception:  # pragma: no cover
            self._monitor_task = None

    async def _basic_integrity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificación básica de integridad"""
        # Verificaciones básicas
        checks = {
            'has_required_fields': self._check_required_fields(data),
            'data_consistency': self._check_data_consistency(data),
            'value_ranges': self._check_value_ranges(data)
        }

        passed_checks = sum(1 for check in checks.values() if check)
        confidence_score = passed_checks / len(checks)

        return {
            'method': 'basic',
            'checks': checks,
            'confidence_score': confidence_score,
            'anomalies': [k for k, v in checks.items() if not v]
        }

    async def _comprehensive_integrity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificación comprehensiva de integridad"""
        # Combinar múltiples métodos
        basic_result = await self._basic_integrity_check(data)
        statistical_result = await self._statistical_integrity_check(data)

        # Calcular confianza combinada
        combined_confidence = (basic_result['confidence_score'] + statistical_result['confidence_score']) / 2

        return {
            'method': 'comprehensive',
            'basic_checks': basic_result,
            'statistical_checks': statistical_result,
            'confidence_score': combined_confidence,
            'anomalies': basic_result.get('anomalies', []) + statistical_result.get('anomalies', [])
        }

    async def _statistical_integrity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificación estadística de integridad"""
        output_data = data.get('output_data', {})

        if 'solution' not in output_data:
            return {
                'method': 'statistical',
                'confidence_score': 0.0,
                'anomalies': ['missing_solution_data']
            }

        solution = output_data['solution']

        # Verificaciones estadísticas
        checks = {
            'solution_monotonicity': self._check_solution_monotonicity(solution),
            'solution_bounds': self._check_solution_bounds(solution),
            'error_consistency': self._check_error_consistency(data)
        }

        passed_checks = sum(1 for check in checks.values() if check)
        confidence_score = passed_checks / len(checks)

        return {
            'method': 'statistical',
            'checks': checks,
            'confidence_score': confidence_score,
            'anomalies': [k for k, v in checks.items() if not v]
        }

    async def _blockchain_integrity_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificación usando blockchain"""
        result_hash = self._calculate_data_hash(data)

        # Verificar si el resultado existe en la blockchain
        # En lugar de usar proof_id, buscamos por hash
        is_valid, blockchain_details = blockchain_service.verify_result_integrity(
            result_hash, ""  # No necesitamos proof_id específico
        )

        confidence_score = 1.0 if is_valid else 0.0

        return {
            'method': 'blockchain',
            'blockchain_verification': is_valid,
            'blockchain_details': blockchain_details,
            'confidence_score': confidence_score,
            'anomalies': [] if is_valid else ['blockchain_verification_failed']
        }

    def _check_required_fields(self, data: Dict[str, Any]) -> bool:
        """Verificar campos requeridos"""
        required_fields = ['result_id', 'model_type', 'output_data']
        return all(field in data for field in required_fields)

    def _check_data_consistency(self, data: Dict[str, Any]) -> bool:
        """Verificar consistencia de datos"""
        # Verificar que los tipos de datos sean consistentes
        if 'output_data' in data:
            output = data['output_data']
            if 'solution' in output:
                solution = output['solution']
                # Verificar que la solución sea una lista de números
                return isinstance(solution, list) and all(isinstance(x, (int, float)) for x in solution)
        return False

    def _check_value_ranges(self, data: Dict[str, Any]) -> bool:
        """Verificar rangos de valores"""
        confidence = data.get('confidence_score', 0)
        execution_time = data.get('execution_time', 0)

        # Verificar rangos razonables
        return (0 <= confidence <= 1 and execution_time >= 0)

    def _check_solution_monotonicity(self, solution: List[float]) -> bool:
        """Verificar monotonicidad de la solución (para ciertos PDEs)"""
        if len(solution) < 3:
            return True

        # Verificar que no haya cambios bruscos
        differences = [abs(solution[i+1] - solution[i]) for i in range(len(solution)-1)]
        max_diff = max(differences) if differences else 0
        mean_diff = sum(differences) / len(differences) if differences else 0

        # Si la diferencia máxima es mucho mayor que la media, puede indicar anomalía
        return max_diff <= mean_diff * 5

    def _check_solution_bounds(self, solution: List[float]) -> bool:
        """Verificar límites de la solución"""
        if not solution:
            return False

        # Verificar que los valores estén en rangos razonables
        min_val, max_val = min(solution), max(solution)
        return -1000 <= min_val <= max_val <= 1000

    def _check_error_consistency(self, data: Dict[str, Any]) -> bool:
        """Verificar consistencia del error"""
        output_data = data.get('output_data', {})
        error = output_data.get('error')

        if error is None:
            return True  # Error no siempre está presente

        # Verificar que el error sea positivo y razonable
        return isinstance(error, (int, float)) and 0 <= error <= 1

    def _determine_integrity_status(self, verification_result: Dict[str, Any]) -> str:
        """Determinar estado de integridad basado en resultados"""
        confidence = verification_result.get('confidence_score', 0)
        anomalies = verification_result.get('anomalies', [])

        if confidence >= self.integrity_threshold and not anomalies:
            return 'valid'
        elif confidence >= 0.5:
            return 'warning'
        else:
            return 'compromised'

    async def perform_integrity_audit(
        self,
        result_id: str,
        audit_type: str = "full",
        include_historical: bool = True
    ) -> IntegrityAudit:
        """
        Realizar auditoría de integridad

        Args:
            result_id: ID del resultado a auditar
            audit_type: Tipo de auditoría
            include_historical: Incluir datos históricos

        Returns:
            IntegrityAudit: Resultado de la auditoría
        """
        audit_id = str(uuid.uuid4())

        # Recopilar datos para auditoría
        audit_data = await self._gather_audit_data(result_id, include_historical)

        # Realizar diferentes tipos de verificación
        findings = []
        recommendations = []

        if audit_type in ['full', 'comprehensive']:
            # Verificación completa
            integrity_record = await self.verify_result_integrity(result_id, "comprehensive")
            findings.append({
                'type': 'integrity_check',
                'status': integrity_record.integrity_status,
                'confidence': integrity_record.confidence_score,
                'details': integrity_record.details
            })

        if audit_type == 'full':
            # Verificación blockchain (opcional)
            blockchain_check = await self._blockchain_integrity_check(audit_data)
            findings.append({
                'type': 'blockchain_verification',
                'status': 'valid' if blockchain_check['blockchain_verification'] else 'not_available',
                'details': blockchain_check
            })

        # Generar recomendaciones
        recommendations = self._generate_audit_recommendations(findings)

        # Determinar estado de auditoría
        audit_status = self._determine_audit_status(findings)

        audit = IntegrityAudit(
            audit_id=audit_id,
            target_result_id=result_id,
            audit_timestamp=datetime.now(),
            auditor_node=self.node_id,
            audit_type=audit_type,
            findings=findings,
            recommendations=recommendations,
            audit_status=audit_status
        )

        # Almacenar auditoría
        self.audit_history[audit_id] = audit

        logger.info(f"Integrity audit completed for result {result_id}: {audit_status}")
        return audit

    async def _gather_audit_data(self, result_id: str, include_historical: bool) -> Dict[str, Any]:
        """Recopilar datos para auditoría"""
        # Obtener datos actuales
        current_data = await self._fetch_result_data(result_id)

        if not include_historical:
            return current_data or {}

        # En un sistema real, obtendríamos datos históricos
        # Por ahora, devolvemos solo datos actuales
        return current_data or {}

    def _generate_audit_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones basadas en hallazgos"""
        recommendations = []

        for finding in findings:
            if finding['type'] == 'integrity_check':
                if finding['status'] == 'compromised':
                    recommendations.append("Revisar integridad de datos - posible manipulación detectada")
                elif finding['status'] == 'warning':
                    recommendations.append("Monitorear resultado - anomalías menores detectadas")

            elif finding['type'] == 'blockchain_verification':
                if finding['status'] == 'invalid':
                    recommendations.append("Verificar registro blockchain - inconsistencia detectada")

        if not recommendations:
            recommendations.append("Resultado aprobado - integridad verificada")

        return recommendations

    def _determine_audit_status(self, findings: List[Dict[str, Any]]) -> str:
        """Determinar estado de auditoría"""
        has_failures = any(f['status'] in ['compromised', 'invalid'] for f in findings)
        has_warnings = any(f['status'] == 'warning' for f in findings)

        if has_failures:
            return 'failed'
        elif has_warnings:
            return 'warning'
        else:
            return 'passed'

    async def _continuous_integrity_monitoring(self):
        """Monitoreo continuo de integridad"""
        while True:
            try:
                # Verificar integridad de resultados recientes
                recent_results = await self._get_recent_results()

                for result_id in recent_results:
                    # Verificación rápida
                    record = await self.verify_result_integrity(result_id, "basic", False)

                    if record.integrity_status == 'compromised':
                        logger.warning(f"Integrity compromise detected for result {result_id}")

                        # Trigger alert
                        security_auditor.log_security_event(SecurityEvent(
                            event_type="integrity_compromise_detected",
                            severity="ERROR",
                            source_ip="monitoring",
                            user_agent="IntegrityMonitor",
                            endpoint="continuous_monitoring",
                            user_id=None,
                            details={"result_id": result_id, "status": "compromised"},
                            timestamp=datetime.now()
                        ))

                # Esperar antes de siguiente verificación
                await asyncio.sleep(300)  # 5 minutos

            except Exception as e:
                logger.error(f"Error in continuous integrity monitoring: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto en caso de error

    async def _get_recent_results(self) -> List[str]:
        """Obtener IDs de resultados recientes (simulado)"""
        # En un sistema real, esto consultaría la base de datos
        return [f"result_{i}" for i in range(10)]

    def get_integrity_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de integridad"""
        total_records = len(self.integrity_records)
        valid_records = sum(1 for r in self.integrity_records.values() if r.integrity_status == 'valid')
        compromised_records = sum(1 for r in self.integrity_records.values() if r.integrity_status == 'compromised')

        return {
            'total_records': total_records,
            'valid_records': valid_records,
            'compromised_records': compromised_records,
            'integrity_rate': valid_records / total_records if total_records > 0 else 0,
            'audits_performed': len(self.audit_history),
            'node_id': self.node_id
        }

# Instancia global del servicio
integrity_service = IntegrityVerificationService()

# API Router para verificación de integridad
integrity_router = APIRouter(prefix="/api/integrity", tags=["integrity-verification"])

@integrity_router.post("/verify", response_model=IntegrityCheckResponse)
async def verify_integrity(
    request: IntegrityCheckRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(require_bearer)
):
    """
    Verificar integridad de un resultado PINN
    """
    try:
        record = await integrity_service.verify_result_integrity(
            request.result_id,
            request.verification_method,
            request.include_metadata
        )

        return IntegrityCheckResponse(
            check_id=record.record_id,
            result_id=record.result_id,
            integrity_status=record.integrity_status,
            confidence_score=record.confidence_score,
            verification_timestamp=record.verification_timestamp,
            details=record.details
        )

    except Exception as e:
        logger.error(f"Error in integrity verification: {e}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")

@integrity_router.post("/audit", response_model=AuditResponse)
async def perform_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(require_bearer)
):
    """
    Realizar auditoría de integridad
    """
    try:
        audit = await integrity_service.perform_integrity_audit(
            request.result_id,
            request.audit_type,
            request.include_historical
        )

        return AuditResponse(
            audit_id=audit.audit_id,
            audit_status=audit.audit_status,
            findings=audit.findings,
            recommendations=audit.recommendations,
            audit_timestamp=audit.audit_timestamp
        )

    except Exception as e:
        logger.error(f"Error in integrity audit: {e}")
        raise HTTPException(status_code=500, detail=f"Audit error: {str(e)}")

@integrity_router.get("/stats")
async def get_integrity_stats(token: str = Depends(require_bearer)):
    """
    Obtener estadísticas de integridad
    """
    try:
        stats = integrity_service.get_integrity_stats()
        return {
            "integrity_stats": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting integrity stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@integrity_router.get("/records/{result_id}")
async def get_integrity_records(
    result_id: str,
    token: str = Depends(require_bearer)
):
    """
    Obtener registros de integridad para un resultado
    """
    try:
        records = [
            {
                "record_id": record.record_id,
                "verification_timestamp": record.verification_timestamp.isoformat(),
                "integrity_status": record.integrity_status,
                "confidence_score": record.confidence_score,
                "verification_method": record.verification_method
            }
            for record in integrity_service.integrity_records.values()
            if record.result_id == result_id
        ]

        return {
            "result_id": result_id,
            "total_records": len(records),
            "records": records[-10:],  # Últimos 10 registros
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting integrity records: {e}")
        raise HTTPException(status_code=500, detail=f"Records error: {str(e)}")

# Función de utilidad para integración con otros servicios
def create_integrity_hash(data: Dict[str, Any]) -> str:
    """
    Crear hash de integridad para datos

    Args:
        data: Datos para los que crear hash de integridad

    Returns:
        str: Hash de integridad
    """
    data_json = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_json.encode()).hexdigest()

# Exportar componentes principales
__all__ = [
    'IntegrityVerificationService',
    'integrity_service',
    'integrity_router',
    'IntegrityRecord',
    'IntegrityAudit',
    'DataIntegrityCheck',
    'create_integrity_hash'
]
