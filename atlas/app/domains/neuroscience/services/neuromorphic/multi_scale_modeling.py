"""
Multi-Scale Modeling Service
==========================

Servicio avanzado para modelado neuronal multi-escala que integra desde el nivel molecular
hasta redes neuronales completas, incluyendo:

- Modelado de canales iónicos (nivel molecular)
- Modelado de neuronas individuales (modelo Hodgkin-Huxley, Izhikevich)
- Modelado de redes neuronales (conectividad, plasticidad)
- Análisis de dinámica de poblaciones
- Simulación de ritmos cerebrales
- Acoplamiento multi-escala

Autor: Sistema AXIOM
Fecha: 2024-12-23
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from abc import ABC, abstractmethod
from app.exceptions.domain.neuroscience import NeuroscienceError

logger = logging.getLogger(__name__)


class ModelingScale(Enum):
    """Escalas de modelado neuronal"""
    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    NETWORK = "network"
    POPULATION = "population"
    SYSTEM = "system"


class NeuronType(Enum):
    """Tipos de neuronas"""
    EXCITATORY = "excitatory"
    INHIBITORY = "inhibitory"
    PYRAMIDAL = "pyramidal"
    INTERNEURON = "interneuron"


@dataclass
class NeuronParameters:
    """Parámetros de neurona individual"""
    capacitance: float = 1.0  # µF/cm²
    g_na: float = 120.0  # mS/cm² - Conductancia de sodio
    g_k: float = 36.0   # mS/cm² - Conductancia de potasio
    g_l: float = 0.3    # mS/cm² - Conductancia de fuga
    e_na: float = 50.0  # mV - Potencial de inversión de sodio
    e_k: float = -77.0  # mV - Potencial de inversión de potasio
    e_l: float = -54.4  # mV - Potencial de inversión de fuga
    v_rest: float = -70.0  # mV - Potencial de reposo


@dataclass
class NetworkParameters:
    """Parámetros de red neuronal"""
    n_neurons: int = 100
    connectivity_prob: float = 0.1
    synaptic_strength: float = 0.5
    exc_inh_ratio: float = 0.8
    plasticity_enabled: bool = True
    learning_rate: float = 0.01


@dataclass
class SimulationParameters:
    """Parámetros de simulación"""
    dt: float = 0.01  # ms
    duration: float = 1000.0  # ms
    temperature: float = 37.0  # °C
    noise_level: float = 0.1


class NeuronModel(ABC):
    """Clase base para modelos de neurona"""

    def __init__(self, params: NeuronParameters):
        self.params = params
        self.v = params.v_rest  # Potencial de membrana
        self.n = 0.0  # Variable de activación K+
        self.m = 0.0  # Variable de activación Na+
        self.h = 1.0  # Variable de inactivación Na+

    @abstractmethod
    def integrate(self, dt: float, i_ext: float = 0.0) -> float:
        """Integrar la dinámica de la neurona"""


class HodgkinHuxleyNeuron(NeuronModel):
    """Modelo de neurona Hodgkin-Huxley"""

    def alpha_n(self, v: float) -> float:
        """Función alpha para activación de K+"""
        if abs(v + 55.0) < 1e-6:
            return 0.1
        return 0.01 * (v + 55.0) / (1.0 - np.exp(-(v + 55.0) / 10.0))

    def beta_n(self, v: float) -> float:
        """Función beta para activación de K+"""
        return 0.125 * np.exp(-(v + 65.0) / 80.0)

    def alpha_m(self, v: float) -> float:
        """Función alpha para activación de Na+"""
        if abs(v + 40.0) < 1e-6:
            return 1.0
        return 0.1 * (v + 40.0) / (1.0 - np.exp(-(v + 40.0) / 10.0))

    def beta_m(self, v: float) -> float:
        """Función beta para activación de Na+"""
        return 4.0 * np.exp(-(v + 65.0) / 18.0)

    def alpha_h(self, v: float) -> float:
        """Función alpha para inactivación de Na+"""
        return 0.07 * np.exp(-(v + 65.0) / 20.0)

    def beta_h(self, v: float) -> float:
        """Función beta para inactivación de Na+"""
        return 1.0 / (1.0 + np.exp(-(v + 35.0) / 10.0))

    def integrate(self, dt: float, i_ext: float = 0.0) -> float:
        """Integrar ecuaciones de Hodgkin-Huxley"""
        v = self.v

        # Calcular funciones de transición
        an = self.alpha_n(v)
        bn = self.beta_n(v)
        am = self.alpha_m(v)
        bm = self.beta_m(v)
        ah = self.alpha_h(v)
        bh = self.beta_h(v)

        # Actualizar variables de compuerta
        self.n += dt * (an * (1.0 - self.n) - bn * self.n)
        self.m += dt * (am * (1.0 - self.m) - bm * self.m)
        self.h += dt * (ah * (1.0 - self.h) - bh * self.h)

        # Calcular corrientes
        i_na = self.params.g_na * (self.m ** 3) * self.h * (v - self.params.e_na)
        i_k = self.params.g_k * (self.n ** 4) * (v - self.params.e_k)
        i_l = self.params.g_l * (v - self.params.e_l)

        # Actualizar potencial de membrana
        dv_dt = (i_ext - i_na - i_k - i_l) / self.params.capacitance
        self.v += dt * dv_dt

        return self.v


class IzhikevichNeuron(NeuronModel):
    """Modelo de neurona Izhikevich (más eficiente computacionalmente)"""

    def __init__(self, params: NeuronParameters, neuron_type: NeuronType = NeuronType.EXCITATORY):
        super().__init__(params)
        self.neuron_type = neuron_type

        # Parámetros del modelo Izhikevich
        if neuron_type == NeuronType.EXCITATORY:
            self.a = 0.02
            self.b = 0.2
            self.c = -65.0
            self.d = 8.0
        else:  # INHIBITORY
            self.a = 0.02
            self.b = 0.25
            self.c = -65.0
            self.d = 2.0

        self.v = self.c
        self.u = self.b * self.v

    def integrate(self, dt: float, i_ext: float = 0.0) -> float:
        """Integrar ecuaciones de Izhikevich"""
        # Ecuaciones de Izhikevich
        dv = 0.04 * self.v * self.v + 5 * self.v + 140 - self.u + i_ext
        du = self.a * (self.b * self.v - self.u)

        self.v += dt * dv
        self.u += dt * du

        # Spike y reset
        if self.v >= 30.0:
            self.v = self.c
            self.u += self.d
            return 30.0  # Indica spike

        return self.v


class Synapse:
    """Modelo de sinapsis"""

    def __init__(self, pre_idx: int, post_idx: int, weight: float, delay: float = 1.0):
        self.pre_idx = pre_idx
        self.post_idx = post_idx
        self.weight = weight
        self.delay = delay
        self.plasticity_trace = 0.0

    def update_weight(self, pre_spike: bool, post_spike: bool, learning_rate: float):
        """Actualizar peso sináptico con STDP"""
        if pre_spike and post_spike:
            # LTP (potenciación a largo plazo)
            self.weight += learning_rate * 0.1
        elif pre_spike and not post_spike:
            # LTD (depresión a largo plazo)
            self.weight -= learning_rate * 0.05

        # Límites de peso
        self.weight = np.clip(self.weight, 0.0, 10.0)


class NeuralNetwork:
    """Red neuronal multi-escala"""

    def __init__(self, params: NetworkParameters):
        self.params = params
        self.neurons: List[NeuronModel] = []
        self.synapses: List[Synapse] = []
        self.spike_history: List[List[float]] = []

        self._initialize_network()

    def _initialize_network(self):
        """Inicializar la red neuronal"""
        # Crear neuronas
        n_exc = int(self.params.n_neurons * self.params.exc_inh_ratio)
        n_inh = self.params.n_neurons - n_exc

        neuron_params = NeuronParameters()

        # Neuronas excitatorias
        for _ in range(n_exc):
            neuron = IzhikevichNeuron(neuron_params, NeuronType.EXCITATORY)
            self.neurons.append(neuron)

        # Neuronas inhibitorias
        for _ in range(n_inh):
            neuron = IzhikevichNeuron(neuron_params, NeuronType.INHIBITORY)
            self.neurons.append(neuron)

        # Crear conexiones sinápticas
        self._create_synapses()

        # Inicializar historial de spikes
        self.spike_history = [[] for _ in range(self.params.n_neurons)]

    def _create_synapses(self):
        """Crear conexiones sinápticas aleatorias"""
        for i in range(self.params.n_neurons):
            for j in range(self.params.n_neurons):
                if i != j and np.random.random() < self.params.connectivity_prob:
                    # Peso base según tipo de neurona
                    if isinstance(self.neurons[i], IzhikevichNeuron):
                        neuron = self.neurons[i]
                        if hasattr(neuron, 'neuron_type') and neuron.neuron_type == NeuronType.EXCITATORY:
                            weight = self.params.synaptic_strength
                        else:
                            weight = -self.params.synaptic_strength  # Inhibitoria
                    else:
                        weight = self.params.synaptic_strength

                    synapse = Synapse(i, j, weight)
                    self.synapses.append(synapse)

    def simulate_step(self, dt: float, external_input: Optional[np.ndarray] = None) -> List[bool]:
        """Simular un paso de tiempo de la red"""
        if external_input is None:
            external_input = np.zeros(self.params.n_neurons)

        # Calcular entrada sináptica para cada neurona
        synaptic_input = np.zeros(self.params.n_neurons)

        for synapse in self.synapses:
            # Verificar si la neurona presináptica disparó recientemente
            pre_spikes = self.spike_history[synapse.pre_idx]
            if pre_spikes and len(pre_spikes) > 0:
                # Simplificado: asumir que el efecto sináptico es inmediato
                synaptic_input[synapse.post_idx] += synapse.weight

        # Integrar cada neurona
        spikes = []
        for i, neuron in enumerate(self.neurons):
            total_input = external_input[i] + synaptic_input[i]
            v = neuron.integrate(dt, total_input)

            # Detectar spike (simplificado)
            if isinstance(neuron, IzhikevichNeuron):
                spike = v == 30.0  # El modelo Izhikevich devuelve exactamente 30.0 para un spike
            else:
                spike = v >= 30.0  # Para Hodgkin-Huxley, usar umbral
            # Convertir a bool nativo de Python
            spikes.append(bool(spike))

            if spike:
                self.spike_history[i].append(len(self.spike_history[i]) * dt)

        # Actualizar pesos sinápticos si la plasticidad está habilitada
        if self.params.plasticity_enabled:
            self._update_synaptic_weights(spikes)

        return spikes

    def _update_synaptic_weights(self, current_spikes: List[bool]):
        """Actualizar pesos sinápticos usando STDP"""
        for synapse in self.synapses:
            pre_spike = current_spikes[synapse.pre_idx]
            post_spike = current_spikes[synapse.post_idx]
            synapse.update_weight(pre_spike, post_spike, self.params.learning_rate)


class RhythmAnalyzer:
    """Analizador de ritmos cerebrales"""

    @staticmethod
    def analyze_oscillations(spike_trains: List[List[float]],
                           sampling_rate: float = 1000.0) -> Dict[str, float]:
        """Analizar oscilaciones en los trenes de spikes"""
        if not spike_trains or not any(spike_trains):
            return {}

        # Crear señal binaria de population spikes
        max_time = max(max(train) if train else 0 for train in spike_trains)
        time_bins = np.arange(0, max_time, 1.0/sampling_rate)
        population_rate = np.zeros(len(time_bins))

        for train in spike_trains:
            for spike_time in train:
                bin_idx = int(spike_time * sampling_rate)
                if 0 <= bin_idx < len(population_rate):
                    population_rate[bin_idx] += 1

        # Análisis espectral
        from scipy import signal
        freqs, psd = signal.welch(population_rate, fs=sampling_rate, nperseg=256)

        # Identificar bandas de frecuencia
        rhythm_bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }

        rhythm_powers = {}
        for band_name, (low_freq, high_freq) in rhythm_bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            if np.any(band_mask):
                rhythm_powers[band_name] = np.mean(psd[band_mask])
            else:
                rhythm_powers[band_name] = 0.0

        return rhythm_powers


class MultiScaleModelingService:
    """Servicio principal de modelado multi-escala"""

    def __init__(self):
        self.networks: Dict[str, NeuralNetwork] = {}
        self.simulation_results: Dict[str, Any] = {}
        logger.info("✅ MultiScaleModelingService initialized")

    async def create_network(self, network_id: str,
                           network_params: NetworkParameters) -> Dict[str, Any]:
        """Crear una nueva red neuronal"""
        try:
            network = NeuralNetwork(network_params)
            self.networks[network_id] = network

            logger.info(f"✅ Neural network '{network_id}' created with {network_params.n_neurons} neurons")

            return {
                "network_id": network_id,
                "n_neurons": network_params.n_neurons,
                "n_synapses": len(network.synapses),
                "exc_inh_ratio": network_params.exc_inh_ratio,
                "status": "created"
            }

        except NeuroscienceError as e:
            logger.error(f"❌ Error creating network '{network_id}': {e}")
            raise

    async def simulate_network(self, network_id: str,
                             sim_params: SimulationParameters,
                             external_stimulus: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simular una red neuronal"""
        if network_id not in self.networks:
            raise ValueError(f"Network '{network_id}' not found")

        network = self.networks[network_id]

        # Parámetros de simulación
        n_steps = int(sim_params.duration / sim_params.dt)
        time_points = np.arange(0, sim_params.duration, sim_params.dt)

        # Preparar estímulo externo
        if external_stimulus:
            ext_input = self._prepare_external_input(
                external_stimulus, network.params.n_neurons, n_steps
            )
        else:
            ext_input = np.zeros((n_steps, network.params.n_neurons))

        # Ejecutar simulación
        all_spikes = []
        voltage_traces = []

        logger.info(f"🧠 Starting simulation of network '{network_id}' for {sim_params.duration}ms")

        for step in range(n_steps):
            # Añadir ruido
            noise = np.random.normal(0, sim_params.noise_level, network.params.n_neurons)
            current_input = ext_input[step] + noise

            # Simular paso
            spikes = network.simulate_step(sim_params.dt, current_input)
            all_spikes.append(spikes)

            # Guardar voltajes (solo algunas neuronas para eficiencia)
            sample_voltages = []
            for i in range(min(10, len(network.neurons))):
                if hasattr(network.neurons[i], 'v'):
                    sample_voltages.append(network.neurons[i].v)
                else:
                    sample_voltages.append(0.0)
            voltage_traces.append(sample_voltages)

        # Analizar resultados
        rhythm_analysis = RhythmAnalyzer.analyze_oscillations(
            network.spike_history, 1000.0 / sim_params.dt
        )

        # Calcular estadísticas
        total_spikes = sum(sum(spikes) for spikes in all_spikes)
        firing_rate = total_spikes / (network.params.n_neurons * sim_params.duration / 1000.0)

        results = {
            "network_id": network_id,
            "simulation_time": sim_params.duration,
            "total_spikes": int(total_spikes),
            "average_firing_rate": float(firing_rate),
            "rhythm_analysis": rhythm_analysis,
            "voltage_traces": voltage_traces[:100],  # Limitado para eficiencia
            "spike_times": network.spike_history[:10],  # Primeras 10 neuronas
            "time_points": time_points[:len(voltage_traces)].tolist()
        }

        # Guardar resultados
        self.simulation_results[f"{network_id}_latest"] = results

        logger.info(f"✅ Simulation completed. Firing rate: {firing_rate:.2f} Hz")

        return results

    def _prepare_external_input(self, stimulus: Dict[str, Any],
                              n_neurons: int, n_steps: int) -> np.ndarray:
        """Preparar entrada externa para la simulación"""
        ext_input = np.zeros((n_steps, n_neurons))

        stimulus_type = stimulus.get('type', 'constant')
        amplitude = stimulus.get('amplitude', 5.0)
        target_neurons = stimulus.get('target_neurons', list(range(min(10, n_neurons))))

        if stimulus_type == 'constant':
            for neuron_idx in target_neurons:
                if neuron_idx < n_neurons:
                    ext_input[:, neuron_idx] = amplitude

        elif stimulus_type == 'pulse':
            start_time = stimulus.get('start_time', 100.0)  # ms
            duration = stimulus.get('duration', 50.0)  # ms
            dt = stimulus.get('dt', 0.01)

            start_step = int(start_time / dt)
            end_step = int((start_time + duration) / dt)

            for neuron_idx in target_neurons:
                if neuron_idx < n_neurons:
                    ext_input[start_step:end_step, neuron_idx] = amplitude

        elif stimulus_type == 'oscillatory':
            frequency = stimulus.get('frequency', 10.0)  # Hz
            dt = stimulus.get('dt', 0.01)

            time_points = np.arange(n_steps) * dt / 1000.0  # convertir a segundos
            oscillation = amplitude * np.sin(2 * np.pi * frequency * time_points)

            for neuron_idx in target_neurons:
                if neuron_idx < n_neurons:
                    ext_input[:, neuron_idx] = oscillation

        return ext_input

    async def analyze_network_dynamics(self, network_id: str) -> Dict[str, Any]:
        """Analizar dinámicas de red"""
        if network_id not in self.networks:
            raise ValueError(f"Network '{network_id}' not found")

        network = self.networks[network_id]

        # Análisis de conectividad
        connectivity_matrix = np.zeros((network.params.n_neurons, network.params.n_neurons))
        weight_distribution = []

        for synapse in network.synapses:
            connectivity_matrix[synapse.pre_idx, synapse.post_idx] = synapse.weight
            weight_distribution.append(abs(synapse.weight))

        # Estadísticas de conectividad
        total_connections = len(network.synapses)
        mean_weight = np.mean(weight_distribution) if weight_distribution else 0.0
        weight_std = np.std(weight_distribution) if weight_distribution else 0.0

        # Análisis de grado de nodos
        in_degrees = np.sum(connectivity_matrix != 0, axis=0)
        out_degrees = np.sum(connectivity_matrix != 0, axis=1)

        return {
            "network_id": network_id,
            "connectivity_analysis": {
                "total_connections": total_connections,
                "connection_probability": total_connections / (network.params.n_neurons ** 2),
                "mean_weight": float(mean_weight),
                "weight_std": float(weight_std),
                "mean_in_degree": float(np.mean(in_degrees)),
                "mean_out_degree": float(np.mean(out_degrees))
            },
            "network_properties": {
                "n_neurons": network.params.n_neurons,
                "exc_inh_ratio": network.params.exc_inh_ratio,
                "plasticity_enabled": network.params.plasticity_enabled
            }
        }

    async def get_network_status(self, network_id: str) -> Dict[str, Any]:
        """Obtener estado de una red"""
        if network_id not in self.networks:
            raise ValueError(f"Network '{network_id}' not found")

        network = self.networks[network_id]

        # Contar spikes recientes
        recent_activity = 0
        for spike_train in network.spike_history:
            if spike_train:
                recent_activity += len(spike_train)

        return {
            "network_id": network_id,
            "n_neurons": network.params.n_neurons,
            "n_synapses": len(network.synapses),
            "recent_spike_count": recent_activity,
            "plasticity_enabled": network.params.plasticity_enabled,
            "status": "active"
        }

    async def compare_scales(self, molecular_data: Dict[str, Any],
                           cellular_data: Dict[str, Any],
                           network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comparar diferentes escalas de modelado"""
        return {
            "scales_analyzed": ["molecular", "cellular", "network"],
            "temporal_scales": {
                "molecular": "microseconds to milliseconds",
                "cellular": "milliseconds to seconds",
                "network": "seconds to minutes"
            },
            "spatial_scales": {
                "molecular": "nanometers (ion channels)",
                "cellular": "micrometers (single neurons)",
                "network": "millimeters to centimeters (neural circuits)"
            },
            "coupling_analysis": {
                "molecular_to_cellular": "Ion channel dynamics affect neuronal excitability",
                "cellular_to_network": "Individual neuron properties shape network dynamics",
                "network_to_cellular": "Network activity modulates single neuron behavior"
            },
            "emergent_properties": {
                "oscillations": "Network-level rhythms emerge from cellular interactions",
                "synchronization": "Population-level synchrony from local connectivity",
                "plasticity": "Learning emerges from synaptic weight changes"
            }
        }

    def list_networks(self) -> List[str]:
        """Listar todas las redes disponibles"""
        return list(self.networks.keys())

    def get_simulation_results(self, network_id: str) -> Optional[Dict[str, Any]]:
        """Obtener resultados de simulación"""
        return self.simulation_results.get(f"{network_id}_latest")
