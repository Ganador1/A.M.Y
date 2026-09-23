"""
🔄 Router de Reproducibilidad Científica - AXIOM v4.1

Este módulo proporciona endpoints comprehensivos para la reproducibilidad de experimentos
científicos, permitiendo crear paquetes autocontenidos que incluyen todo lo necesario
para replicar experimentos completos con código, datos, dependencias y entorno.

Características principales:
- Generación de paquetes reproducibles en formato ZIP con estado completo del experimento
- Captura automática de código, datos, configuración y metadatos del experimento
- Inclusión configurable de artefactos con límites de tamaño personalizables
- Limpieza automática de paquetes antiguos para gestión eficiente del almacenamiento
- Integración completa con sistemas de seguimiento de experimentos y versionado de datos

Endpoints disponibles:
- POST /export-package: Genera paquete ZIP reproducible para experimentos
- POST /cleanup: Elimina paquetes antiguos de reproducibilidad para gestión de almacenamiento

Consideraciones de seguridad:
- Autenticación requerida mediante Bearer token para todas las operaciones
- Validación estricta de parámetros de entrada para prevenir errores de configuración
- Manejo seguro de errores sin exposición de información sensible del sistema
- Control de acceso a datos experimentales confidenciales

Dependencias:
- ReproducibilityService: Servicio principal de generación de paquetes reproducibles
- ExperimentTrackingService: Captura de metadatos y estado de experimentos
- DataVersioningService: Versionado de datasets y gestión de artefactos
- require_bearer: Autenticación JWT para operaciones seguras

Consideraciones técnicas:
- Los paquetes incluyen snapshots completos del entorno de ejecución
- Soporte para múltiples formatos de datos y tipos de artefactos
- Optimización automática del tamaño de paquetes mediante deduplicación
- Metadata enriquecida para trazabilidad completa del experimento

Ejemplo de uso:
    POST /export-package
    {
        "experiment_id": "exp_2024_001",
        "include_artifacts": true,
        "max_artifact_bytes": 10485760
    }

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import logging
import datetime

from app.security import require_bearer
from app.services.reproducibility import ReproducibilityService
# Reusar instancias compartidas para mantener estado en memoria
from app.routers.experiment_tracking import experiment_service
from app.routers.data_versioning import data_versioning_service
from app.exceptions.domain.biology import BiologyError

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_bearer)])
repro_service = ReproducibilityService()


@router.post("/export-package")
async def export_reproducible_package(request: Dict[str, Any]):
    """
    📦 Genera un paquete reproducible para un experimento científico

    Crea un paquete ZIP autocontenido que incluye todo lo necesario para replicar
    completamente un experimento: código, datos, configuración, dependencias y metadatos.

    Args:
        request: Diccionario con parámetros de configuración del paquete

    Returns:
        Dict[str, Any]: Resultado de la exportación con información del paquete generado

    Raises:
        HTTPException: Si hay error en la generación o parámetros inválidos

    Example:
        POST /export-package
        {
            "experiment_id": "exp_2024_001",
            "include_artifacts": true,
            "max_artifact_bytes": 10485760,
            "retention_max_bundles": 5
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        experiment_id = request.get("experiment_id")
        if not experiment_id or not isinstance(experiment_id, str) or not experiment_id.strip():
            logger.warning("🚫 Solicitud de exportación sin experiment_id válido")
            raise HTTPException(
                status_code=400,
                detail="experiment_id es requerido y debe ser una cadena no vacía"
            )

        include_artifacts = bool(request.get("include_artifacts", False))
        max_bytes = int(request.get("max_artifact_bytes", 5 * 1024 * 1024))

        if max_bytes <= 0 or max_bytes > 100 * 1024 * 1024:  # Máximo 100MB
            logger.warning("🚫 Límite de bytes de artefactos fuera de rango: %d", max_bytes)
            raise HTTPException(
                status_code=400,
                detail="max_artifact_bytes debe estar entre 1 y 100MB"
            )

        logger.info("📦 Iniciando exportación de paquete reproducible para experimento: %s (artefactos: %s, límite: %d bytes)",
                   experiment_id, include_artifacts, max_bytes)

        # Generar paquete reproducible
        result = repro_service.create_reproducible_package(
            experiment_service=experiment_service,
            data_versioning_service=data_versioning_service,
            experiment_id=experiment_id,
            include_artifacts=include_artifacts,
            max_artifact_bytes=max_bytes,
            retention_max_bundles=request.get("retention_max_bundles"),
        )

        if not result.get("success"):
            logger.error("❌ Error en generación de paquete reproducible: %s", result.get("error", "Error desconocido"))
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Exportación fallida")
            )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        result["metadata"] = {
            "experiment_id": experiment_id,
            "include_artifacts": include_artifacts,
            "max_artifact_bytes": max_bytes,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "export_type": "reproducible_package"
        }

        logger.info("✅ Paquete reproducible generado exitosamente para experimento %s (tiempo: %.4fs)",
                   experiment_id, execution_time)

        return result

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en exportación de paquete: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en exportación: {str(e)}"
        ) from e


@router.post("/cleanup")
async def cleanup_exports(request: Dict[str, Any]):
    """
    🧹 Elimina paquetes antiguos de reproducibilidad para gestión de almacenamiento

    Realiza limpieza automática de bundles ZIP antiguos, manteniendo solo los más
    recientes según la configuración especificada para optimizar el uso del almacenamiento.

    Args:
        request: Diccionario con parámetros de configuración de limpieza

    Returns:
        Dict[str, Any]: Resultado de la operación de limpieza con estadísticas

    Raises:
        HTTPException: Si hay error en la limpieza o parámetros inválidos

    Example:
        POST /cleanup
        {
            "max_bundles": 10
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        max_bundles = int(request.get("max_bundles", 10))

        if max_bundles <= 0 or max_bundles > 1000:
            logger.warning("🚫 Número máximo de bundles fuera de rango: %d", max_bundles)
            raise HTTPException(
                status_code=400,
                detail="max_bundles debe estar entre 1 y 1000"
            )

        logger.info("🧹 Iniciando limpieza de paquetes antiguos, manteniendo máximo %d bundles", max_bundles)

        # Ejecutar limpieza
        res = await repro_service.process_request({
            "action": "cleanup_exports",
            "max_bundles": max_bundles,
        })

        if not res.get("success"):
            logger.error("❌ Error en limpieza de paquetes: %s", res.get("error", "Error desconocido"))
            raise HTTPException(
                status_code=400,
                detail=res.get("error", "Limpieza fallida")
            )

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        res["metadata"] = {
            "max_bundles_retained": max_bundles,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "cleanup_type": "reproducibility_packages"
        }

        logger.info("✅ Limpieza de paquetes completada: mantenidos %d bundles más recientes (tiempo: %.4fs)",
                   max_bundles, execution_time)

        return res

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en limpieza de paquetes: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en limpieza: {str(e)}"
        ) from e
