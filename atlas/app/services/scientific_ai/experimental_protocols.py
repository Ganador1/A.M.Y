"""
Experimental Protocols Service - AXIOM META 4
System for managing and executing experimental protocols.
"""

from __future__ import annotations

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import asyncio
from pathlib import Path

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.experimental_protocols_types import (
    ProcessRequestResult,
    ListProtocolsResult,
    GetProtocolResult,
    CreateProtocolResult,
    ValidateProtocolResult,
    ExecuteProtocolResult,
    GetExecutionStatusResult,
    ConvertProtocolResult,
    ParseHumanProtocolResult,
    OptimizeProtocolResult,
)


class ProtocolType(Enum):
    """Types of experimental protocols"""
    SYNTHESIS = "synthesis"
    ANALYSIS = "analysis"
    CHARACTERIZATION = "characterization"
    PURIFICATION = "purification"
    ASSAY = "assay"
    CULTURE = "culture"
    EXTRACTION = "extraction"
    STANDARDIZATION = "standardization"


class StepType(Enum):
    """Types of protocol steps"""
    PREPARATION = "preparation"
    REACTION = "reaction"
    INCUBATION = "incubation"
    MEASUREMENT = "measurement"
    PURIFICATION = "purification"
    ANALYSIS = "analysis"
    QUALITY_CONTROL = "quality_control"
    DOCUMENTATION = "documentation"


class ProtocolStatus(Enum):
    """Status of protocol execution"""
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProtocolStep:
    """Individual step in a protocol"""
    step_id: str
    step_type: StepType
    name: str
    description: str
    duration: float  # minutes
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    ph: Optional[float] = None
    reagents: List[Dict[str, Any]] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    safety_notes: List[str] = field(default_factory=list)
    quality_checks: List[str] = field(default_factory=list)


@dataclass
class ExperimentalProtocol:
    """Complete experimental protocol"""
    protocol_id: str
    name: str
    protocol_type: ProtocolType
    description: str
    version: str
    author: str
    created_at: datetime
    updated_at: datetime
    steps: List[ProtocolStep]
    total_duration: float  # minutes
    equipment_required: List[str]
    reagents_required: List[str]
    safety_level: str  # low, medium, high
    validation_status: ProtocolStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolExecution:
    """Execution instance of a protocol"""
    execution_id: str
    protocol_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: ProtocolStatus = ProtocolStatus.RUNNING
    current_step: Optional[str] = None
    progress: float = 0.0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    operator: Optional[str] = None


