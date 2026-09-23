"""
Federated Learning Service

Servicio para coordinar el entrenamiento federado de modelos de machine learning
utilizando el framework Flower. Permite entrenar modelos de forma distribuida
manteniendo la privacidad de los datos y coordinando múltiples clientes.

Características principales:
- Coordinación de entrenamiento federado con múltiples clientes
- Estrategias de agregación configurables (FedAvg, FedProx, etc.)
- Soporte para diferentes tipos de modelos (PyTorch, TensorFlow)
- Métricas de evaluación distribuida
- Gestión de rondas de entrenamiento
- Configuración de hiperparámetros federados
- Monitoreo de progreso y convergencia

Dependencias:
- flwr: Framework principal de federated learning
- torch: Para modelos PyTorch
- numpy: Operaciones numéricas
- typing: Type hints
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from app.exceptions.infrastructure.database import DatabaseError

try:
    import flwr as fl
    from flwr.server import ServerConfig
    from flwr.server.strategy import FedAvg, FedProx, Strategy
    from flwr.common import Parameters, FitRes, Scalar
    FEDERATED_LEARNING_AVAILABLE = True
except ImportError as e:
    FEDERATED_LEARNING_AVAILABLE = False
    logging.warning(f"Federated learning dependencies not available: {e}")
    # Create dummy classes to avoid NameError
    class FedAvg:
        pass
    class FedProx:
        pass
    class Strategy:
        pass
    class Parameters:
        pass
    class FitRes:
        pass
    class Scalar:
        pass
    class ServerConfig:
        pass
    fl = None

from app.core.bootstrap_logging import logger
from app.types.federated_learning_service_types import (
    CheckAvailabilityResult,
    GetSessionStatusResult,
    ListSessionsResult,
    GetSessionMetricsResult,
    StopSessionResult,
)


@dataclass
class FederatedConfig:
    """Configuración para entrenamiento federado"""
    num_rounds: int = 10
    min_fit_clients: int = 2
    min_evaluate_clients: int = 2
    min_available_clients: int = 2
    strategy: str = "FedAvg"
    learning_rate: float = 0.01
    batch_size: int = 32
    local_epochs: int = 1
    fraction_fit: float = 1.0
    fraction_evaluate: float = 1.0


@dataclass
class ClientMetrics:
    """Métricas de un cliente federado"""
    client_id: str
    round_num: int
    loss: float
    accuracy: Optional[float] = None
    num_examples: int = 0
    training_time: float = 0.0
    timestamp: datetime = None


@dataclass
class FederatedResults:
    """Resultados del entrenamiento federado"""
    total_rounds: int
    final_loss: float
    final_accuracy: Optional[float]
    convergence_round: Optional[int]
    client_metrics: List[ClientMetrics]
    training_time: float
    model_parameters: Optional[Dict] = None


if FEDERATED_LEARNING_AVAILABLE:
    class CustomFedAvg(FedAvg):
        """Estrategia FedAvg personalizada con métricas mejoradas"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.round_metrics = []
        
        def aggregate_fit(
            self,
            server_round: int,
            results: List[Tuple[fl.server.client_proxy.ClientProxy, FitRes]],
            failures: List[Tuple[fl.server.client_proxy.ClientProxy, FitRes] | BaseException],
        ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
            """Agregación personalizada con logging de métricas"""
            
            # Llamar a la implementación base
            aggregated_parameters, aggregated_metrics = super().aggregate_fit(
                server_round, results, failures
            )
            
            # Recopilar métricas de los clientes
            round_metrics = {
                "round": server_round,
                "num_clients": len(results),
                "num_failures": len(failures),
                "timestamp": datetime.now().isoformat()
            }
            
            if results:
                if losses := [res.metrics.get("loss", 0.0) for _, res in results if res.metrics]:
                    round_metrics["avg_loss"] = np.mean(losses)
                    round_metrics["min_loss"] = np.min(losses)
                    round_metrics["max_loss"] = np.max(losses)
            
            self.round_metrics.append(round_metrics)
            logger.info(f"Round {server_round} completed: {round_metrics}")
            
            return aggregated_parameters, aggregated_metrics
else:
    class CustomFedAvg:
        """Dummy class when federated learning is not available"""
        pass


class FederatedLearningService:
    """Servicio principal de Federated Learning"""
    
    def __init__(self):
        self.is_available = FEDERATED_LEARNING_AVAILABLE
        self.active_sessions = {}
        self.session_results = {}
        
        if not self.is_available:
            logger.warning("Federated Learning service initialized without dependencies")
    
    def check_availability(self) -> CheckAvailabilityResult:
        """Verificar disponibilidad del servicio"""
        return {
            "available": self.is_available,
            "dependencies": {
                "flwr": FEDERATED_LEARNING_AVAILABLE,
                "torch": "torch" in globals(),
            },
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.session_results)
        }
    
    def create_strategy(self, config: FederatedConfig) -> Strategy:
        """Crear estrategia de agregación"""
        if not self.is_available:
            raise RuntimeError("Federated learning dependencies not available")
        
        strategy_params = {
            "min_fit_clients": config.min_fit_clients,
            "min_evaluate_clients": config.min_evaluate_clients,
            "min_available_clients": config.min_available_clients,
            "fraction_fit": config.fraction_fit,
            "fraction_evaluate": config.fraction_evaluate,
        }
        
        if config.strategy.lower() == "fedavg":
            return CustomFedAvg(**strategy_params)
        elif config.strategy.lower() == "fedprox":
            return FedProx(proximal_mu=1.0, **strategy_params)
        else:
            logger.warning(f"Unknown strategy {config.strategy}, using FedAvg")
            return CustomFedAvg(**strategy_params)
    
    async def start_federated_server(
        self,
        session_id: str,
        config: FederatedConfig,
        server_address: str = "localhost:8080"
    ) -> Dict[str, Any]:
        """Iniciar servidor federado"""
        if not self.is_available:
            return {
                "success": False,
                "error": "Federated learning dependencies not available"
            }
        
        try:
            # Crear estrategia
            strategy = self.create_strategy(config)
            
            # Configuración del servidor
            server_config = ServerConfig(num_rounds=config.num_rounds)
            
            # Registrar sesión activa
            self.active_sessions[session_id] = {
                "config": config,
                "strategy": strategy,
                "server_address": server_address,
                "start_time": datetime.now(),
                "status": "starting"
            }
            
            logger.info(f"Starting federated server for session {session_id}")
            
            # Iniciar servidor en background
            asyncio.create_task(self._run_server(session_id, strategy, server_config, server_address))
            
            return {
                "success": True,
                "session_id": session_id,
                "server_address": server_address,
                "config": config.__dict__,
                "message": "Federated server starting"
            }
            
        except (ImportError, AttributeError, ValueError, ConnectionError) as e:
            logger.error(f"Error starting federated server: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def _run_server(
        self,
        session_id: str,
        strategy: Strategy,
        config: ServerConfig,
        server_address: str
    ):
        """Ejecutar servidor federado en background"""
        try:
            self.active_sessions[session_id]["status"] = "running"
            
            # Ejecutar servidor Flower
            hist = fl.server.start_server(
                server_address=server_address,
                config=config,
                strategy=strategy,
            )
            
            # Procesar resultados
            results = self._process_server_results(session_id, hist, strategy)
            
            # Guardar resultados
            self.session_results[session_id] = results
            
            # Limpiar sesión activa
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            logger.info(f"Federated training completed for session {session_id}")
            
        except DatabaseError as e:
            logger.error(f"Error in federated server {session_id}: {e}")
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "error"
                self.active_sessions[session_id]["error"] = str(e)
    
    def _process_server_results(
        self,
        session_id: str,
        history,
        strategy: Strategy
    ) -> FederatedResults:
        """Procesar resultados del servidor"""
        
        # Extraer métricas del historial
        losses = history.losses_distributed if hasattr(history, 'losses_distributed') else []
        accuracies = history.metrics_distributed.get('accuracy', []) if hasattr(history, 'metrics_distributed') else []
        
        # Métricas de la estrategia personalizada
        round_metrics = []
        if hasattr(strategy, 'round_metrics'):
            round_metrics = strategy.round_metrics
        
        # Crear métricas de clientes
        client_metrics = []
        for i, metrics in enumerate(round_metrics):
            client_metrics.append(ClientMetrics(
                client_id=f"aggregated_round_{i+1}",
                round_num=i + 1,
                loss=metrics.get("avg_loss", 0.0),
                accuracy=metrics.get("avg_accuracy"),
                num_examples=0,
                training_time=0.0,
                timestamp=datetime.fromisoformat(metrics["timestamp"])
            ))
        
        # Determinar convergencia
        convergence_round = None
        if len(losses) > 1:
            for i in range(1, len(losses)):
                if abs(losses[i][1] - losses[i-1][1]) < 0.001:  # Threshold de convergencia
                    convergence_round = i + 1
                    break
        
        return FederatedResults(
            total_rounds=len(losses),
            final_loss=losses[-1][1] if losses else 0.0,
            final_accuracy=accuracies[-1][1] if accuracies else None,
            convergence_round=convergence_round,
            client_metrics=client_metrics,
            training_time=0.0,  # Se calculará en implementaciones futuras
            model_parameters=None
        )
    
    def get_session_status(self, session_id: str) -> GetSessionStatusResult:
        """Obtener estado de una sesión"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session_id,
                "status": session["status"],
                "start_time": session["start_time"].isoformat(),
                "server_address": session["server_address"],
                "config": session["config"].__dict__,
                "error": session.get("error")
            }
        elif session_id in self.session_results:
            results = self.session_results[session_id]
            return {
                "session_id": session_id,
                "status": "completed",
                "results": {
                    "total_rounds": results.total_rounds,
                    "final_loss": results.final_loss,
                    "final_accuracy": results.final_accuracy,
                    "convergence_round": results.convergence_round,
                    "training_time": results.training_time
                }
            }
        else:
            return {
                "session_id": session_id,
                "status": "not_found",
                "error": "Session not found"
            }
    
    def list_sessions(self) -> ListSessionsResult:
        """Listar todas las sesiones"""
        return {
            "active_sessions": list(self.active_sessions.keys()),
            "completed_sessions": list(self.session_results.keys()),
            "total_active": len(self.active_sessions),
            "total_completed": len(self.session_results)
        }
    
    def get_session_metrics(self, session_id: str) -> GetSessionMetricsResult:
        """Obtener métricas detalladas de una sesión"""
        if session_id in self.session_results:
            results = self.session_results[session_id]
            return {
                "session_id": session_id,
                "metrics": {
                    "total_rounds": results.total_rounds,
                    "final_loss": results.final_loss,
                    "final_accuracy": results.final_accuracy,
                    "convergence_round": results.convergence_round,
                    "training_time": results.training_time,
                    "client_metrics": [
                        {
                            "client_id": m.client_id,
                            "round_num": m.round_num,
                            "loss": m.loss,
                            "accuracy": m.accuracy,
                            "num_examples": m.num_examples,
                            "training_time": m.training_time,
                            "timestamp": m.timestamp.isoformat() if m.timestamp else None
                        }
                        for m in results.client_metrics
                    ]
                }
            }
        else:
            return {
                "session_id": session_id,
                "error": "Session not found or not completed"
            }
    
    def stop_session(self, session_id: str) -> StopSessionResult:
        """Detener una sesión activa"""
        if session_id in self.active_sessions:
            # En una implementación real, aquí se detendría el servidor
            self.active_sessions[session_id]["status"] = "stopped"
            logger.info(f"Session {session_id} marked for stopping")
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session marked for stopping"
            }
        else:
            return {
                "success": False,
                "session_id": session_id,
                "error": "Session not found or not active"
            }
    
    def get_supported_strategies(self) -> List[str]:
        """Obtener estrategias soportadas"""
        return ["FedAvg", "FedProx"]
    
    def create_client_config(
        self,
        server_address: str,
        client_id: str,
        model_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crear configuración para cliente federado"""
        return {
            "server_address": server_address,
            "client_id": client_id,
            "model_config": model_config,
            "instructions": {
                "1": "Install flwr client: pip install flwr",
                "2": "Implement FlowerClient class with your model",
                "3": f"Connect to server: fl.client.start_numpy_client(server_address='{server_address}', client=your_client)",
                "4": "Ensure your model matches the server's expected architecture"
            }
        }


# Instancia global del servicio
federated_learning_service = FederatedLearningService()