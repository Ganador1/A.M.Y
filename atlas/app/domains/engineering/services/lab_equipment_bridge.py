"""
Lab Equipment Bridge - Interface with laboratory equipment (real or simulated)

This service provides a unified interface to laboratory equipment for
automated experimental execution. Supports both real equipment APIs
and high-fidelity simulations.

Author: ATLAS Autonomous Laboratory System  
Date: ${new Date().toISOString().split('T')[0]}
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone as tz
from enum import Enum
import json
from abc import ABC, abstractmethod
from app.exceptions.domain.biology import BiologyError

# Configure logging
logger = logging.getLogger(__name__)

UTC = tz.utc

# Import Knowledge Graph integration
from app.services.knowledge_graph_service import get_knowledge_graph_service


class EquipmentType(Enum):
    """Types of laboratory equipment"""
    SPECTROMETER_NMR = "nmr_spectrometer"
    SPECTROMETER_MS = "mass_spectrometer"
    SPECTROMETER_UV_VIS = "uv_vis_spectrometer"
    SPECTROMETER_IR = "ir_spectrometer"
    MICROSCOPE_OPTICAL = "optical_microscope"
    MICROSCOPE_ELECTRON = "electron_microscope"
    MICROSCOPE_FLUORESCENCE = "fluorescence_microscope"
    SYNTHESIZER_AUTOMATED = "automated_synthesizer"
    PLATE_READER = "plate_reader"
    PCR_MACHINE = "pcr_machine"
    SEQUENCER_DNA = "dna_sequencer"
    CENTRIFUGE = "centrifuge"
    INCUBATOR = "incubator"
    HPLC = "hplc"
    GC_MS = "gc_ms"


class EquipmentStatus(Enum):
    """Equipment operational status"""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class EquipmentSpec:
    """Equipment specifications"""
    equipment_id: str
    equipment_type: EquipmentType
    name: str
    manufacturer: str
    model: str
    location: str
    capabilities: List[str]
    supported_formats: List[str]
    max_throughput: int
    resolution: Optional[str] = None
    accuracy: Optional[str] = None
    temperature_range: Optional[Tuple[float, float]] = None
    is_simulated: bool = True
    api_endpoint: Optional[str] = None
    status: EquipmentStatus = EquipmentStatus.AVAILABLE


@dataclass
class ExperimentTask:
    """Task to be executed on equipment"""
    task_id: str
    equipment_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 1  # 1=highest, 5=lowest
    estimated_duration: int = 300  # seconds
    samples: List[Dict[str, Any]] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.QUEUED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass 
class EquipmentResult:
    """Result from equipment execution"""
    task_id: str
    equipment_id: str
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class EquipmentInterface(ABC):
    """Abstract interface for laboratory equipment"""
    
    def __init__(self, spec: EquipmentSpec):
        self.spec = spec
        self.current_task: Optional[ExperimentTask] = None
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize equipment connection"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: ExperimentTask) -> EquipmentResult:
        """Execute a task on the equipment"""
        pass
    
    @abstractmethod
    async def get_status(self) -> EquipmentStatus:
        """Get current equipment status"""
        pass
    
    @abstractmethod
    async def abort_task(self) -> bool:
        """Abort current task"""
        pass
    
    async def validate_task(self, task: ExperimentTask) -> Tuple[bool, List[str]]:
        """Validate if task can be executed"""
        errors = []
        
        if task.task_type not in self.spec.capabilities:
            errors.append(f"Task type {task.task_type} not supported")
            
        return len(errors) == 0, errors


class NMRSpectrometer(EquipmentInterface):
    """NMR Spectrometer interface (simulated)"""
    
    def __init__(self, spec: EquipmentSpec):
        super().__init__(spec)
        self.field_strength = 400  # MHz
        
    async def initialize(self) -> bool:
        """Initialize NMR spectrometer"""
        logger.info(f"Initializing NMR {self.spec.equipment_id}")
        await asyncio.sleep(2)  # Simulate initialization
        return True
    
    async def execute_task(self, task: ExperimentTask) -> EquipmentResult:
        """Execute NMR measurement"""
        start_time = datetime.now(UTC)
        
        try:
            # Extract parameters
            nucleus = task.parameters.get("nucleus", "1H")
            pulse_sequence = task.parameters.get("pulse_sequence", "zg30")
            scans = task.parameters.get("scans", 16)
            
            # Simulate acquisition
            await asyncio.sleep(task.estimated_duration / 60)  # Convert to minutes
            
            # Generate simulated spectrum
            spectrum = self._simulate_nmr_spectrum(
                nucleus=nucleus,
                molecule=task.parameters.get("molecule", "water")
            )
            
            result = EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=True,
                data={
                    "spectrum": spectrum,
                    "chemical_shifts": spectrum["peaks"],
                    "integrals": spectrum["integrals"],
                    "coupling_constants": spectrum.get("j_couplings", [])
                },
                metadata={
                    "nucleus": nucleus,
                    "field_strength_mhz": self.field_strength,
                    "pulse_sequence": pulse_sequence,
                    "scans": scans,
                    "temperature": task.parameters.get("temperature", 298)
                }
            )
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except BiologyError as e:
            return EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=False,
                data={},
                errors=[f"NMR execution failed: {str(e)}"]
            )
    
    def _simulate_nmr_spectrum(self, nucleus: str, molecule: str) -> Dict[str, Any]:
        """Simulate NMR spectrum based on molecule"""
        if nucleus == "1H":
            # Simulate common proton chemical shifts
            if "benzene" in molecule.lower():
                peaks = [7.26]  # Aromatic
                integrals = [6]
            elif "water" in molecule.lower():
                peaks = [4.79]  # HOD
                integrals = [2]
            elif "methanol" in molecule.lower():
                peaks = [3.31, 4.87]  # CH3OH
                integrals = [3, 1]
            else:
                # Generic alkyl peaks
                peaks = [0.9, 1.3, 2.1]
                integrals = [3, 2, 2]
                
        elif nucleus == "13C":
            # Simulate carbon spectrum
            if "benzene" in molecule.lower():
                peaks = [128.0]
                integrals = [6]
            else:
                peaks = [20.1, 30.5, 170.2]
                integrals = [1, 1, 1]
        else:
            peaks = [0.0]
            integrals = [1]
            
        # Add some noise and peak width
        spectrum_data = {
            "peaks": peaks,
            "integrals": integrals,
            "linewidths": [0.5] * len(peaks),
            "noise_level": 0.01,
            "baseline": 0.0
        }
        
        return spectrum_data
    
    async def get_status(self) -> EquipmentStatus:
        """Get NMR status"""
        return self.spec.status
    
    async def abort_task(self) -> bool:
        """Abort current NMR acquisition"""
        if self.current_task:
            logger.info(f"Aborting NMR task {self.current_task.task_id}")
            self.current_task = None
            return True
        return False


class MassSpectrometer(EquipmentInterface):
    """Mass Spectrometer interface (simulated)"""
    
    def __init__(self, spec: EquipmentSpec):
        super().__init__(spec)
        self.ionization_mode = "ESI+"
        
    async def initialize(self) -> bool:
        """Initialize mass spectrometer"""
        logger.info(f"Initializing MS {self.spec.equipment_id}")
        await asyncio.sleep(1)
        return True
    
    async def execute_task(self, task: ExperimentTask) -> EquipmentResult:
        """Execute MS analysis"""
        start_time = datetime.now(UTC)
        
        try:
            # Extract parameters
            ionization = task.parameters.get("ionization", "ESI+")
            mass_range = task.parameters.get("mass_range", [50, 1000])
            resolution = task.parameters.get("resolution", 30000)
            
            # Simulate analysis
            await asyncio.sleep(task.estimated_duration / 60)
            
            # Generate simulated mass spectrum
            spectrum = self._simulate_mass_spectrum(
                molecule=task.parameters.get("molecule", "unknown"),
                ionization=ionization
            )
            
            result = EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=True,
                data={
                    "mass_spectrum": spectrum,
                    "molecular_ion": spectrum["molecular_ion"],
                    "base_peak": spectrum["base_peak"],
                    "fragments": spectrum["fragments"]
                },
                metadata={
                    "ionization": ionization,
                    "mass_range": mass_range,
                    "resolution": resolution,
                    "scan_mode": task.parameters.get("scan_mode", "full_scan")
                }
            )
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except BiologyError as e:
            return EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=False,
                data={},
                errors=[f"MS execution failed: {str(e)}"]
            )
    
    def _simulate_mass_spectrum(self, molecule: str, ionization: str) -> Dict[str, Any]:
        """Simulate mass spectrum"""
        # Simple simulation based on molecule type
        if "aspirin" in molecule.lower():
            molecular_weight = 180.16
            molecular_ion = molecular_weight + 1 if "+" in ionization else molecular_weight - 1
            fragments = [
                {"mz": molecular_ion, "intensity": 45},
                {"mz": 138.03, "intensity": 100},  # Loss of CH2CO2
                {"mz": 120.02, "intensity": 30},   # Loss of CH3CO2H
                {"mz": 92.03, "intensity": 25}     # Phenyl cation
            ]
        elif "caffeine" in molecule.lower():
            molecular_weight = 194.19
            molecular_ion = molecular_weight + 1 if "+" in ionization else molecular_weight - 1
            fragments = [
                {"mz": molecular_ion, "intensity": 60},
                {"mz": 109.04, "intensity": 100},  # Base peak
                {"mz": 82.04, "intensity": 45},
                {"mz": 55.03, "intensity": 30}
            ]
        else:
            # Generic small molecule
            molecular_weight = 150.0
            molecular_ion = molecular_weight + 1 if "+" in ionization else molecular_weight - 1
            fragments = [
                {"mz": molecular_ion, "intensity": 70},
                {"mz": molecular_ion - 18, "intensity": 100},  # Loss of H2O
                {"mz": molecular_ion - 28, "intensity": 50},   # Loss of CO
                {"mz": molecular_ion - 45, "intensity": 30}    # Loss of COOH
            ]
        
        base_peak = max(fragments, key=lambda x: x["intensity"])
        
        return {
            "molecular_ion": {"mz": molecular_ion, "intensity": fragments[0]["intensity"]},
            "base_peak": base_peak,
            "fragments": fragments,
            "total_ion_current": sum(f["intensity"] for f in fragments)
        }
    
    async def get_status(self) -> EquipmentStatus:
        """Get MS status"""
        return self.spec.status
    
    async def abort_task(self) -> bool:
        """Abort current MS analysis"""
        if self.current_task:
            logger.info(f"Aborting MS task {self.current_task.task_id}")
            self.current_task = None
            return True
        return False


class PlateReader(EquipmentInterface):
    """Microplate Reader interface (simulated)"""
    
    def __init__(self, spec: EquipmentSpec):
        super().__init__(spec)
        self.plate_formats = [96, 384, 1536]
        
    async def initialize(self) -> bool:
        """Initialize plate reader"""
        logger.info(f"Initializing plate reader {self.spec.equipment_id}")
        await asyncio.sleep(0.5)
        return True
    
    async def execute_task(self, task: ExperimentTask) -> EquipmentResult:
        """Execute plate reading"""
        start_time = datetime.now(UTC)
        
        try:
            # Extract parameters
            read_mode = task.parameters.get("read_mode", "absorbance")
            wavelength = task.parameters.get("wavelength", 450)  # nm
            plate_format = task.parameters.get("plate_format", 96)
            
            # Simulate reading
            await asyncio.sleep(task.estimated_duration / 60)
            
            # Generate simulated plate data
            plate_data = self._simulate_plate_reading(
                plate_format=plate_format,
                read_mode=read_mode,
                assay_type=task.parameters.get("assay_type", "viability")
            )
            
            result = EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=True,
                data={
                    "plate_data": plate_data,
                    "statistics": self._calculate_plate_stats(plate_data),
                    "quality_control": self._assess_plate_quality(plate_data)
                },
                metadata={
                    "read_mode": read_mode,
                    "wavelength": wavelength,
                    "plate_format": plate_format,
                    "temperature": task.parameters.get("temperature", 37)
                }
            )
            
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except BiologyError as e:
            return EquipmentResult(
                task_id=task.task_id,
                equipment_id=self.spec.equipment_id,
                success=False,
                data={},
                errors=[f"Plate reader execution failed: {str(e)}"]
            )
    
    def _simulate_plate_reading(self, plate_format: int, read_mode: str, assay_type: str) -> Dict[str, Any]:
        """Simulate plate reader data"""
        rows = 8 if plate_format == 96 else (16 if plate_format == 384 else 32)
        cols = 12 if plate_format == 96 else (24 if plate_format == 384 else 48)
        
        # Generate realistic assay data
        if assay_type == "viability":
            # Cell viability assay - sigmoid dose response
            baseline = 1.0
            ec50_col = cols // 2
            data = np.zeros((rows, cols))
            
            for row in range(rows):
                for col in range(cols):
                    if col < 2:  # Negative controls
                        value = baseline + np.random.normal(0, 0.05)
                    elif col >= cols - 2:  # Positive controls
                        value = 0.1 + np.random.normal(0, 0.02)
                    else:  # Dose response
                        concentration = 10 ** (col - ec50_col)
                        value = baseline / (1 + concentration) + np.random.normal(0, 0.03)
                    
                    data[row, col] = max(0, value)
                    
        elif assay_type == "binding":
            # Binding assay with saturation curve
            data = np.zeros((rows, cols))
            kd_col = cols // 3
            
            for row in range(rows):
                for col in range(cols):
                    if col < 2:  # Background
                        value = 0.05 + np.random.normal(0, 0.01)
                    else:
                        concentration = col / kd_col
                        value = concentration / (1 + concentration) + np.random.normal(0, 0.02)
                    
                    data[row, col] = max(0, value)
        else:
            # Generic assay
            data = np.random.normal(0.5, 0.1, (rows, cols))
            data = np.clip(data, 0, None)
        
        return {
            "values": data.tolist(),
            "dimensions": {"rows": rows, "cols": cols},
            "well_ids": [f"{chr(65+r)}{c+1:02d}" for r in range(rows) for c in range(cols)]
        }
    
    def _calculate_plate_stats(self, plate_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate plate statistics"""
        values = np.array(plate_data["values"])
        
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "cv": float(np.std(values) / np.mean(values) * 100) if np.mean(values) > 0 else 0,
            "z_factor": self._calculate_z_factor(values),
            "signal_to_noise": float(np.max(values) / np.min(values)) if np.min(values) > 0 else float('inf')
        }
    
    def _calculate_z_factor(self, values: np.ndarray) -> float:
        """Calculate Z' factor for assay quality"""
        # Assuming first 2 and last 2 columns are controls
        if values.shape[1] >= 4:
            negative_controls = values[:, :2].flatten()
            positive_controls = values[:, -2:].flatten()
            
            if len(negative_controls) > 1 and len(positive_controls) > 1:
                z_factor = 1 - (3 * (np.std(positive_controls) + np.std(negative_controls)) / 
                               abs(np.mean(positive_controls) - np.mean(negative_controls)))
                return float(max(z_factor, -10))  # Cap at -10
        
        return 0.0
    
    def _assess_plate_quality(self, plate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess plate reading quality"""
        stats = self._calculate_plate_stats(plate_data)
        
        quality = {
            "overall_grade": "good",
            "issues": [],
            "warnings": []
        }
        
        if stats["cv"] > 20:
            quality["issues"].append("High coefficient of variation")
            quality["overall_grade"] = "poor"
        elif stats["cv"] > 10:
            quality["warnings"].append("Moderate coefficient of variation")
            if quality["overall_grade"] == "good":
                quality["overall_grade"] = "acceptable"
        
        if stats["z_factor"] < 0.5:
            quality["issues"].append("Low Z' factor - poor assay quality")
            quality["overall_grade"] = "poor"
        elif stats["z_factor"] < 0.7:
            quality["warnings"].append("Moderate Z' factor")
        
        return quality
    
    async def get_status(self) -> EquipmentStatus:
        """Get plate reader status"""
        return self.spec.status
    
    async def abort_task(self) -> bool:
        """Abort current plate reading"""
        if self.current_task:
            logger.info(f"Aborting plate reader task {self.current_task.task_id}")
            self.current_task = None
            return True
        return False


class LabEquipmentBridge:
    """
    Central bridge for managing laboratory equipment
    """
    
    def __init__(self):
        self.equipment: Dict[str, EquipmentInterface] = {}
        self.task_queue: List[ExperimentTask] = []
        self.completed_tasks: Dict[str, EquipmentResult] = {}
        self.scheduler_running = False
        self._initialize_default_equipment()
        logger.info("✅ LabEquipmentBridge initialized")
    
    def _initialize_default_equipment(self):
        """Initialize default simulated equipment"""
        
        # NMR Spectrometer
        nmr_spec = EquipmentSpec(
            equipment_id="nmr_001",
            equipment_type=EquipmentType.SPECTROMETER_NMR,
            name="Bruker AVANCE 400",
            manufacturer="Bruker",
            model="AVANCE NEO 400",
            location="Room 201",
            capabilities=["1h_nmr", "13c_nmr", "2d_nmr", "quantitative_nmr"],
            supported_formats=["liquid", "solid"],
            max_throughput=48,  # samples per day
            resolution="0.01 ppm",
            is_simulated=True
        )
        self.equipment["nmr_001"] = NMRSpectrometer(nmr_spec)
        
        # Mass Spectrometer
        ms_spec = EquipmentSpec(
            equipment_id="ms_001",
            equipment_type=EquipmentType.SPECTROMETER_MS,
            name="Thermo Q Exactive",
            manufacturer="Thermo Fisher",
            model="Q Exactive Plus",
            location="Room 203",
            capabilities=["esi_ms", "apci_ms", "ms_ms", "hrms"],
            supported_formats=["liquid", "gas"],
            max_throughput=96,
            resolution="140000 @ m/z 200",
            is_simulated=True
        )
        self.equipment["ms_001"] = MassSpectrometer(ms_spec)
        
        # Plate Reader
        reader_spec = EquipmentSpec(
            equipment_id="reader_001",
            equipment_type=EquipmentType.PLATE_READER,
            name="BioTek Synergy H1",
            manufacturer="BioTek",
            model="Synergy H1",
            location="Room 205",
            capabilities=["absorbance", "fluorescence", "luminescence", "time_resolved_fluorescence"],
            supported_formats=["96-well", "384-well"],
            max_throughput=200,  # plates per day
            is_simulated=True
        )
        self.equipment["reader_001"] = PlateReader(reader_spec)
    
    async def initialize_all_equipment(self) -> Dict[str, bool]:
        """Initialize all equipment"""
        results = {}
        
        for eq_id, equipment in self.equipment.items():
            try:
                success = await equipment.initialize()
                results[eq_id] = success
                if success:
                    equipment.spec.status = EquipmentStatus.AVAILABLE
                else:
                    equipment.spec.status = EquipmentStatus.ERROR
            except BiologyError as e:
                logger.error(f"Failed to initialize {eq_id}: {str(e)}")
                results[eq_id] = False
                equipment.spec.status = EquipmentStatus.ERROR
        
        return results
    
    def list_equipment(self, equipment_type: Optional[EquipmentType] = None) -> List[Dict[str, Any]]:
        """List available equipment"""
        equipment_list = []
        
        for eq_id, equipment in self.equipment.items():
            if equipment_type is None or equipment.spec.equipment_type == equipment_type:
                equipment_list.append({
                    "equipment_id": eq_id,
                    "type": equipment.spec.equipment_type.value,
                    "name": equipment.spec.name,
                    "manufacturer": equipment.spec.manufacturer,
                    "model": equipment.spec.model,
                    "location": equipment.spec.location,
                    "status": equipment.spec.status.value,
                    "capabilities": equipment.spec.capabilities,
                    "is_simulated": equipment.spec.is_simulated
                })
        
        return equipment_list
    
    async def submit_task(self, task: ExperimentTask) -> bool:
        """Submit a task to the queue"""
        if task.equipment_id not in self.equipment:
            logger.error(f"Equipment {task.equipment_id} not found")
            return False
        
        equipment = self.equipment[task.equipment_id]
        
        # Validate task
        valid, errors = await equipment.validate_task(task)
        if not valid:
            logger.error(f"Task validation failed: {errors}")
            task.status = TaskStatus.FAILED
            task.error_message = "; ".join(errors)
            return False
        
        # Add to queue
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: (t.priority, t.created_at))
        
        logger.info(f"Task {task.task_id} submitted to queue")
        
        # Start scheduler if not running
        if not self.scheduler_running:
            asyncio.create_task(self._run_scheduler())
        
        return True
    
    async def _run_scheduler(self):
        """Run the task scheduler"""
        self.scheduler_running = True
        logger.info("🚀 Task scheduler started")
        
        kg_service = await get_knowledge_graph_service()
        
        while self.task_queue:
            # Get highest priority task
            task = self.task_queue.pop(0)
            
            if task.equipment_id not in self.equipment:
                logger.error(f"Equipment {task.equipment_id} not found for task {task.task_id}")
                task.status = TaskStatus.FAILED
                task.error_message = "Equipment not found"
                continue
            
            equipment = self.equipment[task.equipment_id]
            
            try:
                # Capture experimental conditions in Knowledge Graph
                try:
                    # Extract parameters from task
                    experimental_conditions = {}
                    
                    # Common equipment parameters to capture
                    condition_params = ["temperature", "pressure", "time", "wavelength", 
                                      "voltage", "current", "flow_rate", "concentration"]
                    
                    if hasattr(task, 'parameters') and task.parameters:
                        for param in condition_params:
                            if param in task.parameters:
                                experimental_conditions[param] = task.parameters[param]
                    
                    # Capture instrument information
                    instrument_info = equipment.spec.name
                    
                    # Store conditions in Knowledge Graph
                    if experimental_conditions:
                        await kg_service.capture_experimental_conditions({
                            "experiment_id": task.task_id,
                            "conditions": experimental_conditions,
                            "instrument": instrument_info,
                            "domain": self._get_domain_from_equipment(equipment.spec.equipment_type),
                            "purpose": f"{task.task_type} analysis using {instrument_info}",
                            "hypothesis_tested": getattr(task, 'hypothesis', '')
                        })
                        
                except BiologyError as kg_error:
                    logger.warning(f"Could not capture experimental conditions in KG: {kg_error}")
                
                # Execute the actual task
                task.status = TaskStatus.RUNNING
                result = await equipment.execute_task(task)
                
                # Store result
                self.completed_tasks[task.task_id] = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(UTC)
                
                logger.info(f"✅ Task {task.task_id} completed successfully")
                
            except BiologyError as e:
                logger.error(f"Task {task.task_id} failed: {str(e)}")
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.now(UTC)
            
            # Small delay between tasks
            await asyncio.sleep(0.1)
        
        self.scheduler_running = False
        logger.info("⏹️ Task scheduler stopped")

    def _get_domain_from_equipment(self, equipment_type: EquipmentType) -> str:
        """Map equipment type to scientific domain"""
        domain_map = {
            EquipmentType.SPECTROMETER_NMR: "chemistry",
            EquipmentType.SPECTROMETER_MS: "chemistry",
            EquipmentType.SPECTROMETER_UV_VIS: "chemistry",
            EquipmentType.SPECTROMETER_IR: "chemistry",
            EquipmentType.MICROSCOPE_OPTICAL: "biology",
            EquipmentType.MICROSCOPE_ELECTRON: "materials",
            EquipmentType.MICROSCOPE_FLUORESCENCE: "biology",
            EquipmentType.SYNTHESIZER_AUTOMATED: "chemistry",
            EquipmentType.PLATE_READER: "biology",
            EquipmentType.PCR_MACHINE: "biology",
            EquipmentType.SEQUENCER_DNA: "biology",
            EquipmentType.CENTRIFUGE: "biology",
            EquipmentType.INCUBATOR: "biology",
            EquipmentType.HPLC: "chemistry",
            EquipmentType.GC_MS: "chemistry"
        }
        return domain_map.get(equipment_type, "general")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        # Check running tasks
        for equipment in self.equipment.values():
            if equipment.current_task and equipment.current_task.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": equipment.current_task.status.value,
                    "equipment_id": equipment.current_task.equipment_id,
                    "progress": "running",
                    "started_at": equipment.current_task.started_at.isoformat() if equipment.current_task.started_at else None
                }
        
        # Check queue
        for task in self.task_queue:
            if task.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": task.status.value,
                    "equipment_id": task.equipment_id,
                    "queue_position": self.task_queue.index(task) + 1,
                    "created_at": task.created_at.isoformat()
                }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            result = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": "completed" if result.success else "failed",
                "equipment_id": result.equipment_id,
                "completed_at": result.timestamp.isoformat(),
                "execution_time": result.execution_time,
                "success": result.success
            }
        
        return None
    
    def get_equipment_status(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific equipment"""
        if equipment_id not in self.equipment:
            return None
        
        equipment = self.equipment[equipment_id]
        status = {
            "equipment_id": equipment_id,
            "status": equipment.spec.status.value,
            "current_task": None,
            "queue_length": len([t for t in self.task_queue if t.equipment_id == equipment_id])
        }
        
        if equipment.current_task:
            status["current_task"] = {
                "task_id": equipment.current_task.task_id,
                "task_type": equipment.current_task.task_type,
                "started_at": equipment.current_task.started_at.isoformat() if equipment.current_task.started_at else None,
                "estimated_completion": None  # Could calculate based on duration
            }
        
        return status
    
    async def abort_task(self, task_id: str) -> bool:
        """Abort a specific task"""
        # Check running tasks
        for equipment in self.equipment.values():
            if equipment.current_task and equipment.current_task.task_id == task_id:
                success = await equipment.abort_task()
                if success:
                    equipment.current_task.status = TaskStatus.CANCELLED
                    equipment.spec.status = EquipmentStatus.AVAILABLE
                return success
        
        # Check queue
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.status = TaskStatus.CANCELLED
                self.task_queue.pop(i)
                return True
        
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_equipment = len(self.equipment)
        available = sum(1 for eq in self.equipment.values() if eq.spec.status == EquipmentStatus.AVAILABLE)
        busy = sum(1 for eq in self.equipment.values() if eq.spec.status == EquipmentStatus.BUSY)
        
        return {
            "total_equipment": total_equipment,
            "available": available,
            "busy": busy,
            "maintenance": sum(1 for eq in self.equipment.values() if eq.spec.status == EquipmentStatus.MAINTENANCE),
            "error": sum(1 for eq in self.equipment.values() if eq.spec.status == EquipmentStatus.ERROR),
            "queue_length": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "scheduler_running": self.scheduler_running
        }


# Singleton instance
_bridge_instance = None


async def get_lab_bridge() -> LabEquipmentBridge:
    """Get or create the singleton bridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = LabEquipmentBridge()
        await _bridge_instance.initialize_all_equipment()
        
    return _bridge_instance
