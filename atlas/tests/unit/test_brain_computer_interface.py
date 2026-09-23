"""
Tests unitarios para Brain-Computer Interface Service
"""

import pytest
import numpy as np

from app.domains.neuroscience.services.neuromorphic.brain_computer_interface import (
    BrainComputerInterfaceService,
    BCIModalityType,
    DecodingAlgorithm,
    BCISignalData,
    EEGMotorImageryDecoder,
    P300SpellerDecoder,
    SignalQuality
)


class TestBrainComputerInterfaceService:
    """Tests para BrainComputerInterfaceService"""

    @pytest.fixture
    def bci_service(self):
        """Fixture del servicio BCI"""
        return BrainComputerInterfaceService()

    @pytest.fixture
    def sample_signal_data(self):
        """Fixture con datos de señal de prueba"""
        return {
            'channels': ['C3', 'C4', 'Cz'],
            'sampling_rate': 250.0,
            'data': np.random.randn(3, 1000).tolist(),
            'timestamps': (np.arange(1000) / 250.0).tolist(),
            'quality_scores': {'C3': 0.8, 'C4': 0.85, 'Cz': 0.75},
            'metadata': {'session': 'test'}
        }

    @pytest.mark.asyncio
    async def test_initialize_decoder_motor_imagery(self, bci_service):
        """Test inicialización de decodificador motor imagery"""
        decoder_id = "test_motor_imagery"
        config = {'adaptation_rate': 0.1, 'frequency_bands': [(8, 12), (12, 30)]}

        result = await bci_service.initialize_decoder(
            decoder_id,
            BCIModalityType.MOTOR_IMAGERY,
            DecodingAlgorithm.CSP,
            config
        )

        assert result['status'] == 'initialized'
        assert result['decoder_id'] == decoder_id
        assert result['modality'] == 'motor_imagery'
        assert result['algorithm'] == 'common_spatial_pattern'
        assert decoder_id in bci_service.decoders
        assert isinstance(bci_service.decoders[decoder_id], EEGMotorImageryDecoder)

    @pytest.mark.asyncio
    async def test_initialize_decoder_p300(self, bci_service):
        """Test inicialización de decodificador P300"""
        decoder_id = "test_p300"
        config = {'detection_threshold': 0.7}

        result = await bci_service.initialize_decoder(
            decoder_id,
            BCIModalityType.P300,
            DecodingAlgorithm.LDA,
            config
        )

        assert result['status'] == 'initialized'
        assert result['decoder_id'] == decoder_id
        assert result['modality'] == 'p300'
        assert decoder_id in bci_service.decoders
        assert isinstance(bci_service.decoders[decoder_id], P300SpellerDecoder)

    @pytest.mark.asyncio
    async def test_train_decoder_success(self, bci_service, sample_signal_data):
        """Test entrenamiento exitoso de decodificador"""
        decoder_id = "test_decoder"

        # Inicializar decodificador
        await bci_service.initialize_decoder(
            decoder_id,
            BCIModalityType.MOTOR_IMAGERY,
            DecodingAlgorithm.CSP,
            {}
        )

        # Datos de entrenamiento
        training_signals = [sample_signal_data.copy() for _ in range(10)]
        labels = ["left_hand" if i % 2 == 0 else "right_hand" for i in range(10)]

        result = await bci_service.train_decoder(decoder_id, training_signals, labels)

        assert result['status'] == 'trained'
        assert result['decoder_id'] == decoder_id
        assert 'training_result' in result
        assert result['training_result']['status'] == 'trained_successfully'

    @pytest.mark.asyncio
    async def test_train_decoder_not_found(self, bci_service, sample_signal_data):
        """Test entrenamiento de decodificador inexistente"""
        result = await bci_service.train_decoder("nonexistent", [sample_signal_data], ["test"])

        assert result['status'] == 'failed'
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_decode_real_time_success(self, bci_service, sample_signal_data):
        """Test decodificación en tiempo real exitosa"""
        decoder_id = "test_decoder"

        # Inicializar y entrenar decodificador
        await bci_service.initialize_decoder(
            decoder_id,
            BCIModalityType.MOTOR_IMAGERY,
            DecodingAlgorithm.CSP,
            {}
        )

        training_signals = [sample_signal_data.copy() for _ in range(5)]
        labels = ["left_hand", "right_hand", "left_hand", "right_hand", "left_hand"]
        await bci_service.train_decoder(decoder_id, training_signals, labels)

        # Decodificar
        result = await bci_service.decode_real_time(decoder_id, sample_signal_data)

        assert result['status'] == 'decoded'
        assert result['decoder_id'] == decoder_id
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'class_probabilities' in result
        assert 'processing_time_ms' in result
        assert result['prediction'] in ['left_hand', 'right_hand']
        assert 0 <= result['confidence'] <= 1

    @pytest.mark.asyncio
    async def test_decode_real_time_decoder_not_found(self, bci_service, sample_signal_data):
        """Test decodificación con decodificador inexistente"""
        result = await bci_service.decode_real_time("nonexistent", sample_signal_data)

        assert result['status'] == 'failed'
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_adapt_decoder_success(self, bci_service, sample_signal_data):
        """Test adaptación exitosa de decodificador"""
        decoder_id = "test_decoder"

        # Inicializar y entrenar decodificador
        await bci_service.initialize_decoder(
            decoder_id,
            BCIModalityType.MOTOR_IMAGERY,
            DecodingAlgorithm.CSP,
            {}
        )

        training_signals = [sample_signal_data.copy() for _ in range(3)]
        labels = ["left_hand", "right_hand", "left_hand"]
        await bci_service.train_decoder(decoder_id, training_signals, labels)

        # Adaptar
        result = await bci_service.adapt_decoder(decoder_id, sample_signal_data, "right_hand")

        assert result['status'] == 'adapted'
        assert result['decoder_id'] == decoder_id
        assert result['true_label'] == "right_hand"
        assert 'adaptation_result' in result

    @pytest.mark.asyncio
    async def test_calibrate_user_session(self, bci_service):
        """Test calibración de sesión de usuario"""
        user_id = "test_user"
        modality = BCIModalityType.MOTOR_IMAGERY
        protocol = {'session_duration': 300, 'break_interval': 60}

        result = await bci_service.calibrate_user_session(user_id, modality, protocol)

        assert result['status'] == 'calibrated'
        assert result['user_id'] == user_id
        assert result['modality'] == 'motor_imagery'
        assert 'baseline_established' in result
        assert 'performance_metrics' in result
        assert user_id in bci_service.calibration_data

    @pytest.mark.asyncio
    async def test_get_system_status(self, bci_service):
        """Test obtención de estado del sistema"""
        # Crear algunos decodificadores
        await bci_service.initialize_decoder("decoder1", BCIModalityType.MOTOR_IMAGERY, DecodingAlgorithm.CSP, {})
        await bci_service.initialize_decoder("decoder2", BCIModalityType.P300, DecodingAlgorithm.LDA, {})

        # Calibrar un usuario
        await bci_service.calibrate_user_session("user1", BCIModalityType.MOTOR_IMAGERY, {})

        status = await bci_service.get_system_status()

        assert status['system_status'] == 'operational'
        assert status['active_decoders'] == 2
        assert status['calibrated_users'] == 1
        assert 'decoder_details' in status
        assert len(status['decoder_details']) == 2
        assert status['adaptation_enabled'] is True

    @pytest.mark.asyncio
    async def test_simulate_real_time_session(self, bci_service):
        """Test simulación de sesión en tiempo real"""
        duration = 5  # 5 segundos

        result = await bci_service.simulate_real_time_session(duration)

        assert result['status'] == 'simulation_completed'
        assert result['session_duration_seconds'] == duration
        assert 'total_predictions' in result
        assert 'average_confidence' in result
        assert 'prediction_distribution' in result
        assert 'detailed_results' in result
        assert len(result['detailed_results']) == duration

    def test_get_decoder_capabilities_motor_imagery(self, bci_service):
        """Test obtención de capacidades motor imagery"""
        capabilities = bci_service._get_decoder_capabilities(BCIModalityType.MOTOR_IMAGERY)

        assert 'classes' in capabilities
        assert 'frequency_bands' in capabilities
        assert 'spatial_filtering' in capabilities
        assert 'real_time' in capabilities
        assert 'left_hand' in capabilities['classes']
        assert 'right_hand' in capabilities['classes']

    def test_get_decoder_capabilities_p300(self, bci_service):
        """Test obtención de capacidades P300"""
        capabilities = bci_service._get_decoder_capabilities(BCIModalityType.P300)

        assert 'classes' in capabilities
        assert 'temporal_window_ms' in capabilities
        assert 'averaging' in capabilities
        assert 'speller_compatible' in capabilities
        assert 'P300' in capabilities['classes']
        assert 'non_P300' in capabilities['classes']


