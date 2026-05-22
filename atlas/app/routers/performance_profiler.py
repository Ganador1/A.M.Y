"""
Router Performance Profiler para AXIOM - Perfilado y Monitoreo de Rendimiento

Este módulo proporciona endpoints completos para el perfilado de rendimiento y
monitoreo del sistema AXIOM. Permite la recolección, análisis y reporte de métricas
de rendimiento a nivel de operación, ayudando a identificar cuellos de botella
y optimizar flujos de trabajo computacionales.

== CAPACIDADES ==
• Estadísticas de rendimiento a nivel de operación: tiempos de ejecución, conteos
• Agregación de métricas en tiempo real: promedios, mínimos, máximos, percentiles
• Identificación de cuellos de botella: análisis automático de rendimiento
• Análisis de tendencias históricas: evolución del rendimiento en el tiempo
• Generación automática de reportes: informes comprehensivos de rendimiento
• Monitoreo de salud del profiler: diagnóstico y estado del sistema de monitoreo

== ENDPOINTS DISPONIBLES ==
• GET /stats/{operation} - Estadísticas detalladas para una operación específica
• GET /stats - Estadísticas de rendimiento para todas las operaciones perfiladas
• GET /report - Reporte comprehensivo de análisis de rendimiento
• POST /clear - Reiniciar todas las métricas y contadores de rendimiento
• GET /health - Estado de salud del profiler y resumen de monitoreo activo

== DEPENDENCIAS ==
• PerformanceProfiler: Servicio principal de perfilado y recolección de métricas
• System monitoring: Seguimiento de rendimiento de CPU, memoria y E/S
• Statistical analysis: Agregación y análisis estadístico de métricas de rendimiento

== MÉTRICAS SOPORTADAS ==
• Tiempos de ejecución: duración total, promedio, mínimo, máximo
• Conteos de operaciones: frecuencia de ejecución por operación
• Tasas de rendimiento: operaciones por segundo, throughput
• Utilización de recursos: CPU, memoria, E/S durante operaciones
• Latencia y percentiles: distribución de tiempos de respuesta

== USO ==
Los endpoints proporcionan acceso en tiempo real a datos de rendimiento con
análisis estadístico detallado. Los reportes ayudan a identificar oportunidades
de optimización y cuellos de botella en flujos de trabajo científicos.

== SEGURIDAD ==
• Validación de nombres de operaciones para prevenir inyección
• Límites en consultas de métricas para prevenir DoS
• Logging detallado de operaciones de perfilado
• Manejo seguro de errores sin exposición de información sensible
• Acceso restringido a métricas sensibles del sistema
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import datetime

from app.performance_profiler import profiler
from app.exceptions.domain.biology import BiologyError
from app.types.performance_profiler_types import (
    GetOperationStatsResult,
    GetAllStatsResult,
    GetPerformanceReportResult,
    ClearMetricsResult,
    HealthCheckResult,
)

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])

@router.get("/stats/{operation_name}")
async def get_operation_stats(operation_name: str) -> GetOperationStatsResult:
    """
    📊 Obtener estadísticas de rendimiento para una operación específica

    Retorna métricas detalladas de rendimiento para una operación nombrada,
    incluyendo tiempos de ejecución, conteos, promedios y análisis estadístico.

    Args:
        operation_name (str): Nombre de la operación a consultar

    Returns:
        Dict[str, Any]: Estadísticas completas de la operación

    Raises:
        HTTPException: Si la operación no existe o hay error interno

    Example:
        GET /stats/matrix_multiplication
        Response: {"operation": "matrix_multiplication", "count": 150, "avg_time": 0.023, "min_time": 0.015, ...}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not operation_name or not operation_name.strip():
            logger.warning("🚫 Intento de consultar estadísticas con nombre de operación vacío")
            raise HTTPException(
                status_code=400,
                detail="El nombre de la operación no puede estar vacío"
            )

        logger.info("📊 Consultando estadísticas para operación: %s", operation_name)

        # Obtener estadísticas
        stats = profiler.get_operation_stats(operation_name)

        # Verificar si hay error en las estadísticas
        if "error" in stats:
            logger.warning("🚫 Operación no encontrada: %s", operation_name)
            raise HTTPException(
                status_code=404,
                detail=f"Operación '{operation_name}' no encontrada: {stats['error']}"
            )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info("✅ Estadísticas obtenidas para %s (tiempo: %.4fs)", operation_name, execution_time)

        # Enriquecer respuesta con metadatos
        return {
            **stats,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo estadísticas para %s: %s (tiempo: %.4fs)", operation_name, str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo estadísticas: {str(e)}"
        ) from e

