"""
Quantum Physics Router for AXIOM - User-friendly interface
Provides intuitive REST API endpoints for quantum physics simulations

Ethics & Safety:
- Uso educativo/demostrativo. No operar hardware ni sistemas reales con estos endpoints.
- Controla parámetros (n_max, n_points, t_max) para evitar consumo excesivo.
- Resultados dependen de modelos ideales; valida con referencias.
"""

from fastapi import APIRouter, HTTPException
from ..quantum.quantum_physics_service import QuantumPhysicsService
from app.domains.models import BaseResponse
from app.exceptions.domain.physics import QuantumError

router = APIRouter()
service = QuantumPhysicsService()

@router.get("/", response_model=BaseResponse)
async def get_quantum_physics_home():
    """
    Página principal de física cuántica con información general
    """
    return BaseResponse(
        success=True,
        message="Bienvenido a la física cuántica de Mathematics AI",
        data={
            "description": "Simulaciones de sistemas cuánticos, evolución de espín, osciladores armónicos y óptica cuántica",
            "available_simulations": [
                "Evolución de espín en campo magnético",
                "Oscilador armónico cuántico",
                "Sistema de dos niveles con disipación",
                "Análisis de entrelazamiento",
                "Óptica cuántica (modelo Jaynes-Cummings)"
            ],
            "examples": {
                "spin_evolution": "POST /api/quantum-physics/spin-evolution con parámetros de campo magnético",
                "harmonic_oscillator": "POST /api/quantum-physics/harmonic-oscillator con frecuencia y estado coherente",
                "two_level_system": "POST /api/quantum-physics/two-level-system con frecuencia de transición",
                "entanglement": "POST /api/quantum-physics/entanglement-analysis con tipo de estado",
                "quantum_optics": "POST /api/quantum-physics/quantum-optics con parámetros del modelo Jaynes-Cummings"
            }
        }
    )

