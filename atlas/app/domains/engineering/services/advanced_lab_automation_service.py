"""
Advanced Lab Automation Service
Servicio avanzado de automatización de laboratorio con PyLabRobot
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import json
from datetime import datetime, timedelta
import os
from app.config import settings
from app.exceptions.domain.biology import BiologyError
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class AdvancedLabAutomationService(BaseService):
    """
    Servicio avanzado de automatización de laboratorio con PyLabRobot
    Incluye control de múltiples instrumentos y protocolos complejos
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("AdvancedLabAutomationService")
        self.config = config or {}
        # Permitir override por variables de entorno y settings con defaults seguros
        self.robot_type = (
            self.config.get('robot_type')
            or os.getenv("LAB_ROBOT_TYPE", getattr(settings, "lab_robot_type", "hamilton_star"))
        )
        if 'simulation' in self.config:
            self.simulation_mode = bool(self.config.get('simulation'))
        else:
            sim_val = os.getenv(
                "LAB_SIMULATION",
                getattr(settings, "lab_simulation", "true")
            )
            self.simulation_mode = str(sim_val).lower() in ("1", "true", "yes")
        self.deck_layout = (
            self.config.get('deck_layout')
            or os.getenv("LAB_DECK_LAYOUT", getattr(settings, "lab_deck_layout", "standard"))
        )
        self.instruments = {}
        self.protocol_history = []
        
        # Configuración de instrumentos disponibles
        self.available_instruments = {
            'liquid_handler': {'status': 'ready', 'type': 'hamilton_star'},
            'thermocycler': {'status': 'ready', 'type': 'bio_rad_cfx'},
            'plate_reader': {'status': 'ready', 'type': 'tecan_infinite'},
            'incubator': {'status': 'ready', 'type': 'thermo_heracell'},
            'centrifuge': {'status': 'ready', 'type': 'eppendorf_5810r'},
            'pipettes': {'status': 'ready', 'type': 'electronic_multichannel'}
        }
        
        # Protocolos pre-definidos
        self.protocol_templates = {
            'pcr_standard': {
                'name': 'PCR Estándar',
                'duration_minutes': 180,
                'instruments': ['liquid_handler', 'thermocycler'],
                'reagents': ['master_mix', 'primers', 'template'],
                'steps': [
                    'prepare_master_mix',
                    'add_samples',
                    'thermocycling',
                    'store_products'
                ]
            },
            'elisa_96well': {
                'name': 'ELISA 96 pocillos',
                'duration_minutes': 300,
                'instruments': ['liquid_handler', 'plate_reader', 'incubator'],
                'reagents': ['coating_antibody', 'blocking_buffer', 'samples', 'detection_antibody', 'substrate'],
                'steps': [
                    'coat_plate',
                    'incubate_coating',
                    'wash_plate',
                    'block_plate',
                    'add_samples',
                    'incubate_samples',
                    'wash_plate',
                    'add_detection',
                    'incubate_detection',
                    'add_substrate',
                    'read_absorbance'
                ]
            },
            'dna_extraction': {
                'name': 'Extracción de DNA',
                'duration_minutes': 120,
                'instruments': ['liquid_handler', 'centrifuge'],
                'reagents': ['lysis_buffer', 'binding_buffer', 'wash_buffer', 'elution_buffer'],
                'steps': [
                    'cell_lysis',
                    'protein_precipitation',
                    'dna_binding',
                    'wash_dna',
                    'elute_dna',
                    'quantify_dna'
                ]
            },
            'cell_culture': {
                'name': 'Cultivo celular automatizado',
                'duration_minutes': 1440,  # 24 horas
                'instruments': ['liquid_handler', 'incubator', 'plate_reader'],
                'reagents': ['culture_medium', 'supplements', 'antibiotics'],
                'steps': [
                    'prepare_medium',
                    'seed_cells',
                    'incubate_culture',
                    'monitor_growth',
                    'medium_change',
                    'harvest_cells'
                ]
            }
        }

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de automatización de laboratorio
        """
        action = request_data.get("action")
        
        if action == "run_protocol":
            return await self.run_automated_protocol(
                protocol_name=request_data.get("protocol_name"),
                samples=request_data.get("samples", []),
                parameters=request_data.get("parameters", {})
            )
        elif action == "initialize":
            return await self.initialize_instruments()
        elif action == "list_protocols":
            return await self.get_protocol_templates()
        elif action == "get_status":
            return await self.get_instrument_status()
        elif action == "get_history":
            return await self.get_protocol_history(limit=request_data.get("limit", 10))
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    async def initialize_instruments(self) -> Dict[str, Any]:
        """Inicializa todos los instrumentos del laboratorio"""
        try:
            initialization_results = {}
            
            for instrument_name, instrument_info in self.available_instruments.items():
                if self.simulation_mode:
                    # Simulación de inicialización
                    await asyncio.sleep(0.1)
                    initialization_results[instrument_name] = {
                        'status': 'initialized',
                        'type': instrument_info['type'],
                        'simulation': True
                    }
                else:
                    # Aquí iría la inicialización real de cada instrumento
                    initialization_results[instrument_name] = await self._initialize_real_instrument(
                        instrument_name, instrument_info
                    )
            
            return {
                'success': True,
                'instruments_initialized': len(initialization_results),
                'details': initialization_results,
                'laboratory_ready': True
            }
            
        except BiologyError as e:
            logger.error(f"Error inicializando instrumentos: {e}")
            return {"error": f"Error en inicialización: {str(e)}"}
    
    async def run_automated_protocol(self, protocol_name: str, samples: List[Dict[str, Any]], 
                                   parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ejecuta un protocolo automatizado completo
        """
        try:
            if protocol_name not in self.protocol_templates:
                return {"error": f"Protocolo {protocol_name} no encontrado"}
            
            protocol = self.protocol_templates[protocol_name]
            parameters = parameters or {}
            
            # Verificar disponibilidad de instrumentos
            instrument_check = await self._check_instruments_availability(protocol['instruments'])
            if not instrument_check['all_available']:
                return {"error": f"Instrumentos no disponibles: {instrument_check['unavailable']}"}
            
            # Crear ID único para el protocolo
            protocol_id = f"{protocol_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Inicializar resultado
            result = {
                'protocol_id': protocol_id,
                'protocol_name': protocol_name,
                'samples_processed': len(samples),
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'steps_completed': [],
                'instruments_used': protocol['instruments'],
                'estimated_duration_minutes': protocol['duration_minutes']
            }
            
            # Ejecutar cada paso del protocolo
            for step in protocol['steps']:
                step_result = await self._execute_protocol_step(step, samples, parameters, protocol_name)
                result['steps_completed'].append(step_result)
                
                if step_result['status'] == 'failed':
                    result['status'] = 'failed'
                    result['error'] = step_result.get('error', 'Error desconocido')
                    break
            
            if result['status'] == 'running':
                result['status'] = 'completed'
            
            result['end_time'] = datetime.now().isoformat()
            result['actual_duration_minutes'] = self._calculate_duration(result['start_time'], result['end_time'])
            
            # Guardar en historial
            self.protocol_history.append(result)
            
            return result
            
        except BiologyError as e:
            logger.error(f"Error ejecutando protocolo: {e}")
            return {"error": f"Error en protocolo: {str(e)}"}
    
    async def _execute_protocol_step(self, step: str, samples: List[Dict], 
                                   parameters: Dict, protocol_name: str) -> Dict[str, Any]:
        """Ejecuta un paso individual del protocolo"""
        step_start = datetime.now()
        
        try:
            if protocol_name == 'pcr_standard':
                return await self._execute_pcr_step(step, samples, parameters)
            elif protocol_name == 'elisa_96well':
                return await self._execute_elisa_step(step, samples, parameters)
            elif protocol_name == 'dna_extraction':
                return await self._execute_dna_extraction_step(step, samples, parameters)
            elif protocol_name == 'cell_culture':
                return await self._execute_cell_culture_step(step, samples, parameters)
            else:
                # Paso genérico
                await asyncio.sleep(1)  # Simular tiempo de ejecución
                return {
                    'step': step,
                    'status': 'completed',
                    'duration_seconds': 1,
                    'timestamp': step_start.isoformat()
                }
                
        except BiologyError as e:
            return {
                'step': step,
                'status': 'failed',
                'error': str(e),
                'timestamp': step_start.isoformat()
            }
    
    async def _execute_pcr_step(self, step: str, samples: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """Ejecuta pasos específicos del protocolo PCR"""
        step_start = datetime.now()
        
        if step == 'prepare_master_mix':
            # Preparar master mix
            master_mix_volume = parameters.get('master_mix_volume', 20) * len(samples)
            await asyncio.sleep(2)  # Simular tiempo de preparación
            
            return {
                'step': step,
                'status': 'completed',
                'master_mix_volume_ul': master_mix_volume,
                'reactions_prepared': len(samples),
                'duration_seconds': 2,
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'add_samples':
            # Añadir muestras
            await asyncio.sleep(len(samples) * 0.5)  # 0.5 seg por muestra
            
            return {
                'step': step,
                'status': 'completed',
                'samples_added': len(samples),
                'volume_per_sample_ul': parameters.get('sample_volume', 5),
                'duration_seconds': len(samples) * 0.5,
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'thermocycling':
            # Termociclado
            cycles = parameters.get('cycles', 35)
            cycle_time = parameters.get('cycle_time_seconds', 180)
            total_time = cycles * cycle_time
            
            # Simular tiempo de termociclado (escalado)
            await asyncio.sleep(min(total_time / 100, 10))
            
            return {
                'step': step,
                'status': 'completed',
                'cycles': cycles,
                'total_time_seconds': total_time,
                'annealing_temp': parameters.get('annealing_temp', 60),
                'duration_seconds': min(total_time / 100, 10),
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'store_products':
            # Almacenar productos
            await asyncio.sleep(1)
            
            return {
                'step': step,
                'status': 'completed',
                'storage_temp': parameters.get('storage_temp', -20),
                'products_stored': len(samples),
                'duration_seconds': 1,
                'timestamp': step_start.isoformat()
            }
    
    async def _execute_elisa_step(self, step: str, samples: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """Ejecuta pasos específicos del protocolo ELISA"""
        step_start = datetime.now()
        
        if step == 'coat_plate':
            coating_volume = parameters.get('coating_volume', 100)
            await asyncio.sleep(2)
            
            return {
                'step': step,
                'status': 'completed',
                'coating_volume_ul': coating_volume,
                'wells_coated': 96,
                'duration_seconds': 2,
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'incubate_coating':
            incubation_time = parameters.get('coating_incubation_minutes', 60)
            await asyncio.sleep(min(incubation_time / 10, 6))  # Tiempo escalado
            
            return {
                'step': step,
                'status': 'completed',
                'incubation_time_minutes': incubation_time,
                'temperature': parameters.get('incubation_temp', 37),
                'duration_seconds': min(incubation_time / 10, 6),
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'wash_plate':
            wash_cycles = parameters.get('wash_cycles', 3)
            await asyncio.sleep(wash_cycles * 0.5)
            
            return {
                'step': step,
                'status': 'completed',
                'wash_cycles': wash_cycles,
                'wash_buffer': 'PBS-Tween',
                'duration_seconds': wash_cycles * 0.5,
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'read_absorbance':
            await asyncio.sleep(1)
            
            # Simular lecturas de absorbancia
            import random
            readings = [round(random.uniform(0.1, 2.5), 3) for _ in range(len(samples))]
            
            return {
                'step': step,
                'status': 'completed',
                'wavelength': parameters.get('wavelength', 450),
                'readings': readings,
                'mean_absorbance': round(sum(readings) / len(readings), 3),
                'duration_seconds': 1,
                'timestamp': step_start.isoformat()
            }
        
        # Otros pasos de ELISA
        await asyncio.sleep(1)
        return {
            'step': step,
            'status': 'completed',
            'duration_seconds': 1,
            'timestamp': step_start.isoformat()
        }
    
    async def _execute_dna_extraction_step(self, step: str, samples: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """Ejecuta pasos específicos del protocolo de extracción de DNA"""
        step_start = datetime.now()
        
        if step == 'cell_lysis':
            lysis_time = parameters.get('lysis_time_minutes', 10)
            await asyncio.sleep(min(lysis_time / 5, 2))
            
            return {
                'step': step,
                'status': 'completed',
                'lysis_time_minutes': lysis_time,
                'buffer_volume_ul': parameters.get('lysis_buffer_volume', 200),
                'duration_seconds': min(lysis_time / 5, 2),
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'quantify_dna':
            await asyncio.sleep(1)
            
            # Simular concentraciones de DNA
            import random
            concentrations = [round(random.uniform(50, 500), 1) for _ in range(len(samples))]
            
            return {
                'step': step,
                'status': 'completed',
                'concentrations_ng_ul': concentrations,
                'mean_concentration': round(sum(concentrations) / len(concentrations), 1),
                'method': 'fluorometric',
                'duration_seconds': 1,
                'timestamp': step_start.isoformat()
            }
        
        # Otros pasos genéricos
        await asyncio.sleep(1)
        return {
            'step': step,
            'status': 'completed',
            'duration_seconds': 1,
            'timestamp': step_start.isoformat()
        }
    
    async def _execute_cell_culture_step(self, step: str, samples: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """Ejecuta pasos específicos del protocolo de cultivo celular"""
        step_start = datetime.now()
        
        if step == 'seed_cells':
            cell_density = parameters.get('cell_density_per_ml', 100000)
            await asyncio.sleep(2)
            
            return {
                'step': step,
                'status': 'completed',
                'cell_density_per_ml': cell_density,
                'wells_seeded': len(samples),
                'medium_volume_ul': parameters.get('medium_volume', 200),
                'duration_seconds': 2,
                'timestamp': step_start.isoformat()
            }
            
        elif step == 'monitor_growth':
            await asyncio.sleep(1)
            
            # Simular medidas de crecimiento
            import random
            od_readings = [round(random.uniform(0.1, 1.5), 3) for _ in range(len(samples))]
            
            return {
                'step': step,
                'status': 'completed',
                'od_readings': od_readings,
                'mean_od': round(sum(od_readings) / len(od_readings), 3),
                'measurement_method': 'optical_density_600nm',
                'duration_seconds': 1,
                'timestamp': step_start.isoformat()
            }
        
        # Otros pasos genéricos
        await asyncio.sleep(1)
        return {
            'step': step,
            'status': 'completed',
            'duration_seconds': 1,
            'timestamp': step_start.isoformat()
        }
    
    async def _check_instruments_availability(self, required_instruments: List[str]) -> Dict[str, Any]:
        """Verifica disponibilidad de instrumentos requeridos"""
        available = []
        unavailable = []
        
        for instrument in required_instruments:
            if instrument in self.available_instruments:
                if self.available_instruments[instrument]['status'] == 'ready':
                    available.append(instrument)
                else:
                    unavailable.append(instrument)
            else:
                unavailable.append(instrument)
        
        return {
            'all_available': len(unavailable) == 0,
            'available': available,
            'unavailable': unavailable
        }
    
    async def _initialize_real_instrument(self, name: str, info: Dict) -> Dict[str, Any]:
        """Inicialización real de instrumento (placeholder)"""
        # Aquí iría la lógica real de inicialización
        await asyncio.sleep(1)
        return {
            'status': 'initialized',
            'type': info['type'],
            'simulation': False,
            'connection': 'established'
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calcula duración en minutos"""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds() / 60
    
    async def get_protocol_templates(self) -> Dict[str, Any]:
        """Obtiene plantillas de protocolos disponibles"""
        return {
            'available_protocols': list(self.protocol_templates.keys()),
            'total_protocols': len(self.protocol_templates),
            'protocols': self.protocol_templates
        }
    
    async def get_instrument_status(self) -> Dict[str, Any]:
        """Obtiene estado actual de todos los instrumentos"""
        return {
            'instruments': self.available_instruments,
            'total_instruments': len(self.available_instruments),
            'ready_instruments': len([i for i in self.available_instruments.values() if i['status'] == 'ready']),
            'simulation_mode': self.simulation_mode
        }
    
    async def get_protocol_history(self, limit: int = 10) -> Dict[str, Any]:
        """Obtiene historial de protocolos ejecutados"""
        recent_history = self.protocol_history[-limit:] if self.protocol_history else []
        
        return {
            'total_protocols_run': len(self.protocol_history),
            'recent_protocols': recent_history,
            'successful_protocols': len([p for p in self.protocol_history if p['status'] == 'completed']),
            'failed_protocols': len([p for p in self.protocol_history if p['status'] == 'failed'])
        }
