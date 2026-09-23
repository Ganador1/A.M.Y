#!/usr/bin/env python3
"""
AXIOM Domain Templates Generator Service
Automatic generation of domain-specific research templates and workflows

This service enables AXIOM to create customized research templates for different
scientific domains, automatically generating optimized workflows based on field-specific
best practices and methodologies.

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import copy
import asyncio
from app.exceptions.domain.biology import BiologyError
from app.types.domain_templates_service_types import (
    GetServiceStatusResult,
)

logger = logging.getLogger(__name__)

class ScientificDomain(Enum):
    """Scientific research domains for template generation"""
    COMPUTATIONAL_BIOLOGY = "computational_biology"
    MATERIALS_SCIENCE = "materials_science"
    QUANTUM_PHYSICS = "quantum_physics"
    CLIMATE_SCIENCE = "climate_science"
    DRUG_DISCOVERY = "drug_discovery"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    NANOTECHNOLOGY = "nanotechnology"
    RENEWABLE_ENERGY = "renewable_energy"
    BIOTECHNOLOGY = "biotechnology"
    SPACE_SCIENCE = "space_science"
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    BIOLOGY = "biology"
    ENGINEERING = "engineering"
    ENVIRONMENTAL_SCIENCE = "environmental_science"

class ExperimentType(Enum):
    """Types of experiments for template generation"""
    SIMULATION = "simulation"
    WET_LAB = "wet_lab"
    COMPUTATIONAL = "computational"
    DATA_ANALYSIS = "data_analysis"
    SYNTHESIS = "synthesis"
    CHARACTERIZATION = "characterization"
    MODELING = "modeling"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    SCREENING = "screening"

class TemplateComplexity(Enum):
    """Complexity levels for generated templates"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class WorkflowStep:
    """Individual step in a scientific workflow"""
    id: str
    name: str
    description: str
    category: str
    inputs: List[str]
    outputs: List[str]
    parameters: Dict[str, Any]
    duration_estimate: timedelta
    dependencies: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    safety_requirements: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)

@dataclass
class ExperimentTemplate:
    """Complete experiment template for a specific domain"""
    id: str
    name: str
    domain: ScientificDomain
    experiment_type: ExperimentType
    complexity: TemplateComplexity
    description: str
    objectives: List[str]
    workflow_steps: List[WorkflowStep]
    required_equipment: List[str]
    required_materials: List[str]
    required_software: List[str]
    estimated_duration: timedelta
    estimated_cost: float
    success_metrics: List[str]
    safety_protocols: List[str]
    quality_controls: List[str]
    data_management: Dict[str, Any]
    literature_references: List[str]
    created_at: datetime
    last_updated: datetime
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

@dataclass
class DomainKnowledge:
    """Domain-specific knowledge base for template generation"""
    domain: ScientificDomain
    common_methodologies: List[str]
    standard_protocols: List[str]
    typical_equipment: List[str]
    common_materials: List[str]
    software_tools: List[str]
    best_practices: List[str]
    safety_considerations: List[str]
    validation_methods: List[str]
    data_standards: List[str]
    publication_guidelines: List[str]

