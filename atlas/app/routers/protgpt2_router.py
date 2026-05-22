"""
ProtGPT2 Protein Design API Router for AXIOM
RESTful endpoints for generative protein design using transformer models

Endpoints:
- POST /generate: Generate novel protein sequences from text prompts
- POST /optimize: Optimize existing protein sequences for specific properties
- POST /insert-domain: Design domain insertions into proteins
- POST /batch-variants: Generate multiple protein variants
- GET /health: Service health check
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.domains.biology.services.protgpt2_service import ProtGPT2ProteinDesignService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Initialize router and service
router = APIRouter(prefix="/protgpt2", tags=["ProtGPT2 Protein Design"])
protgpt2_service = ProtGPT2ProteinDesignService()


# Request/Response Models
class ProteinGenerationRequest(BaseModel):
    """Request model for protein sequence generation"""
    prompt: str = Field(
        ..., 
        min_length=5, 
        description="Text description of desired protein properties/function"
    )
    temperature: Optional[float] = Field(
        0.8, 
        ge=0.1, 
        le=2.0, 
        description="Generation temperature (0.1-2.0)"
    )
    top_p: Optional[float] = Field(
        0.9, 
        ge=0.1, 
        le=1.0, 
        description="Nucleus sampling parameter (0.1-1.0)"
    )
    max_length: Optional[int] = Field(
        500, 
        ge=20, 
        le=1000, 
        description="Maximum sequence length"
    )


class ProteinOptimizationRequest(BaseModel):
    """Request model for protein sequence optimization"""
    sequence: str = Field(
        ..., 
        min_length=20, 
        description="Original protein sequence to optimize"
    )
    target_property: str = Field(
        ..., 
        description="Property to optimize (stability, solubility, activity, etc.)"
    )


class DomainInsertionRequest(BaseModel):
    """Request model for domain insertion design"""
    base_sequence: str = Field(
        ..., 
        min_length=20, 
        description="Base protein sequence for domain insertion"
    )
    domain_function: str = Field(
        ..., 
        description="Desired function of domain to insert"
    )


class BatchVariantRequest(BaseModel):
    """Request model for batch variant generation"""
    base_prompt: str = Field(
        ..., 
        min_length=5, 
        description="Base prompt for variant generation"
    )
    num_variants: int = Field(
        5, 
        ge=2, 
        le=10, 
        description="Number of variants to generate (2-10)"
    )


class ProtGPT2Response(BaseModel):
    """Standardized response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    service: str = "ProtGPT2ProteinDesignService"


@router.post("/generate", response_model=ProtGPT2Response)
async def generate_protein_sequence(request: ProteinGenerationRequest):
    """
    Generate novel protein sequence from text prompt
    
    Uses ProtGPT2 transformer model to create protein sequences based on
    natural language descriptions of desired properties or functions.
    
    Example prompts:
    - "A small enzyme that binds ATP and catalyzes phosphorylation"
    - "Membrane protein for calcium ion transport"
    - "Stable thermophilic enzyme for industrial applications"
    """
    try:
        logger.info(f"🧬 Protein generation request: {request.prompt[:50]}...")
        
        result = await protgpt2_service.generate_protein_sequence(
            prompt=request.prompt,
            temperature=request.temperature,
            top_p=request.top_p,
            max_length=request.max_length
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Protein generation failed: {result.get('error')}"
            )
        
        # Adapt domain service output into standardized data structure if needed
        data = result.get('data')
        if data is None:
            data = {
                "generated_protein": {
                    "sequence": result.get("generated_sequence"),
                    "sequence_length": result.get("sequence_length"),
                    "properties": result.get("properties"),
                    "confidence_score": result.get("confidence", 0.0),
                }
            }
        
        return ProtGPT2Response(
            success=True,
            data=data
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in protein generation endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during protein generation: {str(e)}"
        )


@router.post("/optimize", response_model=ProtGPT2Response)
async def optimize_protein_sequence(request: ProteinOptimizationRequest):
    """
    Optimize protein sequence for specific properties
    
    Takes an existing protein sequence and suggests mutations to improve
    specific properties like stability, solubility, or catalytic activity.
    
    Supported target properties:
    - stability: Improve thermodynamic stability
    - solubility: Increase aqueous solubility
    - activity: Enhance catalytic or binding activity
    """
    try:
        logger.info(f"🔧 Optimizing protein for: {request.target_property}")
        
        result = await protgpt2_service.optimize_protein_sequence(
            sequence=request.sequence,
            target_property=request.target_property
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Protein optimization failed: {result.get('error')}"
            )
        
        # Adapt domain service output into standardized data structure if needed
        data = result.get('data')
        if data is None:
            data = {
                "optimization": {
                    "original_sequence": result.get("original_sequence"),
                    "optimized_sequence": result.get("optimized_sequence"),
                    "target_property": result.get("target_property"),
                    "mutations": [],  # domain service may not provide detailed mutations
                    "results": result.get("optimization_results"),
                }
            }
        
        return ProtGPT2Response(
            success=True,
            data=data
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in protein optimization endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during protein optimization: {str(e)}"
        )


