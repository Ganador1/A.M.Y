"""
BiomechanicsService - Servicio completo de análisis biomecánico
=============================================================

Implementación comprehensiva para análisis de movimiento, marcha, fuerzas,
y evaluación de riesgo de lesiones en el contexto médico.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from scipy import signal

from .biomechanics_types import (
    ActivityType, JointType, AnalysisType,
    MotionCaptureData, ForceData, EMGData, AnthropometricData,
    GaitAnalysisResult, JointKinematics, ForceAnalysis,
    MusculoskeletalModel, InjuryRiskAssessment,
    PerformanceMetrics, BiomechanicsAnalysisRequest, BiomechanicsAnalysisResult,
    NORMATIVE_GAIT_DATA, INJURY_RISK_THRESHOLDS, MUSCLE_GROUPS
)
from app.exceptions.domain.medicine import MedicalError


logger = logging.getLogger(__name__)


class BiomechanicsService:
    """
    Servicio comprehensivo de análisis biomecánico
    
    Capacidades principales:
    - Análisis de marcha y parámetros temporoespaciales
    - Cinemática y cinética articular
    - Análisis de fuerzas de reacción del suelo
    - Modelado musculoesquelético
    - Evaluación de riesgo de lesiones
    - Optimización del rendimiento deportivo
    - Procesamiento en tiempo real
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar BiomechanicsService
        
        Args:
            config: Configuración opcional del servicio
        """
        self.config = config or {}
        self.is_initialized = False
        
        # Configuraciones por defecto
        self.supported_activities = [activity.value for activity in ActivityType]
        self.supported_analysis_types = [analysis.value for analysis in AnalysisType]
        
        # Filtros y procesamiento
        self.default_lowpass_cutoff = 6.0  # Hz
        self.default_sampling_rate = 120  # Hz para motion capture
        self.force_plate_sampling_rate = 240  # Hz típico para placas de fuerza
        
        # Modelos y referencias
        self.normative_data = NORMATIVE_GAIT_DATA
        self.risk_thresholds = INJURY_RISK_THRESHOLDS
        self.muscle_groups = MUSCLE_GROUPS
        
        # Cache para análisis
        self._analysis_cache: Dict[str, Any] = {}
        self._model_cache: Dict[str, Any] = {}
        
        logger.info("BiomechanicsService inicializado")

    async def initialize(self) -> bool:
        """
        Inicializar el servicio de biomecánica
        
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            # Cargar modelos pre-entrenados (simulado)
            await self._load_movement_models()
            await self._load_injury_risk_models()
            await self._initialize_signal_processing()
            
            self.is_initialized = True
            logger.info("BiomechanicsService inicializado exitosamente")
            return True
            
        except MedicalError as e:
            logger.error(f"Error inicializando BiomechanicsService: {e}")
            return False

    async def analyze_comprehensive(
        self, 
        request: BiomechanicsAnalysisRequest
    ) -> BiomechanicsAnalysisResult:
        """
        Realizar análisis biomecánico comprehensivo
        
        Args:
            request: Solicitud de análisis
            
        Returns:
            BiomechanicsAnalysisResult: Resultados del análisis
        """
        start_time = datetime.now()
        
        try:
            # Validar datos de entrada
            self._validate_analysis_request(request)
            
            # Preprocesar datos
            processed_data = await self._preprocess_data(request)
            
            # Realizar análisis según el tipo
            result = BiomechanicsAnalysisResult(
                request=request,
                analysis_timestamp=start_time,
                processing_time_seconds=0.0
            )
            
            if request.analysis_type == AnalysisType.GAIT_ANALYSIS:
                result.gait_analysis = await self.analyze_gait(
                    processed_data.get("motion"), 
                    processed_data.get("force")
                )
                
            elif request.analysis_type == AnalysisType.JOINT_KINEMATICS:
                result.joint_kinematics = await self.analyze_joint_kinematics(
                    processed_data.get("motion")
                )
                
            elif request.analysis_type == AnalysisType.FORCE_ANALYSIS:
                result.force_analysis = await self.analyze_forces(
                    processed_data.get("force")
                )
                
            elif request.analysis_type == AnalysisType.INJURY_RISK:
                result.injury_risk = await self.assess_injury_risk(
                    processed_data.get("motion"),
                    processed_data.get("force"),
                    request.anthropometric_data
                )
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time_seconds = processing_time
            
            # Evaluación de calidad
            result.quality_assessment = await self._assess_data_quality(processed_data)
            
            return result
            
        except MedicalError as e:
            logger.error(f"Error en análisis comprehensivo: {e}")
            raise

    async def analyze_gait(
        self, 
        motion_data: MotionCaptureData,
        force_data: Optional[ForceData] = None,
        analysis_type: str = "comprehensive"
    ) -> GaitAnalysisResult:
        """
        Análisis comprehensivo de marcha
        
        Args:
            motion_data: Datos de captura de movimiento
            force_data: Datos de placa de fuerza (opcional)
            analysis_type: Tipo de análisis ("basic", "comprehensive")
            
        Returns:
            GaitAnalysisResult: Resultados del análisis de marcha
        """
        result = GaitAnalysisResult(subject_id=motion_data.subject_id)
        
        try:
            # Detección de eventos de marcha
            gait_events = await self._detect_gait_events(motion_data, force_data)
            
            # Análisis temporal
            result.temporal_parameters = await self._analyze_temporal_parameters(
                motion_data, gait_events
            )
            
            # Análisis espacial
            result.spatial_parameters = await self._analyze_spatial_parameters(
                motion_data, gait_events
            )
            
            # Ángulos articulares
            result.joint_angles = await self._calculate_joint_angles(motion_data)
            
            # Índices de asimetría
            result.asymmetry_indices = await self._calculate_asymmetry_indices(
                result.temporal_parameters, result.spatial_parameters
            )
            
            # Variabilidad
            result.variability_metrics = await self._calculate_gait_variability(
                motion_data, gait_events
            )
            
            logger.info(f"Análisis de marcha completado para {motion_data.subject_id}")
            return result
            
        except MedicalError as e:
            logger.error(f"Error en análisis de marcha: {e}")
            raise

    async def analyze_joint_kinematics(
        self,
        motion_data: MotionCaptureData,
        joints: Optional[List[str]] = None,
        smoothing_filter: bool = True
    ) -> Dict[str, JointKinematics]:
        """
        Análisis de cinemática articular
        
        Args:
            motion_data: Datos de movimiento
            joints: Lista de articulaciones a analizar
            smoothing_filter: Aplicar filtro de suavizado
            
        Returns:
            Dict[str, JointKinematics]: Resultados por articulación
        """
        if joints is None:
            joints = ["hip", "knee", "ankle"]
            
        results = {}
        
        for joint_name in joints:
            try:
                joint_type = JointType(joint_name)
                
                # Calcular ángulos articulares
                angles = await self._calculate_joint_angles_detailed(
                    motion_data, joint_type
                )
                
                if smoothing_filter:
                    angles = self._apply_smoothing_filter(angles)
                
                # Calcular velocidades y aceleraciones angulares
                angular_velocities = self._calculate_angular_derivatives(angles, 1)
                angular_accelerations = self._calculate_angular_derivatives(angles, 2)
                
                # Calcular rangos de movimiento
                range_of_motion = self._calculate_rom(angles)
                
                # Valores pico
                peak_values = self._find_peak_values(angles)
                
                results[joint_name] = JointKinematics(
                    joint=joint_type,
                    angles=angles,
                    angular_velocities=angular_velocities,
                    angular_accelerations=angular_accelerations,
                    range_of_motion=range_of_motion,
                    peak_values=peak_values
                )
                
            except MedicalError as e:
                logger.error(f"Error analizando cinemática de {joint_name}: {e}")
                continue
        
        return results

    async def analyze_forces(
        self,
        force_data: ForceData,
        analysis_type: str = "ground_reaction_forces"
    ) -> ForceAnalysis:
        """
        Análisis de fuerzas de reacción del suelo
        
        Args:
            force_data: Datos de placa de fuerza
            analysis_type: Tipo de análisis de fuerzas
            
        Returns:
            ForceAnalysis: Resultados del análisis
        """
        result = ForceAnalysis(subject_id=force_data.subject_mass_kg)
        
        try:
            # Análisis de fuerzas pico
            result.peak_forces = await self._analyze_peak_forces(force_data)
            
            # Tasas de carga
            result.loading_rates = await self._analyze_loading_rates(force_data)
            
            # Parámetros de impulso
            result.impulse_parameters = await self._analyze_impulse(force_data)
            
            # Métricas de centro de presión
            result.center_of_pressure_metrics = await self._analyze_cop(force_data)
            
            return result
            
        except MedicalError as e:
            logger.error(f"Error en análisis de fuerzas: {e}")
            raise

    async def create_musculoskeletal_model(
        self,
        motion_data: MotionCaptureData,
        anthropometric_data: AnthropometricData,
        muscle_activation_data: Optional[EMGData] = None
    ) -> MusculoskeletalModel:
        """
        Crear modelo musculoesquelético
        
        Args:
            motion_data: Datos de movimiento
            anthropometric_data: Datos antropométricos
            muscle_activation_data: Datos EMG (opcional)
            
        Returns:
            MusculoskeletalModel: Modelo musculoesquelético
        """
        model = MusculoskeletalModel(
            subject_id=motion_data.subject_id,
            anthropometrics=anthropometric_data
        )
        
        try:
            # Calcular fuerzas musculares usando optimización
            model.muscle_forces = await self._estimate_muscle_forces(
                motion_data, anthropometric_data, muscle_activation_data
            )
            
            # Calcular momentos articulares
            model.joint_moments = await self._calculate_joint_moments(
                motion_data, model.muscle_forces
            )
            
            # Calcular potencia articular
            model.joint_powers = await self._calculate_joint_powers(
                model.joint_moments, motion_data
            )
            
            # Activaciones musculares predichas
            if muscle_activation_data is None:
                model.muscle_activations = await self._predict_muscle_activations(
                    motion_data, model.muscle_forces
                )
            else:
                model.muscle_activations = self._process_emg_activations(
                    muscle_activation_data
                )
            
            return model
            
        except MedicalError as e:
            logger.error(f"Error creando modelo musculoesquelético: {e}")
            raise

    async def assess_injury_risk(
        self,
        motion_data: MotionCaptureData,
        force_data: Optional[ForceData] = None,
        athlete_profile: Optional[Dict[str, Any]] = None
    ) -> InjuryRiskAssessment:
        """
        Evaluación comprehensiva de riesgo de lesiones
        
        Args:
            motion_data: Datos de movimiento
            force_data: Datos de fuerza (opcional)
            athlete_profile: Perfil del atleta (opcional)
            
        Returns:
            InjuryRiskAssessment: Evaluación de riesgo
        """
        assessment = InjuryRiskAssessment(subject_id=motion_data.subject_id)
        
        try:
            # Análisis de factores de riesgo biomecánicos
            risk_factors = {}
            
            # Factor 1: Tasa de carga elevada
            if force_data:
                loading_rate = await self._calculate_loading_rate_risk(force_data)
                risk_factors["high_loading_rate"] = loading_rate
                
            # Factor 2: Asimetrías
            asymmetry_risk = await self._calculate_asymmetry_risk(motion_data)
            risk_factors["asymmetry_index"] = asymmetry_risk
            
            # Factor 3: Rigidez articular
            joint_stiffness_risk = await self._calculate_joint_stiffness_risk(motion_data)
            risk_factors["joint_stiffness"] = joint_stiffness_risk
            
            # Factor 4: Patrones de movimiento disfuncionales
            movement_pattern_risk = await self._analyze_movement_dysfunction(motion_data)
            risk_factors["movement_patterns"] = movement_pattern_risk
            
            assessment.risk_factors = risk_factors
            
            # Calcular puntuación general de riesgo
            assessment.overall_risk_score = await self._calculate_overall_risk_score(
                risk_factors, athlete_profile
            )
            
            # Generar recomendaciones
            assessment.recommendations = await self._generate_injury_prevention_recommendations(
                risk_factors, assessment.overall_risk_score
            )
            
            # Identificar áreas de preocupación
            assessment.concern_areas = await self._identify_concern_areas(risk_factors)
            
            return assessment
            
        except MedicalError as e:
            logger.error(f"Error en evaluación de riesgo: {e}")
            raise

    async def optimize_performance(
        self,
        motion_data: MotionCaptureData,
        performance_goals: List[str],
        sport_context: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        Optimización del rendimiento deportivo
        
        Args:
            motion_data: Datos de movimiento
            performance_goals: Objetivos de rendimiento
            sport_context: Contexto deportivo específico
            
        Returns:
            PerformanceMetrics: Métricas y recomendaciones
        """
        metrics = PerformanceMetrics(subject_id=motion_data.subject_id)
        
        try:
            # Análisis de eficiencia
            metrics.efficiency_metrics = await self._analyze_movement_efficiency(motion_data)
            
            # Puntuaciones de técnica
            metrics.technique_scores = await self._analyze_technique(
                motion_data, sport_context
            )
            
            # Métricas específicas del deporte
            if sport_context:
                metrics.sport_specific_metrics = await self._analyze_sport_specific_metrics(
                    motion_data, sport_context
                )
            
            # Identificar áreas de mejora
            metrics.improvement_areas = await self._identify_improvement_areas(
                metrics.efficiency_metrics, metrics.technique_scores, performance_goals
            )
            
            # Generar recomendaciones de entrenamiento
            metrics.training_recommendations = await self._generate_training_recommendations(
                metrics.improvement_areas, sport_context
            )
            
            return metrics
            
        except MedicalError as e:
            logger.error(f"Error en optimización de rendimiento: {e}")
            raise

    # Métodos de utilidad y preprocesamiento
    def apply_lowpass_filter(
        self, 
        data: np.ndarray, 
        cutoff_frequency: float, 
        sampling_rate: int
    ) -> np.ndarray:
        """Aplicar filtro pasa-bajas Butterworth"""
        nyquist = sampling_rate / 2
        normalized_cutoff = cutoff_frequency / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        
        if data.ndim == 1:
            return signal.filtfilt(b, a, data)
        else:
            # Aplicar filtro a cada columna
            filtered_data = np.zeros_like(data)
            for i in range(data.shape[1]):
                filtered_data[:, i] = signal.filtfilt(b, a, data[:, i])
            return filtered_data

    def detect_data_gaps(
        self, 
        data: Dict[str, np.ndarray], 
        threshold: float = 0.1
    ) -> Dict[str, List[Tuple[int, int]]]:
        """Detectar gaps en los datos"""
        gaps = {}
        
        for marker_name, marker_data in data.items():
            marker_gaps = []
            
            # Detectar valores NaN o fuera de rango
            invalid_mask = np.isnan(marker_data).any(axis=1) if marker_data.ndim > 1 else np.isnan(marker_data)
            
            # Encontrar secuencias continuas de datos inválidos
            gap_starts = np.where(np.diff(invalid_mask.astype(int)) == 1)[0] + 1
            gap_ends = np.where(np.diff(invalid_mask.astype(int)) == -1)[0] + 1
            
            # Manejar casos especiales
            if invalid_mask[0]:
                gap_starts = np.concatenate([[0], gap_starts])
            if invalid_mask[-1]:
                gap_ends = np.concatenate([gap_ends, [len(invalid_mask)]])
            
            for start, end in zip(gap_starts, gap_ends):
                marker_gaps.append((start, end))
            
            gaps[marker_name] = marker_gaps
        
        return gaps

    def interpolate_missing_data(
        self, 
        data: np.ndarray, 
        method: str = "cubic_spline"
    ) -> np.ndarray:
        """Interpolar datos faltantes"""
        if method == "cubic_spline":
            from scipy.interpolate import interp1d
            
            if data.ndim == 1:
                valid_indices = ~np.isnan(data)
                if np.sum(valid_indices) < 4:  # Necesitamos al menos 4 puntos para spline cúbico
                    method = "linear"
                else:
                    f = interp1d(
                        np.where(valid_indices)[0], 
                        data[valid_indices], 
                        kind='cubic', 
                        fill_value='extrapolate'
                    )
                    return f(np.arange(len(data)))
            else:
                # Interpolar cada columna por separado
                interpolated = np.copy(data)
                for col in range(data.shape[1]):
                    interpolated[:, col] = self.interpolate_missing_data(
                        data[:, col], method
                    )
                return interpolated
        
        # Fallback a interpolación lineal
        from scipy.interpolate import interp1d
        if data.ndim == 1:
            valid_indices = ~np.isnan(data)
            if np.sum(valid_indices) >= 2:
                f = interp1d(
                    np.where(valid_indices)[0], 
                    data[valid_indices], 
                    kind='linear', 
                    fill_value='extrapolate'
                )
                return f(np.arange(len(data)))
        
        return data

    async def process_real_time_frame(
        self,
        frame_data: Dict[str, Any],
        analysis_mode: str = "gait_phase_detection"
    ) -> Dict[str, Any]:
        """
        Procesar frame en tiempo real
        
        Args:
            frame_data: Datos del frame actual
            analysis_mode: Modo de análisis en tiempo real
            
        Returns:
            Dict: Resultados del procesamiento en tiempo real
        """
        try:
            result = {
                "frame_id": frame_data.get("timestamp", 0),
                "processing_timestamp": datetime.now().isoformat()
            }
            
            if analysis_mode == "gait_phase_detection":
                # Detección de fase de marcha en tiempo real
                markers = frame_data.get("markers", {})
                if "ankle" in markers:
                    ankle_height = markers["ankle"][2]  # Coordenada Z (vertical)
                    result["ankle_angle"] = await self._estimate_ankle_angle_realtime(markers)
                    result["ground_contact"] = ankle_height < 0.05  # Umbral de contacto
                    result["gait_phase"] = await self._classify_gait_phase_realtime(markers)
            
            elif analysis_mode == "balance_assessment":
                # Evaluación de balance en tiempo real
                cop_data = frame_data.get("center_of_pressure")
                if cop_data:
                    result["balance_score"] = await self._calculate_balance_score_realtime(cop_data)
                    result["stability_index"] = await self._calculate_stability_index(cop_data)
            
            return result
            
        except MedicalError as e:
            logger.error(f"Error procesando frame en tiempo real: {e}")
            return {"error": str(e), "frame_id": frame_data.get("timestamp", 0)}

    # Métodos internos para análisis específicos
    async def _load_movement_models(self):
        """Cargar modelos de reconocimiento de movimiento"""
        # Simulación de carga de modelos pre-entrenados
        self._model_cache["gait_classifier"] = "gait_model_v2.pkl"
        self._model_cache["joint_angle_estimator"] = "joint_angle_model.pkl"
        logger.info("Modelos de movimiento cargados")

    async def _load_injury_risk_models(self):
        """Cargar modelos de predicción de riesgo de lesiones"""
        self._model_cache["injury_risk_predictor"] = "injury_risk_model.pkl"
        self._model_cache["asymmetry_detector"] = "asymmetry_model.pkl"
        logger.info("Modelos de riesgo de lesiones cargados")

    async def _initialize_signal_processing(self):
        """Inicializar componentes de procesamiento de señales"""
        # Configurar filtros por defecto
        self.default_filters = {
            "lowpass_6hz": signal.butter(4, 6.0 / (self.default_sampling_rate / 2), 'low'),
            "lowpass_10hz": signal.butter(4, 10.0 / (self.default_sampling_rate / 2), 'low'),
            "bandpass_emg": signal.butter(4, [20, 450] / (1000 / 2), 'band')  # Para EMG
        }
        logger.info("Procesamiento de señales inicializado")

    def _validate_analysis_request(self, request: BiomechanicsAnalysisRequest):
        """Validar solicitud de análisis"""
        if request.analysis_type not in self.supported_analysis_types:
            raise ValueError(f"Tipo de análisis no soportado: {request.analysis_type}")
        
        if request.motion_data is None and request.force_data is None:
            raise ValueError("Se requieren datos de movimiento o fuerza")

    async def _preprocess_data(self, request: BiomechanicsAnalysisRequest) -> Dict[str, Any]:
        """Preprocesar datos de entrada"""
        processed = {}
        
        if request.motion_data:
            # Aplicar filtros si está habilitado
            if request.filtering_enabled:
                filtered_markers = {}
                for marker_name, marker_data in request.motion_data.markers.items():
                    filtered_markers[marker_name] = self.apply_lowpass_filter(
                        marker_data, 
                        request.cutoff_frequency,
                        request.motion_data.sampling_rate
                    )
                
                # Crear copia con datos filtrados
                filtered_motion = MotionCaptureData(
                    timestamp=request.motion_data.timestamp,
                    markers=filtered_markers,
                    sampling_rate=request.motion_data.sampling_rate,
                    subject_id=request.motion_data.subject_id,
                    activity=request.motion_data.activity,
                    duration_seconds=request.motion_data.duration_seconds
                )
                processed["motion"] = filtered_motion
            else:
                processed["motion"] = request.motion_data
        
        if request.force_data:
            processed["force"] = request.force_data
        
        if request.emg_data:
            processed["emg"] = request.emg_data
            
        return processed

    # Métodos placeholder para funcionalidades específicas
    async def _detect_gait_events(self, motion_data: MotionCaptureData, force_data: Optional[ForceData]):
        """Detectar eventos de marcha (heel strike, toe off)"""
        # Implementación simplificada
        events = {
            "heel_strikes": [0, 120, 240],  # Frames de heel strike
            "toe_offs": [60, 180, 300],     # Frames de toe off
            "stride_times": [1.0, 1.05, 0.98]  # Duraciones de stride en segundos
        }
        return events

    async def _analyze_temporal_parameters(self, motion_data: MotionCaptureData, gait_events: Dict):
        """Analizar parámetros temporales de marcha"""
        stride_times = gait_events["stride_times"]
        return {
            "stride_length_m": np.mean(stride_times) * 1.4,  # Estimación
            "cadence_steps_per_min": 60 / (np.mean(stride_times) / 2),
            "walking_speed_ms": 1.3,  # Estimación
            "stance_phase_percent": 62.0,
            "swing_phase_percent": 38.0,
            "double_support_percent": 12.0
        }

    async def _analyze_spatial_parameters(self, motion_data: MotionCaptureData, gait_events: Dict):
        """Analizar parámetros espaciales de marcha"""
        return {
            "step_width_m": 0.14,
            "foot_angle_degrees": 8.5,
            "pelvic_rotation_degrees": 4.2
        }

    async def _calculate_joint_angles(self, motion_data: MotionCaptureData):
        """Calcular ángulos articulares"""
        return {
            "hip_flexion_max": 35,
            "knee_flexion_max": 68,
            "ankle_dorsiflexion_max": 12,
            "ankle_plantarflexion_max": 20
        }

    async def _assess_data_quality(self, processed_data: Dict[str, Any]):
        """Evaluar calidad de los datos"""
        return {
            "data_completeness": 0.95,
            "signal_to_noise_ratio": 8.5,
            "marker_visibility": 0.92
        }

# Crear instancia global para compatibilidad
biomechanical_model = BiomechanicsService()
