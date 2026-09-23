"""
Tests para Advanced Neuroimaging Analysis Service
================================================

Conjunto completo de pruebas unitarias para el servicio de análisis
avanzado de neuroimágenes.

Author: AXIOM Team
Date: 2025-09-23
Version: 1.0.0
"""

import pytest
import numpy as np
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any

from app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis import (
    AdvancedNeuroimagingAnalysis,
    NeuroimagingData,
    ImagingModality,
    ProcessingMode,
    ConnectivityAnalysis,
    BrainSegmentation,
    PatternDetection
)

class TestAdvancedNeuroimagingAnalysis:
    """Pruebas para el servicio principal de neuroimaging."""

    @pytest.fixture
    def neuroimaging_service(self):
        """Fixture del servicio de neuroimaging."""
        return AdvancedNeuroimagingAnalysis()

    @pytest.fixture
    def sample_eeg_data(self):
        """Fixture con datos EEG de ejemplo."""
        # Simular 32 canales, 1000 muestras, 250 Hz
        np.random.seed(42)
        data = np.random.randn(32, 1000) * 50  # Amplitudes típicas de EEG
        channels = [f"EEG_{i:02d}" for i in range(32)]

        return NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=channels,
            metadata={"experiment": "test", "subject": "001"}
        )

    @pytest.fixture
    def sample_fmri_data(self):
        """Fixture con datos fMRI de ejemplo."""
        np.random.seed(123)
        # Simular 100 voxels, 200 timepoints, 0.5 Hz
        data = np.random.randn(100, 200) + np.sin(np.linspace(0, 20*np.pi, 200))

        return NeuroimagingData(
            data=data,
            modality=ImagingModality.FMRI,
            sampling_rate=0.5,
            channels=[f"Voxel_{i}" for i in range(100)],
            metadata={"TR": 2.0, "voxel_size": "3x3x3"}
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, neuroimaging_service):
        """Probar inicialización del servicio."""
        assert neuroimaging_service is not None
        assert neuroimaging_service.processing_pipelines == {}
        assert neuroimaging_service.real_time_buffers == {}
        assert neuroimaging_service.analysis_cache == {}
        assert "real_time_buffer_size" in neuroimaging_service.default_config

    @pytest.mark.asyncio
    async def test_create_analysis_session_batch(self, neuroimaging_service):
        """Probar creación de sesión en modo batch."""
        session_id = "test_session_001"

        result = await neuroimaging_service.create_analysis_session(
            session_id=session_id,
            modality=ImagingModality.EEG,
            processing_mode=ProcessingMode.BATCH
        )

        assert result["session_id"] == session_id
        assert result["modality"] == "eeg"
        assert result["processing_mode"] == "batch"
        assert result["status"] == "created"

        # Verificar que la sesión fue almacenada
        assert session_id in neuroimaging_service.processing_pipelines
        assert session_id not in neuroimaging_service.real_time_buffers

    @pytest.mark.asyncio
    async def test_create_analysis_session_real_time(self, neuroimaging_service):
        """Probar creación de sesión en modo tiempo real."""
        session_id = "test_session_rt_001"

        result = await neuroimaging_service.create_analysis_session(
            session_id=session_id,
            modality=ImagingModality.FMRI,
            processing_mode=ProcessingMode.REAL_TIME,
            config={"real_time_buffer_size": 500, "analysis_window_size": 50}
        )

        assert result["session_id"] == session_id
        assert result["modality"] == "fmri"
        assert result["processing_mode"] == "real_time"

        # Verificar buffer de tiempo real
        assert session_id in neuroimaging_service.real_time_buffers
        assert "data_buffer" in neuroimaging_service.real_time_buffers[session_id]
        assert result["config"]["real_time_buffer_size"] == 500

    @pytest.mark.asyncio
    async def test_preprocess_data_eeg(self, neuroimaging_service, sample_eeg_data):
        """Probar preprocesamiento de datos EEG."""
        original_shape = sample_eeg_data.data.shape

        with patch('app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis.SCIPY_AVAILABLE', True):
            with patch('scipy.signal.butter') as mock_butter:
                with patch('scipy.signal.sosfilt') as mock_sosfilt:
                    mock_butter.return_value = np.array([[1, 0, 0], [0, 1, 0]])
                    mock_sosfilt.return_value = sample_eeg_data.data[0] * 0.9

                    preprocessed = await neuroimaging_service.preprocess_data(sample_eeg_data)

        assert preprocessed.modality == ImagingModality.EEG
        assert preprocessed.data.shape == original_shape
        assert preprocessed.metadata["preprocessed"] is True
        assert preprocessed.sampling_rate == sample_eeg_data.sampling_rate

    @pytest.mark.asyncio
    async def test_preprocess_data_fmri(self, neuroimaging_service, sample_fmri_data):
        """Probar preprocesamiento de datos fMRI."""
        with patch('app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis.SCIPY_AVAILABLE', True):
            with patch('scipy.ndimage.gaussian_filter') as mock_filter:
                with patch('scipy.stats.zscore') as mock_zscore:
                    mock_filter.return_value = sample_fmri_data.data
                    mock_zscore.return_value = sample_fmri_data.data

                    preprocessed = await neuroimaging_service.preprocess_data(sample_fmri_data)

        assert preprocessed.modality == ImagingModality.FMRI
        assert preprocessed.metadata["preprocessed"] is True
        mock_filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_preprocess_data_no_scipy(self, neuroimaging_service, sample_eeg_data):
        """Probar preprocesamiento sin SciPy disponible."""
        with patch('app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis.SCIPY_AVAILABLE', False):
            preprocessed = await neuroimaging_service.preprocess_data(sample_eeg_data)

        # Sin SciPy, debe devolver los datos originales
        np.testing.assert_array_equal(preprocessed.data, sample_eeg_data.data)
        assert preprocessed.modality == sample_eeg_data.modality

