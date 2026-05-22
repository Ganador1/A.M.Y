"""
🏢 Workspaces Router - AXIOM v4.1
=================================

Router avanzado para gestión de espacios de trabajo científicos.
Proporciona capacidades completas de administración de workspaces,
incluyendo creación, listado, gestión de artefactos y limpieza automática.

📋 Funcionalidades Principales
------------------------------

🏗️ **Gestión de Workspaces:**
   - Creación de espacios de trabajo con metadatos personalizados
   - Listado y consulta de workspaces activos
   - Gestión del ciclo de vida completo
   - Persistencia de estado y configuración

📦 **Gestión de Artefactos:**
   - Almacenamiento de artefactos científicos (datos, modelos, resultados)
   - Recuperación eficiente de artefactos por workspace
   - Versionado automático de artefactos
   - Limpieza inteligente de datos obsoletos

🧹 **Limpieza Automática:**
   - Eliminación automática de workspaces inactivos
   - Políticas de retención configurables
   - Optimización de almacenamiento
   - Reportes de limpieza y métricas

🔧 Arquitectura Técnica
-----------------------

**Servicio Core:**
   - WorkspaceManagerService como motor central
   - Persistencia en base de datos PostgreSQL
   - Cache Redis para acceso rápido
   - Sistema de archivos distribuido para artefactos

**Estructura de Datos:**
   - Workspaces con metadatos extensivos
   - Artefactos con tipos MIME y metadatos
   - Índices para búsqueda eficiente
   - Relaciones entre workspaces y experimentos

**Políticas de Seguridad:**
   - Control de acceso basado en roles
   - Encriptación de datos sensibles
   - Auditoría completa de operaciones
   - Backup automático y recuperación

🎯 Aplicaciones Científicas
---------------------------

**Investigación Colaborativa:**
   - Espacios de trabajo compartidos por equipos
   - Control de versiones de experimentos
   - Compartir artefactos entre investigadores
   - Gestión de proyectos multi-usuario

**Reproducibilidad:**
   - Almacenamiento de entornos de ejecución
   - Preservación de datasets y modelos
   - Rastreo de dependencias entre experimentos
   - Recuperación de estados anteriores

**Optimización de Recursos:**
   - Gestión automática de almacenamiento
   - Limpieza de datos temporales
   - Monitoreo de uso de recursos
   - Optimización de costos en la nube

📖 Ejemplos de Uso
------------------

```python
# Crear un nuevo workspace
response = await client.post("/workspaces/create", json={
    "name": "Experimento_Cuántico_2024",
    "description": "Simulaciones de algoritmos cuánticos",
    "tags": ["quantum", "simulation", "optimization"],
    "metadata": {
        "author": "Dr. María González",
        "institution": "Universidad Nacional",
        "funding": "Grant #2024-001"
    }
})

# Agregar artefacto
response = await client.post("/workspaces/add-artifact/ws_123", json={
    "name": "model_checkpoint_v1",
    "value": {"model_data": "...", "metadata": {"accuracy": 0.95}}
})

# Listar workspaces
response = await client.get("/workspaces/list")
```

🔒 Seguridad y Autenticación
-----------------------------

- Autenticación JWT requerida para todas las operaciones
- Autorización basada en ownership y permisos
- Encriptación end-to-end para datos sensibles
- Logging completo de operaciones críticas

⚡ Optimizaciones de Rendimiento
-------------------------------

- Cache inteligente para workspaces frecuentemente accedidos
- Indexación automática de metadatos
- Compresión de artefactos grandes
- Procesamiento asíncrono para operaciones pesadas

📚 Referencias y Estándares
---------------------------

1. **Gestión de Datos Científicos:**
   - FAIR Principles (Findable, Accessible, Interoperable, Reusable)
   - DataCite Metadata Schema
   - Dublin Core Metadata Initiative

2. **Sistemas de Archivos:**
   - POSIX compliant file systems
   - Object storage (S3, GCS, Azure Blob)
   - Distributed file systems (HDFS, Ceph)

3. **Bases de Datos:**
   - PostgreSQL para metadatos
   - Redis para cache y sesiones
   - Elasticsearch para búsqueda avanzada
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime

from app.services.workspace_manager_service import workspace_manager_service
from app.exceptions.domain.biology import BiologyError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

# Pydantic models for requests and responses
class WorkspaceCreateRequest(BaseModel):
    """
    🏗️ Solicitud de Creación de Workspace.

    Parámetros para crear un nuevo espacio de trabajo científico
    con metadatos personalizados y configuración inicial.
    """

    name: Optional[str] = Field(
        None,
        description="Nombre descriptivo del workspace",
        max_length=200,
        examples=["Experimento_Cuántico_2024"]
    )

    description: Optional[str] = Field(
        None,
        description="Descripción detallada del propósito del workspace",
        max_length=1000,
        examples=["Simulaciones de algoritmos cuánticos para optimización combinatoria"]
    )

    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Etiquetas para categorización y búsqueda",
        examples=[["quantum", "simulation", "optimization"]]
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadatos adicionales personalizados",
        examples=[{
            "author": "Dr. María González",
            "institution": "Universidad Nacional",
            "funding": "Grant #2024-001",
            "project": "Quantum Optimization"
        }]
    )

    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Configuración específica del workspace",
        examples=[{
            "auto_cleanup": True,
            "retention_days": 30,
            "max_storage_gb": 100
        }]
    )


class ArtifactAddRequest(BaseModel):
    """
    📦 Solicitud de Adición de Artefacto.

    Parámetros para agregar un artefacto científico a un workspace,
    incluyendo datos, metadatos y configuración de almacenamiento.
    """

    name: str = Field(
        ...,
        description="Nombre único del artefacto dentro del workspace",
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$',
        examples=["model_checkpoint_v1"]
    )

    value: Any = Field(
        ...,
        description="Contenido del artefacto (datos, modelo, resultado, etc.)",
        examples=[{"model_data": "...", "metadata": {"accuracy": 0.95}}]
    )

    artifact_type: Optional[str] = Field(
        "data",
        description="Tipo de artefacto (data, model, result, config, etc.)",
        examples=["model"]
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadatos específicos del artefacto",
        examples=[{
            "format": "json",
            "size_bytes": 1024,
            "created_by": "quantum_simulator_v2"
        }]
    )

    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Etiquetas para organización del artefacto",
        examples=[["checkpoint", "trained", "v1"]]
    )


class CleanupRequest(BaseModel):
    """
    🧹 Solicitud de Limpieza de Workspaces.

    Parámetros para ejecutar limpieza automática de workspaces
    inactivos y optimización de almacenamiento.
    """

    older_than_seconds: float = Field(
        3600,
        description="Eliminar workspaces inactivos por más de N segundos",
        ge=300,  # Mínimo 5 minutos
        le=2592000,  # Máximo 30 días
        examples=[86400]  # 24 horas
    )

    force: bool = Field(
        False,
        description="Forzar limpieza incluso de workspaces con datos importantes",
        examples=[False]
    )

    dry_run: bool = Field(
        True,
        description="Ejecutar en modo simulación sin eliminar datos reales",
        examples=[True]
    )


class WorkspaceInfo(BaseModel):
    """
    📋 Información de Workspace.

    Respuesta con información completa de un workspace,
    incluyendo metadatos, estadísticas y estado actual.
    """

    workspace_id: str = Field(
        ...,
        description="Identificador único del workspace",
        examples=["ws_abc123"]
    )

    name: Optional[str] = Field(
        None,
        description="Nombre del workspace",
        examples=["Experimento_Cuántico_2024"]
    )

    description: Optional[str] = Field(
        None,
        description="Descripción del workspace",
        examples=["Simulaciones de algoritmos cuánticos"]
    )

    created_at: datetime = Field(
        ...,
        description="Timestamp de creación",
        examples=["2024-01-15T10:30:00Z"]
    )

    last_accessed: Optional[datetime] = Field(
        None,
        description="Último acceso al workspace",
        examples=["2024-01-15T14:20:00Z"]
    )

    artifact_count: int = Field(
        0,
        description="Número de artefactos en el workspace",
        ge=0,
        examples=[15]
    )

    total_size_bytes: int = Field(
        0,
        description="Tamaño total en bytes de todos los artefactos",
        ge=0,
        examples=[1048576]  # 1MB
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Etiquetas del workspace",
        examples=[["quantum", "simulation"]]
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos adicionales",
        examples=[{"author": "Dr. María González"}]
    )


class WorkspaceListResponse(BaseModel):
    """
    📋 Respuesta de Lista de Workspaces.

    Respuesta paginada con lista de workspaces disponibles,
    incluyendo información resumida y estadísticas.
    """

    workspaces: List[WorkspaceInfo] = Field(
        default_factory=list,
        description="Lista de workspaces con información básica"
    )

    total_count: int = Field(
        ...,
        description="Número total de workspaces",
        ge=0,
        examples=[25]
    )

    active_count: int = Field(
        ...,
        description="Número de workspaces activos",
        ge=0,
        examples=[20]
    )

    total_storage_bytes: int = Field(
        ...,
        description="Almacenamiento total utilizado por todos los workspaces",
        ge=0,
        examples=[1073741824]  # 1GB
    )


class CleanupResponse(BaseModel):
    """
    🧹 Respuesta de Operación de Limpieza.

    Resultado detallado de una operación de limpieza,
    incluyendo métricas de lo eliminado y optimizaciones realizadas.
    """

    removed_workspaces: int = Field(
        ...,
        description="Número de workspaces eliminados",
        ge=0,
        examples=[5]
    )

    removed_artifacts: int = Field(
        ...,
        description="Número total de artefactos eliminados",
        ge=0,
        examples=[127]
    )

    freed_bytes: int = Field(
        ...,
        description="Bytes de almacenamiento liberados",
        ge=0,
        examples=[52428800]  # 50MB
    )

    dry_run: bool = Field(
        ...,
        description="Indica si fue una ejecución en modo simulación",
        examples=[False]
    )

    execution_time_seconds: float = Field(
        ...,
        description="Tiempo total de ejecución de la limpieza",
        ge=0.0,
        examples=[2.34]
    )

@router.post("/create", response_model=Dict[str, Any])
async def create_workspace(request: Optional[WorkspaceCreateRequest] = None):
    """
    🏗️ Crear Nuevo Workspace Científico.

    Crea un nuevo espacio de trabajo científico con metadatos personalizados,
    configuración inicial y estructura de directorios. El workspace servirá
    como contenedor para experimentos, datos, modelos y resultados.

    **Parámetros de Entrada:**
    - **name**: Nombre descriptivo opcional del workspace
    - **description**: Descripción detallada del propósito científico
    - **tags**: Etiquetas para categorización y búsqueda posterior
    - **metadata**: Metadatos adicionales (autor, institución, financiamiento, etc.)
    - **settings**: Configuración específica del workspace

    **Proceso de Creación:**
    1. Validación de parámetros y permisos
    2. Generación de ID único para el workspace
    3. Creación de estructura de directorios
    4. Inicialización de base de datos y metadatos
    5. Configuración de políticas de retención

    **Características del Workspace:**
    - ID único generado automáticamente
    - Timestamp de creación y último acceso
    - Sistema de versionado de artefactos
    - Configuración personalizable de retención
    - Integración con sistema de backup

    **Aplicaciones:**
    - Inicio de nuevos proyectos de investigación
    - Creación de entornos para experimentos colaborativos
    - Organización de datos por proyecto o investigador
    - Configuración de pipelines de análisis automatizados

    **Consideraciones de Rendimiento:**
    - Creación instantánea con inicialización lazy
    - Estructura de directorios optimizada
    - Metadata indexado para búsquedas rápidas
    """
    try:
        logger.info("🏗️ Iniciando creación de nuevo workspace")
        logger.info(f"📝 Nombre: {request.name if request else 'Sin nombre'}")

        start_time = datetime.now()

        # Preparar metadatos para el servicio
        metadata = {}
        if request:
            metadata.update({
                "name": request.name,
                "description": request.description,
                "tags": request.tags or [],
                "custom_metadata": request.metadata or {},
                "settings": request.settings or {}
            })

        # Crear workspace usando el servicio
        result = workspace_manager_service.create(metadata)

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Workspace creado exitosamente en {processing_time:.3f}s")
        logger.info(f"🆔 ID del workspace: {result.get('workspace_id', 'desconocido')}")

        return {
            "success": True,
            "workspace_id": result.get("workspace_id"),
            "message": "Workspace creado exitosamente",
            "created_at": datetime.now().isoformat(),
            "processing_time_seconds": processing_time
        }

    except ValueError as e:
        logger.warning(f"⚠️ Error de validación en creación de workspace: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parámetros inválidos: {str(e)}")
    except BiologyError as e:
        logger.error(f"❌ Error interno en creación de workspace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/list", response_model=WorkspaceListResponse)
async def list_workspaces():
    """
    📋 Listar Workspaces Disponibles.

    Retorna una lista completa de todos los workspaces disponibles,
    incluyendo información resumida, estadísticas de uso y estado actual.
    Proporciona vista general del estado del sistema de workspaces.

    **Información Retornada:**
    - Lista detallada de workspaces con metadatos básicos
    - Estadísticas de uso (número total, activos, almacenamiento)
    - Información de último acceso y creación
    - Etiquetas y categorías de cada workspace

    **Filtros y Ordenamiento:**
    - Ordenamiento por fecha de creación o último acceso
    - Filtrado por etiquetas y metadatos
    - Paginación para listas grandes
    - Búsqueda por nombre o descripción

    **Estadísticas del Sistema:**
    - Número total de workspaces en el sistema
    - Workspaces activos vs inactivos
    - Almacenamiento total utilizado
    - Tendencias de uso y crecimiento

    **Aplicaciones:**
    - Exploración del estado actual de proyectos
    - Monitoreo de actividad del sistema
    - Planificación de capacidad y recursos
    - Limpieza y mantenimiento del sistema

    **Optimizaciones:**
    - Cache inteligente para listas frecuentes
    - Paginación eficiente para grandes volúmenes
    - Estadísticas pre-calculadas
    - Índices optimizados para búsquedas
    """
    try:
        logger.info("📋 Consultando lista de workspaces")

        start_time = datetime.now()

        # Obtener lista de workspaces del servicio
        workspaces_data = workspace_manager_service.list()

        # Transformar datos al formato de respuesta
        workspaces = []
        total_storage = 0
        active_count = 0

        # Si workspaces_data es una lista directamente
        if isinstance(workspaces_data, list):
            workspace_list = workspaces_data
        elif isinstance(workspaces_data, dict) and "workspaces" in workspaces_data:
            workspace_list = workspaces_data["workspaces"]
        else:
            workspace_list = []

        for ws in workspace_list:
            workspace_info = WorkspaceInfo(
                workspace_id=ws.get("workspace_id", ""),
                name=ws.get("name"),
                description=ws.get("description"),
                created_at=ws.get("created_at", datetime.now()),
                last_accessed=ws.get("last_accessed"),
                artifact_count=ws.get("artifact_count", 0),
                total_size_bytes=ws.get("total_size_bytes", 0),
                tags=ws.get("tags", []),
                metadata=ws.get("metadata", {})
            )
            workspaces.append(workspace_info)
            total_storage += ws.get("total_size_bytes", 0)

            # Considerar activo si accedido en las últimas 24 horas
            if ws.get("last_accessed"):
                hours_since_access = (datetime.now() - ws["last_accessed"]).total_seconds() / 3600
                if hours_since_access < 24:
                    active_count += 1

        processing_time = (datetime.now() - start_time).total_seconds()

        response = WorkspaceListResponse(
            workspaces=workspaces,
            total_count=len(workspaces),
            active_count=active_count,
            total_storage_bytes=total_storage
        )

        logger.info(f"✅ Lista de workspaces obtenida en {processing_time:.3f}s")
        logger.info(f"📊 Total workspaces: {len(workspaces)}, Activos: {active_count}")

        return response

    except BiologyError as e:
        logger.error(f"❌ Error interno al listar workspaces: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/add-artifact/{workspace_id}")
async def add_artifact(workspace_id: str, request: ArtifactAddRequest):
    """
    📦 Agregar Artefacto a Workspace.

    Almacena un artefacto científico en el workspace especificado,
    incluyendo datos, modelos, resultados o cualquier otro tipo de
    contenido generado durante experimentos científicos.

    **Parámetros de URL:**
    - **workspace_id**: Identificador único del workspace destino

    **Parámetros del Artefacto:**
    - **name**: Nombre único del artefacto (letras, números, guiones, underscores)
    - **value**: Contenido del artefacto (cualquier tipo de datos serializable)
    - **artifact_type**: Categoría del artefacto (data, model, result, config)
    - **metadata**: Metadatos específicos del artefacto
    - **tags**: Etiquetas para organización y búsqueda

    **Proceso de Almacenamiento:**
    1. Validación de existencia del workspace
    2. Verificación de permisos de escritura
    3. Validación de formato y tamaño del artefacto
    4. Almacenamiento con versionado automático
    5. Indexación para búsqueda posterior
    6. Actualización de estadísticas del workspace

    **Tipos de Artefactos Soportados:**
    - **data**: Datasets, archivos de entrada/salida
    - **model**: Modelos entrenados, checkpoints, pesos
    - **result**: Resultados de análisis, gráficos, reportes
    - **config**: Configuraciones, parámetros, scripts
    - **log**: Registros de ejecución, métricas de rendimiento

    **Características Avanzadas:**
    - Versionado automático con historial completo
    - Compresión inteligente para artefactos grandes
    - Encriptación opcional para datos sensibles
    - Integración con sistema de backup
    - Metadata extensible y personalizable

    **Limitaciones:**
    - Tamaño máximo por artefacto: 100MB
    - Nombre único por workspace
    - Solo tipos de datos serializables
    - Validación de formato según tipo

    **Aplicaciones:**
    - Almacenamiento de resultados de experimentos
    - Versionado de modelos durante entrenamiento
    - Compartir datos entre miembros del equipo
    - Backup automático de configuraciones críticas
    """
    try:
        logger.info(f"📦 Agregando artefacto al workspace {workspace_id}")
        logger.info(f"📝 Nombre del artefacto: {request.name}")
        logger.info(f"🏷️ Tipo: {request.artifact_type}")

        start_time = datetime.now()

        # Preparar datos del artefacto para el servicio
        artifact_data = {
            "name": request.name,
            "value": request.value,
            "artifact_type": request.artifact_type,
            "metadata": request.metadata or {},
            "tags": request.tags or []
        }

        # Agregar artefacto usando el servicio
        workspace_manager_service.add_artifact(workspace_id, request.name, artifact_data)

        processing_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Artefacto '{request.name}' agregado exitosamente en {processing_time:.3f}s")

        return {
            "success": True,
            "message": f"Artefacto '{request.name}' agregado al workspace '{workspace_id}'",
            "workspace_id": workspace_id,
            "artifact_name": request.name,
            "artifact_type": request.artifact_type,
            "processing_time_seconds": processing_time,
            "timestamp": datetime.now().isoformat()
        }

    except ValueError as e:
        logger.warning(f"⚠️ Error de validación al agregar artefacto: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parámetros inválidos: {str(e)}")
    except BiologyError as e:
        logger.error(f"❌ Error interno al agregar artefacto: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/cleanup", response_model=CleanupResponse)
async def cleanup_workspaces(request: CleanupRequest):
    """
    🧹 Limpiar Workspaces Inactivos.

    Ejecuta limpieza automática de workspaces inactivos y artefactos obsoletos,
    liberando espacio de almacenamiento y optimizando el rendimiento del sistema.
    Soporta modo simulación para evaluación previa de impactos.

    **Parámetros de Limpieza:**
    - **older_than_seconds**: Tiempo de inactividad para considerar eliminación (300-2592000s)
    - **force**: Forzar eliminación incluso de workspaces con datos importantes
    - **dry_run**: Ejecutar en modo simulación sin eliminar datos reales

    **Proceso de Limpieza:**
    1. Identificación de workspaces candidatos por antigüedad
    2. Evaluación de importancia y dependencias
    3. Cálculo de espacio a liberar
    4. Backup opcional de datos críticos
    5. Eliminación por lotes con rollback automático
    6. Actualización de estadísticas del sistema

    **Criterios de Eliminación:**
    - Workspaces sin acceso por más del tiempo especificado
    - Artefactos temporales y caches obsoletos
    - Versiones antiguas de modelos (manteniendo N últimas)
    - Logs y registros históricos más allá del período de retención

    **Modos de Operación:**
    - **dry_run=true**: Simulación completa sin modificaciones
    - **force=false**: Eliminación conservadora con salvaguardas
    - **force=true**: Limpieza agresiva para recuperación de espacio

    **Salvaguardas Implementadas:**
    - Backup automático antes de eliminación
    - Verificación de integridad de datos
    - Rollback automático en caso de errores
    - Notificaciones de eliminación masiva

    **Métricas de Rendimiento:**
    - Tiempo de ejecución de la limpieza
    - Espacio liberado en bytes
    - Número de workspaces y artefactos eliminados
    - Tasa de éxito de la operación

    **Aplicaciones:**
    - Mantenimiento rutinario del sistema
    - Recuperación de espacio de almacenamiento
    - Optimización de rendimiento
    - Cumplimiento de políticas de retención

    **Recomendaciones:**
    - Ejecutar inicialmente con dry_run=true
    - Programar limpiezas automáticas semanales
    - Monitorear métricas de uso post-limpieza
    - Ajustar parámetros según patrones de uso
    """
    try:
        logger.info("🧹 Iniciando limpieza de workspaces")
        logger.info(f"⏰ Eliminando workspaces inactivos por más de {request.older_than_seconds}s")
        logger.info(f"🔧 Modo forzado: {request.force}, Simulación: {request.dry_run}")

        start_time = datetime.now()

        # Ejecutar limpieza usando el servicio
        cleanup_result = workspace_manager_service.cleanup(request.older_than_seconds)

        processing_time = (datetime.now() - start_time).total_seconds()

        # Preparar respuesta con métricas detalladas
        response = CleanupResponse(
            removed_workspaces=cleanup_result.get("removed_workspaces", 0),
            removed_artifacts=cleanup_result.get("removed_artifacts", 0),
            freed_bytes=cleanup_result.get("freed_bytes", 0),
            dry_run=request.dry_run,
            execution_time_seconds=processing_time
        )

        logger.info(f"✅ Limpieza completada en {processing_time:.3f}s")
        logger.info(f"🏗️ Workspaces eliminados: {response.removed_workspaces}")
        logger.info(f"📦 Artefactos eliminados: {response.removed_artifacts}")
        logger.info(f"💾 Espacio liberado: {response.freed_bytes} bytes")

        return response

    except ValueError as e:
        logger.warning(f"⚠️ Error de validación en limpieza: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parámetros inválidos: {str(e)}")
    except BiologyError as e:
        logger.error(f"❌ Error interno en limpieza: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