class ExperimentalProtocols(BaseService):
    """Service for managing experimental protocols"""
    
    def __init__(self):
        super().__init__("ExperimentalProtocols")
        
        # Initialize protocol library
        self.protocols = self._initialize_protocol_library()
        self.executions = {}
        
        logger.info("✅ ExperimentalProtocols initialized")
    
    def _initialize_protocol_library(self) -> Dict[str, ExperimentalProtocol]:
        """Initialize library of standard protocols"""
        protocols = {}
        
        # Protein Purification Protocol
        protocols["protein_purification"] = ExperimentalProtocol(
            protocol_id="protein_purification",
            name="Protein Purification Protocol",
            protocol_type=ProtocolType.PURIFICATION,
            description="Standard protocol for protein purification using affinity chromatography",
            version="1.0",
            author="AXIOM System",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=[
                ProtocolStep(
                    step_id="step_1",
                    step_type=StepType.PREPARATION,
                    name="Buffer Preparation",
                    description="Prepare purification buffers",
                    duration=30.0,
                    reagents=[{"name": "Tris-HCl", "concentration": "50mM", "ph": 8.0}],
                    equipment=["balance", "ph_meter"],
                    safety_notes=["Wear gloves", "Work in fume hood"]
                ),
                ProtocolStep(
                    step_id="step_2",
                    step_type=StepType.PREPARATION,
                    name="Column Preparation",
                    description="Equilibrate affinity column",
                    duration=60.0,
                    temperature=4.0,
                    equipment=["chromatography_system"],
                    parameters={"flow_rate": "1ml/min", "equilibration_volumes": 5}
                ),
                ProtocolStep(
                    step_id="step_3",
                    step_type=StepType.PURIFICATION,
                    name="Sample Loading",
                    description="Load protein sample onto column",
                    duration=120.0,
                    temperature=4.0,
                    equipment=["chromatography_system"],
                    parameters={"flow_rate": "0.5ml/min"}
                ),
                ProtocolStep(
                    step_id="step_4",
                    step_type=StepType.PURIFICATION,
                    name="Wash Step",
                    description="Wash unbound proteins",
                    duration=60.0,
                    temperature=4.0,
                    equipment=["chromatography_system"],
                    parameters={"flow_rate": "1ml/min", "wash_volumes": 10}
                ),
                ProtocolStep(
                    step_id="step_5",
                    step_type=StepType.PURIFICATION,
                    name="Elution",
                    description="Elute bound protein",
                    duration=30.0,
                    temperature=4.0,
                    equipment=["chromatography_system"],
                    parameters={"flow_rate": "1ml/min", "elution_buffer": "imidazole"}
                ),
                ProtocolStep(
                    step_id="step_6",
                    step_type=StepType.ANALYSIS,
                    name="Concentration Analysis",
                    description="Determine protein concentration",
                    duration=15.0,
                    equipment=["spectrophotometer"],
                    quality_checks=["absorbance_280nm", "purity_check"]
                )
            ],
            total_duration=315.0,
            equipment_required=["chromatography_system", "spectrophotometer", "balance", "ph_meter"],
            reagents_required=["Tris-HCl", "NaCl", "imidazole", "affinity_resin"],
            safety_level="medium",
            validation_status=ProtocolStatus.VALIDATED
        )
        
        # Cell Culture Protocol
        protocols["cell_culture"] = ExperimentalProtocol(
            protocol_id="cell_culture",
            name="Mammalian Cell Culture Protocol",
            protocol_type=ProtocolType.CULTURE,
            description="Standard protocol for mammalian cell culture maintenance",
            version="1.0",
            author="AXIOM System",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=[
                ProtocolStep(
                    step_id="step_1",
                    step_type=StepType.PREPARATION,
                    name="Media Preparation",
                    description="Prepare cell culture media",
                    duration=45.0,
                    temperature=37.0,
                    reagents=[{"name": "DMEM", "concentration": "1x"}, {"name": "FBS", "concentration": "10%"}],
                    equipment=["incubator", "sterile_hood"],
                    safety_notes=["Sterile technique required", "Work in biosafety cabinet"]
                ),
                ProtocolStep(
                    step_id="step_2",
                    step_type=StepType.PREPARATION,
                    name="Cell Thawing",
                    description="Thaw frozen cell stock",
                    duration=15.0,
                    temperature=37.0,
                    equipment=["water_bath", "centrifuge"],
                    safety_notes=["Handle liquid nitrogen carefully"]
                ),
                ProtocolStep(
                    step_id="step_3",
                    step_type=StepType.PREPARATION,
                    name="Cell Seeding",
                    description="Seed cells in culture vessel",
                    duration=30.0,
                    temperature=37.0,
                    equipment=["incubator"],
                    parameters={"cell_density": "1e5_cells/ml", "volume": "10ml"}
                ),
                ProtocolStep(
                    step_id="step_4",
                    step_type=StepType.INCUBATION,
                    name="Incubation",
                    description="Incubate cells for growth",
                    duration=1440.0,  # 24 hours
                    temperature=37.0,
                    equipment=["incubator"],
                    parameters={"co2": "5%", "humidity": "95%"}
                ),
                ProtocolStep(
                    step_id="step_5",
                    step_type=StepType.ANALYSIS,
                    name="Cell Counting",
                    description="Count and assess cell viability",
                    duration=20.0,
                    equipment=["microscope", "hemocytometer"],
                    quality_checks=["viability_check", "morphology_assessment"]
                )
            ],
            total_duration=1550.0,
            equipment_required=["incubator", "microscope", "centrifuge", "sterile_hood"],
            reagents_required=["DMEM", "FBS", "trypsin", "PBS"],
            safety_level="medium",
            validation_status=ProtocolStatus.VALIDATED
        )
        
        # Chemical Synthesis Protocol
        protocols["chemical_synthesis"] = ExperimentalProtocol(
            protocol_id="chemical_synthesis",
            name="Organic Synthesis Protocol",
            protocol_type=ProtocolType.SYNTHESIS,
            description="Standard protocol for organic compound synthesis",
            version="1.0",
            author="AXIOM System",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            steps=[
                ProtocolStep(
                    step_id="step_1",
                    step_type=StepType.PREPARATION,
                    name="Reagent Preparation",
                    description="Prepare starting materials and reagents",
                    duration=60.0,
                    equipment=["balance", "rotary_evaporator"],
                    safety_notes=["Work in fume hood", "Check MSDS"]
                ),
                ProtocolStep(
                    step_id="step_2",
                    step_type=StepType.REACTION,
                    name="Reaction Setup",
                    description="Set up reaction vessel and conditions",
                    duration=30.0,
                    temperature=25.0,
                    equipment=["reaction_vessel", "stirrer"],
                    parameters={"stirring_rate": "500_rpm", "atmosphere": "nitrogen"}
                ),
                ProtocolStep(
                    step_id="step_3",
                    step_type=StepType.REACTION,
                    name="Reaction Execution",
                    description="Execute the chemical reaction",
                    duration=480.0,  # 8 hours
                    temperature=80.0,
                    equipment=["heating_mantle", "reflux_condenser"],
                    parameters={"reflux": True, "monitoring": "TLC"}
                ),
                ProtocolStep(
                    step_id="step_4",
                    step_type=StepType.PURIFICATION,
                    name="Workup",
                    description="Quench reaction and extract product",
                    duration=120.0,
                    temperature=25.0,
                    equipment=["separatory_funnel", "rotary_evaporator"],
                    reagents=[{"name": "water", "volume": "50ml"}, {"name": "dichloromethane", "volume": "50ml"}]
                ),
                ProtocolStep(
                    step_id="step_5",
                    step_type=StepType.PURIFICATION,
                    name="Purification",
                    description="Purify product by column chromatography",
                    duration=180.0,
                    equipment=["chromatography_column", "fraction_collector"],
                    parameters={"stationary_phase": "silica_gel", "mobile_phase": "hexane_ethyl_acetate"}
                ),
                ProtocolStep(
                    step_id="step_6",
                    step_type=StepType.ANALYSIS,
                    name="Characterization",
                    description="Characterize purified product",
                    duration=60.0,
                    equipment=["nmr", "mass_spec", "ir"],
                    quality_checks=["purity_nmr", "yield_calculation"]
                )
            ],
            total_duration=930.0,
            equipment_required=["reaction_vessel", "heating_mantle", "chromatography_column", "nmr", "mass_spec"],
            reagents_required=["starting_material", "reagent", "solvent", "silica_gel"],
            safety_level="high",
            validation_status=ProtocolStatus.VALIDATED
        )
        
        return protocols
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process protocol requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "list_protocols":
                return await self.list_protocols(request_data)
            elif action == "get_protocol":
                return await self.get_protocol(request_data)
            elif action == "create_protocol":
                return await self.create_protocol(request_data)
            elif action == "validate_protocol":
                return await self.validate_protocol(request_data)
            elif action == "execute_protocol":
                return await self.execute_protocol(request_data)
            elif action == "get_execution_status":
                return await self.get_execution_status(request_data)
            elif action == "convert_protocol":
                return await self.convert_protocol(request_data)
            elif action == "parse_human_protocol":
                return await self.parse_human_protocol(request_data)
            elif action == "optimize_protocol":
                return await self.optimize_protocol(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "list_protocols", "get_protocol", "create_protocol",
                        "validate_protocol", "execute_protocol", "get_execution_status",
                        "convert_protocol", "parse_human_protocol", "optimize_protocol"
                    ]
                }
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
    
    async def list_protocols(self, request_data: ListProtocolsResult) -> ListProtocolsResult:
        """List available protocols"""
        try:
            protocol_type = request_data.get("protocol_type")
            status = request_data.get("status")
            
            filtered_protocols = self.protocols
            
            if protocol_type:
                filtered_protocols = {
                    name: protocol for name, protocol in filtered_protocols.items()
                    if protocol.protocol_type.value == protocol_type
                }
            
            if status:
                filtered_protocols = {
                    name: protocol for name, protocol in filtered_protocols.items()
                    if protocol.validation_status.value == status
                }
            
            protocol_list = [
                {
                    "protocol_id": protocol.protocol_id,
                    "name": protocol.name,
                    "type": protocol.protocol_type.value,
                    "description": protocol.description,
                    "version": protocol.version,
                    "author": protocol.author,
                    "total_duration": protocol.total_duration,
                    "equipment_required": protocol.equipment_required,
                    "reagents_required": protocol.reagents_required,
                    "safety_level": protocol.safety_level,
                    "validation_status": protocol.validation_status.value,
                    "created_at": protocol.created_at.isoformat(),
                    "updated_at": protocol.updated_at.isoformat()
                }
                for name, protocol in filtered_protocols.items()
            ]
            
            return {
                "success": True,
                "protocols": protocol_list,
                "total_count": len(protocol_list)
            }
            
        except BiologyError as e:
            return self.handle_error(e, "list_protocols")
    
    async def get_protocol(self, request_data: GetProtocolResult) -> GetProtocolResult:
        """Get detailed protocol information"""
        try:
            protocol_id = request_data.get("protocol_id")
            
            if not protocol_id or protocol_id not in self.protocols:
                return {
                    "success": False,
                    "error": f"Protocol {protocol_id} not found"
                }
            
            protocol = self.protocols[protocol_id]
            
            # Convert steps to dictionaries
            steps_data = []
            for step in protocol.steps:
                steps_data.append({
                    "step_id": step.step_id,
                    "step_type": step.step_type.value,
                    "name": step.name,
                    "description": step.description,
                    "duration": step.duration,
                    "temperature": step.temperature,
                    "pressure": step.pressure,
                    "ph": step.ph,
                    "reagents": step.reagents,
                    "equipment": step.equipment,
                    "parameters": step.parameters,
                    "safety_notes": step.safety_notes,
                    "quality_checks": step.quality_checks
                })
            
            return {
                "success": True,
                "protocol": {
                    "protocol_id": protocol.protocol_id,
                    "name": protocol.name,
                    "type": protocol.protocol_type.value,
                    "description": protocol.description,
                    "version": protocol.version,
                    "author": protocol.author,
                    "created_at": protocol.created_at.isoformat(),
                    "updated_at": protocol.updated_at.isoformat(),
                    "steps": steps_data,
                    "total_duration": protocol.total_duration,
                    "equipment_required": protocol.equipment_required,
                    "reagents_required": protocol.reagents_required,
                    "safety_level": protocol.safety_level,
                    "validation_status": protocol.validation_status.value,
                    "metadata": protocol.metadata
                }
            }
            
        except BiologyError as e:
            return self.handle_error(e, "get_protocol")
    
    async def create_protocol(self, request_data: CreateProtocolResult) -> CreateProtocolResult:
        """Create a new protocol"""
        try:
            protocol_data = request_data.get("protocol_data", {})
            
            protocol_id = protocol_data.get("protocol_id", f"protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Create protocol steps
            steps = []
            for step_data in protocol_data.get("steps", []):
                data = step_data
                step = ProtocolStep(
                    step_id=data["step_id"],
                    step_type=StepType(data["step_type"]),
                    name=data["name"],
                    description=data["description"],
                    duration=data["duration"],
                    temperature=data.get("temperature"),
                    pressure=data.get("pressure"),
                    ph=data.get("ph"),
                    reagents=data.get("reagents", []),
                    equipment=data.get("equipment", []),
                    parameters=data.get("parameters", {}),
                    safety_notes=data.get("safety_notes", []),
                    quality_checks=data.get("quality_checks", [])
                )
                steps.append(step)
            
            # Create protocol
            protocol = ExperimentalProtocol(
                protocol_id=protocol_id,
                name=protocol_data["name"],
                protocol_type=ProtocolType(protocol_data["protocol_type"]),
                description=protocol_data["description"],
                version=protocol_data.get("version", "1.0"),
                author=protocol_data.get("author", "Unknown"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                steps=steps,
                total_duration=sum(step.duration for step in steps),
                equipment_required=protocol_data.get("equipment_required", []),
                reagents_required=protocol_data.get("reagents_required", []),
                safety_level=protocol_data.get("safety_level", "medium"),
                validation_status=ProtocolStatus.DRAFT,
                metadata=protocol_data.get("metadata", {})
            )
            
            # Add to protocols library
            self.protocols[protocol_id] = protocol
            
            logger.info(f"✅ Protocol created: {protocol_id}")
            
            return {
                "success": True,
                "protocol_id": protocol_id,
                "message": f"Protocol {protocol_id} created successfully"
            }
            
        except BiologyError as e:
            return self.handle_error(e, "create_protocol")
    
    async def validate_protocol(self, request_data: ValidateProtocolResult) -> ValidateProtocolResult:
        """Validate a protocol"""
        try:
            protocol_id = request_data.get("protocol_id")
            
            if not protocol_id or protocol_id not in self.protocols:
                return {
                    "success": False,
                    "error": f"Protocol {protocol_id} not found"
                }
            
            protocol = self.protocols[protocol_id]
            
            # Perform validation checks
            validation_results = {
                "safety_check": self._validate_safety(protocol),
                "equipment_check": self._validate_equipment(protocol),
                "reagent_check": self._validate_reagents(protocol),
                "step_sequence_check": self._validate_step_sequence(protocol),
                "parameter_check": self._validate_parameters(protocol)
            }
            
            # Overall validation status
            all_valid = all(validation_results.values())
            protocol.validation_status = ProtocolStatus.VALIDATED if all_valid else ProtocolStatus.DRAFT
            
            logger.info(f"✅ Protocol validation completed: {protocol_id} - {'Valid' if all_valid else 'Invalid'}")
            
            return {
                "success": True,
                "protocol_id": protocol_id,
                "validation_results": validation_results,
                "overall_status": "valid" if all_valid else "invalid",
                "validation_status": protocol.validation_status.value
            }
            
        except BiologyError as e:
            return self.handle_error(e, "validate_protocol")
    
    async def execute_protocol(self, request_data: ExecuteProtocolResult) -> ExecuteProtocolResult:
        """Execute a protocol"""
        try:
            protocol_id = request_data.get("protocol_id")
            operator = request_data.get("operator", "system")
            
            if not protocol_id or protocol_id not in self.protocols:
                return {
                    "success": False,
                    "error": f"Protocol {protocol_id} not found"
                }
            
            protocol = self.protocols[protocol_id]
            
            # Check if protocol is validated
            if protocol.validation_status != ProtocolStatus.VALIDATED:
                return {
                    "success": False,
                    "error": f"Protocol {protocol_id} must be validated before execution"
                }
            
            # Create execution instance
            execution_id = f"exec_{protocol_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            execution = ProtocolExecution(
                execution_id=execution_id,
                protocol_id=protocol_id,
                started_at=datetime.now(),
                operator=operator
            )
            
            # Store execution
            self.executions[execution_id] = execution
            
            # Start execution in background
            asyncio.create_task(self._execute_protocol_steps(execution, protocol))
            
            logger.info(f"✅ Protocol execution started: {execution_id}")
            
            return {
                "success": True,
                "execution_id": execution_id,
                "protocol_id": protocol_id,
                "status": execution.status.value,
                "started_at": execution.started_at.isoformat()
            }
            
        except BiologyError as e:
            return self.handle_error(e, "execute_protocol")
    
    async def get_execution_status(self, request_data: GetExecutionStatusResult) -> GetExecutionStatusResult:
        """Get execution status"""
        try:
            execution_id = request_data.get("execution_id")
            
            if not execution_id or execution_id not in self.executions:
                return {
                    "success": False,
                    "error": f"Execution {execution_id} not found"
                }
            
            execution = self.executions[execution_id]
            
            return {
                "success": True,
                "execution_id": execution_id,
                "protocol_id": execution.protocol_id,
                "status": execution.status.value,
                "current_step": execution.current_step,
                "progress": execution.progress,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "operator": execution.operator,
                "results": execution.results,
                "errors": execution.errors
            }
            
        except BiologyError as e:
            return self.handle_error(e, "get_execution_status")
    
    async def convert_protocol(self, request_data: ConvertProtocolResult) -> ConvertProtocolResult:
        """Convert protocol between formats"""
        try:
            protocol_id = request_data.get("protocol_id")
            target_format = request_data.get("target_format", "json")
            
            if not protocol_id or protocol_id not in self.protocols:
                return {
                    "success": False,
                    "error": f"Protocol {protocol_id} not found"
                }
            
            protocol = self.protocols[protocol_id]
            
            # Convert to target format
            if target_format == "json":
                converted_data = self._protocol_to_json(protocol)
            elif target_format == "yaml":
                converted_data = self._protocol_to_yaml(protocol)
            elif target_format == "human_readable":
                converted_data = self._protocol_to_human_readable(protocol)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {target_format}"
                }
            
            return {
                "success": True,
                "protocol_id": protocol_id,
                "target_format": target_format,
                "converted_data": converted_data
            }
            
        except BiologyError as e:
            return self.handle_error(e, "convert_protocol")

    async def parse_human_protocol(self, request_data: ParseHumanProtocolResult) -> ParseHumanProtocolResult:
        """Parsea un protocolo en texto humano a estructura ejecutable"""
        try:
            text = request_data.get("text", "").strip()
            protocol_name = request_data.get("name", "Human Parsed Protocol")
            author = request_data.get("author", "Unknown")
            protocol_type = request_data.get("protocol_type", "analysis")
            if not text:
                return {"success": False, "error": "No protocol text provided"}

            import re

            steps: List[ProtocolStep] = []
            equipment_required: List[str] = []
            reagents_required: List[str] = []

            # Heurística: líneas por paso. Formato sugerido:
            # Step 1: Nombre - Descripción (duration=30m; temp=25C; pressure=1atm; ph=7; equipment=centrifuge|incubator; reagents=NaCl:1g|Water:50ml)
            for i, line in enumerate([l for l in text.splitlines() if l.strip()] , start=1):
                name_match = re.search(r":\s*(.*?)\s*-", line)
                name = name_match.group(1).strip() if name_match else f"Step {i}"
                desc_match = re.search(r"-\s*(.*?)\s*\(", line)
                description = desc_match.group(1).strip() if desc_match else line.strip()
                duration_min = 15.0
                temp = None
                pressure = None
                ph = None
                params = {}
                reagents = []
                equipment = []
                meta_match = re.search(r"\((.*)\)", line)
                if meta_match:
                    meta = meta_match.group(1)
                    # duration
                    dm = re.search(r"duration\s*=\s*([0-9]+)m", meta, re.IGNORECASE)
                    if dm:
                        duration_min = float(dm.group(1))
                    tm = re.search(r"temp(erature)?\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*C", meta, re.IGNORECASE)
                    if tm:
                        temp = float(tm.group(2))
                    pm = re.search(r"pressure\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*atm", meta, re.IGNORECASE)
                    if pm:
                        pressure = float(pm.group(1))
                    phm = re.search(r"ph\s*=\s*([0-9]+(?:\.[0-9]+)?)", meta, re.IGNORECASE)
                    if phm:
                        ph = float(phm.group(1))
                    eqm = re.search(r"equipment\s*=\s*([^;]+)", meta, re.IGNORECASE)
                    if eqm:
                        equipment = [e.strip() for e in eqm.group(1).split("|") if e.strip()]
                        equipment_required.extend(equipment)
                    rrm = re.search(r"reagents\s*=\s*([^;]+)", meta, re.IGNORECASE)
                    if rrm:
                        for r in [x.strip() for x in rrm.group(1).split("|") if x.strip()]:
                            # NaCl:1g
                            if ":" in r:
                                rname, rqty = r.split(":", 1)
                                reagents.append({"name": rname.strip(), "quantity": rqty.strip()})
                                reagents_required.append(rname.strip())
                            else:
                                reagents.append({"name": r})
                                reagents_required.append(r)

                step = ProtocolStep(
                    step_id=f"step_{i}",
                    step_type=StepType.ANALYSIS if i == 1 else StepType.MEASUREMENT,
                    name=name,
                    description=description,
                    duration=duration_min,
                    temperature=temp,
                    pressure=pressure,
                    ph=ph,
                    reagents=reagents,
                    equipment=equipment,
                    parameters=params,
                )
                steps.append(step)

            protocol_id = f"human_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            protocol = ExperimentalProtocol(
                protocol_id=protocol_id,
                name=protocol_name,
                protocol_type=ProtocolType(protocol_type),
                description=f"Parsed from human text ({len(steps)} steps)",
                version="1.0",
                author=author,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                steps=steps,
                total_duration=sum(s.duration for s in steps),
                equipment_required=sorted(list(set(equipment_required))),
                reagents_required=sorted(list(set(reagents_required))),
                safety_level="medium",
                validation_status=ProtocolStatus.DRAFT,
            )

            self.protocols[protocol_id] = protocol
            return {"success": True, "protocol_id": protocol_id}
        except BiologyError as e:
            return self.handle_error(e, "parse_human_protocol")

    async def optimize_protocol(self, request_data: OptimizeProtocolResult) -> OptimizeProtocolResult:
        """Optimiza parámetros del protocolo en base a resultados/objetivos"""
        try:
            protocol_id = request_data.get("protocol_id")
            objective = request_data.get("objective", "minimize_time")  # or maximize_yield
            constraints = request_data.get("constraints", {})
            if not protocol_id or protocol_id not in self.protocols:
                return {"success": False, "error": f"Protocol {protocol_id} not found"}

            protocol = self.protocols[protocol_id]
            updated_steps: List[Dict[str, Any]] = []

            for step in protocol.steps:
                new_duration = step.duration
                new_temp = step.temperature
                # Heurística: si objetivo es minimizar tiempo, reduce 10% hasta un mínimo
                if objective == "minimize_time":
                    new_duration = max(step.duration * 0.9, 5.0)
                elif objective == "maximize_yield":
                    # sube temperatura moderadamente si hay temperatura definida
                    if step.temperature is not None:
                        new_temp = min(step.temperature + 2.0, 95.0)

                updated_steps.append({
                    "step_id": step.step_id,
                    "old_duration": step.duration,
                    "new_duration": new_duration,
                    "old_temperature": step.temperature,
                    "new_temperature": new_temp,
                })

                step.duration = new_duration
                step.temperature = new_temp

            protocol.updated_at = datetime.now()
            return {
                "success": True,
                "protocol_id": protocol_id,
                "objective": objective,
                "updated_steps": updated_steps,
                "new_total_duration": sum(s.duration for s in protocol.steps),
            }
        except BiologyError as e:
            return self.handle_error(e, "optimize_protocol")
    
    def _validate_safety(self, protocol: ExperimentalProtocol) -> bool:
        """Validate safety aspects of protocol"""
        # Check safety level consistency
        if protocol.safety_level == "high":
            # High safety protocols should have safety notes for each step
            for step in protocol.steps:
                if not step.safety_notes:
                    return False
        return True
    
    def _validate_equipment(self, protocol: ExperimentalProtocol) -> bool:
        """Validate equipment requirements"""
        # Check that all equipment is specified
        required_equipment = set(protocol.equipment_required)
        used_equipment = set()
        
        for step in protocol.steps:
            used_equipment.update(step.equipment)
        
        return required_equipment.issubset(used_equipment)
    
    def _validate_reagents(self, protocol: ExperimentalProtocol) -> bool:
        """Validate reagent requirements"""
        # Check that all reagents are specified
        required_reagents = set(protocol.reagents_required)
        used_reagents = set()
        
        for step in protocol.steps:
            for reagent in step.reagents:
                used_reagents.add(reagent.get("name", ""))
        
        return required_reagents.issubset(used_reagents)
    
    def _validate_step_sequence(self, protocol: ExperimentalProtocol) -> bool:
        """Validate step sequence logic"""
        # Check that steps are in logical order
        step_types = [step.step_type for step in protocol.steps]
        
        # Preparation steps should come first
        if step_types and step_types[0] != StepType.PREPARATION:
            return False
        
        return True
    
    def _validate_parameters(self, protocol: ExperimentalProtocol) -> bool:
        """Validate parameter consistency"""
        # Check that critical parameters are within reasonable ranges
        for step in protocol.steps:
            if step.temperature and (step.temperature < -200 or step.temperature > 1000):
                return False
            if step.pressure and (step.pressure < 0 or step.pressure > 1000):
                return False
            if step.ph and (step.ph < 0 or step.ph > 14):
                return False
        
        return True
    
    async def _execute_protocol_steps(self, execution: ProtocolExecution, protocol: ExperimentalProtocol):
        """Execute protocol steps"""
        try:
            execution.status = ProtocolStatus.RUNNING
            
            for i, step in enumerate(protocol.steps):
                execution.current_step = step.step_id
                execution.progress = (i / len(protocol.steps)) * 100
                
                # Simulate step execution
                await asyncio.sleep(0.1)  # Simulate step duration
                
                # Simulate step results
                execution.results[step.step_id] = {
                    "status": "completed",
                    "duration": step.duration,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Mark execution as completed
            execution.status = ProtocolStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.progress = 100.0
            
            logger.info(f"✅ Protocol execution completed: {execution.execution_id}")
            
        except BiologyError as e:
            execution.status = ProtocolStatus.FAILED
            execution.errors.append(str(e))
            logger.error(f"❌ Protocol execution failed: {execution.execution_id} - {e}")
    
    def _protocol_to_json(self, protocol: ExperimentalProtocol) -> str:
        """Convert protocol to JSON format"""
        protocol_dict = {
            "protocol_id": protocol.protocol_id,
            "name": protocol.name,
            "type": protocol.protocol_type.value,
            "description": protocol.description,
            "version": protocol.version,
            "author": protocol.author,
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_type": step.step_type.value,
                    "name": step.name,
                    "description": step.description,
                    "duration": step.duration,
                    "temperature": step.temperature,
                    "pressure": step.pressure,
                    "ph": step.ph,
                    "reagents": step.reagents,
                    "equipment": step.equipment,
                    "parameters": step.parameters,
                    "safety_notes": step.safety_notes,
                    "quality_checks": step.quality_checks
                }
                for step in protocol.steps
            ],
            "total_duration": protocol.total_duration,
            "equipment_required": protocol.equipment_required,
            "reagents_required": protocol.reagents_required,
            "safety_level": protocol.safety_level,
            "validation_status": protocol.validation_status.value
        }
        
        return json.dumps(protocol_dict, indent=2)
    
    def _protocol_to_yaml(self, protocol: ExperimentalProtocol) -> str:
        """Convert protocol to YAML format"""
        protocol_dict = {
            "protocol_id": protocol.protocol_id,
            "name": protocol.name,
            "type": protocol.protocol_type.value,
            "description": protocol.description,
            "version": protocol.version,
            "author": protocol.author,
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_type": step.step_type.value,
                    "name": step.name,
                    "description": step.description,
                    "duration": step.duration,
                    "temperature": step.temperature,
                    "pressure": step.pressure,
                    "ph": step.ph,
                    "reagents": step.reagents,
                    "equipment": step.equipment,
                    "parameters": step.parameters,
                    "safety_notes": step.safety_notes,
                    "quality_checks": step.quality_checks
                }
                for step in protocol.steps
            ],
            "total_duration": protocol.total_duration,
            "equipment_required": protocol.equipment_required,
            "reagents_required": protocol.reagents_required,
            "safety_level": protocol.safety_level,
            "validation_status": protocol.validation_status.value
        }
        
        return yaml.dump(protocol_dict, default_flow_style=False)
    
    def _protocol_to_human_readable(self, protocol: ExperimentalProtocol) -> str:
        """Convert protocol to human-readable format"""
        output = []
        output.append(f"Protocol: {protocol.name}")
        output.append(f"Type: {protocol.protocol_type.value}")
        output.append(f"Description: {protocol.description}")
        output.append(f"Version: {protocol.version}")
        output.append(f"Author: {protocol.author}")
        output.append(f"Total Duration: {protocol.total_duration} minutes")
        output.append(f"Safety Level: {protocol.safety_level}")
        output.append("")
        
        output.append("Equipment Required:")
        for equipment in protocol.equipment_required:
            output.append(f"  - {equipment}")
        output.append("")
        
        output.append("Reagents Required:")
        for reagent in protocol.reagents_required:
            output.append(f"  - {reagent}")
        output.append("")
        
        output.append("Steps:")
        for i, step in enumerate(protocol.steps, 1):
            output.append(f"{i}. {step.name}")
            output.append(f"   Type: {step.step_type.value}")
            output.append(f"   Description: {step.description}")
            output.append(f"   Duration: {step.duration} minutes")
            
            if step.temperature:
                output.append(f"   Temperature: {step.temperature}°C")
            if step.pressure:
                output.append(f"   Pressure: {step.pressure} atm")
            if step.ph:
                output.append(f"   pH: {step.ph}")
            
            if step.reagents:
                output.append("   Reagents:")
                for reagent in step.reagents:
                    output.append(f"     - {reagent}")
            
            if step.equipment:
                output.append("   Equipment:")
                for equipment in step.equipment:
                    output.append(f"     - {equipment}")
            
            if step.safety_notes:
                output.append("   Safety Notes:")
                for note in step.safety_notes:
                    output.append(f"     - {note}")
            
            output.append("")
        
        return "\n".join(output)