@router.get("/info", response_model=BaseResponse)
async def get_quantum_physics_info():
    """
    Información detallada sobre las capacidades de simulación cuántica
    """
    try:
        result = service.get_service_info()
        return BaseResponse(
            success=True,
            message="Información de simulaciones de física cuántica",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples", response_model=BaseResponse)
async def get_quantum_physics_examples():
    """
    Ejemplos prácticos de simulaciones de física cuántica
    """
    return BaseResponse(
        success=True,
        message="Ejemplos de simulaciones de física cuántica",
        data={
            "spin_examples": [
                {
                    "name": "Espín en campo magnético uniforme",
                    "parameters": {"Bx": 0, "By": 0, "Bz": 1.0, "t_max": 10, "n_points": 100},
                    "description": "Evolución de espín-1/2 en campo magnético a lo largo del eje Z",
                    "endpoint": "POST /api/quantum-physics/spin-evolution",
                    "expected_results": ["precesión de Larmor", "evolución temporal del estado"]
                },
                {
                    "name": "Espín en campo magnético rotante",
                    "parameters": {"Bx": 1.0, "By": 1.0, "Bz": 0.5, "t_max": 15, "n_points": 150},
                    "description": "Efecto de campo magnético en múltiples direcciones",
                    "endpoint": "POST /api/quantum-physics/spin-evolution",
                    "expected_results": ["precesión compleja", "efecto de campo transversal"]
                }
            ],
            "oscillator_examples": [
                {
                    "name": "Estado coherente del oscilador",
                    "parameters": {"omega": 1.0, "n_max": 10, "alpha": 2.0, "t_max": 20, "n_points": 200},
                    "description": "Evolución de estado coherente en oscilador armónico",
                    "endpoint": "POST /api/quantum-physics/harmonic-oscillator",
                    "expected_results": ["evolución del estado coherente", "distribución de fotones"]
                },
                {
                    "name": "Estado vacío con alta frecuencia",
                    "parameters": {"omega": 2.0, "n_max": 5, "alpha": 0.0, "t_max": 10, "n_points": 100},
                    "description": "Oscilador en estado vacío con frecuencia elevada",
                    "endpoint": "POST /api/quantum-physics/harmonic-oscillator",
                    "expected_results": ["estado fundamental", "energía cero-punto"]
                }
            ],
            "two_level_examples": [
                {
                    "name": "Sistema sin disipación",
                    "parameters": {"omega": 1.0, "gamma": 0.0, "t_max": 25, "n_points": 250},
                    "description": "Evolución coherente de sistema de dos niveles",
                    "endpoint": "POST /api/quantum-physics/two-level-system",
                    "expected_results": ["oscilaciones de Rabi", "coherencia perfecta"]
                },
                {
                    "name": "Sistema con decaimiento",
                    "parameters": {"omega": 1.0, "gamma": 0.1, "t_max": 30, "n_points": 300},
                    "description": "Sistema de dos niveles con relajación",
                    "endpoint": "POST /api/quantum-physics/two-level-system",
                    "expected_results": ["decaimiento exponencial", "pérdida de coherencia"]
                }
            ],
            "entanglement_examples": [
                {
                    "name": "Estado de Bell",
                    "parameters": {"state_type": "bell"},
                    "description": "Análisis de entrelazamiento en estado de Bell",
                    "endpoint": "POST /api/quantum-physics/entanglement-analysis",
                    "expected_results": ["entrelazamiento máximo", "concurrencia = 1"]
                },
                {
                    "name": "Estado de Werner",
                    "parameters": {"state_type": "werner"},
                    "description": "Análisis de estado parcialmente entrelazado",
                    "endpoint": "POST /api/quantum-physics/entanglement-analysis",
                    "expected_results": ["entrelazamiento parcial", "concurrencia < 1"]
                }
            ],
            "quantum_optics_examples": [
                {
                    "name": "Modelo Jaynes-Cummings básico",
                    "parameters": {"n_max": 20, "kappa": 0.1, "g": 0.1, "alpha": 3.0, "t_max": 50, "n_points": 500},
                    "description": "Interacción átomo-cavidad en óptica cuántica",
                    "endpoint": "POST /api/quantum-physics/quantum-optics",
                    "expected_results": ["oscilaciones de vacío", "transferencia de energía"]
                },
                {
                    "name": "Cavidad de alta calidad",
                    "parameters": {"n_max": 15, "kappa": 0.01, "g": 0.2, "alpha": 2.0, "t_max": 40, "n_points": 400},
                    "description": "Sistema con baja tasa de decaimiento de cavidad",
                    "endpoint": "POST /api/quantum-physics/quantum-optics",
                    "expected_results": ["coherencia prolongada", "efecto de acoplamiento fuerte"]
                }
            ],
            "tips": [
                "Los parámetros de campo magnético se dan en unidades de frecuencia de Larmor",
                "El parámetro alpha representa la amplitud del estado coherente",
                "Gamma controla la tasa de disipación en sistemas de dos niveles",
                "Los estados de Bell representan entrelazamiento máximo",
                "El modelo Jaynes-Cummings describe la interacción luz-materia"
            ]
        }
    )

@router.post("/spin-evolution", response_model=BaseResponse)
async def simulate_spin_evolution(
    Bx: float = 1.0,
    By: float = 0.0,
    Bz: float = 1.0,
    t_max: float = 10.0,
    n_points: int = 100
):
    """
    Simula la evolución de una partícula de espín-1/2 en campo magnético

    Args:
        Bx, By, Bz: Componentes del campo magnético (en unidades de frecuencia de Larmor)
        t_max: Tiempo máximo de simulación
        n_points: Número de puntos temporales

    Returns:
        Evolución temporal del estado de espín con explicaciones
    """
    try:
        # Validar parámetros
        if t_max <= 0 or n_points <= 0:
            raise HTTPException(
                status_code=400,
                detail="El tiempo máximo y número de puntos deben ser positivos"
            )
        if n_points > 1000:
            raise HTTPException(
                status_code=400,
                detail="El número máximo de puntos es 1000 para evitar sobrecarga"
            )

        params = {
            "Bx": Bx, "By": By, "Bz": Bz,
            "t_max": t_max, "n_points": n_points
        }
        result = service.simulate_spin_evolution(params)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones
        result["explanations"] = {
            "magnetic_field": f"Campo magnético: Bx={Bx}, By={By}, Bz={Bz}",
            "simulation_time": f"Tiempo de simulación: {t_max} unidades",
            "larmor_frequency": "Frecuencia de Larmor determina la velocidad de precesión",
            "spin_evolution": "Evolución del vector de Bloch en el espacio de espín"
        }

        return BaseResponse(
            success=True,
            message=f"Simulación de evolución de espín completada (campo: [{Bx}, {By}, {Bz}])",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en simulación de espín: {str(e)}. Verifica los parámetros del campo magnético."
        )

@router.post("/harmonic-oscillator", response_model=BaseResponse)
async def simulate_harmonic_oscillator(
    omega: float = 1.0,
    n_max: int = 10,
    alpha: float = 2.0,
    t_max: float = 20.0,
    n_points: int = 200
):
    """
    Simula un oscilador armónico cuántico

    Args:
        omega: Frecuencia del oscilador
        n_max: Número máximo de fotones a considerar
        alpha: Parámetro del estado coherente inicial
        t_max: Tiempo máximo de simulación
        n_points: Número de puntos temporales

    Returns:
        Evolución del estado coherente con análisis detallado
    """
    try:
        # Validar parámetros
        if omega <= 0:
            raise HTTPException(status_code=400, detail="La frecuencia omega debe ser positiva")
        if n_max < 1 or n_max > 50:
            raise HTTPException(status_code=400, detail="n_max debe estar entre 1 y 50")
        if t_max <= 0 or n_points <= 0:
            raise HTTPException(
                status_code=400,
                detail="El tiempo máximo y número de puntos deben ser positivos"
            )

        params = {
            "omega": omega, "n_max": n_max, "alpha": alpha,
            "t_max": t_max, "n_points": n_points
        }
        result = service.simulate_harmonic_oscillator(params)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones
        result["explanations"] = {
            "oscillator_frequency": f"Frecuencia del oscilador: {omega}",
            "coherent_state": f"Estado coherente inicial con amplitud: {alpha}",
            "photon_cutoff": f"Número máximo de fotones considerados: {n_max}",
            "simulation_parameters": f"Tiempo: {t_max}, Puntos: {n_points}",
            "physical_interpretation": "El estado coherente representa un campo clásico en mecánica cuántica"
        }

        return BaseResponse(
            success=True,
            message=f"Simulación de oscilador armónico completada (ω={omega}, α={alpha})",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en simulación del oscilador: {str(e)}. Verifica los parámetros."
        )

@router.post("/two-level-system", response_model=BaseResponse)
async def simulate_two_level_system(
    omega: float = 1.0,
    gamma: float = 0.1,
    t_max: float = 25.0,
    n_points: int = 250
):
    """
    Simula un sistema cuántico de dos niveles con disipación

    Args:
        omega: Frecuencia de transición
        gamma: Tasa de decaimiento (disipación)
        t_max: Tiempo máximo de simulación
        n_points: Número de puntos temporales

    Returns:
        Evolución del sistema con análisis de coherencia
    """
    try:
        # Validar parámetros
        if omega <= 0:
            raise HTTPException(status_code=400, detail="La frecuencia omega debe ser positiva")
        if gamma < 0:
            raise HTTPException(status_code=400, detail="La tasa de decaimiento gamma no puede ser negativa")
        if t_max <= 0 or n_points <= 0:
            raise HTTPException(
                status_code=400,
                detail="El tiempo máximo y número de puntos deben ser positivos"
            )

        params = {
            "omega": omega, "gamma": gamma,
            "t_max": t_max, "n_points": n_points
        }
        result = service.simulate_two_level_system(params)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones
        result["explanations"] = {
            "transition_frequency": f"Frecuencia de transición: {omega}",
            "decay_rate": f"Tasa de decaimiento: {gamma}",
            "dissipation_level": "Sin disipación" if gamma == 0 else f"Disipación moderada (γ={gamma})" if gamma < 0.5 else f"Alta disipación (γ={gamma})",
            "coherence_time": f"Tiempo de coherencia aproximado: {1/gamma if gamma > 0 else 'infinito'}",
            "physical_system": "Representa átomos, espines o qubits en computación cuántica"
        }

        return BaseResponse(
            success=True,
            message=f"Simulación de sistema de dos niveles completada (ω={omega}, γ={gamma})",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en simulación de dos niveles: {str(e)}. Verifica los parámetros."
        )

@router.post("/entanglement-analysis", response_model=BaseResponse)
async def calculate_entanglement(state_type: str = "bell"):
    """
    Calcula medidas de entrelazamiento para estados cuánticos

    Args:
        state_type: Tipo de estado cuántico ("bell" o "werner")

    Returns:
        Análisis completo del entrelazamiento con medidas cuantitativas
    """
    try:
        if state_type not in ["bell", "werner"]:
            raise HTTPException(
                status_code=400,
                detail="Tipo de estado debe ser 'bell' o 'werner'"
            )

        result = service.calculate_quantum_entanglement(state_type)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones detalladas
        explanations = {
            "state_type": f"Tipo de estado: {state_type.upper()}",
            "entanglement_measure": "Medida cuantitativa del entrelazamiento",
            "concurrence": "Concurrencia (0 = sin entrelazamiento, 1 = máximo entrelazamiento)",
            "fidelity": "Fidelidad del estado con respecto al estado ideal"
        }

        if state_type == "bell":
            explanations["bell_states"] = "Estados de Bell representan entrelazamiento máximo entre dos qubits"
        elif state_type == "werner":
            explanations["werner_states"] = "Estados de Werner son mezcla de estado entrelazado y estado separable"

        result["explanations"] = explanations

        return BaseResponse(
            success=True,
            message=f"Análisis de entrelazamiento completado para estado {state_type}",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en análisis de entrelazamiento: {str(e)}. Verifica el tipo de estado."
        )

@router.post("/quantum-optics", response_model=BaseResponse)
async def simulate_quantum_optics(
    n_max: int = 20,
    kappa: float = 0.1,
    g: float = 0.1,
    alpha: float = 3.0,
    t_max: float = 50.0,
    n_points: int = 500
):
    """
    Simula fenómenos de óptica cuántica (modelo Jaynes-Cummings)

    Args:
        n_max: Número máximo de fotones
        kappa: Tasa de decaimiento de la cavidad
        g: Fuerza de acoplamiento átomo-campo
        alpha: Amplitud del estado coherente inicial
        t_max: Tiempo máximo de simulación
        n_points: Número de puntos temporales

    Returns:
        Simulación completa del modelo Jaynes-Cummings
    """
    try:
        # Validar parámetros
        if n_max < 1 or n_max > 100:
            raise HTTPException(status_code=400, detail="n_max debe estar entre 1 y 100")
        if kappa < 0 or g < 0:
            raise HTTPException(
                status_code=400,
                detail="Las tasas kappa y g no pueden ser negativas"
            )
        if t_max <= 0 or n_points <= 0:
            raise HTTPException(
                status_code=400,
                detail="El tiempo máximo y número de puntos deben ser positivos"
            )

        params = {
            "n_max": n_max, "kappa": kappa, "g": g, "alpha": alpha,
            "t_max": t_max, "n_points": n_points
        }
        result = service.simulate_quantum_optics(params)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Agregar explicaciones
        result["explanations"] = {
            "jaynes_cummings_model": "Modelo que describe la interacción entre un átomo de dos niveles y un modo de cavidad",
            "coupling_regime": "Régimen de acoplamiento fuerte" if g > kappa else "Régimen de acoplamiento débil",
            "vacuum_rabi_oscillations": "Oscilaciones de Rabi en el vacío representan transferencia coherente de energía",
            "cavity_decay": f"Decaimiento de cavidad con tasa κ={kappa}",
            "coherent_state": f"Estado coherente inicial con amplitud α={alpha}"
        }

        return BaseResponse(
            success=True,
            message=f"Simulación de óptica cuántica completada (g={g}, κ={kappa}, α={alpha})",
            data=result
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en simulación de óptica cuántica: {str(e)}. Verifica los parámetros del modelo."
        )

@router.get("/quick-spin/{Bx}/{By}/{Bz}")
async def quick_spin_simulation(
    Bx: float,
    By: float,
    Bz: float,
    t_max: float = 5.0
):
    """
    Simulación rápida de evolución de espín con parámetros en la URL

    Ejemplos:
    - /api/quantum-physics/quick-spin/0/0/1 (espín en campo Z)
    - /api/quantum-physics/quick-spin/1/0/1 (campo con componente X)

    Args:
        Bx, By, Bz: Componentes del campo magnético
        t_max: Tiempo máximo (por defecto 5.0)

    Returns:
        Simulación básica de evolución de espín
    """
    try:
        params = {
            "Bx": Bx, "By": By, "Bz": Bz,
            "t_max": t_max, "n_points": 50
        }
        result = service.simulate_spin_evolution(params)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return BaseResponse(
            success=True,
            message=f"Simulación rápida de espín (B=[{Bx}, {By}, {Bz}])",
            data={
                "magnetic_field": [Bx, By, Bz],
                "simulation_time": t_max,
                "larmor_frequency": (Bx**2 + By**2 + Bz**2)**0.5,
                "quick_summary": [
                    f"Frecuencia de Larmor: {(Bx**2 + By**2 + Bz**2)**0.5:.2f}",
                    f"Campo total: {(Bx**2 + By**2 + Bz**2)**0.5:.2f}",
                    f"Tiempo de simulación: {t_max} unidades"
                ]
            }
        )
    except QuantumError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en simulación rápida: {str(e)}. Verifica los parámetros del campo."
        )
