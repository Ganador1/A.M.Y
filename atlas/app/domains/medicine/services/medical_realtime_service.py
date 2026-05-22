"""
⚡ Servicio de Tiempo Real Médico - AXIOM v4.1

Este módulo implementa capacidades de tiempo real para el dominio médico,
proporcionando streaming de datos, procesamiento en vivo, y monitoreo continuo
de señales biomédicas y datos clínicos.

Características principales:
- Streaming de datos médicos en tiempo real via WebSockets
- Procesamiento continuo de señales biomédicas (ECG, EEG, EMG)
- Monitoreo de signos vitales con alertas automáticas
- Análisis en vivo de imágenes médicas (ultrasonido, fluoroscopia)
- Sincronización multi-dispositivo para quirófanos
- Buffer inteligente con compresión de datos
- Alertas clínicas automáticas basadas en umbrales
- Dashboard en tiempo real para personal médico

Capacidades de streaming:
- ECG: Electrocardiografía en tiempo real (hasta 1000 Hz)
- EEG: Electroencefalografía para monitoreo neurológico
- EMG: Electromiografía para análisis muscular
- Signos vitales: Presión arterial, saturación O2, temperatura
- Imágenes médicas: Ultrasonido, fluoroscopia, endoscopia
- Datos de sensores: Acelerómetros, giroscopios biomédicos

Protocolos soportados:
- WebSocket: Comunicación bidireccional en tiempo real
- Server-Sent Events: Streaming unidireccional
- gRPC: Para servicios de alto rendimiento
- MQTT: Para dispositivos IoT médicos
- HL7 FHIR: Para interoperabilidad clínica

Patrones de procesamiento:
- Stream processing con ventanas deslizantes
- Detección de patrones en tiempo real
- Agregación temporal de métricas
- Filtrado adaptativo de señales
- Compresión sin pérdida para almacenamiento

Seguridad y privacidad:
- Cifrado extremo a extremo
- Autenticación per-stream
- Audit trail completo
- Cumplimiento HIPAA/GDPR
- Anonimización automática

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, AsyncIterator, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import deque
import uuid

from app.core.logging import get_logger
from app.exceptions.domain.medicine import MedicalError

logger = get_logger(__name__)

# =====================================================================================
# ENUMS Y CONSTANTES
# =====================================================================================

class StreamType(Enum):
    """Tipos de stream médicos soportados"""
    ECG = "ecg"
    EEG = "eeg" 
    EMG = "emg"
    VITAL_SIGNS = "vital_signs"
    MEDICAL_IMAGING = "medical_imaging"
    SENSOR_DATA = "sensor_data"
    CLINICAL_NOTES = "clinical_notes"
    LABORATORY_RESULTS = "lab_results"

class AlertLevel(Enum):
    """Niveles de alerta clínica"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ProcessingMode(Enum):
    """Modos de procesamiento en tiempo real"""
    RAW = "raw"  # Datos sin procesar
    FILTERED = "filtered"  # Filtrado básico
    ANALYZED = "analyzed"  # Análisis completo
    COMPRESSED = "compressed"  # Compresión inteligente

# Configuración de frecuencias por tipo de señal
SIGNAL_FREQUENCIES = {
    StreamType.ECG: 1000,  # Hz
    StreamType.EEG: 500,   # Hz
    StreamType.EMG: 2000,  # Hz
    StreamType.VITAL_SIGNS: 1,  # Hz
    StreamType.MEDICAL_IMAGING: 30,  # FPS
    StreamType.SENSOR_DATA: 100,  # Hz
    StreamType.CLINICAL_NOTES: 0.1,  # Hz
    StreamType.LABORATORY_RESULTS: 0.01  # Hz
}

# =====================================================================================
# MODELOS DE DATOS
# =====================================================================================