class TestEEGMotorImageryDecoder:
    """Tests para EEGMotorImageryDecoder"""

    @pytest.fixture
    def decoder(self):
        """Fixture del decodificador motor imagery"""
        config = {
            'adaptation_rate': 0.1,
            'frequency_bands': [(8, 12), (12, 30)]
        }
        return EEGMotorImageryDecoder(config)

    @pytest.fixture
    def signal_data(self):
        """Fixture con datos de señal BCI"""
        return BCISignalData(
            channels=['C3', 'C4', 'Cz'],
            sampling_rate=250.0,
            signal_data=np.random.randn(3, 1000),
            timestamps=np.arange(1000) / 250.0,
            quality_scores={'C3': 0.8, 'C4': 0.85, 'Cz': 0.75}
        )

    @pytest.mark.asyncio
    async def test_train_decoder(self, decoder, signal_data):
        """Test entrenamiento de decodificador motor imagery"""
        training_data = [signal_data for _ in range(10)]
        labels = ["left_hand" if i % 2 == 0 else "right_hand" for i in range(10)]

        result = await decoder.train(training_data, labels)

        assert result['status'] == 'trained_successfully'
        assert 'training_accuracy' in result
        assert 'feature_dimension' in result
        assert 'csp_eigenvalues' in result
        assert decoder.csp_filters is not None
        assert decoder.classifier is not None

    @pytest.mark.asyncio
    async def test_decode_signal(self, decoder, signal_data):
        """Test decodificación de señal"""
        # Entrenar primero
        training_data = [signal_data for _ in range(5)]
        labels = ["left_hand", "right_hand", "left_hand", "right_hand", "left_hand"]
        await decoder.train(training_data, labels)

        # Decodificar
        result = await decoder.decode(signal_data)

        assert result.predicted_class in ['left_hand', 'right_hand']
        assert 0 <= result.confidence <= 1
        assert len(result.class_probabilities) == 2
        assert 'left_hand' in result.class_probabilities
        assert 'right_hand' in result.class_probabilities
        assert result.processing_time_ms > 0
        assert isinstance(result.signal_quality, SignalQuality)

    @pytest.mark.asyncio
    async def test_adapt_decoder(self, decoder, signal_data):
        """Test adaptación de decodificador"""
        # Entrenar primero
        training_data = [signal_data for _ in range(3)]
        labels = ["left_hand", "right_hand", "left_hand"]
        await decoder.train(training_data, labels)

        # Adaptar
        result = await decoder.adapt(signal_data, "right_hand")

        assert result['adaptation_performed'] is True
        assert 'new_accuracy_estimate' in result
        assert 'weight_change_magnitude' in result

    def test_extract_band_powers(self, decoder, signal_data):
        """Test extracción de potencias en bandas"""
        band_powers = decoder._extract_band_powers(signal_data)

        assert isinstance(band_powers, np.ndarray)
        assert len(band_powers) == len(decoder.frequency_bands) * len(signal_data.channels)
        assert all(power >= 0 for power in band_powers)

    def test_assess_signal_quality(self, decoder, signal_data):
        """Test evaluación de calidad de señal"""
        quality = decoder._assess_signal_quality(signal_data)

        assert isinstance(quality, SignalQuality)
        assert quality in [SignalQuality.EXCELLENT, SignalQuality.GOOD,
                          SignalQuality.FAIR, SignalQuality.POOR, SignalQuality.UNUSABLE]


