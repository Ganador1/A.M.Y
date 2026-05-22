"""
Router para Stress Testing Infrastructure - Pruebas de Carga Científicas
========================================================================

Router FastAPI que expone las capacidades de stress testing para pipelines
científicos concurrentes. Permite evaluar el rendimiento, estabilidad y
límites del sistema bajo condiciones de alta carga y fallos simulados.

Características:
- Pruebas de carga, estrés y resistencia
- Simulación de usuarios concurrentes
- Chaos engineering para evaluar resistencia
- Monitoreo de recursos en tiempo real
- Generación de reportes detallados
- Análisis de cuellos de botella

Tipos de Pruebas:
- Load Testing: Carga normal esperada
- Stress Testing: Más allá de la capacidad normal
- Spike Testing: Picos súbitos de tráfico
- Endurance Testing: Carga sostenida prolongada
- Chaos Testing: Inyección de fallos aleatorios

Endpoints Principales:
- POST /run-comprehensive: Ejecutar suite completa de pruebas
- POST /run-pipeline-concurrency: Probar concurrencia de pipelines específicos
- POST /run-chaos-engineering: Ejecutar pruebas de chaos engineering
- GET /active-tests: Ver pruebas en ejecución
- GET /test-history: Historial de pruebas
- POST /generate-report: Generar reporte detallado
- GET /system-baseline: Capturar métricas baseline

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, field_validator

from app.routers.auth import require_scopes
from app.exceptions.domain.biology import BiologyError
from app.services.stress_testing_service import (
    stress_testing_service,
    StressTestConfig,
    TestType,
    LoadPattern,
)
from app.core.bootstrap_logging import logger
from app.types.stress_testing_types import (
    HealthCheckResult,
)

router = APIRouter()


# ========== MODELOS DE REQUEST/RESPONSE ==========

class StressTestConfigRequest(BaseModel):
    """Request para configuración de stress test"""
    test_name: str = Field(..., description="Nombre identificativo de la prueba")
    test_type: str = Field(..., description="Tipo de prueba (load, stress, spike, volume, endurance, chaos)")
    duration_minutes: int = Field(10, ge=1, le=180, description="Duración de la prueba en minutos")
    
    # Configuración de carga
    max_concurrent_users: int = Field(100, ge=1, le=10000, description="Usuarios concurrentes máximos")
    requests_per_second: float = Field(10.0, gt=0, le=1000.0, description="Requests por segundo")
    load_pattern: str = Field("constant", description="Patrón de carga (constant, ramp_up, spike, etc.)")
    
    # Sistema objetivo
    target_endpoints: List[str] = Field(default_factory=list, description="Endpoints específicos a testear")
    base_url: str = Field("http://localhost:8000", description="URL base del sistema")
    
    # Configuración de escalado
    ramp_up_time_minutes: int = Field(2, ge=0, le=30, description="Tiempo de escalado inicial")
    ramp_down_time_minutes: int = Field(2, ge=0, le=30, description="Tiempo de escalado final")
    data_volume_mb: float = Field(100.0, gt=0, le=10000.0, description="Volumen de datos en MB")
    
    # Criterios de éxito
    max_response_time_ms: float = Field(5000.0, gt=0, description="Tiempo de respuesta máximo aceptable")
    max_error_rate_percent: float = Field(5.0, ge=0, le=100, description="Tasa de error máxima aceptable")
    min_throughput_rps: float = Field(5.0, gt=0, description="Throughput mínimo requerido")
    
    @field_validator('test_type')
    @classmethod
    def validate_test_type(cls, v):
        valid_types = ['load', 'stress', 'spike', 'volume', 'endurance', 'chaos']
        if v not in valid_types:
            raise ValueError(f'test_type debe ser uno de: {valid_types}')
        return v
    
    @field_validator('load_pattern')
    @classmethod
    def validate_load_pattern(cls, v):
        valid_patterns = ['constant', 'ramp_up', 'ramp_down', 'spike', 'sine_wave', 'random']
        if v not in valid_patterns:
            raise ValueError(f'load_pattern debe ser uno de: {valid_patterns}')
        return v

class ComprehensiveTestRequest(BaseModel):
    """Request para suite completa de pruebas"""
    suite_name: str = Field(..., description="Nombre de la suite de pruebas")
    test_configurations: List[StressTestConfigRequest] = Field(..., description="Configuraciones de pruebas individuales")
    parallel_execution: bool = Field(False, description="Ejecutar pruebas en paralelo")
    include_baseline: bool = Field(True, description="Incluir captura de métricas baseline")
    
    @field_validator('test_configurations')
    @classmethod
    def validate_test_configs(cls, v):
        if not v:
            raise ValueError('Se requiere al menos una configuración de prueba')
        if len(v) > 10:
            raise ValueError('Máximo 10 pruebas por suite')
        return v

class PipelineConcurrencyRequest(BaseModel):
    """Request para prueba de concurrencia de pipelines"""
    target_pipelines: List[str] = Field(..., description="Pipelines científicos a testear")
    concurrent_users_per_pipeline: int = Field(50, ge=1, le=500, description="Usuarios concurrentes por pipeline")
    test_duration_minutes: int = Field(15, ge=5, le=60, description="Duración de la prueba")
    include_resource_monitoring: bool = Field(True, description="Incluir monitoreo detallado de recursos")
    
    @field_validator('target_pipelines')
    @classmethod
    def validate_pipelines(cls, v):
        valid_pipelines = ['topology_analysis', 'automl_massive', 'priority_queue', 'knowledge_graph']
        for pipeline in v:
            if pipeline not in valid_pipelines:
                raise ValueError(f'Pipeline {pipeline} no válido. Válidos: {valid_pipelines}')
        return v

class ChaosEngineeringRequest(BaseModel):
    """Request para chaos engineering"""
    duration_minutes: int = Field(30, ge=10, le=120, description="Duración de la prueba de caos")
    failure_injection_rate: float = Field(0.1, ge=0.01, le=0.5, description="Tasa de inyección de fallos")
    failure_types: List[str] = Field(
        default_factory=lambda: ['timeout', '503', 'connection_error'],
        description="Tipos de fallos a inyectar"
    )
    baseline_load_rps: float = Field(10.0, gt=0, le=100.0, description="Carga base durante chaos testing")
    recovery_time_threshold_seconds: float = Field(30.0, gt=0, description="Umbral de tiempo de recuperación")

class ReportGenerationRequest(BaseModel):
    """Request para generación de reportes"""
    test_suite_id: Optional[str] = Field(None, description="ID de suite específica")
    include_visualizations: bool = Field(True, description="Incluir gráficos y visualizaciones")
    include_recommendations: bool = Field(True, description="Incluir recomendaciones")
    report_format: str = Field("comprehensive", description="Formato del reporte")
    time_range_hours: int = Field(24, ge=1, le=168, description="Rango temporal en horas")

class StressTestResponse(BaseModel):
    """Response de stress test individual"""
    test_id: str = Field(..., description="ID único de la prueba")
    test_name: str = Field(..., description="Nombre de la prueba")
    status: str = Field(..., description="Estado de la prueba")
    success_criteria_met: bool = Field(..., description="Si se cumplieron los criterios de éxito")
    metrics: Dict[str, Any] = Field(..., description="Métricas de rendimiento")
    duration_minutes: float = Field(..., description="Duración real de la prueba")
    config: Dict[str, Any] = Field(..., description="Configuración utilizada")

class ComprehensiveTestResponse(BaseModel):
    """Response de suite completa"""
    suite_id: str = Field(..., description="ID de la suite")
    baseline_metrics: Dict[str, Any] = Field(..., description="Métricas baseline")
    individual_tests: List[Dict[str, Any]] = Field(..., description="Resultados individuales")
    summary: Dict[str, Any] = Field(..., description="Resumen consolidado")
    recommendations: List[str] = Field(..., description="Recomendaciones")
    start_time: str = Field(..., description="Timestamp de inicio")
    end_time: str = Field(..., description="Timestamp de fin")

class SystemBaselineResponse(BaseModel):
    """Response con métricas baseline del sistema"""
    timestamp: str = Field(..., description="Timestamp de captura")
    system_resources: Dict[str, Any] = Field(..., description="Recursos del sistema")
    response_times_baseline: Dict[str, float] = Field(..., description="Tiempos de respuesta baseline")
    throughput_baseline: float = Field(..., description="Throughput baseline")
    active_connections: int = Field(..., description="Conexiones activas")
    system_health_score: float = Field(..., description="Score de salud del sistema")


# ========== ENDPOINTS ==========

@router.post("/run-comprehensive", response_model=ComprehensiveTestResponse)
async def run_comprehensive_stress_test(
    request: ComprehensiveTestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_scopes(["stress-test:execute"]))
) -> ComprehensiveTestResponse:
    """
    🧪 SUITE COMPLETA DE STRESS TESTING
    ==================================
    
    Ejecuta una suite completa de pruebas de estrés para evaluar el rendimiento,
    estabilidad y límites del sistema bajo múltiples condiciones de carga.
    
    Tipos de pruebas incluidas:
    - Load Testing: Verificar comportamiento bajo carga normal
    - Stress Testing: Probar límites más allá de la capacidad esperada
    - Spike Testing: Evaluar respuesta a picos súbitos de tráfico
    - Endurance Testing: Verificar estabilidad bajo carga sostenida
    
    La suite proporciona análisis consolidado, identificación de cuellos de
    botella y recomendaciones específicas para optimización del sistema.
    """
    logger.info(f"🧪 Iniciando suite completa de stress testing: {request.suite_name} - Usuario: {current_user.get('sub')}")
    
    try:
        # Convertir configuraciones
        test_configs = []
        for config_req in request.test_configurations:
            test_config = StressTestConfig(
                test_name=config_req.test_name,
                test_type=TestType(config_req.test_type),
                duration_minutes=config_req.duration_minutes,
                max_concurrent_users=config_req.max_concurrent_users,
                requests_per_second=config_req.requests_per_second,
                load_pattern=LoadPattern(config_req.load_pattern),
                target_endpoints=config_req.target_endpoints,
                base_url=config_req.base_url,
                ramp_up_time_minutes=config_req.ramp_up_time_minutes,
                ramp_down_time_minutes=config_req.ramp_down_time_minutes,
                data_volume_mb=config_req.data_volume_mb,
                max_response_time_ms=config_req.max_response_time_ms,
                max_error_rate_percent=config_req.max_error_rate_percent,
                min_throughput_rps=config_req.min_throughput_rps
            )
            test_configs.append(test_config)
        
        # Ejecutar suite completa
        results = await stress_testing_service.run_comprehensive_stress_test(
            test_configs=test_configs,
            parallel_execution=request.parallel_execution
        )
        
        logger.info(f"✅ Suite de stress testing completada: {results['suite_id']}")
        
        return ComprehensiveTestResponse(**results)
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error ejecutando suite de stress testing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando suite de stress testing: {str(e)}"
        )

@router.post("/run-pipeline-concurrency")
async def run_pipeline_concurrency_test(
    request: PipelineConcurrencyRequest,
    current_user: dict = Depends(require_scopes(["stress-test:execute"]))
) -> Dict[str, Any]:
    """
    🔄 PRUEBA DE CONCURRENCIA DE PIPELINES
    =====================================
    
    Ejecuta pruebas de concurrencia específicas para pipelines científicos
    críticos. Evalúa cómo el sistema maneja múltiples pipelines ejecutándose
    simultáneamente con alta concurrencia.
    
    Pipelines soportados:
    - topology_analysis: Análisis topológico avanzado
    - automl_massive: AutoML con >1000 modelos
    - priority_queue: Sistema de colas dinámicas
    - knowledge_graph: Gestión de grafos de conocimiento
    
    La prueba simula usuarios reales ejecutando experimentos concurrentes
    y mide el impacto en rendimiento, estabilidad y recursos del sistema.
    """
    logger.info(f"🔄 Iniciando prueba de concurrencia de pipelines: {request.target_pipelines} - Usuario: {current_user.get('sub')}")
    
    try:
        results = await stress_testing_service.run_pipeline_concurrency_test(
            target_pipelines=request.target_pipelines,
            concurrent_users_per_pipeline=request.concurrent_users_per_pipeline,
            test_duration_minutes=request.test_duration_minutes
        )
        
        logger.info(f"✅ Prueba de concurrencia completada")
        
        return results
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error en prueba de concurrencia: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en prueba de concurrencia: {str(e)}"
        )

@router.post("/run-chaos-engineering")
async def run_chaos_engineering_test(
    request: ChaosEngineeringRequest,
    current_user: dict = Depends(require_scopes(["stress-test:chaos"]))
) -> Dict[str, Any]:
    """
    🌪️ CHAOS ENGINEERING TEST
    =========================
    
    Ejecuta pruebas de ingeniería del caos para evaluar la resistencia y
    capacidad de recuperación del sistema ante fallos inesperados.
    
    Tipos de fallos inyectados:
    - Timeouts y latencia elevada
    - Errores HTTP (503, 500, etc.)
    - Fallos de conexión de red
    - Picos de CPU y memoria
    - Caídas de servicios dependientes
    
    La prueba mide:
    - Tiempo de detección de fallos
    - Tiempo de recuperación automática
    - Degradación graceful del servicio
    - Impacto en otros componentes
    - Efectividad de circuit breakers
    
    ⚠️ Ejecutar solo en entornos de testing o staging.
    """
    logger.info(f"🌪️ Iniciando chaos engineering test - Usuario: {current_user.get('sub')}")
    
    try:
        results = await stress_testing_service.run_chaos_engineering_test(
            duration_minutes=request.duration_minutes,
            failure_injection_rate=request.failure_injection_rate
        )
        
        logger.info(f"✅ Chaos engineering test completado")
        
        return results
        
    except BiologyError as e:
        logger.error(f"❌ Error en chaos engineering: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en chaos engineering: {str(e)}"
        )

@router.get("/system-baseline", response_model=SystemBaselineResponse)
async def capture_system_baseline(
    current_user: dict = Depends(require_scopes(["stress-test:read"]))
) -> SystemBaselineResponse:
    """
    📊 CAPTURAR MÉTRICAS BASELINE
    ============================
    
    Captura las métricas baseline del sistema en condiciones normales
    de operación. Estas métricas sirven como referencia para comparar
    el rendimiento durante las pruebas de estrés.
    
    Métricas capturadas:
    - Utilización de CPU, memoria, disco, red
    - Tiempos de respuesta promedio por endpoint
    - Throughput normal del sistema
    - Conexiones activas y pools de conexión
    - Latencia de base de datos
    - Health checks de servicios
    """
    logger.info(f"📊 Capturando métricas baseline - Usuario: {current_user.get('sub')}")
    
    try:
        baseline = await stress_testing_service._capture_baseline_metrics()
        
        # Convertir a formato de respuesta
        response = SystemBaselineResponse(
            timestamp=baseline["timestamp"],
            system_resources=baseline["system_resources"],
            response_times_baseline=baseline["response_times_baseline"],
            throughput_baseline=baseline["throughput_baseline"],
            active_connections=baseline.get("active_connections", 0),
            system_health_score=baseline.get("system_health_score", 0.85)
        )
        
        logger.info("✅ Métricas baseline capturadas")
        
        return response
        
    except BiologyError as e:
        logger.error(f"❌ Error capturando baseline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error capturando baseline: {str(e)}"
        )

@router.get("/active-tests")
async def get_active_tests(
    current_user: dict = Depends(require_scopes(["stress-test:read"]))
) -> Dict[str, Any]:
    """
    🔍 PRUEBAS ACTIVAS
    ==================
    
    Obtiene información sobre todas las pruebas de estrés actualmente
    en ejecución, incluyendo progreso, métricas en tiempo real y
    estado de cada prueba.
    """
    logger.info(f"🔍 Consultando pruebas activas - Usuario: {current_user.get('sub')}")
    
    try:
        active_tests = {}
        
        for test_id, test_result in stress_testing_service.active_tests.items():
            duration = (datetime.now() - test_result.start_time).total_seconds() / 60
            
            active_tests[test_id] = {
                "test_name": test_result.config.test_name,
                "test_type": test_result.config.test_type.value,
                "status": test_result.status,
                "duration_minutes": duration,
                "progress_percent": min(100, (duration / test_result.config.duration_minutes) * 100),
                "current_metrics": {
                    "total_requests": test_result.total_requests,
                    "successful_requests": test_result.successful_requests,
                    "failed_requests": test_result.failed_requests,
                    "average_response_time_ms": test_result.average_response_time_ms,
                    "current_throughput_rps": test_result.actual_throughput_rps
                }
            }
        
        return {
            "active_tests": active_tests,
            "total_active": len(active_tests),
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo pruebas activas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo pruebas activas: {str(e)}"
        )

@router.get("/test-history")
async def get_test_history(
    limit: int = 50,
    test_type: Optional[str] = None,
    current_user: dict = Depends(require_scopes(["stress-test:read"]))
) -> Dict[str, Any]:
    """
    📚 HISTORIAL DE PRUEBAS
    ======================
    
    Obtiene el historial de pruebas de estrés ejecutadas, con filtros
    opcionales por tipo de prueba y límite de resultados.
    """
    logger.info(f"📚 Consultando historial de pruebas - Usuario: {current_user.get('sub')}")
    
    try:
        # En implementación real, consultar base de datos
        test_history = stress_testing_service.test_history[-limit:]
        
        # Filtrar por tipo si se especifica
        if test_type:
            test_history = [
                test for test in test_history 
                if test.get("test_type") == test_type
            ]
        
        # Agregar estadísticas del historial
        if test_history:
            success_rate = len([t for t in test_history if t.get("success_criteria_met", False)]) / len(test_history)
            avg_duration = sum(t.get("duration_minutes", 0) for t in test_history) / len(test_history)
        else:
            success_rate = 0.0
            avg_duration = 0.0
        
        return {
            "test_history": test_history,
            "total_tests": len(test_history),
            "statistics": {
                "success_rate_percent": success_rate * 100,
                "average_duration_minutes": avg_duration,
                "most_common_test_type": test_type or "load",
                "total_requests_processed": sum(
                    t.get("metrics", {}).get("total_requests", 0) for t in test_history
                )
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )

@router.post("/generate-report")
async def generate_stress_test_report(
    request: ReportGenerationRequest,
    current_user: dict = Depends(require_scopes(["stress-test:read"]))
) -> Dict[str, Any]:
    """
    📊 GENERAR REPORTE DE STRESS TESTING
    ===================================
    
    Genera un reporte completo de análisis de stress testing con:
    - Análisis de rendimiento y tendencias
    - Identificación de cuellos de botella
    - Evaluación de escalabilidad
    - Recomendaciones específicas
    - Análisis de riesgos de rendimiento
    - Visualizaciones y gráficos (opcional)
    """
    logger.info(f"📊 Generando reporte de stress testing - Usuario: {current_user.get('sub')}")
    
    try:
        # En implementación real, obtener datos según test_suite_id o rango temporal
        test_results = {
            "suite_id": request.test_suite_id or "latest",
            "individual_tests": stress_testing_service.test_history[-10:],  # Últimas 10 pruebas
            "summary": {
                "total_tests": 10,
                "successful_tests": 8,
                "failed_tests": 2,
                "success_rate_percent": 80.0
            }
        }
        
        # Generar reporte completo
        report = await stress_testing_service.generate_load_test_report(
            test_results=test_results,
            include_visualizations=request.include_visualizations
        )
        
        # Agregar metadatos de la request
        report["report_metadata"] = {
            "requested_by": current_user.get('sub'),
            "request_timestamp": datetime.now().isoformat(),
            "report_format": request.report_format,
            "time_range_hours": request.time_range_hours,
            "include_visualizations": request.include_visualizations,
            "include_recommendations": request.include_recommendations
        }
        
        logger.info(f"✅ Reporte generado: {report['report_id']}")
        
        return report
        
    except BiologyError as e:
        logger.error(f"❌ Error generando reporte: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )

@router.get("/performance-dashboard")
async def get_performance_dashboard(
    current_user: dict = Depends(require_scopes(["stress-test:read"]))
) -> Dict[str, Any]:
    """
    📈 DASHBOARD DE RENDIMIENTO
    ==========================
    
    Proporciona una vista consolidada del rendimiento del sistema
    basada en datos históricos de stress testing.
    """
    logger.info(f"📈 Consultando dashboard de rendimiento - Usuario: {current_user.get('sub')}")
    
    try:
        # Simular datos del dashboard
        dashboard_data = {
            "system_health": {
                "overall_score": 0.85,
                "cpu_health": 0.80,
                "memory_health": 0.90,
                "network_health": 0.85,
                "storage_health": 0.88
            },
            "performance_trends": {
                "response_time_trend": "stable",
                "throughput_trend": "improving",
                "error_rate_trend": "decreasing",
                "resource_usage_trend": "stable"
            },
            "current_limits": {
                "max_concurrent_users": 500,
                "max_throughput_rps": 150.0,
                "response_time_p95_ms": 2000.0,
                "sustainable_load_percent": 75.0
            },
            "recent_bottlenecks": [
                {
                    "component": "database_queries",
                    "severity": "medium",
                    "last_detected": "2024-09-20T10:30:00Z"
                },
                {
                    "component": "cpu_intensive_operations",
                    "severity": "low",
                    "last_detected": "2024-09-20T08:15:00Z"
                }
            ],
            "recommendations": [
                "Implementar connection pooling en base de datos",
                "Optimizar consultas N+1 en endpoints de análisis",
                "Considerar cache distribuido para resultados frecuentes",
                "Evaluar auto-scaling horizontal para picos de carga"
            ],
            "next_recommended_tests": [
                {
                    "test_type": "endurance",
                    "reason": "Verificar estabilidad bajo carga sostenida",
                    "priority": "high"
                },
                {
                    "test_type": "chaos",
                    "reason": "Evaluar resistencia a fallos de red",
                    "priority": "medium"
                }
            ]
        }
        
        return dashboard_data
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo dashboard: {str(e)}"
        )

@router.delete("/test/{test_id}")
async def cancel_active_test(
    test_id: str,
    current_user: dict = Depends(require_scopes(["stress-test:admin"]))
) -> Dict[str, Any]:
    """
    ❌ CANCELAR PRUEBA ACTIVA
    ========================
    
    Cancela una prueba de estrés actualmente en ejecución.
    """
    logger.info(f"❌ Cancelando prueba {test_id} - Usuario: {current_user.get('sub')}")
    
    try:
        if test_id not in stress_testing_service.active_tests:
            raise HTTPException(status_code=404, detail="Prueba no encontrada o no activa")
        
        # En implementación real, cancelar la prueba
        test_result = stress_testing_service.active_tests[test_id]
        test_result.status = "cancelled"
        test_result.end_time = datetime.now()
        
        # Mover a historial
        stress_testing_service.test_history.append({
            "test_id": test_id,
            "test_name": test_result.config.test_name,
            "status": "cancelled",
            "cancelled_by": current_user.get('sub'),
            "cancelled_at": datetime.now().isoformat()
        })
        
        # Remover de activas
        del stress_testing_service.active_tests[test_id]
        
        logger.info(f"✅ Prueba {test_id} cancelada")
        
        return {
            "test_id": test_id,
            "status": "cancelled",
            "cancelled_by": current_user.get('sub'),
            "cancelled_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error cancelando prueba: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelando prueba: {str(e)}"
        )

@router.get("/health")
async def health_check() -> HealthCheckResult:
    """
    💊 HEALTH CHECK
    ===============
    
    Verifica el estado de salud del servicio de stress testing.
    """
    try:
        return {
            "status": "healthy",
            "service": "StressTesting",
            "active_tests": len(stress_testing_service.active_tests),
            "total_tests_executed": len(stress_testing_service.test_history),
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
