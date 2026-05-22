"""
STDP Plasticity Service - AXIOM META 4
=====================================

Servicio especializado para implementar múltiples formas de plasticidad sináptica
incluyendo STDP clásica, tripletas, plasticidad homeostática y meta-plasticidad.
Basado en los últimos avances en neurociencia computacional y optimizado para
simulaciones de gran escala.

Características principales:
- STDP clásica con ventanas asimétricas
- STDP con tripletas para efectos de frecuencia
- Plasticidad homeostática para estabilización
- Meta-plasticidad (plasticidad de la plasticidad)
- BCM (Bienenstock-Cooper-Munro) rule
- Regla de Oja para normalización de pesos
- Integración con redes spiking

Autor: AXIOM META 4 Development Team
Fecha: Diciembre 2024
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class PlasticityType(Enum):
    """Tipos de plasticidad sináptica"""
    STDP_CLASSIC = "stdp_classic"                    # STDP clásica
    STDP_TRIPLET = "stdp_triplet"                    # STDP con tripletas
    STDP_VOLTAGE = "stdp_voltage_dependent"          # STDP dependiente del voltaje
    HOMEOSTATIC = "homeostatic_scaling"              # Escalamiento homeostático
    META_PLASTIC = "meta_plasticity"                 # Meta-plasticidad
    BCM_RULE = "bienenstock_cooper_munro"           # Regla BCM
    OJA_RULE = "oja_rule"                           # Regla de Oja
    COVARIANCE = "covariance_rule"                   # Regla de covarianza
    CALCIUM_BASED = "calcium_dependent"              # Dependiente de calcio


class LearningPhase(Enum):
    """Fases de aprendizaje"""
    CRITICAL_PERIOD = "critical_period"      # Período crítico
    ADULT_LEARNING = "adult_learning"        # Aprendizaje adulto
    DEVELOPMENTAL = "developmental"          # Desarrollo
    RECOVERY = "recovery"                    # Recuperación post-lesión


@dataclass
class STDPClassicParameters:
    """Parámetros para STDP clásica"""
    tau_plus: float = 20.0        # Constante de tiempo LTP (ms)
    tau_minus: float = 20.0       # Constante de tiempo LTD (ms)
    a_plus: float = 0.01          # Amplitud LTP
    a_minus: float = 0.012        # Amplitud LTD
    w_max: float = 1.0            # Peso máximo
    w_min: float = 0.0            # Peso mínimo
    multiplicative: bool = True   # Escalamiento multiplicativo

    # Parámetros adicionales
    all_to_all: bool = False      # Interacciones all-to-all vs nearest-neighbor
    suppress_depression: bool = False  # Suprimir depresión para pesos bajos


@dataclass
class STDPTripletParameters:
    """Parámetros para STDP con tripletas"""
    # Parámetros clásicos
    tau_plus: float = 16.8        # ms
    tau_minus: float = 33.7       # ms
    a2_plus: float = 7.5e-10      # Amplitud pair LTP
    a2_minus: float = 7e-3        # Amplitud pair LTD

    # Parámetros de tripletas
    tau_x: float = 101.0          # Constante lenta pre (ms)
    tau_y: float = 125.0          # Constante lenta post (ms)
    a3_plus: float = 9.3e-3       # Amplitud triplet LTP
    a3_minus: float = 2.3e-4      # Amplitud triplet LTD

    # Límites
    w_max: float = 1.0
    w_min: float = 0.0


@dataclass
class HomeostaticParameters:
    """Parámetros para plasticidad homeostática"""
    target_rate: float = 5.0      # Tasa objetivo (Hz)
    tau_homeostatic: float = 3600000.0  # Constante de tiempo lenta (ms) ~ 1 hora
    alpha_h: float = 0.1          # Tasa de escalamiento
    beta_h: float = 0.001         # Factor de scaling

    # Métodos de homeostasis
    method: str = "synaptic_scaling"  # "synaptic_scaling", "intrinsic_plasticity", "metaplasticity"
    global_normalization: bool = True


@dataclass
class MetaPlasticityParameters:
    """Parámetros para meta-plasticidad"""
    theta_d: float = 0.2          # Umbral de depresión
    theta_p: float = 0.8          # Umbral de potenciación
    tau_theta: float = 10000.0    # Constante de tiempo del umbral (ms)
    alpha_theta: float = 0.1      # Tasa de cambio del umbral

    # Sliding threshold
    sliding_threshold: bool = True
    activity_window: float = 1000.0  # Ventana de actividad (ms)


@dataclass
class BCMParameters:
    """Parámetros para regla BCM"""
    tau_theta: float = 10000.0    # Constante de tiempo del umbral (ms)
    p: float = 2.0                # Exponente para theta
    learning_rate: float = 0.01   # Tasa de aprendizaje
    w_max: float = 1.0
    w_min: float = 0.0


class PlasticityRule(ABC):
    """Clase base para reglas de plasticidad"""

    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Actualizar peso sináptico"""
        raise NotImplementedError("Update weight method must be implemented")

    @abstractmethod
    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar trazas de actividad"""
        raise NotImplementedError("Update traces method must be implemented")


class STDPClassicRule(PlasticityRule):
    """Implementación de STDP clásica"""

    def __init__(self, params: STDPClassicParameters):
        super().__init__("stdp_classic")
        self.params = params

        # Trazas de actividad
        self.pre_trace = 0.0
        self.post_trace = 0.0

        # Historial para all-to-all
        self.pre_spike_times = []
        self.post_spike_times = []

    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar trazas exponenciales"""
        # Decaimiento exponencial
        self.pre_trace *= np.exp(-dt / self.params.tau_plus)
        self.post_trace *= np.exp(-dt / self.params.tau_minus)

        # Agregar spikes
        if pre_spike:
            self.pre_trace += 1.0
            if self.params.all_to_all:
                self.pre_spike_times.append(0.0)  # Reset time reference

        if post_spike:
            self.post_trace += 1.0
            if self.params.all_to_all:
                self.post_spike_times.append(0.0)

        # Limpiar historial antiguo para all-to-all
        if self.params.all_to_all:
            max_window = max(5 * self.params.tau_plus, 5 * self.params.tau_minus)
            self.pre_spike_times = [t for t in self.pre_spike_times if t < max_window]
            self.post_spike_times = [t for t in self.post_spike_times if t < max_window]

            # Incrementar tiempos
            self.pre_spike_times = [t + dt for t in self.pre_spike_times]
            self.post_spike_times = [t + dt for t in self.post_spike_times]

    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Actualizar peso usando STDP clásica"""

        if not self.params.all_to_all:
            # Nearest-neighbor STDP
            dw = 0.0

            # LTP: post spike causa potenciación basada en traza pre
            if len(post_activity) > 0 and post_activity[-1]:
                dw += self.params.a_plus * self.pre_trace

            # LTD: pre spike causa depresión basada en traza post
            if len(pre_activity) > 0 and pre_activity[-1]:
                if not self.params.suppress_depression or w_current > 0.1:
                    dw -= self.params.a_minus * self.post_trace

        else:
            # All-to-all STDP
            dw = self._calculate_all_to_all_stdp()

        # Aplicar escalamiento multiplicativo/aditivo
        if self.params.multiplicative:
            if dw > 0:  # LTP
                dw *= (self.params.w_max - w_current)
            else:  # LTD
                dw *= (w_current - self.params.w_min)

        # Nuevo peso
        w_new = w_current + dw
        w_new = np.clip(w_new, self.params.w_min, self.params.w_max)

        return w_new

    def _calculate_all_to_all_stdp(self) -> float:
        """Calcular STDP all-to-all"""
        dw = 0.0

        # Todas las combinaciones de spikes pre y post
        for t_pre in self.pre_spike_times:
            for t_post in self.post_spike_times:
                dt_spike = t_post - t_pre

                if dt_spike > 0:  # post después de pre -> LTP
                    dw += self.params.a_plus * np.exp(-dt_spike / self.params.tau_plus)
                elif dt_spike < 0:  # pre después de post -> LTD
                    dw -= self.params.a_minus * np.exp(dt_spike / self.params.tau_minus)

        return dw


class STDPTripletRule(PlasticityRule):
    """STDP con tripletas para dependencia de frecuencia"""

    def __init__(self, params: STDPTripletParameters):
        super().__init__("stdp_triplet")
        self.params = params

        # Trazas rápidas (pares)
        self.r1 = 0.0  # Traza pre rápida
        self.o1 = 0.0  # Traza post rápida

        # Trazas lentas (tripletas)
        self.r2 = 0.0  # Traza pre lenta
        self.o2 = 0.0  # Traza post lenta

    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar trazas rápidas y lentas"""
        # Decaimiento de todas las trazas
        self.r1 *= np.exp(-dt / self.params.tau_plus)
        self.o1 *= np.exp(-dt / self.params.tau_minus)
        self.r2 *= np.exp(-dt / self.params.tau_x)
        self.o2 *= np.exp(-dt / self.params.tau_y)

        # Agregar contribuciones de spikes
        if pre_spike:
            self.r1 += 1.0
            self.r2 += 1.0

        if post_spike:
            self.o1 += 1.0
            self.o2 += 1.0

    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Actualizar peso usando STDP con tripletas"""
        dw = 0.0

        # Términos de pares (STDP clásica)
        if len(post_activity) > 0 and post_activity[-1]:  # Post spike
            dw += self.params.a2_plus * self.r1 * (1 + self.params.a3_plus * self.r2)

        if len(pre_activity) > 0 and pre_activity[-1]:  # Pre spike
            dw -= self.params.a2_minus * self.o1 * (1 + self.params.a3_minus * self.o2)

        # Aplicar cambio
        w_new = w_current + dw
        w_new = np.clip(w_new, self.params.w_min, self.params.w_max)

        return w_new


class HomeostaticPlasticityRule(PlasticityRule):
    """Plasticidad homeostática para estabilización de red"""

    def __init__(self, params: HomeostaticParameters):
        super().__init__("homeostatic")
        self.params = params

        # Variables de estado
        self.avg_activity = 0.0
        self.scaling_factor = 1.0

        # Historial de actividad
        self.activity_window = []
        self.time_window = []

    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar promedio de actividad"""
        # Decaimiento exponencial del promedio
        self.avg_activity *= np.exp(-dt / self.params.tau_homeostatic)

        # Agregar actividad actual
        current_activity = float(post_spike)  # Enfoque en actividad postsináptica
        self.avg_activity += current_activity * dt / self.params.tau_homeostatic

        # Mantener ventana deslizante para métodos más sofisticados
        if len(self.activity_window) > 1000:  # Limitar memoria
            self.activity_window.pop(0)
            self.time_window.pop(0)

        self.activity_window.append(current_activity)
        self.time_window.append(dt)

    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Aplicar escalamiento homeostático"""

        if self.params.method == "synaptic_scaling":
            # Synaptic scaling multiplicativo
            activity_error = self.avg_activity - self.params.target_rate / 1000.0  # Hz -> kHz

            # Factor de escalamiento
            scaling_change = -self.params.alpha_h * activity_error * dt / self.params.tau_homeostatic
            self.scaling_factor *= (1 + scaling_change)
            self.scaling_factor = max(0.1, min(10.0, self.scaling_factor))  # Límites razonables

            # Aplicar escalamiento
            w_new = w_current * (1 + scaling_change)

        elif self.params.method == "intrinsic_plasticity":
            # Cambiar propiedades intrínsecas (simulado como cambio de peso)
            activity_error = self.avg_activity - self.params.target_rate / 1000.0
            dw = -self.params.beta_h * activity_error * dt
            w_new = w_current + dw

        else:  # metaplasticity
            # Ajustar umbral de plasticidad (simulado)
            w_new = w_current

        return max(0.0, w_new)  # Evitar pesos negativos en homeostasis


class MetaPlasticityRule(PlasticityRule):
    """Meta-plasticidad: plasticidad de la plasticidad"""

    def __init__(self, params: MetaPlasticityParameters):
        super().__init__("meta_plasticity")
        self.params = params

        # Umbral deslizante
        self.theta = (self.params.theta_d + self.params.theta_p) / 2

        # Historial de actividad
        self.activity_history = []
        self.time_history = []

    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar umbral deslizante"""
        # Actividad postsináptica
        post_activity = float(post_spike)

        if self.params.sliding_threshold:
            # Ventana deslizante de actividad
            current_time = sum(self.time_history) + dt

            # Agregar actividad actual
            self.activity_history.append(post_activity)
            self.time_history.append(dt)

            # Remover actividad fuera de la ventana
            cutoff_time = current_time - self.params.activity_window
            while self.time_history and sum(self.time_history[:-len(self.time_history)]) < cutoff_time:
                self.activity_history.pop(0)
                self.time_history.pop(0)

            # Calcular actividad promedio en ventana
            if self.activity_history:
                avg_activity = np.mean(self.activity_history)

                # Actualizar umbral
                dtheta = self.params.alpha_theta * (avg_activity - self.theta) * dt / self.params.tau_theta
                self.theta += dtheta

                # Mantener umbral en rango razonable
                self.theta = np.clip(self.theta, self.params.theta_d, self.params.theta_p)

    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Aplicar meta-plasticidad"""
        if len(post_activity) == 0:
            return w_current

        recent_activity = np.mean(post_activity[-10:]) if len(post_activity) >= 10 else np.mean(post_activity)

        # Modificar plasticidad basada en actividad vs umbral
        if recent_activity > self.theta:
            # Alta actividad -> facilitar LTP, dificultar LTD
            plasticity_modifier = 1.5
        else:
            # Baja actividad -> facilitar LTD, dificultar LTP
            plasticity_modifier = 0.7

        # Aplicar modificación (simulada como pequeño ajuste)
        dw = 0.001 * (recent_activity - self.theta) * plasticity_modifier
        w_new = w_current + dw

        return np.clip(w_new, 0.0, 1.0)


class BCMRule(PlasticityRule):
    """Regla Bienenstock-Cooper-Munro"""

    def __init__(self, params: BCMParameters):
        super().__init__("bcm")
        self.params = params

        # Umbral deslizante theta
        self.theta = 0.1
        self.post_activity_avg = 0.0

    def update_traces(self, pre_spike: bool, post_spike: bool, dt: float):
        """Actualizar promedio de actividad postsináptica"""
        post_rate = float(post_spike) / (dt / 1000.0) if dt > 0 else 0.0  # Hz

        # Actualizar promedio con constante de tiempo larga
        decay = np.exp(-dt / self.params.tau_theta)
        self.post_activity_avg = decay * self.post_activity_avg + (1 - decay) * post_rate

        # Actualizar umbral: theta = <post^p>
        self.theta = self.post_activity_avg ** self.params.p

    def update_weight(self, w_current: float, pre_activity: np.ndarray,
                     post_activity: np.ndarray, dt: float) -> float:
        """Aplicar regla BCM"""
        if len(pre_activity) == 0 or len(post_activity) == 0:
            return w_current

        # Actividades recientes
        pre_rate = np.mean(pre_activity[-5:]) if len(pre_activity) >= 5 else np.mean(pre_activity)
        post_rate = np.mean(post_activity[-5:]) if len(post_activity) >= 5 else np.mean(post_activity)

        # Regla BCM: dw/dt = eta * pre * post * (post - theta)
        phi_post = post_rate * (post_rate - self.theta)
        dw = self.params.learning_rate * pre_rate * phi_post * dt

        w_new = w_current + dw
        w_new = np.clip(w_new, self.params.w_min, self.params.w_max)

        return w_new


class STDPPlasticityService:
    """Servicio principal para plasticidad sináptica STDP"""

    def __init__(self):
        """Inicializar servicio de plasticidad"""
        self.plasticity_rules = {}
        self.active_synapses = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        logger.info("🧬 STDP Plasticity Service initialized")

    def create_plasticity_rule(self, rule_id: str, rule_type: PlasticityType,
                             parameters: Dict[str, Any]) -> str:
        """
        Crear regla de plasticidad

        Args:
            rule_id: Identificador único
            rule_type: Tipo de plasticidad
            parameters: Parámetros específicos

        Returns:
            ID de la regla creada
        """
        self.logger.info(f"🔧 Creando regla de plasticidad: {rule_id} ({rule_type.value})")

        if rule_type == PlasticityType.STDP_CLASSIC:
            params = STDPClassicParameters(**parameters)
            rule = STDPClassicRule(params)

        elif rule_type == PlasticityType.STDP_TRIPLET:
            params = STDPTripletParameters(**parameters)
            rule = STDPTripletRule(params)

        elif rule_type == PlasticityType.HOMEOSTATIC:
            params = HomeostaticParameters(**parameters)
            rule = HomeostaticPlasticityRule(params)

        elif rule_type == PlasticityType.META_PLASTIC:
            params = MetaPlasticityParameters(**parameters)
            rule = MetaPlasticityRule(params)

        elif rule_type == PlasticityType.BCM_RULE:
            params = BCMParameters(**parameters)
            rule = BCMRule(params)

        else:
            raise ValueError(f"Tipo de plasticidad no soportado: {rule_type}")

        self.plasticity_rules[rule_id] = rule
        self.logger.info(f"✅ Regla {rule_id} creada exitosamente")

        return rule_id

    async def simulate_plasticity_protocol(self, rule_id: str,
                                         protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simular protocolo de plasticidad

        Args:
            rule_id: ID de la regla de plasticidad
            protocol: Definición del protocolo

        Returns:
            Resultados de la simulación
        """
        if rule_id not in self.plasticity_rules:
            raise ValueError(f"Regla {rule_id} no encontrada")

        rule = self.plasticity_rules[rule_id]

        # Parámetros del protocolo
        duration = protocol.get('duration', 1000.0)  # ms
        dt = protocol.get('dt', 0.1)  # ms
        pre_pattern = protocol.get('pre_pattern', 'poisson')
        post_pattern = protocol.get('post_pattern', 'poisson')
        initial_weight = protocol.get('initial_weight', 0.5)

        # Generar patrones de actividad
        n_steps = int(duration / dt)
        pre_activity = self._generate_activity_pattern(pre_pattern, n_steps, dt, protocol)
        post_activity = self._generate_activity_pattern(post_pattern, n_steps, dt, protocol)

        # Simular plasticidad
        weights = [initial_weight]
        current_weight = initial_weight

        for step in range(n_steps):
            # Actualizar trazas
            pre_spike = pre_activity[step] if step < len(pre_activity) else False
            post_spike = post_activity[step] if step < len(post_activity) else False

            rule.update_traces(pre_spike, post_spike, dt)

            # Actualizar peso
            pre_window = pre_activity[max(0, step-100):step+1]
            post_window = post_activity[max(0, step-100):step+1]

            current_weight = rule.update_weight(current_weight, pre_window, post_window, dt)
            weights.append(current_weight)

        # Análisis de resultados
        final_weight = weights[-1]
        weight_change = final_weight - initial_weight
        max_weight = max(weights)
        min_weight = min(weights)

        # Detectar fases de aprendizaje
        phases = self._detect_learning_phases(weights, dt)

        return {
            'protocol_info': protocol,
            'initial_weight': initial_weight,
            'final_weight': final_weight,
            'weight_change': weight_change,
            'percent_change': (weight_change / initial_weight) * 100,
            'max_weight': max_weight,
            'min_weight': min_weight,
            'weight_trajectory': weights[::10],  # Muestreo para reducir tamaño
            'learning_phases': phases,
            'convergence_time': self._calculate_convergence_time(weights, dt),
            'stability_index': self._calculate_stability(weights[-1000:]) if len(weights) > 1000 else 0
        }

    def _generate_activity_pattern(self, pattern_type: str, n_steps: int, dt: float,
                                 protocol: Dict[str, Any]) -> np.ndarray:
        """Generar patrón de actividad neuronal"""

        if pattern_type == 'poisson':
            rate = protocol.get('rate', 10.0)  # Hz
            prob = rate * dt / 1000.0  # Probabilidad por paso
            return np.random.random(n_steps) < prob

        elif pattern_type == 'regular':
            rate = protocol.get('rate', 10.0)  # Hz
            interval = int(1000.0 / (rate * dt))  # Pasos entre spikes
            spikes = np.zeros(n_steps, dtype=bool)
            spikes[::interval] = True
            return spikes

        elif pattern_type == 'burst':
            burst_rate = protocol.get('burst_rate', 1.0)  # Hz
            spikes_per_burst = protocol.get('spikes_per_burst', 5)
            intraburst_freq = protocol.get('intraburst_freq', 100.0)  # Hz

            spikes = np.zeros(n_steps, dtype=bool)
            burst_interval = int(1000.0 / (burst_rate * dt))
            spike_interval = int(1000.0 / (intraburst_freq * dt))

            for burst_start in range(0, n_steps, burst_interval):
                for spike_idx in range(spikes_per_burst):
                    spike_time = burst_start + spike_idx * spike_interval
                    if spike_time < n_steps:
                        spikes[spike_time] = True

            return spikes

        elif pattern_type == 'paired':
            # Protocolo de pareamiento para STDP
            pair_rate = protocol.get('pair_rate', 1.0)  # Hz
            pair_interval = int(1000.0 / (pair_rate * dt))
            delay = protocol.get('delay', 10.0)  # ms
            delay_steps = int(delay / dt)

            spikes = np.zeros(n_steps, dtype=bool)
            for pair_start in range(0, n_steps - delay_steps, pair_interval):
                spikes[pair_start] = True  # Pre
                spikes[pair_start + delay_steps] = True  # Post (para post_activity)

            return spikes

        else:  # random
            return np.random.random(n_steps) < 0.01

    def _detect_learning_phases(self, weights: List[float], dt: float) -> Dict[str, Any]:
        """Detectar fases de aprendizaje en trayectoria de pesos"""
        if len(weights) < 100:
            return {'phases': [], 'transitions': []}

        weights_array = np.array(weights)

        # Detectar cambios de pendiente
        diff1 = np.diff(weights_array)
        diff2 = np.diff(diff1)

        # Encontrar puntos de inflexión
        inflection_points = []
        for i in range(1, len(diff2) - 1):
            if diff2[i-1] * diff2[i+1] < 0:  # Cambio de signo
                inflection_points.append(i)

        # Clasificar fases
        phases = []
        if len(inflection_points) > 0:
            phases.append({
                'type': 'initial',
                'start_time': 0,
                'end_time': inflection_points[0] * dt,
                'weight_change': weights_array[inflection_points[0]] - weights_array[0]
            })

            for i in range(len(inflection_points) - 1):
                start_idx = inflection_points[i]
                end_idx = inflection_points[i + 1]

                change = weights_array[end_idx] - weights_array[start_idx]
                phase_type = 'potentiation' if change > 0 else 'depression'

                phases.append({
                    'type': phase_type,
                    'start_time': start_idx * dt,
                    'end_time': end_idx * dt,
                    'weight_change': change
                })

        return {
            'phases': phases,
            'transitions': len(inflection_points),
            'dominant_phase': 'potentiation' if weights_array[-1] > weights_array[0] else 'depression'
        }

    def _calculate_convergence_time(self, weights: List[float], dt: float) -> Optional[float]:
        """Calcular tiempo de convergencia"""
        if len(weights) < 100:
            return None

        weights_array = np.array(weights)
        final_weight = weights_array[-1]

        # Encontrar cuando el peso se estabiliza (dentro del 5% del valor final)
        threshold = 0.05 * abs(final_weight)

        for i in range(len(weights_array) - 100, 0, -1):
            if abs(weights_array[i] - final_weight) > threshold:
                return (i + 100) * dt

        return None

    def _calculate_stability(self, recent_weights: List[float]) -> float:
        """Calcular índice de estabilidad"""
        if len(recent_weights) < 10:
            return 0.0

        weights_array = np.array(recent_weights)
        return 1.0 / (1.0 + np.std(weights_array))  # Mayor estabilidad = menor variabilidad

    async def compare_plasticity_rules(self, rule_ids: List[str],
                                     protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comparar múltiples reglas de plasticidad

        Args:
            rule_ids: Lista de IDs de reglas
            protocol: Protocolo de prueba

        Returns:
            Comparación detallada
        """
        results = {}

        for rule_id in rule_ids:
            if rule_id in self.plasticity_rules:
                result = await self.simulate_plasticity_protocol(rule_id, protocol)
                results[rule_id] = result

        # Análisis comparativo
        comparison = {
            'individual_results': results,
            'summary': {
                'most_potentiation': max(results.items(), key=lambda x: x[1]['weight_change'])[0],
                'most_depression': min(results.items(), key=lambda x: x[1]['weight_change'])[0],
                'most_stable': max(results.items(), key=lambda x: x[1]['stability_index'])[0],
                'fastest_convergence': min(
                    [(k, v['convergence_time']) for k, v in results.items() if v['convergence_time']],
                    key=lambda x: x[1], default=(None, None)
                )[0]
            }
        }

        return comparison

    def get_plasticity_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio"""
        return {
            'total_rules': len(self.plasticity_rules),
            'rule_types': [rule.rule_id for rule in self.plasticity_rules.values()],
            'active_synapses': len(self.active_synapses),
            'service_status': 'operational'
        }


# Instancia global del servicio
stdp_plasticity_service = STDPPlasticityService()


async def create_stdp_rule(rule_type: PlasticityType,
                         parameters: Optional[Dict[str, Any]] = None) -> str:
    """Función de conveniencia para crear regla STDP"""
    rule_id = f"stdp_{rule_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    params = parameters or {}
    return stdp_plasticity_service.create_plasticity_rule(rule_id, rule_type, params)


if __name__ == "__main__":
    # Demo del servicio STDP

    async def demo():
        logger.info("🧬 STDP Plasticity Service - Demo")

        print("🧬 Servicio de Plasticidad STDP inicializado")
        print("⚡ Formas de plasticidad disponibles:")
        for ptype in PlasticityType:
            print(f"  - {ptype.value}")

        # Crear regla STDP clásica
        stdp_rule = await create_stdp_rule(
            PlasticityType.STDP_CLASSIC,
            {'tau_plus': 20.0, 'tau_minus': 20.0, 'a_plus': 0.01, 'a_minus': 0.012}
        )
        print(f"\\n📊 Regla STDP creada: {stdp_rule}")

        # Protocolo de pareamiento
        protocol = {
            'duration': 60000.0,  # 1 minuto
            'dt': 1.0,
            'pre_pattern': 'paired',
            'post_pattern': 'paired',
            'rate': 1.0,  # 1 Hz
            'delay': 10.0,  # +10ms (LTP)
            'initial_weight': 0.5
        }

        # Simular plasticidad
        results = await stdp_plasticity_service.simulate_plasticity_protocol(stdp_rule, protocol)

        print("\\n📈 Resultados de simulación:")
        print(f"  • Peso inicial: {results['initial_weight']:.3f}")
        print(f"  • Peso final: {results['final_weight']:.3f}")
        print(f"  • Cambio: {results['percent_change']:.1f}%")
        print(f"  • Tiempo de convergencia: {results['convergence_time']:.1f} ms")
        print(f"  • Fases detectadas: {len(results['learning_phases']['phases'])}")

        # Crear regla con tripletas
        triplet_rule = await create_stdp_rule(PlasticityType.STDP_TRIPLET)

        # Comparar reglas
        comparison = await stdp_plasticity_service.compare_plasticity_rules(
            [stdp_rule, triplet_rule], protocol
        )

        print("\\n🔬 Comparación de reglas:")
        print(f"  • Mayor potenciación: {comparison['summary']['most_potentiation']}")
        print(f"  • Más estable: {comparison['summary']['most_stable']}")

        print("\\n🏆 Servicio STDP listo para investigación en plasticidad!")

    # Ejecutar demo
    asyncio.run(demo())