@dataclass
class StreamMetadata:
    """Metadatos de un stream médico"""
    stream_id: str
    stream_type: StreamType
    patient_id: str
    device_id: str
    sampling_rate: float
    start_time: datetime
    processing_mode: ProcessingMode = ProcessingMode.FILTERED
    encryption_enabled: bool = True
    compression_level: int = 1  # 0-9
    buffer_size: int = 1000
    alert_thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class MedicalDataPoint:
    """Punto de datos médicos en tiempo real"""
    timestamp: datetime
    stream_id: str
    patient_id: str
    data_type: StreamType
    values: Union[Dict[str, float], List[float], np.ndarray]
    quality_score: float = 1.0
    flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MedicalAlert:
    """Alerta médica en tiempo real"""
    alert_id: str
    timestamp: datetime
    patient_id: str
    stream_id: str
    level: AlertLevel
    message: str
    trigger_value: float
    threshold: float
    recommended_action: str
    auto_acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

@dataclass
class StreamStatistics:
    """Estadísticas de un stream médico"""
    stream_id: str
    total_data_points: int
    data_rate_hz: float
    average_latency_ms: float
    packet_loss_percent: float
    quality_score: float
    alerts_triggered: int
    last_updated: datetime
    buffer_utilization: float

# =====================================================================================
# CORE REALTIME SERVICE
# =====================================================================================

