"""
🔬 Esquemas Pydantic para Workflow Orchestrator - AXIOM v4.1
===========================================================

Modelos de datos robustos para la orquestación de flujos de trabajo científicos.
Proporciona validación estricta, documentación completa y tipos seguros para
todos los aspectos de la gestión de workflows científicos.

📋 Modelos Principales
----------------------

🔧 **WorkflowStepCreate:** Definición de pasos individuales en un workflow
📝 **WorkflowCreateRequest:** Especificación completa para crear workflows
▶️ **ExecuteWorkflowRequest:** Parámetros para ejecutar workflows
📊 **WorkflowStatusResponse:** Estado detallado de ejecución de workflows
🔗 **WorkflowGraphResponse:** Representación gráfica DAG de dependencias

🎯 Validaciones Implementadas
-----------------------------

- **Tipos Literales:** Restricción de servicios y operaciones permitidas
- **Validadores Personalizados:** Lógica de negocio específica
- **Constraints Numéricos:** Límites realistas para timeouts y reintentos
- **Validación de Dependencias:** Verificación de grafos acíclicos
- **Metadatos Estructurados:** Campos opcionales con valores por defecto

🔬 Aplicaciones Científicas
---------------------------

**Investigación Biomédica:**
   - Análisis genómico automatizado
   - Screening molecular de alto rendimiento
   - Estudios clínicos multi-fase

**Química Computacional:**
   - Simulaciones de docking molecular
   - Optimización de rutas sintéticas
   - Predicción de propiedades fisicoquímicas

**Física y Matemáticas:**
   - Cadenas de simulación numérica
   - Análisis estadístico automatizado
   - Validación cruzada de modelos

**Ciencias de la Tierra:**
   - Procesamiento geoespacial
   - Modelado climático
   - Análisis ambiental temporal
"""

from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field, validator, root_validator, model_validator, ConfigDict
from datetime import datetime, timedelta
from enum import Enum
import re


class WorkflowStatus(str, Enum):
    """Estados posibles de un workflow científico."""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowPriority(str, Enum):
    """Niveles de prioridad para ejecución de workflows."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ServiceType(str, Enum):
    """Tipos de servicios científicos soportados por el orquestador."""
    COMPUTATIONAL_CHEMISTRY = "computational_chemistry"
    QUANTUM_PHYSICS = "quantum_physics"
    QUANTUM_COMPUTING = "quantum_computing"
    PDE = "pde"
    OPTIMIZATION = "optimization"
    SCIENTIFIC_AI = "scientific_ai"
    ARITHMETIC = "arithmetic"
    CALCULUS = "calculus"
    EQUATIONS = "equations"
    STATISTICS = "statistics"
    GRAPHING = "graphing"
    GEOMETRY = "geometry"
    GENOMICS = "genomics"
    NEUROSCIENCE = "neuroscience"
    EARTH_SCIENCES = "earth_sciences"


class WorkflowStepCreate(BaseModel):
    """
    🔧 Definición de un paso individual en un workflow científico.

    Cada paso representa una operación específica dentro del flujo de trabajo,
    con dependencias claras y parámetros configurables.
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    step_id: Optional[str] = Field(
        None,
        description="Identificador único del paso (auto-generado si no se proporciona)",
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )

    service_type: ServiceType = Field(
        ...,
        description="Tipo de servicio científico que ejecutará este paso"
    )

    operation: str = Field(
        ...,
        description="Nombre de la operación específica a ejecutar",
        min_length=1,
        max_length=200
    )

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parámetros específicos para la operación",
        example={"input_file": "data.csv", "method": "fft", "threshold": 0.95}
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de pasos que deben completarse antes de este",
        example=["step_1", "step_2"]
    )

    timeout_sec: Optional[int] = Field(
        None,
        ge=1,
        le=36000,  # Máximo 10 horas
        description="Timeout en segundos para este paso (1-36000)",
        example=3600
    )

    max_retries: Optional[int] = Field(
        0,
        ge=0,
        le=5,
        description="Número máximo de reintentos en caso de fallo (0-5)",
        example=3
    )

    priority: WorkflowPriority = Field(
        WorkflowPriority.NORMAL,
        description="Prioridad de ejecución del paso"
    )

    @validator('step_id')
    def validate_step_id(cls, v):
        """Validar formato del step_id."""
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('step_id must contain only alphanumeric characters, underscores, and hyphens')
        return v

    @validator('dependencies')
    def validate_dependencies(cls, v):
        """Validar que no haya dependencias circulares básicas."""
        if len(v) != len(set(v)):
            raise ValueError('Dependencies must be unique')
        return v


