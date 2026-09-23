"""
Service Management Module for Master Orchestration Service
Gestión de servicios, inicialización y configuración
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.base_service import BaseService
import aiofiles

logger = logging.getLogger(__name__)


class ServiceManager:
    """Gestor de servicios para el sistema de orquestación"""

    def __init__(self):
        self.services = {}
        self.service_health = {}

    def initialize_services(self, config: Dict[str, Any]) -> bool:
        """
        Initialize and register available services with proper error handling
        """
        try:
            # Import services
            services_to_initialize = [
                ('automl', 'ScientificAutoMLService', 'app.services.scientific_automl_service'),
                ('literature', 'LiteratureMiningService', 'app.services.literature_mining_service'),
                ('scientific_ai', 'ScientificAIService', 'app.services.scientific_ai'),
                ('research_orchestrator', 'UnifiedResearchOrchestrator', 'app.services.unified_research_orchestrator'),
                ('ai_scientist', 'AIScientistService', 'app.services.ai_scientist_service'),
                ('code_scientist', 'CodeScientistService', 'app.services.code_scientist_service'),
                ('agent2_bridge', 'Agent2BridgeService', 'app.services.agent2_bridge_service'),
                ('optimization', 'PipelineOptimizationService', 'app.services.pipeline_optimization_service'),
            ]

            initialized_count = 0

            for service_key, class_name, module_name in services_to_initialize:
                try:
                    # Import the module
                    module = __import__(module_name, fromlist=[class_name])
                    service_class = getattr(module, class_name)

                    # Initialize service
                    service_instance = service_class()
                    self.services[service_key] = service_instance

                    # Initialize health status
                    self.service_health[service_key] = {
                        'status': 'healthy',
                        'last_check': datetime.now(),
                        'failure_count': 0,
                        'response_time': 0.0,
                        'consecutive_failures': 0
                    }

                    initialized_count += 1
                    logger.info(f"Successfully initialized {service_key} service")

                except (ImportError, AttributeError, TypeError, ValueError) as e:
                    logger.warning(f"Could not initialize {service_key} service: {e}")
                    self.services[service_key] = None
                except Exception as e:
                    logger.error(f"Unexpected error initializing {service_key} service: {e}")
                    self.services[service_key] = None

            if initialized_count > 0:
                logger.info(f"Successfully initialized {initialized_count} services")
                return True
            else:
                logger.warning("No services were initialized - running in mock mode")
                return False

        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return False

    def get_service(self, service_key: str) -> Optional[Any]:
        """Get a service instance"""
        return self.services.get(service_key)

    def get_all_services(self) -> Dict[str, Any]:
        """Get all service instances"""
        return self.services.copy()

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all services"""
        return {
            "registered_services": list(self.services.keys()),
            "service_health": self.service_health,
            "services_status": {
                service_key: service.get_service_info() if service else None
                for service_key, service in self.services.items()
            }
        }

    def is_service_available(self, service_key: str) -> bool:
        """Check if a service is available and healthy"""
        service = self.services.get(service_key)
        if not service:
            return False

        health = self.service_health.get(service_key, {})
        return health.get('status') == 'healthy'


class CircuitBreakerManager:
    """Gestor de circuit breakers para servicios"""

    def __init__(self, failure_thresholds: Dict[str, int]):
        self.failure_thresholds = failure_thresholds
        self.circuit_breakers = {}

    def is_circuit_open(self, service_key: str) -> bool:
        """Check if circuit breaker is open for service"""
        circuit = self.circuit_breakers.get(service_key, {})
        return circuit.get('state') == 'open'

    def record_success(self, service_key: str):
        """Record successful service call"""
        if service_key not in self.circuit_breakers:
            self.circuit_breakers[service_key] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure': None
            }

        circuit = self.circuit_breakers[service_key]
        circuit['state'] = 'closed'
        circuit['failure_count'] = max(0, circuit['failure_count'] - 1)

    def record_failure(self, service_key: str):
        """Record failed service call"""
        if service_key not in self.circuit_breakers:
            self.circuit_breakers[service_key] = {
                'state': 'closed',
                'failure_count': 0,
                'last_failure': None
            }

        circuit = self.circuit_breakers[service_key]
        circuit['failure_count'] += 1
        circuit['last_failure'] = datetime.now()

        if circuit['failure_count'] >= self.failure_thresholds.get('service_failures', 5):
            circuit['state'] = 'open'
            logger.warning(f"Circuit breaker opened for {service_key}")

    def get_circuit_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            service_key: {
                'state': circuit['state'],
                'failure_count': circuit['failure_count'],
                'last_failure': circuit['last_failure'].isoformat() if circuit['last_failure'] else None
            }
            for service_key, circuit in self.circuit_breakers.items()
        }
