"""
Agent 2 Bridge Router Wrapper

This module serves as a wrapper to import the agent2_bridge_router functionality.
It provides a consistent import path for the main application while maintaining
compatibility with the existing agent bridge infrastructure.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging

from app.exceptions.infrastructure.api import APIError
from app.services.agent2_bridge_service import (
    Agent2BridgeService,
    DataIngestionRequest,
    DataIngestionResponse,
    Agent2ServiceStatus,
    agent2_bridge_service
)
from app.core.bootstrap_logging import logger

router = APIRouter(
    prefix="/api/agent2-bridge",
    tags=["Agent 2 Bridge"],
    responses={404: {"description": "Not found"}}
)


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for Agent 2 Bridge service"""
    return {
        "status": "healthy",
        "service": "agent2_bridge",
        "timestamp": "2025-01-20T00:00:00Z"
    }


@router.get("/services", response_model=Dict[str, Agent2ServiceStatus])
async def get_available_services():
    """
    Get available Agent 2 services and their status
    """
    return await agent2_bridge_service.discover_services()


@router.post("/ingest", response_model=DataIngestionResponse)
async def ingest_dataset(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest dataset from Agent 2 into Agent 3 for scientific analysis
    """
    try:
        response = await agent2_bridge_service.ingest_dataset(request)
        
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": response.message,
                    "validation_errors": response.validation_errors
                }
            )
            
        return response
        
    except HTTPException:
        raise
    except APIError as e:
        logger.error(f"Dataset ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


__all__ = ['router']