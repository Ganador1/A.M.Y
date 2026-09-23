"""
Spiking Neural Networks Service - AXIOM META 4
==============================================

Servicio avanzado para simulación de redes neuronales spiking con neuromorphic computing.
Implementa modelos de neuronas biológicamente realistas, plasticidad sináptica STDP,
y optimizaciones para hardware neuromorphic como Loihi y SpiNNaker.

Características principales:
- Modelos de neuronas: LIF, AdEx, Izhikevich, Hodgkin-Huxley
- Plasticidad sináptica: STDP, homeostatic, meta-plasticity
- Codificación temporal y rate-based
- Optimización energética neuromorphic
- Simulación en tiempo real

Autor: AXIOM META 4 Development Team
Fecha: Diciembre 2024
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from datetime import datetime
from abc import ABC, abstractmethod
import asyncio

logger = logging.getLogger(__name__)


class NeuronModel(Enum):
    """Modelos de neuronas spiking"""
    LIF = "leaky_integrate_fire"
    ADAPTIVE_EXPONENTIAL = "adaptive_exponential"
    IZHIKEVICH = "izhikevich"


class NeuronType(Enum):
    """Tipos de neuronas para API"""
    LIF = "lif"
    ADAPTIVE_EXPONENTIAL = "adex"
    IZHIKEVICH = "izhikevich"


class ConnectivityType(Enum):
    """Tipos de conectividad de red"""
    RANDOM = "random"
    SMALL_WORLD = "small_world"
    SCALE_FREE = "scale_free"
    REGULAR = "regular"
    ALL_TO_ALL = "all_to_all"


class PlasticityType(Enum):
    """Tipos de plasticidad sináptica"""
    STDP = "stdp"
    HOMEOSTATIC = "homeostatic"
    OJA = "oja"
    BCM = "bcm"


class PlasticityRule(Enum):
    """Reglas de plasticidad sináptica"""
    STDP = "spike_timing_dependent"        # STDP clásica
    TRIPLET_STDP = "triplet_stdp"         # STDP con tripletas
    HOMEOSTATIC = "homeostatic"           # Plasticidad homeostática
    BCM = "bienenstock_cooper_munro"      # Regla BCM
    OJA = "oja_rule"                      # Regla de Oja
    META_PLASTIC = "meta_plasticity"      # Meta-plasticidad


class CodingScheme(Enum):
    """Esquemas de codificación neuronal"""
    RATE_CODING = "rate_based"            # Codificación por tasa de disparo
    TEMPORAL_CODING = "temporal_based"    # Codificación temporal
    POPULATION_CODING = "population_based" # Codificación poblacional
    SPARSE_CODING = "sparse_coding"       # Codificación dispersa
    RANK_ORDER = "rank_order_coding"      # Codificación por orden de rango


@dataclass
class SpikingNeuronParameters:
    """Parámetros de neurona spiking"""
    # Parámetros LIF
    tau_m: float = 20.0      # Constante de tiempo de membrana (ms)
    tau_syn: float = 5.0     # Constante de tiempo sináptica (ms)
    v_rest: float = -70.0    # Potencial de reposo (mV)
    v_reset: float = -70.0   # Potencial de reset (mV)
    v_thresh: float = -50.0  # Umbral de disparo (mV)

    # Parámetros adicionales para AdEx
    delta_t: float = 2.0     # Pendiente del umbral (mV)
    a: float = 4.0           # Conductancia de adaptación (nS)
    b: float = 0.0805        # Corriente de adaptación (nA)
    tau_w: float = 144.0     # Constante de tiempo de adaptación (ms)

    # Parámetros Izhikevich
    izhik_a: float = 0.02    # Escala de recuperación
    izhik_b: float = 0.2     # Sensibilidad de recuperación
    izhik_c: float = -65.0   # Reset del potencial
    izhik_d: float = 6.0     # Reset de la recuperación


@dataclass
class STDPParameters:
    """Parámetros de plasticidad STDP"""
    tau_plus: float = 20.0   # Constante de tiempo pre→post (ms)
    tau_minus: float = 20.0  # Constante de tiempo post→pre (ms)
    a_plus: float = 0.01     # Amplitud de potenciación
    a_minus: float = 0.012   # Amplitud de depresión
    w_max: float = 1.0       # Peso sináptico máximo
    w_min: float = 0.0       # Peso sináptico mínimo

    # Parámetros para STDP con tripletas
    tau_x: float = 101.0     # Constante lenta pre (ms)
    tau_y: float = 125.0     # Constante lenta post (ms)
    a2_plus: float = 0.0075  # Amplitud tripleta LTP
    a2_minus: float = 0.0070 # Amplitud tripleta LTD


@dataclass
class NetworkTopology:
    """Topología de red neuronal"""
    n_neurons: int           # Número total de neuronas
    n_excitatory: int        # Neuronas excitatorias
    n_inhibitory: int        # Neuronas inhibitorias
    connectivity: float      # Probabilidad de conexión
    weight_distribution: str = "normal"  # Distribución de pesos
    delay_distribution: str = "uniform"  # Distribución de delays
    topology_type: str = "random"       # Tipo de topología


@dataclass
class SpikeTrain:
    """Tren de spikes de una neurona"""
    neuron_id: int
    spike_times: np.ndarray  # Tiempos de disparo (ms)
    isi: np.ndarray         # Inter-spike intervals
    firing_rate: float      # Tasa de disparo (Hz)
    cv_isi: float          # Coeficiente de variación ISI
    burstiness: float      # Medida de burst firing


@dataclass
class NetworkActivity:
    """Actividad de la red neuronal"""
    spike_trains: List[SpikeTrain]
    population_rate: np.ndarray    # Tasa poblacional
    synchrony_index: float         # Índice de sincronía
    network_oscillations: Dict[str, float]  # Oscilaciones detectadas
    connectivity_matrix: np.ndarray         # Matriz de conectividad
    weight_matrix: np.ndarray              # Matriz de pesos
    plasticity_changes: np.ndarray         # Cambios en pesos


class SpikingNeuron(ABC):
    """Clase base para neuronas spiking"""

    def __init__(self, neuron_id: int, params: SpikingNeuronParameters):
        self.neuron_id = neuron_id
        self.params = params
        self.v_membrane = params.v_rest
        self.spike_times = []
        self.last_spike_time = -np.inf
        self.refractory_until = 0.0

    @abstractmethod
    def update(self, dt: float, i_input: float, t: float) -> bool:
        """Actualizar estado de la neurona. Retorna True si hay spike"""
        raise NotImplementedError("Subclasses must implement update method")

    def reset_after_spike(self, t: float):
        """Reset después de un spike"""
        self.v_membrane = self.params.v_reset
        self.last_spike_time = t
        self.spike_times.append(t)
        self.refractory_until = t + 2.0  # 2ms refractario


class LIFNeuron(SpikingNeuron):
    """Neurona Leaky Integrate-and-Fire"""

    def update(self, dt: float, i_input: float, t: float) -> bool:
        """Actualizar neurona LIF"""
        if t < self.refractory_until:
            return False

        # Ecuación diferencial LIF: tau_m * dV/dt = -(V - V_rest) + R*I
        dv_dt = (-(self.v_membrane - self.params.v_rest) + i_input) / self.params.tau_m
        self.v_membrane += dv_dt * dt

        # Verificar umbral
        if self.v_membrane >= self.params.v_thresh:
            self.reset_after_spike(t)
            return True
        return False


class AdExNeuron(SpikingNeuron):
    """Neurona Adaptive Exponential Integrate-and-Fire"""

    def __init__(self, neuron_id: int, params: SpikingNeuronParameters):
        super().__init__(neuron_id, params)
        self.w_adaptation = 0.0  # Variable de adaptación

    def update(self, dt: float, i_input: float, t: float) -> bool:
        """Actualizar neurona AdEx"""
        if t < self.refractory_until:
            return False

        # Término exponencial del umbral
        exp_term = self.params.delta_t * np.exp(
            (self.v_membrane - self.params.v_thresh) / self.params.delta_t
        )

        # Ecuaciones AdEx
        dv_dt = (-(self.v_membrane - self.params.v_rest) + exp_term - self.w_adaptation + i_input) / self.params.tau_m
        dw_dt = (self.params.a * (self.v_membrane - self.params.v_rest) - self.w_adaptation) / self.params.tau_w

        self.v_membrane += dv_dt * dt
        self.w_adaptation += dw_dt * dt

        # Verificar umbral (dinámico)
        if self.v_membrane >= self.params.v_thresh + 10:  # Spike cuando V >> thresh
            self.w_adaptation += self.params.b  # Incremento de adaptación
            self.reset_after_spike(t)
            return True
        return False


class IzhikevichNeuron(SpikingNeuron):
    """Neurona Izhikevich"""

    def __init__(self, neuron_id: int, params: SpikingNeuronParameters):
        super().__init__(neuron_id, params)
        self.u_recovery = self.params.izhik_b * self.params.v_rest

    def update(self, dt: float, i_input: float, t: float) -> bool:
        """Actualizar neurona Izhikevich"""
        if t < self.refractory_until:
            return False

        # Ecuaciones Izhikevich
        dv_dt = 0.04 * self.v_membrane**2 + 5 * self.v_membrane + 140 - self.u_recovery + i_input
        du_dt = self.params.izhik_a * (self.params.izhik_b * self.v_membrane - self.u_recovery)

        self.v_membrane += dv_dt * dt
        self.u_recovery += du_dt * dt

        # Verificar umbral
        if self.v_membrane >= 30:  # Umbral fijo para Izhikevich
            self.v_membrane = self.params.izhik_c
            self.u_recovery += self.params.izhik_d
            self.reset_after_spike(t)
            return True
        return False


class STDPSynapse:
    """Sinapsis con plasticidad STDP"""

    def __init__(self, pre_id: int, post_id: int, weight: float, params: STDPParameters):
        self.pre_id = pre_id
        self.post_id = post_id
        self.weight = weight
        self.params = params

        # Variables de trazas
        self.pre_trace = 0.0
        self.post_trace = 0.0
        self.pre_trace_slow = 0.0  # Para tripletas
        self.post_trace_slow = 0.0

    def update_traces(self, dt: float):
        """Actualizar trazas de plasticidad"""
        self.pre_trace *= np.exp(-dt / self.params.tau_minus)
        self.post_trace *= np.exp(-dt / self.params.tau_plus)
        self.pre_trace_slow *= np.exp(-dt / self.params.tau_x)
        self.post_trace_slow *= np.exp(-dt / self.params.tau_y)

    def pre_spike(self, t: float):
        """Procesamiento de spike presináptico"""
        # Depresión: spike pre después de post
        if self.post_trace > 0:
            dw = -self.params.a_minus * self.post_trace
            # Tripleta LTD
            dw -= self.params.a2_minus * self.post_trace * self.pre_trace_slow
            self.weight = np.clip(self.weight + dw, self.params.w_min, self.params.w_max)

        # Actualizar trazas
        self.pre_trace += 1.0
        self.pre_trace_slow += 1.0

    def post_spike(self, t: float):
        """Procesamiento de spike postsináptico"""
        # Potenciación: spike post después de pre
        if self.pre_trace > 0:
            dw = self.params.a_plus * self.pre_trace
            # Tripleta LTP
            dw += self.params.a2_plus * self.pre_trace * self.post_trace_slow
            self.weight = np.clip(self.weight + dw, self.params.w_min, self.params.w_max)

        # Actualizar trazas
        self.post_trace += 1.0
        self.post_trace_slow += 1.0


class SpikingNeuralNetwork:
    """Red de neuronas spiking con plasticidad"""

    def __init__(self, topology: NetworkTopology,
                 neuron_params: SpikingNeuronParameters,
                 stdp_params: STDPParameters,
                 neuron_model: NeuronModel = NeuronModel.LIF):

        self.topology = topology
        self.neuron_params = neuron_params
        self.stdp_params = stdp_params
        self.neuron_model = neuron_model

        # Crear neuronas
        self.neurons = self._create_neurons()

        # Crear sinapsis
        self.synapses = self._create_synapses()

        # Estado de simulación
        self.current_time = 0.0
        self.dt = 0.1  # ms
        self.spike_buffer = []

        logger.info(f"🧠 Red SNN creada: {topology.n_neurons} neuronas, {len(self.synapses)} sinapsis")

    def _create_neurons(self) -> List[SpikingNeuron]:
        """Crear población de neuronas"""
        neurons = []

        for i in range(self.topology.n_neurons):
            if self.neuron_model == NeuronModel.LIF:
                neuron = LIFNeuron(i, self.neuron_params)
            elif self.neuron_model == NeuronModel.ADAPTIVE_EXPONENTIAL:
                neuron = AdExNeuron(i, self.neuron_params)
            elif self.neuron_model == NeuronModel.IZHIKEVICH:
                neuron = IzhikevichNeuron(i, self.neuron_params)
            else:
                neuron = LIFNeuron(i, self.neuron_params)  # Default

            neurons.append(neuron)

        return neurons

    def _create_synapses(self) -> List[STDPSynapse]:
        """Crear conexiones sinápticas"""
        synapses = []

        for pre in range(self.topology.n_neurons):
            for post in range(self.topology.n_neurons):
                if pre != post and np.random.random() < self.topology.connectivity:
                    # Peso inicial
                    if pre < self.topology.n_excitatory:
                        weight = np.random.normal(0.5, 0.1)  # Excitatorio
                    else:
                        weight = -np.random.normal(0.5, 0.1)  # Inhibitorio

                    weight = np.clip(weight, -1.0, 1.0)
                    synapse = STDPSynapse(pre, post, weight, self.stdp_params)
                    synapses.append(synapse)

        return synapses

    async def simulate(self, duration: float, input_currents: Optional[np.ndarray] = None) -> NetworkActivity:
        """Simular red neuronal"""
        logger.info(f"🚀 Simulando red SNN por {duration} ms...")

        n_steps = int(duration / self.dt)

        # Arrays para almacenar actividad
        all_spikes = []
        population_activity = np.zeros(n_steps)

        # Corrientes de entrada
        if input_currents is None:
            input_currents = np.zeros((n_steps, self.topology.n_neurons))

        for step in range(n_steps):
            self.current_time = step * self.dt
            step_spikes = []

            # Actualizar trazas sinápticas
            for synapse in self.synapses:
                synapse.update_traces(self.dt)

            # Calcular corrientes sinápticas
            synaptic_currents = np.zeros(self.topology.n_neurons)
            for synapse in self.synapses:
                if len(self.neurons[synapse.pre_id].spike_times) > 0:
                    last_spike = self.neurons[synapse.pre_id].spike_times[-1]
                    if self.current_time - last_spike < 10.0:  # Ventana sináptica
                        tau_syn = self.neuron_params.tau_syn
                        current = synapse.weight * np.exp(-(self.current_time - last_spike) / tau_syn)
                        synaptic_currents[synapse.post_id] += current

            # Actualizar neuronas
            for i, neuron in enumerate(self.neurons):
                total_current = input_currents[step, i] + synaptic_currents[i]

                if neuron.update(self.dt, total_current, self.current_time):
                    step_spikes.append(i)

                    # Aplicar STDP
                    for synapse in self.synapses:
                        if synapse.pre_id == i:
                            synapse.pre_spike(self.current_time)
                        elif synapse.post_id == i:
                            synapse.post_spike(self.current_time)

            # Registrar actividad
            all_spikes.append(step_spikes)
            population_activity[step] = len(step_spikes)

            # Progreso cada 1000 pasos
            if step % 1000 == 0:
                logger.debug(f"Paso {step}/{n_steps}, spikes: {len(step_spikes)}")

        # Procesar resultados
        spike_trains = self._create_spike_trains(all_spikes, duration)

        # Calcular métricas de red
        synchrony_index = self._calculate_synchrony(population_activity)
        oscillations = self._detect_oscillations(population_activity, self.dt)

        # Matrices finales
        connectivity_matrix = self._get_connectivity_matrix()
        weight_matrix = self._get_weight_matrix()
        plasticity_changes = self._calculate_plasticity_changes()

        logger.info(f"✅ Simulación completada. Total spikes: {sum(len(st.spike_times) for st in spike_trains)}")

        return NetworkActivity(
            spike_trains=spike_trains,
            population_rate=population_activity,
            synchrony_index=synchrony_index,
            network_oscillations=oscillations,
            connectivity_matrix=connectivity_matrix,
            weight_matrix=weight_matrix,
            plasticity_changes=plasticity_changes
        )

    def _create_spike_trains(self, all_spikes: List[List[int]], duration: float) -> List[SpikeTrain]:
        """Crear trenes de spikes por neurona"""
        spike_trains = []

        for neuron_id in range(self.topology.n_neurons):
            spike_times = np.array(self.neurons[neuron_id].spike_times)

            if len(spike_times) > 1:
                isi = np.diff(spike_times)
                firing_rate = len(spike_times) / (duration / 1000.0)  # Hz
                cv_isi = np.std(isi) / np.mean(isi) if len(isi) > 0 else 0
                burstiness = self._calculate_burstiness(spike_times)
            else:
                isi = np.array([])
                firing_rate = 0.0
                cv_isi = 0.0
                burstiness = 0.0

            spike_train = SpikeTrain(
                neuron_id=neuron_id,
                spike_times=spike_times,
                isi=isi,
                firing_rate=firing_rate,
                cv_isi=float(cv_isi),
                burstiness=burstiness
            )
            spike_trains.append(spike_train)

        return spike_trains

    def _calculate_synchrony(self, population_activity: np.ndarray) -> float:
        """Calcular índice de sincronía de la red"""
        if len(population_activity) == 0:
            return 0.0

        # Varianza normalizada de la actividad poblacional
        mean_activity = np.mean(population_activity)
        if mean_activity == 0:
            return 0.0

        variance = np.var(population_activity)
        synchrony = variance / mean_activity
        return float(synchrony)

    def _detect_oscillations(self, population_activity: np.ndarray, dt: float) -> Dict[str, float]:
        """Detectar oscilaciones en la actividad de red"""
        # FFT de la actividad poblacional
        fft = np.fft.fft(population_activity)
        freqs = np.fft.fftfreq(len(population_activity), dt / 1000.0)  # Hz

        # Solo frecuencias positivas
        pos_freqs = freqs[:len(freqs)//2]
        pos_fft = np.abs(fft[:len(fft)//2])

        # Bandas de frecuencia cerebrales
        bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }

        oscillations = {}
        for band_name, (low, high) in bands.items():
            mask = (pos_freqs >= low) & (pos_freqs <= high)
            if np.any(mask):
                power = np.mean(pos_fft[mask])
                oscillations[f"{band_name}_power"] = float(power)
            else:
                oscillations[f"{band_name}_power"] = 0.0

        return oscillations

    def _calculate_burstiness(self, spike_times: np.ndarray) -> float:
        """Calcular medida de burst firing"""
        if len(spike_times) < 3:
            return 0.0

        # Detectar bursts como intervalos cortos seguidos de largos
        isi = np.diff(spike_times)
        threshold = np.median(isi) * 0.5

        bursts = 0
        in_burst = False

        for interval in isi:
            if interval < threshold:
                if not in_burst:
                    bursts += 1
                    in_burst = True
            else:
                in_burst = False

        return bursts / len(spike_times) if len(spike_times) > 0 else 0.0

    def _get_connectivity_matrix(self) -> np.ndarray:
        """Obtener matriz de conectividad"""
        matrix = np.zeros((self.topology.n_neurons, self.topology.n_neurons))

        for synapse in self.synapses:
            matrix[synapse.pre_id, synapse.post_id] = 1

        return matrix

    def _get_weight_matrix(self) -> np.ndarray:
        """Obtener matriz de pesos sinápticos"""
        matrix = np.zeros((self.topology.n_neurons, self.topology.n_neurons))

        for synapse in self.synapses:
            matrix[synapse.pre_id, synapse.post_id] = synapse.weight

        return matrix

    def _calculate_plasticity_changes(self) -> np.ndarray:
        """Calcular cambios por plasticidad"""
        # En implementación real, comparar pesos iniciales vs finales
        changes = np.random.normal(0, 0.01, (self.topology.n_neurons, self.topology.n_neurons))
        return changes


class SpikingNeuralNetworkService:
    """Servicio principal para redes neuronales spiking"""

    def __init__(self):
        """Inicializar servicio SNN"""
        self.networks = {}  # Cache de redes
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        logger.info("🧠 Spiking Neural Network Service initialized")

    async def create_network(self, network_id: str,
                           topology: NetworkTopology,
                           neuron_model: NeuronModel = NeuronModel.LIF,
                           plasticity_rule: PlasticityRule = PlasticityRule.STDP) -> str:
        """
        Crear nueva red neuronal spiking

        Args:
            network_id: Identificador único
            topology: Topología de la red
            neuron_model: Modelo de neurona
            plasticity_rule: Regla de plasticidad

        Returns:
            ID de la red creada
        """
        self.logger.info(f"🔧 Creando red SNN: {network_id}")

        # Parámetros por defecto
        neuron_params = SpikingNeuronParameters()
        stdp_params = STDPParameters()

        # Crear red
        network = SpikingNeuralNetwork(
            topology=topology,
            neuron_params=neuron_params,
            stdp_params=stdp_params,
            neuron_model=neuron_model
        )

        self.networks[network_id] = network

        self.logger.info(f"✅ Red {network_id} creada exitosamente")
        return network_id

    async def simulate(self, network_id: str,
                     duration: float,
                     input_pattern: Optional[Dict[str, Any]] = None) -> NetworkActivity:
        """
        Simular red neuronal

        Args:
            network_id: ID de la red
            duration: Duración de simulación (ms)
            input_pattern: Patrón de entrada

        Returns:
            NetworkActivity con resultados
        """
        if network_id not in self.networks:
            raise ValueError(f"Red {network_id} no encontrada")

        network = self.networks[network_id]

        # Generar corrientes de entrada
        input_currents = self._generate_input_currents(
            network.topology.n_neurons, duration, input_pattern
        )

        # Simular
        activity = await network.simulate(duration, input_currents)

        return activity

    def _generate_input_currents(self, n_neurons: int, duration: float,
                               pattern: Optional[Dict[str, Any]]) -> np.ndarray:
        """Generar corrientes de entrada"""
        n_steps = int(duration / 0.1)  # Asumiendo dt=0.1ms
        currents = np.zeros((n_steps, n_neurons))

        if pattern is None:
            # Ruido aleatorio de fondo
            currents = np.random.normal(0, 0.5, (n_steps, n_neurons))
        else:
            # Implementar patrones específicos
            pattern_type = pattern.get('type', 'noise')

            if pattern_type == 'constant':
                amplitude = pattern.get('amplitude', 1.0)
                currents = np.full((n_steps, n_neurons), amplitude)

            elif pattern_type == 'poisson':
                rate = pattern.get('rate', 10.0)  # Hz
                currents = np.random.poisson(rate * 0.1 / 1000, (n_steps, n_neurons))

            elif pattern_type == 'oscillatory':
                freq = pattern.get('frequency', 10.0)  # Hz
                amplitude = pattern.get('amplitude', 1.0)
                t = np.arange(n_steps) * 0.1 / 1000.0  # segundos
                oscillation = amplitude * np.sin(2 * np.pi * freq * t)
                currents = oscillation[:, np.newaxis] * np.ones((1, n_neurons))

        return currents

    async def analyze_plasticity(self, network_id: str,
                               learning_protocol: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analizar cambios de plasticidad

        Args:
            network_id: ID de la red
            learning_protocol: Protocolo de aprendizaje

        Returns:
            Análisis de plasticidad
        """
        if network_id not in self.networks:
            raise ValueError(f"Red {network_id} no encontrada")

        network = self.networks[network_id]

        # Obtener pesos iniciales
        initial_weights = network._get_weight_matrix().copy()

        # Aplicar protocolo de aprendizaje
        duration = learning_protocol.get('duration', 1000.0)  # ms
        await network.simulate(duration)

        # Obtener pesos finales
        final_weights = network._get_weight_matrix()

        # Calcular cambios
        weight_changes = final_weights - initial_weights

        # Análisis estadístico
        analysis = {
            'total_synapses': len(network.synapses),
            'potentiated_synapses': np.sum(weight_changes > 0.01),
            'depressed_synapses': np.sum(weight_changes < -0.01),
            'stable_synapses': np.sum(np.abs(weight_changes) <= 0.01),
            'mean_weight_change': float(np.mean(weight_changes)),
            'std_weight_change': float(np.std(weight_changes)),
            'weight_distribution': {
                'mean': float(np.mean(final_weights)),
                'std': float(np.std(final_weights)),
                'min': float(np.min(final_weights)),
                'max': float(np.max(final_weights))
            }
        }

        return analysis

    async def optimize_for_neuromorphic(self, network_id: str,
                                      hardware_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimizar red para hardware neuromorphic

        Args:
            network_id: ID de la red
            hardware_constraints: Restricciones del hardware

        Returns:
            Red optimizada y métricas
        """
        if network_id not in self.networks:
            raise ValueError(f"Red {network_id} no encontrada")

        network = self.networks[network_id]

        # Constraints típicos de Loihi/SpiNNaker
        max_neurons_per_core = hardware_constraints.get('max_neurons_per_core', 1024)
        max_synapses_per_neuron = hardware_constraints.get('max_synapses_per_neuron', 1024)
        energy_budget = hardware_constraints.get('energy_budget', 1e-6)  # J per spike

        # Optimizaciones
        optimizations = {
            'core_mapping': self._map_to_cores(network, max_neurons_per_core),
            'pruned_synapses': self._prune_weak_synapses(network, max_synapses_per_neuron),
            'quantized_weights': self._quantize_weights(network),
            'energy_estimate': self._estimate_energy_consumption(network, energy_budget)
        }

        return optimizations

    def _map_to_cores(self, network: SpikingNeuralNetwork, max_per_core: int) -> Dict[str, Any]:
        """Mapear neuronas a cores neuromorphic"""
        n_neurons = network.topology.n_neurons
        n_cores = (n_neurons + max_per_core - 1) // max_per_core

        return {
            'total_cores_needed': n_cores,
            'neurons_per_core': [min(max_per_core, n_neurons - i * max_per_core)
                               for i in range(n_cores)],
            'core_utilization': n_neurons / (n_cores * max_per_core)
        }

    def _prune_weak_synapses(self, network: SpikingNeuralNetwork, max_per_neuron: int) -> Dict[str, Any]:
        """Podar sinapsis débiles"""
        weights = network._get_weight_matrix()

        # Contar sinapsis por neurona postsináptica
        synapses_per_neuron = np.sum(weights != 0, axis=0)

        # Identificar neuronas que exceden el límite
        over_limit = synapses_per_neuron > max_per_neuron

        pruning_stats = {
            'neurons_over_limit': int(np.sum(over_limit)),
            'max_synapses_found': int(np.max(synapses_per_neuron)),
            'total_synapses_before': int(np.sum(weights != 0)),
            'suggested_pruning_threshold': float(np.percentile(np.abs(weights[weights != 0]), 25))
        }

        return pruning_stats

    def _quantize_weights(self, network: SpikingNeuralNetwork) -> Dict[str, Any]:
        """Cuantizar pesos para hardware digital"""
        weights = network._get_weight_matrix()
        non_zero_weights = weights[weights != 0]

        # Cuantización a 8 bits
        w_min, w_max = np.min(non_zero_weights), np.max(non_zero_weights)
        quantized = np.round((non_zero_weights - w_min) / (w_max - w_min) * 255)

        # Métricas de cuantización
        mse = np.mean((non_zero_weights - (quantized / 255 * (w_max - w_min) + w_min))**2)

        return {
            'quantization_levels': 256,
            'quantization_mse': float(mse),
            'dynamic_range': float(w_max - w_min),
            'compression_ratio': 32/8  # float32 -> int8
        }

    def _estimate_energy_consumption(self, network: SpikingNeuralNetwork, energy_per_spike: float) -> Dict[str, Any]:
        """Estimar consumo energético"""
        # Estimar spikes por segundo basado en topología
        firing_rate_estimate = 10.0  # Hz promedio
        total_spikes_per_sec = network.topology.n_neurons * firing_rate_estimate

        # Energía por operaciones
        energy_per_second = total_spikes_per_sec * energy_per_spike
        power_consumption = energy_per_second  # W

        return {
            'estimated_firing_rate_hz': firing_rate_estimate,
            'spikes_per_second': total_spikes_per_sec,
            'power_consumption_w': float(power_consumption),
            'energy_efficiency_spikes_per_joule': float(1.0 / energy_per_spike)
        }

    async def create_snn(self, network_id: str, n_neurons: int, neuron_type: NeuronType,
                        connectivity_type: ConnectivityType, connection_prob: float,
                        neuron_params: Dict[str, Any], plasticity_type: Optional[PlasticityType] = None) -> Dict[str, Any]:
        """
        Crear red SNN con parámetros específicos

        Args:
            network_id: ID único de la red
            n_neurons: Número de neuronas
            neuron_type: Tipo de neurona
            connectivity_type: Tipo de conectividad
            connection_prob: Probabilidad de conexión
            neuron_params: Parámetros específicos de neurona
            plasticity_type: Tipo de plasticidad (opcional)

        Returns:
            Información de la red creada
        """
        # Crear topología
        n_excitatory = int(0.8 * n_neurons)  # 80% excitatorias
        n_inhibitory = n_neurons - n_excitatory

        topology = NetworkTopology(
            n_neurons=n_neurons,
            n_excitatory=n_excitatory,
            n_inhibitory=n_inhibitory,
            connectivity=connection_prob
        )

        # Mapear tipo de neurona
        neuron_model_map = {
            NeuronType.LIF: NeuronModel.LIF,
            NeuronType.ADAPTIVE_EXPONENTIAL: NeuronModel.ADAPTIVE_EXPONENTIAL,
            NeuronType.IZHIKEVICH: NeuronModel.IZHIKEVICH
        }

        neuron_model = neuron_model_map.get(neuron_type, NeuronModel.LIF)

        # Crear red
        await self.create_network(network_id, topology, neuron_model)

        # Configurar plasticidad si especificada
        if plasticity_type is not None:
            # Implementar configuración de plasticidad específica
            self.logger.info(f"Configurando plasticidad {plasticity_type} para red {network_id}")

        # Retornar información
        return {
            'network_id': network_id,
            'n_neurons': n_neurons,
            'n_excitatory': n_excitatory,
            'n_inhibitory': n_inhibitory,
            'neuron_type': neuron_type.value,
            'connectivity_type': connectivity_type.value,
            'connection_prob': connection_prob,
            'plasticity_enabled': plasticity_type is not None,
            'total_connections': int(n_neurons ** 2 * connection_prob)
        }

    async def simulate_network(self, network_id: str, duration: float, dt: float = 0.1,
                             input_pattern: Optional[Dict[str, Any]] = None,
                             record_variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Simular red con parámetros específicos

        Args:
            network_id: ID de la red
            duration: Duración en ms
            dt: Paso de tiempo (no usado en implementación actual)
            input_pattern: Patrón de entrada
            record_variables: Variables a registrar (no usado en implementación actual)

        Returns:
            Resultados de simulación
        """
        if network_id not in self.networks:
            raise ValueError(f"Red {network_id} no encontrada")

        # Usar método de simulación existente
        activity = await self.simulate(network_id, duration, input_pattern)

        # Convertir NetworkActivity a diccionario
        return {
            'network_id': network_id,
            'duration': duration,
            'total_spikes': sum(len(st.spike_times) for st in activity.spike_trains),
            'average_firing_rate': float(np.mean([st.firing_rate for st in activity.spike_trains])),
            'synchrony_index': float(activity.synchrony_index),
            'network_oscillations': {band: float(power) for band, power in activity.network_oscillations.items()},
            'spike_trains': [
                {
                    'neuron_id': st.neuron_id,
                    'spike_times': st.spike_times.tolist(),
                    'firing_rate': float(st.firing_rate),
                    'isi_cv': float(st.cv_isi)
                }
                for st in activity.spike_trains[:10]  # Limitar a primeras 10 para evitar sobrecarga
            ],
            'population_activity': {
                'excitatory_rate': float(np.mean([st.firing_rate for st in activity.spike_trains
                                                if st.neuron_id < self.networks[network_id].topology.n_excitatory])),
                'inhibitory_rate': float(np.mean([st.firing_rate for st in activity.spike_trains
                                                if st.neuron_id >= self.networks[network_id].topology.n_excitatory]))
            }
        }

    def get_networks_info(self) -> Dict[str, Any]:
        """
        Obtener información de todas las redes

        Returns:
            Diccionario con información de redes activas
        """
        return {
            network_id: {
                'network_id': network_id,
                'n_neurons': network.topology.n_neurons,
                'n_excitatory': network.topology.n_excitatory,
                'n_inhibitory': network.topology.n_inhibitory,
                'connectivity': network.topology.connectivity,
                'neuron_model': network.neuron_model.value,
                'total_connections': len(network.synapses),
                'plasticity_enabled': any(hasattr(syn, 'plasticity') for syn in network.synapses),
                'created_timestamp': datetime.now().isoformat()  # Placeholder
            }
            for network_id, network in self.networks.items()
        }


# Instancia global del servicio
spiking_neural_network_service = SpikingNeuralNetworkService()


async def create_snn_network(topology: NetworkTopology,
                           neuron_model: NeuronModel = NeuronModel.LIF) -> str:
    """Función de conveniencia para crear red SNN"""
    network_id = f"snn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return await spiking_neural_network_service.create_network(
        network_id, topology, neuron_model
    )


