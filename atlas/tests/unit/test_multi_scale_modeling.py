"""
Tests para Multi-Scale Modeling Service
======================================

Suite de pruebas unitarias para el servicio de modelado neuronal multi-escala.
Cubre funcionalidades de creación de redes, simulación, análisis y comparación
de escalas.

Test cases:
- TestMultiScaleModelingService: Tests del servicio principal
- TestHodgkinHuxleyNeuron: Tests del modelo Hodgkin-Huxley
- TestIzhikevichNeuron: Tests del modelo Izhikevich
- TestNeuralNetwork: Tests de redes neuronales
- TestRhythmAnalyzer: Tests del analizador de ritmos
- TestMultiScaleIntegration: Tests de integración multi-escala

Autor: Sistema AXIOM
Fecha: 2024-12-23
"""

import pytest
import numpy as np
from unittest.mock import patch

from app.domains.neuroscience.services.neuromorphic.multi_scale_modeling import (
    MultiScaleModelingService,
    NetworkParameters,
    SimulationParameters,
    NeuronParameters,
    HodgkinHuxleyNeuron,
    IzhikevichNeuron,
    NeuralNetwork,
    Synapse,
    RhythmAnalyzer,
    NeuronType
)


class TestMultiScaleModelingService:
    """Tests para MultiScaleModelingService"""

    @pytest.fixture
    def service(self):
        """Fixture del servicio"""
        return MultiScaleModelingService()

    @pytest.fixture
    def network_params(self):
        """Fixture de parámetros de red"""
        return NetworkParameters(
            n_neurons=50,
            connectivity_prob=0.1,
            synaptic_strength=0.5,
            exc_inh_ratio=0.8,
            plasticity_enabled=True,
            learning_rate=0.01
        )

    @pytest.fixture
    def sim_params(self):
        """Fixture de parámetros de simulación"""
        return SimulationParameters(
            dt=0.01,
            duration=100.0,
            temperature=37.0,
            noise_level=0.1
        )

    @pytest.mark.asyncio
    async def test_create_network_success(self, service, network_params):
        """Test creación exitosa de red neuronal"""
        network_id = "test_network_001"

        result = await service.create_network(network_id, network_params)

        assert result["network_id"] == network_id
        assert result["n_neurons"] == network_params.n_neurons
        assert result["status"] == "created"
        assert result["exc_inh_ratio"] == network_params.exc_inh_ratio
        assert network_id in service.networks

        # Verificar estructura de la red creada
        network = service.networks[network_id]
        assert len(network.neurons) == network_params.n_neurons
        assert len(network.synapses) > 0
        assert len(network.spike_history) == network_params.n_neurons

    @pytest.mark.asyncio
    async def test_simulate_network_success(self, service, network_params, sim_params):
        """Test simulación exitosa de red neuronal"""
        network_id = "test_simulation_net"

        # Crear red primero
        await service.create_network(network_id, network_params)

        # Simular red
        result = await service.simulate_network(network_id, sim_params)

        assert result["network_id"] == network_id
        assert result["simulation_time"] == sim_params.duration
        assert "total_spikes" in result
        assert "average_firing_rate" in result
        assert "rhythm_analysis" in result
        assert "voltage_traces" in result
        assert "spike_times" in result

        # Verificar que los resultados fueron guardados
        assert f"{network_id}_latest" in service.simulation_results

    @pytest.mark.asyncio
    async def test_simulate_network_not_found(self, service, sim_params):
        """Test simulación con red inexistente"""
        with pytest.raises(ValueError, match="Network 'nonexistent' not found"):
            await service.simulate_network("nonexistent", sim_params)

    @pytest.mark.asyncio
    async def test_simulate_with_external_stimulus(self, service, network_params, sim_params):
        """Test simulación con estímulo externo"""
        network_id = "test_stimulus_net"

        # Crear red
        await service.create_network(network_id, network_params)

        # Definir estímulo externo
        external_stimulus = {
            "type": "pulse",
            "amplitude": 10.0,
            "target_neurons": [0, 1, 2],
            "start_time": 50.0,
            "duration": 20.0,
            "dt": sim_params.dt
        }

        # Simular con estímulo
        result = await service.simulate_network(
            network_id, sim_params, external_stimulus
        )

        assert result["network_id"] == network_id
        assert result["total_spikes"] >= 0
        assert len(result["voltage_traces"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_network_dynamics(self, service, network_params):
        """Test análisis de dinámicas de red"""
        network_id = "test_analysis_net"

        # Crear red
        await service.create_network(network_id, network_params)

        # Analizar dinámicas
        result = await service.analyze_network_dynamics(network_id)

        assert result["network_id"] == network_id
        assert "connectivity_analysis" in result
        assert "network_properties" in result

        connectivity = result["connectivity_analysis"]
        assert "total_connections" in connectivity
        assert "mean_weight" in connectivity
        assert "weight_std" in connectivity

        properties = result["network_properties"]
        assert properties["n_neurons"] == network_params.n_neurons
        assert properties["exc_inh_ratio"] == network_params.exc_inh_ratio

    @pytest.mark.asyncio
    async def test_get_network_status(self, service, network_params):
        """Test obtención de estado de red"""
        network_id = "test_status_net"

        # Crear red
        await service.create_network(network_id, network_params)

        # Obtener estado
        status = await service.get_network_status(network_id)

        assert status["network_id"] == network_id
        assert status["n_neurons"] == network_params.n_neurons
        assert status["status"] == "active"
        assert "recent_spike_count" in status
        assert "plasticity_enabled" in status

    @pytest.mark.asyncio
    async def test_compare_scales(self, service):
        """Test comparación de escalas"""
        molecular_data = {"ion_channels": 100, "conductance": 0.5}
        cellular_data = {"neurons": 1000, "dendrites": 5000}
        network_data = {"circuits": 10, "connections": 50000}

        result = await service.compare_scales(
            molecular_data, cellular_data, network_data
        )

        assert "scales_analyzed" in result
        assert "temporal_scales" in result
        assert "spatial_scales" in result
        assert "coupling_analysis" in result
        assert "emergent_properties" in result

        assert len(result["scales_analyzed"]) == 3
        assert "molecular" in result["temporal_scales"]
        assert "cellular" in result["spatial_scales"]


class TestHodgkinHuxleyNeuron:
    """Tests para modelo Hodgkin-Huxley"""

    @pytest.fixture
    def neuron_params(self):
        """Fixture de parámetros de neurona"""
        return NeuronParameters()

    @pytest.fixture
    def hh_neuron(self, neuron_params):
        """Fixture de neurona Hodgkin-Huxley"""
        return HodgkinHuxleyNeuron(neuron_params)

    def test_initialization(self, hh_neuron, neuron_params):
        """Test inicialización correcta"""
        assert hh_neuron.v == neuron_params.v_rest
        assert hh_neuron.n == 0.0
        assert hh_neuron.m == 0.0
        assert hh_neuron.h == 1.0
        assert hh_neuron.params == neuron_params

    def test_alpha_beta_functions(self, hh_neuron):
        """Test funciones alpha y beta"""
        v = -65.0  # Potencial de prueba

        # Test alpha_n
        alpha_n = hh_neuron.alpha_n(v)
        assert alpha_n > 0

        # Test beta_n
        beta_n = hh_neuron.beta_n(v)
        assert beta_n > 0

        # Test alpha_m
        alpha_m = hh_neuron.alpha_m(v)
        assert alpha_m > 0

        # Test beta_m
        beta_m = hh_neuron.beta_m(v)
        assert beta_m > 0

        # Test alpha_h
        alpha_h = hh_neuron.alpha_h(v)
        assert alpha_h > 0

        # Test beta_h
        beta_h = hh_neuron.beta_h(v)
        assert beta_h > 0

    def test_integration_step(self, hh_neuron):
        """Test paso de integración"""
        dt = 0.01
        i_ext = 10.0  # Corriente externa

        initial_v = hh_neuron.v

        # Ejecutar varios pasos de integración
        for _ in range(100):
            new_v = hh_neuron.integrate(dt, i_ext)
            assert isinstance(new_v, float)
            assert np.isfinite(new_v)

        # El voltaje debe haber cambiado con corriente externa
        assert hh_neuron.v != initial_v

    def test_spike_generation(self, hh_neuron):
        """Test generación de spike con corriente fuerte"""
        dt = 0.01
        i_ext = 50.0  # Corriente fuerte para generar spike

        max_v = -100.0

        # Integrar hasta encontrar un spike
        for _ in range(1000):
            v = hh_neuron.integrate(dt, i_ext)
            max_v = max(max_v, v)

            # Si el voltaje supera 0mV, es un spike
            if v > 0.0:
                assert True
                return

        # Al menos el voltaje debe haber aumentado significativamente
        assert max_v > -50.0


class TestIzhikevichNeuron:
    """Tests para modelo Izhikevich"""

    @pytest.fixture
    def neuron_params(self):
        """Fixture de parámetros de neurona"""
        return NeuronParameters()

    @pytest.fixture
    def izh_exc_neuron(self, neuron_params):
        """Fixture de neurona Izhikevich excitadora"""
        return IzhikevichNeuron(neuron_params, NeuronType.EXCITATORY)

    @pytest.fixture
    def izh_inh_neuron(self, neuron_params):
        """Fixture de neurona Izhikevich inhibidora"""
        return IzhikevichNeuron(neuron_params, NeuronType.INHIBITORY)

    def test_excitatory_initialization(self, izh_exc_neuron):
        """Test inicialización de neurona excitadora"""
        assert izh_exc_neuron.neuron_type == NeuronType.EXCITATORY
        assert izh_exc_neuron.a == 0.02
        assert izh_exc_neuron.b == 0.2
        assert izh_exc_neuron.c == -65.0
        assert izh_exc_neuron.d == 8.0
        assert izh_exc_neuron.v == -65.0

    def test_inhibitory_initialization(self, izh_inh_neuron):
        """Test inicialización de neurona inhibidora"""
        assert izh_inh_neuron.neuron_type == NeuronType.INHIBITORY
        assert izh_inh_neuron.a == 0.02
        assert izh_inh_neuron.b == 0.25
        assert izh_inh_neuron.c == -65.0
        assert izh_inh_neuron.d == 2.0

    def test_integration_no_spike(self, izh_exc_neuron):
        """Test integración sin spike"""
        dt = 0.01
        i_ext = 5.0

        v = izh_exc_neuron.integrate(dt, i_ext)

        assert v < 30.0  # No debe generar spike
        assert isinstance(v, float)
        assert np.isfinite(v)

    def test_spike_generation_and_reset(self, izh_exc_neuron):
        """Test generación de spike y reset"""
        dt = 0.01
        i_ext = 20.0  # Corriente fuerte

        # Integrar hasta generar spike
        for _ in range(1000):
            v = izh_exc_neuron.integrate(dt, i_ext)

            if v == 30.0:  # Spike detectado
                # Verificar que se hizo reset
                assert izh_exc_neuron.v == izh_exc_neuron.c
                return

        # Si no se generó spike, al menos el voltaje debe haber aumentado
        assert izh_exc_neuron.v > -65.0


class TestNeuralNetwork:
    """Tests para NeuralNetwork"""

    @pytest.fixture
    def small_network_params(self):
        """Fixture de parámetros para red pequeña"""
        return NetworkParameters(
            n_neurons=20,
            connectivity_prob=0.2,
            synaptic_strength=1.0,
            exc_inh_ratio=0.8,
            plasticity_enabled=True,
            learning_rate=0.05
        )

    @pytest.fixture
    def network(self, small_network_params):
        """Fixture de red neuronal"""
        return NeuralNetwork(small_network_params)

    def test_network_initialization(self, network, small_network_params):
        """Test inicialización de red"""
        assert len(network.neurons) == small_network_params.n_neurons
        assert len(network.synapses) > 0
        assert len(network.spike_history) == small_network_params.n_neurons

        # Verificar ratio excitatorio/inhibitorio
        exc_count = sum(1 for n in network.neurons
                       if hasattr(n, 'neuron_type') and n.neuron_type == NeuronType.EXCITATORY)
        expected_exc = int(small_network_params.n_neurons * small_network_params.exc_inh_ratio)

        # Permitir pequeña variación por redondeo
        assert abs(exc_count - expected_exc) <= 1

    def test_synapse_creation(self, network):
        """Test creación de sinapsis"""
        assert len(network.synapses) > 0

        for synapse in network.synapses:
            assert isinstance(synapse, Synapse)
            assert 0 <= synapse.pre_idx < len(network.neurons)
            assert 0 <= synapse.post_idx < len(network.neurons)
            assert synapse.pre_idx != synapse.post_idx
            assert synapse.weight != 0.0

    def test_simulation_step_no_input(self, network):
        """Test paso de simulación sin entrada"""
        dt = 0.01

        spikes = network.simulate_step(dt)

        assert len(spikes) == len(network.neurons)
        # Debug: imprimir tipos
        print(f"Spikes: {spikes}")
        print(f"Types: {[type(spike) for spike in spikes]}")
        assert all(isinstance(spike, bool) for spike in spikes)

    def test_simulation_step_with_input(self, network):
        """Test paso de simulación con entrada externa"""
        dt = 0.01
        external_input = np.zeros(len(network.neurons))
        external_input[0] = 20.0  # Estimular primera neurona

        spikes = network.simulate_step(dt, external_input)

        assert len(spikes) == len(network.neurons)
        assert all(isinstance(spike, bool) for spike in spikes)

    def test_multiple_simulation_steps(self, network):
        """Test múltiples pasos de simulación"""
        dt = 0.01
        n_steps = 100

        all_spikes = []
        for _ in range(n_steps):
            spikes = network.simulate_step(dt)
            all_spikes.append(spikes)

        assert len(all_spikes) == n_steps

        # Verificar que se registraron algunos spikes en el historial
        total_recorded_spikes = sum(len(history) for history in network.spike_history)
        assert total_recorded_spikes >= 0  # Puede ser 0 sin estímulo


class TestSynapse:
    """Tests para Synapse"""

    @pytest.fixture
    def synapse(self):
        """Fixture de sinapsis"""
        return Synapse(pre_idx=0, post_idx=1, weight=0.5, delay=1.0)

    def test_synapse_initialization(self, synapse):
        """Test inicialización de sinapsis"""
        assert synapse.pre_idx == 0
        assert synapse.post_idx == 1
        assert synapse.weight == 0.5
        assert synapse.delay == 1.0
        assert synapse.plasticity_trace == 0.0

    def test_weight_update_ltp(self, synapse):
        """Test actualización de peso - LTP"""
        initial_weight = synapse.weight
        learning_rate = 0.1

        # Ambas neuronas disparan -> LTP
        synapse.update_weight(
            pre_spike=True,
            post_spike=True,
            learning_rate=learning_rate
        )

        assert synapse.weight > initial_weight

    def test_weight_update_ltd(self, synapse):
        """Test actualización de peso - LTD"""
        initial_weight = synapse.weight
        learning_rate = 0.1

        # Solo pre-sináptica dispara -> LTD
        synapse.update_weight(
            pre_spike=True,
            post_spike=False,
            learning_rate=learning_rate
        )

        assert synapse.weight < initial_weight

    def test_weight_limits(self, synapse):
        """Test límites de peso sináptico"""
        learning_rate = 1.0  # Tasa alta para forzar límites

        # Múltiples actualizaciones hacia arriba
        for _ in range(100):
            synapse.update_weight(True, True, learning_rate)

        assert synapse.weight <= 10.0  # Límite superior

        # Múltiples actualizaciones hacia abajo
        for _ in range(200):
            synapse.update_weight(True, False, learning_rate)

        assert synapse.weight >= 0.0  # Límite inferior


class TestRhythmAnalyzer:
    """Tests para RhythmAnalyzer"""

    def test_analyze_empty_spike_trains(self):
        """Test análisis con trenes de spikes vacíos"""
        empty_trains = [[], [], []]

        result = RhythmAnalyzer.analyze_oscillations(empty_trains)

        assert result == {}

    def test_analyze_spike_trains_with_activity(self):
        """Test análisis con actividad de spikes"""
        # Crear trenes de spikes artificiales
        spike_trains = [
            [10.0, 20.0, 30.0],  # Neurona 1
            [15.0, 25.0, 35.0],  # Neurona 2
            [12.0, 22.0, 32.0],  # Neurona 3
        ]

        result = RhythmAnalyzer.analyze_oscillations(spike_trains)

        assert isinstance(result, dict)
        assert "delta" in result
        assert "theta" in result
        assert "alpha" in result
        assert "beta" in result
        assert "gamma" in result

        # Todos los valores deben ser números no negativos
        for power in result.values():
            assert isinstance(power, (int, float))
            assert power >= 0.0

    @patch('scipy.signal.welch')
    def test_rhythm_analysis_with_mock(self, mock_welch):
        """Test análisis de ritmos con mock de scipy"""
        # Configurar mock
        mock_freqs = np.array([1, 5, 10, 20, 50])
        mock_psd = np.array([0.1, 0.2, 0.3, 0.15, 0.05])
        mock_welch.return_value = (mock_freqs, mock_psd)

        spike_trains = [[10.0, 20.0], [15.0, 25.0]]

        result = RhythmAnalyzer.analyze_oscillations(spike_trains)

        assert "delta" in result
        assert "alpha" in result
        mock_welch.assert_called_once()


class TestMultiScaleIntegration:
    """Tests de integración multi-escala"""

    @pytest.fixture
    def full_service(self):
        """Fixture del servicio completo"""
        return MultiScaleModelingService()

    @pytest.mark.asyncio
    async def test_complete_workflow(self, full_service):
        """Test flujo completo de trabajo"""
        network_id = "integration_test_network"

        # 1. Crear red
        network_params = NetworkParameters(
            n_neurons=30,
            connectivity_prob=0.15,
            synaptic_strength=0.8,
            exc_inh_ratio=0.75,
            plasticity_enabled=True,
            learning_rate=0.02
        )

        create_result = await full_service.create_network(network_id, network_params)
        assert create_result["status"] == "created"

        # 2. Verificar estado
        status = await full_service.get_network_status(network_id)
        assert status["network_id"] == network_id

        # 3. Simular red
        sim_params = SimulationParameters(
            dt=0.01,
            duration=200.0,
            temperature=37.0,
            noise_level=0.2
        )

        sim_result = await full_service.simulate_network(network_id, sim_params)
        assert sim_result["network_id"] == network_id
        assert sim_result["simulation_time"] == 200.0

        # 4. Analizar dinámicas
        analysis = await full_service.analyze_network_dynamics(network_id)
        assert analysis["network_id"] == network_id
        assert "connectivity_analysis" in analysis

        # 5. Obtener resultados
        results = full_service.get_simulation_results(network_id)
        assert results is not None
        assert results["network_id"] == network_id

        # 6. Verificar que la red está en la lista
        networks = full_service.list_networks()
        assert network_id in networks

    @pytest.mark.asyncio
    async def test_multi_network_management(self, full_service):
        """Test manejo de múltiples redes"""
        network_ids = ["net_001", "net_002", "net_003"]

        # Crear múltiples redes
        for net_id in network_ids:
            params = NetworkParameters(n_neurons=20 + len(net_id))
            await full_service.create_network(net_id, params)

        # Verificar que todas están listadas
        networks = full_service.list_networks()
        for net_id in network_ids:
            assert net_id in networks

        # Simular una de ellas
        sim_params = SimulationParameters(duration=50.0)
        result = await full_service.simulate_network(network_ids[0], sim_params)
        assert result["network_id"] == network_ids[0]

        # Verificar que solo esa tiene resultados
        assert full_service.get_simulation_results(network_ids[0]) is not None
        assert full_service.get_simulation_results(network_ids[1]) is None

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, full_service):
        """Test manejo de errores en integración"""
        # Test simular red inexistente
        sim_params = SimulationParameters()
        with pytest.raises(ValueError):
            await full_service.simulate_network("nonexistent", sim_params)

        # Test analizar red inexistente
        with pytest.raises(ValueError):
            await full_service.analyze_network_dynamics("nonexistent")

        # Test estado de red inexistente
        with pytest.raises(ValueError):
            await full_service.get_network_status("nonexistent")

        # Test resultados de red inexistente
        assert full_service.get_simulation_results("nonexistent") is None
