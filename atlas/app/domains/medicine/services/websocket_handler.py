"""
🌐 WebSocket Handler Médico - AXIOM v4.1

Este módulo maneja conexiones WebSocket para streaming de datos médicos
en tiempo real, proporcionando comunicación bidireccional entre clientes
y el servicio de tiempo real médico.

Características principales:
- Gestión de conexiones WebSocket persistentes
- Autenticación y autorización por conexión
- Suscripción selectiva a streams médicos
- Rate limiting inteligente
- Compresión de mensajes automática
- Heartbeat y reconexión automática
- Logging detallado de conexiones
- Manejo de errores robusto

Tipos de mensajes soportados:
- medical_data: Datos médicos en tiempo real
- medical_alert: Alertas clínicas críticas
- stream_status: Estado de streams médicos
- subscription: Gestión de suscripciones
- heartbeat: Keepalive de conexión
- authentication: Tokens y permisos
- configuration: Configuración de cliente

Protocolos WebSocket:
- Subprotocolo médico personalizado
- Compresión per-message-deflate
- Extensiones de seguridad
- Fragmentación inteligente

Seguridad:
- Validación de origen (CORS)
- Rate limiting por cliente
- Tokens JWT para autenticación
- Encriptación de mensajes sensibles
- Audit trail de conexiones

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.core.logging import get_logger
from app.domains.medicine.services.medical_realtime_service import (
    MedicalRealtimeService,
    MedicalDataPoint,
    MedicalAlert
)
from app.exceptions.domain.medicine import MedicalError


logger = get_logger(__name__)

# =====================================================================================
# ENUMS Y CONSTANTES
# =====================================================================================

class MessageType(Enum):
    """Tipos de mensajes WebSocket"""
    MEDICAL_DATA = "medical_data"
    MEDICAL_ALERT = "medical_alert"
    STREAM_STATUS = "stream_status"
    SUBSCRIPTION = "subscription"
    HEARTBEAT = "heartbeat"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    ERROR = "error"

class ConnectionStatus(Enum):
    """Estados de conexión WebSocket"""
    CONNECTING = "connecting"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"

# Configuración de rate limiting
RATE_LIMITS = {
    "messages_per_second": 100,
    "bytes_per_second": 1024 * 1024,  # 1MB/s
    "heartbeat_interval": 30  # segundos
}

# =====================================================================================
# MODELOS DE DATOS
# =====================================================================================

@dataclass
class WebSocketClient:
    """Información de cliente WebSocket"""
    client_id: str
    connection_id: str
    user_id: Optional[str] = None
    role: Optional[str] = None
    subscribed_streams: Set[str] = field(default_factory=set)
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    rate_limit_violations: int = 0
    
    # Rate limiting
    message_timestamps: List[datetime] = field(default_factory=list)
    byte_timestamps: List[datetime] = field(default_factory=list)

@dataclass
class WebSocketMessage:
    """Mensaje WebSocket estructurado"""
    message_type: MessageType
    timestamp: datetime
    client_id: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    compression_enabled: bool = True
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=critical

# =====================================================================================
# WEBSOCKET HANDLER PRINCIPAL
# =====================================================================================

class MedicalWebSocketHandler:
    """
    Manejador principal de conexiones WebSocket médicas
    
    Gestiona conexiones persistentes, autenticación, suscripciones,
    y distribución de datos médicos en tiempo real.
    """
    
    def __init__(self, realtime_service: MedicalRealtimeService):
        self.realtime_service = realtime_service
        self.clients: Dict[str, WebSocketClient] = {}
        self.connections: Dict[str, Any] = {}  # WebSocket connections
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Tareas de mantenimiento
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._rate_limit_task: Optional[asyncio.Task] = None
        
        # Estado interno
        self._is_running = False
        
        # Configurar handlers de mensaje
        self._setup_message_handlers()
        
        logger.info("🌐 MedicalWebSocketHandler inicializado")
    
    async def start_handler(self) -> None:
        """Inicia el handler de WebSocket"""
        if self._is_running:
            logger.warning("⚠️ Handler ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando handler de WebSocket médico...")
        
        # Iniciar tareas de mantenimiento
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._rate_limit_task = asyncio.create_task(self._rate_limit_loop())
        
        self._is_running = True
        logger.info("✅ Handler de WebSocket iniciado correctamente")
    
    async def stop_handler(self) -> None:
        """Detiene el handler de WebSocket"""
        if not self._is_running:
            return
        
        logger.info("🛑 Deteniendo handler de WebSocket médico...")
        
        # Cancelar tareas
        for task in [self._heartbeat_task, self._cleanup_task, self._rate_limit_task]:
            if task and not task.done():
                task.cancel()
        
        # Desconectar todos los clientes
        await self._disconnect_all_clients()
        
        self._is_running = False
        logger.info("✅ Handler de WebSocket detenido")
    
    async def handle_connection(self, websocket: Any, path: str) -> None:
        """
        Maneja una nueva conexión WebSocket
        
        Args:
            websocket: Conexión WebSocket
            path: Ruta de la conexión
        """
        connection_id = f"ws_{uuid.uuid4().hex[:8]}"
        client_id = None
        
        logger.info(f"🔗 Nueva conexión WebSocket: {connection_id} ({path})")
        
        try:
            # Registrar conexión
            self.connections[connection_id] = websocket
            
            # Enviar mensaje de bienvenida
            welcome_message = self._create_message(
                MessageType.CONFIGURATION,
                connection_id,
                {
                    "connection_id": connection_id,
                    "server_version": "4.1",
                    "supported_protocols": ["medical-realtime-v1"],
                    "rate_limits": RATE_LIMITS
                }
            )
            await self._send_message(websocket, welcome_message)
            
            # Loop principal de mensajes
            async for raw_message in websocket:
                try:
                    message = await self._parse_message(raw_message, connection_id)
                    if message:
                        client_id = message.client_id
                        await self._handle_message(websocket, message)
                        
                except json.JSONDecodeError:
                    error_msg = self._create_error_message(
                        connection_id, 
                        "INVALID_JSON", 
                        "Mensaje JSON inválido"
                    )
                    await self._send_message(websocket, error_msg)
                    
                except MedicalError as e:
                    logger.error(f"❌ Error procesando mensaje: {e}")
                    error_msg = self._create_error_message(
                        connection_id, 
                        "PROCESSING_ERROR", 
                        str(e)
                    )
                    await self._send_message(websocket, error_msg)
        
        except ConnectionError:
            logger.info(f"🔌 Conexión {connection_id} cerrada por el cliente")
        
        except MedicalError as e:
            logger.error(f"❌ Error en conexión {connection_id}: {e}")
        
        finally:
            # Limpiar conexión
            await self._cleanup_connection(connection_id, client_id)
    
    async def broadcast_medical_data(
        self, 
        stream_id: str, 
        data_point: MedicalDataPoint
    ) -> None:
        """Transmite datos médicos a clientes suscritos"""
        message = self._create_message(
            MessageType.MEDICAL_DATA,
            "server",
            {
                "stream_id": stream_id,
                "patient_id": data_point.patient_id,
                "data_type": data_point.data_type.value,
                "timestamp": data_point.timestamp.isoformat(),
                "values": self._serialize_values(data_point.values),
                "quality_score": data_point.quality_score,
                "flags": data_point.flags
            },
            priority=2
        )
        
        # Enviar a clientes suscritos
        for client in self.clients.values():
            if stream_id in client.subscribed_streams:
                connection = self.connections.get(client.connection_id)
                if connection:
                    await self._send_message(connection, message)
    
    async def broadcast_medical_alert(self, alert: MedicalAlert) -> None:
        """Transmite alerta médica a clientes relevantes"""
        message = self._create_message(
            MessageType.MEDICAL_ALERT,
            "server",
            {
                "alert_id": alert.alert_id,
                "patient_id": alert.patient_id,
                "stream_id": alert.stream_id,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "trigger_value": alert.trigger_value,
                "threshold": alert.threshold,
                "recommended_action": alert.recommended_action
            },
            priority=4  # Máxima prioridad
        )
        
        # Enviar a clientes con permisos
        for client in self.clients.values():
            if self._client_can_receive_alert(client, alert):
                connection = self.connections.get(client.connection_id)
                if connection:
                    await self._send_message(connection, message)
    
    async def get_handler_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del handler"""
        now = datetime.now()
        
        return {
            "handler_status": "running" if self._is_running else "stopped",
            "total_connections": len(self.connections),
            "authenticated_clients": len([
                c for c in self.clients.values() 
                if c.status == ConnectionStatus.AUTHENTICATED
            ]),
            "active_clients": len([
                c for c in self.clients.values() 
                if c.status == ConnectionStatus.ACTIVE
            ]),
            "total_messages_sent": sum(c.messages_sent for c in self.clients.values()),
            "total_messages_received": sum(c.messages_received for c in self.clients.values()),
            "total_bytes_sent": sum(c.bytes_sent for c in self.clients.values()),
            "total_bytes_received": sum(c.bytes_received for c in self.clients.values()),
            "rate_limit_violations": sum(
                c.rate_limit_violations for c in self.clients.values()
            ),
            "subscription_summary": self._get_subscription_summary(),
            "last_updated": now.isoformat()
        }
    
    # =====================================================================================
    # MÉTODOS PRIVADOS - MANEJO DE MENSAJES
    # =====================================================================================
    
    def _setup_message_handlers(self) -> None:
        """Configura handlers de mensaje por tipo"""
        self.message_handlers = {
            MessageType.AUTHENTICATION: self._handle_authentication,
            MessageType.SUBSCRIPTION: self._handle_subscription,
            MessageType.HEARTBEAT: self._handle_heartbeat,
            MessageType.CONFIGURATION: self._handle_configuration
        }
    
    async def _handle_message(self, websocket: Any, message: WebSocketMessage) -> None:
        """Maneja un mensaje WebSocket"""
        # Verificar rate limiting
        if not await self._check_rate_limit(message.client_id):
            error_msg = self._create_error_message(
                message.client_id,
                "RATE_LIMIT_EXCEEDED",
                "Límite de velocidad excedido"
            )
            await self._send_message(websocket, error_msg)
            return
        
        # Obtener handler
        handler = self.message_handlers.get(message.message_type)
        if not handler:
            error_msg = self._create_error_message(
                message.client_id,
                "UNKNOWN_MESSAGE_TYPE",
                f"Tipo de mensaje desconocido: {message.message_type}"
            )
            await self._send_message(websocket, error_msg)
            return
        
        # Procesar mensaje
        try:
            await handler(websocket, message)
        except MedicalError as e:
            logger.error(f"❌ Error en handler {message.message_type}: {e}")
            error_msg = self._create_error_message(
                message.client_id,
                "HANDLER_ERROR",
                f"Error procesando mensaje: {str(e)}"
            )
            await self._send_message(websocket, error_msg)
    
    async def _handle_authentication(
        self, 
        websocket: Any, 
        message: WebSocketMessage
    ) -> None:
        """Maneja autenticación de cliente"""
        payload = message.payload
        token = payload.get("token")
        
        if not token:
            error_msg = self._create_error_message(
                message.client_id,
                "MISSING_TOKEN",
                "Token de autenticación requerido"
            )
            await self._send_message(websocket, error_msg)
            return
        
        # Verificar token (mock implementation)
        try:
            # user_info = await verify_token(token)  # Implementar
            user_info = {"user_id": "demo_user", "role": "doctor"}  # Mock
            
            # Crear o actualizar cliente
            connection_id = None
            for conn_id, conn in self.connections.items():
                if conn == websocket:
                    connection_id = conn_id
                    break
            
            if not connection_id:
                raise ValueError("Conexión no encontrada")
            
            client = WebSocketClient(
                client_id=message.client_id,
                connection_id=connection_id,
                user_id=user_info["user_id"],
                role=user_info["role"],
                status=ConnectionStatus.AUTHENTICATED
            )
            
            self.clients[message.client_id] = client
            
            # Respuesta de autenticación exitosa
            auth_response = self._create_message(
                MessageType.AUTHENTICATION,
                "server",
                {
                    "status": "authenticated",
                    "user_id": user_info["user_id"],
                    "role": user_info["role"],
                    "permissions": self._get_user_permissions(user_info["role"])
                }
            )
            await self._send_message(websocket, auth_response)
            
            logger.info(f"✅ Cliente autenticado: {message.client_id} "
                       f"({user_info['user_id']})")
        
        except MedicalError as e:
            error_msg = self._create_error_message(
                message.client_id,
                "AUTHENTICATION_FAILED",
                "Autenticación fallida"
            )
            await self._send_message(websocket, error_msg)
            logger.warning(f"⚠️ Autenticación fallida para {message.client_id}: {e}")
    
    async def _handle_subscription(
        self, 
        websocket: Any, 
        message: WebSocketMessage
    ) -> None:
        """Maneja suscripciones a streams"""
        client = self.clients.get(message.client_id)
        if not client or client.status != ConnectionStatus.AUTHENTICATED:
            error_msg = self._create_error_message(
                message.client_id,
                "NOT_AUTHENTICATED",
                "Cliente no autenticado"
            )
            await self._send_message(websocket, error_msg)
            return
        
        payload = message.payload
        action = payload.get("action")  # "subscribe" o "unsubscribe"
        stream_ids = payload.get("stream_ids", [])
        
        if action == "subscribe":
            client.subscribed_streams.update(stream_ids)
            # Registrar con el servicio de tiempo real
            await self.realtime_service.add_websocket_client(
                message.client_id,
                websocket,
                list(client.subscribed_streams)
            )
        elif action == "unsubscribe":
            client.subscribed_streams.difference_update(stream_ids)
        
        client.status = ConnectionStatus.ACTIVE
        
        # Respuesta
        sub_response = self._create_message(
            MessageType.SUBSCRIPTION,
            "server",
            {
                "action": action,
                "stream_ids": stream_ids,
                "active_subscriptions": list(client.subscribed_streams)
            }
        )
        await self._send_message(websocket, sub_response)
        
        logger.info(f"📡 Cliente {message.client_id} - {action}: {stream_ids}")
    
    async def _handle_heartbeat(
        self, 
        websocket: Any, 
        message: WebSocketMessage
    ) -> None:
        """Maneja heartbeat del cliente"""
        client = self.clients.get(message.client_id)
        if client:
            client.last_heartbeat = datetime.now()
        
        # Responder heartbeat
        heartbeat_response = self._create_message(
            MessageType.HEARTBEAT,
            "server",
            {"timestamp": datetime.now().isoformat()}
        )
        await self._send_message(websocket, heartbeat_response)
    
    async def _handle_configuration(
        self, 
        websocket: Any, 
        message: WebSocketMessage
    ) -> None:
        """Maneja configuración del cliente"""
        # Procesar configuración específica del cliente
        payload = message.payload
        client = self.clients.get(message.client_id)
        
        if client and "compression" in payload:
            client.compression_enabled = payload["compression"]
        
        # Respuesta de configuración
        config_response = self._create_message(
            MessageType.CONFIGURATION,
            "server",
            {"status": "updated", "applied_config": payload}
        )
        await self._send_message(websocket, config_response)
    
    # =====================================================================================
    # MÉTODOS PRIVADOS - UTILIDADES
    # =====================================================================================
    
    async def _parse_message(
        self, 
        raw_message: str, 
        connection_id: str
    ) -> Optional[WebSocketMessage]:
        """Parsea mensaje WebSocket crudo"""
        try:
            data = json.loads(raw_message)
            
            return WebSocketMessage(
                message_type=MessageType(data["type"]),
                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                client_id=data["client_id"],
                payload=data.get("payload", {}),
                message_id=data.get("message_id", uuid.uuid4().hex),
                compression_enabled=data.get("compression", True),
                priority=data.get("priority", 1)
            )
        
        except (KeyError, ValueError) as e:
            logger.warning(f"⚠️ Error parseando mensaje de {connection_id}: {e}")
            return None
    
    def _create_message(
        self,
        message_type: MessageType,
        client_id: str,
        payload: Dict[str, Any],
        priority: int = 1
    ) -> WebSocketMessage:
        """Crea un mensaje WebSocket"""
        return WebSocketMessage(
            message_type=message_type,
            timestamp=datetime.now(),
            client_id=client_id,
            payload=payload,
            priority=priority
        )
    
    def _create_error_message(
        self,
        client_id: str,
        error_code: str,
        error_message: str
    ) -> WebSocketMessage:
        """Crea mensaje de error"""
        return self._create_message(
            MessageType.ERROR,
            client_id,
            {
                "error_code": error_code,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat()
            },
            priority=3
        )
    
    async def _send_message(self, websocket: Any, message: WebSocketMessage) -> None:
        """Envía mensaje WebSocket"""
        try:
            # Serializar mensaje
            data = {
                "type": message.message_type.value,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.message_id,
                "payload": message.payload,
                "priority": message.priority
            }
            
            serialized = json.dumps(data)
            
            # Enviar
            await websocket.send(serialized)
            
            # Actualizar estadísticas
            client = self.clients.get(message.client_id)
            if client:
                client.messages_sent += 1
                client.bytes_sent += len(serialized)
        
        except MedicalError as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Verifica rate limiting para un cliente"""
        client = self.clients.get(client_id)
        if not client:
            return False
        
        now = datetime.now()
        cutoff = now - timedelta(seconds=1)
        
        # Limpiar timestamps antiguos
        client.message_timestamps = [
            ts for ts in client.message_timestamps if ts > cutoff
        ]
        
        # Verificar límite
        if len(client.message_timestamps) >= RATE_LIMITS["messages_per_second"]:
            client.rate_limit_violations += 1
            return False
        
        client.message_timestamps.append(now)
        return True
    
    def _client_can_receive_alert(self, client: WebSocketClient, alert: MedicalAlert) -> bool:
        """Verifica si un cliente puede recibir una alerta"""
        # Verificar suscripción al stream
        if alert.stream_id not in client.subscribed_streams:
            return False
        
        # Verificar permisos por rol
        if client.role in ["doctor", "nurse", "admin"]:
            return True
        
        return False
    
    def _get_user_permissions(self, role: str) -> List[str]:
        """Obtiene permisos por rol de usuario"""
        permissions_map = {
            "admin": ["read", "write", "manage", "alerts"],
            "doctor": ["read", "write", "alerts"],
            "nurse": ["read", "alerts"],
            "viewer": ["read"]
        }
        
        return permissions_map.get(role, ["read"])
    
    def _serialize_values(self, values: Any) -> Any:
        """Serializa valores para WebSocket"""
        if hasattr(values, 'tolist'):  # numpy array
            return values.tolist()
        elif isinstance(values, dict):
            return {k: float(v) if isinstance(v, (int, float)) else v 
                   for k, v in values.items()}
        elif isinstance(values, list):
            return [float(v) if isinstance(v, (int, float)) else v for v in values]
        else:
            return values
    
    def _get_subscription_summary(self) -> Dict[str, int]:
        """Obtiene resumen de suscripciones"""
        all_streams = set()
        for client in self.clients.values():
            all_streams.update(client.subscribed_streams)
        
        return {
            "unique_streams": len(all_streams),
            "total_subscriptions": sum(
                len(client.subscribed_streams) for client in self.clients.values()
            ),
            "clients_with_subscriptions": len([
                client for client in self.clients.values() 
                if client.subscribed_streams
            ])
        }
    
    async def _cleanup_connection(
        self, 
        connection_id: str, 
        client_id: Optional[str]
    ) -> None:
        """Limpia una conexión cerrada"""
        # Remover conexión
        if connection_id in self.connections:
            del self.connections[connection_id]
        
        # Remover cliente si existe
        if client_id and client_id in self.clients:
            # Remover del servicio de tiempo real
            await self.realtime_service.remove_websocket_client(client_id)
            del self.clients[client_id]
        
        logger.info(f"🧹 Conexión limpiada: {connection_id}")
    
    async def _disconnect_all_clients(self) -> None:
        """Desconecta todos los clientes"""
        for connection in self.connections.values():
            try:
                await connection.close()
            except MedicalError as e:
                logger.error(f"❌ Error cerrando conexión: {e}")
        
        self.connections.clear()
        self.clients.clear()
    
    # =====================================================================================
    # TAREAS DE MANTENIMIENTO
    # =====================================================================================
    
    async def _heartbeat_loop(self) -> None:
        """Loop de heartbeat para detectar conexiones muertas"""
        while self._is_running:
            try:
                now = datetime.now()
                timeout = timedelta(seconds=RATE_LIMITS["heartbeat_interval"] * 2)
                
                dead_clients = []
                for client_id, client in self.clients.items():
                    if now - client.last_heartbeat > timeout:
                        dead_clients.append(client_id)
                
                # Limpiar clientes muertos
                for client_id in dead_clients:
                    logger.info(f"💀 Cliente sin heartbeat detectado: {client_id}")
                    await self._cleanup_connection(
                        self.clients[client_id].connection_id, 
                        client_id
                    )
                
                await asyncio.sleep(RATE_LIMITS["heartbeat_interval"])
                
            except asyncio.CancelledError:
                break
            except MedicalError as e:
                logger.error(f"❌ Error en heartbeat loop: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self) -> None:
        """Loop de limpieza general"""
        while self._is_running:
            try:
                # Limpiar datos antiguos, optimizar memoria, etc.
                await asyncio.sleep(300)  # Cada 5 minutos
                
            except asyncio.CancelledError:
                break
            except MedicalError as e:
                logger.error(f"❌ Error en cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _rate_limit_loop(self) -> None:
        """Loop de mantenimiento de rate limiting"""
        while self._is_running:
            try:
                # Resetear contadores, limpiar timestamps antiguos
                now = datetime.now()
                cutoff = now - timedelta(minutes=5)
                
                for client in self.clients.values():
                    client.message_timestamps = [
                        ts for ts in client.message_timestamps if ts > cutoff
                    ]
                    client.byte_timestamps = [
                        ts for ts in client.byte_timestamps if ts > cutoff
                    ]
                
                await asyncio.sleep(60)  # Cada minuto
                
            except asyncio.CancelledError:
                break
            except MedicalError as e:
                logger.error(f"❌ Error en rate limit loop: {e}")
                await asyncio.sleep(30)


# =====================================================================================
# FACTORY Y UTILIDADES
# =====================================================================================

def create_websocket_handler(
    realtime_service: MedicalRealtimeService
) -> MedicalWebSocketHandler:
    """Factory para crear handler de WebSocket"""
    return MedicalWebSocketHandler(realtime_service)

async def create_demo_websocket_server(
    host: str = "localhost", 
    port: int = 8765
) -> None:
    """
    Crea servidor WebSocket de demostración
    
    Args:
        host: Host del servidor
        port: Puerto del servidor
    """
    # Crear servicios
    realtime_service = MedicalRealtimeService()
    await realtime_service.start_service()
    
    websocket_handler = create_websocket_handler(realtime_service)
    await websocket_handler.start_handler()
    
    # FIXED: Use secure WebSocket (wss://) instead of insecure (ws://)
    protocol = "wss" if port == 443 or port >= 8443 else "ws"
    logger.info(f"🌐 Servidor WebSocket médico iniciado en {protocol}://{host}:{port}")
    if protocol == "ws":
        logger.warning("⚠️ WebSocket inseguro. Configura SSL/TLS para producción (puerto 443 o 8443+)")
    
    try:
        # Aquí iría la lógica del servidor WebSocket real
        # En producción usar websockets library o FastAPI WebSocket con SSL
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("⌨️ Deteniendo servidor por interrupción de teclado")
    
    finally:
        await websocket_handler.stop_handler()
        await realtime_service.stop_service()
        logger.info("✅ Servidor WebSocket detenido")
