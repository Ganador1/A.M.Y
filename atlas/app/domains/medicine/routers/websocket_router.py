"""
🌐 Router WebSocket Médico - AXIOM v4.1

Este módulo proporciona endpoints WebSocket para conexiones de tiempo real
en el dominio médico, integrando con FastAPI WebSockets y el handler
especializado de WebSocket médico.

Características principales:
- Endpoints WebSocket para streaming médico
- Integración con MedicalRealtimeService
- Manejo automático de conexiones y desconexiones
- Routing dinámico basado en paths
- Middleware de autenticación WebSocket
- Rate limiting por conexión
- Logging detallado de conexiones
- Manejo de errores robusto

Endpoints principales:
- /ws/medical/stream/{patient_id}: Stream de datos de paciente específico
- /ws/medical/alerts: Stream de alertas médicas globales
- /ws/medical/monitor/{device_id}: Stream de dispositivo específico
- /ws/medical/dashboard: Dashboard en tiempo real multi-stream

Protocolos soportados:
- WebSocket estándar (RFC 6455)
- Subprotocolo médico personalizado
- Server-Sent Events como fallback
- Compresión automática de mensajes

Seguridad:
- Validación de tokens JWT
- Autorización basada en roles
- Rate limiting inteligente
- CORS configurado para WebSockets
- Logging de audit trail completo

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse

from app.core.logging import get_logger
from app.domains.medicine.services.medical_realtime_service import (
from app.exceptions.domain.medicine import MedicalError
    MedicalRealtimeService,
    create_medical_realtime_service,
    StreamType,
    ProcessingMode
)
from app.domains.medicine.services.websocket_handler import (
    MedicalWebSocketHandler,
    create_websocket_handler
)

logger = get_logger(__name__)

# =====================================================================================
# CONFIGURACIÓN DEL ROUTER
# =====================================================================================

# Router principal para WebSockets médicos
medical_websocket_router = APIRouter(
    prefix="/ws/medical",
    tags=["Medical WebSockets"],
    responses={
        404: {"description": "WebSocket endpoint not found"},
        403: {"description": "Access forbidden"},
        429: {"description": "Rate limit exceeded"}
    }
)

# Servicios globales (en producción usar dependency injection)
_realtime_service: Optional[MedicalRealtimeService] = None
_websocket_handler: Optional[MedicalWebSocketHandler] = None

# =====================================================================================
# DEPENDENCY PROVIDERS
# =====================================================================================

async def get_realtime_service() -> MedicalRealtimeService:
    """Obtiene instancia del servicio de tiempo real"""
    global _realtime_service
    
    if _realtime_service is None:
        _realtime_service = create_medical_realtime_service()
        await _realtime_service.start_service()
        logger.info("🚀 MedicalRealtimeService inicializado para WebSocket router")
    
    return _realtime_service

async def get_websocket_handler() -> MedicalWebSocketHandler:
    """Obtiene instancia del handler de WebSocket"""
    global _websocket_handler
    
    if _websocket_handler is None:
        realtime_service = await get_realtime_service()
        _websocket_handler = create_websocket_handler(realtime_service)
        await _websocket_handler.start_handler()
        logger.info("🌐 MedicalWebSocketHandler inicializado para router")
    
    return _websocket_handler

# =====================================================================================
# WEBSOCKET ENDPOINTS
# =====================================================================================

@medical_websocket_router.websocket("/stream/{patient_id}")
async def websocket_patient_stream(
    websocket: WebSocket,
    patient_id: str,
        stream_types: Optional[str] = "vital_signs",  # Query param con tipos separados por coma
    processing_mode: Optional[str] = "filtered"
):
    """
    WebSocket para streaming de datos de un paciente específico
    
    Args:
        websocket: Conexión WebSocket
        patient_id: ID del paciente
        stream_types: Tipos de stream separados por coma
        processing_mode: Modo de procesamiento (raw, filtered, analyzed)
    
    Ejemplo de uso:
        ws://localhost:8000/ws/medical/stream/PATIENT_123?stream_types=ecg,vital_signs&processing_mode=analyzed
    """
    handler = await get_websocket_handler()
    
    logger.info(f"🔗 Nueva conexión WebSocket para paciente: {patient_id}")
    
    await websocket.accept()
    
    try:
        # Parsear parámetros
        if stream_types:
            requested_stream_types = [
                StreamType(s.strip()) for s in stream_types.split(",")
                if s.strip() in [st.value for st in StreamType]
            ]
        else:
            requested_stream_types = [StreamType.VITAL_SIGNS]
        processing_mode_enum = ProcessingMode(processing_mode)
        
        # Crear streams para el paciente
        realtime_service = await get_realtime_service()
        created_streams = []
        
        for stream_type in requested_stream_types:
            stream_id = await realtime_service.create_medical_stream(
                patient_id=patient_id,
                stream_type=stream_type,
                device_id=f"DEVICE_{patient_id}_{stream_type.value}",
                processing_mode=processing_mode_enum
            )
            created_streams.append(stream_id)
            logger.info(f"📊 Stream creado: {stream_id} para {patient_id}")
        
        # Configurar conexión WebSocket
        connection_path = f"/stream/{patient_id}"
        await handler.handle_connection(websocket, connection_path)
        
    except WebSocketDisconnect:
        logger.info(f"🔌 Cliente WebSocket desconectado: paciente {patient_id}")
    
    except ValueError as e:
        logger.error(f"❌ Parámetros inválidos para {patient_id}: {e}")
        await websocket.close(code=1003, reason="Invalid parameters")
    
    except MedicalError as e:
        logger.error(f"❌ Error en WebSocket para {patient_id}: {e}")
        await websocket.close(code=1011, reason="Internal server error")
    
    finally:
        # Limpiar streams creados
        if 'created_streams' in locals() and 'realtime_service' in locals():
            for stream_id in created_streams:
                try:
                    await realtime_service.stop_stream(stream_id)
                    logger.info(f"🛑 Stream limpiado: {stream_id}")
                except MedicalError as e:
                    logger.error(f"❌ Error limpiando stream {stream_id}: {e}")

@medical_websocket_router.websocket("/alerts")
async def websocket_medical_alerts(websocket: WebSocket):
    """
    WebSocket para streaming de alertas médicas globales
    
    Recibe todas las alertas médicas del sistema en tiempo real,
    filtradas según los permisos del usuario autenticado.
    """
    handler = await get_websocket_handler()
    
    logger.info("🚨 Nueva conexión WebSocket para alertas médicas")
    
    await websocket.accept()
    
    try:
        await handler.handle_connection(websocket, "/alerts")
    
    except WebSocketDisconnect:
        logger.info("🔌 Cliente de alertas médicas desconectado")
    
    except MedicalError as e:
        logger.error(f"❌ Error en WebSocket de alertas: {e}")
        await websocket.close(code=1011, reason="Internal server error")

@medical_websocket_router.websocket("/monitor/{device_id}")
async def websocket_device_monitor(
    websocket: WebSocket,
    device_id: str,
    sampling_rate: Optional[float] = None
):
    """
    WebSocket para monitoreo de dispositivo médico específico
    
    Args:
        websocket: Conexión WebSocket
        device_id: ID del dispositivo médico
        sampling_rate: Frecuencia de muestreo personalizada
    """
    handler = await get_websocket_handler()
    
    logger.info(f"📟 Nueva conexión WebSocket para dispositivo: {device_id}")
    
    await websocket.accept()
    
    try:
        # Configurar monitoreo de dispositivo
        # En un sistema real, aquí se configuraría la conexión con el dispositivo
        # y se crearían streams específicos basados en el tipo de dispositivo
        
        await handler.handle_connection(websocket, f"/monitor/{device_id}")
    
    except WebSocketDisconnect:
        logger.info(f"🔌 Monitor de dispositivo {device_id} desconectado")
    
    except MedicalError as e:
        logger.error(f"❌ Error en monitor de dispositivo {device_id}: {e}")
        await websocket.close(code=1011, reason="Internal server error")

@medical_websocket_router.websocket("/dashboard")
async def websocket_medical_dashboard(websocket: WebSocket):
    """
    WebSocket para dashboard médico en tiempo real
    
    Proporciona datos agregados y estadísticas en tiempo real
    para interfaces de dashboard médico.
    """
    handler = await get_websocket_handler()
    
    logger.info("📊 Nueva conexión WebSocket para dashboard médico")
    
    await websocket.accept()
    
    try:
        # Configurar dashboard con datos agregados
        await handler.handle_connection(websocket, "/dashboard")
        
        # Enviar estadísticas periódicas
        while True:
            realtime_service = await get_realtime_service()
            statistics = await realtime_service.get_service_statistics()
            handler_stats = await handler.get_handler_statistics()
            
            dashboard_data = {
                "type": "dashboard_update",
                "timestamp": datetime.now().isoformat(),
                "realtime_service": statistics,
                "websocket_handler": handler_stats
            }
            
            await websocket.send_json(dashboard_data)
            await asyncio.sleep(5)  # Actualizar cada 5 segundos
    
    except WebSocketDisconnect:
        logger.info("🔌 Dashboard médico desconectado")
    
    except MedicalError as e:
        logger.error(f"❌ Error en dashboard médico: {e}")
        await websocket.close(code=1011, reason="Internal server error")

# =====================================================================================
# ENDPOINTS HTTP DE SOPORTE
# =====================================================================================

@medical_websocket_router.get("/status")
async def get_websocket_status():
    """
    Obtiene el estado actual del servicio WebSocket
    
    Returns:
        Estado detallado de servicios WebSocket y tiempo real
    """
    try:
        # Obtener estadísticas de ambos servicios
        realtime_service = await get_realtime_service()
        websocket_handler = await get_websocket_handler()
        
        realtime_stats = await realtime_service.get_service_statistics()
        websocket_stats = await websocket_handler.get_handler_statistics()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "realtime_service": realtime_stats,
                "websocket_handler": websocket_stats
            },
            "endpoints": {
                "patient_stream": "/ws/medical/stream/{patient_id}",
                "alerts": "/ws/medical/alerts",
                "device_monitor": "/ws/medical/monitor/{device_id}",
                "dashboard": "/ws/medical/dashboard"
            }
        }
    
    except MedicalError as e:
        logger.error(f"❌ Error obteniendo estado WebSocket: {e}")
        raise HTTPException(status_code=500, detail="Error getting WebSocket status")

@medical_websocket_router.get("/demo")
async def get_websocket_demo() -> HTMLResponse:
    """
    Página de demostración para conexiones WebSocket médicas
    
    Returns:
        Página HTML con cliente WebSocket de prueba
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AXIOM Medical WebSocket Demo</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
                background: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .connection-status {
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .connected { background: #d4edda; color: #155724; }
            .disconnected { background: #f8d7da; color: #721c24; }
            .message-log {
                height: 300px;
                overflow-y: scroll;
                border: 1px solid #ddd;
                padding: 10px;
                background: #f8f9fa;
                font-family: monospace;
                font-size: 12px;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            input, select {
                padding: 8px;
                margin: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 AXIOM Medical WebSocket Demo</h1>
            
            <div class="connection-section">
                <h3>Conexión</h3>
                <div id="status" class="connection-status disconnected">Desconectado</div>
                
                <div>
                    <label>Endpoint:</label>
                    <select id="endpoint">
                        <option value="/ws/medical/stream/PATIENT_DEMO">Patient Stream</option>
                        <option value="/ws/medical/alerts">Medical Alerts</option>
                        <option value="/ws/medical/monitor/DEVICE_DEMO">Device Monitor</option>
                        <option value="/ws/medical/dashboard">Dashboard</option>
                    </select>
                    
                    <label>Patient ID:</label>
                    <input type="text" id="patientId" value="PATIENT_DEMO" placeholder="Patient ID">
                    
                    <button id="connectBtn" onclick="connect()">Conectar</button>
                    <button id="disconnectBtn" onclick="disconnect()" disabled>Desconectar</button>
                </div>
            </div>
            
            <div class="controls-section">
                <h3>Controles</h3>
                <button onclick="sendHeartbeat()" disabled id="heartbeatBtn">Enviar Heartbeat</button>
                <button onclick="subscribe()" disabled id="subscribeBtn">Suscribirse</button>
                <button onclick="unsubscribe()" disabled id="unsubscribeBtn">Desuscribirse</button>
                <button onclick="clearLog()">Limpiar Log</button>
            </div>
            
            <div class="log-section">
                <h3>Log de Mensajes</h3>
                <div id="messageLog" class="message-log"></div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let clientId = 'demo_client_' + Math.random().toString(36).substr(2, 9);
            
            function log(message, type = 'info') {
                const timestamp = new Date().toLocaleTimeString();
                const logElement = document.getElementById('messageLog');
                logElement.innerHTML += `<div>[${timestamp}] ${type.toUpperCase()}: ${message}</div>`;
                logElement.scrollTop = logElement.scrollHeight;
            }
            
            function updateStatus(connected) {
                const statusElement = document.getElementById('status');
                const connectBtn = document.getElementById('connectBtn');
                const disconnectBtn = document.getElementById('disconnectBtn');
                const controlBtns = ['heartbeatBtn', 'subscribeBtn', 'unsubscribeBtn'];
                
                if (connected) {
                    statusElement.textContent = 'Conectado';
                    statusElement.className = 'connection-status connected';
                    connectBtn.disabled = true;
                    disconnectBtn.disabled = false;
                    controlBtns.forEach(id => document.getElementById(id).disabled = false);
                } else {
                    statusElement.textContent = 'Desconectado';
                    statusElement.className = 'connection-status disconnected';
                    connectBtn.disabled = false;
                    disconnectBtn.disabled = true;
                    controlBtns.forEach(id => document.getElementById(id).disabled = true);
                }
            }
            
            function connect() {
                const endpoint = document.getElementById('endpoint').value;
                const patientId = document.getElementById('patientId').value;
                
                let wsUrl = `ws://localhost:8000${endpoint}`;
                if (endpoint.includes('stream') && patientId) {
                    wsUrl = `ws://localhost:8000/ws/medical/stream/${patientId}`;
                }
                
                log(`Conectando a: ${wsUrl}`);
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    log('WebSocket conectado exitosamente', 'success');
                    updateStatus(true);
                    
                    // Enviar mensaje de autenticación
                    const authMessage = {
                        type: 'authentication',
                        client_id: clientId,
                        timestamp: new Date().toISOString(),
                        payload: {
                            token: 'demo_token_12345'  // Token de demo
                        }
                    };
                    ws.send(JSON.stringify(authMessage));
                };
                
                ws.onmessage = function(event) {
                    try {
                        const message = JSON.parse(event.data);
                        log(`Mensaje recibido: ${JSON.stringify(message, null, 2)}`, 'received');
                    } catch (e) {
                        log(`Mensaje crudo: ${event.data}`, 'received');
                    }
                };
                
                ws.onerror = function(error) {
                    log(`Error de WebSocket: ${error}`, 'error');
                };
                
                ws.onclose = function(event) {
                    log(`WebSocket cerrado. Código: ${event.code}, Razón: ${event.reason}`, 'warning');
                    updateStatus(false);
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                    log('Desconectando WebSocket...');
                }
            }
            
            function sendHeartbeat() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'heartbeat',
                        client_id: clientId,
                        timestamp: new Date().toISOString(),
                        payload: {}
                    };
                    ws.send(JSON.stringify(message));
                    log('Heartbeat enviado', 'sent');
                }
            }
            
            function subscribe() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'subscription',
                        client_id: clientId,
                        timestamp: new Date().toISOString(),
                        payload: {
                            action: 'subscribe',
                            stream_ids: ['stream_demo_1', 'stream_demo_2']
                        }
                    };
                    ws.send(JSON.stringify(message));
                    log('Suscripción enviada', 'sent');
                }
            }
            
            function unsubscribe() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'subscription',
                        client_id: clientId,
                        timestamp: new Date().toISOString(),
                        payload: {
                            action: 'unsubscribe',
                            stream_ids: ['stream_demo_1']
                        }
                    };
                    ws.send(JSON.stringify(message));
                    log('Desuscripción enviada', 'sent');
                }
            }
            
            function clearLog() {
                document.getElementById('messageLog').innerHTML = '';
            }
            
            // Auto-conectar en demo
            setTimeout(connect, 1000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# =====================================================================================
# UTILIDADES Y CLEANUP
# =====================================================================================

@medical_websocket_router.post("/simulate/{patient_id}")
async def start_data_simulation(
    patient_id: str,
    stream_type: str = "vital_signs",
    duration_seconds: int = 60
):
    """
    Inicia simulación de datos médicos para testing
    
    Args:
        patient_id: ID del paciente
        stream_type: Tipo de stream a simular
        duration_seconds: Duración de la simulación
    
    Returns:
        Confirmación de inicio de simulación
    """
    try:
        realtime_service = await get_realtime_service()
        
        # Convertir string a enum
        stream_type_enum = StreamType(stream_type)
        
        # Crear stream si no existe
        stream_id = await realtime_service.create_medical_stream(
            patient_id=patient_id,
            stream_type=stream_type_enum,
            device_id=f"SIMULATOR_{patient_id}",
            processing_mode=ProcessingMode.FILTERED
        )
        
        # Iniciar simulación en background
        asyncio.create_task(
            _simulate_data_background(
                realtime_service,
                stream_id,
                stream_type_enum,
                duration_seconds
            )
        )
        
        logger.info(f"🎯 Simulación iniciada: {stream_id} por {duration_seconds}s")
        
        return {
            "status": "simulation_started",
            "stream_id": stream_id,
            "patient_id": patient_id,
            "stream_type": stream_type,
            "duration_seconds": duration_seconds,
            "estimated_end": (datetime.now().timestamp() + duration_seconds)
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stream type: {stream_type}")
    
    except MedicalError as e:
        logger.error(f"❌ Error iniciando simulación: {e}")
        raise HTTPException(status_code=500, detail="Error starting simulation")

async def _simulate_data_background(
    realtime_service: MedicalRealtimeService,
    stream_id: str,
    stream_type: StreamType,
    duration_seconds: int
) -> None:
    """Ejecuta simulación de datos en background"""
    try:
        from app.domains.medicine.services.medical_realtime_service import simulate_medical_data_stream
        
        async for data_point in simulate_medical_data_stream(
            stream_id,
            stream_type,
            duration_seconds,
            realtime_service
        ):
            # Los datos se ingestarán automáticamente en el servicio
            pass
        
        logger.info(f"✅ Simulación completada para stream: {stream_id}")
        
    except MedicalError as e:
        logger.error(f"❌ Error en simulación background: {e}")
    
    finally:
        # Limpiar stream después de la simulación
        try:
            await realtime_service.stop_stream(stream_id)
        except MedicalError as e:
            logger.error(f"❌ Error limpiando stream de simulación: {e}")

# =====================================================================================
# CLEANUP Y SHUTDOWN
# =====================================================================================

async def cleanup_websocket_services():
    """Limpia servicios WebSocket al cerrar la aplicación"""
    global _realtime_service, _websocket_handler
    
    if _websocket_handler:
        await _websocket_handler.stop_handler()
        _websocket_handler = None
        logger.info("🧹 WebSocketHandler limpiado")
    
    if _realtime_service:
        await _realtime_service.stop_service()
        _realtime_service = None
        logger.info("🧹 MedicalRealtimeService limpiado")

# Registrar cleanup en el shutdown de la aplicación
# En main.py: app.add_event_handler("shutdown", cleanup_websocket_services)
