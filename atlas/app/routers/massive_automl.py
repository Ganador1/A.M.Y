"""
Router para AutoML Masivo con Evaluación de >1000 Modelos
========================================================

Router FastAPI que expone las capacidades de AutoML masivo para evaluación
distribuida de más de 1000 modelos de machine learning con optimización
automática de hiperparámetros y construcción de ensembles.

Características:
- Experimentos masivos con >1000 configuraciones de modelos
- Evaluación distribuida con Ray o multiprocessing
- Construcción automática de ensembles diversos
- Análisis comparativo de rendimiento por tipo de modelo
- Gestión de recursos con auto-scaling
- Monitoreo en tiempo real del progreso

Endpoints Principales:
- POST /initialize-cluster: Inicializar cluster Ray para computación distribuida
- POST /run-massive-experiment: Ejecutar experimento masivo de AutoML
- GET /experiment-status: Obtener estado de experimentos en curso
- GET /cluster-status: Información del cluster distribuido
- POST /shutdown-cluster: Cerrar cluster Ray

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import time
import asyncio
import numpy as np

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, field_validator

from app.routers.auth import require_scopes
from app.services.massive_automl_service import massive_automl_service, MassiveExperimentConfig
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.massive_automl_types import (
    HealthCheckResult,
)

router = APIRouter()


# ========== MODELOS DE REQUEST/RESPONSE ==========

class ClusterInitRequest(BaseModel):
    """Request para inicializar cluster Ray"""
    num_cpus: Optional[int] = Field(None, description="Número de CPUs a usar (None = auto)")
    num_gpus: Optional[int] = Field(0, description="Número de GPUs a usar")
    memory_limit_gb: Optional[int] = Field(4, ge=1, le=128, description="Límite de memoria en GB")
    auto_scaling: bool = Field(False, description="Habilitar auto-scaling del cluster")

class MassiveExperimentRequest(BaseModel):
    """Request para experimento masivo de AutoML"""
    # Dataset
    features: List[List[float]] = Field(..., description="Features del dataset (matriz X)")
    target: List[Union[int, float]] = Field(..., description="Variable objetivo (vector y)")
    task_type: str = Field(..., description="Tipo de tarea: 'classification' o 'regression'")
    
    # Configuración del experimento
    max_models: int = Field(1000, ge=100, le=10000, description="Número máximo de modelos a evaluar")
    time_budget_hours: float = Field(24.0, gt=0, le=168, description="Presupuesto de tiempo en horas")
    use_distributed: bool = Field(True, description="Usar evaluación distribuida con Ray")
    
    # Configuración de recursos
    max_concurrent_models: int = Field(50, ge=1, le=200, description="Modelos concurrentes máximos")
    memory_limit_mb: int = Field(8192, ge=1024, description="Límite de memoria por modelo en MB")
    
    # Configuración específica del dominio
    domain: str = Field("general", description="Dominio científico (physics, chemistry, biology, general)")
    
    # Ensemble
    ensemble_size: int = Field(10, ge=3, le=50, description="Tamaño del ensemble automático")
    diversity_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Umbral de diversidad del ensemble")
    
    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v):
        if v not in ['classification', 'regression']:
            raise ValueError('task_type debe ser "classification" o "regression"')
        return v
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if not v or not v[0]:
            raise ValueError('Features no pueden estar vacías')
        
        # Verificar que todas las filas tengan la misma longitud
        feature_length = len(v[0])
        for i, row in enumerate(v):
            if len(row) != feature_length:
                raise ValueError(f'Fila {i} tiene {len(row)} features, esperado {feature_length}')
        
        return v

class ExperimentStatusRequest(BaseModel):
    """Request para obtener estado de experimento"""
    experiment_id: Optional[str] = Field(None, description="ID del experimento específico")

class ClusterStatusResponse(BaseModel):
    """Response con estado del cluster"""
    cluster_active: bool = Field(..., description="Si el cluster está activo")
    num_nodes: int = Field(..., description="Número de nodos en el cluster")
    total_cpus: int = Field(..., description="CPUs totales disponibles")
    total_memory_gb: float = Field(..., description="Memoria total en GB")
    total_gpus: int = Field(..., description="GPUs totales disponibles")
    active_tasks: int = Field(..., description="Tareas actualmente ejecutándose")

class ExperimentSummaryResponse(BaseModel):
    """Response con resumen del experimento"""
    experiment_id: str = Field(..., description="ID único del experimento")
    status: str = Field(..., description="Estado del experimento")
    progress_percent: float = Field(..., description="Progreso del experimento (0-100)")
    
    # Resultados
    total_models_evaluated: int = Field(..., description="Modelos evaluados hasta ahora")
    successful_models: int = Field(..., description="Modelos exitosos")
    failed_models: int = Field(..., description="Modelos fallidos")
    
    # Mejor modelo encontrado
    best_model: Optional[Dict[str, Any]] = Field(None, description="Mejor modelo encontrado")
    best_score: Optional[float] = Field(None, description="Mejor score obtenido")
    
    # Tiempos
    elapsed_time_hours: float = Field(..., description="Tiempo transcurrido en horas")
    estimated_remaining_hours: Optional[float] = Field(None, description="Tiempo estimado restante")
    
    # Recursos
    resource_usage: Optional[Dict[str, Any]] = Field(None, description="Uso de recursos")

class MassiveExperimentResponse(BaseModel):
    """Response completa del experimento masivo"""
    experiment_id: str = Field(..., description="ID único del experimento")
    total_models_evaluated: int = Field(..., description="Total de modelos evaluados")
    successful_models: int = Field(..., description="Modelos entrenados exitosamente")
    failed_models: int = Field(..., description="Modelos que fallaron")
    total_time_hours: float = Field(..., description="Tiempo total del experimento")
    
    # Dataset info
    dataset_info: Dict[str, Any] = Field(..., description="Información del dataset")
    
    # Mejores resultados
    best_single_model: Dict[str, Any] = Field(..., description="Mejor modelo individual")
    top_models: List[Dict[str, Any]] = Field(..., description="Top 20 mejores modelos")
    
    # Ensemble
    ensemble_performance: Dict[str, Any] = Field(..., description="Performance del ensemble automático")
    
    # Análisis
    performance_analysis: Dict[str, Any] = Field(..., description="Análisis de performance por tipo de modelo")
    resource_usage: Dict[str, Any] = Field(..., description="Estadísticas de uso de recursos")


# ========== ENDPOINTS ==========

@router.post("/initialize-cluster", response_model=ClusterStatusResponse)
async def initialize_ray_cluster(
    request: ClusterInitRequest,
    current_user: dict = Depends(require_scopes(["automl:admin"]))
) -> ClusterStatusResponse:
    """
    🚀 INICIALIZAR CLUSTER RAY
    =========================
    
    Inicializa un cluster Ray para computación distribuida de AutoML masivo.
    
    El cluster permite evaluar miles de modelos en paralelo distribuyendo
    la carga computacional entre múltiples nodos y procesadores.
    
    Características:
    - Auto-detección de recursos disponibles
    - Configuración de límites de memoria y CPU
    - Auto-scaling opcional para cargas variables
    - Monitoreo de recursos en tiempo real
    """
    logger.info(f"🚀 Inicializando cluster Ray - Usuario: {current_user.get('sub')}")
    
    try:
        # Convertir memoria de GB a bytes
        memory_limit_bytes = request.memory_limit_gb * 1024 * 1024 * 1024 if request.memory_limit_gb else None
        
        cluster_info = await massive_automl_service.initialize_ray_cluster(
            num_cpus=request.num_cpus,
            num_gpus=request.num_gpus,
            memory_limit=memory_limit_bytes
        )
        
        logger.info(f"✅ Cluster Ray inicializado exitosamente")
        
        return ClusterStatusResponse(
            cluster_active=True,
            num_nodes=cluster_info.get("nodes", 1),
            total_cpus=int(cluster_info.get("cpus_total", 0)),
            total_memory_gb=cluster_info.get("memory_total", 0) / (1024**3),
            total_gpus=int(cluster_info.get("gpus_total", 0)),
            active_tasks=0
        )
        
    except BiologyError as e:
        logger.error(f"❌ Error inicializando cluster Ray: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inicializando cluster Ray: {str(e)}"
        )

@router.post("/run-massive-experiment", response_model=MassiveExperimentResponse)
async def run_massive_automl_experiment(
    request: MassiveExperimentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_scopes(["automl:experiment"]))
) -> MassiveExperimentResponse:
    """
    🧪 EXPERIMENTO MASIVO DE AUTOML
    ===============================
    
    Ejecuta un experimento masivo de AutoML evaluando >1000 modelos de ML
    con diferentes algoritmos, hiperparámetros y técnicas de preprocessing.
    
    El sistema automáticamente:
    - Genera configuraciones diversas de modelos
    - Evalúa modelos en paralelo/distribuido
    - Construye ensembles automáticos de los mejores modelos
    - Proporciona análisis comparativo detallado
    - Optimiza el uso de recursos computacionales
    
    Algoritmos incluidos:
    - Scikit-learn: RandomForest, XGBoost, SVM, etc.
    - Deep Learning: TensorFlow/Keras, PyTorch
    - AutoML: FLAML, AutoSklearn, Optuna
    - Ensemble methods: Voting, Stacking, Blending
    """
    logger.info(f"🧪 Iniciando experimento masivo AutoML - Usuario: {current_user.get('sub')}")
    logger.info(f"📊 Dataset: {len(request.features)} samples, {len(request.features[0])} features")
    logger.info(f"🎯 Tarea: {request.task_type}, Dominio: {request.domain}")
    logger.info(f"⚙️ Max modelos: {request.max_models}, Tiempo límite: {request.time_budget_hours}h")
    
    try:
        # Convertir datos a numpy arrays
        X = np.array(request.features, dtype=np.float32)
        y = np.array(request.target)
        
        # Validar dimensiones
        if len(X) != len(y):
            raise ValueError(f"Número de muestras no coincide: X={len(X)}, y={len(y)}")
        
        if len(X) < 10:
            raise ValueError("Se requieren al menos 10 muestras para el experimento")
        
        # Crear configuración del experimento
        experiment_config = MassiveExperimentConfig(
            max_models=request.max_models,
            time_budget_hours=request.time_budget_hours,
            n_jobs=-1,
            use_gpu=False,  # Por ahora sin GPU
            early_stopping_patience=50,
            diversity_threshold=request.diversity_threshold,
            ensemble_size=request.ensemble_size,
            resource_limits={
                "max_memory_mb": request.memory_limit_mb,
                "max_cpu_percent": 80,
                "max_models_concurrent": request.max_concurrent_models
            }
        )
        
        # Ejecutar experimento masivo
        start_time = time.time()
        
        experiment_results = await massive_automl_service.run_massive_automl_experiment(
            X=X,
            y=y,
            task_type=request.task_type,
            experiment_config=experiment_config,
            domain=request.domain
        )
        
        total_time = time.time() - start_time
        
        logger.info(f"✅ Experimento masivo completado en {total_time/3600:.2f} horas")
        logger.info(f"🏆 Mejor score: {experiment_results['best_single_model']['best_score']:.4f}")
        logger.info(f"📈 Modelos evaluados: {experiment_results['total_models_evaluated']}")
        
        return MassiveExperimentResponse(
            experiment_id=experiment_results["experiment_id"],
            total_models_evaluated=experiment_results["total_models_evaluated"],
            successful_models=experiment_results["successful_models"],
            failed_models=experiment_results["failed_models"],
            total_time_hours=experiment_results["total_time_hours"],
            dataset_info=experiment_results["data_info"],
            best_single_model=experiment_results["best_single_model"],
            top_models=experiment_results["top_models"],
            ensemble_performance=experiment_results["ensemble_performance"],
            performance_analysis=experiment_results["performance_analysis"],
            resource_usage=experiment_results["resource_usage"]
        )
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error en experimento masivo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en experimento masivo: {str(e)}"
        )

@router.get("/cluster-status", response_model=ClusterStatusResponse)
async def get_cluster_status(
    current_user: dict = Depends(require_scopes(["automl:read"]))
) -> ClusterStatusResponse:
    """
    📊 ESTADO DEL CLUSTER
    ====================
    
    Obtiene información en tiempo real del estado del cluster Ray,
    incluyendo recursos disponibles, tareas activas y utilización.
    """
    logger.info(f"📊 Consultando estado del cluster - Usuario: {current_user.get('sub')}")
    
    try:
        # Verificar si Ray está inicializado
        if not massive_automl_service.ray_initialized:
            return ClusterStatusResponse(
                cluster_active=False,
                num_nodes=0,
                total_cpus=0,
                total_memory_gb=0.0,
                total_gpus=0,
                active_tasks=0
            )
        
        # Obtener información del cluster (implementación simplificada)
        try:
            import ray
            if ray.is_initialized():
                cluster_resources = ray.cluster_resources()
                
                return ClusterStatusResponse(
                    cluster_active=True,
                    num_nodes=len(ray.nodes()),
                    total_cpus=int(cluster_resources.get("CPU", 0)),
                    total_memory_gb=cluster_resources.get("memory", 0) / (1024**3),
                    total_gpus=int(cluster_resources.get("GPU", 0)),
                    active_tasks=len(ray.active_tasks()) if hasattr(ray, 'active_tasks') else 0
                )
            else:
                return ClusterStatusResponse(
                    cluster_active=False,
                    num_nodes=0,
                    total_cpus=0,
                    total_memory_gb=0.0,
                    total_gpus=0,
                    active_tasks=0
                )
        except ImportError:
            return ClusterStatusResponse(
                cluster_active=False,
                num_nodes=0,
                total_cpus=0,
                total_memory_gb=0.0,
                total_gpus=0,
                active_tasks=0
            )
    
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo estado del cluster: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado del cluster: {str(e)}"
        )

@router.get("/service-stats")
async def get_service_statistics(
    current_user: dict = Depends(require_scopes(["automl:read"]))
) -> Dict[str, Any]:
    """
    📈 ESTADÍSTICAS DEL SERVICIO
    ============================
    
    Obtiene estadísticas acumuladas del servicio de AutoML masivo,
    incluyendo modelos evaluados, tiempo total de entrenamiento y performance.
    """
    logger.info(f"📈 Consultando estadísticas del servicio - Usuario: {current_user.get('sub')}")
    
    try:
        stats = massive_automl_service.stats.copy()
        
        # Agregar estadísticas adicionales
        stats.update({
            "service_uptime_hours": time.time() / 3600,  # Simplificación
            "success_rate": (
                stats["successful_models"] / (stats["successful_models"] + stats["failed_models"])
                if (stats["successful_models"] + stats["failed_models"]) > 0 else 0
            ),
            "avg_training_time_per_model": (
                stats["total_training_time"] / stats["models_evaluated"]
                if stats["models_evaluated"] > 0 else 0
            ),
            "frameworks_available": {
                "ray": massive_automl_service.ray_initialized,
                "sklearn": True,  # Asumimos que sklearn está disponible
                "xgboost": "XGBOOST_AVAILABLE" in globals(),
                "tensorflow": "TENSORFLOW_AVAILABLE" in globals(),
                "pytorch": "PYTORCH_AVAILABLE" in globals()
            }
        })
        
        return stats
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.post("/shutdown-cluster")
async def shutdown_ray_cluster(
    current_user: dict = Depends(require_scopes(["automl:admin"]))
) -> Dict[str, str]:
    """
    🔴 CERRAR CLUSTER RAY
    ====================
    
    Cierra el cluster Ray y libera todos los recursos computacionales.
    
    ⚠️ Advertencia: Esto detendrá todos los experimentos en curso.
    """
    logger.info(f"🔴 Cerrando cluster Ray - Usuario: {current_user.get('sub')}")
    
    try:
        await massive_automl_service.shutdown_ray_cluster()
        
        logger.info("✅ Cluster Ray cerrado exitosamente")
        
        return {
            "status": "success",
            "message": "Cluster Ray cerrado exitosamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error cerrando cluster Ray: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cerrando cluster Ray: {str(e)}"
        )

@router.get("/health")
async def health_check() -> HealthCheckResult:
    """
    💊 HEALTH CHECK
    ===============
    
    Verifica el estado de salud del servicio de AutoML masivo.
    """
    try:
        return {
            "status": "healthy",
            "service": "MassiveAutoML",
            "ray_available": massive_automl_service.ray_initialized,
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

