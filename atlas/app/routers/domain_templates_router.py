"""
AXIOM Domain Templates Generator Router

Router FastAPI para generador de plantillas específicas de dominio de investigación.
Proporciona acceso RESTful al servicio de Generador de Plantillas de Dominio,
habilitando creación automática y personalización de plantillas de investigación científica.

Capacidades principales:
- Generación automática de plantillas de investigación específicas de dominio
- Creación y personalización de plantillas científicas de investigación
- Soporte para múltiples dominios científicos (biología, química, física, etc.)
- Tipos de experimentos especializados por dominio
- Niveles de complejidad de plantillas configurables
- Personalización de plantillas basada en requisitos específicos
- Generación de protocolos experimentales estandarizados
- Plantillas de análisis de datos y reportes científicos
- Integración con flujos de trabajo de investigación
- Biblioteca extensible de plantillas predefinidas

Endpoints disponibles:
- GET /status: Estado del servicio de generador de plantillas
- GET /domains: Dominios científicos soportados
- GET /experiment-types: Tipos de experimentos disponibles
- POST /generate-template: Generar plantilla específica de dominio
- POST /customize-template: Personalizar plantilla existente
- GET /templates/{domain}: Plantillas disponibles para un dominio
- POST /validate-template: Validar plantilla generada
- GET /examples: Ejemplos de plantillas por dominio
- POST /export-template: Exportar plantilla en múltiples formatos

Dependencias:
- DomainTemplatesService: Servicio principal de plantillas de dominio
- ScientificDomain: Enumeración de dominios científicos
- ExperimentType: Tipos de experimentos disponibles
- TemplateComplexity: Niveles de complejidad de plantillas

Uso típico:
    from app.routers.domain_templates_router import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /domain-templates
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional, Any
import logging
from datetime import datetime

from app.exceptions.domain.biology import BiologyError
from app.services.domain_templates_service import (
    domain_templates,
    ScientificDomain,
    ExperimentType,
    TemplateComplexity,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/domain-templates",
    tags=["Domain Templates Generator"],
    responses={404: {"description": "Not found"}}
)

@router.get("/status")
async def get_service_status():
    """
    🧬 Get Domain Templates Generator Service Status
    
    Returns comprehensive status information including supported domains,
    experiment types, and service capabilities.
    """
    try:
        status = await domain_templates.get_service_status()
        return status
    except BiologyError as e:
        logger.error(f"❌ Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains")
async def get_supported_domains():
    """
    🔬 Get Supported Scientific Domains
    
    Returns list of all supported scientific domains for template generation.
    """
    return {
        "domains": [
            {
                "id": domain.value,
                "name": domain.value.replace("_", " ").title(),
                "description": f"Templates for {domain.value.replace('_', ' ')} research"
            }
            for domain in ScientificDomain
        ]
    }

@router.get("/experiment-types")
async def get_experiment_types():
    """
    🧪 Get Supported Experiment Types
    
    Returns list of all supported experiment types for template generation.
    """
    return {
        "experiment_types": [
            {
                "id": exp_type.value,
                "name": exp_type.value.replace("_", " ").title(),
                "description": f"{exp_type.value.replace('_', ' ').title()} experiments"
            }
            for exp_type in ExperimentType
        ]
    }

@router.get("/complexity-levels")
async def get_complexity_levels():
    """
    📊 Get Complexity Levels
    
    Returns available complexity levels for template generation.
    """
    return {
        "complexity_levels": [
            {
                "id": complexity.value,
                "name": complexity.value.title(),
                "description": f"{complexity.value.title()} level templates"
            }
            for complexity in TemplateComplexity
        ]
    }

@router.post("/generate")
async def generate_template(
    domain: str,
    experiment_type: str,
    complexity: str,
    custom_requirements: Optional[Dict[str, Any]] = None
):
    """
    🧬 Generate Domain-Specific Research Template
    
    Creates a customized research template based on:
    - Scientific domain (e.g., computational_biology, materials_science)
    - Experiment type (e.g., simulation, wet_lab, synthesis)
    - Complexity level (basic, intermediate, advanced, expert)
    - Optional custom requirements
    
    Returns complete template with workflow, resources, and protocols.
    """
    try:
        # Validate domain
        try:
            domain_enum = ScientificDomain(domain)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported domain: {domain}. Use /domains endpoint to see supported domains."
            )
        
        # Validate experiment type
        try:
            experiment_enum = ExperimentType(experiment_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported experiment type: {experiment_type}. Use /experiment-types endpoint to see supported types."
            )
        
        # Validate complexity
        try:
            complexity_enum = TemplateComplexity(complexity)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported complexity: {complexity}. Use /complexity-levels endpoint to see supported levels."
            )
        
        # Generate template
        template = await domain_templates.generate_template(
            domain=domain_enum,
            experiment_type=experiment_enum,
            complexity=complexity_enum,
            custom_requirements=custom_requirements
        )
        
        # Convert to JSON-serializable format
        return {
            "template_id": template.id,
            "name": template.name,
            "domain": template.domain.value,
            "experiment_type": template.experiment_type.value,
            "complexity": template.complexity.value,
            "description": template.description,
            "objectives": template.objectives,
            "workflow_steps": [
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
                    "best_practices": step.best_practices,
                    "validation_criteria": step.validation_criteria
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
            "version": template.version,
            "tags": template.tags,
            "created_at": template.created_at.isoformat(),
            "last_updated": template.last_updated.isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error generating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_templates(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    experiment_type: Optional[str] = Query(None, description="Filter by experiment type"),
    complexity: Optional[str] = Query(None, description="Filter by complexity"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of templates to return")
):
    """
    📋 List Generated Templates
    
    Returns list of previously generated templates with optional filtering.
    """
    try:
        templates = []
        
        for template in domain_templates.templates.values():
            # Apply filters
            if domain and template.domain.value != domain:
                continue
            if experiment_type and template.experiment_type.value != experiment_type:
                continue
            if complexity and template.complexity.value != complexity:
                continue
            
            templates.append({
                "template_id": template.id,
                "name": template.name,
                "domain": template.domain.value,
                "experiment_type": template.experiment_type.value,
                "complexity": template.complexity.value,
                "description": template.description,
                "workflow_steps_count": len(template.workflow_steps),
                "estimated_duration_days": template.estimated_duration.days,
                "estimated_cost_usd": template.estimated_cost,
                "usage_count": domain_templates.template_usage_stats.get(template.id, 0),
                "created_at": template.created_at.isoformat(),
                "last_updated": template.last_updated.isoformat(),
                "tags": template.tags
            })
            
            if len(templates) >= limit:
                break
        
        # Sort by creation date (newest first)
        templates.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "templates": templates,
            "total_count": len(templates),
            "filters_applied": {
                "domain": domain,
                "experiment_type": experiment_type,
                "complexity": complexity
            }
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}")
async def get_template_details(template_id: str):
    """
    🔍 Get Template Details
    
    Returns complete details for a specific template including
    full workflow, resources, and protocols.
    """
    try:
        if template_id not in domain_templates.templates:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        template = domain_templates.templates[template_id]
        
        # Update usage stats
        domain_templates.template_usage_stats[template_id] = domain_templates.template_usage_stats.get(template_id, 0) + 1
        
        # Return complete template details
        return {
            "template_id": template.id,
            "name": template.name,
            "domain": template.domain.value,
            "experiment_type": template.experiment_type.value,
            "complexity": template.complexity.value,
            "description": template.description,
            "objectives": template.objectives,
            "workflow_steps": [
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
                    "best_practices": step.best_practices,
                    "validation_criteria": step.validation_criteria
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
            "version": template.version,
            "tags": template.tags,
            "usage_count": domain_templates.template_usage_stats.get(template_id, 0),
            "created_at": template.created_at.isoformat(),
            "last_updated": template.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error getting template details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/customize")
async def customize_template(
    template_id: str,
    customizations: Dict[str, Any]
):
    """
    ✏️ Customize Existing Template
    
    Create a customized version of an existing template with:
    - Additional objectives
    - Custom workflow steps
    - Modified resource requirements
    - Updated parameters
    """
    try:
        if template_id not in domain_templates.templates:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        customized_template = await domain_templates.customize_template(
            template_id=template_id,
            customizations=customizations
        )
        
        return {
            "customized_template_id": customized_template.id,
            "original_template_id": template_id,
            "name": customized_template.name,
            "customizations_applied": customizations,
            "workflow_steps_count": len(customized_template.workflow_steps),
            "estimated_duration_days": customized_template.estimated_duration.days,
            "estimated_cost_usd": customized_template.estimated_cost,
            "created_at": customized_template.created_at.isoformat(),
            "last_updated": customized_template.last_updated.isoformat(),
            "message": f"Template {template_id} successfully customized as {customized_template.id}"
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error customizing template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}/export")
async def export_template(
    template_id: str,
    format: str = Query("yaml", regex="^(yaml|json)$", description="Export format: yaml or json")
):
    """
    📄 Export Template
    
    Export template in YAML or JSON format for external use
    or integration with other systems.
    """
    try:
        if template_id not in domain_templates.templates:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        exported_content = await domain_templates.export_template(
            template_id=template_id,
            format_type=format
        )
        
        return {
            "template_id": template_id,
            "format": format,
            "content": exported_content,
            "exported_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error exporting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations")
async def get_template_recommendations(
    request_data: Dict[str, Any]
):
    """
    🎯 Get Template Recommendations
    
    Get intelligent template recommendations based on:
    - Research goals and objectives
    - Available resources (equipment, budget, timeline)
    - Project constraints
    
    Request format:
    {
        "research_goals": ["goal1", "goal2", ...],
        "available_resources": {
            "equipment": ["item1", "item2", ...],
            "budget": float,
            "timeline_days": int
        },
        "constraints": {
            "budget": float,
            "timeline_days": int,
            "complexity_preference": "basic|intermediate|advanced|expert"
        }
    }
    """
    try:
        research_goals = request_data.get("research_goals", [])
        available_resources = request_data.get("available_resources", {})
        constraints = request_data.get("constraints", {})
        
        if not research_goals:
            raise HTTPException(
                status_code=400,
                detail="Research goals are required for recommendations"
            )
        
        recommendations = await domain_templates.get_template_recommendations(
            research_goals=research_goals,
            available_resources=available_resources,
            constraints=constraints
        )
        
        return {
            "recommendations": recommendations,
            "request_summary": {
                "research_goals_count": len(research_goals),
                "resources_specified": list(available_resources.keys()),
                "constraints_applied": list(constraints.keys())
            },
            "total_recommendations": len(recommendations),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics():
    """
    📈 Get Service Analytics
    
    Returns analytics and usage statistics for the template generation service.
    """
    try:
        total_templates = len(domain_templates.templates)
        total_usage = sum(domain_templates.template_usage_stats.values())
        
        # Domain distribution
        domain_stats = {}
        for template in domain_templates.templates.values():
            domain = template.domain.value
            domain_stats[domain] = domain_stats.get(domain, 0) + 1
        
        # Complexity distribution
        complexity_stats = {}
        for template in domain_templates.templates.values():
            complexity = template.complexity.value
            complexity_stats[complexity] = complexity_stats.get(complexity, 0) + 1
        
        # Most used templates
        most_used = []
        for template_id, usage_count in sorted(
            domain_templates.template_usage_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            if template_id in domain_templates.templates:
                template = domain_templates.templates[template_id]
                most_used.append({
                    "template_id": template_id,
                    "template_name": template.name,
                    "usage_count": usage_count,
                    "domain": template.domain.value,
                    "complexity": template.complexity.value
                })
        
        return {
            "overview": {
                "total_templates_generated": total_templates,
                "total_template_usage": total_usage,
                "total_customizations": len(domain_templates.customizations),
                "average_usage_per_template": round(total_usage / max(total_templates, 1), 2)
            },
            "distributions": {
                "by_domain": domain_stats,
                "by_complexity": complexity_stats
            },
            "top_templates": most_used,
            "service_health": {
                "domains_supported": len(domain_templates.domain_knowledge),
                "workflow_steps_library": len(domain_templates.workflow_library),
                "status": "operational"
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """
    🗑️ Delete Template
    
    Delete a specific template and its associated data.
    """
    try:
        if template_id not in domain_templates.templates:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        template_name = domain_templates.templates[template_id].name
        
        # Remove template and associated data
        del domain_templates.templates[template_id]
        if template_id in domain_templates.template_usage_stats:
            del domain_templates.template_usage_stats[template_id]
        if template_id in domain_templates.customizations:
            del domain_templates.customizations[template_id]
        
        return {
            "template_id": template_id,
            "template_name": template_name,
            "deleted_at": datetime.now().isoformat(),
            "message": f"Template {template_id} successfully deleted"
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-generate")
async def batch_generate_templates(
    batch_request: Dict[str, Any]
):
    """
    🏭 Batch Generate Templates
    
    Generate multiple templates in a single request for efficient processing.
    
    Request format:
    {
        "templates": [
            {
                "domain": "computational_biology",
                "experiment_type": "simulation",
                "complexity": "advanced",
                "custom_requirements": {...}
            },
            ...
        ]
    }
    """
    try:
        template_specs = batch_request.get("templates", [])
        
        if not template_specs:
            raise HTTPException(
                status_code=400,
                detail="No template specifications provided"
            )
        
        if len(template_specs) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 templates per batch request"
            )
        
        generated_templates = []
        errors = []
        
        for i, spec in enumerate(template_specs):
            try:
                # Validate required fields
                if not all(key in spec for key in ["domain", "experiment_type", "complexity"]):
                    errors.append({
                        "template_index": i,
                        "error": "Missing required fields: domain, experiment_type, complexity"
                    })
                    continue
                
                # Parse enums
                domain_enum = ScientificDomain(spec["domain"])
                experiment_enum = ExperimentType(spec["experiment_type"])
                complexity_enum = TemplateComplexity(spec["complexity"])
                
                # Generate template
                template = await domain_templates.generate_template(
                    domain=domain_enum,
                    experiment_type=experiment_enum,
                    complexity=complexity_enum,
                    custom_requirements=spec.get("custom_requirements")
                )
                
                generated_templates.append({
                    "template_index": i,
                    "template_id": template.id,
                    "template_name": template.name,
                    "domain": template.domain.value,
                    "experiment_type": template.experiment_type.value,
                    "complexity": template.complexity.value,
                    "workflow_steps_count": len(template.workflow_steps),
                    "estimated_duration_days": template.estimated_duration.days,
                    "estimated_cost_usd": template.estimated_cost
                })
                
            except ValueError as ve:
                errors.append({
                    "template_index": i,
                    "error": f"Invalid enum value: {str(ve)}"
                })
            except BiologyError as e:
                errors.append({
                    "template_index": i,
                    "error": str(e)
                })
        
        return {
            "batch_summary": {
                "requested_templates": len(template_specs),
                "successfully_generated": len(generated_templates),
                "errors": len(errors)
            },
            "generated_templates": generated_templates,
            "errors": errors,
            "processed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"❌ Error in batch generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

logger.info("🧬 Domain Templates Router loaded with 13 endpoints")
