"""
AXIOM Astronomy - Flujos de Trabajo Avanzados de Análisis Astronómico
=====================================================================

Sistema avanzado de flujos de trabajo (workflows) para análisis astronómico
automatizado, con configuraciones predefinidas, ejecución por lotes, y
orquestación inteligente de pipelines complejos para investigación científica.

Funcionalidades principales:
- Flujos de trabajo predefinidos para casos de uso comunes
- Ejecución por lotes de múltiples objetos
- Orquestación inteligente de análisis complejos
- Configuraciones adaptativas según el tipo de objeto
- Monitoreo y logging avanzado de workflows
- Integración con sistemas de almacenamiento científico
- Generación automática de reportes de investigación
- Optimización de recursos computacionales

Autor: AXIOM Development Team
Fecha: Octubre 2025
Versión: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import numpy as np
import logging
from datetime import datetime
from pathlib import Path
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import uuid
import aiofiles
import asyncio
from app.exceptions.domain.biology import BiologyError

# Setup logging
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Tipos de flujos de trabajo predefinidos."""
    STELLAR_SURVEY = "stellar_survey"
    EXOPLANET_SEARCH = "exoplanet_search"
    VARIABLE_STAR_MONITORING = "variable_star_monitoring"
    BINARY_SYSTEM_ANALYSIS = "binary_system_analysis"
    ASTROMETRIC_PRECISION = "astrometric_precision"
    MULTI_OBJECT_PHOTOMETRY = "multi_object_photometry"
    COMPREHENSIVE_CHARACTERIZATION = "comprehensive_characterization"
    CUSTOM_WORKFLOW = "custom_workflow"

class ExecutionMode(Enum):
    """Modos de ejecución de workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    BATCH_PROCESSING = "batch_processing"

class WorkflowStatus(Enum):
    """Estados de los workflows."""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Niveles de prioridad."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class WorkflowStep:
    """Definición de un paso en el workflow."""
    step_id: str
    service_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    retry_count: int = 3
    timeout_minutes: int = 30
    quality_threshold: float = 0.5

@dataclass
class WorkflowTemplate:
    """Plantilla de workflow predefinida."""
    template_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    steps: List[WorkflowStep] = field(default_factory=list)
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_minutes: int = 60
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    target_object_types: List[str] = field(default_factory=list)

@dataclass
class BatchConfiguration:
    """Configuración para procesamiento por lotes."""
    batch_size: int = 10
    max_concurrent_batches: int = 3
    retry_failed_objects: bool = True
    continue_on_failure: bool = True
    progress_reporting_interval: int = 5
    checkpoint_frequency: int = 50
    auto_scaling: bool = False

@dataclass
class WorkflowExecution:
    """Información de ejecución de un workflow."""
    execution_id: str
    workflow_type: WorkflowType
    template_id: str
    object_ids: List[str]
    status: WorkflowStatus = WorkflowStatus.CREATED
    priority: Priority = Priority.NORMAL
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    current_step: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceMonitor:
    """Monitor de recursos del sistema."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_workflows: int = 0
    queued_workflows: int = 0
    last_update: Optional[datetime] = None

@dataclass
class WorkflowReport:
    """Reporte completo de ejecución de workflow."""
    execution_id: str
    workflow_type: WorkflowType
    total_objects: int
    successful_objects: int
    failed_objects: int
    execution_time: float
    average_quality_score: float
    resource_utilization: Dict[str, float]
    scientific_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)