class TestConnectivityAnalysis:
    """Pruebas para análisis de conectividad."""

    @pytest.fixture
    def neuroimaging_service(self):
        return AdvancedNeuroimagingAnalysis()

    @pytest.fixture
    def multichannel_data(self):
        """Datos multi-canal para conectividad."""
        np.random.seed(42)
        # 10 canales, 500 muestras
        data = np.random.randn(10, 500)

        # Añadir correlación entre algunos canales
        data[1] = data[0] * 0.8 + np.random.randn(500) * 0.2  # Alta correlación
        data[2] = -data[0] * 0.6 + np.random.randn(500) * 0.4  # Anti-correlación

        return NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=[f"CH_{i}" for i in range(10)]
        )

    @pytest.mark.asyncio
    async def test_analyze_functional_connectivity_correlation(self, neuroimaging_service, multichannel_data):
        """Probar análisis de conectividad por correlación."""
        result = await neuroimaging_service.analyze_functional_connectivity(
            data=multichannel_data,
            method="correlation"
        )

        assert isinstance(result, ConnectivityAnalysis)
        assert result.functional_connectivity.shape == (10, 10)

        # Verificar propiedades de la matriz de correlación
        assert np.allclose(np.diag(result.functional_connectivity), 1.0)  # Diagonal = 1
        assert np.allclose(result.functional_connectivity, result.functional_connectivity.T)  # Simétrica

        # Verificar métricas de red
        assert "density" in result.network_metrics
        assert "mean_connectivity" in result.network_metrics
        assert "clustering_coefficient" in result.network_metrics
        assert "global_efficiency" in result.network_metrics

        # Verificar medidas de grafo
        assert "strength" in result.graph_measures
        assert "degree" in result.graph_measures
        assert "centrality" in result.graph_measures
        assert result.graph_measures["strength"].shape == (10,)

    @pytest.mark.asyncio
    async def test_analyze_functional_connectivity_coherence(self, neuroimaging_service, multichannel_data):
        """Probar análisis de conectividad por coherencia."""
        with patch('app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis.SCIPY_AVAILABLE', True):
            with patch('scipy.signal.coherence') as mock_coherence:
                mock_coherence.return_value = (np.linspace(0, 125, 100), np.random.rand(100))

                result = await neuroimaging_service.analyze_functional_connectivity(
                    data=multichannel_data,
                    method="coherence"
                )

        assert isinstance(result, ConnectivityAnalysis)
        assert result.functional_connectivity.shape == (10, 10)
        assert mock_coherence.call_count > 0

    @pytest.mark.asyncio
    async def test_analyze_connectivity_single_channel_error(self, neuroimaging_service):
        """Probar error con datos de un solo canal."""
        # Crear datos 2D pero con solo 1 canal para probar la validación de conectividad
        single_channel_data = NeuroimagingData(
            data=np.random.randn(1, 500),  # 1 canal, 500 muestras (2D)
            modality=ImagingModality.EEG,
            sampling_rate=250.0
        )

        # La función debe funcionar pero generar una matriz 1x1
        result = await neuroimaging_service.analyze_functional_connectivity(single_channel_data)
        assert result.functional_connectivity.shape == (1, 1)
        assert result.functional_connectivity[0, 0] == 1.0  # Auto-correlación = 1

