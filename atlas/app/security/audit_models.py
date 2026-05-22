"""
Audit Models - Modelos Pydantic para eventos de auditoría
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum


class AuditEventType(str, Enum):
    """Tipos de eventos de auditoría"""
    ETHICS_EVALUATION = "ethics_evaluation"
    RISK_ASSESSMENT = "risk_assessment"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENT_EXECUTION = "experiment_execution"
    MODEL_INFERENCE = "model_inference"
    USER_AUTHENTICATION = "user_authentication"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_CHANGE = "configuration_change"


class AuditEvent(BaseModel):
    """Modelo base para eventos de auditoría"""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = Field(..., description="Identificador único del evento")
    event_type: AuditEventType = Field(..., description="Tipo de evento")
    user_id: Optional[str] = Field(None, description="ID del usuario que generó el evento")
    details: Dict[str, Any] = Field(..., description="Detalles específicos del evento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
    
    @validator('event_id')
    def validate_event_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('event_id must be at least 10 characters long')
        return v
    
    @validator('details')
    def validate_details(cls, v):
        if not isinstance(v, dict):
            raise ValueError('details must be a dictionary')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class EthicsEvaluationEvent(BaseModel):
    """Evento específico para evaluaciones éticas"""
    domain: str = Field(..., description="Dominio científico del experimento")
    description: str = Field(..., description="Descripción del experimento")
    decision: str = Field(..., description="Decisión ética (LOW, MEDIUM, HIGH, CRITICAL)")
    risk_score: int = Field(..., ge=0, le=20, description="Score de riesgo (0-20)")
    allowed: bool = Field(..., description="Si el experimento está permitido")
    requires_signature: bool = Field(False, description="Si requiere firma")
    escalation_reasons: List[str] = Field(default_factory=list, description="Razones de escalación")
    keywords: List[str] = Field(default_factory=list, description="Keywords detectadas")
    data_sensitivity: str = Field("none", description="Sensibilidad de datos")
    declared_intent: str = Field("research", description="Intención declarada")
    
    @validator('decision')
    def validate_decision(cls, v):
        valid_decisions = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if v not in valid_decisions:
            raise ValueError(f'decision must be one of {valid_decisions}')
        return v
    
    @validator('data_sensitivity')
    def validate_data_sensitivity(cls, v):
        valid_sensitivities = ['none', 'low', 'medium', 'high', 'critical']
        if v not in valid_sensitivities:
            raise ValueError(f'data_sensitivity must be one of {valid_sensitivities}')
        return v
    
    @validator('declared_intent')
    def validate_declared_intent(cls, v):
        valid_intents = ['research', 'education', 'commercial', 'defense', 'dual_use']
        if v not in valid_intents:
            raise ValueError(f'declared_intent must be one of {valid_intents}')
        return v


class RiskAssessmentEvent(BaseModel):
    """Evento específico para evaluaciones de riesgo"""
    domain: str = Field(..., description="Dominio científico")
    description: str = Field(..., description="Descripción del experimento")
    level: str = Field(..., description="Nivel de riesgo")
    risk_score: int = Field(..., ge=0, le=20, description="Score de riesgo")
    blocked: bool = Field(..., description="Si está bloqueado")
    reasons: List[str] = Field(default_factory=list, description="Razones del bloqueo")
    ethical_level: str = Field(..., description="Nivel ético")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if v not in valid_levels:
            raise ValueError(f'level must be one of {valid_levels}')
        return v


class DataAccessEvent(BaseModel):
    """Evento específico para acceso a datos sensibles"""
    data_type: str = Field(..., description="Tipo de datos accedidos")
    access_level: str = Field(..., description="Nivel de acceso")
    operation: str = Field(..., description="Operación realizada")
    data_size: Optional[int] = Field(None, description="Tamaño de datos en bytes")
    duration: Optional[float] = Field(None, description="Duración de la operación en segundos")
    success: bool = Field(True, description="Si la operación fue exitosa")
    
    @validator('access_level')
    def validate_access_level(cls, v):
        valid_levels = ['read', 'write', 'delete', 'admin']
        if v not in valid_levels:
            raise ValueError(f'access_level must be one of {valid_levels}')
        return v


class HypothesisGenerationEvent(BaseModel):
    """Evento específico para generación de hipótesis"""
    domain: str = Field(..., description="Dominio científico")
    hypothesis: str = Field(..., description="Hipótesis generada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en la hipótesis")
    method: str = Field("ai_generated", description="Método de generación")
    source_data: Optional[str] = Field(None, description="Fuente de datos")
    validation_status: str = Field("pending", description="Estado de validación")
    
    @validator('method')
    def validate_method(cls, v):
        valid_methods = ['ai_generated', 'manual', 'hybrid', 'template_based']
        if v not in valid_methods:
            raise ValueError(f'method must be one of {valid_methods}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        valid_statuses = ['pending', 'validated', 'rejected', 'needs_review']
        if v not in valid_statuses:
            raise ValueError(f'validation_status must be one of {valid_statuses}')
        return v


class ExperimentExecutionEvent(BaseModel):
    """Evento específico para ejecución de experimentos"""
    experiment_id: str = Field(..., description="ID único del experimento")
    domain: str = Field(..., description="Dominio científico")
    status: str = Field(..., description="Estado del experimento")
    resources_used: Dict[str, Any] = Field(default_factory=dict, description="Recursos utilizados")
    start_time: Optional[datetime] = Field(None, description="Tiempo de inicio")
    end_time: Optional[datetime] = Field(None, description="Tiempo de finalización")
    duration: Optional[float] = Field(None, description="Duración en segundos")
    error_message: Optional[str] = Field(None, description="Mensaje de error si aplica")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['started', 'running', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of {valid_statuses}')
        return v
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


class ModelInferenceEvent(BaseModel):
    """Evento específico para inferencia de modelos"""
    model_name: str = Field(..., description="Nombre del modelo")
    input_type: str = Field(..., description="Tipo de entrada")
    output_type: str = Field(..., description="Tipo de salida")
    processing_time: float = Field(..., ge=0, description="Tiempo de procesamiento en segundos")
    input_size: Optional[int] = Field(None, description="Tamaño de entrada")
    output_size: Optional[int] = Field(None, description="Tamaño de salida")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confianza del modelo")
    model_version: Optional[str] = Field(None, description="Versión del modelo")
    
    @validator('input_type')
    def validate_input_type(cls, v):
        valid_types = ['text', 'image', 'audio', 'video', 'structured_data', 'mixed']
        if v not in valid_types:
            raise ValueError(f'input_type must be one of {valid_types}')
        return v
    
    @validator('output_type')
    def validate_output_type(cls, v):
        valid_types = ['text', 'image', 'audio', 'video', 'structured_data', 'mixed', 'classification', 'regression']
        if v not in valid_types:
            raise ValueError(f'output_type must be one of {valid_types}')
        return v


class UserAuthenticationEvent(BaseModel):
    """Evento específico para autenticación de usuarios"""
    user_id: str = Field(..., description="ID del usuario")
    action: str = Field(..., description="Acción de autenticación")
    success: bool = Field(..., description="Si la autenticación fue exitosa")
    ip_address: Optional[str] = Field(None, description="Dirección IP")
    user_agent: Optional[str] = Field(None, description="User agent del cliente")
    session_id: Optional[str] = Field(None, description="ID de sesión")
    failure_reason: Optional[str] = Field(None, description="Razón del fallo si aplica")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['login', 'logout', 'token_refresh', 'password_change', 'account_lockout']
        if v not in valid_actions:
            raise ValueError(f'action must be one of {valid_actions}')
        return v


class PolicyViolationEvent(BaseModel):
    """Evento específico para violaciones de política"""
    policy_name: str = Field(..., description="Nombre de la política violada")
    violation_type: str = Field(..., description="Tipo de violación")
    severity: str = Field(..., description="Severidad de la violación")
    description: str = Field(..., description="Descripción de la violación")
    affected_resource: Optional[str] = Field(None, description="Recurso afectado")
    remediation_action: Optional[str] = Field(None, description="Acción de remediación")
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'severity must be one of {valid_severities}')
        return v


class SystemErrorEvent(BaseModel):
    """Evento específico para errores del sistema"""
    error_type: str = Field(..., description="Tipo de error")
    error_message: str = Field(..., description="Mensaje de error")
    stack_trace: Optional[str] = Field(None, description="Stack trace del error")
    component: Optional[str] = Field(None, description="Componente que generó el error")
    severity: str = Field("medium", description="Severidad del error")
    recovery_action: Optional[str] = Field(None, description="Acción de recuperación")
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'severity must be one of {valid_severities}')
        return v


class ConfigurationChangeEvent(BaseModel):
    """Evento específico para cambios de configuración"""
    config_name: str = Field(..., description="Nombre de la configuración")
    old_value: str = Field(..., description="Valor anterior")
    new_value: str = Field(..., description="Nuevo valor")
    changed_by: Optional[str] = Field(None, description="Usuario que realizó el cambio")
    change_reason: Optional[str] = Field(None, description="Razón del cambio")
    requires_restart: bool = Field(False, description="Si requiere reinicio")
    validation_status: str = Field("pending", description="Estado de validación")
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        valid_statuses = ['pending', 'validated', 'rejected', 'needs_review']
        if v not in valid_statuses:
            raise ValueError(f'validation_status must be one of {valid_statuses}')
        return v


# Mapeo de tipos de evento a modelos específicos
EVENT_MODEL_MAPPING = {
    AuditEventType.ETHICS_EVALUATION: EthicsEvaluationEvent,
    AuditEventType.RISK_ASSESSMENT: RiskAssessmentEvent,
    AuditEventType.SENSITIVE_DATA_ACCESS: DataAccessEvent,
    AuditEventType.HYPOTHESIS_GENERATION: HypothesisGenerationEvent,
    AuditEventType.EXPERIMENT_EXECUTION: ExperimentExecutionEvent,
    AuditEventType.MODEL_INFERENCE: ModelInferenceEvent,
    AuditEventType.USER_AUTHENTICATION: UserAuthenticationEvent,
    AuditEventType.POLICY_VIOLATION: PolicyViolationEvent,
    AuditEventType.SYSTEM_ERROR: SystemErrorEvent,
    AuditEventType.CONFIGURATION_CHANGE: ConfigurationChangeEvent,
}