class TestP300SpellerDecoder:
    """Tests para P300SpellerDecoder"""

    @pytest.fixture
    def decoder(self):
        """Fixture del decodificador P300"""
        config = {'detection_threshold': 0.7}
        return P300SpellerDecoder(config)

    @pytest.fixture
    def signal_data(self):
        """Fixture con datos de señal P300"""
        return BCISignalData(
            channels=['Fz', 'Cz', 'Pz'],
            sampling_rate=250.0,
            signal_data=np.random.randn(3, 800),  # 800ms epoch
            timestamps=np.arange(800) / 250.0,
            quality_scores={'Fz': 0.8, 'Cz': 0.85, 'Pz': 0.75}
        )

    @pytest.mark.asyncio
    async def test_train_p300_template(self, decoder, signal_data):
        """Test entrenamiento de template P300"""
        training_data = [signal_data for _ in range(10)]
        labels = ["P300" if i < 5 else "non_P300" for i in range(10)]

        result = await decoder.train(training_data, labels)

        assert result['template_created'] is True
        assert 'p300_trials_count' in result
        assert 'peak_latency_ms' in result
        assert 'amplitude_uv' in result
        assert decoder.template is not None

    @pytest.mark.asyncio
    async def test_decode_p300(self, decoder, signal_data):
        """Test detección P300"""
        # Entrenar template primero
        training_data = [signal_data for _ in range(5)]
        labels = ["P300", "P300", "non_P300", "P300", "non_P300"]
        await decoder.train(training_data, labels)

        # Decodificar
        result = await decoder.decode(signal_data)

        assert result.predicted_class in ['P300', 'non_P300']
        assert 0 <= result.confidence <= 1
        assert len(result.class_probabilities) == 2
        assert 'P300' in result.class_probabilities
        assert 'non_P300' in result.class_probabilities
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_decode_no_template(self, decoder, signal_data):
        """Test decodificación sin template"""
        result = await decoder.decode(signal_data)

        assert result.predicted_class == "no_template"
        assert result.confidence == 0.0
        assert len(result.class_probabilities) == 0

    @pytest.mark.asyncio
    async def test_adapt_p300_template(self, decoder, signal_data):
        """Test adaptación del template P300"""
        # Entrenar template primero
        training_data = [signal_data for _ in range(3)]
        labels = ["P300", "P300", "non_P300"]
        await decoder.train(training_data, labels)

        original_template = decoder.template.copy()

        # Adaptar
        result = await decoder.adapt(signal_data, "P300")

        assert result['template_updated'] is True
        # Template debe haber cambiado
        assert not np.array_equal(decoder.template, original_template)


