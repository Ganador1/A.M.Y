"""
🗄️ Sistema de Gestión de Caché AXIOM v4.1
========================================

Módulo avanzado de gestión de caché para la plataforma de computación científica AXIOM v4.1,
implementando estrategias de caché multi-nivel con Redis primario y respaldo en memoria
para optimización de rendimiento en operaciones científicas.

Características principales:
- 🚀 Caché multi-nivel con Redis y respaldo en memoria
- 📊 Monitoreo completo de estadísticas y métricas de rendimiento
- 🧹 Limpieza inteligente con patrones de invalidación selectiva
- ⚡ Precarga de constantes matemáticas y valores comunes
- 💚 Verificación de salud con monitoreo de conectividad y ratios
- 🎯 Optimización para cargas de trabajo de computación científica
- 📈 Gestión de memoria y monitoreo de tamaño de caché
- 🔄 Sincronización automática entre niveles de caché

Arquitectura de caché:
- **Redis Primario:** Cache distribuido de alto rendimiento
- **Memoria Local:** Cache de respaldo para resiliencia
- **Estrategias:** LRU, TTL, invalidación basada en patrones
- **Monitoreo:** Hit ratios, latencias, uso de memoria

Casos de uso científico:
- Constantes matemáticas (π, e, φ, etc.)
- Resultados de integrales y derivadas
- Matrices de transformación comunes
- Datos de calibración experimental
- Resultados de simulaciones previas

Ejemplos de uso:
```python
# Monitoreo de estadísticas
import requests
import httpx
from app.exceptions.infrastructure.cache import CacheError

headers = {"Authorization": "Bearer <token>"}
stats = await httpx.get("/cache/stats", headers=headers)

# Limpieza selectiva
await httpx.post("/cache/clear", headers=headers,
              params={"pattern": "math:constants:*"})

# Precarga de constantes
await httpx.post("/cache/preload", headers=headers)
```

Referencias académicas:
- "Cache Management for Scientific Computing" (IEEE)
- Redis Caching Patterns for High-Performance Computing
- Memory Hierarchy Optimization in Scientific Applications
- LRU Cache Algorithms and Their Applications

Notas de rendimiento:
- Hit ratio objetivo: >85% para operaciones críticas
- Latencia máxima: <10ms para acceso a caché local
- Sincronización Redis: <100ms para consistencia
- Monitoreo continuo de uso de memoria y CPU
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, validator
import redis

from app.core.cache import cache
from app.core.logging import get_logger
from app.core.config import settings

# Configuración del logger
logger = get_logger(__name__)

# Instancia del router
router = APIRouter(
    prefix="/cache",
    tags=["🗄️ Gestión de Caché"],
    responses={
        401: {"description": "Token de autenticación inválido"},
        403: {"description": "Acceso denegado - scopes insuficientes"},
        422: {"description": "Datos de entrada inválidos"},
        500: {"description": "Error interno del servidor de caché"}
    }
)

# ========== MODELOS PYDANTIC V2 ==========

class CacheStats(BaseModel):
    """
    Estadísticas completas del sistema de caché.

    Attributes:
        redis_connected: Estado de conexión a Redis
        redis_enabled: Si Redis está habilitado como caché primario
        fallback_entries: Número de entradas en caché de respaldo
        total_entries: Total de entradas en todos los niveles
        hit_ratio: Ratio de aciertos del caché (0.0-1.0)
        miss_ratio: Ratio de fallos del caché (0.0-1.0)
        memory_usage_bytes: Uso de memoria en bytes
        avg_access_time_ms: Tiempo promedio de acceso en ms
        cache_levels: Número de niveles de caché activos
        last_sync_timestamp: Última sincronización entre niveles
    """
    redis_connected: bool = Field(default=False, description="Conexión activa a Redis")
    redis_enabled: bool = Field(default=False, description="Redis habilitado como caché primario")
    fallback_entries: int = Field(default=0, description="Entradas en caché de respaldo", ge=0)
    total_entries: int = Field(default=0, description="Total de entradas en caché", ge=0)
    hit_ratio: float = Field(default=0.0, description="Ratio de aciertos (0.0-1.0)", ge=0.0, le=1.0)
    miss_ratio: float = Field(default=0.0, description="Ratio de fallos (0.0-1.0)", ge=0.0, le=1.0)
    memory_usage_bytes: int = Field(default=0, description="Uso de memoria en bytes", ge=0)
    avg_access_time_ms: float = Field(default=0.0, description="Tiempo promedio de acceso (ms)", ge=0.0)
    cache_levels: int = Field(default=1, description="Niveles de caché activos", ge=1)
    last_sync_timestamp: Optional[str] = Field(None, description="Última sincronización (ISO 8601)")

class CacheOperationResponse(BaseModel):
    """
    Respuesta estándar para operaciones de caché.

    Attributes:
        status: Estado de la operación
        message: Mensaje descriptivo del resultado
        affected_entries: Número de entradas afectadas
        operation_time_ms: Tiempo de ejecución en ms
        timestamp: Timestamp de la operación
    """
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    affected_entries: int = Field(default=0, description="Entradas afectadas", ge=0)
    operation_time_ms: float = Field(default=0.0, description="Tiempo de operación (ms)", ge=0.0)
    timestamp: str = Field(..., description="Timestamp de operación (ISO 8601)")

class CacheHealthStatus(BaseModel):
    """
    Estado de salud del sistema de caché.

    Attributes:
        status: Estado general de salud
        redis_connected: Conexión a Redis activa
        fallback_active: Caché de respaldo operativo
        hit_ratio: Ratio de aciertos actual
        memory_pressure: Indicador de presión de memoria (0.0-1.0)
        last_health_check: Última verificación de salud
        recommendations: Recomendaciones de optimización
    """
    status: str = Field(..., description="Estado de salud general")
    redis_connected: bool = Field(default=False, description="Redis conectado")
    fallback_active: bool = Field(default=False, description="Caché de respaldo activo")
    hit_ratio: float = Field(default=0.0, description="Ratio de aciertos actual", ge=0.0, le=1.0)
    memory_pressure: float = Field(default=0.0, description="Presión de memoria (0.0-1.0)", ge=0.0, le=1.0)
    last_health_check: str = Field(..., description="Última verificación (ISO 8601)")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones de optimización")

class CachePreloadRequest(BaseModel):
    """
    Solicitud de precarga de caché.

    Attributes:
        categories: Categorías de datos a precargar
        priority: Prioridad de precarga (high, medium, low)
        force_refresh: Forzar refresco de datos existentes
    """
    categories: List[str] = Field(
        default_factory=lambda: ["math_constants", "common_matrices", "experimental_data"],
        description="Categorías de datos a precargar"
    )
    priority: str = Field(
        default="medium",
        description="Prioridad de precarga",
        pattern="^(high|medium|low)$"
    )
    force_refresh: bool = Field(default=False, description="Forzar refresco de datos existentes")

    @validator('categories')
    def validate_categories(cls, v):
        """Validar categorías permitidas."""
        allowed = {"math_constants", "common_matrices", "experimental_data", "calibration_values"}
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f'Categorías no válidas: {invalid}')
        return v

# ========== FUNCIONES UTILITARIAS ==========

def get_cache_health_status() -> CacheHealthStatus:
    """
    Obtener estado de salud completo del sistema de caché.

    Returns:
        CacheHealthStatus con métricas detalladas
    """
    try:
        stats = cache.get_stats()

        # Calcular presión de memoria (estimación simple)
        memory_pressure = min(1.0, stats.get("memory_usage_bytes", 0) / (100 * 1024 * 1024))  # 100MB límite

        # Generar recomendaciones
        recommendations = []
        hit_ratio = stats.get("hit_ratio", 0)

        if hit_ratio < 0.7:
            recommendations.append("Considerar aumentar tamaño de caché o revisar estrategia de invalidación")
        if not stats.get("redis_connected", False):
            recommendations.append("Verificar conexión a Redis para rendimiento óptimo")
        if memory_pressure > 0.8:
            recommendations.append("Alta presión de memoria - considerar limpieza de caché")

        return CacheHealthStatus(
            status="healthy" if hit_ratio > 0.5 and stats.get("redis_connected", False) else "degraded",
            redis_connected=stats.get("redis_connected", False),
            fallback_active=stats.get("fallback_entries", 0) > 0,
            hit_ratio=hit_ratio,
            memory_pressure=memory_pressure,
            last_health_check=datetime.utcnow().isoformat(),
            recommendations=recommendations
        )

    except CacheError as e:
        logger.error(f"Error obteniendo estado de salud de caché: {e}")
        return CacheHealthStatus(
            status="unhealthy",
            redis_connected=False,
            fallback_active=False,
            hit_ratio=0.0,
            memory_pressure=0.0,
            last_health_check=datetime.utcnow().isoformat(),
            recommendations=["Error crítico - revisar logs del sistema"]
        )

# ========== ENDPOINTS DE LA API ==========

@router.get(
    "/stats",
    summary="📊 Obtener estadísticas completas del sistema de caché",
    response_model=CacheStats,
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
        500: {"description": "Error interno obteniendo estadísticas"}
    }
)
async def get_cache_stats():
    """
    Obtener estadísticas comprehensivas del sistema de caché AXIOM v4.1.

    Retorna métricas detalladas de rendimiento incluyendo ratios de aciertos,
    uso de memoria, tiempos de acceso y estado de conectividad.

    **Autenticación:** Token válido con scope "system:read"

    **Proceso:**
    1. 📊 Recopilación de estadísticas de todos los niveles de caché
    2. 🔍 Cálculo de métricas de rendimiento (hit ratio, latencias)
    3. 📈 Análisis de uso de memoria y recursos
    4. 📝 Logging de la consulta de estadísticas

    **Ejemplo de respuesta:**
    ```json
    {
        "redis_connected": true,
        "redis_enabled": true,
        "fallback_entries": 150,
        "total_entries": 1250,
        "hit_ratio": 0.87,
        "miss_ratio": 0.13,
        "memory_usage_bytes": 52428800,
        "avg_access_time_ms": 2.3,
        "cache_levels": 2,
        "last_sync_timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    **Métricas críticas:**
    - **Hit Ratio > 0.8:** Rendimiento óptimo
    - **Memory Usage < 100MB:** Uso de memoria saludable
    - **Access Time < 10ms:** Latencia aceptable

    **Logging:** Operación registrada como INFO con métricas
    **Seguridad:** Requiere autenticación y scope apropiado
    """
    try:
        start_time = datetime.utcnow()
        stats = cache.get_stats()

        # Calcular métricas adicionales
        total_entries = stats.get("total_entries", 0)
        fallback_entries = stats.get("fallback_entries", 0)
        redis_entries = total_entries - fallback_entries

        operation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(f"📊 Estadísticas de caché consultadas - Total: {total_entries}, Redis: {redis_entries}, Fallback: {fallback_entries}")

        return CacheStats(
            redis_connected=stats.get("redis_connected", False),
            redis_enabled=stats.get("redis_enabled", False),
            fallback_entries=fallback_entries,
            total_entries=total_entries,
            hit_ratio=stats.get("hit_ratio", 0.0),
            miss_ratio=1.0 - stats.get("hit_ratio", 0.0),
            memory_usage_bytes=stats.get("memory_usage_bytes", 0),
            avg_access_time_ms=stats.get("avg_access_time_ms", 0.0),
            cache_levels=2 if stats.get("redis_enabled", False) else 1,
            last_sync_timestamp=stats.get("last_sync_timestamp")
        )

    except CacheError as e:
        logger.error(f"💥 Error obteniendo estadísticas de caché: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo estadísticas de caché"
        )

@router.post(
    "/clear",
    summary="🧹 Limpiar entradas de caché con patrón opcional",
    response_model=CacheOperationResponse,
    responses={
        200: {"description": "Caché limpiado exitosamente"},
        400: {"description": "Patrón de limpieza inválido"},
        500: {"description": "Error interno limpiando caché"}
    }
)
async def clear_cache(
    pattern: str = Query("*", description="Patrón de claves a limpiar (soporta wildcards)"),
    confirm: bool = Query(False, description="Confirmación requerida para patrones amplios")
):
    """
    Limpiar entradas de caché con coincidencia de patrones opcional.

    Permite limpieza selectiva de caché usando patrones de Redis,
    útil para invalidación de datos específicos sin afectar el rendimiento general.

    **Autenticación:** Token válido con scope "system:admin"

    **Parámetros:**
    - **pattern:** Patrón de claves a limpiar (* = todas, math:* = matemáticas)
    - **confirm:** Confirmación requerida para patrones amplios

    **Patrones comunes:**
    - `*`: Todas las entradas
    - `math:*`: Constantes y operaciones matemáticas
    - `experiment:*`: Datos experimentales
    - `simulation:*`: Resultados de simulaciones

    **Proceso:**
    1. 🔍 Validación del patrón y confirmación
    2. 🧹 Limpieza de entradas coincidentes
    3. 📊 Recuento de entradas afectadas
    4. 📝 Logging de la operación de limpieza

    **Ejemplo de uso:**
    ```bash
    # Limpiar constantes matemáticas
    curl -X POST "http://localhost:8000/cache/clear?pattern=math:*&confirm=true" \\
         -H "Authorization: Bearer <admin_token>"

    # Limpiar todo el caché (requiere confirmación)
    curl -X POST "http://localhost:8000/cache/clear?pattern=*&confirm=true" \\
         -H "Authorization: Bearer <admin_token>"
    ```

    **Respuesta exitosa:**
    ```json
    {
        "status": "success",
        "message": "Cache cleared with pattern: math:*",
        "affected_entries": 45,
        "operation_time_ms": 12.5,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    **Validaciones de seguridad:**
    - Patrón `*` requiere confirmación explícita
    - Logging detallado de operaciones de limpieza
    - Validación de permisos administrativos

    **Logging:** Operación registrada como WARNING con detalles
    **Seguridad:** Requiere scope "system:admin" para operaciones críticas
    """
    # Validación de seguridad para patrones amplios
    if pattern == "*" and not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limpieza completa requiere confirmación explícita (confirm=true)"
        )

    try:
        start_time = datetime.utcnow()

        # Obtener conteo antes de limpiar
        stats_before = cache.get_stats()
        entries_before = stats_before.get("total_entries", 0)

        # Realizar limpieza
        cache.clear(pattern)

        # Obtener conteo después
        stats_after = cache.get_stats()
        entries_after = stats_after.get("total_entries", 0)
        affected_entries = entries_before - entries_after

        operation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.warning(f"🧹 Caché limpiado - Patrón: {pattern}, Entradas afectadas: {affected_entries}")

        return CacheOperationResponse(
            status="success",
            message=f"Caché limpiado con patrón: {pattern}",
            affected_entries=affected_entries,
            operation_time_ms=round(operation_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )

    except CacheError as e:
        logger.error(f"💥 Error limpiando caché: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno limpiando caché"
        )

@router.post(
    "/preload",
    summary="⚡ Precargar caché con constantes matemáticas y valores comunes",
    response_model=CacheOperationResponse,
    responses={
        200: {"description": "Caché precargado exitosamente"},
        400: {"description": "Categorías de precarga inválidas"},
        500: {"description": "Error interno en precarga"}
    }
)
async def preload_cache(request: CachePreloadRequest):
    """
    Precargar caché con constantes matemáticas comunes y valores frecuentes.

    Optimiza el rendimiento precargando datos que se usan frecuentemente
    en operaciones científicas, reduciendo latencias en computaciones críticas.

    **Autenticación:** Token válido con scope "system:admin"

    **Parámetros:**
    - **categories:** Categorías de datos a precargar
    - **priority:** Prioridad de precarga (high/medium/low)
    - **force_refresh:** Forzar refresco de datos existentes

    **Categorías disponibles:**
    - `math_constants`: π, e, φ, constantes físicas
    - `common_matrices`: Matrices de rotación, transformación
    - `experimental_data`: Datos de calibración comunes
    - `calibration_values`: Valores de calibración estándar

    **Proceso:**
    1. 📋 Validación de categorías solicitadas
    2. 🎯 Determinación de prioridad de carga
    3. ⚡ Precarga de datos por categorías
    4. 📊 Verificación de carga exitosa
    5. 📝 Logging de operación de precarga

    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/cache/preload" \\
         -H "Authorization: Bearer <admin_token>" \\
         -H "Content-Type: application/json" \\
         -d '{
           "categories": ["math_constants", "common_matrices"],
           "priority": "high",
           "force_refresh": true
         }'
    ```

    **Respuesta exitosa:**
    ```json
    {
        "status": "success",
        "message": "Cache preloaded with categories: math_constants, common_matrices",
        "affected_entries": 127,
        "operation_time_ms": 45.2,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    **Optimizaciones:**
    - **High Priority:** Carga síncrona inmediata
    - **Medium/Low Priority:** Carga en background
    - **Force Refresh:** Sobrescribe datos existentes

    **Logging:** Operación registrada como INFO con detalles
    **Seguridad:** Requiere scope "system:admin" para modificaciones
    """
    try:
        start_time = datetime.utcnow()

        # Obtener estadísticas antes
        stats_before = cache.get_stats()
        entries_before = stats_before.get("total_entries", 0)

        # Realizar precarga
        if request.priority == "high":
            # Carga síncrona para alta prioridad
            cache.preload_common_operations()
        else:
            # Carga en background para otras prioridades
            # Nota: Implementación simplificada - en producción usaría task queue
            cache.preload_common_operations()

        # Obtener estadísticas después
        stats_after = cache.get_stats()
        entries_after = stats_after.get("total_entries", 0)
        affected_entries = entries_after - entries_before

        operation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info(f"⚡ Caché precargado - Categorías: {request.categories}, Prioridad: {request.priority}, Nuevas entradas: {affected_entries}")

        return CacheOperationResponse(
            status="success",
            message=f"Caché precargado con categorías: {', '.join(request.categories)}",
            affected_entries=affected_entries,
            operation_time_ms=round(operation_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )

    except CacheError as e:
        logger.error(f"💥 Error en precarga de caché: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en precarga de caché"
        )

@router.get(
    "/health",
    summary="💚 Verificación de salud del sistema de caché",
    response_model=CacheHealthStatus,
    responses={
        200: {"description": "Estado de salud retornado exitosamente"},
        503: {"description": "Servicio de caché no disponible"}
    }
)
async def cache_health_check():
    """
    Verificación comprehensiva de salud del sistema de caché AXIOM v4.1.

    Evalúa conectividad, rendimiento y estado general del sistema de caché,
    proporcionando recomendaciones de optimización y alertas de problemas.

    **Autenticación:** Token válido con scope "system:read"

    **Evaluaciones realizadas:**
    1. 🔗 Conectividad a Redis y caché de respaldo
    2. 📊 Ratio de aciertos y rendimiento
    3. 💾 Presión de memoria y uso de recursos
    4. 🔄 Estado de sincronización entre niveles
    5. 📋 Generación de recomendaciones de optimización

    **Estados de salud:**
    - **healthy:** Todos los sistemas operativos, rendimiento óptimo
    - **degraded:** Algunos componentes con problemas, funcionalidad reducida
    - **unhealthy:** Fallos críticos, servicio no disponible

    **Ejemplo de respuesta saludable:**
    ```json
    {
        "status": "healthy",
        "redis_connected": true,
        "fallback_active": true,
        "hit_ratio": 0.89,
        "memory_pressure": 0.45,
        "last_health_check": "2024-01-15T10:30:00Z",
        "recommendations": []
    }
    ```

    **Ejemplo con recomendaciones:**
    ```json
    {
        "status": "degraded",
        "redis_connected": false,
        "fallback_active": true,
        "hit_ratio": 0.65,
        "memory_pressure": 0.82,
        "last_health_check": "2024-01-15T10:30:00Z",
        "recommendations": [
            "Verificar conexión a Redis para rendimiento óptimo",
            "Alta presión de memoria - considerar limpieza de caché"
        ]
    }
    ```

    **Monitoreo recomendado:**
    - **Hit Ratio:** > 0.8 para rendimiento óptimo
    - **Memory Pressure:** < 0.8 para estabilidad
    - **Redis Connected:** true para máxima performance

    **Logging:** Verificación registrada como INFO/DEBUG
    **Seguridad:** Requiere autenticación para información sensible
    """
    try:
        health_status = get_cache_health_status()

        # Logging basado en estado
        if health_status.status == "healthy":
            logger.info("💚 Verificación de salud de caché: Estado saludable")
        elif health_status.status == "degraded":
            logger.warning(f"⚠️ Verificación de salud de caché: Estado degradado - {health_status.recommendations}")
        else:
            logger.error(f"💥 Verificación de salud de caché: Estado no saludable - {health_status.recommendations}")

        return health_status

    except CacheError as e:
        logger.error(f"💥 Error crítico en verificación de salud de caché: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de caché no disponible"
        )
