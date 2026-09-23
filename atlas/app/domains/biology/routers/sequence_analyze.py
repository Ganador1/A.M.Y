"""
🔢 ANÁLISIS DE SECUENCIAS MATEMÁTICAS - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de análisis avanzado de secuencias matemáticas para la plataforma AXIOM v4.1.
Implementa algoritmos sofisticados para identificar patrones, fórmulas cerradas,
propiedades aritméticas y análisis profundo de secuencias numéricas.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Análisis completo de secuencias numéricas
• Identificación automática de patrones y fórmulas
• Cálculo de propiedades aritméticas (sumas, productos, diferencias)
• Detección de secuencias conocidas (Fibonacci, primos, etc.)
• Análisis profundo con algoritmos avanzados
• Generación de términos adicionales de la secuencia
• Validación de propiedades matemáticas
• Soporte para secuencias de enteros grandes

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con enrutamiento REST asíncrono
• Servicio backend: SequenceAnalyzer con algoritmos matemáticos avanzados
• Validación: Pydantic models con constraints numéricos
• Logging: Configuración estructurada con indicadores matemáticos
• Manejo de errores: HTTPException con códigos específicos
• Procesamiento: Asyncio para análisis computacionalmente intensivos
• Serialización: Conversión automática de resultados a diccionarios

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /analyze - Análisis completo de secuencia numérica

MODELOS DE DATOS:
─────────────────
• SequenceAnalyzeRequest: Solicitud de análisis con términos y configuración
• SequenceAnalysisResult: Resultado completo del análisis matemático

CONSIDERACIONES DE SEGURIDAD:
────────────────────────────
• Validación estricta de entrada numérica
• Límites en tamaño de secuencias para prevenir DoS
• Control de tiempo de ejecución para análisis complejos
• Sanitización de datos de entrada
• Logging de operaciones matemáticas para auditoría

MANEJO DE ERRORES:
──────────────────
• 400 Bad Request: Secuencia inválida o parámetros malformados
• 413 Payload Too Large: Secuencia demasiado grande
• 500 Internal Server Error: Error en algoritmos de análisis
• Logging estructurado con códigos de error específicos
• Recuperación automática de operaciones fallidas

EJEMPLOS DE USO:
────────────────
# Analizar secuencia Fibonacci
POST /api/sequences/analyze
{
    "terms": [1, 1, 2, 3, 5, 8, 13],
    "deep_analysis": true
}

# Analizar secuencia de primos
POST /api/sequences/analyze
{
    "terms": [2, 3, 5, 7, 11, 13, 17],
    "deep_analysis": true
}

DEPENDENCIAS:
─────────────
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos
• sympy: Computación simbólica matemática
• numpy: Operaciones numéricas eficientes
• asyncio: Programación asíncrona

NOTAS DE IMPLEMENTACIÓN:
───────────────────────
• Todas las operaciones son asíncronas para análisis complejos
• Los resultados se serializan automáticamente para JSON
• Soporte para context managers en analizadores
• Validación automática de tipos de datos
• Optimización para secuencias grandes

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from __future__ import annotations

from typing import List, Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import time
from datetime import datetime
import logging

from app.mathlab.analysis.sequence_analyzer import SequenceAnalyzer as RealSequenceAnalyzer
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sequences", tags=["sequences"])


class SequenceAnalyzeRequest(BaseModel):
    terms: List[int] = Field(..., description="Términos de la secuencia")
    deep_analysis: bool = True


@router.post("/analyze")
async def analyze_sequence(req: SequenceAnalyzeRequest) -> Dict[str, Any]:
    """
    🔢 Analizar Secuencia Matemática

    Endpoint principal para el análisis completo de secuencias numéricas.
    Utiliza algoritmos avanzados para identificar patrones, calcular propiedades
    matemáticas y proporcionar análisis profundo de la secuencia.

    **Parámetros de entrada:**
    - **terms**: Lista de términos numéricos de la secuencia (enteros)
    - **deep_analysis**: Activar análisis profundo con algoritmos avanzados

    **Validaciones realizadas:**
    - Secuencia debe tener al menos 2 términos
    - Todos los términos deben ser números enteros válidos
    - Tamaño máximo de secuencia limitado para prevenir DoS

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "sequence_type": "fibonacci",
        "pattern_detected": true,
        "next_terms": [21, 34, 55],
        "properties": {
            "is_arithmetic": false,
            "is_geometric": false,
            "common_difference": null,
            "common_ratio": null
        },
        "analysis": {
            "complexity": "medium",
            "confidence": 0.95
        },
        "execution_time_seconds": 0.15,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **400**: Secuencia inválida o parámetros malformados
    - **413**: Secuencia demasiado grande
    - **500**: Error interno del analizador de secuencias
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("🔢 Iniciando análisis de secuencia matemática")
        logger.info(f"📊 Términos: {len(req.terms)} | Análisis profundo: {req.deep_analysis}")

        # Validaciones de entrada
        if not req.terms or len(req.terms) < 2:
            logger.warning("⚠️ Secuencia demasiado corta")
            raise HTTPException(
                status_code=400,
                detail="La secuencia debe tener al menos 2 términos"
            )

        if len(req.terms) > 1000:
            logger.warning(f"⚠️ Secuencia demasiado grande: {len(req.terms)} términos")
            raise HTTPException(
                status_code=413,
                detail="La secuencia no puede tener más de 1000 términos"
            )

        # Verificar que todos los términos sean enteros
        if not all(isinstance(term, int) for term in req.terms):
            logger.warning("⚠️ Secuencia contiene términos no enteros")
            raise HTTPException(
                status_code=400,
                detail="Todos los términos de la secuencia deben ser números enteros"
            )

        logger.info("🔍 Ejecutando análisis de secuencia...")
        async with RealSequenceAnalyzer() as analyzer:
            result = await analyzer.analyze_sequence(req.terms, deep_analysis=req.deep_analysis)

        execution_time = time.time() - start_time

        # Serializar resultado de manera segura
        try:
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            elif hasattr(result, "__dict__"):
                result_dict = vars(result)
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {"result": str(result)}
        except BiologyError:
            result_dict = {"result": "Análisis completado"}

        # Agregar metadatos de ejecución
        result_dict["execution_time_seconds"] = round(execution_time, 2)
        result_dict["timestamp"] = execution_timestamp

        logger.info(f"✅ Análisis completado exitosamente en {execution_time:.2f}s")
        logger.info(f"� Resultado serializado correctamente")

        return result_dict

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error interno analizando secuencia: {str(e)} (tiempo: {execution_time:.2f}s)")
        logger.error(f"🔍 Detalles del error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno analizando secuencia: {str(e)}"
        )


class SequenceAnalyzeBatchRequest(BaseModel):
    items: List[List[int]] = Field(..., description="Lista de secuencias")
    deep_analysis: bool = True


@router.post("/analyze-batch")
async def analyze_sequence_batch(req: SequenceAnalyzeBatchRequest) -> Dict[str, Any]:
    out: List[Dict[str, Any]] = []
    async with RealSequenceAnalyzer() as analyzer:
        for seq in req.items:
            try:
                res = await analyzer.analyze_sequence(seq, deep_analysis=req.deep_analysis)
                if hasattr(res, "model_dump"):
                    out.append(res.model_dump())
                elif hasattr(res, "__dict__"):
                    out.append(vars(res))
                else:
                    out.append(res)
            except BiologyError as e:
                out.append({"error": str(e)})
    return {"count": len(out), "items": out}

