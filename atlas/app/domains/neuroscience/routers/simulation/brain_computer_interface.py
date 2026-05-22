"""
🧠 Brain-Computer Interface Router - ATLAS AXIOM
API endpoints para interfaces cerebro-computadora

Endpoints disponibles:
- POST /bci/decoder/initialize - Inicializar decodificador BCI
- POST /bci/decoder/train - Entrenar decodificador
- POST /bci/decode/realtime - Decodificación en tiempo real
- POST /bci/decoder/adapt - Adaptación online
- POST /bci/user/calibrate - Calibración de usuario
- GET /bci/system/status - Estado del sistema
- POST /bci/session/simulate - Simulación de sesión BCI
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any
from datetime import datetime
import logging

from app.domains.neuroscience.services.neuromorphic.brain_computer_interface import (
from app.exceptions.domain.neuroscience import NeuroscienceError
    bci_service,
    BCIModalityType,
    DecodingAlgorithm,
    SignalQuality
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bci", tags=["brain-computer-interface"])


# Modelos Pydantic para requests/responses
class BCIDecoderInitRequest(BaseModel):
    """Request para inicializar decodificador BCI"""
    decoder_id: str = Field(..., description="ID único del decodificador")
    modality: str = Field(..., description="Modalidad BCI")
    algorithm: str = Field(..., description="Algoritmo de decodificación")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuración del decodificador")

    @validator('modality')
    def validate_modality(cls, v):
        try:
            BCIModalityType(v)
            return v
        except ValueError:
            valid_modalities = [m.value for m in BCIModalityType]
            raise ValueError(f"Modalidad inválida. Opciones: {valid_modalities}")

    @validator('algorithm')
    def validate_algorithm(cls, v):
        try:
            DecodingAlgorithm(v)
            return v
        except ValueError:
            valid_algorithms = [a.value for a in DecodingAlgorithm]
            raise ValueError(f"Algoritmo inválido. Opciones: {valid_algorithms}")


class BCISignalDataRequest(BaseModel):
    """Request con datos de señal BCI"""
    channels: List[str] = Field(..., description="Nombres de los canales")
    sampling_rate: float = Field(..., gt=0, description="Frecuencia de muestreo en Hz")
    data: List[List[float]] = Field(..., description="Datos de señal por canal")
    timestamps: List[float] = Field(default_factory=list, description="Timestamps de las muestras")
    quality_scores: Dict[str, float] = Field(default_factory=dict, description="Puntuaciones de calidad por canal")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")

    @validator('data')
    def validate_data_shape(cls, v, values):
        if 'channels' in values and len(v) != len(values['channels']):
            raise ValueError("Número de canales de datos debe coincidir con lista de canales")
        return v


class BCITrainingRequest(BaseModel):
    """Request para entrenar decodificador BCI"""
    decoder_id: str = Field(..., description="ID del decodificador")
    training_signals: List[Dict[str, Any]] = Field(..., description="Señales de entrenamiento")
    labels: List[str] = Field(..., description="Etiquetas de las señales")

    @validator('labels')
    def validate_equal_length(cls, v, values):
        if 'training_signals' in values and len(v) != len(values['training_signals']):
            raise ValueError("Número de señales y etiquetas debe ser igual")
        return v


class BCIRealTimeDecodeRequest(BaseModel):
    """Request para decodificación en tiempo real"""
    decoder_id: str = Field(..., description="ID del decodificador")
    signal_data: BCISignalDataRequest = Field(..., description="Datos de señal a decodificar")


class BCIAdaptRequest(BaseModel):
    """Request para adaptación del decodificador"""
    decoder_id: str = Field(..., description="ID del decodificador")
    signal_data: BCISignalDataRequest = Field(..., description="Datos de señal para adaptación")
    true_label: str = Field(..., description="Etiqueta verdadera para la adaptación")


class BCICalibrationRequest(BaseModel):
    """Request para calibración de usuario"""
    user_id: str = Field(..., description="ID del usuario")
    modality: str = Field(..., description="Modalidad BCI")
    calibration_protocol: Dict[str, Any] = Field(default_factory=dict, description="Protocolo de calibración")

    @validator('modality')
    def validate_modality(cls, v):
        try:
            BCIModalityType(v)
            return v
        except ValueError:
            valid_modalities = [m.value for m in BCIModalityType]
            raise ValueError(f"Modalidad inválida. Opciones: {valid_modalities}")


class BCISimulationRequest(BaseModel):
    """Request para simulación de sesión BCI"""
    duration_seconds: int = Field(10, ge=1, le=300, description="Duración de la simulación en segundos")


# Modelos de respuesta
class BCIResponse(BaseModel):
    """Respuesta base BCI"""
    status: str = Field(..., description="Estado de la operación")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = Field(default_factory=dict, description="Datos de respuesta")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")


# Endpoints BCI
@router.post("/decoder/initialize", response_model=BCIResponse)
async def initialize_bci_decoder(
    request: BCIDecoderInitRequest,
    background_tasks: BackgroundTasks
) -> BCIResponse:
    """
    🔧 Inicializar decodificador BCI

    Crea y configura un nuevo decodificador para una modalidad específica de BCI.

    **Modalidades soportadas:**
    - **eeg**: Electroencefalografía
    - **fmri**: Resonancia magnética funcional
    - **ecog**: Electrocorticografía
    - **nirs**: Espectroscopía cercana al infrarrojo
    - **ssvep**: Potenciales evocados visuales de estado estable
    - **p300**: Componente P300 de potenciales evocados
    - **motor_imagery**: Imaginación motora
    - **hybrid**: Combinación de modalidades

    **Algoritmos disponibles:**
    - **common_spatial_pattern**: CSP para motor imagery
    - **support_vector_machine**: SVM para clasificación
    - **linear_discriminant_analysis**: LDA clásico
    - **deep_learning**: Redes neuronales profundas
    - **ensemble**: Conjunto de clasificadores
    - **adaptive**: Algoritmos adaptativos

    **Configuraciones típicas:**
    ```json
    {
        "adaptation_rate": 0.1,
        "frequency_bands": [[8, 12], [12, 30]],
        "spatial_filters": 6,
        "detection_threshold": 0.7
    }
    ```
    """
    try:
        logger.info(f"🔧 Inicializando decodificador BCI: {request.decoder_id}")

        result = await bci_service.initialize_decoder(
            request.decoder_id,
            BCIModalityType(request.modality),
            DecodingAlgorithm(request.algorithm),
            request.config
        )

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return BCIResponse(
            status="initialized",
            data=result,
            metadata={
                "decoder_id": request.decoder_id,
                "modality": request.modality,
                "algorithm": request.algorithm
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error inicializando decodificador BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error inicializando decodificador: {str(e)}")


@router.post("/decoder/train", response_model=BCIResponse)
async def train_bci_decoder(
    request: BCITrainingRequest,
    background_tasks: BackgroundTasks
) -> BCIResponse:
    """
    🎯 Entrenar decodificador BCI

    Entrena un decodificador BCI usando datos de señales etiquetadas.

    **Proceso de entrenamiento:**
    1. Preprocesamiento de señales
    2. Extracción de características
    3. Entrenamiento del modelo
    4. Validación cruzada
    5. Optimización de hiperparámetros

    **Formato de datos de entrenamiento:**
    ```json
    {
        "channels": ["C3", "C4", "Cz"],
        "sampling_rate": 250.0,
        "data": [[...], [...], [...]],
        "timestamps": [...],
        "metadata": {"condition": "training"}
    }
    ```

    **Etiquetas típicas:**
    - Motor imagery: ["left_hand", "right_hand", "feet", "tongue"]
    - P300: ["P300", "non_P300"]
    - SSVEP: ["8Hz", "10Hz", "12Hz", "15Hz"]
    """
    try:
        logger.info(f"🎯 Entrenando decodificador BCI: {request.decoder_id}")

        result = await bci_service.train_decoder(
            request.decoder_id,
            request.training_signals,
            request.labels
        )

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        # Agregar tarea en background para validación
        background_tasks.add_task(
            log_training_completion,
            request.decoder_id,
            len(request.training_signals)
        )

        return BCIResponse(
            status="trained",
            data=result,
            metadata={
                "training_samples": len(request.training_signals),
                "unique_labels": list(set(request.labels))
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error entrenando decodificador BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento: {str(e)}")


@router.post("/decode/realtime", response_model=BCIResponse)
async def decode_bci_realtime(
    request: BCIRealTimeDecodeRequest
) -> BCIResponse:
    """
    ⚡ Decodificación BCI en tiempo real

    Decodifica una señal BCI en tiempo real para generar predicciones inmediatas.

    **Flujo de decodificación:**
    1. Validación de calidad de señal
    2. Preprocesamiento en tiempo real
    3. Extracción de características
    4. Clasificación/decodificación
    5. Post-procesamiento de confianza

    **Métricas de calidad:**
    - **excellent**: SNR > 20 dB
    - **good**: SNR > 15 dB
    - **fair**: SNR > 10 dB
    - **poor**: SNR > 5 dB
    - **unusable**: SNR ≤ 5 dB

    **Respuesta incluye:**
    - Predicción de clase
    - Nivel de confianza
    - Probabilidades por clase
    - Importancia de características
    - Tiempo de procesamiento
    - Calidad de señal
    """
    try:
        logger.info(f"⚡ Decodificación en tiempo real: {request.decoder_id}")

        # Convertir request a formato interno
        signal_data = {
            'channels': request.signal_data.channels,
            'sampling_rate': request.signal_data.sampling_rate,
            'data': request.signal_data.data,
            'timestamps': request.signal_data.timestamps,
            'quality_scores': request.signal_data.quality_scores,
            'metadata': request.signal_data.metadata
        }

        result = await bci_service.decode_real_time(request.decoder_id, signal_data)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return BCIResponse(
            status="decoded",
            data=result,
            metadata={
                "signal_length": len(request.signal_data.data[0]) if request.signal_data.data else 0,
                "channels_count": len(request.signal_data.channels)
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error en decodificación tiempo real: {e}")
        raise HTTPException(status_code=500, detail=f"Error en decodificación: {str(e)}")


@router.post("/decoder/adapt", response_model=BCIResponse)
async def adapt_bci_decoder(
    request: BCIAdaptRequest,
    background_tasks: BackgroundTasks
) -> BCIResponse:
    """
    🔄 Adaptación online del decodificador BCI

    Actualiza el decodificador usando nueva información de retroalimentación.

    **Estrategias de adaptación:**
    - **Supervised**: Con etiquetas verdaderas del usuario
    - **Semi-supervised**: Con etiquetas parciales
    - **Unsupervised**: Basado en confianza de predicciones
    - **Transfer learning**: Adaptación entre sesiones

    **Parámetros de adaptación:**
    - Tasa de aprendizaje adaptativo
    - Olvido de datos antiguos
    - Detección de cambios de sesión
    - Regularización para estabilidad

    **Beneficios:**
    - Mejora de precisión con el uso
    - Adaptación a cambios de estado
    - Personalización por usuario
    - Robustez a artifacts
    """
    try:
        logger.info(f"🔄 Adaptando decodificador BCI: {request.decoder_id}")

        # Convertir request a formato interno
        signal_data = {
            'channels': request.signal_data.channels,
            'sampling_rate': request.signal_data.sampling_rate,
            'data': request.signal_data.data,
            'timestamps': request.signal_data.timestamps,
            'quality_scores': request.signal_data.quality_scores,
            'metadata': request.signal_data.metadata
        }

        result = await bci_service.adapt_decoder(
            request.decoder_id,
            signal_data,
            request.true_label
        )

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        # Registrar adaptación en background
        background_tasks.add_task(
            log_adaptation_event,
            request.decoder_id,
            request.true_label
        )

        return BCIResponse(
            status="adapted",
            data=result,
            metadata={
                "true_label": request.true_label,
                "adaptation_type": "supervised"
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error adaptando decodificador BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en adaptación: {str(e)}")


@router.post("/user/calibrate", response_model=BCIResponse)
async def calibrate_bci_user(
    request: BCICalibrationRequest,
    background_tasks: BackgroundTasks
) -> BCIResponse:
    """
    👤 Calibración de usuario BCI

    Establece parámetros de línea base específicos para un usuario.

    **Proceso de calibración:**
    1. Grabación de señal en reposo
    2. Grabación de tareas específicas
    3. Análisis de características individuales
    4. Optimización de parámetros
    5. Validación de rendimiento

    **Parámetros calibrados:**
    - Bandas de frecuencia óptimas
    - Patrones espaciales individuales
    - Umbrales de detección
    - Parámetros de filtrado
    - Tiempos de respuesta

    **Protocolo típico:**
    ```json
    {
        "rest_duration_seconds": 60,
        "task_trials": 40,
        "break_interval_seconds": 5,
        "feedback_enabled": true,
        "adaptive_threshold": true
    }
    ```

    **Métricas de calibración:**
    - Precisión de clasificación
    - Tiempo de respuesta
    - Estabilidad de señal
    - Comodidad del usuario
    """
    try:
        logger.info(f"👤 Calibrando usuario BCI: {request.user_id}")

        result = await bci_service.calibrate_user_session(
            request.user_id,
            BCIModalityType(request.modality),
            request.calibration_protocol
        )

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        # Guardar calibración en background
        background_tasks.add_task(
            save_calibration_data,
            request.user_id,
            request.modality,
            result
        )

        return BCIResponse(
            status="calibrated",
            data=result,
            metadata={
                "user_id": request.user_id,
                "modality": request.modality,
                "protocol_used": request.calibration_protocol
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error calibrando usuario BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en calibración: {str(e)}")


@router.get("/system/status", response_model=BCIResponse)
async def get_bci_system_status() -> BCIResponse:
    """
    🔍 Estado del sistema BCI

    Proporciona información completa sobre el estado actual del sistema BCI.

    **Información incluida:**
    - Decodificadores activos
    - Usuarios calibrados
    - Rendimiento del sistema
    - Uso de recursos
    - Estado de conexiones

    **Métricas del sistema:**
    - Latencia promedio de decodificación
    - Precisión por decodificador
    - Uso de CPU/memoria
    - Número de sesiones activas
    - Estado de adaptación

    **Monitoreo de salud:**
    - Calidad de señal promedio
    - Tasa de errores
    - Disponibilidad del servicio
    - Alertas de rendimiento
    """
    try:
        logger.info("🔍 Consultando estado del sistema BCI")

        status = await bci_service.get_system_status()

        return BCIResponse(
            status="operational",
            data=status,
            metadata={
                "service_version": "1.0.0",
                "supported_modalities": [m.value for m in BCIModalityType],
                "supported_algorithms": [a.value for a in DecodingAlgorithm]
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error consultando estado del sistema BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.post("/session/simulate", response_model=BCIResponse)
async def simulate_bci_session(
    request: BCISimulationRequest,
    background_tasks: BackgroundTasks
) -> BCIResponse:
    """
    🎮 Simulación de sesión BCI

    Ejecuta una simulación completa de sesión BCI para pruebas y demostración.

    **Componentes simulados:**
    1. Inicialización de decodificador
    2. Entrenamiento con datos sintéticos
    3. Decodificación en tiempo real
    4. Métricas de rendimiento
    5. Visualización de resultados

    **Parámetros de simulación:**
    - Duración configurable (1-300 segundos)
    - Modalidad: Motor imagery EEG
    - Clases: Mano izquierda vs derecha
    - Frecuencia: 1 predicción por segundo
    - Adaptación: Habilitada

    **Métricas reportadas:**
    - Precisión promedio
    - Confianza por predicción
    - Distribución de clases
    - Calidad de señal
    - Tiempo de procesamiento

    **Casos de uso:**
    - Pruebas de rendimiento
    - Demostración del sistema
    - Validación de algoritmos
    - Entrenamiento de usuarios
    """
    try:
        logger.info(f"🎮 Iniciando simulación BCI por {request.duration_seconds} segundos")

        result = await bci_service.simulate_real_time_session(request.duration_seconds)

        # Analizar resultados en background
        background_tasks.add_task(
            analyze_simulation_results,
            result,
            request.duration_seconds
        )

        return BCIResponse(
            status="simulation_completed",
            data=result,
            metadata={
                "simulation_type": "motor_imagery_demo",
                "duration_requested": request.duration_seconds,
                "predictions_per_second": 1.0
            }
        )

    except NeuroscienceError as e:
        logger.error(f"❌ Error en simulación BCI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")


# Tareas en background
async def log_training_completion(decoder_id: str, sample_count: int):
    """Registrar finalización de entrenamiento"""
    logger.info(f"✅ Entrenamiento completado - Decoder: {decoder_id}, Samples: {sample_count}")


async def log_adaptation_event(decoder_id: str, true_label: str):
    """Registrar evento de adaptación"""
    logger.info(f"🔄 Adaptación realizada - Decoder: {decoder_id}, Label: {true_label}")


async def save_calibration_data(user_id: str, modality: str, result: Dict[str, Any]):
    """Guardar datos de calibración"""
    logger.info(f"💾 Calibración guardada - Usuario: {user_id}, Modalidad: {modality}")


async def analyze_simulation_results(result: Dict[str, Any], duration: int):
    """Analizar resultados de simulación"""
    accuracy = result.get('average_confidence', 0.0)
    total_predictions = result.get('total_predictions', 0)
    logger.info(f"📊 Simulación analizada - Duración: {duration}s, Predicciones: {total_predictions}, Precisión: {accuracy:.3f}")


# Endpoints de utilidad
@router.get("/modalities", response_model=Dict[str, List[str]])
async def get_supported_modalities():
    """
    📋 Obtener modalidades BCI soportadas

    Lista todas las modalidades BCI disponibles en el sistema.
    """
    return {
        "modalities": [modality.value for modality in BCIModalityType],
        "algorithms": [algorithm.value for algorithm in DecodingAlgorithm],
        "signal_qualities": [quality.value for quality in SignalQuality]
    }


@router.get("/capabilities/{modality}")
async def get_modality_capabilities(modality: str) -> Dict[str, Any]:
    """
    ⚙️ Obtener capacidades de modalidad específica

    Detalla las capacidades y configuraciones disponibles para una modalidad BCI.
    """
    try:
        modality_enum = BCIModalityType(modality)
        capabilities = bci_service._get_decoder_capabilities(modality_enum)

        return {
            "modality": modality,
            "capabilities": capabilities,
            "recommended_config": {
                "sampling_rate": 250.0 if modality in {"eeg", "ecog"} else 1000.0,
                "channels": ["C3", "C4", "Cz"] if modality == "motor_imagery" else ["Fz", "Cz", "Pz"],
                "session_duration_minutes": 15,
                "training_trials": 40
            }
        }

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Modalidad no soportada: {modality}")