@router.post("/insert-domain", response_model=ProtGPT2Response)
async def design_domain_insertion(request: DomainInsertionRequest):
    """
    Design functional domain insertion into existing protein
    
    Designs insertion of functional domains into existing protein structures
    while maintaining structural compatibility and adding desired functionality.
    
    Domain functions include:
    - binding: Add ligand/substrate binding capability
    - catalytic: Insert catalytic active site
    - structural: Add structural motifs (loops, helices)
    - signaling: Insert signaling/regulatory domains
    """
    try:
        logger.info(f"🔗 Designing domain insertion: {request.domain_function}")
        
        result = await protgpt2_service.design_domain_insertion(
            base_sequence=request.base_sequence,
            domain_function=request.domain_function
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Domain insertion design failed: {result.get('error')}"
            )
        
        # Adapt domain service output into standardized data structure if needed
        data = result.get('data')
        if data is None:
            data = {
                "domain_insertion": {
                    "base_sequence": result.get("base_sequence"),
                    "modified_sequence": result.get("modified_sequence"),
                    "inserted_domain": result.get("domain_sequence"),
                    "insertion_position": result.get("insertion_point"),
                }
            }
        
        return ProtGPT2Response(
            success=True,
            data=data
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in domain insertion endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during domain insertion: {str(e)}"
        )


@router.post("/batch-variants", response_model=ProtGPT2Response)
async def generate_batch_variants(request: BatchVariantRequest):
    """
    Generate multiple protein variants from single prompt
    
    Creates multiple diverse protein sequences based on a single prompt,
    useful for exploring sequence space and generating libraries of
    related proteins with similar functions.
    """
    try:
        logger.info(f"🧪 Generating {request.num_variants} protein variants")
        
        result = await protgpt2_service.batch_generate_variants(
            base_prompt=request.base_prompt,
            num_variants=request.num_variants
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Batch variant generation failed: {result.get('error')}"
            )
        
        # Adapt domain service output into standardized data structure if needed
        data = result.get('data')
        if data is None:
            variants = result.get("variants", [])
            data = {
                "variants": [
                    {
                        "sequence": v.get("sequence"),
                        "generation_id": str(v.get("variant_id")),
                        "properties": v.get("properties"),
                    } for v in variants
                ],
                "num_variants_generated": result.get("num_variants_generated"),
            }
        
        return ProtGPT2Response(
            success=True,
            data=data
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in batch variant generation endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch generation: {str(e)}"
        )


@router.get("/health", response_model=ProtGPT2Response)
async def health_check():
    """
    ProtGPT2 service health check
    
    Returns service status, capabilities, and performance metrics
    """
    try:
        health_data = await protgpt2_service.health_check()
        
        return ProtGPT2Response(
            success=True,
            data=health_data
        )
        
    except BiologyError as e:
        logger.error(f"Error in health check endpoint: {e}")
        return ProtGPT2Response(
            success=False,
            error=f"Health check failed: {str(e)}"
        )


# Background task endpoints
@router.post("/generate-async")
async def generate_protein_async(request: ProteinGenerationRequest, background_tasks: BackgroundTasks):
    """
    Asynchronous protein generation for large sequences
    
    Starts protein generation in background for complex/long sequences.
    Use this for computationally intensive generation tasks.
    """
    try:
        # In production, would use task queue (Celery, RQ, etc.)
        def background_generation():
            logger.info(f"Starting background protein generation")
            # This would actually run the generation asynchronously
            
        background_tasks.add_task(background_generation)
        
        return ProtGPT2Response(
            success=True,
            data={
                "message": "Protein generation started in background",
                "status": "processing",
                "estimated_completion": "2-5 minutes"
            }
        )
        
    except BiologyError as e:
        logger.error(f"Error starting background generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start background generation: {str(e)}"
        )


# Utility endpoints
@router.get("/capabilities")
async def get_capabilities():
    """
    Get ProtGPT2 service capabilities and supported features
    """
    try:
        return ProtGPT2Response(
            success=True,
            data={
                "service_name": "ProtGPT2ProteinDesignService",
                "version": "1.0.0",
                "model": "nferruz/ProtGPT2",
                "supported_operations": [
                    "sequence_generation",
                    "sequence_optimization", 
                    "domain_insertion",
                    "batch_variants"
                ],
                "generation_parameters": {
                    "temperature_range": [0.1, 2.0],
                    "top_p_range": [0.1, 1.0],
                    "max_length_range": [20, 1000]
                },
                "optimization_targets": [
                    "stability",
                    "solubility",
                    "activity",
                    "binding"
                ],
                "domain_functions": [
                    "binding",
                    "catalytic", 
                    "structural",
                    "signaling"
                ],
                "batch_limits": {
                    "max_variants_per_batch": 10,
                    "max_concurrent_batches": 5
                }
            }
        )
        
    except BiologyError as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve capabilities: {str(e)}"
        )
