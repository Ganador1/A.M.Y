"""
TypedDict definitions for mlflow_registry_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Procesar solicitudes del registry"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RegisterModelResult(TypedDict, total=False):
    """Response type for register_model."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListRegisteredModelsResult(TypedDict, total=False):
    """Listar todos los modelos registrados"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetModelVersionResult(TypedDict, total=False):
    """Obtener información de una versión específica de modelo"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetLatestVersionsResult(TypedDict, total=False):
    """Obtener las últimas versiones de un modelo por stage"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TransitionModelVersionStageResult(TypedDict, total=False):
    """Promover modelo entre stages"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class UpdateModelVersionResult(TypedDict, total=False):
    """Actualizar descripción de una versión de modelo"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SearchModelVersionsResult(TypedDict, total=False):
    """Buscar versiones de modelos con filtros"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetModelVersionDownloadUriResult(TypedDict, total=False):
    """Obtener URI de descarga de una versión de modelo"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SetModelVersionTagResult(TypedDict, total=False):
    """Establecer tag en una versión de modelo"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DeleteModelVersionTagResult(TypedDict, total=False):
    """Eliminar tag de una versión de modelo"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetRegistryStatsResult(TypedDict, total=False):
    """Obtener estadísticas del registry"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