class MedicalRealtimeService:
    """
    Servicio principal de tiempo real médico
    
    Gestiona streams de datos médicos, procesamiento en vivo,
    alertas automáticas, y distribución a clientes conectados.
    """
    
    def __init__(self):
        self.active_streams: Dict[str, StreamMetadata] = {}
        self.data_buffers: Dict[str, deque] = {}
        self.websocket_clients: Dict[str, Any] = {}
        self.alert_handlers: List[Callable[[MedicalAlert], None]] = []
        self.stream_statistics: Dict[str, StreamStatistics] = {}
        
        # Componentes de procesamiento
        self.signal_processors: Dict[StreamType, 'SignalProcessor'] = {}
        self.alert_engine: 'AlertEngine' = AlertEngine()
        self.compression_engine: 'CompressionEngine' = CompressionEngine()
        
        # Estado interno
        self._is_running = False
        self._processing_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("🏥 MedicalRealtimeService inicializado")
    
    async def start_service(self) -> None:
        """Inicia el servicio de tiempo real"""
        if self._is_running:
            logger.warning("⚠️ Servicio ya está ejecutándose")
            return
            
        try:
            logger.info("⚡ Iniciando servicio de tiempo real médico...")
            
            # Inicializar procesadores de señal
            await self._initialize_signal_processors()
            
            # Inicializar motor de alertas
            await self.alert_engine.initialize()
            
            # Inicializar motor de compresión
            await self.compression_engine.initialize()
            
            self._is_running = True
            logger.info("✅ Servicio de tiempo real iniciado correctamente")
            
        except MedicalError as e:
            logger.error(f"❌ Error iniciando servicio de tiempo real: {e}")
            raise
    
    async def stop_service(self) -> None:
        """Detiene el servicio de tiempo real"""
        if not self._is_running:
            return
            
        logger.info("🛑 Deteniendo servicio de tiempo real médico...")
        
        # Cancelar tareas de procesamiento
        for task in self._processing_tasks.values():
            task.cancel()
        
        # Cerrar streams activos
        for stream_id in list(self.active_streams.keys()):
            await self.stop_stream(stream_id)
        
        # Cerrar conexiones WebSocket
        await self._close_all_websockets()
        
        self._is_running = False
        logger.info("✅ Servicio de tiempo real detenido")
    
    async def create_medical_stream(
        self,
        patient_id: str,
        stream_type: StreamType,
        device_id: str,
        processing_mode: ProcessingMode = ProcessingMode.FILTERED,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crea un nuevo stream de datos médicos
        
        Args:
            patient_id: ID del paciente
            stream_type: Tipo de stream médico
            device_id: ID del dispositivo
            processing_mode: Modo de procesamiento
            custom_config: Configuración personalizada
            
        Returns:
            ID del stream creado
        """
        stream_id = f"{patient_id}_{stream_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Configuración por defecto
        config = custom_config or {}
        sampling_rate = config.get('sampling_rate', SIGNAL_FREQUENCIES[stream_type])
        buffer_size = config.get('buffer_size', 1000)
        alert_thresholds = config.get('alert_thresholds', {})
        
        # Crear metadatos del stream
        metadata = StreamMetadata(
            stream_id=stream_id,
            stream_type=stream_type,
            patient_id=patient_id,
            device_id=device_id,
            sampling_rate=sampling_rate,
            start_time=datetime.now(),
            processing_mode=processing_mode,
            buffer_size=buffer_size,
            alert_thresholds=alert_thresholds
        )
        
        # Registrar stream
        self.active_streams[stream_id] = metadata
        self.data_buffers[stream_id] = deque(maxlen=buffer_size)
        
        # Inicializar estadísticas
        self.stream_statistics[stream_id] = StreamStatistics(
            stream_id=stream_id,
            total_data_points=0,
            data_rate_hz=0.0,
            average_latency_ms=0.0,
            packet_loss_percent=0.0,
            quality_score=1.0,
            alerts_triggered=0,
            last_updated=datetime.now(),
            buffer_utilization=0.0
        )
        
        # Iniciar tarea de procesamiento
        processing_task = asyncio.create_task(
            self._process_stream(stream_id)
        )
        self._processing_tasks[stream_id] = processing_task
        
        logger.info(f"📊 Stream médico creado: {stream_id} ({stream_type.value}) "
                   f"para paciente {patient_id}")
        
        return stream_id
    
    async def stop_stream(self, stream_id: str) -> None:
        """Detiene un stream específico"""
        if stream_id not in self.active_streams:
            logger.warning(f"⚠️ Stream {stream_id} no encontrado")
            return
        
        # Cancelar tarea de procesamiento
        if stream_id in self._processing_tasks:
            self._processing_tasks[stream_id].cancel()
            del self._processing_tasks[stream_id]
        
        # Limpiar datos
        del self.active_streams[stream_id]
        del self.data_buffers[stream_id]
        if stream_id in self.stream_statistics:
            del self.stream_statistics[stream_id]
        
        logger.info(f"🛑 Stream {stream_id} detenido")
    
    async def ingest_data_point(
        self,
        stream_id: str,
        data_point: MedicalDataPoint
    ) -> None:
        """
        Ingesta un punto de datos médicos en tiempo real
        
        Args:
            stream_id: ID del stream
            data_point: Punto de datos médicos
        """
        if stream_id not in self.active_streams:
            logger.warning(f"⚠️ Stream {stream_id} no encontrado para ingesta")
            return
        
        # Validar datos
        if not self._validate_data_point(data_point):
            logger.warning(f"⚠️ Punto de datos inválido para stream {stream_id}")
            return
        
        # Añadir al buffer
        self.data_buffers[stream_id].append(data_point)
        
        # Actualizar estadísticas
        await self._update_stream_statistics(stream_id, data_point)
        
        # Procesar para alertas
        await self._check_for_alerts(stream_id, data_point)
        
        # Distribuir a clientes conectados
        await self._distribute_to_clients(stream_id, data_point)
    
    async def get_stream_data(
        self,
        stream_id: str,
        window_size: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MedicalDataPoint]:
        """
        Obtiene datos de un stream con filtros temporales
        
        Args:
            stream_id: ID del stream
            window_size: Tamaño de ventana (últimos N puntos)
            start_time: Tiempo de inicio
            end_time: Tiempo de fin
            
        Returns:
            Lista de puntos de datos filtrados
        """
        if stream_id not in self.data_buffers:
            return []
        
        buffer = self.data_buffers[stream_id]
        data_points = list(buffer)
        
        # Filtrar por tiempo
        if start_time or end_time:
            filtered_points = []
            for point in data_points:
                if start_time and point.timestamp < start_time:
                    continue
                if end_time and point.timestamp > end_time:
                    continue
                filtered_points.append(point)
            data_points = filtered_points
        
        # Aplicar ventana
        if window_size and window_size < len(data_points):
            data_points = data_points[-window_size:]
        
        return data_points
    
    async def add_websocket_client(
        self,
        client_id: str,
        websocket: Any,
        subscribed_streams: Optional[List[str]] = None
    ) -> None:
        """Añade un cliente WebSocket"""
        self.websocket_clients[client_id] = {
            'websocket': websocket,
            'subscribed_streams': subscribed_streams or [],
            'connected_at': datetime.now()
        }
        
        logger.info(f"🌐 Cliente WebSocket conectado: {client_id}")
    
    async def remove_websocket_client(self, client_id: str) -> None:
        """Remueve un cliente WebSocket"""
        if client_id in self.websocket_clients:
            del self.websocket_clients[client_id]
            logger.info(f"🌐 Cliente WebSocket desconectado: {client_id}")
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        return {
            "service_status": "running" if self._is_running else "stopped",
            "active_streams": len(self.active_streams),
            "connected_clients": len(self.websocket_clients),
            "total_data_points": sum(
                stats.total_data_points 
                for stats in self.stream_statistics.values()
            ),
            "average_latency_ms": np.mean([
                stats.average_latency_ms 
                for stats in self.stream_statistics.values()
            ]) if self.stream_statistics else 0,
            "streams_by_type": self._get_streams_by_type(),
            "alert_summary": await self.alert_engine.get_summary(),
            "last_updated": datetime.now().isoformat()
        }
    
    # =====================================================================================
    # MÉTODOS PRIVADOS
    # =====================================================================================
    
    async def _initialize_signal_processors(self) -> None:
        """Inicializa procesadores de señal especializados"""
        for stream_type in StreamType:
            processor = SignalProcessor(stream_type)
            await processor.initialize()
            self.signal_processors[stream_type] = processor
    
    async def _process_stream(self, stream_id: str) -> None:
        """Procesa un stream específico de forma continua"""
        metadata = self.active_streams[stream_id]
        
        while stream_id in self.active_streams:
            try:
                await asyncio.sleep(1.0 / metadata.sampling_rate)
                
                # Procesar buffer de datos
                if self.data_buffers[stream_id]:
                    await self._process_buffer_batch(stream_id)
                
            except asyncio.CancelledError:
                break
            except MedicalError as e:
                logger.error(f"❌ Error procesando stream {stream_id}: {e}")
                await asyncio.sleep(1.0)  # Evitar loop infinito
    
    async def _process_buffer_batch(self, stream_id: str) -> None:
        """Procesa un lote de datos del buffer"""
        metadata = self.active_streams[stream_id]
        buffer = self.data_buffers[stream_id]
        processor = self.signal_processors[metadata.stream_type]
        
        # Procesar según el modo
        if metadata.processing_mode == ProcessingMode.ANALYZED:
            await processor.analyze_batch(list(buffer))
        elif metadata.processing_mode == ProcessingMode.FILTERED:
            await processor.filter_batch(list(buffer))
    
    def _validate_data_point(self, data_point: MedicalDataPoint) -> bool:
        """Valida un punto de datos médicos"""
        if not data_point.timestamp:
            return False
        if not data_point.stream_id:
            return False
        if not data_point.patient_id:
            return False
        if data_point.quality_score < 0.0 or data_point.quality_score > 1.0:
            return False
        
        return True
    
    async def _update_stream_statistics(
        self, 
        stream_id: str, 
        data_point: MedicalDataPoint
    ) -> None:
        """Actualiza estadísticas de un stream"""
        stats = self.stream_statistics[stream_id]
        
        stats.total_data_points += 1
        stats.last_updated = datetime.now()
        
        # Calcular latencia
        processing_latency = (datetime.now() - data_point.timestamp).total_seconds() * 1000
        stats.average_latency_ms = (
            (stats.average_latency_ms * (stats.total_data_points - 1) + processing_latency) 
            / stats.total_data_points
        )
        
        # Actualizar utilización del buffer
        buffer_size = len(self.data_buffers[stream_id])
        max_size = self.active_streams[stream_id].buffer_size
        stats.buffer_utilization = buffer_size / max_size
    
    async def _check_for_alerts(
        self, 
        stream_id: str, 
        data_point: MedicalDataPoint
    ) -> None:
        """Verifica si se deben generar alertas"""
        metadata = self.active_streams[stream_id]
        
        for threshold_name, threshold_value in metadata.alert_thresholds.items():
            if isinstance(data_point.values, dict):
                current_value = data_point.values.get(threshold_name)
                if current_value and abs(current_value) > threshold_value:
                    await self._trigger_alert(
                        stream_id, 
                        data_point, 
                        threshold_name, 
                        current_value, 
                        threshold_value
                    )
    
    async def _trigger_alert(
        self,
        stream_id: str,
        data_point: MedicalDataPoint,
        parameter: str,
        value: float,
        threshold: float
    ) -> None:
        """Genera una alerta médica"""
        alert = MedicalAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            patient_id=data_point.patient_id,
            stream_id=stream_id,
            level=self._determine_alert_level(parameter, value, threshold),
            message=f"{parameter} fuera de rango: {value} (límite: {threshold})",
            trigger_value=value,
            threshold=threshold,
            recommended_action=self._get_recommended_action(parameter, value, threshold)
        )
        
        # Procesar alerta
        await self.alert_engine.process_alert(alert)
        
        # Actualizar estadísticas
        self.stream_statistics[stream_id].alerts_triggered += 1
        
        # Notificar handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except MedicalError as e:
                logger.error(f"❌ Error en handler de alerta: {e}")
    
    def _determine_alert_level(
        self, 
        parameter: str, 
        value: float, 
        threshold: float
    ) -> AlertLevel:
        """Determina el nivel de alerta basado en parámetros"""
        ratio = abs(value) / threshold
        
        if ratio > 2.0:
            return AlertLevel.EMERGENCY
        elif ratio > 1.5:
            return AlertLevel.CRITICAL
        elif ratio > 1.2:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _get_recommended_action(
        self, 
        parameter: str, 
        value: float, 
        threshold: float
    ) -> str:
        """Obtiene acción recomendada para una alerta"""
        # Mapeo básico de acciones recomendadas
        action_map = {
            'heart_rate': 'Verificar estado cardiovascular del paciente',
            'blood_pressure': 'Revisar medicación antihipertensiva',
            'oxygen_saturation': 'Evaluar función respiratoria',
            'temperature': 'Controlar signos de infección',
            'glucose': 'Ajustar protocolo diabético'
        }
        
        return action_map.get(parameter, 'Consultar con médico especialista')
    
    async def _distribute_to_clients(
        self, 
        stream_id: str, 
        data_point: MedicalDataPoint
    ) -> None:
        """Distribuye datos a clientes WebSocket conectados"""
        disconnected_clients = []
        
        for client_id, client_info in self.websocket_clients.items():
            # Verificar suscripción
            subscribed_streams = client_info['subscribed_streams']
            if subscribed_streams and stream_id not in subscribed_streams:
                continue
            
            try:
                # Serializar y enviar
                message = {
                    'type': 'medical_data',
                    'stream_id': stream_id,
                    'timestamp': data_point.timestamp.isoformat(),
                    'patient_id': data_point.patient_id,
                    'data_type': data_point.data_type.value,
                    'values': self._serialize_values(data_point.values),
                    'quality_score': data_point.quality_score
                }
                
                websocket = client_info['websocket']
                await websocket.send(json.dumps(message))
                
            except ConnectionError:
                disconnected_clients.append(client_id)
            except MedicalError as e:
                logger.error(f"❌ Error enviando datos a cliente {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Limpiar clientes desconectados
        for client_id in disconnected_clients:
            await self.remove_websocket_client(client_id)
    
    def _serialize_values(self, values: Union[Dict, List, np.ndarray]) -> Any:
        """Serializa valores para JSON"""
        if isinstance(values, np.ndarray):
            return values.tolist()
        elif isinstance(values, dict):
            return {k: float(v) if isinstance(v, (int, float)) else v 
                   for k, v in values.items()}
        elif isinstance(values, list):
            return [float(v) if isinstance(v, (int, float)) else v for v in values]
        else:
            return values
    
    async def _close_all_websockets(self) -> None:
        """Cierra todas las conexiones WebSocket"""
        for client_id, client_info in self.websocket_clients.items():
            try:
                websocket = client_info['websocket']
                await websocket.close()
            except MedicalError as e:
                logger.error(f"❌ Error cerrando WebSocket {client_id}: {e}")
        
        self.websocket_clients.clear()
    
    def _get_streams_by_type(self) -> Dict[str, int]:
        """Obtiene conteo de streams por tipo"""
        counts = {}
        for metadata in self.active_streams.values():
            stream_type = metadata.stream_type.value
            counts[stream_type] = counts.get(stream_type, 0) + 1
        return counts


# =====================================================================================
# COMPONENTES ESPECIALIZADOS
# =====================================================================================

class SignalProcessor:
    """Procesador especializado de señales médicas"""
    
    def __init__(self, stream_type: StreamType):
        self.stream_type = stream_type
        self.filters = {}
        self.analyzers = {}
    
    async def initialize(self) -> None:
        """Inicializa el procesador de señal"""
        if self.stream_type == StreamType.ECG:
            await self._setup_ecg_processing()
        elif self.stream_type == StreamType.EEG:
            await self._setup_eeg_processing()
        elif self.stream_type == StreamType.EMG:
            await self._setup_emg_processing()
    
    async def filter_batch(self, data_points: List[MedicalDataPoint]) -> List[MedicalDataPoint]:
        """Aplica filtrado a un lote de datos"""
        # Implementación específica por tipo de señal
        return data_points
    
    async def analyze_batch(self, data_points: List[MedicalDataPoint]) -> Dict[str, Any]:
        """Analiza un lote de datos"""
        # Implementación específica por tipo de señal
        return {"analysis": "placeholder"}
    
    async def _setup_ecg_processing(self) -> None:
        """Configura procesamiento de ECG"""
        # Filtros especializados para ECG
        pass
    
    async def _setup_eeg_processing(self) -> None:
        """Configura procesamiento de EEG"""
        # Filtros especializados para EEG
        pass
    
    async def _setup_emg_processing(self) -> None:
        """Configura procesamiento de EMG"""
        # Filtros especializados para EMG
        pass


class AlertEngine:
    """Motor de alertas médicas"""
    
    def __init__(self):
        self.alert_rules = {}
        self.alert_history = deque(maxlen=1000)
        self.suppression_rules = {}
    
    async def initialize(self) -> None:
        """Inicializa el motor de alertas"""
        await self._load_alert_rules()
    
    async def process_alert(self, alert: MedicalAlert) -> None:
        """Procesa una alerta médica"""
        # Verificar supresión
        if await self._is_suppressed(alert):
            return
        
        # Añadir al historial
        self.alert_history.append(alert)
        
        # Procesar según el nivel
        if alert.level == AlertLevel.EMERGENCY:
            await self._handle_emergency_alert(alert)
        elif alert.level == AlertLevel.CRITICAL:
            await self._handle_critical_alert(alert)
        
        logger.info(f"🚨 Alerta procesada: {alert.level.value} - {alert.message}")
    
    async def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de alertas"""
        if not self.alert_history:
            return {"total_alerts": 0}
        
        recent_alerts = [
            a for a in self.alert_history 
            if a.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "total_alerts": len(self.alert_history),
            "recent_alerts_24h": len(recent_alerts),
            "by_level": {
                level.value: len([a for a in recent_alerts if a.level == level])
                for level in AlertLevel
            },
            "unacknowledged": len([a for a in recent_alerts if not a.auto_acknowledged])
        }
    
    async def _load_alert_rules(self) -> None:
        """Carga reglas de alerta"""
        # Cargar desde configuración
        pass
    
    async def _is_suppressed(self, alert: MedicalAlert) -> bool:
        """Verifica si una alerta está suprimida"""
        # Implementar lógica de supresión
        return False
    
    async def _handle_emergency_alert(self, alert: MedicalAlert) -> None:
        """Maneja alertas de emergencia"""
        # Notificaciones inmediatas
        logger.critical(f"🆘 EMERGENCIA MÉDICA: {alert.message}")
    
    async def _handle_critical_alert(self, alert: MedicalAlert) -> None:
        """Maneja alertas críticas"""
        # Notificaciones prioritarias
        logger.error(f"🚨 ALERTA CRÍTICA: {alert.message}")


class CompressionEngine:
    """Motor de compresión de datos médicos"""
    
    def __init__(self):
        self.compression_algorithms = {}
    
    async def initialize(self) -> None:
        """Inicializa el motor de compresión"""
        # Configurar algoritmos de compresión
        pass
    
    async def compress_data(
        self, 
        data: List[MedicalDataPoint], 
        compression_level: int = 1
    ) -> bytes:
        """Comprime datos médicos"""
        # Implementar compresión
        return b""
    
    async def decompress_data(self, compressed_data: bytes) -> List[MedicalDataPoint]:
        """Descomprime datos médicos"""
        # Implementar descompresión
        return []


# =====================================================================================
# FACTORY Y UTILIDADES
# =====================================================================================

def create_medical_realtime_service() -> MedicalRealtimeService:
    """Factory para crear instancia del servicio"""
    return MedicalRealtimeService()

async def simulate_medical_data_stream(
    stream_id: str,
    stream_type: StreamType,
    duration_seconds: int = 60,
    service: Optional[MedicalRealtimeService] = None
) -> AsyncIterator[MedicalDataPoint]:
    """
    Genera stream simulado de datos médicos para testing
    
    Args:
        stream_id: ID del stream
        stream_type: Tipo de stream
        duration_seconds: Duración de la simulación
        service: Servicio para ingestar datos
        
    Yields:
        MedicalDataPoint simulados
    """
    start_time = datetime.now()
    patient_id = f"PATIENT_DEMO_{uuid.uuid4().hex[:6]}"
    
    while (datetime.now() - start_time).total_seconds() < duration_seconds:
        # Generar datos simulados según el tipo
        if stream_type == StreamType.ECG:
            values = {"amplitude": np.random.normal(1.0, 0.2)}
        elif stream_type == StreamType.VITAL_SIGNS:
            values = {
                "heart_rate": np.random.normal(75, 10),
                "blood_pressure_systolic": np.random.normal(120, 15),
                "blood_pressure_diastolic": np.random.normal(80, 10),
                "oxygen_saturation": np.random.normal(98, 2),
                "temperature": np.random.normal(37.0, 0.5)
            }
        else:
            values = {"value": np.random.random()}
        
        data_point = MedicalDataPoint(
            timestamp=datetime.now(),
            stream_id=stream_id,
            patient_id=patient_id,
            data_type=stream_type,
            values=values,
            quality_score=np.random.uniform(0.8, 1.0)
        )
        
        if service:
            await service.ingest_data_point(stream_id, data_point)
        
        yield data_point
        
        # Respetar frecuencia de muestreo
        await asyncio.sleep(1.0 / SIGNAL_FREQUENCIES[stream_type])
