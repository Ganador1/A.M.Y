"""
Publication API Router - AXIOM META 4
RESTful API endpoints for automated scientific publication generation.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
import zipfile
import io
from pathlib import Path
import asyncio

from app.services.publication_generator import PublicationGeneratorService
from app.security import require_bearer
from app.exceptions.domain.biology import BiologyError
from app.types.publications_types import (
    GetPublicationResult,
    DeletePublicationResult,
    GetPublicationStatsResult,
)


# Initialize service
publication_service = PublicationGeneratorService()

# Create router
router = APIRouter(
    prefix="/api/publications",
    tags=["Publications"],
    dependencies=[Depends(require_bearer)]
)


# Pydantic models
class PublicationRequest(BaseModel):
    """Request model for publication generation"""
    hypothesis_id: Optional[str] = Field(None, description="Hypothesis ID to generate publication for")
    research_cycle_id: Optional[str] = Field(None, description="Research cycle ID")
    title: Optional[str] = Field(None, description="Custom publication title")
    custom_content: Dict[str, Any] = Field(default_factory=dict, description="Custom content sections")
    authors: List[str] = Field(default_factory=lambda: ["AXIOM Research Agent"], description="Authors list")
    domains: List[str] = Field(default_factory=list, description="Research domains")
    keywords: List[str] = Field(default_factory=list, description="Keywords")


class PublicationResponse(BaseModel):
    """Response model for publication operations"""
    success: bool
    pub_id: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    package_path: Optional[str] = None
    package_hash: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class PublicationListResponse(BaseModel):
    """Response model for publication list"""
    success: bool
    publications: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0
    error: Optional[str] = None


class PublicationValidationResponse(BaseModel):
    """Response model for publication validation"""
    success: bool
    pub_id: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate", response_model=PublicationResponse)
async def generate_publication(
    request: PublicationRequest,
    background_tasks: BackgroundTasks
) -> PublicationResponse:
    """
    Generate a complete scientific publication package
    
    - **hypothesis_id**: ID of hypothesis to generate publication for
    - **research_cycle_id**: ID of research cycle
    - **title**: Custom publication title
    - **custom_content**: Dictionary of custom content sections
    - **authors**: List of authors
    - **domains**: Research domains
    - **keywords**: Publication keywords
    """
    try:
        # Prepare request data
        request_data = {
            "action": "generate_publication",
            "hypothesis_id": request.hypothesis_id,
            "research_cycle_id": request.research_cycle_id,
            "title": request.title,
            "custom_content": {
                **request.custom_content,
                "authors": request.authors,
                "domains": request.domains,
                "keywords": request.keywords
            }
        }
        
        # Generate publication
        result = await publication_service.process_request(request_data)
        
        if result["success"]:
            return PublicationResponse(
                success=True,
                pub_id=result["pub_id"],
                doi=result["doi"],
                title=result.get("title"),
                package_path=result.get("package_path"),
                package_hash=result.get("package_hash"),
                created_at=result.get("created_at")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Publication generation failed")
            )
            
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating publication: {str(e)}"
        )


@router.get("/list", response_model=PublicationListResponse)
async def list_publications() -> PublicationListResponse:
    """
    List all generated publications with metadata
    """
    try:
        request_data = {"action": "list_publications"}
        result = await publication_service.process_request(request_data)
        
        if result["success"]:
            return PublicationListResponse(
                success=True,
                publications=result["publications"],
                total_count=result["total_count"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to list publications")
            )
            
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing publications: {str(e)}"
        )


@router.get("/{pub_id}", response_model=Dict[str, Any])
async def get_publication(pub_id: str) -> GetPublicationResult:
    """
    Get publication information by ID
    
    - **pub_id**: Publication ID
    """
    try:
        request_data = {"action": "get_publication", "pub_id": pub_id}
        result = await publication_service.process_request(request_data)
        
        if result["success"]:
            return result["publication"]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", f"Publication {pub_id} not found")
            )
            
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving publication: {str(e)}"
        )


@router.get("/{pub_id}/validate", response_model=PublicationValidationResponse)
async def validate_publication(pub_id: str) -> PublicationValidationResponse:
    """
    Validate publication integrity and blockchain proof
    
    - **pub_id**: Publication ID
    """
    try:
        request_data = {"action": "validate_publication", "pub_id": pub_id}
        result = await publication_service.process_request(request_data)
        
        if result["success"]:
            return PublicationValidationResponse(
                success=True,
                pub_id=pub_id,
                validation=result["validation"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", f"Publication {pub_id} not found")
            )
            
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating publication: {str(e)}"
        )


@router.get("/{pub_id}/download")
async def download_publication(pub_id: str) -> StreamingResponse:
    """
    Download publication package as ZIP file
    
    - **pub_id**: Publication ID
    """
    try:
        # Find publication directory
        pub_path = Path("./publications") / f"publication_{pub_id}"
        if not pub_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication {pub_id} not found"
            )
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in pub_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(pub_path)
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        
        # Return as streaming response
        def generate():
            yield zip_buffer.read()
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=publication_{pub_id}.zip"}
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading publication: {str(e)}"
        )


@router.get("/{pub_id}/files/{file_name}")
async def get_publication_file(pub_id: str, file_name: str) -> FileResponse:
    """
    Get specific file from publication package
    
    - **pub_id**: Publication ID  
    - **file_name**: Name of file to retrieve
    """
    try:
        pub_path = Path("./publications") / f"publication_{pub_id}"
        file_path = pub_path / file_name
        
        if not pub_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication {pub_id} not found"
            )
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_name} not found in publication {pub_id}"
            )
        
        # Security check - ensure file is within publication directory
        try:
            file_path.resolve().relative_to(pub_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return FileResponse(
            file_path,
            filename=file_name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving file: {str(e)}"
        )


@router.post("/{pub_id}/regenerate", response_model=PublicationResponse)
async def regenerate_publication(
    pub_id: str,
    request: PublicationRequest,
    background_tasks: BackgroundTasks
) -> PublicationResponse:
    """
    Regenerate an existing publication with updated content
    
    - **pub_id**: Publication ID to regenerate
    - **request**: Updated publication request data
    """
    try:
        # Check if publication exists
        pub_path = Path("./publications") / f"publication_{pub_id}"
        if not pub_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication {pub_id} not found"
            )
        
        # Generate new publication (will overwrite existing)
        request_data = {
            "action": "generate_publication",
            "hypothesis_id": request.hypothesis_id,
            "research_cycle_id": request.research_cycle_id,
            "title": request.title,
            "custom_content": {
                **request.custom_content,
                "authors": request.authors,
                "domains": request.domains,
                "keywords": request.keywords,
                "regeneration": True,
                "original_pub_id": pub_id
            }
        }
        
        result = await publication_service.process_request(request_data)
        
        if result["success"]:
            return PublicationResponse(
                success=True,
                pub_id=result["pub_id"],
                doi=result["doi"],
                title=result.get("title"),
                package_path=result.get("package_path"),
                package_hash=result.get("package_hash"),
                created_at=result.get("created_at")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Publication regeneration failed")
            )
            
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating publication: {str(e)}"
        )


@router.delete("/{pub_id}")
async def delete_publication(pub_id: str) -> DeletePublicationResult:
    """
    Delete a publication package
    
    - **pub_id**: Publication ID to delete
    """
    try:
        import shutil
        
        pub_path = Path("./publications") / f"publication_{pub_id}"
        if not pub_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication {pub_id} not found"
            )
        
        # Remove directory and all contents
        shutil.rmtree(pub_path)
        
        return {
            "success": True,
            "message": f"Publication {pub_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting publication: {str(e)}"
        )


@router.get("/{pub_id}/stats")
async def get_publication_stats(pub_id: str) -> GetPublicationStatsResult:
    """
    Get statistics for a publication
    
    - **pub_id**: Publication ID
    """
    try:
        pub_path = Path("./publications") / f"publication_{pub_id}"
        if not pub_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication {pub_id} not found"
            )
        
        # Calculate statistics
        total_files = len(list(pub_path.rglob("*")))
        total_size = sum(f.stat().st_size for f in pub_path.rglob("*") if f.is_file())
        
        # Read manifest for additional info
        manifest_path = pub_path / "manifest.json"
        manifest_data = {}
        if manifest_path.exists():
            import json
            manifest_data = json.loads(manifest_path.read_text())
        
        return {
            "success": True,
            "pub_id": pub_id,
            "stats": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "created_at": manifest_data.get("created_at"),
                "doi": manifest_data.get("doi"),
                "domains": manifest_data.get("domains", []),
                "consensus_score": manifest_data.get("consensus_score", 0.0),
                "blockchain_validated": bool(manifest_data.get("blockchain_proof"))
            }
        }
        
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting publication stats: {str(e)}"
        )
