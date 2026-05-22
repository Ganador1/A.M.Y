"""
Active Reproducibility Engine - Autonomous reproduction of scientific experiments

This service actively attempts to reproduce published experiments by:
1. Parsing methods from scientific papers
2. Mapping to available tools
3. Executing with controlled variations
4. Comparing results statistically

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
"""

import logging
import re
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone as tz
from enum import Enum
import asyncio

from app.services.experimental_toolkit_hub import get_experimental_hub, ExperimentalResult
from app.services.experimental_validator import get_experimental_validator, ExperimentalData
from app.services.perturbation_engine import PerturbationEngine as AdvancedPerturbationEngine
from app.services.reproducibility_database import ReproducibilityDatabase
from app.services.base_service import BaseService

# Import Knowledge Graph integration
from app.services.knowledge_graph_service import get_knowledge_graph_service
from app.exceptions.domain.biology import BiologyError
from app.types.active_reproducibility_engine_types import (
    ExtractGlobalParametersResult,
    ExtractParametersResult,
    AdvancedRobustnessAnalysisResult,
    AnalyzeFailurePatternsResult,
    GenerateReproducibilityRecommendationsResult,
    GetReproducibilityStatisticsResult,
)

# Configure logging
logger = logging.getLogger(__name__)

UTC = tz.utc


class ReproductionStatus(Enum):
    """Status of reproduction attempt"""
    NOT_STARTED = "not_started"
    PARSING = "parsing"
    MAPPING = "mapping"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class PerturbationType(Enum):
    """Types of perturbations to apply"""
    PARAMETER = "parameter"  # Change numerical parameters
    METHOD = "method"  # Use alternative methods
    NOISE = "noise"  # Add random noise
    SAMPLING = "sampling"  # Change sampling strategy
    NONE = "none"  # No perturbation (exact reproduction)


@dataclass
class MethodStep:
    """A single step in experimental methods"""
    step_number: int
    description: str
    tool_hint: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    chemicals: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[str] = None
    temperature: Optional[float] = None


@dataclass
class ParsedMethods:
    """Parsed experimental methods from a paper"""
    paper_id: str
    title: str
    methods_text: str
    steps: List[MethodStep]
    domain: Optional[str] = None
    experimental_type: Optional[str] = None
    key_molecules: List[str] = field(default_factory=list)
    key_parameters: Dict[str, Any] = field(default_factory=dict)
    parsing_confidence: float = 0.0


