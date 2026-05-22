"""
Advanced Neuroimaging Analysis Service
=====================================

Servicio de análisis avanzado de neuroimágenes con capacidades de procesamiento en tiempo real.
Incluye análisis de fMRI, EEG, MEG, DTI, conectividad funcional y estructural.

Author: AXIOM Team
Date: 2025-09-23
Version: 1.0.0
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Simulaciones de librerías de neuroimaging (en producción usar nibabel, nipy, etc.)
try:
    import scipy.signal
    import scipy.ndimage
    from scipy.stats import zscore
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImagingModality(Enum):
    """Modalidades de neuroimaging soportadas."""
    FMRI = "fmri"
    EEG = "eeg"
    MEG = "meg"
    DTI = "dti"
    PET = "pet"
    SPECT = "spect"
    STRUCTURAL_MRI = "structural_mri"

class ProcessingMode(Enum):
    """Modos de procesamiento."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class NeuroimagingData:
    """Estructura de datos de neuroimaging."""
    data: np.ndarray
    modality: ImagingModality
    sampling_rate: float
    channels: List[str] = field(default_factory=list)
    timestamps: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validación post-inicialización."""
        if len(self.data.shape) < 2:
            raise ValueError("Los datos deben tener al menos 2 dimensiones")

        if self.timestamps is None:
            # Generar timestamps por defecto
            n_timepoints = self.data.shape[-1] if len(self.data.shape) > 1 else len(self.data)
            self.timestamps = np.arange(n_timepoints) / self.sampling_rate

@dataclass
class ConnectivityAnalysis:
    """Resultados de análisis de conectividad."""
    functional_connectivity: np.ndarray
    structural_connectivity: Optional[np.ndarray] = None
    network_metrics: Dict[str, float] = field(default_factory=dict)
    graph_measures: Dict[str, np.ndarray] = field(default_factory=dict)
    community_structure: Optional[np.ndarray] = None

@dataclass
class BrainSegmentation:
    """Resultados de segmentación cerebral."""
    regions: Dict[str, np.ndarray]
    volumes: Dict[str, float]
    coordinates: Dict[str, Tuple[float, float, float]]
    confidence_scores: Dict[str, float]

@dataclass
class PatternDetection:
    """Resultados de detección de patrones."""
    detected_patterns: List[Dict[str, Any]]
    anomaly_scores: np.ndarray
    classification_results: Dict[str, float]
    temporal_features: Dict[str, np.ndarray]

class AdvancedNeuroimagingAnalysis:
    """
    Servicio de análisis avanzado de neuroimágenes con procesamiento en tiempo real.
    """

    def __init__(self):
        """Inicializar el servicio de neuroimaging."""
        self.logger = logging.getLogger(__name__)
        self.processing_pipelines = {}
        self.real_time_buffers = {}
        self.analysis_cache = {}

        # Configuración por defecto
        self.default_config = {
            "real_time_buffer_size": 1000,
            "analysis_window_size": 100,
            "connectivity_threshold": 0.3,
            "artifact_threshold": 3.0,
            "preprocessing_enabled": True
        }

        self.logger.info("✅ AdvancedNeuroimagingAnalysis inicializado")

    async def create_analysis_session(
        self,
        session_id: str,
        modality: ImagingModality,
        processing_mode: ProcessingMode = ProcessingMode.BATCH,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crear una nueva sesión de análisis.

        Args:
            session_id: Identificador único de la sesión
            modality: Modalidad de neuroimaging
            processing_mode: Modo de procesamiento
            config: Configuración específica

        Returns:
            Información de la sesión creada
        """
        session_config = self.default_config.copy()
        if config:
            session_config.update(config)

        self.processing_pipelines[session_id] = {
            "modality": modality,
            "processing_mode": processing_mode,
            "config": session_config,
            "created_at": datetime.now(),
            "status": "active",
            "processed_samples": 0
        }

        if processing_mode == ProcessingMode.REAL_TIME:
            self.real_time_buffers[session_id] = {
                "data_buffer": [],
                "analysis_results": [],
                "last_analysis": None
            }

        self.logger.info("📊 Sesión de análisis creada: %s (%s)", session_id, modality.value)
        return {
            "session_id": session_id,
            "modality": modality.value,
            "processing_mode": processing_mode.value,
            "status": "created",
            "config": session_config
        }

    async def preprocess_data(
        self,
        data: NeuroimagingData,
        session_id: Optional[str] = None
    ) -> NeuroimagingData:
        """
        Preprocesar datos de neuroimaging.

        Args:
            data: Datos de neuroimaging
            session_id: ID de sesión (opcional)

        Returns:
            Datos preprocesados
        """
        if not SCIPY_AVAILABLE:
            self.logger.warning("⚠️ SciPy no disponible - usando preprocesamiento básico")
            return data

        processed_data = data.data.copy()

        # Filtrado de artefactos básico
        if data.modality in [ImagingModality.EEG, ImagingModality.MEG]:
            # Filtro pasa-banda para EEG/MEG
            if len(processed_data.shape) >= 2:
                for i in range(processed_data.shape[0]):
                    # Filtro básico usando scipy
                    sos = scipy.signal.butter(4, [1, 40], btype='band',
                                            fs=data.sampling_rate, output='sos')
                    processed_data[i] = scipy.signal.sosfilt(sos, processed_data[i])

        elif data.modality == ImagingModality.FMRI:
            # Suavizado para fMRI (temporal o espacial)
            if len(processed_data.shape) >= 2:
                processed_data = scipy.ndimage.gaussian_filter(processed_data, sigma=1.0)

        # Normalización z-score
        processed_data = zscore(processed_data, axis=-1, nan_policy='omit')

        # Crear nueva instancia con datos procesados
        preprocessed = NeuroimagingData(
            data=processed_data,
            modality=data.modality,
            sampling_rate=data.sampling_rate,
            channels=data.channels,
            timestamps=data.timestamps,
            metadata={**data.metadata, "preprocessed": True}
        )

        self.logger.info("🔧 Datos preprocesados: %s", data.modality.value)
        return preprocessed

    async def analyze_functional_connectivity(
        self,
        data: NeuroimagingData,
        method: str = "correlation"
    ) -> ConnectivityAnalysis:
        """
        Analizar conectividad funcional.

        Args:
            data: Datos de neuroimaging
            method: Método de análisis ('correlation', 'coherence', 'mutual_info')

        Returns:
            Resultados de análisis de conectividad
        """
        if len(data.data.shape) < 2:
            raise ValueError("Se requieren datos multi-canal para análisis de conectividad")

        # Matriz de conectividad funcional
        if method == "correlation":
            # Correlación de Pearson entre canales/regiones
            connectivity_matrix = np.corrcoef(data.data)
            # Asegurar que sea al menos una matriz 2D
            if connectivity_matrix.ndim == 0:
                connectivity_matrix = np.array([[1.0]])
            elif connectivity_matrix.ndim == 1:
                connectivity_matrix = connectivity_matrix.reshape(1, -1)
        elif method == "coherence" and SCIPY_AVAILABLE:
            # Coherencia espectral (simplificado)
            n_channels = data.data.shape[0]
            connectivity_matrix = np.zeros((n_channels, n_channels))

            for i in range(n_channels):
                for j in range(i, n_channels):
                    _, coherence = scipy.signal.coherence(
                        data.data[i], data.data[j],
                        fs=data.sampling_rate, nperseg=min(256, len(data.data[i])//4)
                    )
                    # Promedio de coherencia en bandas de interés
                    connectivity_matrix[i, j] = np.mean(coherence)
                    connectivity_matrix[j, i] = connectivity_matrix[i, j]
        else:
            # Fallback a correlación
            connectivity_matrix = np.corrcoef(data.data)

        # Métricas de red
        network_metrics = self._calculate_network_metrics(connectivity_matrix)

        # Medidas de grafos
        graph_measures = self._calculate_graph_measures(connectivity_matrix)

        result = ConnectivityAnalysis(
            functional_connectivity=connectivity_matrix,
            network_metrics=network_metrics,
            graph_measures=graph_measures
        )

        self.logger.info("🔗 Análisis de conectividad completado: %s", method)
        return result

    def _calculate_network_metrics(self, connectivity_matrix: np.ndarray) -> Dict[str, float]:
        """Calcular métricas básicas de red."""
        if len(connectivity_matrix.shape) != 2:
            return {"density": 0.0, "mean_connectivity": 0.0, "max_connectivity": 0.0,
                   "clustering_coefficient": 0.0, "global_efficiency": 0.0}

        n_nodes = connectivity_matrix.shape[0]
        if n_nodes < 2:
            return {"density": 1.0 if n_nodes == 1 else 0.0, "mean_connectivity": 0.0,
                   "max_connectivity": 0.0, "clustering_coefficient": 0.0, "global_efficiency": 0.0}

        # Umbralizar matriz
        thresholded = connectivity_matrix > self.default_config["connectivity_threshold"]

        # Crear máscara para excluir diagonal
        mask = ~np.eye(n_nodes, dtype=bool)

        return {
            "density": np.sum(thresholded[mask]) / np.sum(mask) if np.sum(mask) > 0 else 0.0,
            "mean_connectivity": np.mean(connectivity_matrix[mask]) if np.sum(mask) > 0 else 0.0,
            "max_connectivity": np.max(connectivity_matrix[mask]) if np.sum(mask) > 0 else 0.0,
            "clustering_coefficient": self._clustering_coefficient(thresholded),
            "global_efficiency": self._global_efficiency(connectivity_matrix)
        }

    def _calculate_graph_measures(self, connectivity_matrix: np.ndarray) -> Dict[str, np.ndarray]:
        """Calcular medidas de grafo."""
        if len(connectivity_matrix.shape) != 2:
            return {"strength": np.array([]), "degree": np.array([]), "centrality": np.array([])}

        n_nodes = connectivity_matrix.shape[0]

        if n_nodes == 0:
            return {"strength": np.array([]), "degree": np.array([]), "centrality": np.array([])}

        # Strength (suma de conexiones)
        strength = np.sum(np.abs(connectivity_matrix), axis=1) - np.diag(connectivity_matrix)

        # Degree (número de conexiones significativas)
        threshold = self.default_config["connectivity_threshold"]
        degree = np.sum(np.abs(connectivity_matrix) > threshold, axis=1) - 1

        # Centralidad simple (basada en strength)
        max_strength = np.max(strength)
        centrality = strength / max_strength if max_strength > 0 else np.zeros(n_nodes)

        return {
            "strength": strength,
            "degree": degree,
            "centrality": centrality
        }

    def _clustering_coefficient(self, adjacency_matrix: np.ndarray) -> float:
        """Calcular coeficiente de clustering promedio."""
        n = adjacency_matrix.shape[0]
        clustering_coeffs = []

        for i in range(n):
            neighbors = np.where(adjacency_matrix[i, :])[0]
            k = len(neighbors)

            if k < 2:
                clustering_coeffs.append(0.0)
                continue

            # Contar triángulos
            triangles = 0
            for j in range(len(neighbors)):
                for m in range(j + 1, len(neighbors)):
                    if adjacency_matrix[neighbors[j], neighbors[m]]:
                        triangles += 1

            clustering_coeffs.append(2.0 * triangles / (k * (k - 1)))

        return np.mean(clustering_coeffs)

    def _global_efficiency(self, connectivity_matrix: np.ndarray) -> float:
        """Calcular eficiencia global simplificada."""
        # Usar conectividad inversa como distancia aproximada
        distances = 1.0 / (np.abs(connectivity_matrix) + 1e-6)
        np.fill_diagonal(distances, 0)

        n = distances.shape[0]
        efficiency_sum = 0.0

        for i in range(n):
            for j in range(i + 1, n):
                if distances[i, j] > 0:
                    efficiency_sum += 1.0 / distances[i, j]

        return 2.0 * efficiency_sum / (n * (n - 1))

    async def segment_brain_regions(
        self,
        data: NeuroimagingData,
        atlas: str = "aal"
    ) -> BrainSegmentation:
        """
        Segmentar regiones cerebrales.

        Args:
            data: Datos de neuroimaging
            atlas: Atlas cerebral a usar

        Returns:
            Resultados de segmentación
        """
        # Simulación de segmentación cerebral
        if data.modality == ImagingModality.STRUCTURAL_MRI:
            # Simular segmentación automática
            regions = {
                "frontal_cortex": np.random.rand(100, 100, 50),
                "parietal_cortex": np.random.rand(80, 90, 45),
                "temporal_cortex": np.random.rand(90, 85, 40),
                "occipital_cortex": np.random.rand(70, 75, 35),
                "hippocampus": np.random.rand(30, 25, 20),
                "amygdala": np.random.rand(20, 15, 10)
            }

            volumes = {region: np.sum(mask) for region, mask in regions.items()}

            # Coordenadas de centro de masa simuladas
            coordinates = {
                "frontal_cortex": (45.0, 120.0, 60.0),
                "parietal_cortex": (65.0, 85.0, 75.0),
                "temporal_cortex": (25.0, 45.0, 35.0),
                "occipital_cortex": (85.0, 25.0, 45.0),
                "hippocampus": (35.0, 65.0, 25.0),
                "amygdala": (28.0, 55.0, 18.0)
            }

            confidence_scores = {region: np.random.uniform(0.8, 0.95) for region in regions.keys()}

        else:
            # Para otras modalidades, usar regiones basadas en canales
            n_channels = len(data.channels) if data.channels else data.data.shape[0]
            regions = {f"region_{i}": data.data[i] for i in range(min(n_channels, 10))}
            volumes = {region: float(np.sum(np.abs(signal))) for region, signal in regions.items()}
            coordinates = {region: (float(i*10), float(i*5), float(i*2)) for i, region in enumerate(regions.keys())}
            confidence_scores = {region: np.random.uniform(0.7, 0.9) for region in regions.keys()}

        result = BrainSegmentation(
            regions=regions,
            volumes=volumes,
            coordinates=coordinates,
            confidence_scores=confidence_scores
        )

        self.logger.info("🧠 Segmentación completada: %s regiones identificadas", len(regions))
        return result

    async def detect_patterns(
        self,
        data: NeuroimagingData,
        pattern_types: List[str] = None
    ) -> PatternDetection:
        """
        Detectar patrones en datos de neuroimaging.

        Args:
            data: Datos de neuroimaging
            pattern_types: Tipos de patrones a detectar

        Returns:
            Resultados de detección de patrones
        """
        if pattern_types is None:
            pattern_types = ["oscillations", "anomalies", "connectivity_patterns"]

        detected_patterns = []

        # Detección de oscilaciones
        if "oscillations" in pattern_types:
            oscillation_patterns = self._detect_oscillations(data)
            detected_patterns.extend(oscillation_patterns)

        # Detección de anomalías
        if "anomalies" in pattern_types:
            anomaly_patterns = self._detect_anomalies(data)
            detected_patterns.extend(anomaly_patterns)

        # Patrones de conectividad
        if "connectivity_patterns" in pattern_types:
            connectivity_patterns = self._detect_connectivity_patterns(data)
            detected_patterns.extend(connectivity_patterns)

        # Scores de anomalía globales
        anomaly_scores = np.abs(zscore(np.mean(data.data, axis=0), nan_policy='omit'))

        # Clasificación de estados cerebrales simulada
        classification_results = {
            "rest_state": np.random.uniform(0.3, 0.7),
            "active_state": np.random.uniform(0.2, 0.6),
            "pathological": np.random.uniform(0.0, 0.3)
        }

        # Features temporales
        temporal_features = self._extract_temporal_features(data)

        result = PatternDetection(
            detected_patterns=detected_patterns,
            anomaly_scores=anomaly_scores,
            classification_results=classification_results,
            temporal_features=temporal_features
        )

        self.logger.info("🔍 Detección de patrones completada: %s patrones encontrados", len(detected_patterns))
        return result

    def _detect_oscillations(self, data: NeuroimagingData) -> List[Dict[str, Any]]:
        """Detectar oscilaciones cerebrales."""
        patterns = []

        if not SCIPY_AVAILABLE:
            # Fallback simple
            return [{
                "type": "oscillation",
                "frequency_band": "alpha",
                "power": float(np.mean(np.abs(data.data))),
                "channels": data.channels[:5] if data.channels else ["simulated"],
                "confidence": 0.7
            }]

        # Análisis espectral por canal
        for i in range(min(data.data.shape[0], 5)):  # Limitar a 5 canales
            freqs, psd = scipy.signal.welch(
                data.data[i],
                fs=data.sampling_rate,
                nperseg=min(256, len(data.data[i])//4)
            )

            # Bandas de frecuencia estándar
            bands = {
                "delta": (1, 4),
                "theta": (4, 8),
                "alpha": (8, 13),
                "beta": (13, 30),
                "gamma": (30, 100)
            }

            for band_name, (low, high) in bands.items():
                band_mask = (freqs >= low) & (freqs <= high)
                if np.any(band_mask):
                    band_power = np.mean(psd[band_mask])

                    if band_power > np.percentile(psd, 75):  # Umbral simple
                        patterns.append({
                            "type": "oscillation",
                            "frequency_band": band_name,
                            "frequency_range": [low, high],
                            "power": float(band_power),
                            "channel": data.channels[i] if data.channels and i < len(data.channels) else f"channel_{i}",
                            "confidence": min(0.9, band_power / np.max(psd))
                        })

        return patterns

    def _detect_anomalies(self, data: NeuroimagingData) -> List[Dict[str, Any]]:
        """Detectar anomalías en los datos."""
        patterns = []

        # Detección simple basada en z-score
        z_scores = np.abs(zscore(data.data, axis=-1, nan_policy='omit'))
        threshold = self.default_config["artifact_threshold"]

        anomaly_indices = np.where(z_scores > threshold)

        for i in range(min(len(anomaly_indices[0]), 10)):  # Limitar a 10 anomalías
            channel_idx = anomaly_indices[0][i] if len(anomaly_indices) > 0 else 0
            time_idx = anomaly_indices[1][i] if len(anomaly_indices) > 1 else 0

            patterns.append({
                "type": "anomaly",
                "anomaly_type": "artifact",
                "channel": data.channels[channel_idx] if data.channels and channel_idx < len(data.channels) else f"channel_{channel_idx}",
                "time_point": float(time_idx / data.sampling_rate),
                "severity": float(z_scores[channel_idx, time_idx]) if len(z_scores.shape) > 1 else float(z_scores[channel_idx]),
                "confidence": 0.8
            })

        return patterns

    def _detect_connectivity_patterns(self, data: NeuroimagingData) -> List[Dict[str, Any]]:
        """Detectar patrones de conectividad."""
        patterns = []

        if data.data.shape[0] < 2:
            return patterns

        # Conectividad básica entre pares de canales
        for i in range(min(data.data.shape[0], 5)):
            for j in range(i + 1, min(data.data.shape[0], 5)):
                correlation = np.corrcoef(data.data[i], data.data[j])[0, 1]

                if abs(correlation) > self.default_config["connectivity_threshold"]:
                    patterns.append({
                        "type": "connectivity",
                        "pattern_type": "high_correlation" if correlation > 0 else "anti_correlation",
                        "channel_pair": [
                            data.channels[i] if data.channels and i < len(data.channels) else f"channel_{i}",
                            data.channels[j] if data.channels and j < len(data.channels) else f"channel_{j}"
                        ],
                        "correlation": float(correlation),
                        "confidence": min(0.9, abs(correlation))
                    })

        return patterns

    def _extract_temporal_features(self, data: NeuroimagingData) -> Dict[str, np.ndarray]:
        """Extraer características temporales."""
        features = {}

        # Características básicas por canal
        features["mean_activity"] = np.mean(data.data, axis=-1)
        features["std_activity"] = np.std(data.data, axis=-1)
        features["peak_activity"] = np.max(np.abs(data.data), axis=-1)

        # Características temporales
        if len(data.data.shape) > 1:
            features["temporal_variance"] = np.var(data.data, axis=-1)
            features["temporal_skewness"] = np.array([
                float(np.mean((channel - np.mean(channel))**3) / (np.std(channel)**3))
                for channel in data.data
            ])

        return features

    async def process_real_time_stream(
        self,
        session_id: str,
        new_data: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Procesar datos en tiempo real.

        Args:
            session_id: ID de la sesión
            new_data: Nuevos datos a procesar
            timestamps: Timestamps de los datos

        Returns:
            Resultados del análisis en tiempo real
        """
        if session_id not in self.real_time_buffers:
            raise ValueError(f"Sesión {session_id} no encontrada")

        buffer = self.real_time_buffers[session_id]
        config = self.processing_pipelines[session_id]["config"]

        # Agregar datos al buffer
        buffer["data_buffer"].append(new_data)

        # Mantener tamaño del buffer
        max_buffer_size = config["real_time_buffer_size"]
        if len(buffer["data_buffer"]) > max_buffer_size:
            buffer["data_buffer"] = buffer["data_buffer"][-max_buffer_size:]

        # Procesar si tenemos suficientes datos
        window_size = config["analysis_window_size"]
        if len(buffer["data_buffer"]) >= window_size:
            # Combinar datos del buffer
            combined_data = np.concatenate(buffer["data_buffer"][-window_size:], axis=-1)

            # Crear objeto de datos
            modality = self.processing_pipelines[session_id]["modality"]
            sampling_rate = 250.0  # Valor por defecto

            neuroimaging_data = NeuroimagingData(
                data=combined_data,
                modality=modality,
                sampling_rate=sampling_rate,
                timestamps=timestamps
            )

            # Análisis rápido en tiempo real
            results = await self._quick_real_time_analysis(neuroimaging_data)

            buffer["analysis_results"].append(results)
            buffer["last_analysis"] = results

            # Mantener historial limitado
            if len(buffer["analysis_results"]) > 100:
                buffer["analysis_results"] = buffer["analysis_results"][-100:]

            self.processing_pipelines[session_id]["processed_samples"] += 1

            return {
                "session_id": session_id,
                "status": "processed",
                "results": results,
                "buffer_size": len(buffer["data_buffer"]),
                "processed_samples": self.processing_pipelines[session_id]["processed_samples"]
            }

        return {
            "session_id": session_id,
            "status": "buffering",
            "buffer_size": len(buffer["data_buffer"]),
            "required_size": window_size
        }

    async def _quick_real_time_analysis(self, data: NeuroimagingData) -> Dict[str, Any]:
        """Análisis rápido para procesamiento en tiempo real."""
        # Análisis básico optimizado para velocidad
        results = {
            "timestamp": datetime.now().isoformat(),
            "mean_amplitude": float(np.mean(np.abs(data.data))),
            "peak_amplitude": float(np.max(np.abs(data.data))),
            "activity_level": "normal"  # Clasificación simple
        }

        # Detección simple de anomalías
        z_score = np.abs(zscore(np.mean(data.data, axis=0), nan_policy='omit'))
        max_z = np.max(z_score) if len(z_score) > 0 else 0

        if max_z > 3.0:
            results["activity_level"] = "high"
            results["anomaly_detected"] = True
        elif max_z < 0.5:
            results["activity_level"] = "low"

        results["max_z_score"] = float(max_z)

        return results

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Obtener el estado de una sesión."""
        if session_id not in self.processing_pipelines:
            raise ValueError(f"Sesión {session_id} no encontrada")

        session_info = self.processing_pipelines[session_id].copy()

        if session_id in self.real_time_buffers:
            buffer_info = self.real_time_buffers[session_id]
            session_info.update({
                "buffer_size": len(buffer_info["data_buffer"]),
                "analysis_count": len(buffer_info["analysis_results"]),
                "last_analysis": buffer_info["last_analysis"]
            })

        return session_info

    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Cerrar una sesión de análisis."""
        if session_id not in self.processing_pipelines:
            raise ValueError(f"Sesión {session_id} no encontrada")

        # Limpiar buffers
        if session_id in self.real_time_buffers:
            del self.real_time_buffers[session_id]

        # Marcar como cerrada
        self.processing_pipelines[session_id]["status"] = "closed"
        self.processing_pipelines[session_id]["closed_at"] = datetime.now()

        self.logger.info("📊 Sesión cerrada: %s", session_id)

        return {
            "session_id": session_id,
            "status": "closed",
            "processed_samples": self.processing_pipelines[session_id]["processed_samples"]
        }
