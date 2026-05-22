"""
Supplementary Materials Router - AXIOM META 4
API endpoints for automated supplementary materials generation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.core.bootstrap_logging import logger
from app.services.supplementary_materials_generator import SupplementaryMaterialsGenerator
from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError

router = APIRouter(prefix="/api/v1/supplementary-materials", tags=["supplementary-materials"])
supplementary_materials_router = router


class SupplementaryPackageRequest(BaseModel):
    """Request model for generating supplementary materials package"""
    publication_id: str = Field(..., description="Publication ID")
    materials_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for materials to generate")
    experimental_data: Dict[str, Any] = Field(default_factory=dict, description="Experimental data and methods")
    data_sources: Dict[str, Any] = Field(default_factory=dict, description="Data sources and datasets")
    protocol_data: Dict[str, Any] = Field(default_factory=dict, description="Protocol information")
    figure_data: Dict[str, Any] = Field(default_factory=dict, description="Figure data")
    table_data: Dict[str, Any] = Field(default_factory=dict, description="Table data")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


class ExtendedMethodsRequest(BaseModel):
    """Request model for generating extended methods"""
    publication_id: str = Field(..., description="Publication ID")
    experimental_data: Dict[str, Any] = Field(..., description="Experimental data and methods")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


class SupplementaryDataRequest(BaseModel):
    """Request model for generating supplementary data"""
    publication_id: str = Field(..., description="Publication ID")
    data_sources: Dict[str, Any] = Field(..., description="Data sources and datasets")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


class ProtocolRequest(BaseModel):
    """Request model for generating protocol"""
    publication_id: str = Field(..., description="Publication ID")
    protocol_data: Dict[str, Any] = Field(..., description="Protocol information")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


class SupplementaryFigureRequest(BaseModel):
    """Request model for generating supplementary figure"""
    publication_id: str = Field(..., description="Publication ID")
    figure_number: int = Field(..., description="Figure number")
    figure_data: Dict[str, Any] = Field(..., description="Figure data and information")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


class SupplementaryTableRequest(BaseModel):
    """Request model for generating supplementary table"""
    publication_id: str = Field(..., description="Publication ID")
    table_number: int = Field(..., description="Table number")
    table_data: Dict[str, Any] = Field(..., description="Table data and information")
    output_path: str = Field(default="./supplementary_materials", description="Output directory path")


# Initialize supplementary materials generator service
supplementary_generator = SupplementaryMaterialsGenerator()


@router.post("/generate-package", summary="Generate Complete Supplementary Materials Package")
async def generate_supplementary_package(request: SupplementaryPackageRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete supplementary materials package for a publication.
    
    This endpoint generates all types of supplementary materials:
    - Extended methods and detailed protocols
    - Supplementary data and datasets
    - Experimental protocols
    - Supplementary figures
    - Supplementary tables
    
    The package includes a manifest file and organized directory structure.
    """
    try:
        result = await supplementary_generator.generate_supplementary_package({
            "action": "generate_supplementary_package",
            "publication_id": request.publication_id,
            "materials_config": request.materials_config,
            "experimental_data": request.experimental_data,
            "data_sources": request.data_sources,
            "protocol_data": request.protocol_data,
            "figure_data": request.figure_data,
            "table_data": request.table_data,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "package_id": result["package_id"],
                "package_path": result["package_path"],
                "total_materials": result["total_materials"],
                "total_size": result["total_size"],
                "materials": result["materials"],
                "manifest": result["manifest"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating supplementary package: {e}")
        raise HTTPException(status_code=500, detail=f"Supplementary package generation failed: {str(e)}")


@router.post("/generate-extended-methods", summary="Generate Extended Methods")
async def generate_extended_methods(request: ExtendedMethodsRequest):
    """
    Generate extended methods document with detailed experimental protocols.
    
    Includes:
    - Detailed experimental procedures
    - Equipment specifications
    - Reagent information
    - Data analysis methods
    - Quality control measures
    """
    try:
        result = await supplementary_generator.generate_extended_methods({
            "action": "generate_extended_methods",
            "publication_id": request.publication_id,
            "experimental_data": request.experimental_data,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "material": result["material"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating extended methods: {e}")
        raise HTTPException(status_code=500, detail=f"Extended methods generation failed: {str(e)}")


@router.post("/generate-supplementary-data", summary="Generate Supplementary Data")
async def generate_supplementary_data(request: SupplementaryDataRequest):
    """
    Generate supplementary data document with raw data and datasets.
    
    Includes:
    - Data description and format
    - Dataset metadata
    - Data access information
    - Processing pipeline details
    - Validation methods
    """
    try:
        result = await supplementary_generator.generate_supplementary_data({
            "action": "generate_supplementary_data",
            "publication_id": request.publication_id,
            "data_sources": request.data_sources,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "material": result["material"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating supplementary data: {e}")
        raise HTTPException(status_code=500, detail=f"Supplementary data generation failed: {str(e)}")


@router.post("/generate-protocol", summary="Generate Experimental Protocol")
async def generate_protocol(request: ProtocolRequest):
    """
    Generate detailed experimental protocol document.
    
    Includes:
    - Objective and materials
    - Step-by-step procedure
    - Equipment specifications
    - Troubleshooting guide
    - Safety information
    """
    try:
        result = await supplementary_generator.generate_protocol({
            "action": "generate_protocol",
            "publication_id": request.publication_id,
            "protocol_data": request.protocol_data,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "material": result["material"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating protocol: {e}")
        raise HTTPException(status_code=500, detail=f"Protocol generation failed: {str(e)}")


@router.post("/generate-supplementary-figure", summary="Generate Supplementary Figure")
async def generate_supplementary_figure(request: SupplementaryFigureRequest):
    """
    Generate supplementary figure document.
    
    Includes:
    - Figure description and interpretation
    - Data source information
    - Analysis methods
    - Technical details
    - Related data references
    """
    try:
        result = await supplementary_generator.generate_supplementary_figure({
            "action": "generate_supplementary_figure",
            "publication_id": request.publication_id,
            "figure_number": request.figure_number,
            "figure_data": request.figure_data,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "material": result["material"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating supplementary figure: {e}")
        raise HTTPException(status_code=500, detail=f"Supplementary figure generation failed: {str(e)}")


@router.post("/generate-supplementary-table", summary="Generate Supplementary Table")
async def generate_supplementary_table(request: SupplementaryTableRequest):
    """
    Generate supplementary table document.
    
    Includes:
    - Table description and interpretation
    - Data source information
    - Statistical methods
    - Table data
    - Additional notes
    """
    try:
        result = await supplementary_generator.generate_supplementary_table({
            "action": "generate_supplementary_table",
            "publication_id": request.publication_id,
            "table_number": request.table_number,
            "table_data": request.table_data,
            "output_path": request.output_path
        })
        
        if result["success"]:
            return {
                "success": True,
                "material": result["material"],
                "filename": result["filename"],
                "file_path": result["file_path"],
                "file_size": result["file_size"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating supplementary table: {e}")
        raise HTTPException(status_code=500, detail=f"Supplementary table generation failed: {str(e)}")


@router.get("/material-types", summary="Get Available Material Types")
async def get_material_types():
    """
    Get information about available supplementary material types and their requirements.
    """
    return {
        "success": True,
        "material_types": {
            "extended_methods": {
                "description": "Extended methods and detailed protocols",
                "required_sections": ["overview", "detailed_protocols", "equipment", "reagents", "data_analysis"],
                "template": "extended_methods.md"
            },
            "supplementary_data": {
                "description": "Raw data and supplementary datasets",
                "required_sections": ["data_description", "data_format", "data_access", "metadata"],
                "template": "supplementary_data.md"
            },
            "protocol": {
                "description": "Detailed experimental protocols",
                "required_sections": ["objective", "materials", "procedure", "troubleshooting", "notes"],
                "template": "protocol.md"
            },
            "figure": {
                "description": "Supplementary figures and visualizations",
                "required_sections": ["figure_description", "data_source", "analysis_methods", "interpretation"],
                "template": "supplementary_figure.md"
            },
            "table": {
                "description": "Supplementary tables and datasets",
                "required_sections": ["table_description", "data_source", "statistical_methods", "interpretation"],
                "template": "supplementary_table.md"
            }
        }
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the supplementary materials generator service is healthy"""
    return {
        "success": True,
        "service": "SupplementaryMaterialsGenerator",
        "status": "healthy",
        "available_material_types": 5,
        "supported_formats": ["markdown", "json", "csv"]
    }