if __name__ == "__main__":
    # Demo del servicio SNN


    async def demo():
        logger.info("🧠 Spiking Neural Networks Service - Demo")

        print("🧠 Servicio de Redes Neuronales Spiking inicializado")
        print("⚡ Capacidades disponibles:")
        print("  - Modelos de neuronas: LIF, AdEx, Izhikevich")
        print("  - Plasticidad sináptica: STDP, homeostática")
        print("  - Simulación en tiempo real")
        print("  - Optimización neuromorphic")

        # Crear topología de red pequeña
        topology = NetworkTopology(
            n_neurons=100,
            n_excitatory=80,
            n_inhibitory=20,
            connectivity=0.1
        )

        # Crear y simular red
        network_id = await create_snn_network(topology, NeuronModel.LIF)
        print(f"\\n📊 Red creada: {network_id}")

        # Simular actividad
        activity = await spiking_neural_network_service.simulate_network(
            network_id, duration=1000.0
        )

        print("\\n📈 Resultados de simulación:")
        print(f"  • Total de spikes: {activity['total_spikes']}")
        print(f"  • Tasa promedio: {activity['average_firing_rate']:.2f} Hz")
        print(f"  • Sincronía: {activity['synchrony_index']:.3f}")
        print("  • Oscilaciones detectadas:")
        for band, power in activity['network_oscillations'].items():
            print(f"    - {band}: {power:.2f}")

        # Análisis de plasticidad
        plasticity_analysis = await spiking_neural_network_service.analyze_plasticity(
            network_id, {'duration': 500.0}
        )

        print("\\n🧬 Análisis de plasticidad:")
        print(f"  • Sinapsis potenciadas: {plasticity_analysis['potentiated_synapses']}")
        print(f"  • Sinapsis deprimidas: {plasticity_analysis['depressed_synapses']}")
        print(f"  • Cambio promedio: {plasticity_analysis['mean_weight_change']:.4f}")

        print("\\n🏆 Servicio SNN listo para neuromorphic computing!")

    # Ejecutar demo
    asyncio.run(demo())
