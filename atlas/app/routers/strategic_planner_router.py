#!/usr/bin/env python3
"""
AXIOM Strategic Planner Router
FastAPI endpoints for autonomous research strategy planning

Author: AXIOM Autonomous Laboratory System  
Date: September 13, 2025
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Optional, Any
from datetime import datetime
import logging

from app.exceptions.domain.biology import BiologyError
from app.services.strategic_planner_service import (
    strategic_planner,
    ResearchPriority,
    ResearchDomain,
    ObjectiveStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategic-planner", tags=["strategic-planner"])

@router.get("/status")
async def get_service_status():
    """
    🧠 Get Strategic Planner Service Status
    
    Returns comprehensive status of the autonomous strategic planning system
    including tracked knowledge gaps, active research objectives, and capabilities.
    """
    try:
        return await strategic_planner.get_service_status()
    except BiologyError as e:
        logger.error(f"Error getting strategic planner status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-knowledge-landscape")
async def analyze_knowledge_landscape():
    """
    🔍 Analyze Knowledge Landscape
    
    Autonomously scans literature and identifies knowledge gaps across
    all research domains. This is the foundation of strategic research planning.
    
    Returns analysis results including:
    - Number of papers analyzed
    - Knowledge gaps identified
    - Research trends detected 
    - Interdisciplinary opportunities
    """
    try:
        results = await strategic_planner.analyze_knowledge_landscape()
        logger.info(f"Knowledge landscape analysis completed: {results.get('gaps_identified', 0)} gaps found")
        return {
            "success": True,
            "message": "Knowledge landscape analysis completed",
            "analysis_results": results
        }
    except BiologyError as e:
        logger.error(f"Error analyzing knowledge landscape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-objectives")
async def generate_research_objectives(
    max_objectives: int = Query(10, description="Maximum number of objectives to generate", ge=1, le=50)
):
    """
    🎯 Generate Research Objectives
    
    Autonomously generates prioritized research objectives based on identified
    knowledge gaps, ROI calculations, and strategic value assessment.
    
    Each objective includes:
    - ROI estimates and resource requirements
    - Success criteria and risk factors
    - Dependencies and timeline estimates
    """
    try:
        objectives = await strategic_planner.generate_research_objectives(max_objectives)
        
        objectives_data = []
        for obj in objectives:
            objectives_data.append({
                "id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "domain": obj.domain.value,
                "priority": obj.priority.value,
                "roi_estimate": obj.roi_estimate,
                "estimated_duration_days": obj.estimated_duration.days,
                "required_resources": obj.required_resources,
                "success_criteria": obj.success_criteria,
                "risk_factors": obj.risk_factors,
                "dependencies": obj.dependencies,
                "status": obj.status.value,
                "created_at": obj.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": f"Generated {len(objectives)} research objectives",
            "objectives_count": len(objectives),
            "objectives": objectives_data
        }
    except BiologyError as e:
        logger.error(f"Error generating research objectives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/objectives")
async def get_research_objectives(
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    status: Optional[str] = Query(None, description="Filter by objective status")
):
    """
    📋 Get Research Objectives
    
    Retrieve all research objectives with optional filtering by domain,
    priority level, or status.
    """
    try:
        objectives = list(strategic_planner.research_objectives.values())
        
        # Apply filters
        if domain:
            try:
                domain_enum = ResearchDomain(domain)
                objectives = [obj for obj in objectives if obj.domain == domain_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
        
        if priority:
            try:
                priority_enum = ResearchPriority(priority)
                objectives = [obj for obj in objectives if obj.priority == priority_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
        
        if status:
            try:
                status_enum = ObjectiveStatus(status)
                objectives = [obj for obj in objectives if obj.status == status_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        objectives_data = []
        for obj in objectives:
            objectives_data.append({
                "id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "domain": obj.domain.value,
                "priority": obj.priority.value,
                "roi_estimate": obj.roi_estimate,
                "estimated_duration_days": obj.estimated_duration.days,
                "progress": obj.progress,
                "status": obj.status.value,
                "created_at": obj.created_at.isoformat(),
                "dependencies_count": len(obj.dependencies),
                "risk_factors_count": len(obj.risk_factors)
            })
        
        return {
            "success": True,
            "objectives_count": len(objectives_data),
            "objectives": objectives_data
        }
    except BiologyError as e:
        logger.error(f"Error getting research objectives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/objectives/{objective_id}")
async def get_objective_details(objective_id: str):
    """
    🎯 Get Objective Details
    
    Get detailed information for a specific research objective including
    all metadata, dependencies, and progress information.
    """
    try:
        if objective_id not in strategic_planner.research_objectives:
            raise HTTPException(status_code=404, detail=f"Objective {objective_id} not found")
        
        obj = strategic_planner.research_objectives[objective_id]
        
        return {
            "success": True,
            "objective": {
                "id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "domain": obj.domain.value,
                "priority": obj.priority.value,
                "knowledge_gaps": obj.knowledge_gaps,
                "estimated_duration_days": obj.estimated_duration.days,
                "required_resources": obj.required_resources,
                "success_criteria": obj.success_criteria,
                "roi_estimate": obj.roi_estimate,
                "risk_factors": obj.risk_factors,
                "dependencies": obj.dependencies,
                "status": obj.status.value,
                "progress": obj.progress,
                "created_at": obj.created_at.isoformat(),
                "planned_start": obj.planned_start.isoformat() if obj.planned_start else None,
                "actual_start": obj.actual_start.isoformat() if obj.actual_start else None,
                "completion_date": obj.completion_date.isoformat() if obj.completion_date else None
            }
        }
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error getting objective details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolios")
async def create_research_portfolio(
    portfolio_data: Dict[str, Any] = Body(..., description="Portfolio configuration")
):
    """
    📊 Create Research Portfolio
    
    Create an optimized research portfolio combining multiple objectives
    for balanced resource allocation and risk management.
    
    Expected format:
    {
        "name": "Portfolio Name",
        "objective_ids": ["obj_id_1", "obj_id_2"],
        "total_budget": 500000.0
    }
    """
    try:
        name = portfolio_data.get("name")
        objective_ids = portfolio_data.get("objective_ids", [])
        total_budget = portfolio_data.get("total_budget", 0)
        
        if not name:
            raise HTTPException(status_code=400, detail="Portfolio name is required")
        
        if not objective_ids:
            raise HTTPException(status_code=400, detail="At least one objective ID is required")
        
        if total_budget <= 0:
            raise HTTPException(status_code=400, detail="Total budget must be positive")
        
        portfolio = await strategic_planner.create_research_portfolio(
            name=name,
            objective_ids=objective_ids,
            total_budget=float(total_budget)
        )
        
        return {
            "success": True,
            "message": f"Research portfolio '{name}' created successfully",
            "portfolio": {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "objectives_count": len(portfolio.objectives),
                "total_budget": portfolio.total_budget,
                "allocated_budget": portfolio.allocated_budget,
                "expected_roi": portfolio.expected_roi,
                "risk_level": portfolio.risk_level,
                "created_at": portfolio.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error creating research portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolios")
async def get_research_portfolios():
    """
    📊 Get Research Portfolios
    
    Retrieve all research portfolios with their key metrics and status.
    """
    try:
        portfolios = list(strategic_planner.research_portfolios.values())
        
        portfolios_data = []
        for portfolio in portfolios:
            portfolios_data.append({
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "objectives_count": len(portfolio.objectives),
                "total_budget": portfolio.total_budget,
                "allocated_budget": portfolio.allocated_budget,
                "expected_roi": portfolio.expected_roi,
                "risk_level": portfolio.risk_level,
                "created_at": portfolio.created_at.isoformat(),
                "last_updated": portfolio.last_updated.isoformat()
            })
        
        return {
            "success": True,
            "portfolios_count": len(portfolios_data),
            "portfolios": portfolios_data
        }
    except BiologyError as e:
        logger.error(f"Error getting research portfolios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolios/{portfolio_id}/optimize")
async def optimize_portfolio(portfolio_id: str):
    """
    ⚡ Optimize Research Portfolio
    
    Apply advanced optimization algorithms to rebalance portfolio
    for maximum ROI and optimal resource allocation.
    """
    try:
        optimization_results = await strategic_planner.optimize_portfolio(portfolio_id)
        
        return {
            "success": True,
            "message": f"Portfolio {portfolio_id} optimization completed",
            "optimization_results": optimization_results
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-gaps")
async def get_knowledge_gaps(
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence threshold", ge=0.0, le=1.0),
    min_impact: Optional[float] = Query(None, description="Minimum impact threshold", ge=0.0, le=1.0)
):
    """
    🔍 Get Knowledge Gaps
    
    Retrieve identified knowledge gaps with optional filtering by domain,
    confidence level, or potential impact.
    """
    try:
        gaps = list(strategic_planner.knowledge_gaps.values())
        
        # Apply filters
        if domain:
            try:
                domain_enum = ResearchDomain(domain)
                gaps = [gap for gap in gaps if gap.domain == domain_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid domain: {domain}")
        
        if min_confidence is not None:
            gaps = [gap for gap in gaps if gap.confidence >= min_confidence]
        
        if min_impact is not None:
            gaps = [gap for gap in gaps if gap.potential_impact >= min_impact]
        
        gaps_data = []
        for gap in gaps:
            gaps_data.append({
                "id": gap.id,
                "title": gap.title,
                "description": gap.description,
                "domain": gap.domain.value,
                "confidence": gap.confidence,
                "potential_impact": gap.potential_impact,
                "difficulty": gap.difficulty,
                "priority_score": gap.priority_score,
                "required_resources": gap.required_resources,
                "related_publications_count": len(gap.related_publications),
                "identified_at": gap.identified_at.isoformat()
            })
        
        return {
            "success": True,
            "gaps_count": len(gaps_data),
            "knowledge_gaps": gaps_data
        }
    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error getting knowledge gaps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress")
async def monitor_research_progress():
    """
    📊 Monitor Research Progress
    
    Get comprehensive progress report for all research objectives
    including bottleneck identification and strategic recommendations.
    """
    try:
        progress_report = await strategic_planner.monitor_progress()
        
        return {
            "success": True,
            "message": "Progress monitoring completed",
            "progress_report": progress_report
        }
    except BiologyError as e:
        logger.error(f"Error monitoring research progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt-strategy")
async def adapt_research_strategy(
    performance_data: Optional[Dict[str, Any]] = Body(None, description="Performance data for strategy adaptation")
):
    """
    🔄 Adapt Research Strategy
    
    Automatically adjust research priorities and resource allocation
    based on performance data and changing conditions.
    """
    try:
        if performance_data is None:
            performance_data = {}
        
        adaptations = await strategic_planner.adapt_strategy(performance_data)
        
        return {
            "success": True,
            "message": "Strategy adaptation completed",
            "adaptations": adaptations
        }
    except BiologyError as e:
        logger.error(f"Error adapting research strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains")
async def get_research_domains():
    """
    🔬 Get Research Domains
    
    Get list of all supported research domains with current expertise levels.
    """
    try:
        domains_data = []
        for domain, expertise in strategic_planner.domain_expertise.items():
            domains_data.append({
                "domain": domain.value,
                "name": domain.value.replace("_", " ").title(),
                "expertise_level": expertise,
                "active_objectives": len([
                    obj for obj in strategic_planner.research_objectives.values()
                    if obj.domain == domain and obj.status in [ObjectiveStatus.IN_PROGRESS, ObjectiveStatus.PLANNED]
                ])
            })
        
        return {
            "success": True,
            "domains_count": len(domains_data),
            "research_domains": domains_data
        }
    except BiologyError as e:
        logger.error(f"Error getting research domains: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_strategic_analytics():
    """
    📈 Get Strategic Analytics
    
    Comprehensive analytics dashboard showing strategic planning metrics,
    performance trends, and optimization opportunities.
    """
    try:
        # Calculate key metrics
        objectives = list(strategic_planner.research_objectives.values())
        portfolios = list(strategic_planner.research_portfolios.values())
        gaps = list(strategic_planner.knowledge_gaps.values())
        
        # ROI analytics
        roi_distribution = {}
        for obj in objectives:
            roi_range = "high" if obj.roi_estimate > 5 else "medium" if obj.roi_estimate > 2 else "low"
            roi_distribution[roi_range] = roi_distribution.get(roi_range, 0) + 1
        
        # Domain distribution
        domain_distribution = {}
        for obj in objectives:
            domain = obj.domain.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        # Status distribution
        status_distribution = {}
        for obj in objectives:
            status = obj.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Risk analysis
        high_risk_objectives = len([obj for obj in objectives if len(obj.risk_factors) >= 3])
        
        # Calculate average progress
        total_progress = sum(obj.progress for obj in objectives)
        avg_progress = total_progress / len(objectives) if objectives else 0
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_objectives": len(objectives),
                    "total_portfolios": len(portfolios),
                    "total_knowledge_gaps": len(gaps),
                    "average_progress": avg_progress,
                    "high_risk_objectives": high_risk_objectives
                },
                "roi_distribution": roi_distribution,
                "domain_distribution": domain_distribution,
                "status_distribution": status_distribution,
                "performance_metrics": {
                    "objectives_per_domain": len(objectives) / len(ResearchDomain) if objectives else 0,
                    "average_roi": sum(obj.roi_estimate for obj in objectives) / len(objectives) if objectives else 0,
                    "completion_rate": len([obj for obj in objectives if obj.status == ObjectiveStatus.COMPLETED]) / len(objectives) if objectives else 0
                },
                "generated_at": datetime.now().isoformat()
            }
        }
    except BiologyError as e:
        logger.error(f"Error getting strategic analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

logger.info("🧠 Strategic Planner Router loaded with 15 endpoints")
