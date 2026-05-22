"""
🚀 Ejemplo Práctico de Sistema de Tiempo Real Médico - AXIOM v4.1

Este script demuestra las capacidades completas del sistema de tiempo real
médico, incluyendo streaming de datos, WebSockets, alertas automáticas,
y monitoreo continuo.

Escenarios demostrados:
1. 🏥 Monitoreo de signos vitales en UCI
2. 🫀 Análisis de ECG en tiempo real con detección de arritmias
3. 🧠 Procesamiento de señales EEG para monitoreo neurológico
4. 💊 Alertas médicas automáticas basadas en umbrales
5. 📊 Dashboard en tiempo real para personal médico
6. 🔗 Comunicación WebSocket bidireccional
7. 📈 Análisis de tendencias y patrones
8. 🚨 Sistema de alertas escaladas

Este ejemplo simula un escenario hospitalario real donde múltiples
pacientes están siendo monitoreados simultáneamente con diferentes
tipos de dispositivos médicos.

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.logging import get_logger
from app.domains.medicine.services.medical_realtime_service import (
    MedicalRealtimeService,
    StreamType,
    ProcessingMode,
    MedicalDataPoint,
    MedicalAlert,
    AlertLevel,
    create_medical_realtime_service
)
from app.domains.medicine.services.websocket_handler import (
    MedicalWebSocketHandler,
    create_websocket_handler
)

logger = get_logger(__name__)

# =====================================================================================
# CONFIGURACIÓN DE LA DEMOSTRACIÓN
# =====================================================================================

# Pacientes de ejemplo
DEMO_PATIENTS = [
    {
        "patient_id": "ICU_001",
        "name": "María García",
        "age": 67,
        "condition": "Post-operatorio cardíaco",
        "severity": "critical",
        "streams": [StreamType.ECG, StreamType.VITAL_SIGNS],
        "alert_thresholds": {
            "heart_rate": 100,
            "blood_pressure_systolic": 160,
            "oxygen_saturation": 92
        }
    },
    {
        "patient_id": "ICU_002", 
        "name": "José Rodríguez",
        "age": 45,
        "condition": "Monitoreo neurológico",
        "severity": "high",
        "streams": [StreamType.EEG, StreamType.VITAL_SIGNS],
        "alert_thresholds": {
            "heart_rate": 110,
            "blood_pressure_systolic": 150
        }
    },
    {
        "patient_id": "WARD_003",
        "name": "Ana López",
        "age": 78,
        "condition": "Recuperación general",
        "severity": "medium",
        "streams": [StreamType.VITAL_SIGNS],
        "alert_thresholds": {
            "heart_rate": 90,
            "temperature": 38.5
        }
    }
]

# Configuración de dispositivos
DEMO_DEVICES = {
    "ECG_MONITOR_001": {"type": "ecg", "sampling_rate": 250},
    "VITAL_MONITOR_001": {"type": "vital_signs", "sampling_rate": 1},
    "EEG_SYSTEM_001": {"type": "eeg", "sampling_rate": 256},
    "PULSE_OX_001": {"type": "vital_signs", "sampling_rate": 1}
}

# =====================================================================================
# SIMULADORES DE DATOS MÉDICOS
# =====================================================================================

class MedicalDataSimulator:
    """Simulador de datos médicos realistas"""
    
    def __init__(self):
        self.baseline_vitals = {
            "heart_rate": 75,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "oxygen_saturation": 98,
            "temperature": 37.0,
            "respiratory_rate": 16
        }
        self.ecg_pattern = self._generate_ecg_pattern()
        self.eeg_baseline = 0.0
        
    def generate_vital_signs(self, patient_severity: str) -> Dict[str, float]:
        """Genera signos vitales simulados basados en la severidad del paciente"""
        
        # Factores de variabilidad según severidad
        variability = {
            "critical": 0.3,
            "high": 0.2,
            "medium": 0.15,
            "low": 0.1
        }
        
        factor = variability.get(patient_severity, 0.15)
        
        vitals = {}
        for vital, baseline in self.baseline_vitals.items():
            # Añadir variabilidad realista
            noise = np.random.normal(0, baseline * factor * 0.1)
            trend = np.sin(time.time() / 60) * baseline * factor * 0.05  # Tendencia lenta
            
            # Ocasionales anomalías
            if random.random() < 0.05:  # 5% probabilidad de anomalía
                anomaly = np.random.normal(0, baseline * factor * 0.5)
                noise += anomaly
            
            vitals[vital] = max(0, baseline + noise + trend)
        
        # Ajustes específicos por tipo
        if patient_severity == "critical":
            vitals["heart_rate"] += random.uniform(-10, 20)
            vitals["blood_pressure_systolic"] += random.uniform(-20, 30)
        
        return vitals
    
    def generate_ecg_sample(self) -> List[float]:
        """Genera muestra de ECG simulada"""
        # Patrón ECG básico: P-QRS-T
        timestamp = time.time()
        heart_rate = 75 + np.sin(timestamp / 10) * 10  # Variabilidad cardíaca
        
        # Generar onda con ocasionales arritmias
        if random.random() < 0.02:  # 2% probabilidad de arritmia
            return self._generate_arrhythmic_pattern()
        else:
            return self._generate_normal_ecg(heart_rate)
    
    def generate_eeg_sample(self) -> List[float]:
        """Genera muestra de EEG simulada"""
        # Diferentes bandas de frecuencia EEG
        alpha = np.sin(time.time() * 2 * np.pi * 10) * 0.5  # 8-12 Hz
        beta = np.sin(time.time() * 2 * np.pi * 20) * 0.3   # 13-30 Hz
        theta = np.sin(time.time() * 2 * np.pi * 6) * 0.2   # 4-8 Hz
        
        # Ruido de fondo
        noise = np.random.normal(0, 0.1)
        
        eeg_signal = alpha + beta + theta + noise
        
        # Ocasionales picos epileptiformes
        if random.random() < 0.01:  # 1% probabilidad
            eeg_signal += random.uniform(2, 5)
        
        return [eeg_signal]
    
    def _generate_ecg_pattern(self) -> List[float]:
        """Genera patrón ECG base"""
        # Patrón simplificado de ECG normal
        pattern = []
        for i in range(100):  # 1 segundo a 100 Hz
            t = i / 100.0
            if 0.1 < t < 0.2:  # Onda P
                pattern.append(0.1 * np.sin(np.pi * (t - 0.1) / 0.1))
            elif 0.3 < t < 0.4:  # Complejo QRS
                pattern.append(1.0 * np.sin(np.pi * (t - 0.3) / 0.1))
            elif 0.5 < t < 0.7:  # Onda T
                pattern.append(0.3 * np.sin(np.pi * (t - 0.5) / 0.2))
            else:
                pattern.append(0.0)
        return pattern
    
    def _generate_normal_ecg(self, heart_rate: float) -> List[float]:
        """Genera ECG normal ajustado por frecuencia cardíaca"""
        scale_factor = 60.0 / heart_rate
        scaled_pattern = []
        
        for i, value in enumerate(self.ecg_pattern):
            scaled_time = i * scale_factor
            if scaled_time < len(self.ecg_pattern):
                scaled_pattern.append(value + np.random.normal(0, 0.05))
        
        return scaled_pattern[:50]  # Retornar 50 samples
    
    def _generate_arrhythmic_pattern(self) -> List[float]:
        """Genera patrón arrítmico"""
        # Patrón irregular para simular arritmia
        pattern = []
        for _ in range(50):
            if random.random() < 0.3:
                pattern.append(random.uniform(-0.5, 1.5))
            else:
                pattern.append(random.uniform(-0.1, 0.1))
        return pattern

# =====================================================================================
# MANEJADOR DE ALERTAS
# =====================================================================================

class DemoAlertHandler:
    """Manejador de demostración para alertas médicas"""
    
    def __init__(self):
        self.alert_count = 0
        self.critical_alerts = 0
        self.last_alert_time = {}
        
    def handle_alert(self, alert: MedicalAlert) -> None:
        """Maneja una alerta médica"""
        self.alert_count += 1
        
        if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            self.critical_alerts += 1
        
        # Evitar spam de alertas
        alert_key = f"{alert.patient_id}_{alert.stream_id}"
        now = datetime.now()
        
        if alert_key in self.last_alert_time:
            time_diff = now - self.last_alert_time[alert_key]
            if time_diff < timedelta(minutes=5):
                return  # Suprimir alerta repetitiva
        
        self.last_alert_time[alert_key] = now
        
        # Log según el nivel de alerta
        if alert.level == AlertLevel.EMERGENCY:
            logger.critical(f"🆘 EMERGENCIA - {alert.patient_id}: {alert.message}")
            logger.critical(f"   Acción recomendada: {alert.recommended_action}")
        elif alert.level == AlertLevel.CRITICAL:
            logger.error(f"🚨 CRÍTICO - {alert.patient_id}: {alert.message}")
            logger.error(f"   Acción recomendada: {alert.recommended_action}")
        elif alert.level == AlertLevel.WARNING:
            logger.warning(f"⚠️ ALERTA - {alert.patient_id}: {alert.message}")
        else:
            logger.info(f"ℹ️ INFO - {alert.patient_id}: {alert.message}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de alertas"""
        return {
            "total_alerts": self.alert_count,
            "critical_alerts": self.critical_alerts,
            "active_patients": len(self.last_alert_time),
            "last_update": datetime.now().isoformat()
        }

