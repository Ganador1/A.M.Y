"""
Lab Automation Service
Orquesta protocolos de laboratorio a alto nivel usando el puente de equipamiento simulado.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.exceptions.base import AtlasException
from app.domains.engineering.services.lab_equipment_bridge import (
    get_lab_bridge,
    ExperimentTask,
    EquipmentResult,
)

logger = logging.getLogger(__name__)


class LabAutomationService:
    """
    Servicio de automatización de laboratorio (simulado) que compone LabEquipmentBridge.

    - run_pcr_protocol: simula termociclado y preparación
    - run_elisa_assay: ejecuta protocolo ELISA y lectura con plate reader
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False

    async def initialize(self) -> bool:
        try:
            self.bridge = await get_lab_bridge()
            self.initialized = True
            logger.info("✅ LabAutomationService inicializado")
            return True
        except AtlasException as e:
            logger.error(f"Error inicializando LabAutomationService: {e}")
            return False

    async def run_pcr_protocol(self, samples: List[Dict[str, Any]], program: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta protocolo PCR simulado (sin instrumentación real de termociclador).
        """
        if not self.initialized:
            await self.initialize()

        program = program or {
            'initial_denaturation': {'temp': 95, 'time': 180},
            'cycles': 30,
            'denaturation': {'temp': 95, 'time': 30},
            'annealing': {'temp': 60, 'time': 30},
            'extension': {'temp': 72, 'time': 45},
            'final_extension': {'temp': 72, 'time': 300}
        }

        steps: List[Dict[str, Any]] = []
        total_seconds = program['initial_denaturation']['time'] + program['final_extension']['time']
        total_seconds += program['cycles'] * (program['denaturation']['time'] + program['annealing']['time'] + program['extension']['time'])

        # Simular tiempos comprimidos
        await asyncio.sleep(min(10, total_seconds / 120.0))

        for idx, s in enumerate(samples):
            steps.append({
                'sample_id': s.get('id', f'sample_{idx+1}'),
                'well': s.get('well', f"{chr(65 + (idx // 12))}{(idx % 12)+1}"),
                'volume_ul': s.get('volume', 20),
                'status': 'prepared'
            })

        return {
            'protocol': 'PCR',
            'samples_processed': len(samples),
            'thermocycler': 'completed',
            'program': program,
            'steps': steps,
            'completed_at': datetime.utcnow().isoformat()
        }

    async def run_elisa_assay(self, samples: List[str], antibodies: Dict[str, Any], read_wavelength_nm: int = 450) -> Dict[str, Any]:
        """
        Ejecuta ensayo ELISA simulado y realiza lectura con plate reader a la longitud de onda indicada.
        """
        if not self.initialized:
            await self.initialize()

        # Simular incubaciones cortas
        await asyncio.sleep(1.0)

        # Lectura con plate reader
        task = ExperimentTask(
            task_id=f"elisa_read_{int(datetime.utcnow().timestamp())}",
            equipment_id='reader_001',
            task_type='absorbance',
            parameters={
                'read_mode': 'absorbance',
                'wavelength': read_wavelength_nm,
                'plate_format': 96,
                'assay_type': 'binding'
            },
            estimated_duration=30,
            samples=[{'id': sid} for sid in samples],
            priority=1
        )

        submitted = await self.bridge.submit_task(task)
        if not submitted:
            return {'success': False, 'error': 'No se pudo enviar tarea al plate reader'}

        # Esperar a que la cola procese (polling sencillo)
        for _ in range(100):
            status = self.bridge.get_task_status(task.task_id)
            if status and status.get('status') in ('completed', 'failed'):
                break
            await asyncio.sleep(0.1)

        result = self.bridge.completed_tasks.get(task.task_id)
        if not result:
            return {'success': False, 'error': 'Lectura no disponible'}

        return {
            'success': result.success,
            'assay_type': 'ELISA',
            'wavelength': read_wavelength_nm,
            'measurements': result.data if result.success else {},
            'metadata': result.metadata,
            'completed_at': datetime.utcnow().isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        try:
            if not self.initialized:
                await self.initialize()
            equipment = self.bridge.list_equipment()
            return {'status': 'healthy', 'equipment': equipment}
        except AtlasException as e:
            return {'status': 'error', 'error': str(e)}