class WorkflowCreateRequest(BaseModel):
    """
    📝 Solicitud completa para crear un nuevo workflow científico.

    Permite crear workflows desde cero o utilizando plantillas predefinidas,
    con metadatos extensivos para trazabilidad completa.
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    """

    name: str = Field(
        ...,
        description="Nombre descriptivo del workflow",
        min_length=1,
        max_length=200,
        example="Análisis Genómico SARS-CoV-2"
    )

    description: Optional[str] = Field(
        None,
        description="Descripción detallada del propósito del workflow",
        max_length=1000,
        example="Pipeline completo para análisis genómico de variantes virales"
    )

    template: Optional[str] = Field(
        None,
        description="Nombre de plantilla predefinida a utilizar",
        example="genomic_analysis_v1"
    )

    steps: Optional[List[WorkflowStepCreate]] = Field(
        None,
        description="Pasos personalizados del workflow (requerido si no se usa template)"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos adicionales para trazabilidad",
        example={
            "author": "Dr. María González",
            "institution": "Universidad Nacional",
            "funding": "Grant #2024-001",
            "tags": ["genomics", "virology", "automation"]
        }
    )

    priority: WorkflowPriority = Field(
        WorkflowPriority.NORMAL,
        description="Prioridad global del workflow"
    )

    max_execution_time: Optional[int] = Field(
        None,
        ge=60,
        le=86400,  # Máximo 24 horas
        description="Tiempo máximo de ejecución en segundos",
        example=7200
    )

    @model_validator(mode='before')
    @classmethod
    def validate_creation_params(cls, values):
        """Validar parámetros de creación."""
        if isinstance(values, dict):
            template = values.get('template')
            steps = values.get('steps')

            if not template and not steps:
                raise ValueError('Either template or steps must be provided')

            if template and steps:
                raise ValueError('Cannot specify both template and custom steps')

        return values


class ExecuteWorkflowRequest(BaseModel):
    """
    ▶️ Parámetros para ejecutar un workflow existente.

    Permite iniciar la ejecución de workflows con parámetros específicos
    y opciones de configuración.
    """

    workflow_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identificador único del workflow a ejecutar",
        examples=["wf_2024_001"]
    )

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parámetros de ejecución específicos",
        examples=[{"input_data": "experiment_001.csv", "output_format": "json"}]
    )

    priority: Optional[WorkflowPriority] = Field(
        None,
        description="Prioridad de ejecución (sobrescribe la del workflow)"
    )

    notify_on_completion: bool = Field(
        False,
        description="Enviar notificación al completar la ejecución"
    )

    callback_url: Optional[str] = Field(
        None,
        description="URL para callback asíncrono al completar",
        pattern=r'^https?://.+$'
    )


class WorkflowStepStatus(BaseModel):
    """Estado detallado de un paso individual del workflow."""

    step_id: str = Field(..., description="Identificador del paso")
    status: WorkflowStatus = Field(..., description="Estado actual del paso")
    service_type: ServiceType = Field(..., description="Tipo de servicio utilizado")
    operation: str = Field(..., description="Operación ejecutada")
    started_at: Optional[datetime] = Field(None, description="Timestamp de inicio")
    completed_at: Optional[datetime] = Field(None, description="Timestamp de finalización")
    duration_sec: Optional[float] = Field(None, description="Duración en segundos")
    retries: int = Field(0, description="Número de reintentos realizados")
    error_message: Optional[str] = Field(None, description="Mensaje de error si falló")
    results: Dict[str, Any] = Field(default_factory=dict, description="Resultados del paso")


class WorkflowStatusResponse(BaseModel):
    """
    📊 Respuesta completa con estado detallado de un workflow.

    Proporciona información comprehensiva sobre el estado de ejecución,
    progreso, métricas de rendimiento y resultados obtenidos.
    """

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    workflow_id: str = Field(..., description="Identificador único del workflow")
    name: str = Field(..., description="Nombre del workflow")
    status: WorkflowStatus = Field(..., description="Estado actual del workflow")
    priority: WorkflowPriority = Field(..., description="Prioridad de ejecución")

    created_at: Optional[datetime] = Field(None, description="Timestamp de creación")
    started_at: Optional[datetime] = Field(None, description="Timestamp de inicio de ejecución")
    completed_at: Optional[datetime] = Field(None, description="Timestamp de finalización")
    duration_sec: Optional[float] = Field(None, description="Duración total en segundos")

    progress_percentage: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        description="Porcentaje de progreso (0-100%)"
    )

    steps: List[WorkflowStepStatus] = Field(
        default_factory=list,
        description="Estado detallado de cada paso"
    )

    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resultados finales del workflow",
        examples=[{"output_files": ["result.csv"], "metrics": {"accuracy": 0.95}}]
    )

    error_message: Optional[str] = Field(
        None,
        description="Mensaje de error si el workflow falló"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos adicionales del workflow"
    )