# =====================================================================================
# CLASE PRINCIPAL DE DEMOSTRACIÓN
# =====================================================================================

class MedicalRealtimeDemo:
    """Demostración completa del sistema de tiempo real médico"""
    
    def __init__(self):
        self.realtime_service: Optional[MedicalRealtimeService] = None
        self.websocket_handler: Optional[MedicalWebSocketHandler] = None
        self.data_simulator = MedicalDataSimulator()
        self.alert_handler = DemoAlertHandler()
        
        self.active_streams: Dict[str, str] = {}  # patient_id -> stream_id
        self.simulation_tasks: List[asyncio.Task] = []
        
    async def initialize(self) -> None:
        """Inicializa los servicios de la demostración"""
        logger.info("🚀 Inicializando demostración de tiempo real médico...")
        
        # Crear e inicializar servicios
        self.realtime_service = create_medical_realtime_service()
        await self.realtime_service.start_service()
        
        self.websocket_handler = create_websocket_handler(self.realtime_service)
        await self.websocket_handler.start_handler()
        
        # Registrar manejador de alertas
        self.realtime_service.alert_handlers.append(self.alert_handler.handle_alert)
        
        logger.info("✅ Servicios inicializados correctamente")
    
    async def setup_patients(self) -> None:
        """Configura streams para pacientes de demostración"""
        logger.info("👥 Configurando pacientes de demostración...")
        
        for patient in DEMO_PATIENTS:
            patient_id = patient["patient_id"]
            logger.info(f"🏥 Configurando paciente: {patient['name']} ({patient_id})")
            
            # Crear streams para cada tipo de monitoreo
            for stream_type in patient["streams"]:
                device_id = f"DEVICE_{patient_id}_{stream_type.value.upper()}"
                
                # Configuración personalizada
                custom_config = {
                    "alert_thresholds": patient["alert_thresholds"],
                    "buffer_size": 1000,
                    "compression_level": 1 if patient["severity"] == "critical" else 2
                }
                
                stream_id = await self.realtime_service.create_medical_stream(
                    patient_id=patient_id,
                    stream_type=stream_type,
                    device_id=device_id,
                    processing_mode=ProcessingMode.ANALYZED,
                    custom_config=custom_config
                )
                
                self.active_streams[f"{patient_id}_{stream_type.value}"] = stream_id
                
                logger.info(f"📊 Stream creado: {stream_type.value} para {patient['name']}")
        
        logger.info(f"✅ {len(self.active_streams)} streams configurados")
    
    async def start_data_simulation(self) -> None:
        """Inicia simulación de datos médicos"""
        logger.info("🎯 Iniciando simulación de datos médicos...")
        
        for patient in DEMO_PATIENTS:
            for stream_type in patient["streams"]:
                task = asyncio.create_task(
                    self._simulate_patient_data(patient, stream_type)
                )
                self.simulation_tasks.append(task)
        
        logger.info(f"✅ {len(self.simulation_tasks)} simuladores iniciados")
    
    async def _simulate_patient_data(
        self, 
        patient: Dict[str, Any], 
        stream_type: StreamType
    ) -> None:
        """Simula datos para un paciente específico"""
        patient_id = patient["patient_id"]
        stream_key = f"{patient_id}_{stream_type.value}"
        stream_id = self.active_streams[stream_key]
        
        logger.info(f"🔬 Iniciando simulación {stream_type.value} para {patient['name']}")
        
        while True:
            try:
                # Generar datos según el tipo de stream
                if stream_type == StreamType.VITAL_SIGNS:
                    values = self.data_simulator.generate_vital_signs(patient["severity"])
                elif stream_type == StreamType.ECG:
                    ecg_samples = self.data_simulator.generate_ecg_sample()
                    values = {"ecg_samples": ecg_samples, "amplitude": np.mean(ecg_samples)}
                elif stream_type == StreamType.EEG:
                    eeg_samples = self.data_simulator.generate_eeg_sample()
                    values = {"eeg_samples": eeg_samples, "amplitude": eeg_samples[0]}
                else:
                    values = {"value": random.uniform(0.5, 1.5)}
                
                # Crear punto de datos
                data_point = MedicalDataPoint(
                    timestamp=datetime.now(),
                    stream_id=stream_id,
                    patient_id=patient_id,
                    data_type=stream_type,
                    values=values,
                    quality_score=random.uniform(0.85, 1.0),
                    flags=self._generate_flags(patient, values)
                )
                
                # Ingestar en el servicio
                await self.realtime_service.ingest_data_point(stream_id, data_point)
                
                # Esperar según la frecuencia de muestreo
                if stream_type == StreamType.VITAL_SIGNS:
                    await asyncio.sleep(1.0)  # 1 Hz
                elif stream_type == StreamType.ECG:
                    await asyncio.sleep(1.0 / 250)  # 250 Hz
                elif stream_type == StreamType.EEG:
                    await asyncio.sleep(1.0 / 256)  # 256 Hz
                else:
                    await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                logger.info(f"🛑 Simulación cancelada para {patient_id}_{stream_type.value}")
                break
            except Exception as e:
                logger.error(f"❌ Error en simulación {patient_id}_{stream_type.value}: {e}")
                await asyncio.sleep(1.0)
    
    def _generate_flags(self, patient: Dict, values: Dict) -> List[str]:
        """Genera flags basados en los valores y estado del paciente"""
        flags = []
        
        if isinstance(values, dict):
            # Verificar anomalías
            if "heart_rate" in values:
                hr = values["heart_rate"]
                if hr > 100:
                    flags.append("tachycardia")
                elif hr < 60:
                    flags.append("bradycardia")
            
            if "oxygen_saturation" in values:
                spo2 = values["oxygen_saturation"]
                if spo2 < 95:
                    flags.append("hypoxemia")
            
            if "temperature" in values:
                temp = values["temperature"]
                if temp > 38.0:
                    flags.append("fever")
                elif temp < 36.0:
                    flags.append("hypothermia")
        
        return flags
    
    async def run_demo(self, duration_minutes: int = 5) -> None:
        """Ejecuta la demostración completa"""
        logger.info(f"🏁 Iniciando demostración por {duration_minutes} minutos...")
        
        try:
            # Mostrar estadísticas cada 30 segundos
            stats_task = asyncio.create_task(self._show_periodic_stats())
            
            # Esperar duración de la demostración
            await asyncio.sleep(duration_minutes * 60)
            
            # Cancelar tarea de estadísticas
            stats_task.cancel()
            
        except KeyboardInterrupt:
            logger.info("⌨️ Demostración interrumpida por el usuario")
        
        finally:
            await self.cleanup()
    
    async def _show_periodic_stats(self) -> None:
        """Muestra estadísticas periódicas"""
        while True:
            try:
                await asyncio.sleep(30)  # Cada 30 segundos
                
                # Estadísticas del servicio de tiempo real
                realtime_stats = await self.realtime_service.get_service_statistics()
                
                # Estadísticas del handler WebSocket
                websocket_stats = await self.websocket_handler.get_handler_statistics()
                
                # Estadísticas de alertas
                alert_stats = self.alert_handler.get_summary()
                
                logger.info("📊 === ESTADÍSTICAS DEL SISTEMA ===")
                logger.info(f"🔄 Streams activos: {realtime_stats['active_streams']}")
                logger.info(f"📈 Total puntos de datos: {realtime_stats['total_data_points']}")
                logger.info(f"⚡ Latencia promedio: {realtime_stats['average_latency_ms']:.1f}ms")
                logger.info(f"🌐 Clientes WebSocket: {websocket_stats['total_connections']}")
                logger.info(f"🚨 Total alertas: {alert_stats['total_alerts']}")
                logger.info(f"🆘 Alertas críticas: {alert_stats['critical_alerts']}")
                logger.info("=" * 40)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error mostrando estadísticas: {e}")
    
    async def cleanup(self) -> None:
        """Limpia recursos de la demostración"""
        logger.info("🧹 Limpiando recursos de la demostración...")
        
        # Cancelar tareas de simulación
        for task in self.simulation_tasks:
            task.cancel()
        
        # Detener streams
        for stream_id in self.active_streams.values():
            try:
                await self.realtime_service.stop_stream(stream_id)
            except Exception as e:
                logger.error(f"❌ Error deteniendo stream: {e}")
        
        # Detener servicios
        if self.websocket_handler:
            await self.websocket_handler.stop_handler()
        
        if self.realtime_service:
            await self.realtime_service.stop_service()
        
        logger.info("✅ Limpieza completada")

