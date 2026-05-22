"""
MLflow Model Registry Service

Servicio dedicado para la gestión avanzada del registro de modelos MLflow.
Extiende las capacidades del ExperimentTrackingService existente con
funcionalidades específicas del Model Registry.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING, cast
from dataclasses import dataclass, field

if TYPE_CHECKING:  # pragma: no cover - hints for type checkers
    import mlflow  # type: ignore
    from mlflow.tracking import MlflowClient  # type: ignore
    from mlflow.exceptions import RestException  # type: ignore

try:
    import mlflow  # type: ignore
    from mlflow.tracking import MlflowClient  # type: ignore
    from mlflow.exceptions import RestException  # type: ignore
    MLFLOW_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback when mlflow is not installed
    mlflow = cast(Any, None)
    MlflowClient = cast(Any, None)
    RestException = Exception  # type: ignore[assignment]
    MLFLOW_AVAILABLE = False

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.config import settings
from app.exceptions.infrastructure.api import APIError


@dataclass
class RegisteredModelInfo:
    """Información de modelo registrado en MLflow"""
    name: str
    version: str
    stage: str
    description: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    run_id: Optional[str] = None
    model_uri: Optional[str] = None
    creation_timestamp: Optional[int] = None
    last_updated_timestamp: Optional[int] = None
    current_stage: Optional[str] = None
    source: Optional[str] = None
    status: str = "READY"


class MLflowRegistryService(BaseService):
    """
    Servicio avanzado para MLflow Model Registry
    
    Características:
    - Registro de modelos con versionado automático
    - Gestión de stages (staging, production, archived)
    - Promoción de modelos entre stages
    - Búsqueda y filtrado de modelos
    - Gestión de aliases y tags
    - Integración con experimentos existentes
    """

    def __init__(self):
        super().__init__("MLflowRegistry")

        if not MLFLOW_AVAILABLE:
            raise RuntimeError(
                "mlflow package is not installed. Install mlflow to enable MLflow registry operations."
            )

        # Configurar MLflow
        self.tracking_uri = getattr(settings, "MLFLOW_TRACKING_URI", "file:./mlruns")
        mlflow.set_tracking_uri(self.tracking_uri)

        self.client = MlflowClient(self.tracking_uri)
        
        # Stages válidos en MLflow
        self.valid_stages = ["None", "Staging", "Production", "Archived"]
        
        logger.info(f"✅ MLflowRegistryService initialized with tracking URI: {self.tracking_uri}")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar solicitudes del registry"""
        try:
            action = request_data.get("action", "")

            if action == "register_model":
                return await self.register_model(request_data)
            elif action == "list_registered_models":
                return await self.list_registered_models(request_data)
            elif action == "get_model_version":
                return await self.get_model_version(request_data)
            elif action == "get_latest_versions":
                return await self.get_latest_versions(request_data)
            elif action == "transition_model_version_stage":
                return await self.transition_model_version_stage(request_data)
            elif action == "update_model_version":
                return await self.update_model_version(request_data)
            elif action == "search_model_versions":
                return await self.search_model_versions(request_data)
            elif action == "get_model_version_download_uri":
                return await self.get_model_version_download_uri(request_data)
            elif action == "set_model_version_tag":
                return await self.set_model_version_tag(request_data)
            elif action == "delete_model_version_tag":
                return await self.delete_model_version_tag(request_data)
            elif action == "get_registry_stats":
                return self.get_registry_stats()
            else:
                return {
                    "success": False,
                    "error": f"Acción desconocida: {action}",
                    "available_actions": [
                        "register_model", "list_registered_models", "get_model_version",
                        "get_latest_versions", "transition_model_version_stage",
                        "update_model_version", "search_model_versions", 
                        "get_model_version_download_uri", "set_model_version_tag", 
                        "delete_model_version_tag", "get_registry_stats"
                    ]
                }

        except APIError as e:
            return self.handle_error(e, "process_request")

    async def register_model(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registrar un modelo en MLflow Model Registry
        
        Args:
            model_uri: URI del modelo (ej: runs:/<run_id>/model)
            name: Nombre del modelo registrado
            description: Descripción opcional
            tags: Tags opcionales
        """
        try:
            model_uri = request_data.get("model_uri")
            name = request_data.get("name")
            description = request_data.get("description")
            tags = request_data.get("tags", {})

            if not model_uri or not name:
                return {
                    "success": False,
                    "error": "model_uri y name son requeridos"
                }

            # Registrar el modelo
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=name,
                tags=tags
            )

            # Actualizar descripción si se proporciona
            if description:
                self.client.update_model_version(
                    name=name,
                    version=model_version.version,
                    description=description
                )

            logger.info(f"Modelo registrado: {name} v{model_version.version}")

            return {
                "success": True,
                "model_name": name,
                "model_version": model_version.version,
                "model_uri": model_uri,
                "registry_uri": f"models:/{name}/{model_version.version}",
                "run_id": model_version.run_id,
                "status": model_version.status,
                "creation_timestamp": model_version.creation_timestamp,
                "description": description
            }

        except APIError as e:
            return self.handle_error(e, "register_model")
        except RestException as e:
            logger.error(f"Error de MLflow al registrar modelo: {str(e)}")
            return {
                "success": False,
                "error": f"Error de MLflow: {str(e)}"
            }

    async def list_registered_models(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Listar todos los modelos registrados"""
        try:
            max_results = request_data.get("max_results", 100)
            page_token = request_data.get("page_token", None)

            # Obtener modelos registrados
            registered_models = self.client.search_registered_models(
                max_results=max_results,
                page_token=page_token
            )

            models_info = []
            for model in registered_models:
                # Obtener versiones del modelo
                versions_info = []
                if hasattr(model, 'latest_versions') and model.latest_versions:
                    for version in model.latest_versions:
                        versions_info.append({
                            "version": version.version,
                            "stage": version.current_stage,
                            "status": version.status,
                            "creation_timestamp": version.creation_timestamp,
                            "last_updated_timestamp": version.last_updated_timestamp,
                            "description": version.description,
                            "run_id": version.run_id,
                            "source": version.source
                        })

                models_info.append({
                    "name": model.name,
                    "description": model.description,
                    "creation_timestamp": model.creation_timestamp,
                    "last_updated_timestamp": model.last_updated_timestamp,
                    "tags": dict(model.tags) if model.tags else {},
                    "latest_versions": versions_info
                })

            return {
                "success": True,
                "registered_models": models_info,
                "count": len(models_info)
            }

        except APIError as e:
            return self.handle_error(e, "list_registered_models")

    async def get_model_version(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener información de una versión específica de modelo"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")

            if not name or not version:
                return {
                    "success": False,
                    "error": "name y version son requeridos"
                }

            model_version = self.client.get_model_version(name=name, version=version)

            return {
                "success": True,
                "model_version": {
                    "name": model_version.name,
                    "version": model_version.version,
                    "stage": model_version.current_stage,
                    "description": model_version.description,
                    "creation_timestamp": model_version.creation_timestamp,
                    "last_updated_timestamp": model_version.last_updated_timestamp,
                    "run_id": model_version.run_id,
                    "source": model_version.source,
                    "status": model_version.status,
                    "tags": dict(model_version.tags) if model_version.tags else {}
                }
            }

        except APIError as e:
            return self.handle_error(e, "get_model_version")

    async def get_latest_versions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener las últimas versiones de un modelo por stage"""
        try:
            name = request_data.get("name")
            stages = request_data.get("stages", ["None", "Staging", "Production"])

            if not name:
                return {
                    "success": False,
                    "error": "name es requerido"
                }

            latest_versions = self.client.get_latest_versions(name=name, stages=stages)

            versions_info = []
            for version in latest_versions:
                versions_info.append({
                    "name": version.name,
                    "version": version.version,
                    "stage": version.current_stage,
                    "description": version.description,
                    "creation_timestamp": version.creation_timestamp,
                    "last_updated_timestamp": version.last_updated_timestamp,
                    "run_id": version.run_id,
                    "source": version.source,
                    "status": version.status,
                    "tags": dict(version.tags) if version.tags else {}
                })

            return {
                "success": True,
                "latest_versions": versions_info,
                "model_name": name,
                "stages_requested": stages
            }

        except APIError as e:
            return self.handle_error(e, "get_latest_versions")

    async def transition_model_version_stage(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Promover modelo entre stages"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            stage = request_data.get("stage")
            archive_existing_versions = request_data.get("archive_existing_versions", False)

            if not name or not version or not stage:
                return {
                    "success": False,
                    "error": "name, version y stage son requeridos"
                }

            if stage not in self.valid_stages:
                return {
                    "success": False,
                    "error": f"Stage inválido. Válidos: {self.valid_stages}"
                }

            # Transición de stage
            model_version = self.client.transition_model_version_stage(
                name=name,
                version=version,
                stage=stage,
                archive_existing_versions=archive_existing_versions
            )

            logger.info(f"Modelo {name} v{version} promovido a stage: {stage}")

            return {
                "success": True,
                "model_name": name,
                "version": version,
                "new_stage": stage,
                "previous_stage": model_version.current_stage,
                "archive_existing_versions": archive_existing_versions,
                "last_updated_timestamp": model_version.last_updated_timestamp
            }

        except APIError as e:
            return self.handle_error(e, "transition_model_version_stage")

    async def update_model_version(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar descripción de una versión de modelo"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            description = request_data.get("description")

            if not name or not version:
                return {
                    "success": False,
                    "error": "name y version son requeridos"
                }

            model_version = self.client.update_model_version(
                name=name,
                version=version,
                description=description
            )

            return {
                "success": True,
                "model_name": name,
                "version": version,
                "updated_description": description,
                "last_updated_timestamp": model_version.last_updated_timestamp
            }

        except APIError as e:
            return self.handle_error(e, "update_model_version")

    async def search_model_versions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar versiones de modelos con filtros"""
        try:
            filter_string = request_data.get("filter", "")
            max_results = request_data.get("max_results", 100)
            order_by = request_data.get("order_by", ["version DESC"])

            model_versions = self.client.search_model_versions(
                filter_string=filter_string,
                max_results=max_results,
                order_by=order_by
            )

            versions_info = []
            for version in model_versions:
                versions_info.append({
                    "name": version.name,
                    "version": version.version,
                    "stage": version.current_stage,
                    "description": version.description,
                    "creation_timestamp": version.creation_timestamp,
                    "last_updated_timestamp": version.last_updated_timestamp,
                    "run_id": version.run_id,
                    "source": version.source,
                    "status": version.status,
                    "tags": dict(version.tags) if version.tags else {}
                })

            return {
                "success": True,
                "model_versions": versions_info,
                "count": len(versions_info),
                "filter_used": filter_string
            }

        except APIError as e:
            return self.handle_error(e, "search_model_versions")

    async def get_model_version_download_uri(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener URI de descarga de una versión de modelo"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")

            if not name or not version:
                return {
                    "success": False,
                    "error": "name y version son requeridos"
                }

            download_uri = self.client.get_model_version_download_uri(name=name, version=version)

            return {
                "success": True,
                "model_name": name,
                "version": version,
                "download_uri": download_uri
            }

        except APIError as e:
            return self.handle_error(e, "get_model_version_download_uri")

    async def set_model_version_tag(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Establecer tag en una versión de modelo"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            key = request_data.get("key")
            value = request_data.get("value")

            if not name or not version or not key or value is None:
                return {
                    "success": False,
                    "error": "name, version, key y value son requeridos"
                }

            self.client.set_model_version_tag(name=name, version=version, key=key, value=value)

            return {
                "success": True,
                "model_name": name,
                "version": version,
                "tag_key": key,
                "tag_value": value
            }

        except APIError as e:
            return self.handle_error(e, "set_model_version_tag")

    async def delete_model_version_tag(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Eliminar tag de una versión de modelo"""
        try:
            name = request_data.get("name")
            version = request_data.get("version")
            key = request_data.get("key")

            if not name or not version or not key:
                return {
                    "success": False,
                    "error": "name, version y key son requeridos"
                }

            self.client.delete_model_version_tag(name=name, version=version, key=key)

            return {
                "success": True,
                "model_name": name,
                "version": version,
                "deleted_tag_key": key
            }

        except APIError as e:
            return self.handle_error(e, "delete_model_version_tag")

    def get_registry_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del registry"""
        try:
            registered_models = self.client.search_registered_models()
            
            stats = {
                "total_models": len(registered_models),
                "models_by_stage": {stage: 0 for stage in self.valid_stages},
                "total_versions": 0,
                "recent_models": []
            }

            for model in registered_models:
                for version in (model.latest_versions or []):
                    stats["total_versions"] += 1
                    stats["models_by_stage"][version.current_stage] += 1

                # Agregar modelos recientes (últimos 5)
                if len(stats["recent_models"]) < 5:
                    stats["recent_models"].append({
                        "name": model.name,
                        "description": model.description,
                        "creation_timestamp": model.creation_timestamp
                    })

            return {
                "success": True,
                "registry_stats": stats,
                "tracking_uri": self.tracking_uri
            }

        except APIError as e:
            logger.error(f"Error obteniendo estadísticas del registry: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