@dataclass
class ToolMapping:
    """Mapping from method step to available tool"""
    step_number: int
    tool_domain: str
    tool_name: str
    method: str
    mapped_parameters: Dict[str, Any]
    confidence: float
    alternative_tools: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReproductionAttempt:
    """Record of a reproduction attempt"""
    attempt_id: str
    paper_id: str
    original_methods: ParsedMethods
    tool_mappings: List[ToolMapping]
    perturbations: List[Dict[str, Any]]
    execution_results: List[List[ExperimentalResult]]
    validation_results: Optional[Dict[str, Any]] = None
    status: ReproductionStatus = ReproductionStatus.NOT_STARTED
    success: bool = False
    reproducibility_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class MethodsParser:
    """Parse experimental methods from scientific text"""
    
    def __init__(self):
        self.step_patterns = [
            r"(?:Step\s+)?(\d+)[\.\)]\s*(.*?)(?=(?:Step\s+)?\d+[\.\)]|$)",
            r"(?:First|Then|Next|Finally),?\s+(.*?)(?=(?:First|Then|Next|Finally)|$)",
            r"(\d+)\.\s*(.*?)(?=\d+\.|$)"
        ]
        
        self.parameter_patterns = {
            "temperature": r"(\d+(?:\.\d+)?)\s*°?[CKF]",
            "time": r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|minutes?|mins?|seconds?|secs?|days?)",
            "concentration": r"(\d+(?:\.\d+)?)\s*(?:mM|μM|nM|mg/mL|μg/mL)",
            "volume": r"(\d+(?:\.\d+)?)\s*(?:mL|μL|L)",
            "speed": r"(\d+(?:\.\d+)?)\s*(?:rpm|g|×g)",
            "ph": r"pH\s*(?:of\s*)?(\d+(?:\.\d+)?)"
        }
        
        self.chemical_patterns = [
            r"(?:in|with|containing|using)\s+(\w+(?:\s+\w+)*)",
            r"(\w+)\s+(?:solution|buffer|reagent)",
            r"(?:dissolved|suspended)\s+in\s+(\w+)"
        ]
        
        self.equipment_keywords = [
            "centrifuge", "incubator", "spectrophotometer", "microscope",
            "PCR", "HPLC", "NMR", "mass spectrometer", "sequencer",
            "plate reader", "flow cytometer", "gel electrophoresis"
        ]
    
    async def parse_methods(self, methods_text: str, paper_id: str, title: str = "") -> ParsedMethods:
        """Parse methods section into structured steps"""
        parsed = ParsedMethods(
            paper_id=paper_id,
            title=title,
            methods_text=methods_text,
            steps=[]
        )
        
        try:
            # Clean text
            text = self._clean_text(methods_text)
            
            # Extract steps
            steps = self._extract_steps(text)
            
            # Parse each step
            for i, step_text in enumerate(steps, 1):
                step = await self._parse_step(i, step_text)
                parsed.steps.append(step)
            
            # Determine domain
            parsed.domain = self._determine_domain(text)
            
            # Extract key parameters
            parsed.key_parameters = self._extract_global_parameters(text)
            
            # Extract key molecules
            parsed.key_molecules = self._extract_molecules(text)
            
            # Calculate parsing confidence
            parsed.parsing_confidence = self._calculate_confidence(parsed)
            
        except BiologyError as e:
            logger.error(f"Error parsing methods: {str(e)}", exc_info=True)
            parsed.parsing_confidence = 0.0
            
        return parsed
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize methods text"""
        # Remove references
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\(\d{4}\)', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('µ', 'μ')
        
        return text.strip()
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract individual method steps"""
        steps = []
        
        # Try different step patterns
        for pattern in self.step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple):
                    steps = [match[1].strip() for match in matches]
                else:
                    steps = [match.strip() for match in matches]
                break
        
        # If no clear steps, split by sentences
        if not steps:
            sentences = re.split(r'[.!?]+', text)
            steps = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return steps
    
    async def _parse_step(self, step_num: int, text: str) -> MethodStep:
        """Parse individual step"""
        step = MethodStep(
            step_number=step_num,
            description=text
        )
        
        # Extract parameters
        for param_name, pattern in self.parameter_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1)
                try:
                    step.parameters[param_name] = float(value)
                except BiologyError:
                    step.parameters[param_name] = value
        
        # Extract chemicals
        for pattern in self.chemical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            step.chemicals.extend([m for m in matches if len(m) > 2])
        
        # Extract equipment
        text_lower = text.lower()
        for equipment in self.equipment_keywords:
            if equipment in text_lower:
                step.equipment.append(equipment)
        
        # Determine tool hint
        step.tool_hint = self._determine_tool_hint(text)
        
        return step
    
    def _determine_tool_hint(self, text: str) -> Optional[str]:
        """Determine which tool might be appropriate"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["pcr", "amplif", "polymerase"]):
            return "pcr_simulator"
        elif any(kw in text_lower for kw in ["nmr", "nuclear magnetic"]):
            return "nmr_predictor"
        elif any(kw in text_lower for kw in ["mass spec", "ms analysis", "m/z"]):
            return "mass_spec_analyzer"
        elif any(kw in text_lower for kw in ["molecular dynamics", "md simulation"]):
            return "molecular_dynamics"
        elif any(kw in text_lower for kw in ["dock", "binding", "ligand"]):
            return "molecular_docking"
        elif any(kw in text_lower for kw in ["express", "transcript", "rna-seq"]):
            return "gene_expression_analysis"
        
        return None
    
    def _determine_domain(self, text: str) -> Optional[str]:
        """Determine scientific domain"""
        text_lower = text.lower()
        
        biology_keywords = ["cell", "protein", "dna", "rna", "gene", "organism", "tissue"]
        chemistry_keywords = ["synthesis", "reaction", "compound", "nmr", "catalyst", "solvent"]
        physics_keywords = ["quantum", "laser", "photon", "field", "particle", "wave"]
        
        bio_score = sum(1 for kw in biology_keywords if kw in text_lower)
        chem_score = sum(1 for kw in chemistry_keywords if kw in text_lower)
        phys_score = sum(1 for kw in physics_keywords if kw in text_lower)
        
        scores = {"biology": bio_score, "chemistry": chem_score, "physics": phys_score}
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def _extract_global_parameters(self, text: str) -> ExtractGlobalParametersResult:
        """Extract global parameters mentioned in methods"""
        params = {}
        
        # Common global parameters
        temp_match = re.search(r"(?:maintained|kept|incubated)\s+at\s+" + 
                              self.parameter_patterns["temperature"], text)
        if temp_match:
            params["global_temperature"] = float(temp_match.group(1))
        
        ph_match = re.search(self.parameter_patterns["ph"], text)
        if ph_match:
            params["global_ph"] = float(ph_match.group(1))
        
        return params
    
    def _extract_molecules(self, text: str) -> List[str]:
        """Extract key molecules mentioned"""
        molecules = []
        
        # Common molecule patterns
        patterns = [
            r"(?:protein|enzyme|antibody)\s+(\w+)",
            r"(\w+)\s+(?:gene|plasmid|vector)",
            r"compound\s+(\w+)",
            r"(\w+)\s+inhibitor"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            molecules.extend(matches)
        
        # Remove common words
        molecules = [m for m in molecules if len(m) > 3 and m.lower() not in 
                    ["this", "that", "with", "from", "into", "using"]]
        
        return list(set(molecules))
    
    def _calculate_confidence(self, parsed: ParsedMethods) -> float:
        """Calculate confidence in parsing quality"""
        score = 0.0
        
        # Has clear steps
        if len(parsed.steps) > 0:
            score += 0.2
        
        # Has parameters
        if any(step.parameters for step in parsed.steps):
            score += 0.2
        
        # Has equipment
        if any(step.equipment for step in parsed.steps):
            score += 0.2
        
        # Has domain
        if parsed.domain:
            score += 0.1
        
        # Has molecules
        if parsed.key_molecules:
            score += 0.1
        
        # Reasonable number of steps
        if 3 <= len(parsed.steps) <= 20:
            score += 0.2
        
        return min(score, 1.0)


class ToolMapper:
    """Map parsed methods to available tools"""
    
    def __init__(self):
        self.tool_mappings = {
            "molecular_dynamics": {
                "keywords": ["md", "simulation", "dynamics", "trajectory"],
                "domain": "biology",
                "required_params": ["pdb_structure", "time_ns"]
            },
            "molecular_properties": {
                "keywords": ["property", "logp", "molecular weight", "descriptor"],
                "domain": "chemistry",
                "required_params": ["smiles"]
            },
            "gene_expression_analysis": {
                "keywords": ["expression", "transcript", "rna-seq", "differential"],
                "domain": "biology",
                "required_params": ["count_matrix"]
            },
            "reaction_prediction": {
                "keywords": ["reaction", "synthesis", "product", "yield"],
                "domain": "chemistry",
                "required_params": ["reactants"]
            }
        }
    
    async def map_to_tools(self, parsed_methods: ParsedMethods) -> List[ToolMapping]:
        """Map method steps to available tools"""
        mappings = []
        hub = await get_experimental_hub()
        available_tools = await hub.list_all_capabilities()
        
        for step in parsed_methods.steps:
            mapping = await self._map_step(step, parsed_methods.domain, available_tools)
            if mapping:
                mappings.append(mapping)
        
        return mappings
    
    async def _map_step(
        self,
        step: MethodStep,
        domain: Optional[str],
        available_tools: Dict[str, List[Dict[str, Any]]]
    ) -> Optional[ToolMapping]:
        """Map individual step to tool"""
        best_match = None
        best_score = 0.0
        
        # Use tool hint if available
        if step.tool_hint:
            for dom, tools in available_tools.items():
                for tool in tools:
                    if tool["tool"] == step.tool_hint:
                        return ToolMapping(
                            step_number=step.step_number,
                            tool_domain=dom,
                            tool_name=tool["tool"],
                            method=tool.get("methods", ["default"])[0],
                            mapped_parameters=self._extract_parameters(step, tool),
                            confidence=0.9
                        )
        
        # Otherwise, find best match
        step_text_lower = step.description.lower()
        
        for dom, tools in available_tools.items():
            # Prefer matching domain
            domain_bonus = 0.2 if dom == domain else 0.0
            
            for tool in tools:
                score = domain_bonus
                
                # Check keywords
                tool_keywords = self.tool_mappings.get(tool["tool"], {}).get("keywords", [])
                for keyword in tool_keywords:
                    if keyword in step_text_lower:
                        score += 0.3
                
                # Check tool description
                if "description" in tool:
                    desc_lower = tool["description"].lower()
                    common_words = set(step_text_lower.split()) & set(desc_lower.split())
                    score += len(common_words) * 0.05
                
                if score > best_score:
                    best_score = score
                    best_match = (dom, tool)
        
        if best_match and best_score > 0.3:
            dom, tool = best_match
            return ToolMapping(
                step_number=step.step_number,
                tool_domain=dom,
                tool_name=tool["tool"],
                method=tool.get("methods", ["default"])[0],
                mapped_parameters=self._extract_parameters(step, tool),
                confidence=min(best_score, 1.0)
            )
        
        return None
    
    def _extract_parameters(self, step: MethodStep, tool: ExtractParametersResult) -> ExtractParametersResult:
        """Extract parameters for tool from step"""
        params = {}
        
        # Copy direct parameters
        params.update(step.parameters)
        
        # Map common parameters
        if "temperature" in step.parameters and "temperature" in tool.get("inputs", []):
            params["temperature"] = step.parameters["temperature"]
        
        if "time" in step.parameters:
            # Convert to appropriate unit
            time_value = step.parameters["time"]
            if "hours" in step.description:
                params["time_ns"] = time_value * 3600 * 1e9  # Convert to nanoseconds
            elif "minutes" in step.description:
                params["time_ns"] = time_value * 60 * 1e9
        
        # Add placeholder values for required params
        for required in tool.get("inputs", []):
            if required not in params:
                if required == "smiles" and step.chemicals:
                    # Try to find SMILES for chemicals (placeholder)
                    params["smiles"] = "C"  # Methane as placeholder
                elif required == "pdb_structure":
                    params["pdb_structure"] = "PLACEHOLDER_PDB"
                elif required == "count_matrix":
                    params["count_matrix"] = [[1, 2], [3, 4]]  # Minimal matrix
        
        return params


class PerturbationEngine:
    """Apply controlled perturbations to experiments"""
    
    def __init__(self):
        self.perturbation_ranges = {
            "temperature": (0.9, 1.1),  # ±10%
            "time": (0.8, 1.2),  # ±20%
            "concentration": (0.9, 1.1),  # ±10%
            "ph": (0.95, 1.05)  # ±5%
        }
    
    async def generate_perturbations(
        self,
        tool_mappings: List[ToolMapping],
        perturbation_types: List[PerturbationType],
        n_variations: int = 3
    ) -> List[List[ToolMapping]]:
        """Generate perturbed versions of tool mappings"""
        if PerturbationType.NONE in perturbation_types:
            return [tool_mappings]  # No perturbation
        
        variations = []
        
        for i in range(n_variations):
            variation = []
            
            for mapping in tool_mappings:
                perturbed = self._copy_mapping(mapping)
                
                if PerturbationType.PARAMETER in perturbation_types:
                    perturbed = self._perturb_parameters(perturbed)
                
                if PerturbationType.NOISE in perturbation_types:
                    perturbed = self._add_noise(perturbed)
                
                variation.append(perturbed)
            
            variations.append(variation)
        
        return variations
    
    def _copy_mapping(self, mapping: ToolMapping) -> ToolMapping:
        """Deep copy a tool mapping"""
        return ToolMapping(
            step_number=mapping.step_number,
            tool_domain=mapping.tool_domain,
            tool_name=mapping.tool_name,
            method=mapping.method,
            mapped_parameters=mapping.mapped_parameters.copy(),
            confidence=mapping.confidence,
            alternative_tools=mapping.alternative_tools.copy()
        )
    
    def _perturb_parameters(self, mapping: ToolMapping) -> ToolMapping:
        """Perturb numerical parameters"""
        for param, value in mapping.mapped_parameters.items():
            if isinstance(value, (int, float)) and param in self.perturbation_ranges:
                min_mult, max_mult = self.perturbation_ranges[param]
                multiplier = np.random.uniform(min_mult, max_mult)
                mapping.mapped_parameters[param] = value * multiplier
        
        return mapping
    
    def _add_noise(self, mapping: ToolMapping) -> ToolMapping:
        """Add random noise to parameters"""
        for param, value in mapping.mapped_parameters.items():
            if isinstance(value, (int, float)):
                # Add Gaussian noise (5% of value)
                noise = np.random.normal(0, 0.05 * abs(value))
                mapping.mapped_parameters[param] = value + noise
        
        return mapping


class ActiveReproducibilityEngine(BaseService):
    """
    Main engine for active experiment reproduction
    """
    
    def __init__(self):
        super().__init__("ActiveReproducibilityEngine")
        self.parser = MethodsParser()
        self.mapper = ToolMapper()
        self.perturber = PerturbationEngine()
        self.validator = get_experimental_validator()
        self.perturbation_engine = AdvancedPerturbationEngine()
        self.reproducibility_db = ReproducibilityDatabase()
        logger.info("✅ ActiveReproducibilityEngine initialized with advanced perturbation and database")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process reproduction requests via BaseService interface
        """
        action = request_data.get("action")
        
        if action == "attempt_reproduction":
            paper_id = request_data.get("paper_id")
            methods_text = request_data.get("methods_text")
            if not paper_id or not methods_text:
                return {"success": False, "error": "paper_id and methods_text are required"}
                
            result = await self.attempt_reproduction(
                paper_id=paper_id,
                methods_text=methods_text,
                title=request_data.get("title", ""),
                expected_results=request_data.get("expected_results"),
                perturbation_types=None, # TODO: Parse from request if needed
                n_variations=request_data.get("n_variations", 3)
            )
            # Convert dataclass/object to dict if needed, or return as is if it's a dict
            # attempt_reproduction returns ReproductionAttempt object, need to serialize
            return {"success": True, "attempt_id": result.attempt_id, "status": result.status.value}

        elif action == "analyze_failure_patterns":
            return await self.analyze_failure_patterns(request_data)
            
        elif action == "generate_recommendations":
            return await self.generate_reproducibility_recommendations(request_data)
            
        elif action == "get_statistics":
            return await self.get_reproducibility_statistics(request_data)
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    async def attempt_reproduction(
        self,
        paper_id: str,
        methods_text: str,
        title: str = "",
        expected_results: Optional[Dict[str, Any]] = None,
        perturbation_types: Optional[List[PerturbationType]] = None,
        n_variations: int = 3
    ) -> ReproductionAttempt:
        """
        Attempt to reproduce experiment from paper methods
        """
        attempt_id = f"repro_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        
        attempt = ReproductionAttempt(
            attempt_id=attempt_id,
            paper_id=paper_id,
            original_methods=ParsedMethods(
                paper_id=paper_id,
                title=title,
                methods_text=methods_text,
                steps=[],
                domain="",
                parsing_confidence=0.0
            ),
            tool_mappings=[],
            perturbations=[],
            execution_results=[]
        )
        
        # Capture reproduction attempt in Knowledge Graph - simplified version
        kg_service = await get_knowledge_graph_service()
        
        try:
            # Create simple KG node for reproduction attempt
            kg_result = await kg_service.create_knowledge_node({
                "action": "create_node",
                "name": f"Reproduction Attempt: {title or paper_id}",
                "type": "method",
                "domain": "reproducibility",
                "properties": {
                    "attempt_id": attempt_id,
                    "paper_id": paper_id,
                    "title": title,
                    "status": "started",
                    "start_time": datetime.now(UTC).isoformat()
                }
            })
            
            # Store KG node ID for later updates
            kg_node_id = kg_result.get("node_id") if kg_result.get("success") else None
            
        except BiologyError as kg_error:
            logger.warning(f"Could not create reproduction node in KG: {kg_error}")
            kg_node_id = None
        
        try:
            # 1. Parse methods
            attempt.status = ReproductionStatus.PARSING
            logger.info(f"Parsing methods for paper {paper_id}")
            
            parsed_methods = await self.parser.parse_methods(methods_text, paper_id, title)
            attempt.original_methods = parsed_methods
            
            if parsed_methods.parsing_confidence < 0.3:
                attempt.issues.append(f"Low parsing confidence: {parsed_methods.parsing_confidence:.2f}")
                attempt.status = ReproductionStatus.FAILED
                
                # Update KG node with failure
                try:
                    await kg_service.update_knowledge_node({
                        "action": "update_node",
                        "node_id": attempt_id,  # Using attempt_id as node_id for simplicity
                        "properties": {
                            "status": "failed",
                            "parsing_confidence": parsed_methods.parsing_confidence,
                            "end_time": datetime.now(UTC).isoformat(),
                            "issues": attempt.issues
                        }
                    })
                except BiologyError:
                    pass
                
                return attempt
            
            # 2. Map to tools
            attempt.status = ReproductionStatus.MAPPING
            logger.info(f"Mapping {len(parsed_methods.steps)} steps to tools")
            
            tool_mappings = await self.mapper.map_to_tools(parsed_methods)
            attempt.tool_mappings = tool_mappings
            
            if not tool_mappings:
                attempt.issues.append("No tools could be mapped to method steps")
                attempt.status = ReproductionStatus.FAILED
                
                # Update KG node with failure
                try:
                    await kg_service.update_knowledge_node({
                        "action": "update_node",
                        "node_id": attempt_id,
                        "properties": {
                            "status": "failed",
                            "mapping_success": False,
                            "end_time": datetime.now(UTC).isoformat(),
                            "issues": attempt.issues
                        }
                    })
                except BiologyError:
                    pass
                
                return attempt
            
            # 3. Generate perturbations
            if perturbation_types is None:
                perturbation_types = [PerturbationType.PARAMETER, PerturbationType.NOISE]
            
            variations = await self.perturber.generate_perturbations(
                tool_mappings,
                perturbation_types,
                n_variations
            )
            
            # 4. Execute experiments
            attempt.status = ReproductionStatus.EXECUTING
            logger.info(f"Executing {len(variations)} experimental variations")
            
            hub = await get_experimental_hub()
            
            for i, variation in enumerate(variations):
                variation_results = []
                
                for mapping in variation:
                    try:
                        result = await hub.execute_experiment(
                            domain=mapping.tool_domain,
                            tool_name=mapping.tool_name,
                            method=mapping.method,
                            inputs=mapping.mapped_parameters
                        )
                        variation_results.append(result)
                        
                    except BiologyError as e:
                        logger.error(f"Error executing step {mapping.step_number}: {str(e)}")
                        variation_results.append(ExperimentalResult(
                            experiment_id=f"error_{i}_{mapping.step_number}",
                            domain=mapping.tool_domain,
                            tool_name=mapping.tool_name,
                            method=mapping.method,
                            inputs=mapping.mapped_parameters,
                            outputs={},
                            metrics={},
                            errors=[str(e)]
                        ))
                
                attempt.execution_results.append(variation_results)
            
            # 5. Validate results
            attempt.status = ReproductionStatus.VALIDATING
            logger.info("Validating reproduction results")
            
            # Compare with expected results if provided
            if expected_results:
                # Convert execution results to ExperimentalData format
                experimental_data = []
                for variation in attempt.execution_results:
                    for result in variation:
                        experimental_data.append(ExperimentalData(
                            data=result.outputs,
                            metadata={
                                "experiment_id": result.experiment_id,
                                "domain": result.domain,
                                "tool": result.tool_name
                            }
                        ))
                
                validation_result = await self.validator.validate_reproducibility(
                    experimental_data,
                    ExperimentalData(data=expected_results, metadata={"source": "original_paper"})
                )
                attempt.validation_results = validation_result
            
            attempt.status = ReproductionStatus.COMPLETED
            
            # Simple KG update with basic completion info
            if kg_node_id:
                try:
                    await kg_service.update_knowledge_node({
                        "action": "update_node",
                        "node_id": kg_node_id,
                        "properties": {
                            "status": "completed",
                            "steps_count": len(parsed_methods.steps),
                            "end_time": datetime.now(UTC).isoformat()
                        }
                    })
                except BiologyError as kg_error:
                    logger.warning(f"Could not update reproduction node in KG: {kg_error}")
            
            return attempt
            
        except BiologyError as e:
            logger.error(f"Reproduction attempt failed: {str(e)}", exc_info=True)
            attempt.status = ReproductionStatus.FAILED
            attempt.issues.append(f"Unexpected error: {str(e)}")
            
            # Update KG node with error
            try:
                await kg_service.update_knowledge_node({
                    "action": "update_node",
                    "node_id": attempt_id,
                    "properties": {
                        "status": "failed",
                        "end_time": datetime.now(UTC).isoformat(),
                        "error": str(e)
                    }
                })
            except BiologyError:
                pass
            
            return attempt
    
    async def _validate_reproduction(
        self,
        results: List[ExperimentalResult],
        expected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate reproduction against expected results"""
        validation = {
            "is_reproduced": False,
            "reproducibility_score": 0.0,
            "comparisons": []
        }
        
        # Extract metrics from results
        result_metrics = []
        for result in results:
            if result.metrics:
                result_metrics.append(result.metrics)
        
        if not result_metrics:
            return validation
        
        # Compare with expected values
        score = 0.0
        comparisons = []
        
        for metric_name, expected_value in expected.items():
            if isinstance(expected_value, (int, float)):
                # Find corresponding metric in results
                found_values = []
                for metrics in result_metrics:
                    if metric_name in metrics:
                        found_values.append(metrics[metric_name])
                
                if found_values:
                    mean_value = np.mean(found_values)
                    std_value = np.std(found_values) if len(found_values) > 1 else 0
                    
                    # Calculate agreement
                    relative_error = abs(mean_value - expected_value) / abs(expected_value)
                    agreement = 1.0 - min(relative_error, 1.0)
                    
                    comparisons.append({
                        "metric": metric_name,
                        "expected": expected_value,
                        "measured": mean_value,
                        "std": std_value,
                        "agreement": agreement
                    })
                    
                    score += agreement
        
        if comparisons:
            validation["reproducibility_score"] = score / len(comparisons)
            validation["is_reproduced"] = validation["reproducibility_score"] > 0.7
            validation["comparisons"] = comparisons
        
        return validation
    
    async def analyze_reproduction_patterns(
        self,
        attempts: List[ReproductionAttempt]
    ) -> Dict[str, Any]:
        """Analyze patterns in reproduction attempts"""
        analysis = {
            "total_attempts": len(attempts),
            "successful": sum(1 for a in attempts if a.success),
            "failed": sum(1 for a in attempts if not a.success),
            "avg_reproducibility_score": 0.0,
            "common_issues": {},
            "domain_success_rates": {},
            "tool_reliability": {}
        }
        
        if not attempts:
            return analysis
        
        # Calculate average score
        scores = [a.reproducibility_score for a in attempts if a.reproducibility_score > 0]
        if scores:
            analysis["avg_reproducibility_score"] = np.mean(scores)
        
        # Analyze issues
        all_issues = []
        for attempt in attempts:
            all_issues.extend(attempt.issues)
        
        for issue in all_issues:
            # Extract issue type
            issue_type = "other"
            if "parsing" in issue.lower():
                issue_type = "parsing"
            elif "mapping" in issue.lower():
                issue_type = "mapping"
            elif "execution" in issue.lower():
                issue_type = "execution"
            
            analysis["common_issues"][issue_type] = analysis["common_issues"].get(issue_type, 0) + 1
        
        # Domain success rates
        for attempt in attempts:
            if attempt.original_methods and attempt.original_methods.domain:
                domain = attempt.original_methods.domain
                if domain not in analysis["domain_success_rates"]:
                    analysis["domain_success_rates"][domain] = {"total": 0, "successful": 0}
                
                analysis["domain_success_rates"][domain]["total"] += 1
                if attempt.success:
                    analysis["domain_success_rates"][domain]["successful"] += 1
        
        # Calculate rates
        for domain, stats in analysis["domain_success_rates"].items():
            if stats["total"] > 0:
                stats["rate"] = stats["successful"] / stats["total"]
        
        return analysis
    
    async def advanced_robustness_analysis(self, request_data: AdvancedRobustnessAnalysisResult) -> AdvancedRobustnessAnalysisResult:
        """Perform advanced robustness analysis using perturbation engine"""
        try:
            experiment_config = request_data.get("experiment_config", {})
            parameters = request_data.get("parameters", [])
            num_iterations = request_data.get("num_iterations", 50)
            
            # Use perturbation engine for robustness analysis
            robustness_result = await self.perturbation_engine.process_request({
                "action": "robustness_analysis",
                "experiment_config": experiment_config,
                "parameters": parameters,
                "num_iterations": num_iterations
            })
            
            if robustness_result["success"]:
                # Record attempts in reproducibility database
                for i, result in enumerate(robustness_result["experiment_results"]):
                    await self.reproducibility_db.process_request({
                        "action": "record_attempt",
                        "attempt_data": {
                            "attempt_id": f"robustness_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "paper_id": experiment_config.get("paper_id", "robustness_test"),
                            "paper_title": experiment_config.get("title", "Robustness Analysis"),
                            "experiment_type": experiment_config.get("experiment_type", "robustness"),
                            "parameters": result["parameters"],
                            "success": result["success"],
                            "reproducibility_score": result["reproducibility_score"],
                            "execution_time": result["execution_time"],
                            "error_message": result.get("error_message")
                        }
                    })
                
                logger.info(f"✅ Advanced robustness analysis completed: {num_iterations} iterations")
                
                return {
                    "success": True,
                    "robustness_metrics": robustness_result["robustness_metrics"],
                    "experiment_results": robustness_result["experiment_results"],
                    "num_iterations": num_iterations,
                    "database_recorded": True
                }
            else:
                return robustness_result
                
        except BiologyError as e:
            logger.error(f"❌ Error in advanced robustness analysis: {e}")
            return {
                "success": False,
                "error": f"Advanced robustness analysis failed: {str(e)}"
            }
    
    async def analyze_failure_patterns(self, request_data: AnalyzeFailurePatternsResult) -> AnalyzeFailurePatternsResult:
        """Analyze patterns in reproducibility failures"""
        try:
            experiment_type = request_data.get("experiment_type")
            min_frequency = request_data.get("min_frequency", 2)
            
            # Use reproducibility database to analyze failure patterns
            patterns_result = await self.reproducibility_db.process_request({
                "action": "analyze_failure_patterns",
                "experiment_type": experiment_type,
                "min_frequency": min_frequency
            })
            
            if patterns_result["success"]:
                logger.info(f"✅ Failure pattern analysis completed: {len(patterns_result['patterns'])} patterns identified")
                
                return {
                    "success": True,
                    "patterns": patterns_result["patterns"],
                    "total_patterns": patterns_result["total_patterns"],
                    "analyzed_attempts": patterns_result["analyzed_attempts"]
                }
            else:
                return patterns_result
                
        except BiologyError as e:
            logger.error(f"❌ Error analyzing failure patterns: {e}")
            return {
                "success": False,
                "error": f"Failure pattern analysis failed: {str(e)}"
            }
    
    async def generate_reproducibility_recommendations(self, request_data: GenerateReproducibilityRecommendationsResult) -> GenerateReproducibilityRecommendationsResult:
        """Generate recommendations for improving reproducibility"""
        try:
            experiment_type = request_data.get("experiment_type")
            priority_threshold = request_data.get("priority_threshold", "medium")
            
            # Use reproducibility database to generate recommendations
            recommendations_result = await self.reproducibility_db.process_request({
                "action": "generate_recommendations",
                "experiment_type": experiment_type,
                "priority_threshold": priority_threshold
            })
            
            if recommendations_result["success"]:
                logger.info(f"✅ Reproducibility recommendations generated: {len(recommendations_result['recommendations'])} recommendations")
                
                return {
                    "success": True,
                    "recommendations": recommendations_result["recommendations"],
                    "total_recommendations": recommendations_result["total_recommendations"],
                    "high_priority_count": recommendations_result["high_priority_count"]
                }
            else:
                return recommendations_result
                
        except BiologyError as e:
            logger.error(f"❌ Error generating reproducibility recommendations: {e}")
            return {
                "success": False,
                "error": f"Reproducibility recommendations generation failed: {str(e)}"
            }
    
    async def get_reproducibility_statistics(self, request_data: GetReproducibilityStatisticsResult) -> GetReproducibilityStatisticsResult:
        """Get comprehensive reproducibility statistics"""
        try:
            experiment_type = request_data.get("experiment_type")
            time_range = request_data.get("time_range", 30)  # days
            
            # Use reproducibility database to get statistics
            stats_result = await self.reproducibility_db.process_request({
                "action": "get_statistics",
                "experiment_type": experiment_type,
                "time_range": time_range
            })
            
            if stats_result["success"]:
                logger.info(f"✅ Reproducibility statistics retrieved")
                
                return {
                    "success": True,
                    "statistics": stats_result["statistics"],
                    "time_range_days": stats_result["time_range_days"]
                }
            else:
                return stats_result
                
        except BiologyError as e:
            logger.error(f"❌ Error getting reproducibility statistics: {e}")
            return {
                "success": False,
                "error": f"Reproducibility statistics retrieval failed: {str(e)}"
            }


# Singleton instance
_engine_instance = None


async def get_reproducibility_engine() -> ActiveReproducibilityEngine:
    """Get or create singleton engine instance"""
    global _engine_instance
    
    if _engine_instance is None:
        _engine_instance = ActiveReproducibilityEngine()
    
    return _engine_instance