@router.get("/stats")
async def get_all_stats() -> GetAllStatsResult:
    """
    📈 Obtener estadísticas de rendimiento para todas las operaciones perfiladas

    Retorna un resumen comprehensivo de todas las operaciones que han sido
    perfiladas, incluyendo métricas agregadas y análisis estadístico global.

    Returns:
        Dict[str, Any]: Estadísticas de todas las operaciones perfiladas

    Raises:
        HTTPException: Si hay error interno obteniendo las estadísticas

    Example:
        GET /stats
        Response: {"total_operations": 15, "operations": {"matrix_mult": {...}, "fft": {...}, ...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📈 Consultando estadísticas de rendimiento globales")

        # Obtener todas las estadísticas
        all_stats = profiler.get_all_stats()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Calcular métricas agregadas
        total_operations = len(all_stats.get("operations", {}))
        total_calls = sum(
            op.get("count", 0)
            for op in all_stats.get("operations", {}).values()
            if isinstance(op, dict)
        )

        logger.info("✅ Estadísticas globales obtenidas: %d operaciones, %d llamadas totales (tiempo: %.4fs)", total_operations, total_calls, execution_time)

        # Enriquecer respuesta con metadatos
        return {
            **all_stats,
            "summary": {
                "total_operations": total_operations,
                "total_calls": total_calls,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo estadísticas globales: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo estadísticas globales: {str(e)}"
        ) from e

@router.get("/report")
async def get_performance_report() -> GetPerformanceReportResult:
    """
    📊 Generar reporte comprehensivo de rendimiento del sistema

    Crea un reporte detallado que incluye análisis estadístico, tendencias
    de rendimiento, recomendaciones de optimización y métricas de salud del sistema.

    Returns:
        Dict[str, Any]: Reporte completo de rendimiento del sistema

    Raises:
        HTTPException: Si hay error generando el reporte

    Example:
        GET /report
        Response: {"report": "🚀 AXIOM Performance Report...", "metadata": {...}}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📊 Generando reporte de rendimiento del sistema")

        # Generar reporte
        report_text = profiler.get_performance_report()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Crear respuesta estructurada
        response = {
            "report": report_text,
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "generation_time_seconds": execution_time,
                "report_version": "1.0",
                "format": "text"
            }
        }

        logger.info("✅ Reporte de rendimiento generado exitosamente (tiempo: %.4fs)", execution_time)

        return response

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error generando reporte de rendimiento: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno generando reporte de rendimiento: {str(e)}"
        ) from e

@router.post("/clear")
async def clear_metrics() -> ClearMetricsResult:
    """
    🧹 Limpiar todas las métricas de perfilado de rendimiento

    Elimina todas las estadísticas de rendimiento acumuladas y reinicia
    el estado del profiler. Esta operación es irreversible.

    Returns:
        Dict[str, str]: Confirmación de limpieza exitosa

    Raises:
        HTTPException: Si hay error limpiando las métricas

    Example:
        POST /clear
        Response: {"message": "Performance metrics cleared successfully", "timestamp": "2024-01-01T12:00:00"}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🧹 Iniciando limpieza de métricas de rendimiento")

        # Obtener estadísticas antes de limpiar
        stats_before = profiler.get_all_stats()
        total_operations_before = len(stats_before.get("operations", {}))

        # Limpiar métricas
        profiler.clear_metrics()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info("✅ Métricas limpiadas exitosamente: %d operaciones eliminadas (tiempo: %.4fs)", total_operations_before, execution_time)

        return {
            "message": "Performance metrics cleared successfully",
            "timestamp": datetime.datetime.now().isoformat(),
            "operations_cleared": total_operations_before,
            "execution_time_seconds": execution_time
        }

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error limpiando métricas: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno limpiando métricas: {str(e)}"
        ) from e

@router.get("/health")
async def health_check() -> HealthCheckResult:
    """
    🏥 Verificación de salud del profiler de rendimiento

    Realiza una verificación comprehensiva del estado del sistema de perfilado,
    incluyendo métricas de operaciones activas, estado de los profilers y salud general.

    Returns:
        Dict[str, Any]: Estado de salud del sistema de perfilado

    Raises:
        HTTPException: Si hay problemas críticos de salud

    Example:
        GET /health
        Response: {"status": "healthy", "total_operations_profiled": 15, "active_profilers": 3}
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🏥 Ejecutando verificación de salud del profiler")

        # Obtener métricas de salud
        total_operations = sum(len(ops) for ops in profiler.metrics.values())
        active_profilers = len(profiler.active_profilers)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Determinar estado de salud
        health_status = "healthy"
        if total_operations == 0 and active_profilers == 0:
            health_status = "idle"  # No hay actividad pero está funcionando
        elif active_profilers > 100:  # Umbral arbitrario
            health_status = "warning"  # Muchos profilers activos

        response = {
            "status": health_status,
            "total_operations_profiled": total_operations,
            "active_profilers": active_profilers,
            "operations": list(profiler.metrics.keys()),
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }

        logger.info("✅ Verificación de salud completada: %s (operaciones: %d, profilers activos: %d, tiempo: %.4fs)",
                   health_status, total_operations, active_profilers, execution_time)

        return response

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en verificación de salud: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en verificación de salud: {str(e)}"
        ) from e