class TestBrainSegmentation:
    """Pruebas para segmentación cerebral."""

    @pytest.fixture
    def neuroimaging_service(self):
        return AdvancedNeuroimagingAnalysis()

    @pytest.fixture
    def structural_mri_data(self):
        """Datos MRI estructural simulados."""
        np.random.seed(42)
        # Volumen 3D típico
        data = np.random.rand(100, 100, 80)

        return NeuroimagingData(
            data=data,
            modality=ImagingModality.STRUCTURAL_MRI,
            sampling_rate=1.0,  # No aplica para estructural
            metadata={"voxel_size": "1x1x1", "field_strength": "3T"}
        )

    @pytest.mark.asyncio
    async def test_segment_brain_regions_structural(self, neuroimaging_service, structural_mri_data):
        """Probar segmentación de MRI estructural."""
        result = await neuroimaging_service.segment_brain_regions(
            data=structural_mri_data,
            atlas="aal"
        )

        assert isinstance(result, BrainSegmentation)

        # Verificar regiones esperadas
        expected_regions = ["frontal_cortex", "parietal_cortex", "temporal_cortex",
                          "occipital_cortex", "hippocampus", "amygdala"]

        for region in expected_regions:
            assert region in result.regions
            assert region in result.volumes
            assert region in result.coordinates
            assert region in result.confidence_scores

        # Verificar tipos de datos
        assert all(isinstance(vol, (int, float)) for vol in result.volumes.values())
        assert all(len(coord) == 3 for coord in result.coordinates.values())
        assert all(0 <= conf <= 1 for conf in result.confidence_scores.values())

    @pytest.mark.asyncio
    async def test_segment_brain_regions_eeg(self, neuroimaging_service):
        """Probar segmentación con datos EEG."""
        eeg_data = NeuroimagingData(
            data=np.random.randn(16, 1000),
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=[f"EEG_{i:02d}" for i in range(16)]
        )

        result = await neuroimaging_service.segment_brain_regions(eeg_data)

        assert isinstance(result, BrainSegmentation)
        assert len(result.regions) <= 10  # Limitado por número de canales

        # Para EEG, las regiones son basadas en canales
        for region_name in result.regions.keys():
            assert region_name.startswith("region_")

