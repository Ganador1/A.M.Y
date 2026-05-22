"""
Router de Matemáticas y Física - AXIOM Meta 4.1
==============================================

Este módulo implementa el router para el servicio de matemáticas y física en la plataforma AXIOM.
Proporciona capacidades avanzadas para procesamiento de problemas matemáticos, verificación de teoremas,
simulaciones físicas y cálculos científicos interdisciplinarios.

Capacidades Principales:
----------------------
- **Verificación de Teoremas**: Validación formal de teoremas matemáticos usando múltiples métodos (SymPy, SMT2, Lean)
- **Astronomía Computacional**: Análisis de tránsito de exoplanetas y lentes gravitacionales
- **Física de Partículas**: Conteo de jets y análisis de eventos de partículas
- **Computación Cuántica**: Ejecución de algoritmos cuánticos y simulaciones
- **Routing Inteligente**: Enrutamiento automático basado en dominio científico
- **Orquestación Multi-Dominio**: Coordinación entre servicios matemáticos y físicos

Endpoints Disponibles:
--------------------
- POST /api/math-physics/route: Enruta solicitud a servicio apropiado por dominio
- POST /api/math-physics/theorem/verify: Verifica teoremas matemáticos
- POST /api/math-physics/theorem/smt2: Verifica teoremas usando SMT2
- POST /api/math-physics/theorem/lean: Verifica teoremas usando Lean
- POST /api/math-physics/astronomy/transit: Análisis de tránsito de exoplanetas
- POST /api/math-physics/particles/jets: Conteo de jets en física de partículas
- POST /api/math-physics/quantum/run: Ejecución de algoritmos cuánticos
- POST /api/math-physics/astronomy/lensing: Simulación de lentes gravitacionales

Dependencias:
-----------
- FastAPI: Framework web para APIs REST
- app.services.math_physics_orchestrator: Orquestador principal de matemáticas y física
- sympy: Biblioteca de matemáticas simbólicas para verificación de teoremas
- z3: Solver SMT para verificación formal
- Lean: Sistema de verificación de teoremas interactivo

Uso del Servicio:
---------------
```python
from fastapi import FastAPI
from app.domains.mathematics.services.math_physics import router
from app.exceptions.domain.physics import QuantumError

app = FastAPI()
app.include_router(router)

# Ejemplo de verificación de teorema
response = await client.post("/api/math-physics/theorem/verify",
    json={
        "statement": "x^2 + 2*x + 1 = (x + 1)^2",
        "method": "sympy"
    })

# Ejemplo de análisis astronómico
response = await client.post("/api/math-physics/astronomy/transit",
    json={"light_curve": [0.98, 0.95, 0.92, 0.95, 0.98]})
```

Consideraciones de Seguridad:
---------------------------
- Validación de entrada para prevenir ejecución de código malicioso en expresiones matemáticas
- Límites en complejidad computacional para prevenir abuso de recursos
- Logging detallado de todas las operaciones para auditoría científica
- Control de acceso basado en dominio para operaciones especializadas
- Validación de parámetros físicos para prevenir cálculos inválidos

Notas de Implementación:
----------------------
- Utiliza orquestador para coordinar múltiples servicios especializados
- Soporta verificación formal con múltiples sistemas (SymPy, Z3, Lean)
- Implementa simulaciones físicas para astronomía y física de partículas
- Proporciona interfaz unificada para dominios científicos diversos
- Incluye validación automática de parámetros y resultados
"""

from __future__ import annotations

from typing import Any, Dict
import logging

from fastapi import APIRouter, HTTPException

from app.domains.mathematics.services.math_physics_orchestrator import MathPhysicsOrchestrator

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/math-physics", tags=["math-physics"])

_orchestrator = MathPhysicsOrchestrator()


