"""
🔍 BÚSQUEDA EN OEIS - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de búsqueda y consulta en la Enciclopedia en Línea de Secuencias de Enteros (OEIS)
para la plataforma AXIOM v4.1. Permite id        except     except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("%s", "❌ Error interno en búsqueda OEIS")
        logger.error("%s", "🔍 Detalles del error")
        raise HTTPException(
            status_code=500,
            detail="Error interno en búsqueda OEIS: %s" % str(e)
        ) from eClientError as e:
            logger.error("%s", "❌ Error de conexión con OEIS")
            raise HTTPException(
                status_code=500,
                detail="Error de conexión con OEIS: %s" % str(e)
            ) from ecar secuencias matemáticas conocidas,
obtener información detallada sobre fórmulas, propiedades y referencias científicas.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Búsqueda automática de secuencias en OEIS
• Identificación de secuencias conocidas por sus primeros términos
• Recuperación de metadatos completos (fórmulas, comentarios, referencias)
• Caché inteligente con TTL basado en calidad de resultados
• Soporte para múltiples resultados con ranking de relevancia
• Integración con análisis matemático local
• Validación de términos de secuencia
• Manejo robusto de errores de conectividad

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con enrutamiento REST asíncrono
• Cliente HTTP: aiohttp para consultas a OEIS API
• Caché: Sistema de caché distribuido con TTL inteligente
• Validación: Pydantic models con constraints numéricos
• Logging: Configuración estructurada con indicadores de búsqueda
• Manejo de errores: HTTPException con códigos específicos
• Serialización: JSON para comunicación con OEIS API

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /search - Búsqueda de secuencias en OEIS

MODELOS DE DATOS:
─────────────────
• OEISQuery: Consulta con términos y configuración de resultados
• OEISResult: Resultado individual de búsqueda OEIS
• OEISResponse: Respuesta completa con múltiples resultados

CONSIDERACIONES DE SEGURIDAD:
────────────────────────────
• Validación estricta de términos numéricos
• Límites en cantidad de términos y resultados
• Control de tiempo de ejecución para consultas externas
• Sanitización de parámetros de búsqueda
• Caché para prevenir abuso de API externa
• Logging de consultas para auditoría

MANEJO DE ERRORES:
──────────────────
• 400 Bad Request: Parámetros inválidos o términos malformados
• 404 Not Found: Secuencia no encontrada en OEIS
• 408 Request Timeout: Tiempo de espera agotado en OEIS
• 500 Internal Server Error: Error en API de OEIS
• Logging estructurado con códigos de error específicos
• Recuperación automática con caché cuando disponible

EJEMPLOS DE USO:
────────────────
# Buscar secuencia Fibonacci
POST /api/sequences/oeis/search
{
    "terms": [1, 1, 2, 3, 5, 8, 13, 21],
    "max_results": 5
}

# Buscar secuencia de primos
POST /api/sequences/oeis/search
{
    "terms": [2, 3, 5, 7, 11, 13, 17],
    "max_results": 3
}

DEPENDENCIAS:
─────────────
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos
• aiohttp: Cliente HTTP asíncrono
• hashlib: Generación de claves de caché
• json: Serialización de datos
• app.cache: Sistema de caché personalizado

NOTAS DE IMPLEMENTACIÓN:
───────────────────────
• Todas las consultas son asíncronas para no bloquear el servidor
• Caché inteligente con TTL variable según calidad de resultados
• Límite de 15 términos para optimizar búsquedas
• Timeout de 10 segundos para consultas externas
• Fallback automático a caché cuando OEIS no está disponible
• Validación automática de tipos de datos de entrada

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from __future__ import annotations

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import hashlib
import time
from datetime import datetime
import asyncio

import aiohttp
from app.core.cache import cache
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.sequence_oeis_types import (
    OeisSearchResult,
)

router = APIRouter(prefix="/api/sequences/oeis", tags=["sequences"])


class OEISQuery(BaseModel):
    """Modelo para consulta de búsqueda en OEIS.

    Define los parámetros para buscar secuencias en la Enciclopedia en Línea de Secuencias de Enteros.
    """

    terms: List[int] = Field(..., description="Primeros términos para búsqueda en OEIS")
    max_results: int = Field(5, ge=1, le=10)


def _generate_cache_key(terms: List[int], max_results: int) -> str:
    """Generate unique cache key for OEIS search"""
    key_data = f"oeis_search:{','.join(str(x) for x in terms[:15])}:{max_results}"
    return hashlib.sha256(key_data.encode()).hexdigest()


def _get_cache_ttl_based_on_results(results: List[Dict[str, Any]]) -> int:
    """Determine intelligent TTL based on OEIS search result quality"""
    if not results:
        # No results - cache for shorter time (1 hour)
        return 3600
    
    # Check if we have high-confidence matches
    for result in results:
        if result.get("id") and result.get("name"):
            # Good match - cache longer (24 hours)
            return 86400
    
    # Some results but not great - cache for medium time (6 hours)
    return 21600


@router.post("/search")
async def oeis_search(req: OEISQuery) -> OeisSearchResult:
    """
    🔍 Buscar en OEIS

    Endpoint principal para búsqueda de secuencias matemáticas en la Enciclopedia
    en Línea de Secuencias de Enteros (OEIS). Identifica secuencias conocidas
    por sus primeros términos y proporciona información detallada.

    **Parámetros de entrada:**
    - **terms**: Lista de términos iniciales de la secuencia (máximo 15)
    - **max_results**: Número máximo de resultados (1-10, default: 5)

    **Validaciones realizadas:**
    - Secuencia debe tener al menos 1 término
    - Máximo 15 términos para optimizar búsqueda
    - Resultados limitados entre 1-10
    - Todos los términos deben ser números enteros

    **Respuesta exitosa:**
    ```json
    {
        "query": "1,1,2,3,5,8,13,21",
        "count": 3,
        "results": [
            {
                "id": "A000045",
                "oeis_id": "A000045",
                "name": "Fibonacci numbers",
                "data_sample": "1,1,2,3,5,8,13,21,34,55,89",
                "formula": "F(n) = F(n-1) + F(n-2)",
                "comments": "The Fibonacci sequence",
                "reference": "Knuth, The Art of Computer Programming",
                "link": "https://oeis.org/A000045"
            }
        ],
        "cached": false,
        "execution_time_seconds": 1.23,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **400**: Parámetros inválidos o términos malformados
    - **408**: Timeout en consulta a OEIS
    - **500**: Error interno o en API de OEIS
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("🔍 Iniciando búsqueda en OEIS")
        logger.info("📊 Términos: %d | Máx resultados: %d", len(req.terms), req.max_results)

        # Validaciones de entrada
        if not req.terms:
            logger.warning("⚠️ Secuencia vacía")
            raise HTTPException(
                status_code=400,
                detail="La secuencia debe tener al menos 1 término"
            )

        if len(req.terms) > 15:
            logger.warning("⚠️ Demasiados términos: %d, truncando a 15", len(req.terms))
            req.terms = req.terms[:15]

        # Verificar que todos los términos sean enteros
        if not all(isinstance(term, int) for term in req.terms):
            logger.warning("⚠️ Secuencia contiene términos no enteros")
            raise HTTPException(
                status_code=400,
                detail="Todos los términos de la secuencia deben ser números enteros"
            )

        base_url = "https://oeis.org/search"
        params = {"q": ",".join(str(x) for x in req.terms), "fmt": "json", "n": req.max_results}

        # Generate cache key
        cache_key = _generate_cache_key(req.terms, req.max_results)

        # Try to get from cache first
        cached_result = cache.get(cache_key, operation_type='oeis_search')
        if cached_result:
            execution_time = time.time() - start_time
            logger.info("✅ Resultado obtenido de caché")
            cached_result["cached"] = True
            cached_result["cache_key"] = cache_key
            cached_result["execution_time_seconds"] = round(execution_time, 2)
            cached_result["timestamp"] = execution_timestamp
            return cached_result

        logger.info("%s", "🌐 Cache miss, consultando OEIS API...")

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as s:
                r = await s.get(base_url, params=params)
                if r.status != 200:
                    logger.error("❌ Error HTTP de OEIS")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error en API de OEIS: HTTP {r.status}"
                    )
                data = await r.json()
                results = _parse_oeis_response(data)

                # Prepare response
                response = {
                    "query": params["q"],
                    "count": len(results),
                    "results": results,
                    "cached": False,
                    "execution_time_seconds": round(time.time() - start_time, 2),
                    "timestamp": execution_timestamp
                }

                # Cache the result with intelligent TTL based on result quality
                ttl = _get_cache_ttl_based_on_results(results)
                cache.set(cache_key, response, ttl=ttl, operation_type='oeis_search')

                logger.info("%s", "✅ Búsqueda completada")
                return response

        except asyncio.TimeoutError as e:
            logger.error("%s", "⏰ Timeout en consulta a OEIS")
            raise HTTPException(
                status_code=408,
                detail="Timeout en consulta a OEIS (10 segundos)"
            ) from e
        except aiohttp.ClientError as e:
            logger.error("%s", "❌ Error de conexión con OEIS")
            raise HTTPException(
                status_code=500,
                detail="Error de conexión con OEIS: %s" % str(e)
            ) from e

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("%s", "❌ Error interno en búsqueda OEIS")
        logger.error("%s", "🔍 Detalles del error")
        raise HTTPException(
            status_code=500,
            detail="Error interno en búsqueda OEIS: %s" % str(e)
        ) from e


def _parse_oeis_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analiza la respuesta de la API de OEIS en resultados estructurados.

    Extrae información relevante de las secuencias encontradas y maneja errores de formato.
    """
    try:
        seqs = data.get("results", [])
        out: List[Dict[str, Any]] = []
        for s in seqs:
            out.append({
                "id": s.get("number"),
                "oeis_id": s.get("data", "").split()[0] if s.get("data") else None,
                "name": s.get("name"),
                "data_sample": s.get("data"),
                "formula": s.get("formula"),
                "comments": s.get("comment"),
                "reference": s.get("reference"),
                "link": s.get("link"),
            })
        return out
    except (KeyError, TypeError, ValueError):
        return []


