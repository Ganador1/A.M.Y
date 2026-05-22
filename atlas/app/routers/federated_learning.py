"""
Federated Learning Router

Router FastAPI para gestión de entrenamiento federado utilizando el framework Flower.
Proporciona endpoints REST API para coordinar el entrenamiento distribuido de modelos
de machine learning manteniendo la privacidad de los datos.

Características principales:
- Iniciar y gestionar sesiones de entrenamiento federado
- Configurar estrategias de agregación (FedAvg, FedProx)
- Monitorear progreso y métricas de entrenamiento
- Gestionar clientes federados
- Obtener resultados y estadísticas de convergencia

Endpoints disponibles:
- POST /start: Iniciar sesión de entrenamiento federado
- GET /sessions: Listar todas las sesiones
- GET /sessions/{session_id}: Obtener estado de una sesión
- GET /sessions/{session_id}/metrics: Obtener métricas detalladas
- POST /sessions/{session_id}/stop: Detener sesión activa
- GET /strategies: Listar estrategias soportadas
- POST /client-config: Generar configuración para cliente
- GET /health: Estado del servicio
- GET /examples: Ejemplos de configuración

Dependencias:
- FederatedLearningService: Servicio principal de federated learning
- flwr: Framework Flower para federated learning
- torch: Para modelos PyTorch
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.exceptions.domain.biology import BiologyError
from app.services.federated_learning_service import (
    federated_learning_service,
    FederatedConfig,
    ClientMetrics,
    FederatedResults,
)
from app.core.bootstrap_logging import logger

router = APIRouter()


# Modelos Pydantic para requests y responses
class FederatedConfigRequest(BaseModel):
    """Configuración para entrenamiento federado"""
    num_rounds: int = Field(default=10, ge=1, le=1000, description="Número de rondas de entrenamiento")
    min_fit_clients: int = Field(default=2, ge=1, description="Mínimo de clientes para entrenamiento")
    min_evaluate_clients: int = Field(default=2, ge=1, description="Mínimo de clientes para evaluación")
    min_available_clients: int = Field(default=2, ge=1, description="Mínimo de clientes disponibles")
    strategy: str = Field(default="FedAvg", description="Estrategia de agregación")
    learning_rate: float = Field(default=0.01, gt=0, description="Tasa de aprendizaje")
    batch_size: int = Field(default=32, ge=1, description="Tamaño de batch")
    local_epochs: int = Field(default=1, ge=1, description="Épocas locales por cliente")
    fraction_fit: float = Field(default=1.0, ge=0.1, le=1.0, description="Fracción de clientes para entrenamiento")
    fraction_evaluate: float = Field(default=1.0, ge=0.1, le=1.0, description="Fracción de clientes para evaluación")


class StartSessionRequest(BaseModel):
    """Request para iniciar sesión federada"""
    session_name: Optional[str] = Field(default=None, description="Nombre de la sesión")
    config: FederatedConfigRequest
    server_address: str = Field(default="localhost:8080", description="Dirección del servidor")


class ClientConfigRequest(BaseModel):
    """Request para configuración de cliente"""
    server_address: str = Field(description="Dirección del servidor federado")
    client_id: str = Field(description="ID único del cliente")
    model_configuration: Dict[str, Any] = Field(default_factory=dict, description="Configuración del modelo")


class SessionResponse(BaseModel):
    """Response con información de sesión"""
    session_id: str
    status: str
    start_time: Optional[str] = None
    server_address: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SessionMetricsResponse(BaseModel):
    """Response con métricas de sesión"""
    session_id: str
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/start", response_model=Dict[str, Any])
async def start_federated_session(request: StartSessionRequest):
    """
    Iniciar una nueva sesión de entrenamiento federado
    
    Crea y configura un servidor federado con la estrategia especificada.
    Los clientes pueden conectarse al servidor para participar en el entrenamiento.
    """
    try:
        # Generar ID único para la sesión
        session_id = request.session_name or f"fed_session_{uuid.uuid4().hex[:8]}"
        
        # Convertir request a config interno
        config = FederatedConfig(
            num_rounds=request.config.num_rounds,
            min_fit_clients=request.config.min_fit_clients,
            min_evaluate_clients=request.config.min_evaluate_clients,
            min_available_clients=request.config.min_available_clients,
            strategy=request.config.strategy,
            learning_rate=request.config.learning_rate,
            batch_size=request.config.batch_size,
            local_epochs=request.config.local_epochs,
            fraction_fit=request.config.fraction_fit,
            fraction_evaluate=request.config.fraction_evaluate
        )
        
        # Iniciar sesión federada
        result = await federated_learning_service.start_federated_server(
            session_id=session_id,
            config=config,
            server_address=request.server_address
        )
        
        if result["success"]:
            logger.info(f"Started federated session: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "server_address": request.server_address,
                "config": request.config.dict(),
                "message": "Federated learning session started successfully",
                "instructions": {
                    "next_steps": [
                        "Configure and start your federated clients",
                        "Monitor session progress via /sessions/{session_id}",
                        "Check metrics via /sessions/{session_id}/metrics"
                    ]
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"Error starting federated session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=Dict[str, Any])
async def list_sessions():
    """
    Listar todas las sesiones de entrenamiento federado
    
    Retorna información sobre sesiones activas y completadas.
    """
    try:
        sessions = federated_learning_service.list_sessions()
        return {
            "success": True,
            "sessions": sessions,
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_status(session_id: str):
    """
    Obtener estado de una sesión específica
    
    Retorna información detallada sobre el progreso y estado de la sesión.
    """
    try:
        status = federated_learning_service.get_session_status(session_id)
        
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(**status)
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/metrics", response_model=SessionMetricsResponse)
async def get_session_metrics(session_id: str):
    """
    Obtener métricas detalladas de una sesión
    
    Retorna métricas de convergencia, pérdida, precisión y estadísticas por cliente.
    """
    try:
        metrics = federated_learning_service.get_session_metrics(session_id)
        return SessionMetricsResponse(**metrics)
        
    except BiologyError as e:
        logger.error(f"Error getting session metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/stop", response_model=Dict[str, Any])
async def stop_session(session_id: str):
    """
    Detener una sesión activa de entrenamiento federado
    
    Marca la sesión para detenerse de forma segura.
    """
    try:
        result = federated_learning_service.stop_session(session_id)
        
        if result["success"]:
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session stop requested",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error stopping session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", response_model=Dict[str, Any])
async def get_supported_strategies():
    """
    Obtener lista de estrategias de agregación soportadas
    
    Retorna las estrategias disponibles para el entrenamiento federado.
    """
    try:
        strategies = federated_learning_service.get_supported_strategies()
        return {
            "success": True,
            "strategies": strategies,
            "descriptions": {
                "FedAvg": "Federated Averaging - Promedio ponderado de parámetros",
                "FedProx": "Federated Proximal - FedAvg con término de regularización proximal"
            }
        }
    except BiologyError as e:
        logger.error(f"Error getting strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/client-config", response_model=Dict[str, Any])
async def generate_client_config(request: ClientConfigRequest):
    """
    Generar configuración para cliente federado
    
    Crea la configuración necesaria para que un cliente se conecte al servidor.
    """
    try:
        config = federated_learning_service.create_client_config(
            server_address=request.server_address,
            client_id=request.client_id,
            model_config=request.model_configuration
        )
        
        return {
            "success": True,
            "client_config": config,
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"Error generating client config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Verificar estado del servicio de Federated Learning
    
    Retorna información sobre disponibilidad de dependencias y estado del servicio.
    """
    try:
        health = federated_learning_service.check_availability()
        return {
            "service": "Federated Learning",
            "status": "healthy" if health["available"] else "degraded",
            "availability": health,
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples", response_model=Dict[str, Any])
async def get_examples():
    """
    Obtener ejemplos de configuración y uso
    
    Retorna ejemplos prácticos para configurar y usar el entrenamiento federado.
    """
    return {
        "examples": {
            "basic_session": {
                "description": "Configuración básica para entrenamiento federado",
                "config": {
                    "session_name": "mnist_federated",
                    "config": {
                        "num_rounds": 10,
                        "min_fit_clients": 2,
                        "min_evaluate_clients": 2,
                        "strategy": "FedAvg",
                        "learning_rate": 0.01,
                        "batch_size": 32,
                        "local_epochs": 1
                    },
                    "server_address": "localhost:8080"
                }
            },
            "advanced_session": {
                "description": "Configuración avanzada con FedProx",
                "config": {
                    "session_name": "advanced_federated",
                    "config": {
                        "num_rounds": 50,
                        "min_fit_clients": 5,
                        "min_evaluate_clients": 3,
                        "strategy": "FedProx",
                        "learning_rate": 0.001,
                        "batch_size": 64,
                        "local_epochs": 3,
                        "fraction_fit": 0.8,
                        "fraction_evaluate": 0.5
                    },
                    "server_address": "0.0.0.0:8080"
                }
            },
            "client_example": {
                "description": "Ejemplo de configuración de cliente",
                "python_code": '''
import flwr as fl
# Optional torch import for deep learning support
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
    
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(784, 10)
        
        def forward(self, x):
            return self.fc(x.view(-1, 784))
            
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
    nn = None # type: ignore
    SimpleModel = None # type: ignore

class FlowerClient(fl.client.NumPyClient):
    def __init__(self, model, trainloader, testloader):
        self.model = model
        self.trainloader = trainloader
        self.testloader = testloader
    
    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]
    
    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)
    
    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # Entrenar modelo localmente
        # ... código de entrenamiento ...
        return self.get_parameters(config={}), len(self.trainloader), {}
    
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        # Evaluar modelo
        # ... código de evaluación ...
        return loss, len(self.testloader), {"accuracy": accuracy}

# Conectar al servidor
fl.client.start_numpy_client(
    server_address="localhost:8080",
    client=FlowerClient(model, trainloader, testloader)
)
                '''
            }
        },
        "usage_instructions": [
            "1. Instalar dependencias: pip install flwr torch",
            "2. Iniciar sesión federada con POST /start",
            "3. Configurar clientes con el código de ejemplo",
            "4. Monitorear progreso con GET /sessions/{session_id}",
            "5. Obtener métricas finales con GET /sessions/{session_id}/metrics"
        ]
    }