class DomainTemplatesService:
    """
    Autonomous Domain Templates Generator
    
    This service automatically generates domain-specific research templates by:
    1. Analyzing scientific best practices for each domain
    2. Creating optimized workflows based on experiment types
    3. Incorporating safety protocols and quality controls
    4. Generating customizable templates for different complexity levels
    5. Maintaining a knowledge base of domain-specific methodologies
    """
    
    def __init__(self):
        self.templates: Dict[str, ExperimentTemplate] = {}
        self.domain_knowledge: Dict[ScientificDomain, DomainKnowledge] = {}
        self.workflow_library: Dict[str, WorkflowStep] = {}
        self.template_usage_stats: Dict[str, int] = {}
        self.customizations: Dict[str, Dict[str, Any]] = {}
        
        # Initialize domain knowledge base
        self._initialize_domain_knowledge()
        # Load common workflow steps
        self._initialize_workflow_library()
        logger.info("🧬 Domain Templates Generator Service initialized")
    
    def _initialize_domain_knowledge(self):
        """Initialize domain-specific knowledge bases"""
        
        # Computational Biology
        self.domain_knowledge[ScientificDomain.COMPUTATIONAL_BIOLOGY] = DomainKnowledge(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,
            common_methodologies=[
                "Molecular dynamics simulations",
                "Protein structure prediction",
                "Genome-wide association studies (GWAS)",
                "RNA-seq analysis",
                "Phylogenetic analysis",
                "Systems biology modeling",
                "Machine learning for genomics"
            ],
            standard_protocols=[
                "FAIR data principles",
                "NCBI submission guidelines",
                "UniProt annotation standards",
                "PDB structure validation",
                "GO ontology annotation"
            ],
            typical_equipment=[
                "High-performance computing clusters",
                "GPU workstations",
                "DNA/RNA sequencers",
                "Mass spectrometers",
                "NMR spectrometers"
            ],
            common_materials=[
                "Genomic datasets",
                "Protein sequences",
                "Chemical compound libraries",
                "Reference genomes",
                "Experimental proteomics data"
            ],
            software_tools=[
                "GROMACS", "NAMD", "PyMOL", "Chimera", "R/Bioconductor",
                "Python/BioPython", "BLAST", "Clustal", "MUSCLE", "RAxML"
            ],
            best_practices=[
                "Version control for analysis scripts",
                "Reproducible computational environments",
                "Statistical significance testing",
                "Multiple hypothesis correction",
                "Cross-validation for ML models"
            ],
            safety_considerations=[
                "Data privacy protection",
                "Ethical approval for human data",
                "Secure data storage",
                "Access control implementation"
            ],
            validation_methods=[
                "Cross-validation",
                "Independent test sets",
                "Literature comparison",
                "Experimental validation",
                "Peer review protocols"
            ],
            data_standards=[
                "FAIR data principles",
                "OMICS data standards",
                "Metadata annotation",
                "Standardized file formats"
            ],
            publication_guidelines=[
                "ARRIVE guidelines for animal studies",
                "CONSORT for clinical trials",
                "STARD for diagnostic studies"
            ]
        )
        
        # Materials Science
        self.domain_knowledge[ScientificDomain.MATERIALS_SCIENCE] = DomainKnowledge(
            domain=ScientificDomain.MATERIALS_SCIENCE,
            common_methodologies=[
                "X-ray diffraction (XRD)",
                "Scanning electron microscopy (SEM)",
                "Transmission electron microscopy (TEM)",
                "Atomic force microscopy (AFM)",
                "Density functional theory (DFT)",
                "Molecular beam epitaxy (MBE)",
                "Sol-gel synthesis"
            ],
            standard_protocols=[
                "ASTM material testing standards",
                "ISO quality management",
                "NIST reference materials",
                "Crystallographic databases"
            ],
            typical_equipment=[
                "X-ray diffractometers",
                "Electron microscopes",
                "Furnaces and reactors",
                "Mechanical testing machines",
                "Spectrometers"
            ],
            common_materials=[
                "Metals and alloys",
                "Ceramics",
                "Polymers",
                "Composites",
                "Nanomaterials"
            ],
            software_tools=[
                "VASP", "Quantum ESPRESSO", "Materials Studio", 
                "VESTA", "CrystalMaker", "Origin", "ImageJ"
            ],
            best_practices=[
                "Sample preparation protocols",
                "Contamination prevention",
                "Statistical analysis of properties",
                "Reproducible synthesis conditions"
            ],
            safety_considerations=[
                "Chemical safety protocols",
                "Radiation safety for X-rays",
                "High-temperature handling",
                "Nanoparticle exposure prevention"
            ],
            validation_methods=[
                "Multiple characterization techniques",
                "Reference standard comparison",
                "Round-robin testing",
                "Independent synthesis verification"
            ],
            data_standards=[
                "Materials genome initiative standards",
                "Crystallographic information files (CIF)",
                "FAIR data for materials"
            ],
            publication_guidelines=[
                "Materials characterization reporting",
                "Synthesis protocol documentation",
                "Property measurement standards"
            ]
        )
        
        # Add more domains as needed
        logger.info(f"🧬 Initialized knowledge base for {len(self.domain_knowledge)} scientific domains")
    
    def _initialize_workflow_library(self):
        """Initialize library of common workflow steps"""
        
        # Data Collection Steps
        self.workflow_library["data_collection_planning"] = WorkflowStep(
            id="data_collection_planning",
            name="Data Collection Planning",
            description="Plan and design data collection strategy",
            category="planning",
            inputs=["research_objectives", "resources_available"],
            outputs=["data_collection_plan", "sampling_strategy"],
            parameters={"sample_size": "int", "collection_timeline": "str"},
            duration_estimate=timedelta(days=2),
            tools_required=["planning_software", "statistical_tools"],
            best_practices=[
                "Define clear data requirements",
                "Consider statistical power",
                "Plan for data quality checks"
            ]
        )
        
        self.workflow_library["literature_review"] = WorkflowStep(
            id="literature_review",
            name="Literature Review",
            description="Comprehensive review of existing literature",
            category="research",
            inputs=["research_topic", "search_terms"],
            outputs=["literature_summary", "knowledge_gaps"],
            parameters={"databases": "list", "time_range": "str"},
            duration_estimate=timedelta(days=7),
            tools_required=["database_access", "reference_manager"],
            best_practices=[
                "Use multiple databases",
                "Document search strategy",
                "Assess study quality"
            ]
        )
        
        # Experimental Steps
        self.workflow_library["sample_preparation"] = WorkflowStep(
            id="sample_preparation",
            name="Sample Preparation",
            description="Prepare samples for analysis or experimentation",
            category="experimental",
            inputs=["raw_materials", "preparation_protocol"],
            outputs=["prepared_samples", "preparation_log"],
            parameters={"batch_size": "int", "quality_criteria": "dict"},
            duration_estimate=timedelta(days=1),
            tools_required=["lab_equipment", "safety_equipment"],
            safety_requirements=[
                "Wear appropriate PPE",
                "Follow chemical safety protocols",
                "Document all procedures"
            ]
        )
        
        # Analysis Steps
        self.workflow_library["statistical_analysis"] = WorkflowStep(
            id="statistical_analysis",
            name="Statistical Analysis",
            description="Perform statistical analysis of experimental data",
            category="analysis",
            inputs=["experimental_data", "analysis_plan"],
            outputs=["statistical_results", "analysis_report"],
            parameters={"significance_level": "float", "test_type": "str"},
            duration_estimate=timedelta(days=3),
            tools_required=["statistical_software", "computing_resources"],
            validation_criteria=[
                "Check data assumptions",
                "Validate statistical tests",
                "Interpret results correctly"
            ]
        )
        
        logger.info(f"🧬 Initialized workflow library with {len(self.workflow_library)} common steps")
    
    async def generate_template(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        custom_requirements: Optional[Dict[str, Any]] = None
    ) -> ExperimentTemplate:
        """
        🧬 Generate Domain-Specific Research Template
        
        Creates a customized research template based on domain expertise,
        experiment type, and complexity requirements.
        """
        logger.info(f"🧬 Generating template: {domain.value} - {experiment_type.value} - {complexity.value}")
        
        try:
            template_id = f"{domain.value}_{experiment_type.value}_{complexity.value}_{int(datetime.now().timestamp() * 1000000)}"
            
            # Get domain knowledge
            domain_info = self.domain_knowledge.get(domain)
            if not domain_info:
                raise ValueError(f"No knowledge base available for domain: {domain.value}")
            
            # Generate template based on domain and experiment type
            template = await self._create_template_structure(
                template_id,
                domain,
                experiment_type,
                complexity,
                domain_info,
                custom_requirements or {}
            )
            
            # Store template
            self.templates[template_id] = template
            
            # Update usage stats
            self.template_usage_stats[template_id] = 0
            
            logger.info(f"🧬 Generated template {template_id} with {len(template.workflow_steps)} steps")
            return template
            
        except BiologyError as e:
            logger.error(f"❌ Error generating template: {str(e)}")
            raise
    
    async def _create_template_structure(
        self,
        template_id: str,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        domain_info: DomainKnowledge,
        custom_requirements: Dict[str, Any]
    ) -> ExperimentTemplate:
        """Create the complete template structure"""
        
        # Generate template name and description
        template_name = self._generate_template_name(domain, experiment_type, complexity)
        description = self._generate_template_description(domain, experiment_type, complexity)
        
        # Generate objectives
        objectives = self._generate_objectives(domain, experiment_type, complexity)
        
        # Generate workflow steps
        workflow_steps = await self._generate_workflow_steps(domain, experiment_type, complexity, domain_info)
        
        # Determine required resources
        equipment = self._determine_required_equipment(domain, experiment_type, complexity, domain_info)
        materials = self._determine_required_materials(domain, experiment_type, complexity, domain_info)
        software = self._determine_required_software(domain, experiment_type, complexity, domain_info)
        
        # Estimate duration and cost
        estimated_duration = self._estimate_duration(workflow_steps, complexity)
        estimated_cost = self._estimate_cost(equipment, materials, complexity)
        
        # Generate success metrics and protocols
        success_metrics = self._generate_success_metrics(domain, experiment_type)
        safety_protocols = self._generate_safety_protocols(domain, experiment_type, domain_info)
        quality_controls = self._generate_quality_controls(domain, experiment_type)
        
        # Generate data management plan
        data_management = self._generate_data_management_plan(domain, experiment_type)
        
        # Add literature references
        literature_references = self._generate_literature_references(domain, experiment_type)
        
        # Create template
        template = ExperimentTemplate(
            id=template_id,
            name=template_name,
            domain=domain,
            experiment_type=experiment_type,
            complexity=complexity,
            description=description,
            objectives=objectives,
            workflow_steps=workflow_steps,
            required_equipment=equipment,
            required_materials=materials,
            required_software=software,
            estimated_duration=estimated_duration,
            estimated_cost=estimated_cost,
            success_metrics=success_metrics,
            safety_protocols=safety_protocols,
            quality_controls=quality_controls,
            data_management=data_management,
            literature_references=literature_references,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            tags=self._generate_tags(domain, experiment_type, complexity)
        )
        
        return template
    
    def _generate_template_name(
        self, 
        domain: ScientificDomain, 
        experiment_type: ExperimentType, 
        complexity: TemplateComplexity
    ) -> str:
        """Generate descriptive template name"""
        domain_names = {
            ScientificDomain.COMPUTATIONAL_BIOLOGY: "Computational Biology",
            ScientificDomain.MATERIALS_SCIENCE: "Materials Science",
            ScientificDomain.QUANTUM_PHYSICS: "Quantum Physics",
            ScientificDomain.DRUG_DISCOVERY: "Drug Discovery"
        }
        
        experiment_names = {
            ExperimentType.SIMULATION: "Simulation",
            ExperimentType.WET_LAB: "Wet Lab Experiment",
            ExperimentType.COMPUTATIONAL: "Computational Analysis",
            ExperimentType.SYNTHESIS: "Chemical Synthesis"
        }
        
        complexity_names = {
            TemplateComplexity.BASIC: "Basic",
            TemplateComplexity.INTERMEDIATE: "Intermediate",
            TemplateComplexity.ADVANCED: "Advanced",
            TemplateComplexity.EXPERT: "Expert"
        }
        
        return f"{complexity_names.get(complexity, 'Standard')} {domain_names.get(domain, domain.value.title())} {experiment_names.get(experiment_type, experiment_type.value.title())}"
    
    def _generate_template_description(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType, 
        complexity: TemplateComplexity
    ) -> str:
        """Generate detailed template description"""
        descriptions = {
            (ScientificDomain.COMPUTATIONAL_BIOLOGY, ExperimentType.SIMULATION): 
                "Comprehensive computational biology simulation template for molecular dynamics, protein folding, and systems biology modeling.",
            (ScientificDomain.MATERIALS_SCIENCE, ExperimentType.SYNTHESIS):
                "Advanced materials synthesis template including characterization and property evaluation protocols.",
            (ScientificDomain.DRUG_DISCOVERY, ExperimentType.SCREENING):
                "High-throughput drug screening template with compound library preparation and bioassay protocols."
        }
        
        default_desc = f"Standardized {domain.value.replace('_', ' ')} template for {experiment_type.value.replace('_', ' ')} experiments with {complexity.value} complexity level."
        
        return descriptions.get((domain, experiment_type), default_desc)
    
    def _generate_objectives(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity
    ) -> List[str]:
        """Generate research objectives for the template"""
        base_objectives = [
            "Conduct systematic investigation following best practices",
            "Generate high-quality, reproducible results",
            "Document methodology for future reference"
        ]
        
        domain_specific = {
            ScientificDomain.COMPUTATIONAL_BIOLOGY: [
                "Analyze biological systems using computational methods",
                "Validate computational predictions with experimental data",
                "Contribute to understanding of biological mechanisms"
            ],
            ScientificDomain.MATERIALS_SCIENCE: [
                "Characterize material properties comprehensively",
                "Establish structure-property relationships",
                "Optimize synthesis or processing conditions"
            ]
        }
        
        objectives = base_objectives.copy()
        if domain in domain_specific:
            objectives.extend(domain_specific[domain])
        
        return objectives
    
    async def _generate_workflow_steps(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        domain_info: DomainKnowledge
    ) -> List[WorkflowStep]:
        """Generate workflow steps based on domain and experiment type"""
        steps = []
        
        # Always start with literature review and planning
        steps.extend([
            self.workflow_library["literature_review"],
            self.workflow_library["data_collection_planning"]
        ])
        
        # Add domain-specific steps
        if experiment_type in [ExperimentType.WET_LAB, ExperimentType.SYNTHESIS]:
            steps.append(self.workflow_library["sample_preparation"])
        
        # Add complexity-based steps
        if complexity in [TemplateComplexity.ADVANCED, TemplateComplexity.EXPERT]:
            # Add advanced statistical analysis
            steps.append(self.workflow_library["statistical_analysis"])
        
        # Add domain-specific experimental steps
        domain_steps = await self._generate_domain_specific_steps(domain, experiment_type, complexity)
        steps.extend(domain_steps)
        
        return steps
    
    async def _generate_domain_specific_steps(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity
    ) -> List[WorkflowStep]:
        """Generate domain-specific workflow steps"""
        steps = []
        
        if domain == ScientificDomain.COMPUTATIONAL_BIOLOGY:
            if experiment_type == ExperimentType.SIMULATION:
                steps.append(WorkflowStep(
                    id="molecular_dynamics_setup",
                    name="Molecular Dynamics Setup",
                    description="Prepare molecular systems for MD simulation",
                    category="computational",
                    inputs=["protein_structure", "force_field"],
                    outputs=["simulation_system", "topology_files"],
                    parameters={"temperature": "float", "pressure": "float"},
                    duration_estimate=timedelta(days=2),
                    tools_required=["GROMACS", "PyMOL"],
                    best_practices=["Validate initial structure", "Equilibrate system properly"]
                ))
        
        elif domain == ScientificDomain.MATERIALS_SCIENCE:
            if experiment_type == ExperimentType.SYNTHESIS:
                steps.append(WorkflowStep(
                    id="material_synthesis",
                    name="Material Synthesis",
                    description="Synthesize target material using optimized conditions",
                    category="experimental",
                    inputs=["precursor_materials", "synthesis_protocol"],
                    outputs=["synthesized_material", "synthesis_log"],
                    parameters={"temperature": "float", "time": "float", "atmosphere": "str"},
                    duration_estimate=timedelta(days=3),
                    tools_required=["furnace", "inert_atmosphere"],
                    safety_requirements=["High temperature safety", "Chemical handling protocols"]
                ))
        
        return steps
    
    def _determine_required_equipment(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        domain_info: DomainKnowledge
    ) -> List[str]:
        """Determine required equipment based on domain and experiment type"""
        base_equipment = ["Computer workstation", "Data storage", "Safety equipment"]
        
        # Add domain-specific equipment
        domain_equipment = domain_info.typical_equipment[:3]  # Top 3 for basic templates
        
        if complexity in [TemplateComplexity.ADVANCED, TemplateComplexity.EXPERT]:
            domain_equipment = domain_info.typical_equipment  # All equipment for advanced
        
        return base_equipment + domain_equipment
    
    def _determine_required_materials(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        domain_info: DomainKnowledge
    ) -> List[str]:
        """Determine required materials"""
        materials = domain_info.common_materials.copy()
        
        # Add experiment-specific materials
        if experiment_type == ExperimentType.WET_LAB:
            materials.extend(["Laboratory reagents", "Consumables", "Standard solutions"])
        
        return materials
    
    def _determine_required_software(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity,
        domain_info: DomainKnowledge
    ) -> List[str]:
        """Determine required software tools"""
        base_software = ["Data analysis software", "Statistical software", "Documentation tools"]
        domain_software = domain_info.software_tools
        
        return base_software + domain_software
    
    def _estimate_duration(self, workflow_steps: List[WorkflowStep], complexity: TemplateComplexity) -> timedelta:
        """Estimate total duration for the template"""
        total_days = sum(step.duration_estimate.days for step in workflow_steps)
        
        # Complexity multiplier
        multipliers = {
            TemplateComplexity.BASIC: 1.0,
            TemplateComplexity.INTERMEDIATE: 1.3,
            TemplateComplexity.ADVANCED: 1.7,
            TemplateComplexity.EXPERT: 2.2
        }
        
        adjusted_days = int(total_days * multipliers.get(complexity, 1.0))
        return timedelta(days=adjusted_days)
    
    def _estimate_cost(self, equipment: List[str], materials: List[str], complexity: TemplateComplexity) -> float:
        """Estimate cost for the template execution"""
        base_cost = 5000.0  # Base cost in USD
        
        # Equipment cost factor
        equipment_cost = len(equipment) * 500.0
        
        # Materials cost factor  
        materials_cost = len(materials) * 200.0
        
        # Complexity multiplier
        complexity_multipliers = {
            TemplateComplexity.BASIC: 1.0,
            TemplateComplexity.INTERMEDIATE: 1.5,
            TemplateComplexity.ADVANCED: 2.5,
            TemplateComplexity.EXPERT: 4.0
        }
        
        total_cost = (base_cost + equipment_cost + materials_cost) * complexity_multipliers.get(complexity, 1.0)
        return round(total_cost, 2)
    
    def _generate_success_metrics(
        self, 
        domain: ScientificDomain, 
        experiment_type: ExperimentType
    ) -> List[str]:
        """Generate success metrics for the template"""
        base_metrics = [
            "Data quality meets established standards",
            "Experimental reproducibility demonstrated",
            "Results align with stated objectives"
        ]
        
        domain_metrics = {
            ScientificDomain.COMPUTATIONAL_BIOLOGY: [
                "Model validation metrics within acceptable ranges",
                "Statistical significance achieved (p < 0.05)",
                "Biological relevance of findings demonstrated"
            ],
            ScientificDomain.MATERIALS_SCIENCE: [
                "Material properties characterized comprehensively",
                "Synthesis reproducibility confirmed",
                "Structure-property relationships established"
            ]
        }
        
        metrics = base_metrics.copy()
        if domain in domain_metrics:
            metrics.extend(domain_metrics[domain])
        
        return metrics
    
    def _generate_safety_protocols(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        domain_info: DomainKnowledge
    ) -> List[str]:
        """Generate safety protocols"""
        base_protocols = [
            "Conduct safety risk assessment",
            "Ensure proper training for all personnel",
            "Maintain emergency contact information"
        ]
        
        return base_protocols + domain_info.safety_considerations
    
    def _generate_quality_controls(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType
    ) -> List[str]:
        """Generate quality control measures"""
        return [
            "Implement data backup procedures",
            "Conduct regular calibration checks",
            "Document all deviations from protocol",
            "Perform independent verification of key results",
            "Maintain detailed experimental logs"
        ]
    
    def _generate_data_management_plan(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType
    ) -> Dict[str, Any]:
        """Generate data management plan"""
        return {
            "storage_requirements": {
                "primary_storage": "Institutional data repository",
                "backup_frequency": "Daily",
                "retention_period": "10 years",
                "access_controls": "Role-based permissions"
            },
            "data_formats": {
                "raw_data": ["CSV", "HDF5", "proprietary instrument formats"],
                "processed_data": ["JSON", "CSV", "NetCDF"],
                "documentation": ["Markdown", "PDF"]
            },
            "metadata_standards": [
                "Dublin Core",
                "Domain-specific ontologies",
                "Experimental parameters"
            ],
            "sharing_policy": {
                "public_release": "After publication",
                "restricted_access": "Collaborators only during project",
                "embargo_period": "12 months"
            }
        }
    
    def _generate_literature_references(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType
    ) -> List[str]:
        """Generate relevant literature references"""
        return [
            "Domain-specific methodology papers",
            "Best practices guidelines",
            "Validation and benchmarking studies",
            "Recent review articles in the field"
        ]
    
    def _generate_tags(
        self,
        domain: ScientificDomain,
        experiment_type: ExperimentType,
        complexity: TemplateComplexity
    ) -> List[str]:
        """Generate tags for template categorization"""
        return [
            domain.value,
            experiment_type.value,
            complexity.value,
            "automated_template",
            "best_practices"
        ]
    
    async def customize_template(
        self,
        template_id: str,
        customizations: Dict[str, Any]
    ) -> ExperimentTemplate:
        """
        ✏️ Customize Existing Template
        
        Modify an existing template based on specific requirements
        while maintaining scientific rigor and best practices.
        """
        logger.info(f"✏️ Customizing template {template_id}")
        
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Create customized copy (deep copy to avoid modifying original)
        customized_id = f"{template_id}_custom_{int(datetime.now().timestamp() * 1000000)}"
        customized_template = copy.deepcopy(template)
        customized_template.id = customized_id
        customized_template.last_updated = datetime.now()
        
        # Apply customizations
        if "objectives" in customizations:
            customized_template.objectives.extend(customizations["objectives"])
        
        if "additional_steps" in customizations:
            for step_config in customizations["additional_steps"]:
                # Create WorkflowStep from config
                custom_step = WorkflowStep(
                    id=step_config["id"],
                    name=step_config["name"],
                    description=step_config["description"],
                    category=step_config["category"],
                    inputs=step_config["inputs"],
                    outputs=step_config["outputs"],
                    parameters=step_config["parameters"],
                    duration_estimate=step_config["duration_estimate"],
                    dependencies=step_config.get("dependencies", []),
                    tools_required=step_config.get("tools_required", []),
                    safety_requirements=step_config.get("safety_requirements", []),
                    best_practices=step_config.get("best_practices", []),
                    validation_criteria=step_config.get("validation_criteria", [])
                )
                customized_template.workflow_steps.append(custom_step)
        
        if "equipment" in customizations:
            customized_template.required_equipment.extend(customizations["equipment"])
        
        # Store customized template
        self.templates[customized_id] = customized_template
        self.customizations[customized_id] = customizations
        
        logger.info(f"✏️ Template customized: {customized_id}")
        return customized_template
    
    async def export_template(
        self,
        template_id: str,
        format_type: str = "yaml"
    ) -> str:
        """
        📄 Export Template
        
        Export template in various formats for external use
        or integration with other systems.
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        # Convert to exportable format
        export_data = {
            "template_info": {
                "id": template.id,
                "name": template.name,
                "domain": template.domain.value,
                "experiment_type": template.experiment_type.value,
                "complexity": template.complexity.value,
                "description": template.description,
                "version": template.version,
                "created_at": template.created_at.isoformat(),
                "last_updated": template.last_updated.isoformat()
            },
            "objectives": template.objectives,
            "workflow": [
                {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "category": step.category,
                    "inputs": step.inputs,
                    "outputs": step.outputs,
                    "parameters": step.parameters,
                    "duration_days": step.duration_estimate.days,
                    "dependencies": step.dependencies,
                    "tools_required": step.tools_required,
                    "safety_requirements": step.safety_requirements,
                    "best_practices": step.best_practices
                }
                for step in template.workflow_steps
            ],
            "resources": {
                "equipment": template.required_equipment,
                "materials": template.required_materials,
                "software": template.required_software
            },
            "estimates": {
                "duration_days": template.estimated_duration.days,
                "cost_usd": template.estimated_cost
            },
            "quality_assurance": {
                "success_metrics": template.success_metrics,
                "safety_protocols": template.safety_protocols,
                "quality_controls": template.quality_controls
            },
            "data_management": template.data_management,
            "literature_references": template.literature_references,
            "tags": template.tags
        }
        
        if format_type.lower() == "yaml":
            return yaml.dump(export_data, default_flow_style=False, sort_keys=False)
        elif format_type.lower() == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    async def get_template_recommendations(
        self,
        research_goals: List[str],
        available_resources: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        🎯 Get Template Recommendations
        
        Recommend appropriate templates based on research goals,
        available resources, and constraints.
        """
        recommendations = []
        
        for template in self.templates.values():
            score = self._calculate_template_score(
                template, research_goals, available_resources, constraints or {}
            )
            
            if score > 0.3:  # Minimum relevance threshold
                recommendations.append({
                    "template_id": template.id,
                    "template_name": template.name,
                    "domain": template.domain.value,
                    "experiment_type": template.experiment_type.value,
                    "complexity": template.complexity.value,
                    "relevance_score": score,
                    "estimated_duration": template.estimated_duration.days,
                    "estimated_cost": template.estimated_cost,
                    "key_benefits": self._identify_key_benefits(template, research_goals)
                })
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _calculate_template_score(
        self,
        template: ExperimentTemplate,
        research_goals: List[str],
        available_resources: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a template"""
        score = 0.0
        
        # Goal alignment (40% of score)
        goal_keywords = [goal.lower() for goal in research_goals]
        template_keywords = (
            template.description.lower() + 
            " ".join(template.objectives).lower() +
            " ".join(template.tags).lower()
        )
        
        goal_matches = sum(1 for keyword in goal_keywords if keyword in template_keywords)
        if goal_keywords:
            score += 0.4 * (goal_matches / len(goal_keywords))
        
        # Resource compatibility (30% of score)
        available_equipment = available_resources.get("equipment", [])
        required_equipment = template.required_equipment
        
        if required_equipment:
            equipment_matches = sum(1 for eq in required_equipment if eq in available_equipment)
            score += 0.3 * (equipment_matches / len(required_equipment))
        
        # Budget constraints (20% of score) - penalize if over budget
        budget = constraints.get("budget", float('inf'))
        if template.estimated_cost <= budget:
            score += 0.2
        else:
            # Heavy penalty for exceeding budget
            score *= 0.1
        
        # Timeline constraints (10% of score) - penalize if over timeline
        timeline = constraints.get("timeline_days", float('inf'))
        if template.estimated_duration.days <= timeline:
            score += 0.1
        else:
            # Penalty for exceeding timeline
            score *= 0.5
        
        return min(score, 1.0)
    
    def _identify_key_benefits(self, template: ExperimentTemplate, research_goals: List[str]) -> List[str]:
        """Identify key benefits of using this template"""
        benefits = []
        
        if template.complexity == TemplateComplexity.EXPERT:
            benefits.append("Comprehensive expert-level methodology")
        
        if len(template.workflow_steps) > 10:
            benefits.append("Detailed step-by-step workflow")
        
        if template.estimated_cost < 10000:
            benefits.append("Cost-effective approach")
        
        if template.estimated_duration.days < 30:
            benefits.append("Fast execution timeline")
        
        return benefits
    
    async def get_service_status(self) -> GetServiceStatusResult:
        """Get comprehensive service status"""
        return {
            "service_name": "Domain Templates Generator Service",
            "status": "operational",
            "version": "1.0.0",
            "statistics": {
                "total_templates": len(self.templates),
                "domains_supported": len(self.domain_knowledge),
                "workflow_steps_library": len(self.workflow_library),
                "total_template_usage": sum(self.template_usage_stats.values()),
                "customizations_created": len(self.customizations)
            },
            "supported_domains": [domain.value for domain in self.domain_knowledge.keys()],
            "supported_experiment_types": [exp_type.value for exp_type in ExperimentType],
            "supported_complexity_levels": [complexity.value for complexity in TemplateComplexity],
            "capabilities": [
                "Automatic template generation for scientific domains",
                "Domain-specific best practices integration",
                "Workflow optimization based on experiment type",
                "Template customization and modification",
                "Multi-format template export (YAML, JSON)",
                "Intelligent template recommendations",
                "Cost and timeline estimation",
                "Safety protocol integration",
                "Quality control automation"
            ],
            "last_updated": datetime.now().isoformat()
        }

# Global service instance
domain_templates = DomainTemplatesService()

logger.info("🧬 Domain Templates Generator Service module loaded")