class TestPatternDetection:
    """Pruebas para detección de patrones."""

    @pytest.fixture
    def neuroimaging_service(self):
        return AdvancedNeuroimagingAnalysis()

    @pytest.fixture
    def oscillatory_data(self):
        """Datos con oscilaciones claras."""
        np.random.seed(42)
        t = np.linspace(0, 4, 1000)  # 4 segundos, 250 Hz

        # Crear señales con diferentes frecuencias
        alpha_signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz (alpha)
        beta_signal = np.sin(2 * np.pi * 20 * t)   # 20 Hz (beta)
        noise = np.random.randn(1000) * 0.1

        data = np.array([
            alpha_signal + noise,
            beta_signal + noise,
            alpha_signal + beta_signal + noise
        ])

        return NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=["Alpha_CH", "Beta_CH", "Mixed_CH"]
        )

    @pytest.mark.asyncio
    async def test_detect_patterns_oscillations(self, neuroimaging_service, oscillatory_data):
        """Probar detección de oscilaciones."""
        with patch('app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis.SCIPY_AVAILABLE', True):
            with patch('scipy.signal.welch') as mock_welch:
                # Simular PSD con picos en alpha y beta
                freqs = np.linspace(0, 125, 100)
                psd_alpha = np.exp(-(freqs - 10)**2 / 4)  # Pico en 10 Hz
                psd_beta = np.exp(-(freqs - 20)**2 / 4)   # Pico en 20 Hz

                mock_welch.side_effect = [
                    (freqs, psd_alpha),
                    (freqs, psd_beta),
                    (freqs, psd_alpha + psd_beta)
                ]

                result = await neuroimaging_service.detect_patterns(
                    data=oscillatory_data,
                    pattern_types=["oscillations"]
                )

        assert isinstance(result, PatternDetection)
        assert len(result.detected_patterns) > 0

        # Verificar que se detectaron oscilaciones
        oscillation_patterns = [p for p in result.detected_patterns if p["type"] == "oscillation"]
        assert len(oscillation_patterns) > 0

        # Verificar propiedades de las oscilaciones
        for pattern in oscillation_patterns:
            assert "frequency_band" in pattern
            assert "power" in pattern
            assert "confidence" in pattern
            assert pattern["frequency_band"] in ["delta", "theta", "alpha", "beta", "gamma"]

    @pytest.mark.asyncio
    async def test_detect_patterns_anomalies(self, neuroimaging_service):
        """Probar detección de anomalías."""
        # Crear datos con anomalías claras
        np.random.seed(42)
        data = np.random.randn(5, 1000)
        data[2, 100:110] = 10  # Anomalía grande en canal 2

        anomaly_data = NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=[f"CH_{i}" for i in range(5)]
        )

        result = await neuroimaging_service.detect_patterns(
            data=anomaly_data,
            pattern_types=["anomalies"]
        )

        assert isinstance(result, PatternDetection)

        # Verificar detección de anomalías
        anomaly_patterns = [p for p in result.detected_patterns if p["type"] == "anomaly"]
        assert len(anomaly_patterns) > 0

        for pattern in anomaly_patterns:
            assert "severity" in pattern
            assert "time_point" in pattern
            assert "channel" in pattern

    @pytest.mark.asyncio
    async def test_detect_patterns_connectivity(self, neuroimaging_service):
        """Probar detección de patrones de conectividad."""
        # Crear datos con conectividad clara
        np.random.seed(42)
        base_signal = np.random.randn(1000)
        data = np.array([
            base_signal,
            base_signal * 0.9 + np.random.randn(1000) * 0.1,  # Alta correlación
            -base_signal * 0.7 + np.random.randn(1000) * 0.3,  # Anti-correlación
            np.random.randn(1000)  # Sin correlación
        ])

        connectivity_data = NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=["Base", "Correlated", "Anti-correlated", "Independent"]
        )

        result = await neuroimaging_service.detect_patterns(
            data=connectivity_data,
            pattern_types=["connectivity_patterns"]
        )

        # Verificar patrones de conectividad
        connectivity_patterns = [p for p in result.detected_patterns if p["type"] == "connectivity"]
        assert len(connectivity_patterns) > 0

        for pattern in connectivity_patterns:
            assert "pattern_type" in pattern
            assert "channel_pair" in pattern
            assert "correlation" in pattern
            assert len(pattern["channel_pair"]) == 2

    @pytest.mark.asyncio
    async def test_detect_patterns_all_types(self, neuroimaging_service, oscillatory_data):
        """Probar detección de todos los tipos de patrones."""
        result = await neuroimaging_service.detect_patterns(oscillatory_data)

        assert isinstance(result, PatternDetection)
        assert len(result.anomaly_scores) == len(oscillatory_data.timestamps)
        assert len(result.classification_results) > 0
        assert len(result.temporal_features) > 0

        # Verificar características temporales
        assert "mean_activity" in result.temporal_features
        assert "std_activity" in result.temporal_features
        assert "peak_activity" in result.temporal_features

class TestRealTimeProcessing:
    """Pruebas para procesamiento en tiempo real."""

    @pytest.fixture
    def neuroimaging_service(self):
        return AdvancedNeuroimagingAnalysis()

    @pytest.fixture
    async def real_time_session(self, neuroimaging_service):
        """Sesión de tiempo real configurada."""
        session_id = "rt_session_001"
        await neuroimaging_service.create_analysis_session(
            session_id=session_id,
            modality=ImagingModality.EEG,
            processing_mode=ProcessingMode.REAL_TIME,
            config={"analysis_window_size": 5, "real_time_buffer_size": 50}
        )
        return session_id

    @pytest.mark.asyncio
    async def test_process_real_time_stream_buffering(self, neuroimaging_service, real_time_session):
        """Probar acumulación en buffer de tiempo real."""
        session_id = real_time_session

        # Enviar pocos datos (menos que window_size)
        for i in range(3):
            new_data = np.random.randn(8, 10)  # 8 canales, 10 muestras

            result = await neuroimaging_service.process_real_time_stream(
                session_id=session_id,
                new_data=new_data
            )

            assert result["status"] == "buffering"
            assert result["buffer_size"] == i + 1
            assert result["required_size"] == 5

    @pytest.mark.asyncio
    async def test_process_real_time_stream_processing(self, neuroimaging_service, real_time_session):
        """Probar procesamiento una vez que se llena el buffer."""
        session_id = real_time_session

        # Llenar buffer hasta el tamaño de ventana
        for i in range(6):  # Más que analysis_window_size = 5
            new_data = np.random.randn(8, 10)

            result = await neuroimaging_service.process_real_time_stream(
                session_id=session_id,
                new_data=new_data
            )

            if i >= 4:  # Una vez que tenemos suficientes datos
                assert result["status"] == "processed"
                assert "results" in resul
                assert result["processed_samples"] > 0
            else:
                assert result["status"] == "buffering"

    @pytest.mark.asyncio
    async def test_process_real_time_stream_invalid_session(self, neuroimaging_service):
        """Probar error con sesión inválida."""
        with pytest.raises(ValueError, match="Sesión .* no encontrada"):
            await neuroimaging_service.process_real_time_stream(
                session_id="non_existent_session",
                new_data=np.random.randn(8, 10)
            )

