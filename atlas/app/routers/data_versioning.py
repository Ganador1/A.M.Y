"""
Data Versioning and Provenance Router

Router FastAPI para versionado comprehensivo de datos, seguimiento de procedencia y gestión
de datasets en la plataforma de computación científica AXIOM. Proporciona endpoints REST API para
control de versiones de datos de investigación, seguimiento de reproducibilidad y gestión de linaje de datos.

Este router ofrece capacidades avanzadas de versionado de datos para:
- Versionado de datos científicos con seguimiento de metadatos y procedencia
- Inicialización y gestión de datasets con historial de versiones
- Comparación de datos y análisis de diferencias entre versiones
- Operaciones de reversión para restauración y rollback de datos
- Reportes de procedencia para reproducibilidad de investigación
- Organización basada en etiquetas y filtrado de versiones de datos
- Validación segura de rutas de datos y control de acceso

El router se integra con DataVersioningService para proporcionar
a investigadores herramientas de gestión de datos de nivel empresarial, asegurando
integridad de datos, reproducibilidad y atribución apropiada en flujos de trabajo científicos.

Endpoints disponibles:
- POST /version-data: Crear nueva versión de datos con metadatos y etiquetas
- GET /version/{version_id}: Recuperar detalles de versión específica de datos
- GET /versions: Listar versiones de datos con filtrado opcional por ruta/etiquetas
- POST /compare-versions: Comparar diferencias entre dos versiones de datos
- POST /revert-to-version: Revertir datos a estado de versión anterior
- POST /provenance-report: Generar reporte de procedencia para linaje de datos
- POST /init-dataset: Inicializar nuevo dataset para versionado
- GET /dataset/{dataset_name}/status: Obtener estado de dataset e información de versiones

Dependencias:
- DataVersioningService: Versionado de datos principal y seguimiento de procedencia
- FileSystem: Operaciones seguras de archivos con validación de rutas
- MetadataStorage: Gestión de metadatos y capacidades de búsqueda
- ProvenanceTracker: Seguimiento de linaje y dependencias de datos
- SecurityService: Autenticación y autorización para acceso a datos
- Logging: Logging de auditoría comprehensivo para operaciones de datos

Uso típico:
    El versionado de datos soporta archivos de datos científicos con extracción automática de metadatos.
    El seguimiento de procedencia asegura reproducibilidad de investigación y atribución apropiada.
    La gestión de datasets proporciona control de versiones organizado para proyectos de investigación.
    Las características de seguridad previenen acceso no autorizado y mantienen integridad de datos.

ÉTICA Y SEGURIDAD:
- No se debe subir o versionar PII/secretos
- Respetar límites de tamaño y cuotas; ver MAX_VERSION_FILE_BYTES
- Usar STRICT_DATA_PATHS=1 y ALLOWED_DATA_ROOT para restringir rutas
- Los endpoints no autentican por defecto: proteger este router en producción
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import os
from app.services.data_versioning import DataVersioningService
from app.security import require_bearer

router = APIRouter(dependencies=[Depends(require_bearer)])
data_versioning_service = DataVersioningService()


@router.post("/version-data")
async def version_data(request: Dict[str, Any]):
    """
    Create a new version of data

    Args:
        request: Data versioning parameters
            - data_path: Path to the data file
            - metadata: Additional metadata (optional)
            - tags: Tags for the version (optional)
            - allow_external_path: bool para permitir paths fuera del root si STRICT_DATA_PATHS=0

    Returns:
        Data versioning response
    """
    result = await data_versioning_service.process_request({
        "action": "version_data",
        **request
    })

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Data versioning failed"))

    return result


@router.get("/version/{version_id}")
async def get_version(version_id: str):
    """
    Get details of a data version

    Args:
        version_id: ID of the data version

    Returns:
        Version details
    """
    result = await data_versioning_service.process_request({
        "action": "get_version",
        "version_id": version_id
    })

    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Version not found"))

    return result


@router.get("/versions")
async def list_versions(data_path: Optional[str] = None, tags: Optional[str] = None):
    """
    List data versions with optional filtering

    Args:
        data_path: Filter by data path (optional)
        tags: Filter by tags (comma-separated, optional)

    Returns:
        List of data versions
    """
    tag_list = tags.split(",") if tags else []
    result = await data_versioning_service.process_request({
        "action": "list_versions",
        "data_path": data_path,
        "tags": tag_list
    })

    return result


@router.post("/compare-versions")
async def compare_versions(request: Dict[str, Any]):
    """
    Compare two data versions

    Args:
        request: Comparison parameters
            - version_id_1: First version ID
            - version_id_2: Second version ID

    Returns:
        Version comparison results
    """
    if "version_id_1" not in request or "version_id_2" not in request:
        raise HTTPException(status_code=400, detail="version_id_1 and version_id_2 are required")

    result = await data_versioning_service.process_request({
        "action": "compare_versions",
        **request
    })

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Version comparison failed"))

    return result


@router.post("/revert-to-version")
async def revert_to_version(request: Dict[str, Any]):
    """
    Revert data to a previous version

    Args:
        request: Revert parameters
            - version_id: Version ID to revert to
            - target_path: Target path for reverted data (optional)

    Returns:
        Revert operation response
    """
    if "version_id" not in request:
        raise HTTPException(status_code=400, detail="version_id is required")

    result = await data_versioning_service.process_request({
        "action": "revert_to_version",
        **request
    })

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Revert operation failed"))

    return result


@router.post("/provenance-report")
async def create_provenance_report(request: Dict[str, Any]):
    """
    Create a provenance report for data

    Args:
        request: Report parameters
            - data_path: Path to the data file

    Returns:
        Provenance report
    """
    if "data_path" not in request:
        raise HTTPException(status_code=400, detail="data_path is required")

    result = await data_versioning_service.process_request({
        "action": "create_provenance_report",
        **request
    })

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Provenance report creation failed"))

    return result


@router.post("/init-dataset")
async def init_dataset(request: Dict[str, Any]):
    """
    Initialize a new dataset for versioning

    Args:
        request: Dataset initialization parameters
            - dataset_name: Name of the dataset
            - description: Dataset description (optional)
            - initial_files: List of initial files to version (optional)

    Returns:
        Dataset initialization response
    """
    dataset_name = request.get("dataset_name")
    if not dataset_name:
        raise HTTPException(status_code=400, detail="dataset_name is required")

    # Create dataset directory
    dataset_path = f"./data/{dataset_name}"
    os.makedirs(dataset_path, exist_ok=True)

    # Version initial files if provided
    versioned_files = []
    initial_files = request.get("initial_files", [])
    for file_path in initial_files:
        if os.path.exists(file_path):
            version_result = await data_versioning_service.process_request({
                "action": "version_data",
                "data_path": file_path,
                "metadata": {
                    "dataset": dataset_name,
                    "type": "initial_version"
                },
                "tags": [dataset_name, "initial"]
            })
            if version_result.get("success"):
                versioned_files.append(version_result["version_id"])

    return {
        "success": True,
        "message": f"Dataset '{dataset_name}' initialized successfully",
        "dataset_name": dataset_name,
        "dataset_path": dataset_path,
        "versioned_files": versioned_files,
        "total_files_versioned": len(versioned_files)
    }


@router.get("/dataset/{dataset_name}/status")
async def get_dataset_status(dataset_name: str):
    """
    Get the status of a dataset

    Args:
        dataset_name: Name of the dataset

    Returns:
        Dataset status information
    """
    # List versions for this dataset
    result = await data_versioning_service.process_request({
        "action": "list_versions",
        "tags": [dataset_name]
    })

    if not result.get("success", False):
        raise HTTPException(status_code=500, detail="Failed to get dataset status")

    versions = result.get("versions", [])
    total_size = sum(v["size_bytes"] for v in versions)
    latest_version = max(versions, key=lambda x: x["created_at"]) if versions else None

    return {
        "success": True,
        "dataset_name": dataset_name,
        "total_versions": len(versions),
        "total_size_bytes": total_size,
        "latest_version": latest_version,
        "versions": versions
    }
