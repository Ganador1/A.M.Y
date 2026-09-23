"""
Superconducting Circuit Design Router for AXIOM Physics Domain
============================================================

API endpoints para diseño optimizado de circuitos superconductores
usando diferenciación automática y optimización basada en gradientes.
"""

import datetime
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.domains.physics.models import responses
from app.domains.physics.quantum.superconducting_design_service import SuperconductingDesignService
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quantum/superconducting", tags=["quantum-superconducting"])
service = SuperconductingDesignService()


@router.get("/")
async def superconducting_design_info() -> Dict[str, Any]:
    """
    🧬 Información sobre el servicio de diseño superconductor
    """
    return service.get_service_info()


@router.post("/optimize")
async def optimize_qubit_parameters(request: Dict[str, Any]) -> responses.BaseResponse:
    """
    ⚡ Optimización de parámetros de qubit superconductor

    Optimiza frecuencias, anarmonicidades y acoplamientos usando
    diferenciación automática para maximizar métricas objetivo.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("⚡ Optimizando parámetros de qubit con config: %s", request)

        result = await service.process_request({
            "operation": "optimize_qubit_parameters",
            "parameters": request
        })

        if "error" in result:
            logger.error("❌ Optimización falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "torch")
            }
        }

        logger.info("✅ Optimización completada - objetivo final: %.6f", result["results"].get("final_objective", 0.0))

        return responses.BaseResponse(
            success=True,
            message="Optimización de qubit completada exitosamente",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en optimización de qubit: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en optimización de qubit: {str(e)}"
        ) from e


@router.post("/spectrum")
async def compute_energy_spectrum(request: Dict[str, Any]) -> responses.BaseResponse:
    """
    📊 Cálculo de espectro de energía para diseño de qubit

    Calcula niveles de energía y gradientes para parámetros de qubit dados.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📊 Calculando espectro de energía con parámetros: %s", request)

        result = await service.process_request({
            "operation": "compute_energy_spectrum",
            "parameters": request
        })

        if "error" in result:
            logger.error("❌ Cálculo de espectro falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "hybrid")
            }
        }

        num_levels = result["results"].get("num_levels", 0)
        logger.info("✅ Espectro calculado - %d niveles de energía", num_levels)

        return responses.BaseResponse(
            success=True,
            message=f"Espectro de energía calculado con {num_levels} niveles",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en cálculo de espectro: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en cálculo de espectro: {str(e)}"
        ) from e


@router.post("/gate-fidelity")
async def optimize_gate_fidelity(request: Dict[str, Any]) -> responses.BaseResponse:
    """
    🎯 Optimización de fidelidad de compuertas

    Optimiza diseño para maximizar fidelidad de operaciones de compuerta.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🎯 Optimizando fidelidad de compuertas: %s", request)

        result = await service.process_request({
            "operation": "optimize_gate_fidelity",
            "parameters": request
        })

        if "error" in result:
            logger.error("❌ Optimización de fidelidad falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "analytical")
            }
        }

        fidelity = result["results"].get("optimized_fidelity", 0.0)
        logger.info("✅ Fidelidad optimizada - %.4f", fidelity)

        return responses.BaseResponse(
            success=True,
            message=f"Fidelidad de compuerta optimizada: {fidelity:.4f}",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en optimización de fidelidad: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en optimización de fidelidad: {str(e)}"
        ) from e


@router.post("/layout")
async def design_circuit_layout(request: Dict[str, Any]) -> responses.BaseResponse:
    """
    🏗️ Diseño de layout de circuito superconductor

    Diseña layout físico basado en requisitos de conectividad y optimización.
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("🏗️ Diseñando layout de circuito: %s", request)

        result = await service.process_request({
            "operation": "design_circuit_layout",
            "parameters": request
        })

        if "error" in result:
            logger.error("❌ Diseño de layout falló: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        response_data = {
            **result,
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "framework": result.get("framework", "analytical")
            }
        }

        layout_type = result["results"].get("layout_type", "unknown")
        logger.info("✅ Layout diseñado - tipo: %s", layout_type)

        return responses.BaseResponse(
            success=True,
            message=f"Layout de circuito diseñado: {layout_type}",
            data=response_data
        )

    except HTTPException:
        raise
    except QuantumError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error en diseño de layout: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error en diseño de layout: {str(e)}"
        ) from e