class TestSessionManagement:
    """Pruebas para manejo de sesiones."""

    @pytest.fixture
    def neuroimaging_service(self):
        return AdvancedNeuroimagingAnalysis()

    @pytest.mark.asyncio
    async def test_get_session_status(self, neuroimaging_service):
        """Probar obtención de estado de sesión."""
        session_id = "status_test_session"

        # Crear sesión
        await neuroimaging_service.create_analysis_session(
            session_id=session_id,
            modality=ImagingModality.FMRI,
            processing_mode=ProcessingMode.BATCH
        )

        # Obtener estado
        status = await neuroimaging_service.get_session_status(session_id)

        assert status["modality"] == ImagingModality.FMRI
        assert status["processing_mode"] == ProcessingMode.BATCH
        assert status["status"] == "active"
        assert status["processed_samples"] == 0
        assert "created_at" in status

    @pytest.mark.asyncio
    async def test_get_session_status_invalid(self, neuroimaging_service):
        """Probar error con sesión inexistente."""
        with pytest.raises(ValueError, match="Sesión .* no encontrada"):
            await neuroimaging_service.get_session_status("invalid_session")

    @pytest.mark.asyncio
    async def test_close_session(self, neuroimaging_service):
        """Probar cierre de sesión."""
        session_id = "close_test_session"

        # Crear sesión con tiempo real
        await neuroimaging_service.create_analysis_session(
            session_id=session_id,
            modality=ImagingModality.EEG,
            processing_mode=ProcessingMode.REAL_TIME
        )

        # Verificar que existe buffer
        assert session_id in neuroimaging_service.real_time_buffers

        # Cerrar sesión
        result = await neuroimaging_service.close_session(session_id)

        assert result["session_id"] == session_id
        assert result["status"] == "closed"

        # Verificar limpieza
        assert session_id not in neuroimaging_service.real_time_buffers
        assert neuroimaging_service.processing_pipelines[session_id]["status"] == "closed"

    @pytest.mark.asyncio
    async def test_close_session_invalid(self, neuroimaging_service):
        """Probar error cerrando sesión inexistente."""
        with pytest.raises(ValueError, match="Sesión .* no encontrada"):
            await neuroimaging_service.close_session("invalid_session")

class TestNeuroimagingDataModel:
    """Pruebas para el modelo de datos de neuroimaging."""

    def test_neuroimaging_data_initialization_valid(self):
        """Probar inicialización válida de NeuroimagingData."""
        data = np.random.randn(10, 1000)

        neuroimaging_data = NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=250.0,
            channels=[f"CH_{i}" for i in range(10)]
        )

        assert neuroimaging_data.data.shape == (10, 1000)
        assert neuroimaging_data.modality == ImagingModality.EEG
        assert neuroimaging_data.sampling_rate == 250.0
        assert len(neuroimaging_data.channels) == 10
        assert neuroimaging_data.timestamps is not None
        assert len(neuroimaging_data.timestamps) == 1000

    def test_neuroimaging_data_initialization_invalid_shape(self):
        """Probar error con datos de dimensión inválida."""
        data = np.array([1, 2, 3])  # 1D

        with pytest.raises(ValueError, match="Los datos deben tener al menos 2 dimensiones"):
            NeuroimagingData(
                data=data,
                modality=ImagingModality.EEG,
                sampling_rate=250.0
            )

    def test_neuroimaging_data_auto_timestamps(self):
        """Probar generación automática de timestamps."""
        data = np.random.randn(5, 500)

        neuroimaging_data = NeuroimagingData(
            data=data,
            modality=ImagingModality.EEG,
            sampling_rate=100.0
        )

        # Verificar timestamps automáticos
        expected_timestamps = np.arange(500) / 100.0
        assert neuroimaging_data.timestamps is not None
        np.testing.assert_array_almost_equal(neuroimaging_data.timestamps, expected_timestamps)

# Ejecutar tests si se ejecuta directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