# =====================================================================================
# FUNCIÓN PRINCIPAL
# =====================================================================================

async def run_medical_realtime_demo():
    """Ejecuta la demostración completa del sistema de tiempo real médico"""
    
    print("""
    🏥 ===== AXIOM MEDICAL REALTIME SYSTEM DEMO =====
    
    Esta demostración muestra las capacidades completas del sistema
    de tiempo real médico de AXIOM, incluyendo:
    
    ✅ Streaming de datos médicos en tiempo real
    ✅ Monitoreo simultáneo de múltiples pacientes
    ✅ Detección automática de anomalías y alertas
    ✅ Procesamiento de señales ECG y EEG
    ✅ Dashboard en tiempo real
    ✅ Comunicación WebSocket bidireccional
    ✅ Manejo de dispositivos médicos
    
    Presiona Ctrl+C para detener la demostración en cualquier momento.
    """)
    
    demo = MedicalRealtimeDemo()
    
    try:
        # Inicializar servicios
        await demo.initialize()
        
        # Configurar pacientes
        await demo.setup_patients()
        
        # Iniciar simulación de datos
        await demo.start_data_simulation()
        
        # Ejecutar demostración
        await demo.run_demo(duration_minutes=5)
        
        # Mostrar resumen final
        logger.info("📋 === RESUMEN FINAL ===")
        realtime_stats = await demo.realtime_service.get_service_statistics()
        alert_stats = demo.alert_handler.get_summary()
        
        logger.info("✅ Demostración completada exitosamente")
        logger.info(f"📊 Total puntos procesados: {realtime_stats['total_data_points']}")
        logger.info(f"🚨 Total alertas generadas: {alert_stats['total_alerts']}")
        logger.info(f"🆘 Alertas críticas: {alert_stats['critical_alerts']}")
        logger.info(f"⚡ Latencia promedio final: {realtime_stats['average_latency_ms']:.1f}ms")
        
    except Exception as e:
        logger.error(f"❌ Error en la demostración: {e}")
        raise
    
    finally:
        await demo.cleanup()

# =====================================================================================
# PUNTO DE ENTRADA
# =====================================================================================

if __name__ == "__main__":
    # Configurar logging para la demostración
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('medical_realtime_demo.log')
        ]
    )
    
    # Ejecutar demostración
    asyncio.run(run_medical_realtime_demo())
