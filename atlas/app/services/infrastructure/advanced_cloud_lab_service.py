"""
Advanced Cloud Lab Service
Servicio avanzado de integración con Emerald Cloud Lab y otros laboratorios remotos
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import json
from datetime import datetime, timedelta
import hashlib
import os
import requests
import httpx
from app.config import settings
from app.exceptions.domain.biology import BiologyError
from app.types.advanced_cloud_lab_service_types import (
    MonitorExperimentResult,
    GetExperimentResultsResult,
    GenerateSimulatedResultsResult,
    GenerateQualityMetricsResult,
    GetAvailableProtocolsResult,
    GetExperimentHistoryResult,
    GetCostEstimateResult,
)

logger = logging.getLogger(__name__)


class AdvancedCloudLabService:
    """
    Servicio avanzado de integración con laboratorios remotos
    Incluye Emerald Cloud Lab, simulaciones avanzadas y monitoreo
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # Permitir configuración vía variables de entorno si no se pasa en config
        self.api_key = (
            self.config.get('ecl_api_key')
            or getattr(settings, 'ecl_api_key', None)
            or os.getenv('ECL_API_KEY')
        )
        if not self.api_key and not self.simulation_mode:
            logger.warning("⚠️ SECURITY: ECL_API_KEY is not configured and simulation_mode is False. API requests will fail.")
        self.base_url = (
            self.config.get('base_url')
            or getattr(settings, 'ecl_base_url', None)
            or os.getenv('ECL_BASE_URL', 'https://api.emeraldcloudlab.com/v2')
        )
        if 'simulation' in self.config:
            self.simulation_mode = bool(self.config.get('simulation'))
        else:
            env_sim = str(
                getattr(settings, 'ecl_simulation', None)
                or os.getenv('ECL_SIMULATION', 'true')
            ).lower()
            self.simulation_mode = env_sim == 'true'
        self.experiment_history = []
        
        # Headers para API real
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Simulación de experimentos en curso
        self.running_experiments = {}
        
        # Protocolos avanzados disponibles
        self.advanced_protocols = {
            'mass_spec_analysis': {
                'name': 'Análisis de espectrometría de masas',
                'duration_hours': 2,
                'cost_usd': 150,
                'instruments': ['LC-MS/MS', 'MALDI-TOF'],
                'parameters': ['ionization_mode', 'mass_range', 'resolution']
            },
            'protein_expression': {
                'name': 'Expresión de proteínas recombinantes',
                'duration_hours': 48,
                'cost_usd': 500,
                'instruments': ['bioreactors', 'FPLC', 'SDS-PAGE'],
                'parameters': ['cell_line', 'inducer', 'temperature', 'duration']
            },
            'crystallization_screen': {
                'name': 'Screen de cristalización de proteínas',
                'duration_hours': 720,  # 30 días
                'cost_usd': 800,
                'instruments': ['crystallization_robot', 'imaging_system'],
                'parameters': ['protein_concentration', 'screens', 'temperature']
            },
            'ngs_sequencing': {
                'name': 'Secuenciación NGS completa',
                'duration_hours': 72,
                'cost_usd': 1200,
                'instruments': ['Illumina_NovaSeq', 'library_prep'],
                'parameters': ['read_length', 'coverage', 'library_type']
            },
            'flow_cytometry': {
                'name': 'Citometría de flujo multiparamétrica',
                'duration_hours': 4,
                'cost_usd': 200,
                'instruments': ['BD_FACSAria', 'BD_LSRFortessa'],
                'parameters': ['antibody_panel', 'cell_count', 'sorting']
            },
            'drug_screening': {
                'name': 'Screening de compuestos farmacológicos',
                'duration_hours': 120,
                'cost_usd': 2000,
                'instruments': ['HTS_system', 'plate_reader', 'liquid_handler'],
                'parameters': ['compound_library', 'cell_line', 'assay_type']
            }
        }
    
    async def submit_advanced_experiment(self, protocol_name: str, samples: List[Dict[str, Any]], 
                                       parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Envía un experimento avanzado al laboratorio remoto
        """
        try:
            if protocol_name not in self.advanced_protocols:
                return {"error": f"Protocolo {protocol_name} no disponible"}
            
            protocol_info = self.advanced_protocols[protocol_name]
            parameters = parameters or {}
            
            # Crear ID único del experimento
            experiment_id = self._generate_experiment_id(protocol_name, samples)
            
            if self.simulation_mode:
                # Modo simulación
                result = await self._simulate_experiment_submission(
                    experiment_id, protocol_name, samples, parameters, protocol_info
                )
            else:
                # Modo real (API de ECL)
                result = await self._submit_real_experiment(
                    experiment_id, protocol_name, samples, parameters, protocol_info
                )
            
            # Guardar en historial
            self.experiment_history.append(result)
            
            # Si está en ejecución, añadir a experimentos activos
            if result.get('status') == 'running':
                self.running_experiments[experiment_id] = {
                    'start_time': datetime.now(),
                    'protocol': protocol_name,
                    'estimated_completion': datetime.now() + timedelta(hours=protocol_info['duration_hours']),
                    'samples_count': len(samples)
                }
            
            return result
            
        except BiologyError as e:
            logger.error(f"Error enviando experimento: {e}")
            return {"error": f"Error en envío: {str(e)}"}
    
    async def _simulate_experiment_submission(self, exp_id: str, protocol: str, 
                                            samples: List[Dict], parameters: Dict, 
                                            protocol_info: Dict) -> Dict[str, Any]:
        """Simula el envío de un experimento"""
        
        # Simular tiempo de validación
        await asyncio.sleep(1)
        
        return {
            'experiment_id': exp_id,
            'protocol_name': protocol,
            'status': 'running',
            'submission_time': datetime.now().isoformat(),
            'estimated_completion': (datetime.now() + timedelta(hours=protocol_info['duration_hours'])).isoformat(),
            'samples_submitted': len(samples),
            'estimated_cost_usd': protocol_info['cost_usd'],
            'instruments_assigned': protocol_info['instruments'],
            'parameters_used': parameters,
            'simulation_mode': True,
            'queue_position': 1
        }
    
    async def _submit_real_experiment(self, exp_id: str, protocol: str,
                                    samples: List[Dict], parameters: Dict,
                                    protocol_info: Dict) -> Dict[str, Any]:
        """Envía experimento real a ECL si ECL_SIMULATION=false"""
        try:
            payload = {
                "name": f"{protocol} - {exp_id}",
                "instructions": [
                    {
                        "op": protocol,
                        "samples": samples,
                        "parameters": parameters or {}
                    }
                ]
            }
            resp = await httpx.post(
                f"{self.base_url}/experiments",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            if resp.status_code not in (200, 201, 202):
                return {
                    'error': f"ECL submit fallo: HTTP {resp.status_code}",
                    'details': resp.text,
                    'simulation_mode': False
                }
            data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            ecl_job_id = data.get('id') or data.get('experiment_id') or f"ECL_{exp_id}"
            return {
                'experiment_id': exp_id,
                'protocol_name': protocol,
                'status': data.get('status', 'submitted'),
                'submission_time': datetime.now().isoformat(),
                'estimated_completion': (datetime.now() + timedelta(hours=protocol_info['duration_hours'])).isoformat(),
                'samples_submitted': len(samples),
                'estimated_cost_usd': protocol_info['cost_usd'],
                'ecl_job_id': ecl_job_id,
                'simulation_mode': False
            }
        except BiologyError as e:
            logger.error(f"ECL submit error: {e}")
            return {'error': str(e), 'simulation_mode': False}
    
    async def monitor_experiment(self, experiment_id: str) -> MonitorExperimentResult:
        """
        Monitorea el progreso de un experimento
        """
        try:
            if experiment_id not in self.running_experiments:
                # Si no es simulación, intentar consultar ECL
                if not self.simulation_mode:
                    try:
                        resp = await httpx.get(
                            f"{self.base_url}/experiments/{experiment_id}",
                            headers=self.headers,
                            timeout=10
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            status = data.get('status', 'unknown')
                            return {
                                'experiment_id': experiment_id,
                                'status': status,
                                'progress_percent': data.get('progress_percent'),
                                'last_updated': datetime.now().isoformat(),
                                'simulation_mode': False
                            }
                        return {'error': f"HTTP {resp.status_code}", 'simulation_mode': False}
                    except BiologyError as e:
                        return {'error': str(e), 'simulation_mode': False}
                return {"error": "Experimento no encontrado o no está en ejecución"}
            
            experiment = self.running_experiments[experiment_id]
            current_time = datetime.now()
            
            # Calcular progreso
            total_duration = experiment['estimated_completion'] - experiment['start_time']
            elapsed_time = current_time - experiment['start_time']
            progress_percent = min((elapsed_time.total_seconds() / total_duration.total_seconds()) * 100, 100)
            
            # Determinar estado actual
            if progress_percent >= 100:
                status = 'completed'
                # Remover de experimentos activos
                del self.running_experiments[experiment_id]
            elif progress_percent >= 90:
                status = 'finalizing'
            elif progress_percent >= 50:
                status = 'processing'
            else:
                status = 'queued'
            
            return {
                'experiment_id': experiment_id,
                'status': status,
                'progress_percent': round(progress_percent, 1),
                'elapsed_hours': round(elapsed_time.total_seconds() / 3600, 1),
                'estimated_remaining_hours': max(0, round((total_duration - elapsed_time).total_seconds() / 3600, 1)),
                'current_stage': self._get_current_stage(experiment['protocol'], progress_percent),
                'last_updated': current_time.isoformat()
            }
            
        except BiologyError as e:
            logger.error(f"Error monitoreando experimento: {e}")
            return {"error": f"Error en monitoreo: {str(e)}"}
    
    def _get_current_stage(self, protocol: str, progress: float) -> str:
        """Determina la etapa actual según el protocolo y progreso"""
        
        stages = {
            'mass_spec_analysis': [
                'sample_preparation', 'ionization', 'mass_analysis', 'data_processing'
            ],
            'protein_expression': [
                'transformation', 'culture_growth', 'induction', 'harvesting', 'purification', 'analysis'
            ],
            'crystallization_screen': [
                'protein_preparation', 'screen_setup', 'nucleation', 'crystal_growth', 'imaging', 'analysis'
            ],
            'ngs_sequencing': [
                'quality_control', 'library_prep', 'sequencing', 'base_calling', 'data_analysis'
            ],
            'flow_cytometry': [
                'sample_preparation', 'staining', 'acquisition', 'analysis'
            ],
            'drug_screening': [
                'plate_preparation', 'compound_addition', 'incubation', 'readout', 'data_analysis'
            ]
        }
        
        protocol_stages = stages.get(protocol, ['preparation', 'execution', 'analysis'])
        stage_index = min(int(progress / (100 / len(protocol_stages))), len(protocol_stages) - 1)
        
        return protocol_stages[stage_index]
    
    async def get_experiment_results(self, experiment_id: str) -> GetExperimentResultsResult:
        """
        Obtiene los resultados de un experimento completado
        """
        try:
            # Buscar en historial
            experiment = None
            for exp in self.experiment_history:
                if exp.get('experiment_id') == experiment_id:
                    experiment = exp
                    break
            
            if not experiment:
                # Intentar en modo real si aplica
                if not self.simulation_mode:
                    try:
                        # Intentar endpoint de resultados y fallback al de estado
                        r = await httpx.get(f"{self.base_url}/experiments/{experiment_id}/results", headers=self.headers, timeout=15)
                        if r.status_code == 404:
                            r = await httpx.get(f"{self.base_url}/experiments/{experiment_id}", headers=self.headers, timeout=15)
                        if r.status_code == 200:
                            data = r.json()
                            return {
                                'experiment_id': experiment_id,
                                'protocol_name': data.get('protocol_name'),
                                'status': data.get('status'),
                                'completion_time': data.get('completion_time') or datetime.now().isoformat(),
                                'results': data.get('results') or data,
                                'data_files': data.get('data_files'),
                                'quality_metrics': data.get('quality_metrics'),
                                'simulation_mode': False
                            }
                        return {'error': f"HTTP {r.status_code}", 'simulation_mode': False}
                    except BiologyError as e:
                        return {'error': str(e), 'simulation_mode': False}
                return {"error": "Experimento no encontrado"}
            
            # Verificar si está completado
            monitor_result = await self.monitor_experiment(experiment_id)
            if monitor_result.get('status') != 'completed' and (self.simulation_mode and experiment_id in self.running_experiments):
                return {"error": "Experimento aún en progreso"}
            
            # Generar resultados simulados basados en el protocolo
            protocol_name = experiment.get('protocol_name', '')
            results = await self._generate_simulated_results(protocol_name, experiment)
            
            return {
                'experiment_id': experiment_id,
                'protocol_name': protocol_name,
                'status': 'completed',
                'completion_time': datetime.now().isoformat(),
                'results': results,
                'data_files': self._generate_data_files_list(protocol_name),
                'quality_metrics': self._generate_quality_metrics(protocol_name)
            }
            
        except BiologyError as e:
            logger.error(f"Error obteniendo resultados: {e}")
            return {"error": f"Error obteniendo resultados: {str(e)}"}
    
    async def _generate_simulated_results(self, protocol: str, experiment: Dict) -> GenerateSimulatedResultsResult:
        """Genera resultados simulados basados en el protocolo"""
        
        if protocol == 'mass_spec_analysis':
            import random
            return {
                'detected_peaks': random.randint(50, 200),
                'molecular_weight_range': [100, 2000],
                'base_peak_mz': round(random.uniform(200, 800), 2),
                'total_ion_current': round(random.uniform(1e6, 1e8), 0),
                'purity_percent': round(random.uniform(85, 98), 1),
                'identified_compounds': random.randint(5, 15)
            }
            
        elif protocol == 'protein_expression':
            import random
            return {
                'protein_yield_mg': round(random.uniform(10, 100), 2),
                'purity_percent': round(random.uniform(90, 99), 1),
                'concentration_mg_ml': round(random.uniform(5, 25), 2),
                'molecular_weight_kda': round(random.uniform(25, 80), 1),
                'expression_level': random.choice(['low', 'medium', 'high']),
                'solubility': random.choice(['soluble', 'inclusion_bodies'])
            }
            
        elif protocol == 'crystallization_screen':
            import random
            return {
                'conditions_tested': 384,
                'crystals_found': random.randint(5, 25),
                'best_resolution_a': round(random.uniform(1.5, 3.0), 2),
                'space_group': random.choice(['P212121', 'P21', 'C2', 'P1']),
                'unit_cell_a': round(random.uniform(50, 150), 1),
                'crystal_quality': random.choice(['poor', 'medium', 'good', 'excellent'])
            }
            
        elif protocol == 'ngs_sequencing':
            import random
            return {
                'total_reads': random.randint(50000000, 200000000),
                'quality_score_mean': round(random.uniform(30, 40), 1),
                'gc_content_percent': round(random.uniform(40, 60), 1),
                'coverage_depth': random.randint(30, 150),
                'variants_detected': random.randint(100000, 500000),
                'assembly_quality': random.choice(['good', 'very_good', 'excellent'])
            }
            
        elif protocol == 'flow_cytometry':
            import random
            return {
                'cells_analyzed': random.randint(10000, 100000),
                'viable_cells_percent': round(random.uniform(85, 98), 1),
                'positive_population_percent': round(random.uniform(10, 70), 1),
                'median_fluorescence_intensity': random.randint(1000, 50000),
                'cell_populations_identified': random.randint(3, 8)
            }
            
        elif protocol == 'drug_screening':
            import random
            return {
                'compounds_tested': random.randint(1000, 10000),
                'active_compounds': random.randint(10, 100),
                'hit_rate_percent': round(random.uniform(0.5, 5.0), 2),
                'ic50_range_um': [round(random.uniform(0.1, 100), 2), round(random.uniform(100, 1000), 2)],
                'selectivity_index': round(random.uniform(10, 1000), 1)
            }
        
        return {'results': 'completed', 'data': 'available'}
    
    def _generate_data_files_list(self, protocol: str) -> List[Dict[str, Any]]:
        """Genera lista de archivos de datos simulados"""
        
        file_types = {
            'mass_spec_analysis': ['raw_data.mzML', 'peak_list.csv', 'analysis_report.pdf'],
            'protein_expression': ['sds_page.jpg', 'purification_trace.csv', 'concentration_data.xlsx'],
            'crystallization_screen': ['crystal_images.zip', 'conditions_tested.csv', 'diffraction_data.mtz'],
            'ngs_sequencing': ['raw_reads.fastq.gz', 'aligned_reads.bam', 'variants.vcf', 'assembly.fasta'],
            'flow_cytometry': ['flow_data.fcs', 'analysis_plots.pdf', 'population_stats.csv'],
            'drug_screening': ['dose_response.csv', 'hit_compounds.sdf', 'screening_report.pdf']
        }
        
        files = file_types.get(protocol, ['data_file.csv', 'report.pdf'])
        
        return [
            {
                'filename': filename,
                'size_mb': round(random.uniform(1, 500), 1),
                'format': filename.split('.')[-1],
                'download_url': f"https://cloud-lab-data.com/download/{filename}"
            }
            for filename in files
        ]
    
    def _generate_quality_metrics(self, protocol: str) -> GenerateQualityMetricsResult:
        """Genera métricas de calidad simuladas"""
        import random
        
        return {
            'overall_quality': random.choice(['poor', 'fair', 'good', 'excellent']),
            'reproducibility_score': round(random.uniform(0.8, 0.99), 3),
            'technical_score': round(random.uniform(0.7, 0.95), 3),
            'data_completeness_percent': round(random.uniform(90, 100), 1),
            'quality_flags': random.choice([[], ['low_signal'], ['contamination'], ['incomplete_data']])
        }
    
    def _generate_experiment_id(self, protocol: str, samples: List[Dict]) -> str:
        """Genera ID único para el experimento"""
        content = f"{protocol}_{len(samples)}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12].upper()
    
    async def get_available_protocols(self) -> GetAvailableProtocolsResult:
        """Obtiene protocolos disponibles"""
        return {
            'available_protocols': list(self.advanced_protocols.keys()),
            'total_protocols': len(self.advanced_protocols),
            'protocols': self.advanced_protocols
        }
    
    async def get_experiment_history(self, limit: int = 20) -> GetExperimentHistoryResult:
        """Obtiene historial de experimentos"""
        recent_history = self.experiment_history[-limit:] if self.experiment_history else []
        
        return {
            'total_experiments': len(self.experiment_history),
            'recent_experiments': recent_history,
            'running_experiments': len(self.running_experiments),
            'completed_experiments': len([e for e in self.experiment_history if e.get('status') == 'completed'])
        }
    
    async def get_cost_estimate(self, protocol_name: str, samples_count: int) -> GetCostEstimateResult:
        """Calcula estimación de costos"""
        if protocol_name not in self.advanced_protocols:
            return {"error": f"Protocolo {protocol_name} no encontrado"}
        
        protocol_info = self.advanced_protocols[protocol_name]
        base_cost = protocol_info['cost_usd']
        
        # Calcular costo total (algunos protocolos escalan con número de muestras)
        if protocol_name in ['flow_cytometry', 'mass_spec_analysis']:
            total_cost = base_cost + (samples_count - 1) * (base_cost * 0.3)
        else:
            total_cost = base_cost
        
        return {
            'protocol_name': protocol_name,
            'samples_count': samples_count,
            'base_cost_usd': base_cost,
            'total_cost_usd': round(total_cost, 2),
            'cost_per_sample_usd': round(total_cost / samples_count, 2),
            'estimated_duration_hours': protocol_info['duration_hours'],
            'currency': 'USD'
        }
