"""
SciBERT Router for AXIOM
General scientific text analysis endpoints

Features:
- Scientific literature analysis across domains
- Research paper classification
- Cross-domain similarity analysis
- Interdisciplinary connection identification
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.services.scibert_service import SciBERTService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Create router
router = APIRouter()

# Initialize service with lazy loading
scibert_service = None

def get_scibert_service():
    """Get or initialize the SciBERT service instance.

    Implements lazy loading for the service to optimize resource usage.
    """
    global scibert_service
    if scibert_service is None:
        scibert_service = SciBERTService()
    return scibert_service

# Request Models
class ScientificAnalysisRequest(BaseModel):
    """Request model for scientific text analysis.

    Contains the text to be analyzed using SciBERT.
    """

    text: str = Field(..., description="Scientific text for analysis", min_length=30)

class ResearchSimilarityRequest(BaseModel):
    """Request model for research text similarity calculation.

    Contains two texts to compare for similarity.
    """

    text1: str = Field(..., description="First research text", min_length=30)
    text2: str = Field(..., description="Second research text", min_length=30)

class PaperClassificationRequest(BaseModel):
    """Request model for research paper classification.

    Contains the abstract and optional title for classification.
    """

    abstract: str = Field(..., description="Research paper abstract", min_length=50)
    title: Optional[str] = Field(None, description="Optional paper title")

@router.post("/analyze")
async def analyze_scientific_text(request: ScientificAnalysisRequest):
    """Comprehensive scientific text analysis"""
    try:
        service = get_scibert_service()
        result = await service.analyze_scientific_text(request.text)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Scientific analysis failed')
            )
        
        return {
            "status": "success",
            "message": "Scientific text analyzed successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"Scientific analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze scientific text: {str(e)}"
        )

@router.post("/research-similarity")
async def calculate_research_similarity(request: ResearchSimilarityRequest):
    """Calculate similarity between research texts"""
    try:
        service = get_scibert_service()
        result = await service.calculate_research_similarity(
            request.text1,
            request.text2
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Research similarity calculation failed')
            )
        
        return {
            "status": "success",
            "message": "Research similarity calculated successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"Research similarity error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate research similarity: {str(e)}"
        )

@router.post("/classify-paper")
async def classify_research_paper(request: PaperClassificationRequest):
    """Classify research paper by domain and methodology"""
    try:
        service = get_scibert_service()
        result = await service.classify_research_paper(
            request.abstract,
            request.title or ""
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Paper classification failed')
            )
        
        return {
            "status": "success",
            "message": "Research paper classified successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"Paper classification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to classify research paper: {str(e)}"
        )

@router.get("/service-info")
async def get_scibert_service_info():
    """Get SciBERT service information"""
    try:
        service = get_scibert_service()
        info = service.get_service_info()
        
        return {
            "status": "success",
            "data": info,
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"SciBERT service info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service info: {str(e)}"
        )