@router.post("/route")
async def route_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enruta una solicitud al servicio matemático o físico apropiado basado en el dominio.

    Este endpoint analiza automáticamente el dominio de la solicitud y la dirige
    al servicio especializado correspondiente para procesamiento óptimo.

    Args:
        payload: Diccionario con la solicitud incluyendo dominio y parámetros específicos

    Returns:
        Resultado del procesamiento por el servicio correspondiente

    Raises:
        HTTPException: Si el dominio no es válido o ocurre un error en el procesamiento
    """
    try:
        domain = payload.get("domain")
        if not domain:
            raise HTTPException(status_code=400, detail="domain requerido")

        logger.info(f"🔀 Routing request to domain: {domain}")

        result = await _orchestrator.process_request(payload)
        if not result.get("success"):
            logger.warning(f"⚠️ Routing failed for domain {domain}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "unknown error"))

        logger.info(f"✅ Successfully routed request for domain {domain}")
        return result

    except HTTPException:
        raise
    except QuantumError as e:
        logger.exception("❌ Error routing request")
        raise HTTPException(status_code=500, detail="Internal server error") from e

@router.post("/theorem/verify")
async def verify_theorem(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica la validez de un teorema matemático usando métodos formales.

    Este endpoint permite verificar teoremas matemáticos utilizando diferentes
    sistemas de verificación formal como SymPy, SMT solvers o Lean.

    Args:
        payload: Diccionario con el teorema y método de verificación

    Returns:
        Resultado de la verificación del teorema

    Raises:
        HTTPException: Si el teorema o método no son válidos
    """
    try:
        statement = payload.get("statement") or payload.get("formula")
        if not statement:
            raise HTTPException(status_code=400, detail="statement/formula requerido")

        method = payload.get("method", "sympy")
        logger.info(f"🔍 Verifying theorem with method {method}: {statement[:50]}...")

        req = {"domain": "mathematics", "statement": statement, "method": method}
        res = await _orchestrator.process_request(req)

        logger.info(f"✅ Theorem verification completed with method {method}")
        return res

    except HTTPException:
        raise
    except QuantumError as e:
        logger.exception("❌ Error verifying theorem")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/theorem/smt2")
async def verify_smt2(payload: Dict[str, Any]) -> Dict[str, Any]:
    smt2 = payload.get("smt2") or payload.get("source")
    if not smt2:
        raise HTTPException(status_code=400, detail="smt2/source requerido")
    req = {"domain": "mathematics", "smt2": smt2}
    return await _orchestrator.process_request(req)


@router.post("/theorem/lean")
async def verify_lean(payload: Dict[str, Any]) -> Dict[str, Any]:
    stmt = payload.get("statement") or payload.get("lean_statement")
    if not stmt:
        raise HTTPException(status_code=400, detail="statement/lean_statement requerido")
    req = {"domain": "mathematics", "method": "lean", "lean_statement": stmt}
    return await _orchestrator.process_request(req)


@router.post("/astronomy/transit")
async def astronomy_transit(payload: Dict[str, Any]) -> Dict[str, Any]:
    light_curve = payload.get("light_curve") or []
    req = {"domain": "astronomy", "operation": "exoplanet_transit", "light_curve": light_curve}
    return await _orchestrator.process_request(req)


@router.post("/particles/jets")
async def particle_jets(payload: Dict[str, Any]) -> Dict[str, Any]:
    particles = payload.get("particles") or []
    req = {"domain": "particle_physics", "operation": "jet_counting", "particles": particles}
    return await _orchestrator.process_request(req)


@router.post("/quantum/run")
async def quantum_run(payload: Dict[str, Any]) -> Dict[str, Any]:
    op = payload.get("algorithm") or payload.get("operation")
    if not op:
        raise HTTPException(status_code=400, detail="algorithm/operation requerido")
    req = {"domain": "quantum_computing", "operation": op, "parameters": payload.get("parameters", {})}
    return await _orchestrator.process_request(req)


@router.post("/astronomy/lensing")
async def astronomy_lensing(payload: Dict[str, Any]) -> Dict[str, Any]:
    mass = payload.get("lens_mass")
    if mass is None:
        raise HTTPException(status_code=400, detail="lens_mass requerido")
    req = {"domain": "astronomy", "operation": "gravitational_lensing", "lens_mass": float(mass)}
    return await _orchestrator.process_request(req)
