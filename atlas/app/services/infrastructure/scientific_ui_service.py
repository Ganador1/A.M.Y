#!/usr/bin/env python3
"""
AXIOM Scientific UI Service
Visual Workflow Builder for Non-Technical Scientists

Provides drag-and-drop interface, natural language translation, and adaptive UI
for democratizing scientific research access.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import re
from enum import Enum
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_ui_service_types import (
    CreateDragDropWorkflowResult,
    TranslateNaturalLanguageResult,
    GenerateDomainTemplatesResult,
    CreateAdaptiveInterfaceResult,
    GenerateUiComponentsResult,
    SuggestWorkflowFromIntentResult,
    GenerateTemplatePreviewResult,
    GetDomainInterfaceConfigResult,
)

logger = logging.getLogger(__name__)

class WorkflowNodeType(str, Enum):
    """Types of workflow nodes available"""
    INPUT = "input"
    ANALYSIS = "analysis" 
    TRANSFORMATION = "transformation"
    VISUALIZATION = "visualization"
    OUTPUT = "output"
    DECISION = "decision"
    LOOP = "loop"

class ScientificDomain(str, Enum):
    """Scientific domains supported"""
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    BIOLOGY = "biology"
    MATERIALS = "materials"
    MEDICINE = "medicine"
    MATHEMATICS = "mathematics"
    QUANTUM = "quantum"

class WorkflowNode(BaseModel):
    """Individual workflow node"""
    id: str
    type: WorkflowNodeType
    name: str
    description: Optional[str] = None
    position: Dict[str, float] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    service_endpoint: Optional[str] = None
    domain: ScientificDomain
    icon: Optional[str] = None
    color: str = "#007bff"

class WorkflowConnection(BaseModel):
    """Connection between workflow nodes"""
    id: str
    source_node: str
    target_node: str
    source_port: str
    target_port: str
    label: Optional[str] = None

class VisualWorkflow(BaseModel):
    """Complete visual workflow definition"""
    id: str
    name: str
    description: Optional[str] = None
    domain: ScientificDomain
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    nodes: List[WorkflowNode] = Field(default_factory=list)
    connections: List[WorkflowConnection] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NaturalLanguageQuery(BaseModel):
    """Natural language query structure"""
    query: str
    domain: Optional[ScientificDomain] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    user_level: str = "beginner"  # beginner, intermediate, expert

class APIMapping(BaseModel):
    """Mapping from NL intent to API call"""
    intent: str
    confidence: float
    api_endpoint: str
    method: str = "POST"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str
    examples: List[str] = Field(default_factory=list)

class ScientificUIService:
    """Main service for scientific UI functionality"""
    
    def __init__(self):
        self.workflow_templates = {}
        self.nl_patterns = {}
        self.api_mappings = {}
        self.user_preferences = {}
        self._initialize_templates()
        self._initialize_nl_patterns()
        self._initialize_api_mappings()
        
    def _initialize_templates(self):
        """Initialize domain-specific workflow templates"""
        self.workflow_templates = {
            ScientificDomain.CHEMISTRY: {
                "molecular_analysis": {
                    "name": "Análisis Molecular Básico",
                    "description": "Análisis de propiedades moleculares y conformeros",
                    "nodes": [
                        {
                            "id": "input_molecule",
                            "type": WorkflowNodeType.INPUT,
                            "name": "Molécula Input",
                            "service_endpoint": "/api/chemistry/analyze-molecule",
                            "parameters": {"format": "SMILES"},
                            "icon": "molecule",
                            "color": "#28a745"
                        },
                        {
                            "id": "analyze_properties", 
                            "type": WorkflowNodeType.ANALYSIS,
                            "name": "Análizar Propiedades",
                            "service_endpoint": "/api/chemistry/analyze-molecule",
                            "parameters": {"properties": ["molecular_weight", "logp", "tpsa"]},
                            "icon": "flask",
                            "color": "#17a2b8"
                        },
                        {
                            "id": "visualize_structure",
                            "type": WorkflowNodeType.VISUALIZATION,
                            "name": "Visualizar Estructura 3D",
                            "service_endpoint": "/api/chemistry/generate-conformers",
                            "parameters": {"optimize": True, "num_conformers": 5},
                            "icon": "cube",
                            "color": "#ffc107"
                        }
                    ]
                }
            },
            ScientificDomain.BIOLOGY: {
                "sequence_analysis": {
                    "name": "Análisis de Secuencias",
                    "description": "Análisis bioinformático de secuencias DNA/RNA/Proteína",
                    "nodes": [
                        {
                            "id": "input_sequence",
                            "type": WorkflowNodeType.INPUT,
                            "name": "Secuencia Input",
                            "service_endpoint": "/api/chemistry/analyze-sequence",
                            "parameters": {"sequence_type": "DNA"},
                            "icon": "dna",
                            "color": "#28a745"
                        },
                        {
                            "id": "analyze_sequence",
                            "type": WorkflowNodeType.ANALYSIS,
                            "name": "Análisis Secuencia",
                            "service_endpoint": "/api/chemistry/analyze-sequence",
                            "parameters": {"analysis_type": "composition"},
                            "icon": "search",
                            "color": "#17a2b8"
                        }
                    ]
                }
            },
            ScientificDomain.PHYSICS: {
                "quantum_simulation": {
                    "name": "Simulación Cuántica Básica",
                    "description": "Simulación de sistemas cuánticos simples",
                    "nodes": [
                        {
                            "id": "setup_system",
                            "type": WorkflowNodeType.INPUT,
                            "name": "Sistema Cuántico",
                            "service_endpoint": "/api/quantum-physics/spin-evolution",
                            "parameters": {"spin": "1/2", "hamiltonian": "sigma_z"},
                            "icon": "atom",
                            "color": "#dc3545"
                        }
                    ]
                }
            }
        }
        
    def _initialize_nl_patterns(self):
        """Initialize natural language processing patterns"""
        self.nl_patterns = {
            # Chemistry patterns
            r"anali[sz]ar?\s+mol[eé]cula\s+(.+)": {
                "intent": "analyze_molecule",
                "domain": ScientificDomain.CHEMISTRY,
                "extract_params": ["molecule"]
            },
            r"calcular\s+propiedades\s+de\s+(.+)": {
                "intent": "calculate_properties", 
                "domain": ScientificDomain.CHEMISTRY,
                "extract_params": ["compound"]
            },
            r"generar\s+conf[oó]rmeros?\s+de\s+(.+)": {
                "intent": "generate_conformers",
                "domain": ScientificDomain.CHEMISTRY,
                "extract_params": ["molecule"]
            },
            
            # Biology patterns
            r"anali[sz]ar?\s+secuencia\s+(.+)": {
                "intent": "analyze_sequence",
                "domain": ScientificDomain.BIOLOGY,
                "extract_params": ["sequence"]
            },
            r"buscar\s+genes?\s+en\s+(.+)": {
                "intent": "gene_search",
                "domain": ScientificDomain.BIOLOGY,
                "extract_params": ["organism"]
            },
            
            # Physics patterns
            r"simular\s+esp[ií]n\s+cu[aá]ntico": {
                "intent": "quantum_spin_simulation",
                "domain": ScientificDomain.PHYSICS,
                "extract_params": []
            },
            r"calcular\s+oscilador\s+arm[oó]nico": {
                "intent": "harmonic_oscillator",
                "domain": ScientificDomain.PHYSICS,
                "extract_params": []
            }
        }
        
    def _initialize_api_mappings(self):
        """Initialize API endpoint mappings"""
        self.api_mappings = {
            "analyze_molecule": APIMapping(
                intent="analyze_molecule",
                confidence=0.9,
                api_endpoint="/api/chemistry/analyze-molecule",
                method="POST",
                parameters={"smiles": "{molecule}", "properties": ["molecular_weight", "logp", "tpsa"]},
                description="Analiza propiedades moleculares básicas",
                examples=["CCO", "c1ccccc1", "CC(C)C"]
            ),
            "generate_conformers": APIMapping(
                intent="generate_conformers",
                confidence=0.85,
                api_endpoint="/api/chemistry/generate-conformers",
                method="POST", 
                parameters={"smiles": "{molecule}", "num_conformers": 10, "optimize": True},
                description="Genera conformeros 3D optimizados",
                examples=["CCO", "CCC", "c1ccccc1O"]
            ),
            "analyze_sequence": APIMapping(
                intent="analyze_sequence",
                confidence=0.88,
                api_endpoint="/api/chemistry/analyze-sequence",
                method="POST",
                parameters={"sequence": "{sequence}", "sequence_type": "DNA", "analysis_type": "composition"},
                description="Analiza composición de secuencias biológicas",
                examples=["ATCGATCG", "AUGCAUGC", "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"]
            )
        }

    async def create_drag_drop_workflow(self, domain: ScientificDomain, template_name: Optional[str] = None) -> CreateDragDropWorkflowResult:
        """Create a drag-and-drop workflow interface"""
        try:
            logger.info(f"🎨 Creating drag-drop workflow for domain: {domain}")
            
            # Get available templates for domain
            domain_templates = self.workflow_templates.get(domain, {})
            
            if template_name and template_name in domain_templates:
                template = domain_templates[template_name]
                workflow = VisualWorkflow(
                    id=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=template["name"],
                    description=template["description"],
                    domain=domain
                )
                
                # Add nodes from template
                for node_data in template["nodes"]:
                    node = WorkflowNode(
                        id=node_data["id"],
                        type=WorkflowNodeType(node_data["type"]),
                        name=node_data["name"],
                        service_endpoint=node_data.get("service_endpoint"),
                        parameters=node_data.get("parameters", {}),
                        domain=domain,
                        icon=node_data.get("icon", "gear"),
                        color=node_data.get("color", "#007bff")
                    )
                    workflow.nodes.append(node)
                    
                return {
                    "success": True,
                    "workflow": workflow.dict(),
                    "available_nodes": await self._get_available_nodes(domain),
                    "ui_components": await self._generate_ui_components(workflow)
                }
            else:
                # Create empty workflow with available nodes
                workflow = VisualWorkflow(
                    id=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=f"Nuevo Workflow - {domain.value.title()}",
                    description=f"Workflow personalizado para {domain.value}",
                    domain=domain
                )
                
                return {
                    "success": True,
                    "workflow": workflow.dict(),
                    "available_templates": list(domain_templates.keys()),
                    "available_nodes": await self._get_available_nodes(domain),
                    "ui_components": await self._generate_ui_components(workflow)
                }
                
        except BiologyError as e:
            logger.error(f"❌ Error creating drag-drop workflow: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating workflow: {str(e)}"
            }

    async def translate_natural_language(self, nl_query: NaturalLanguageQuery) -> TranslateNaturalLanguageResult:
        """Translate natural language query to API calls"""
        try:
            logger.info(f"🗣️ Translating NL query: {nl_query.query}")
            
            matches = []
            query_lower = nl_query.query.lower()
            
            # Pattern matching
            for pattern, config in self.nl_patterns.items():
                match = re.search(pattern, query_lower)
                if match:
                    intent = config["intent"]
                    domain = config["domain"]
                    
                    # Extract parameters
                    extracted_params = {}
                    if config["extract_params"] and match.groups():
                        for i, param_name in enumerate(config["extract_params"]):
                            if i < len(match.groups()):
                                extracted_params[param_name] = match.group(i + 1).strip()
                    
                    # Get API mapping
                    if intent in self.api_mappings:
                        mapping = self.api_mappings[intent]
                        
                        # Replace parameters in API call
                        api_params = mapping.parameters.copy()
                        for key, value in api_params.items():
                            if isinstance(value, str) and "{" in value:
                                for param_name, param_value in extracted_params.items():
                                    placeholder = "{" + param_name + "}"
                                    if placeholder in value:
                                        api_params[key] = value.replace(placeholder, param_value)
                        
                        matches.append({
                            "intent": intent,
                            "confidence": mapping.confidence,
                            "domain": domain.value,
                            "api_endpoint": mapping.api_endpoint,
                            "method": mapping.method,
                            "parameters": api_params,
                            "description": mapping.description,
                            "extracted_params": extracted_params
                        })
            
            if matches:
                # Sort by confidence
                matches.sort(key=lambda x: x["confidence"], reverse=True)
                best_match = matches[0]
                
                return {
                    "success": True,
                    "translation": best_match,
                    "all_matches": matches,
                    "executable": True,
                    "workflow_suggestion": await self._suggest_workflow_from_intent(best_match)
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo interpretar la consulta",
                    "suggestions": await self._get_nl_suggestions(nl_query.domain)
                }
                
        except BiologyError as e:
            logger.error(f"❌ Error translating NL query: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}"
            }

    async def generate_domain_templates(self, domain: ScientificDomain) -> GenerateDomainTemplatesResult:
        """Generate pre-configured templates for specific domain"""
        try:
            logger.info(f"📋 Generating templates for domain: {domain}")
            
            domain_templates = self.workflow_templates.get(domain, {})
            
            templates_info = []
            for template_id, template_data in domain_templates.items():
                template_info = {
                    "id": template_id,
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "node_count": len(template_data["nodes"]),
                    "estimated_time": "5-10 min",
                    "difficulty": "Principiante",
                    "preview": await self._generate_template_preview(template_data)
                }
                templates_info.append(template_info)
            
            return {
                "success": True,
                "domain": domain.value,
                "templates": templates_info,
                "total_templates": len(templates_info),
                "recommended": templates_info[0]["id"] if templates_info else None
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error generating domain templates: {str(e)}")
            return {
                "success": False,
                "error": f"Error generating templates: {str(e)}"
            }

    async def create_adaptive_interface(self, user_profile: CreateAdaptiveInterfaceResult) -> CreateAdaptiveInterfaceResult:
        """Create adaptive UI based on user profile"""
        try:
            logger.info(f"🎯 Creating adaptive interface for user level: {user_profile.get('level', 'beginner')}")
            
            user_level = user_profile.get("level", "beginner")
            preferred_domain = user_profile.get("domain", ScientificDomain.CHEMISTRY)
            
            # Customize interface based on user level
            if user_level == "beginner":
                interface_config = {
                    "complexity": "simple",
                    "show_advanced_options": False,
                    "guided_mode": True,
                    "tooltips": "detailed",
                    "suggested_templates": await self._get_beginner_templates(preferred_domain),
                    "node_complexity": "basic"
                }
            elif user_level == "intermediate":
                interface_config = {
                    "complexity": "moderate", 
                    "show_advanced_options": True,
                    "guided_mode": False,
                    "tooltips": "moderate",
                    "suggested_templates": await self._get_intermediate_templates(preferred_domain),
                    "node_complexity": "standard"
                }
            else:  # expert
                interface_config = {
                    "complexity": "advanced",
                    "show_advanced_options": True,
                    "guided_mode": False,
                    "tooltips": "minimal",
                    "suggested_templates": await self._get_expert_templates(preferred_domain),
                    "node_complexity": "advanced"
                }
            
            # Add domain-specific customizations
            domain_config = await self._get_domain_interface_config(preferred_domain)
            interface_config.update(domain_config)
            
            return {
                "success": True,
                "interface_config": interface_config,
                "user_profile": user_profile,
                "customizations": {
                    "color_scheme": self._get_domain_colors(preferred_domain),
                    "icons": self._get_domain_icons(preferred_domain),
                    "shortcuts": self._get_user_shortcuts(user_level)
                }
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error creating adaptive interface: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating interface: {str(e)}"
            }

    # Helper methods
    async def _get_available_nodes(self, domain: ScientificDomain) -> List[Dict[str, Any]]:
        """Get available nodes for domain"""
        # This would query the actual service registry
        domain_nodes = {
            ScientificDomain.CHEMISTRY: [
                {"id": "molecule_input", "name": "Entrada Molecular", "type": "input", "icon": "molecule"},
                {"id": "property_analysis", "name": "Análisis Propiedades", "type": "analysis", "icon": "flask"},
                {"id": "conformer_gen", "name": "Generar Conformeros", "type": "transformation", "icon": "cube"},
                {"id": "3d_visualization", "name": "Visualización 3D", "type": "visualization", "icon": "eye"}
            ],
            ScientificDomain.BIOLOGY: [
                {"id": "sequence_input", "name": "Entrada Secuencia", "type": "input", "icon": "dna"},
                {"id": "sequence_analysis", "name": "Análisis Secuencia", "type": "analysis", "icon": "search"},
                {"id": "gene_finder", "name": "Buscador Genes", "type": "analysis", "icon": "target"}
            ]
        }
        return domain_nodes.get(domain, [])
        
    async def _generate_ui_components(self, workflow: VisualWorkflow) -> GenerateUiComponentsResult:
        """Generate UI components for workflow"""
        return {
            "canvas": {
                "width": 1200,
                "height": 800,
                "grid": True,
                "zoom": True
            },
            "toolbar": {
                "tools": ["select", "move", "connect", "delete"],
                "node_palette": True,
                "minimap": True
            },
            "properties_panel": {
                "position": "right",
                "width": 300,
                "collapsible": True
            }
        }
        
    async def _suggest_workflow_from_intent(self, intent_match: SuggestWorkflowFromIntentResult) -> SuggestWorkflowFromIntentResult:
        """Suggest workflow based on detected intent"""
        intent = intent_match["intent"]
        
        # Simple workflow suggestions
        workflow_suggestions = {
            "analyze_molecule": {
                "name": "Análisis Molecular Completo",
                "steps": ["Entrada Molecular", "Análisis Propiedades", "Visualización 3D", "Reporte Final"]
            },
            "generate_conformers": {
                "name": "Generación y Optimización Conformeros",
                "steps": ["Entrada Molecular", "Generar Conformeros", "Optimizar Geometría", "Análisis Energético"]
            }
        }
        
        return workflow_suggestions.get(intent, {})
        
    async def _get_nl_suggestions(self, domain: Optional[ScientificDomain]) -> List[str]:
        """Get natural language suggestions"""
        general_suggestions = [
            "Analizar molécula CCO",
            "Calcular propiedades de benceno", 
            "Generar conformeros de etanol",
            "Analizar secuencia ATCGATCG",
            "Simular espín cuántico"
        ]
        
        if domain == ScientificDomain.CHEMISTRY:
            return [
                "Analizar molécula CCO",
                "Calcular propiedades de benceno",
                "Generar conformeros de metanol"
            ]
        elif domain == ScientificDomain.BIOLOGY:
            return [
                "Analizar secuencia ATCGATCG",
                "Buscar genes en humano",
                "Analizar proteína MKTVRQ"
            ]
        
        return general_suggestions
        
    async def _generate_template_preview(self, template_data: GenerateTemplatePreviewResult) -> GenerateTemplatePreviewResult:
        """Generate template preview"""
        return {
            "thumbnail": f"template_preview_{hash(str(template_data))}.png",
            "node_positions": [(i * 100, 100) for i in range(len(template_data["nodes"]))],
            "complexity_score": len(template_data["nodes"]) * 0.2
        }
        
    async def _get_beginner_templates(self, domain: ScientificDomain) -> List[str]:
        """Get templates suitable for beginners"""
        if domain == ScientificDomain.CHEMISTRY:
            return ["molecular_analysis"]
        elif domain == ScientificDomain.BIOLOGY:
            return ["sequence_analysis"]
        return []
        
    async def _get_intermediate_templates(self, domain: ScientificDomain) -> List[str]:
        """Get templates for intermediate users"""
        return await self._get_beginner_templates(domain)  # For now, same as beginner
        
    async def _get_expert_templates(self, domain: ScientificDomain) -> List[str]:
        """Get templates for expert users"""
        return await self._get_beginner_templates(domain)  # For now, same as beginner
        
    async def _get_domain_interface_config(self, domain: ScientificDomain) -> GetDomainInterfaceConfigResult:
        """Get domain-specific interface configuration"""
        return {
            "primary_color": self._get_domain_colors(domain)["primary"],
            "default_node_type": "analysis",
            "common_operations": await self._get_common_operations(domain)
        }
        
    def _get_domain_colors(self, domain: ScientificDomain) -> Dict[str, str]:
        """Get color scheme for domain"""
        colors = {
            ScientificDomain.CHEMISTRY: {"primary": "#28a745", "secondary": "#17a2b8"},
            ScientificDomain.BIOLOGY: {"primary": "#ffc107", "secondary": "#fd7e14"},
            ScientificDomain.PHYSICS: {"primary": "#dc3545", "secondary": "#e83e8c"},
            ScientificDomain.MATERIALS: {"primary": "#6f42c1", "secondary": "#6610f2"}
        }
        return colors.get(domain, {"primary": "#007bff", "secondary": "#6c757d"})
        
    def _get_domain_icons(self, domain: ScientificDomain) -> Dict[str, str]:
        """Get icon set for domain"""
        return {
            ScientificDomain.CHEMISTRY: {"primary": "flask", "secondary": "molecule"},
            ScientificDomain.BIOLOGY: {"primary": "dna", "secondary": "microscope"},
            ScientificDomain.PHYSICS: {"primary": "atom", "secondary": "magnet"}
        }.get(domain, {"primary": "gear", "secondary": "cog"})
        
    def _get_user_shortcuts(self, user_level: str) -> List[Dict[str, str]]:
        """Get keyboard shortcuts based on user level"""
        if user_level == "expert":
            return [
                {"key": "Ctrl+N", "action": "New Node"},
                {"key": "Ctrl+E", "action": "Execute"},
                {"key": "Del", "action": "Delete Selected"}
            ]
        return []
        
    async def _get_common_operations(self, domain: ScientificDomain) -> List[str]:
        """Get common operations for domain"""
        operations = {
            ScientificDomain.CHEMISTRY: ["analyze", "optimize", "visualize", "calculate"],
            ScientificDomain.BIOLOGY: ["sequence", "align", "search", "annotate"],
            ScientificDomain.PHYSICS: ["simulate", "calculate", "model", "solve"]
        }
        return operations.get(domain, ["analyze", "process", "visualize"])