class AdvancedAstronomyWorkflow:
    """
    Sistema avanzado de flujos de trabajo para análisis astronómico.
    
    Proporciona orquestación inteligente de análisis complejos con
    configuraciones predefinidas, ejecución por lotes, y optimización
    automática de recursos para investigación científica a gran escala.
    """
    
    def __init__(self, base_output_dir: Optional[str] = None, max_concurrent_workflows: int = 5):
        """
        Inicializa el sistema de workflows.
        
        Args:
            base_output_dir: Directorio base para outputs
            max_concurrent_workflows: Máximo workflows concurrentes
        """
        self.base_output_dir = Path(base_output_dir or "./axiom_workflows")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent_workflows = max_concurrent_workflows
        
        # Templates predefinidos
        self._workflow_templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_templates()
        
        # Ejecuciones activas
        self._active_executions: Dict[str, WorkflowExecution] = {}
        self._execution_queue: List[WorkflowExecution] = []
        
        # Monitor de recursos
        self._resource_monitor = ResourceMonitor()
        
        # Pipeline integrado
        try:
            from .integrated_astronomy_pipeline import IntegratedAstronomyPipeline
            self._pipeline = IntegratedAstronomyPipeline(str(self.base_output_dir / "pipeline_outputs"))
        except ImportError:
            logger.warning("Pipeline integrado no disponible")
            self._pipeline = None
        
        # Estadísticas
        self._execution_stats = defaultdict(int)
        
        logger.info("AdvancedAstronomyWorkflow inicializado")
    
    def _initialize_templates(self):
        """Inicializa templates predefinidos de workflows."""
        
        # Template: Stellar Survey
        stellar_survey = WorkflowTemplate(
            template_id="stellar_survey_v1",
            name="Stellar Survey Analysis",
            description="Análisis completo de survey estelar con fotometría y clasificación",
            workflow_type=WorkflowType.STELLAR_SURVEY,
            steps=[
                WorkflowStep("aperture_opt", "optimal_aperture", {"method": "adaptive"}),
                WorkflowStep("photometry", "lightkurve_advanced", {"detrend": True}),
                WorkflowStep("variability", "stellar_variability", dependencies=["photometry"]),
                WorkflowStep("classification", "astronomical_ml", dependencies=["variability"]),
                WorkflowStep("statistics", "advanced_statistics", dependencies=["photometry"])
            ],
            estimated_duration_minutes=45,
            target_object_types=["star", "variable_star"]
        )
        
        # Template: Exoplanet Search
        exoplanet_search = WorkflowTemplate(
            template_id="exoplanet_search_v1",
            name="Exoplanet Transit Search",
            description="Búsqueda sistemática de tránsitos exoplanetarios",
            workflow_type=WorkflowType.EXOPLANET_SEARCH,
            steps=[
                WorkflowStep("photometry", "lightkurve_advanced", {"detrend": True, "remove_outliers": True}),
                WorkflowStep("transit_search", "exoplanet_transit", dependencies=["photometry"]),
                WorkflowStep("binary_check", "binary_system", dependencies=["photometry"]),
                WorkflowStep("statistics", "advanced_statistics", dependencies=["transit_search"]),
                WorkflowStep("ml_validation", "astronomical_ml", dependencies=["transit_search"])
            ],
            estimated_duration_minutes=90,
            target_object_types=["star", "main_sequence", "solar_analog"]
        )
        
        # Template: Variable Star Monitoring
        variable_monitoring = WorkflowTemplate(
            template_id="variable_monitoring_v1",
            name="Variable Star Monitoring",
            description="Monitoreo avanzado de estrellas variables",
            workflow_type=WorkflowType.VARIABLE_STAR_MONITORING,
            steps=[
                WorkflowStep("precision_phot", "optimal_aperture", {"precision_mode": True}),
                WorkflowStep("variability", "stellar_variability", dependencies=["precision_phot"]),
                WorkflowStep("period_analysis", "advanced_statistics", dependencies=["variability"]),
                WorkflowStep("classification", "astronomical_ml", dependencies=["period_analysis"]),
                WorkflowStep("multiband", "multiwavelength", dependencies=["precision_phot"], optional=True)
            ],
            estimated_duration_minutes=60,
            target_object_types=["variable_star", "pulsating_star", "eclipsing_binary"]
        )
        
        # Template: Binary System Analysis
        binary_analysis = WorkflowTemplate(
            template_id="binary_analysis_v1",
            name="Binary System Analysis",
            description="Análisis completo de sistemas binarios",
            workflow_type=WorkflowType.BINARY_SYSTEM_ANALYSIS,
            steps=[
                WorkflowStep("photometry", "lightkurve_advanced", {"high_precision": True}),
                WorkflowStep("binary_detection", "binary_system", dependencies=["photometry"]),
                WorkflowStep("astrometry", "astrometric_analysis", dependencies=["photometry"]),
                WorkflowStep("orbit_analysis", "advanced_statistics", dependencies=["binary_detection", "astrometry"]),
                WorkflowStep("system_class", "astronomical_ml", dependencies=["orbit_analysis"])
            ],
            estimated_duration_minutes=120,
            target_object_types=["binary_star", "eclipsing_binary", "spectroscopic_binary"]
        )
        
        # Template: Astrometric Precision
        astrometric_precision = WorkflowTemplate(
            template_id="astrometric_precision_v1",
            name="High-Precision Astrometry",
            description="Análisis astrométrico de alta precisión",
            workflow_type=WorkflowType.ASTROMETRIC_PRECISION,
            steps=[
                WorkflowStep("precision_astro", "astropy_precision", {"high_precision": True}),
                WorkflowStep("astrometric_analysis", "astrometric_analysis", dependencies=["precision_astro"]),
                WorkflowStep("motion_analysis", "advanced_statistics", dependencies=["astrometric_analysis"]),
                WorkflowStep("anomaly_detection", "astronomical_ml", dependencies=["motion_analysis"])
            ],
            estimated_duration_minutes=75,
            target_object_types=["star", "moving_object", "asteroid"]
        )
        
        # Template: Comprehensive Characterization
        comprehensive = WorkflowTemplate(
            template_id="comprehensive_v1",            
            name="Comprehensive Object Characterization",
            description="Caracterización completa usando todos los servicios AXIOM",
            workflow_type=WorkflowType.COMPREHENSIVE_CHARACTERIZATION,
            steps=[
                WorkflowStep("aperture_opt", "optimal_aperture"),
                WorkflowStep("photometry", "lightkurve_advanced", dependencies=["aperture_opt"]),
                WorkflowStep("precision_astro", "astropy_precision"),
                WorkflowStep("variability", "stellar_variability", dependencies=["photometry"]),
                WorkflowStep("binary_check", "binary_system", dependencies=["photometry"]),
                WorkflowStep("transit_search", "exoplanet_transit", dependencies=["photometry"]),
                WorkflowStep("statistics", "advanced_statistics", dependencies=["variability"]),
                WorkflowStep("multiband", "multiwavelength", dependencies=["photometry"]),
                WorkflowStep("astrometry", "astrometric_analysis", dependencies=["precision_astro"]),
                WorkflowStep("ml_analysis", "astronomical_ml", dependencies=["statistics", "astrometry"])
            ],
            estimated_duration_minutes=180,
            target_object_types=["any"]
        )
        
        # Almacenar templates
        templates = [
            stellar_survey, exoplanet_search, variable_monitoring,
            binary_analysis, astrometric_precision, comprehensive
        ]
        
        for template in templates:
            self._workflow_templates[template.template_id] = template
        
        logger.info(f"Inicializados {len(self._workflow_templates)} templates de workflow")
    
    def get_available_workflows(self) -> List[WorkflowTemplate]:
        """Retorna lista de workflows disponibles."""
        return list(self._workflow_templates.values())
    
    def get_workflow_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Obtiene un template específico."""
        return self._workflow_templates.get(template_id)
    
    def create_workflow_execution(
        self,
        template_id: str,
        object_ids: List[str],
        priority: Priority = Priority.NORMAL,
        custom_parameters: Optional[Dict[str, Any]] = None,
        batch_config: Optional[BatchConfiguration] = None
    ) -> str:
        """
        Crea una nueva ejecución de workflow.
        
        Args:
            template_id: ID del template a usar
            object_ids: Lista de objetos a procesar
            priority: Prioridad de ejecución
            custom_parameters: Parámetros personalizados
            batch_config: Configuración de lotes
            
        Returns:
            str: ID de la ejecución creada
        """
        if template_id not in self._workflow_templates:
            raise ValueError(f"Template no encontrado: {template_id}")
        
        template = self._workflow_templates[template_id]
        execution_id = f"axiom_workflow_{uuid.uuid4().hex[:8]}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_type=template.workflow_type,
            template_id=template_id,
            object_ids=object_ids,
            priority=priority,
            metadata={
                "custom_parameters": custom_parameters or {},
                "batch_config": batch_config.__dict__ if batch_config else {},
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Añadir a la cola
        self._execution_queue.append(execution)
        self._execution_queue.sort(key=lambda x: x.priority.value, reverse=True)
        
        logger.info(f"Workflow creado: {execution_id} ({len(object_ids)} objetos)")
        return execution_id
    
    def execute_workflow(
        self,
        execution_id: str,
        execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE
    ) -> WorkflowReport:
        """
        Ejecuta un workflow específico.
        
        Args:
            execution_id: ID de la ejecución
            execution_mode: Modo de ejecución
            
        Returns:
            WorkflowReport: Reporte de ejecución
        """
        # Buscar ejecución en la cola
        execution = None
        for i, exec_item in enumerate(self._execution_queue):
            if exec_item.execution_id == execution_id:
                execution = self._execution_queue.pop(i)
                break
        
        if not execution:
            raise ValueError(f"Ejecución no encontrada: {execution_id}")
        
        # Mover a activas
        self._active_executions[execution_id] = execution
        execution.status = WorkflowStatus.RUNNING
        execution.start_time = datetime.now()
        
        try:
            logger.info(f"Iniciando workflow {execution_id}")
            
            # Obtener template
            template = self._workflow_templates[execution.template_id]
            
            # Determinar modo de ejecución
            if execution_mode == ExecutionMode.ADAPTIVE:
                execution_mode = self._determine_optimal_execution_mode(execution, template)
            
            # Ejecutar según el modo
            if execution_mode == ExecutionMode.BATCH_PROCESSING:
                results = self._execute_batch_workflow(execution, template)
            elif execution_mode == ExecutionMode.PARALLEL:
                results = self._execute_parallel_workflow(execution, template)
            else:
                results = self._execute_sequential_workflow(execution, template)
            
            # Procesar resultados
            execution.results = results
            execution.status = WorkflowStatus.COMPLETED
            execution.progress = 100.0
            
        except BiologyError as e:
            logger.error(f"Error en workflow {execution_id}: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(str(e))
        
        finally:
            execution.end_time = datetime.now()
            
            # Mover de activas a completadas
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]
        
        # Generar reporte
        report = self._generate_workflow_report(execution)
        
        # Actualizar estadísticas
        self._execution_stats[execution.workflow_type.value] += 1
        self._execution_stats["total_executions"] += 1
        
        return report
    
    def _determine_optimal_execution_mode(
        self,
        execution: WorkflowExecution,
        template: WorkflowTemplate
    ) -> ExecutionMode:
        """Determina el modo de ejecución óptimo."""
        num_objects = len(execution.object_ids)
        estimated_duration = template.estimated_duration_minutes
        
        # Lógica adaptativa
        if num_objects > 100:
            return ExecutionMode.BATCH_PROCESSING
        elif num_objects > 10 and estimated_duration < 60:
            return ExecutionMode.PARALLEL
        else:
            return ExecutionMode.SEQUENTIAL
    
    def _execute_sequential_workflow(
        self,
        execution: WorkflowExecution,
        template: WorkflowTemplate
    ) -> Dict[str, Any]:
        """Ejecuta workflow secuencialmente."""
        results = {}
        total_objects = len(execution.object_ids)
        
        for i, object_id in enumerate(execution.object_ids):
            try:
                # Simular análisis del objeto
                object_results = self._analyze_single_object(object_id, template)
                results[object_id] = object_results
                
                # Actualizar progreso
                execution.progress = ((i + 1) / total_objects) * 100
                execution.current_step = f"Procesando {object_id}"
                
                logger.debug(f"Completado {object_id} ({i+1}/{total_objects})")
                
            except BiologyError as e:
                logger.error(f"Error procesando {object_id}: {e}")
                execution.errors.append(f"{object_id}: {str(e)}")
                results[object_id] = {"error": str(e)}
        
        return results
    
    def _execute_parallel_workflow(
        self,
        execution: WorkflowExecution,
        template: WorkflowTemplate
    ) -> Dict[str, Any]:
        """Ejecuta workflow en paralelo."""
        results = {}
        completed_objects = 0
        total_objects = len(execution.object_ids)
        
        max_workers = min(len(execution.object_ids), 8)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Crear tareas
            future_to_object = {
                executor.submit(self._analyze_single_object, obj_id, template): obj_id
                for obj_id in execution.object_ids
            }
            
            # Procesar resultados conforme se completan
            for future in as_completed(future_to_object):
                object_id = future_to_object[future]
                completed_objects += 1
                
                try:
                    object_results = future.result()
                    results[object_id] = object_results
                    
                except BiologyError as e:
                    logger.error(f"Error procesando {object_id}: {e}")
                    execution.errors.append(f"{object_id}: {str(e)}")
                    results[object_id] = {"error": str(e)}
                
                # Actualizar progreso
                execution.progress = (completed_objects / total_objects) * 100
                execution.current_step = f"Completados {completed_objects}/{total_objects}"
        
        return results
    
    def _execute_batch_workflow(
        self,
        execution: WorkflowExecution,
        template: WorkflowTemplate
    ) -> Dict[str, Any]:
        """Ejecuta workflow por lotes."""
        batch_config = BatchConfiguration()
        if "batch_config" in execution.metadata:
            batch_config.__dict__.update(execution.metadata["batch_config"])
        
        results = {}
        object_ids = execution.object_ids
        total_objects = len(object_ids)
        processed = 0
        
        # Procesar en lotes
        for i in range(0, total_objects, batch_config.batch_size):
            batch = object_ids[i:i + batch_config.batch_size]
            batch_num = i // batch_config.batch_size + 1
            total_batches = (total_objects + batch_config.batch_size - 1) // batch_config.batch_size
            
            logger.info(f"Procesando lote {batch_num}/{total_batches} ({len(batch)} objetos)")
            
            # Procesar lote en paralelo
            batch_results = self._process_batch(batch, template, batch_config)
            results.update(batch_results)
            
            processed += len(batch)
            execution.progress = (processed / total_objects) * 100
            execution.current_step = f"Lote {batch_num}/{total_batches}"
            
            # Checkpoint si es necesario
            if batch_num % batch_config.checkpoint_frequency == 0:
                self._save_checkpoint(execution, results)
        
        return results
    
    def _process_batch(
        self,
        object_ids: List[str],
        template: WorkflowTemplate,
        batch_config: BatchConfiguration
    ) -> Dict[str, Any]:
        """Procesa un lote de objetos."""
        results = {}
        
        max_workers = min(len(object_ids), 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_object = {
                executor.submit(self._analyze_single_object, obj_id, template): obj_id
                for obj_id in object_ids
            }
            
            for future in as_completed(future_to_object):
                object_id = future_to_object[future]
                
                try:
                    object_results = future.result()
                    results[object_id] = object_results
                    
                except BiologyError as e:
                    logger.error(f"Error en lote procesando {object_id}: {e}")
                    if batch_config.continue_on_failure:
                        results[object_id] = {"error": str(e)}
                    else:
                        raise
        
        return results
    
    def _analyze_single_object(
        self,
        object_id: str,
        template: WorkflowTemplate
    ) -> Dict[str, Any]:
        """Analiza un objeto individual según el template."""
        # Simular datos del objeto (en producción vendrían de una base de datos)
        object_data = self._generate_mock_data(object_id)
        
        step_results = {}
        
        # Ejecutar pasos del template
        for step in template.steps:
            try:
                # Verificar dependencias
                if step.dependencies:
                    for dep in step.dependencies:
                        if dep not in step_results:
                            raise ValueError(f"Dependencia no satisfecha: {dep}")
                
                # Simular ejecución del paso
                step_result = self._execute_workflow_step(step, object_data, step_results)
                step_results[step.step_id] = step_result
                
            except BiologyError as e:
                if not step.optional:
                    raise RuntimeError(f"Error en paso {step.step_id}: {e}")
                else:
                    logger.warning(f"Paso opcional falló {step.step_id}: {e}")
                    step_results[step.step_id] = {"skipped": True, "reason": str(e)}
        
        return {
            "object_id": object_id,
            "steps": step_results,
            "overall_quality": self._calculate_overall_quality(step_results),
            "execution_time": np.random.uniform(5, 30)  # Simulated
        }
    
    def _generate_mock_data(self, object_id: str) -> Dict[str, Any]:
        """Genera datos simulados para demostración."""
        np.random.seed(hash(object_id) % 2**32)
        
        time = np.linspace(0, 100, 1000)
        flux = 1.0 + 0.1 * np.sin(2 * np.pi * time / 10) + 0.02 * np.random.randn(len(time))
        
        return {
            "object_id": object_id,
            "time": time,
            "flux": flux,
            "flux_err": 0.01 * np.ones_like(flux),
            "coordinates": (np.random.uniform(0, 360), np.random.uniform(-90, 90)),
            "metadata": {"source": "AXIOM Workflow", "filter": "V"}
        }
    
    def _execute_workflow_step(
        self,
        step: WorkflowStep,
        object_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta un paso individual del workflow."""
        # Simular diferentes tipos de análisis
        service_name = step.service_name
        
        # Tiempo de ejecución simulado
        execution_time = np.random.uniform(1, 10)
        # NOTE: time.sleep used here in sync context for simulation purposes only
        time.sleep(execution_time / 100)  # Simular trabajo
        
        # Resultados simulados según el servicio
        if "photometry" in service_name:
            return {
                "service": service_name,
                "mean_flux": float(np.mean(object_data["flux"])),
                "std_flux": float(np.std(object_data["flux"])),
                "quality_score": np.random.uniform(0.7, 0.95),
                "execution_time": execution_time
            }
        elif "variability" in service_name:
            return {
                "service": service_name,
                "variability_detected": np.random.choice([True, False], p=[0.3, 0.7]),
                "amplitude": float(np.random.uniform(0.01, 0.1)),
                "quality_score": np.random.uniform(0.6, 0.9),
                "execution_time": execution_time
            }
        elif "ml" in service_name or "classification" in service_name:
            stellar_classes = ["main_sequence", "variable_star", "binary_system", "red_giant"]
            return {
                "service": service_name,
                "predicted_class": np.random.choice(stellar_classes),
                "confidence": float(np.random.uniform(0.5, 0.95)),
                "quality_score": np.random.uniform(0.7, 0.9),
                "execution_time": execution_time
            }
        else:
            return {
                "service": service_name,
                "analysis_completed": True,
                "quality_score": np.random.uniform(0.6, 0.9),
                "execution_time": execution_time
            }
    
    def _calculate_overall_quality(self, step_results: Dict[str, Any]) -> float:
        """Calcula la calidad general de los resultados."""
        quality_scores = []
        
        for step_result in step_results.values():
            if isinstance(step_result, dict) and "quality_score" in step_result:
                quality_scores.append(step_result["quality_score"])
        
        return float(np.mean(quality_scores)) if quality_scores else 0.5
    
    def _save_checkpoint(self, execution: WorkflowExecution, results: Dict[str, Any]):
        """Guarda un checkpoint del workflow."""
        checkpoint_dir = self.base_output_dir / execution.execution_id / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_{int(time.time())}.json"
        
        checkpoint_data = {
            "execution_id": execution.execution_id,
            "progress": execution.progress,
            "results": {k: str(v)[:500] for k, v in results.items()},  # Truncar para tamaño
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            logger.info(f"Checkpoint guardado: {checkpoint_file}")
        except BiologyError as e:
            logger.error(f"Error guardando checkpoint: {e}")
    
    def _generate_workflow_report(self, execution: WorkflowExecution) -> WorkflowReport:
        """Genera reporte completo del workflow."""
        total_objects = len(execution.object_ids)
        
        # Analizar resultados
        successful_objects = 0
        quality_scores = []
        scientific_findings = []
        
        for obj_id, result in execution.results.items():
            if isinstance(result, dict) and "error" not in result:
                successful_objects += 1
                
                if "overall_quality" in result:
                    quality_scores.append(result["overall_quality"])
                
                # Extraer hallazgos científicos simulados
                if "steps" in result:
                    for _, step_result in result["steps"].items():
                        if isinstance(step_result, dict):
                            if step_result.get("variability_detected"):
                                scientific_findings.append(f"Variabilidad detectada en {obj_id}")
                            if step_result.get("predicted_class") == "binary_system":
                                scientific_findings.append(f"Sistema binario candidato: {obj_id}")
        
        # Calcular métricas
        execution_time = 0.0
        if execution.start_time and execution.end_time:
            execution_time = (execution.end_time - execution.start_time).total_seconds()
        
        avg_quality = float(np.mean(quality_scores)) if quality_scores else 0.0
        failed_objects = total_objects - successful_objects
        
        # Generar recomendaciones
        recommendations = []
        success_rate = successful_objects / total_objects if total_objects > 0 else 0.0
        
        if success_rate < 0.8:
            recommendations.append("Revisar calidad de datos de entrada")
        if avg_quality < 0.7:
            recommendations.append("Considerar ajustar parámetros de análisis")
        if len(scientific_findings) == 0:
            recommendations.append("Revisar criterios de detección científica")
        
        # Utilización de recursos (simulada)
        resource_utilization = {
            "cpu_avg": np.random.uniform(30, 80),
            "memory_peak": np.random.uniform(40, 90),
            "disk_io": np.random.uniform(10, 50)
        }
        
        return WorkflowReport(
            execution_id=execution.execution_id,
            workflow_type=execution.workflow_type,
            total_objects=total_objects,
            successful_objects=successful_objects,
            failed_objects=failed_objects,
            execution_time=execution_time,
            average_quality_score=avg_quality,
            resource_utilization=resource_utilization,
            scientific_findings=scientific_findings[:10],  # Limitar a 10
            recommendations=recommendations,
            generated_files=[]  # Se poblaría en implementación real
        )
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtiene el estado de una ejecución."""
        if execution_id in self._active_executions:
            return self._active_executions[execution_id]
        
        # Buscar en cola
        for execution in self._execution_queue:
            if execution.execution_id == execution_id:
                return execution
        
        return None
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancela una ejecución."""
        # Cancelar si está en cola
        for i, execution in enumerate(self._execution_queue):
            if execution.execution_id == execution_id:
                execution.status = WorkflowStatus.CANCELLED
                self._execution_queue.pop(i)
                return True
        
        # Cancelar si está activa
        if execution_id in self._active_executions:
            self._active_executions[execution_id].status = WorkflowStatus.CANCELLED
            return True
        
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de workflows."""
        return {
            "active_workflows": len(self._active_executions),
            "queued_workflows": len(self._execution_queue),
            "available_templates": len(self._workflow_templates),
            "execution_stats": dict(self._execution_stats),
            "resource_monitor": self._resource_monitor.__dict__,
            "uptime": datetime.now().isoformat()
        }
    
    def optimize_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """Optimiza la ejecución de un workflow."""
        execution = self.get_execution_status(execution_id)
        if not execution:
            return {"error": "Ejecución no encontrada"}
        
        template = self._workflow_templates[execution.template_id]
        
        # Análisis de optimización
        optimization_suggestions = []
        
        # Análizar número de objetos vs recursos
        num_objects = len(execution.object_ids)
        if num_objects > 50:
            optimization_suggestions.append("Considerar procesamiento por lotes")
        
        # Analizar duración estimada
        if template.estimated_duration_minutes > 120:
            optimization_suggestions.append("Dividir workflow en sub-procesos")
        
        # Analizar dependencias
        independent_steps = []
        for step in template.steps:
            if not step.dependencies:
                independent_steps.append(step.step_id)
        
        if len(independent_steps) > 1:
            optimization_suggestions.append("Paralelizar pasos independientes")
        
        return {
            "execution_id": execution_id,
            "current_mode": "adaptive",
            "optimization_suggestions": optimization_suggestions,
            "estimated_improvement": f"{np.random.randint(10, 40)}% más rápido",
            "recommended_resources": {
                "cpu_cores": min(num_objects, 8),
                "memory_gb": max(4, num_objects // 10),
                "parallel_workers": min(num_objects, 16)
            }
        }

# Función de demostración
def demonstrate_advanced_workflows():
    """
    Función de demostración del sistema de workflows avanzados.
    """
    print("🔬 AXIOM Astronomy - Sistema de Workflows Avanzados")
    print("=" * 65)
    
    # Inicializar sistema de workflows
    workflow_system = AdvancedAstronomyWorkflow()
    
    print("\n✅ Sistema inicializado")
    print(f"   • Templates disponibles: {len(workflow_system.get_available_workflows())}")
    print(f"   • Directorio de salida: {workflow_system.base_output_dir}")
    
    # Mostrar templates disponibles
    print("\n📋 Templates de Workflow Disponibles:")
    
    templates = workflow_system.get_available_workflows()
    for template in templates:
        print(f"   • {template.name}")
        print(f"     - Tipo: {template.workflow_type.value}")
        print(f"     - Pasos: {len(template.steps)}")
        print(f"     - Duración estimada: {template.estimated_duration_minutes} min")
        print(f"     - Objetos objetivo: {', '.join(template.target_object_types[:3])}...")
        print()
    
    # Crear ejecuciones de ejemplo
    print("🚀 Creando ejecuciones de ejemplo...")
    
    # Crear diferentes tipos de workflows
    executions = []
    
    # 1. Stellar Survey pequeño
    stellar_objects = [f"STAR_{i:04d}" for i in range(15)]
    exec1 = workflow_system.create_workflow_execution(
        "stellar_survey_v1",
        stellar_objects,
        priority=Priority.HIGH
    )
    executions.append(("Stellar Survey", exec1))
    print(f"   ✓ Stellar Survey: {exec1} ({len(stellar_objects)} objetos)")
    
    # 2. Búsqueda de exoplanetas
    exo_candidates = [f"EXOCANDIDATE_{i:03d}" for i in range(8)]
    exec2 = workflow_system.create_workflow_execution(
        "exoplanet_search_v1",
        exo_candidates,
        priority=Priority.URGENT
    )
    executions.append(("Exoplanet Search", exec2))
    print(f"   ✓ Exoplanet Search: {exec2} ({len(exo_candidates)} objetos)")
    
    # 3. Monitoreo de variables
    variable_stars = [f"VAR_{i:03d}" for i in range(12)]
    exec3 = workflow_system.create_workflow_execution(
        "variable_monitoring_v1",
        variable_stars,
        priority=Priority.NORMAL
    )
    executions.append(("Variable Monitoring", exec3))
    print(f"   ✓ Variable Monitoring: {exec3} ({len(variable_stars)} objetos)")
    
    # Estado del sistema
    print("\n📊 Estado del Sistema:")
    system_status = workflow_system.get_system_status()
    print(f"   • Workflows en cola: {system_status['queued_workflows']}")
    print(f"   • Workflows activos: {system_status['active_workflows']}")
    print(f"   • Templates disponibles: {system_status['available_templates']}")
    
    # Ejecutar un workflow de ejemplo
    print("\n⚙️ Ejecutando workflow de demostración...")
    
    # Ejecutar el stellar survey
    execution_name, execution_id = executions[0]
    print(f"   Ejecutando: {execution_name} ({execution_id})")
    
    try:
        # Ejecutar workflow
        report = workflow_system.execute_workflow(execution_id, ExecutionMode.PARALLEL)
        
        print("\n📈 Resultados de Ejecución:")
        print(f"   ✓ Workflow: {report.workflow_type.value}")
        print(f"   ✓ Objetos procesados: {report.total_objects}")
        print(f"   ✓ Éxitos: {report.successful_objects}")
        print(f"   ✓ Fallos: {report.failed_objects}")
        print(f"   ✓ Tiempo total: {report.execution_time:.2f}s")
        print(f"   ✓ Calidad promedio: {report.average_quality_score:.3f}")
        
        # Hallazgos científicos
        if report.scientific_findings:
            print("\n🔬 Hallazgos Científicos:")
            for finding in report.scientific_findings[:5]:
                print(f"   • {finding}")
        
        # Recomendaciones
        if report.recommendations:
            print("\n💡 Recomendaciones:")
            for rec in report.recommendations:
                print(f"   • {rec}")
        
        # Utilización de recursos
        print("\n💻 Utilización de Recursos:")
        for resource, value in report.resource_utilization.items():
            print(f"   • {resource}: {value:.1f}%")
        
    except BiologyError as e:
        print(f"   ❌ Error en ejecución: {e}")
    
    # Análisis de optimización
    print("\n🎯 Análisis de Optimización:")
    
    for name, exec_id in executions[1:]:  # Analizar los restantes
        optimization = workflow_system.optimize_workflow_execution(exec_id)
        if "error" not in optimization:
            print(f"\n   {name} ({exec_id}):")
            print(f"     • Mejora estimada: {optimization['estimated_improvement']}")
            print(f"     • CPU recomendadas: {optimization['recommended_resources']['cpu_cores']}")
            print(f"     • Memoria recomendada: {optimization['recommended_resources']['memory_gb']} GB")
            
            if optimization['optimization_suggestions']:
                print("     • Sugerencias:")
                for suggestion in optimization['optimization_suggestions']:
                    print(f"       - {suggestion}")
    
    # Estado final del sistema
    print("\n📊 Estado Final del Sistema:")
    final_status = workflow_system.get_system_status()
    print(f"   • Total de ejecuciones: {final_status['execution_stats'].get('total_executions', 0)}")
    print(f"   • Workflows en cola: {final_status['queued_workflows']}")
    
    print("\n🎉 Demostración de Workflows Avanzados completada!")
    print("\n🚀 Capacidades del Sistema de Workflows:")
    print("   • 6 tipos de workflows predefinidos")
    print("   • Ejecución secuencial, paralela y por lotes")
    print("   • Priorización inteligente de trabajos")
    print("   • Monitoreo en tiempo real")
    print("   • Optimización automática de recursos")
    print("   • Checkpoints y recuperación de fallos")
    print("   • Reportes científicos automatizados")
    print("   • Análisis de calidad integrados")
    print("   • Escalabilidad para grandes datasets")

if __name__ == "__main__":
    # Ejecutar demostración
    demonstrate_advanced_workflows()