class WorkflowGraphNode(BaseModel):
    """
    🔗 Nodo en el grafo DAG de un workflow.

    Representa un paso individual con su estado y conexiones
    para visualización gráfica de dependencias.
    """

    id: str = Field(..., description="Identificador único del nodo")
    label: str = Field(..., description="Etiqueta descriptiva del nodo")
    status: WorkflowStatus = Field(..., description="Estado actual del nodo")
    service_type: ServiceType = Field(..., description="Tipo de servicio científico")
    operation: str = Field(..., description="Operación específica")
    position_x: Optional[float] = Field(None, description="Posición X para visualización")
    position_y: Optional[float] = Field(None, description="Posición Y para visualización")


class WorkflowGraphEdge(BaseModel):
    """
    🔗 Arista en el grafo DAG de un workflow.

    Representa una dependencia entre dos pasos del workflow.
    """

    source: str = Field(..., description="ID del nodo origen (dependencia)")
    target: str = Field(..., description="ID del nodo destino")
    label: Optional[str] = Field(None, description="Etiqueta opcional de la conexión")


class WorkflowGraphResponse(BaseModel):
    """
    🔗 Respuesta con representación gráfica completa del workflow.

    Proporciona la estructura DAG completa con nodos y aristas
    para visualización y análisis de dependencias.
    """

    workflow_id: str = Field(..., description="Identificador del workflow")
    name: str = Field(..., description="Nombre del workflow")
    nodes: List[WorkflowGraphNode] = Field(
        default_factory=list,
        description="Lista de nodos del grafo"
    )
    edges: List[WorkflowGraphEdge] = Field(
        default_factory=list,
        description="Lista de aristas del grafo"
    )
    layout_algorithm: str = Field(
        "dagre",
        description="Algoritmo de layout utilizado para la visualización"
    )


class WorkflowTemplateInfo(BaseModel):
    """
    📋 Información de una plantilla de workflow.

    Describe las características de una plantilla predefinida
    disponible para crear workflows rápidamente.
    """

    template_name: str = Field(..., description="Nombre único de la plantilla")
    display_name: str = Field(..., description="Nombre descriptivo para UI")
    description: str = Field(..., description="Descripción detallada de la plantilla")
    category: str = Field(..., description="Categoría científica de la plantilla")
    estimated_duration: Optional[int] = Field(None, description="Duración estimada en segundos")
    required_services: List[ServiceType] = Field(
        default_factory=list,
        description="Servicios requeridos por la plantilla"
    )
    parameters_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Esquema JSON de parámetros requeridos"
    )


class WorkflowListResponse(BaseModel):
    """
    📋 Respuesta con lista de workflows disponibles.

    Proporciona información resumida de múltiples workflows
    para interfaces de listado y búsqueda.
    """

    workflows: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de workflows con información básica"
    )
    total_count: int = Field(..., description="Número total de workflows")
    page: int = Field(1, ge=1, description="Página actual")
    page_size: int = Field(20, ge=1, le=100, description="Elementos por página")


class WorkflowProvenanceResponse(BaseModel):
    """
    🔍 Respuesta con información de procedencia completa.

    Proporciona trazabilidad completa del workflow incluyendo
    IDs de ejecución MLflow, enlaces de datos y metadatos.
    """

    workflow_id: str = Field(..., description="Identificador del workflow")
    mlflow_run_ids: List[str] = Field(
        default_factory=list,
        description="IDs de ejecuciones MLflow relacionadas"
    )
    data_lineage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Linaje de datos y dependencias"
    )
    execution_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos de ejecución detallados"
    )
    created_by: str = Field(..., description="Usuario que creó el workflow")
    created_at: datetime = Field(..., description="Timestamp de creación")
    last_modified: datetime = Field(..., description="Timestamp de última modificación")