# Tests de integración
class TestBCIIntegration:
    """Tests de integración del sistema BCI"""

    @pytest.mark.asyncio
    async def test_complete_bci_workflow(self):
        """Test flujo completo BCI: inicializar -> entrenar -> decodificar -> adaptar"""
        service = BrainComputerInterfaceService()
        decoder_id = "integration_test"

        # 1. Inicializar
        init_result = await service.initialize_decoder(
            decoder_id,
            BCIModalityType.MOTOR_IMAGERY,
            DecodingAlgorithm.CSP,
            {'adaptation_rate': 0.1}
        )
        assert init_result['status'] == 'initialized'

        # 2. Entrenar
        training_signals = []
        labels = []
        for i in range(10):
            signal = {
                'channels': ['C3', 'C4', 'Cz'],
                'sampling_rate': 250.0,
                'data': np.random.randn(3, 1000).tolist(),
                'timestamps': (np.arange(1000) / 250.0).tolist()
            }
            training_signals.append(signal)
            labels.append("left_hand" if i % 2 == 0 else "right_hand")

        train_result = await service.train_decoder(decoder_id, training_signals, labels)
        assert train_result['status'] == 'trained'

        # 3. Decodificar
        test_signal = {
            'channels': ['C3', 'C4', 'Cz'],
            'sampling_rate': 250.0,
            'data': np.random.randn(3, 250).tolist(),
            'timestamps': (np.arange(250) / 250.0).tolist(),
            'quality_scores': {'C3': 0.8, 'C4': 0.85, 'Cz': 0.75}
        }

        decode_result = await service.decode_real_time(decoder_id, test_signal)
        assert decode_result['status'] == 'decoded'
        assert decode_result['prediction'] in ['left_hand', 'right_hand']

        # 4. Adaptar
        adapt_result = await service.adapt_decoder(decoder_id, test_signal, "left_hand")
        assert adapt_result['status'] == 'adapted'

    @pytest.mark.asyncio
    async def test_user_calibration_workflow(self):
        """Test flujo de calibración de usuario"""
        service = BrainComputerInterfaceService()
        user_id = "test_user_integration"

        # Calibrar usuario
        calibration_result = await service.calibrate_user_session(
            user_id,
            BCIModalityType.MOTOR_IMAGERY,
            {
                'session_duration': 300,
                'trials': 40,
                'break_interval': 60
            }
        )

        assert calibration_result['status'] == 'calibrated'
        assert calibration_result['user_id'] == user_id
        assert 'performance_metrics' in calibration_result
        assert user_id in service.calibration_data

        # Verificar datos de calibración
        calibration_data = service.calibration_data[user_id]
        assert calibration_data.user_id == user_id
        assert calibration_data.modality == BCIModalityType.MOTOR_IMAGERY
        assert 'accuracy' in calibration_data.performance_metrics
        assert 'response_time_ms' in calibration_data.performance_metrics


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
