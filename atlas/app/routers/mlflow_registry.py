"""
Router MLflow Registry para AXIOM - Gestión Avanzada de Modelos

Este módulo proporciona endpoints completos para la gestión profesional de modelos
de machine learning utilizando MLflow Model Registry, incluyendo versionado,
stages de deployment, búsqueda avanzada y administración de metadatos.

== CAPACIDADES ==
• Registro y versionado automático de modelos ML
• Gestión de stages de deployment (None, Staging, Production, Archived)
• Búsqueda avanzada con filtros y ordenamiento
• Sistema de tags y metadatos para modelos
• Estadísticas y monitoreo del registry
• Integración completa con MLflow Tracking
• API REST completa para operaciones CRUD

== ENDPOINTS DISPONIBLES ==
• POST /register - Registrar nuevo modelo en el registry
• GET /models - Listar todos los modelos registrados
• GET /models/{name}/versions/{version} - Obtener versión específica
• GET /models/{name}/latest-versions - Últimas versiones por stage
• POST /models/transition-stage - Promover modelo entre stages
• PUT /models/update-version - Actualizar metadatos de versión
• POST /models/search - Búsqueda avanzada de versiones
• GET /models/{name}/versions/{version}/download-uri - URI de descarga
• POST /models/tags - Establecer tags en versiones
• DELETE /models/{name}/versions/{version}/tags/{key} - Eliminar tags
• GET /stats - Estadísticas del registry
• GET /health - Estado de salud del servicio
• POST /demo - Demostración de funcionalidades

== DEPENDENCIAS ==
• MLflowRegistryService: Servicio principal de gestión del registry
• mlflow: Framework de experiment tracking y model registry
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos
• app.security: Sistema de autenticación y autorización

== USO ==
Este router se integra con el sistema de experiment tracking existente para
proporcionar un flujo completo desde el desarrollo hasta el deployment de modelos,
con control de versiones, stages y metadatos comprehensivos.

== SEGURIDAD ==
• Control de acceso basado en scopes (mlflow:read, mlflow:write, mlflow:admin)
• Validación estricta de entradas y parámetros
• Logging detallado de todas las operaciones
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para endpoints de escritura
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.mlflow_registry_service import MLflowRegistryService
from app.security import require_scopes
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError


class _DisabledMLflowRegistryService:
    """Fallback cuando mlflow no está disponible."""

    def __init__(self, error_message: str):
        self._error_message = error_message
        self.tracking_uri: Optional[str] = None

    async def process_request(self, request_data: Dict) -> Dict:
        return {"success": False, "error": self._error_message}

    def get_registry_stats(self) -> Dict:
        return {"success": False, "error": self._error_message}


router = APIRouter()

try:
    registry_service = MLflowRegistryService()
    _registry_service_error: Optional[str] = None
except RuntimeError as exc:  # mlflow no disponible
    error_message = str(exc)
    logger.warning("MLflow Registry Service disabled: %s", error_message)
    registry_service = _DisabledMLflowRegistryService(error_message)
    _registry_service_error = error_message


# Modelos Pydantic para requests
class RegisterModelRequest(BaseModel):
    model_uri: str
    name: str
    description: Optional[str] = None
    tags: Dict[str, str] = {}


class TransitionStageRequest(BaseModel):
    name: str
    version: str
    stage: str
    archive_existing_versions: bool = False


class UpdateModelVersionRequest(BaseModel):
    name: str
    version: str
    description: Optional[str] = None


class SetTagRequest(BaseModel):
    name: str
    version: str
    key: str
    value: str


class SearchRequest(BaseModel):
    filter: str = ""
    max_results: int = 100
    order_by: List[str] = ["version DESC"]


# Response Models
class RegistryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    service: str
    tracking_uri: Optional[str] = None
    message: str


@router.post("/register", response_model=RegistryResponse, dependencies=[Depends(require_scopes(["mlflow:write"]))])
async def register_model(request: RegisterModelRequest):
    """
    Registrar un modelo en MLflow Model Registry.

    Crea una nueva entrada en el registry con versionado automático,
    asignando la versión 1 y stage 'None' por defecto.

    Args:
        request: Datos del modelo a registrar

    Returns:
        Información del modelo registrado exitosamente

    Raises:
        HTTPException: Si el registro falla por datos inválidos o errores del servicio
    """
    try:
        logger.info("📝 Registrando modelo MLflow: %s (URI: %s)", request.name, request.model_uri)
        result = await registry_service.process_request({
            "action": "register_model",
            "model_uri": request.model_uri,
            "name": request.name,
            "description": request.description,
            "tags": request.tags
        })

        if not result.get("success", False):
            logger.error("❌ Error registrando modelo %s: %s", request.name, result.get("error", "Unknown error"))
            raise HTTPException(status_code=400, detail=result.get("error", "Error registrando modelo"))

        logger.info("✅ Modelo %s registrado exitosamente", request.name)
        return RegistryResponse(
            success=True,
            message=f"Model {request.name} registered successfully",
            data=result.get("data"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error inesperado registrando modelo %s", request.name)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/models", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def list_registered_models(
    max_results: int = Query(100, description="Máximo número de resultados"),
    page_token: Optional[str] = Query(None, description="Token de paginación")
):
    """
    Listar todos los modelos registrados
    
    Returns:
        Lista de modelos registrados con sus versiones
    """
    result = await registry_service.process_request({
        "action": "list_registered_models",
        "max_results": max_results,
        "page_token": page_token
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Error obteniendo modelos"))
    
    return result


@router.get("/models/{model_name}/versions/{version}", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def get_model_version(model_name: str, version: str):
    """
    Obtener información detallada de una versión específica de modelo
    
    Args:
        model_name: Nombre del modelo
        version: Versión del modelo
    
    Returns:
        Información detallada de la versión del modelo
    """
    result = await registry_service.process_request({
        "action": "get_model_version",
        "name": model_name,
        "version": version
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Versión de modelo no encontrada"))
    
    return result


@router.get("/models/{model_name}/latest-versions", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def get_latest_versions(
    model_name: str,
    stages: Optional[str] = Query("None,Staging,Production", description="Stages separados por comas")
):
    """
    Obtener las últimas versiones de un modelo por stage
    
    Args:
        model_name: Nombre del modelo
        stages: Lista de stages separados por comas
    
    Returns:
        Últimas versiones del modelo por stage
    """
    stages_list = [s.strip() for s in (stages or "None,Staging,Production").split(",") if s.strip()]
    
    result = await registry_service.process_request({
        "action": "get_latest_versions",
        "name": model_name,
        "stages": stages_list
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Modelo no encontrado"))
    
    return result


@router.post("/models/transition-stage", dependencies=[Depends(require_scopes(["mlflow:admin"]))])
async def transition_model_version_stage(request: TransitionStageRequest):
    """
    Promover modelo a un nuevo stage
    
    Args:
        name: Nombre del modelo
        version: Versión del modelo
        stage: Nuevo stage (None, Staging, Production, Archived)
        archive_existing_versions: Si archivar versiones existentes
    
    Returns:
        Información de la transición
    """
    result = await registry_service.process_request({
        "action": "transition_model_version_stage",
        "name": request.name,
        "version": request.version,
        "stage": request.stage,
        "archive_existing_versions": request.archive_existing_versions
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Error en transición de stage"))
    
    return result


@router.put("/models/update-version", dependencies=[Depends(require_scopes(["mlflow:write"]))])
async def update_model_version(request: UpdateModelVersionRequest):
    """
    Actualizar descripción de una versión de modelo
    
    Args:
        name: Nombre del modelo
        version: Versión del modelo
        description: Nueva descripción
    
    Returns:
        Confirmación de actualización
    """
    result = await registry_service.process_request({
        "action": "update_model_version",
        "name": request.name,
        "version": request.version,
        "description": request.description
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Error actualizando modelo"))
    
    return result


@router.post("/models/search", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def search_model_versions(request: SearchRequest):
    """
    Buscar versiones de modelos con filtros
    
    Args:
        filter: Filtro de búsqueda (ej: "name='MyModel'")
        max_results: Máximo número de resultados
        order_by: Orden de resultados
    
    Returns:
        Versiones de modelos que coinciden con el filtro
    """
    result = await registry_service.process_request({
        "action": "search_model_versions",
        "filter": request.filter,
        "max_results": request.max_results,
        "order_by": request.order_by
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Error en búsqueda"))
    
    return result


@router.get("/models/{model_name}/versions/{version}/download-uri", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def get_model_version_download_uri(model_name: str, version: str):
    """
    Obtener URI de descarga de una versión de modelo
    
    Args:
        model_name: Nombre del modelo
        version: Versión del modelo
    
    Returns:
        URI de descarga del modelo
    """
    result = await registry_service.process_request({
        "action": "get_model_version_download_uri",
        "name": model_name,
        "version": version
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Versión de modelo no encontrada"))
    
    return result


@router.post("/models/tags", dependencies=[Depends(require_scopes(["mlflow:write"]))])
async def set_model_version_tag(request: SetTagRequest):
    """
    Establecer tag en una versión de modelo
    
    Args:
        name: Nombre del modelo
        version: Versión del modelo
        key: Clave del tag
        value: Valor del tag
    
    Returns:
        Confirmación del tag establecido
    """
    result = await registry_service.process_request({
        "action": "set_model_version_tag",
        "name": request.name,
        "version": request.version,
        "key": request.key,
        "value": request.value
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Error estableciendo tag"))
    
    return result


@router.delete("/models/{model_name}/versions/{version}/tags/{tag_key}", dependencies=[Depends(require_scopes(["mlflow:admin"]))])
async def delete_model_version_tag(model_name: str, version: str, tag_key: str):
    """
    Eliminar tag de una versión de modelo
    
    Args:
        model_name: Nombre del modelo
        version: Versión del modelo
        tag_key: Clave del tag a eliminar
    
    Returns:
        Confirmación de eliminación del tag
    """
    result = await registry_service.process_request({
        "action": "delete_model_version_tag",
        "name": model_name,
        "version": version,
        "key": tag_key
    })
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Error eliminando tag"))
    
    return result


@router.get("/stats", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def get_registry_stats():
    """
    Obtener estadísticas del Model Registry
    
    Returns:
        Estadísticas del registry: total de modelos, versiones, distribución por stage
    """
    result = registry_service.get_registry_stats()
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Error obteniendo estadísticas"))
    
    return result


@router.get("/health", response_model=HealthResponse, dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def registry_health():
    """
    Verifica el estado de salud del servicio MLflow Registry.

    Realiza pruebas de conectividad con el servidor MLflow y verifica
    que el servicio de registry esté operativo y accesible.

    Returns:
        Estado de salud del servicio con detalles de conectividad

    Raises:
        HTTPException: Si el servicio no está disponible o hay problemas de conectividad
    """
    try:
        logger.info("🏥 Verificando salud del servicio MLflow Registry")
        # Test básico de conectividad
        result = registry_service.get_registry_stats()

        health_status = "healthy" if result.get("success") else "unhealthy"
        if result.get("success"):
            message = "MLflow Registry Service operational"
        else:
            message = result.get("error", _registry_service_error or "Connection issues")

        logger.info("📊 Estado de salud: %s", health_status)
        return HealthResponse(
            status=health_status,
            service="MLflowRegistryService",
            tracking_uri=registry_service.tracking_uri,
            message=message
        )

    except BiologyError as e:
        logger.exception("❌ Error verificando salud del servicio MLflow Registry")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}") from e


@router.post("/demo", dependencies=[Depends(require_scopes(["mlflow:read"]))])
async def registry_demo():
    """
    Demostración del MLflow Registry Service
    
    Returns:
        Ejemplo de funcionalidades del registry
    """
    return {
        "message": "MLflow Model Registry Service Demo",
        "capabilities": [
            "🚀 Registro de modelos con versionado automático",
            "📊 Gestión de stages (None, Staging, Production, Archived)",
            "🔍 Búsqueda avanzada de modelos y versiones",
            "🏷️ Sistema de tags para metadatos",
            "📈 Estadísticas y monitoreo del registry",
            "🔗 Integración completa con MLflow tracking",
            "⚡ API REST completa para todas las operaciones"
        ],
        "example_workflow": {
            "1": "POST /api/mlflow-registry/register - Registrar modelo desde experimento",
            "2": "GET /api/mlflow-registry/models - Listar modelos disponibles", 
            "3": "POST /api/mlflow-registry/models/transition-stage - Promover a staging",
            "4": "GET /api/mlflow-registry/models/{name}/latest-versions - Obtener versiones",
            "5": "POST /api/mlflow-registry/models/transition-stage - Promover a production"
        },
        "integration_note": "Complementa el ExperimentTrackingService existente con capacidades avanzadas de Model Registry"
    }
