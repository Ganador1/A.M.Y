#!/usr/bin/env python3
"""
AXIOM Strategic Planner Service
Autonomous research strategy planning and objective generation

This service enables AXIOM to independently identify research opportunities,
prioritize investigations, and plan scientific strategies without human intervention.

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict
from app.exceptions.domain.biology import BiologyError
from app.types.strategic_planner_service_types import (
    AnalyzeKnowledgeLandscapeResult,
    OptimizePortfolioResult,
    MonitorProgressResult,
    AdaptStrategyResult,
    GetServiceStatusResult,
)

logger = logging.getLogger(__name__)

class ResearchPriority(Enum):
    """Research priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPLORATORY = "exploratory"

class ResearchDomain(Enum):
    """Scientific research domains"""
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

class ObjectiveStatus(Enum):
    """Research objective status"""
    IDENTIFIED = "identified"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class KnowledgeGap:
    """Represents an identified knowledge gap"""
    id: str
    domain: ResearchDomain
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    potential_impact: float  # 0.0 to 1.0
    difficulty: float  # 0.0 to 1.0
    required_resources: Dict[str, Any]
    related_publications: List[str]
    identified_at: datetime
    priority_score: Optional[float] = None

@dataclass
class ResearchObjective:
    """Autonomous research objective"""
    id: str
    title: str
    description: str
    domain: ResearchDomain
    priority: ResearchPriority
    knowledge_gaps: List[str]  # KnowledgeGap IDs
    estimated_duration: timedelta
    required_resources: Dict[str, Any]
    success_criteria: List[str]
    roi_estimate: float
    risk_factors: List[str]
    dependencies: List[str]  # Other objective IDs
    status: ObjectiveStatus
    created_at: datetime
    planned_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    progress: float = 0.0

@dataclass
class ResearchPortfolio:
    """Portfolio of research objectives"""
    id: str
    name: str
    description: str
    objectives: List[str]  # ResearchObjective IDs
    total_budget: float
    allocated_budget: float
    expected_roi: float
    risk_level: float
    created_at: datetime
    last_updated: datetime

@dataclass
class LiteratureInsight:
    """Insight extracted from literature analysis"""
    id: str
    source_papers: List[str]
    insight_type: str  # "gap", "trend", "opportunity", "contradiction"
    domain: ResearchDomain
    title: str
    description: str
    confidence: float
    actionable: bool
    potential_experiments: List[str]
    discovered_at: datetime

class StrategicPlannerService:
    """
    Autonomous Strategic Research Planner
    
    This service acts as the "scientific brain" of AXIOM, independently:
    1. Analyzing literature to identify knowledge gaps
    2. Generating research objectives based on ROI and impact
    3. Planning research portfolios and resource allocation
    4. Monitoring progress and adapting strategies
    5. Identifying interdisciplinary opportunities
    """
    
    def __init__(self):
        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.research_objectives: Dict[str, ResearchObjective] = {}
        self.research_portfolios: Dict[str, ResearchPortfolio] = {}
        self.literature_insights: Dict[str, LiteratureInsight] = {}
        self.domain_expertise: Dict[ResearchDomain, float] = {}
        self.active_strategies: Dict[str, Any] = {}
        
        # Initialize domain expertise (simulated)
        self._initialize_domain_expertise()
        logger.info("🧠 Strategic Planner Service initialized")
    
    def _initialize_domain_expertise(self):
        """Initialize domain expertise levels"""
        for domain in ResearchDomain:
            # Simulate current expertise level (0.0 to 1.0)
            self.domain_expertise[domain] = np.random.uniform(0.3, 0.9)
    
    async def analyze_knowledge_landscape(self) -> AnalyzeKnowledgeLandscapeResult:
        """
        🔍 Analyze current knowledge landscape to identify gaps
        
        This is the foundation of autonomous research planning.
        It scans literature, existing knowledge, and identifies areas
        where new research could have significant impact.
        """
        logger.info("🔍 Analyzing knowledge landscape for gaps and opportunities")
        
        try:
            # Simulate literature analysis (in production, would use real literature APIs)
            analysis_results = {
                "total_papers_analyzed": np.random.randint(10000, 50000),
                "domains_covered": len(ResearchDomain),
                "gaps_identified": 0,
                "trends_detected": 0,
                "opportunities_found": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "new_gaps_found": 0,
                "total_gaps_tracked": 0
            }
            
            # Identify knowledge gaps by domain
            gaps_found = []
            for domain in ResearchDomain:
                domain_gaps = await self._identify_domain_gaps(domain)
                gaps_found.extend(domain_gaps)
                analysis_results["gaps_identified"] += len(domain_gaps)
            
            # Detect emerging trends
            trends = await self._detect_research_trends()
            analysis_results["trends_detected"] = len(trends)
            
            # Find interdisciplinary opportunities
            opportunities = await self._find_interdisciplinary_opportunities()
            analysis_results["opportunities_found"] = len(opportunities)
            
            # Store insights
            for gap in gaps_found:
                self.knowledge_gaps[gap.id] = gap
            
            analysis_results["analysis_timestamp"] = datetime.now().isoformat()
            analysis_results["new_gaps_found"] = len(gaps_found)
            analysis_results["total_gaps_tracked"] = len(self.knowledge_gaps)
            
            logger.info(f"📊 Knowledge landscape analysis complete: {len(gaps_found)} new gaps identified")
            return analysis_results
            
        except BiologyError as e:
            logger.error(f"❌ Error in knowledge landscape analysis: {str(e)}")
            raise
    
    async def _identify_domain_gaps(self, domain: ResearchDomain) -> List[KnowledgeGap]:
        """Identify knowledge gaps in a specific domain"""
        gaps = []
        
        # Simulate domain-specific gap identification
        domain_specific_gaps = {
            ResearchDomain.COMPUTATIONAL_BIOLOGY: [
                "Protein folding prediction for intrinsically disordered proteins",
                "Multi-scale modeling of cellular metabolism",
                "AI-driven drug-target interaction prediction"
            ],
            ResearchDomain.MATERIALS_SCIENCE: [
                "High-temperature superconductor design principles",
                "Biodegradable electronics materials",
                "Self-healing composite materials"
            ],
            ResearchDomain.QUANTUM_PHYSICS: [
                "Room-temperature quantum coherence mechanisms",
                "Quantum error correction for noisy intermediate-scale devices",
                "Quantum-classical interface optimization"
            ],
            ResearchDomain.CLIMATE_SCIENCE: [
                "Tipping point prediction in climate systems",
                "Carbon capture efficiency in natural ecosystems",
                "Ocean acidification impact on marine biodiversity"
            ],
            ResearchDomain.DRUG_DISCOVERY: [
                "AI-guided molecular design for rare diseases",
                "Personalized medicine based on genetic profiles",
                "Drug delivery systems for brain-blood barrier crossing"
            ]
        }
        
        potential_gaps = domain_specific_gaps.get(domain, ["General research opportunities"])
        num_gaps = np.random.randint(1, 4)
        selected_gaps = np.random.choice(potential_gaps, min(num_gaps, len(potential_gaps)), replace=False)
        
        for i, gap_title in enumerate(selected_gaps):
            gap_id = f"gap_{domain.value}_{int(datetime.now().timestamp())}_{i}"
            gap = KnowledgeGap(
                id=gap_id,
                domain=domain,
                title=gap_title,
                description=f"Research opportunity in {gap_title.lower()} with significant potential impact",
                confidence=np.random.uniform(0.6, 0.95),
                potential_impact=np.random.uniform(0.5, 1.0),
                difficulty=np.random.uniform(0.3, 0.9),
                required_resources={
                    "computational_hours": np.random.randint(100, 10000),
                    "experimental_budget": np.random.randint(10000, 500000),
                    "personnel_months": np.random.randint(3, 24),
                    "specialized_equipment": np.random.choice([True, False])
                },
                related_publications=["doi:10.1000/example"] * np.random.randint(0, 5),
                identified_at=datetime.now()
            )
            
            # Calculate priority score
            gap.priority_score = self._calculate_gap_priority(gap)
            gaps.append(gap)
        
        return gaps
    
    def _calculate_gap_priority(self, gap: KnowledgeGap) -> float:
        """Calculate priority score for a knowledge gap"""
        # Weighted combination of factors
        impact_weight = 0.4
        confidence_weight = 0.3
        feasibility_weight = 0.2
        domain_expertise_weight = 0.1
        
        feasibility = 1.0 - gap.difficulty  # Higher difficulty = lower feasibility
        domain_expertise = self.domain_expertise.get(gap.domain, 0.5)
        
        priority_score = (
            gap.potential_impact * impact_weight +
            gap.confidence * confidence_weight +
            feasibility * feasibility_weight +
            domain_expertise * domain_expertise_weight
        )
        
        return min(1.0, max(0.0, priority_score))
    
    async def _detect_research_trends(self) -> List[Dict[str, Any]]:
        """Detect emerging research trends"""
        trends = [
            {
                "trend": "AI-accelerated materials discovery",
                "domains": ["materials_science", "artificial_intelligence"],
                "growth_rate": 0.45,
                "confidence": 0.85
            },
            {
                "trend": "Quantum machine learning algorithms", 
                "domains": ["quantum_physics", "artificial_intelligence"],
                "growth_rate": 0.38,
                "confidence": 0.78
            },
            {
                "trend": "Synthetic biology for climate solutions",
                "domains": ["biotechnology", "climate_science"],
                "growth_rate": 0.52,
                "confidence": 0.82
            }
        ]
        return trends
    
    async def _find_interdisciplinary_opportunities(self) -> List[Dict[str, Any]]:
        """Find opportunities at intersection of disciplines"""
        opportunities = [
            {
                "title": "Quantum-enhanced drug discovery",
                "domains": ["quantum_physics", "drug_discovery"],
                "potential_impact": 0.9,
                "feasibility": 0.6
            },
            {
                "title": "AI-driven climate modeling with materials innovation",
                "domains": ["artificial_intelligence", "climate_science", "materials_science"],
                "potential_impact": 0.95,
                "feasibility": 0.7
            }
        ]
        return opportunities
    
    async def generate_research_objectives(self, max_objectives: int = 10) -> List[ResearchObjective]:
        """
        🎯 Generate research objectives based on identified knowledge gaps
        
        This function autonomously creates research objectives by:
        1. Analyzing identified knowledge gaps
        2. Calculating ROI and resource requirements
        3. Prioritizing based on strategic value
        4. Creating actionable research plans
        """
        logger.info(f"🎯 Generating up to {max_objectives} research objectives")
        
        try:
            # Ensure we have knowledge gaps to work with
            if not self.knowledge_gaps:
                await self.analyze_knowledge_landscape()
            
            # Sort gaps by priority score
            sorted_gaps = sorted(
                self.knowledge_gaps.values(),
                key=lambda g: g.priority_score or 0,
                reverse=True
            )
            
            objectives = []
            
            for i, gap in enumerate(sorted_gaps[:max_objectives]):
                objective_id = f"obj_{gap.domain.value}_{int(datetime.now().timestamp())}_{i}"
                
                # Calculate ROI estimate
                roi_estimate = self._calculate_roi_estimate(gap)
                
                # Determine priority level
                priority = self._determine_priority_level(gap.priority_score or 0.5)
                
                # Estimate duration based on complexity and resources
                duration_days = self._estimate_duration(gap)
                
                # Generate success criteria
                success_criteria = self._generate_success_criteria(gap)
                
                # Identify risk factors
                risk_factors = self._identify_risk_factors(gap)
                
                objective = ResearchObjective(
                    id=objective_id,
                    title=f"Investigate {gap.title}",
                    description=f"Comprehensive research into {gap.description}",
                    domain=gap.domain,
                    priority=priority,
                    knowledge_gaps=[gap.id],
                    estimated_duration=timedelta(days=duration_days),
                    required_resources=gap.required_resources.copy(),
                    success_criteria=success_criteria,
                    roi_estimate=roi_estimate,
                    risk_factors=risk_factors,
                    dependencies=[],  # Will be calculated later
                    status=ObjectiveStatus.IDENTIFIED,
                    created_at=datetime.now()
                )
                
                self.research_objectives[objective_id] = objective
                objectives.append(objective)
            
            # Calculate dependencies between objectives
            self._calculate_objective_dependencies(objectives)
            
            logger.info(f"🎯 Generated {len(objectives)} research objectives")
            return objectives
            
        except BiologyError as e:
            logger.error(f"❌ Error generating research objectives: {str(e)}")
            raise
    
    def _calculate_roi_estimate(self, gap: KnowledgeGap) -> float:
        """Calculate ROI estimate for addressing a knowledge gap"""
        # Simplified ROI calculation based on impact vs resources
        impact_value = gap.potential_impact * 1000000  # Simulated impact in dollars
        resource_cost = gap.required_resources.get("experimental_budget", 100000)
        
        if resource_cost > 0:
            roi = (impact_value - resource_cost) / resource_cost
        else:
            roi = gap.potential_impact * 10  # High ROI for low-cost research
        
        return max(0.1, min(50.0, roi))  # Clamp between 0.1 and 50
    
    def _determine_priority_level(self, priority_score: float) -> ResearchPriority:
        """Convert numeric priority score to priority level"""
        if priority_score >= 0.9:
            return ResearchPriority.CRITICAL
        elif priority_score >= 0.7:
            return ResearchPriority.HIGH
        elif priority_score >= 0.5:
            return ResearchPriority.MEDIUM
        elif priority_score >= 0.3:
            return ResearchPriority.LOW
        else:
            return ResearchPriority.EXPLORATORY
    
    def _estimate_duration(self, gap: KnowledgeGap) -> int:
        """Estimate duration in days for research objective"""
        base_duration = 30  # Base 30 days
        
        # Adjust based on difficulty
        difficulty_multiplier = 1 + (gap.difficulty * 2)
        
        # Adjust based on required resources
        resource_multiplier = 1.0
        if gap.required_resources.get("specialized_equipment", False):
            resource_multiplier += 0.5
        
        personnel_months = gap.required_resources.get("personnel_months", 6)
        resource_multiplier += personnel_months / 12
        
        duration = int(base_duration * difficulty_multiplier * resource_multiplier)
        return min(365 * 2, max(7, duration))  # Between 1 week and 2 years
    
    def _generate_success_criteria(self, gap: KnowledgeGap) -> List[str]:
        """Generate success criteria for research objective"""
        criteria = [
            f"Achieve {gap.confidence * 100:.1f}% confidence in results",
            "Publish findings in peer-reviewed journal",
            "Validate results through independent experiments"
        ]
        
        if gap.domain == ResearchDomain.DRUG_DISCOVERY:
            criteria.append("Demonstrate in-vitro efficacy")
        elif gap.domain == ResearchDomain.MATERIALS_SCIENCE:
            criteria.append("Characterize material properties")
        elif gap.domain == ResearchDomain.COMPUTATIONAL_BIOLOGY:
            criteria.append("Validate computational predictions experimentally")
        
        return criteria
    
    def _identify_risk_factors(self, gap: KnowledgeGap) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        if gap.difficulty > 0.8:
            risks.append("High technical difficulty may extend timeline")
        
        if gap.required_resources.get("experimental_budget", 0) > 200000:
            risks.append("High budget requirements may limit funding availability")
        
        if gap.required_resources.get("specialized_equipment", False):
            risks.append("Dependency on specialized equipment availability")
        
        if gap.confidence < 0.6:
            risks.append("Low initial confidence in research direction")
        
        return risks
    
    def _calculate_objective_dependencies(self, objectives: List[ResearchObjective]):
        """Calculate dependencies between research objectives"""
        for i, obj1 in enumerate(objectives):
            for j, obj2 in enumerate(objectives):
                if i != j:
                    # Check for logical dependencies
                    if self._has_dependency(obj1, obj2):
                        obj1.dependencies.append(obj2.id)
    
    def _has_dependency(self, obj1: ResearchObjective, obj2: ResearchObjective) -> bool:
        """Check if obj1 depends on obj2"""
        # Simple heuristic: same domain objectives may have dependencies
        if obj1.domain == obj2.domain:
            # Higher priority objectives may depend on lower priority ones
            if obj1.priority.value > obj2.priority.value:
                return np.random.choice([True, False], p=[0.3, 0.7])
        
        return False
    
    async def create_research_portfolio(
        self,
        name: str,
        objective_ids: List[str],
        total_budget: float
    ) -> ResearchPortfolio:
        """
        📊 Create optimized research portfolio
        
        Combines multiple research objectives into a balanced portfolio
        that maximizes scientific impact while managing risk and resources.
        """
        logger.info(f"📊 Creating research portfolio: {name}")
        
        try:
            portfolio_id = f"portfolio_{int(datetime.now().timestamp())}"
            
            # Validate objectives exist
            valid_objectives = []
            for obj_id in objective_ids:
                if obj_id in self.research_objectives:
                    valid_objectives.append(obj_id)
                else:
                    logger.warning(f"⚠️ Objective {obj_id} not found, skipping")
            
            # Calculate portfolio metrics
            total_cost = 0
            expected_roi = 0
            risk_level = 0
            
            for obj_id in valid_objectives:
                obj = self.research_objectives[obj_id]
                obj_cost = obj.required_resources.get("experimental_budget", 50000)
                total_cost += obj_cost
                expected_roi += obj.roi_estimate * (obj_cost / total_budget if total_budget > 0 else 1)
                risk_level += len(obj.risk_factors) / len(valid_objectives)
            
            if total_cost > total_budget:
                logger.warning(f"⚠️ Portfolio cost ({total_cost}) exceeds budget ({total_budget})")
            
            portfolio = ResearchPortfolio(
                id=portfolio_id,
                name=name,
                description=f"Strategic research portfolio with {len(valid_objectives)} objectives",
                objectives=valid_objectives,
                total_budget=total_budget,
                allocated_budget=min(total_cost, total_budget),
                expected_roi=expected_roi,
                risk_level=risk_level,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.research_portfolios[portfolio_id] = portfolio
            
            logger.info(f"📊 Research portfolio created: {len(valid_objectives)} objectives, ROI: {expected_roi:.2f}")
            return portfolio
            
        except BiologyError as e:
            logger.error(f"❌ Error creating research portfolio: {str(e)}")
            raise
    
    async def optimize_portfolio(self, portfolio_id: str) -> OptimizePortfolioResult:
        """
        ⚡ Optimize research portfolio for maximum ROI
        
        Uses advanced algorithms to rebalance portfolio for optimal
        resource allocation and timeline scheduling.
        """
        logger.info(f"⚡ Optimizing portfolio: {portfolio_id}")
        
        if portfolio_id not in self.research_portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        portfolio = self.research_portfolios[portfolio_id]
        
        # Get all objectives in portfolio
        objectives = [self.research_objectives[obj_id] for obj_id in portfolio.objectives]
        
        # Optimization using simple heuristics (in production, use advanced algorithms)
        optimization_results = {
            "original_roi": portfolio.expected_roi,
            "original_risk": portfolio.risk_level,
            "optimizations_applied": [],
            "new_roi": portfolio.expected_roi,
            "new_risk": portfolio.risk_level
        }
        
        # Reorder objectives by ROI/risk ratio
        objectives.sort(key=lambda obj: obj.roi_estimate / (len(obj.risk_factors) + 1), reverse=True)
        
        # Check budget allocation
        if portfolio.allocated_budget < portfolio.total_budget:
            remaining_budget = portfolio.total_budget - portfolio.allocated_budget
            optimization_results["optimizations_applied"].append(
                f"Allocated remaining budget: ${remaining_budget:,.2f}"
            )
        
        # Calculate new metrics
        new_roi = sum(obj.roi_estimate for obj in objectives) / len(objectives)
        new_risk = sum(len(obj.risk_factors) for obj in objectives) / len(objectives)
        
        optimization_results["new_roi"] = new_roi
        optimization_results["new_risk"] = new_risk
        optimization_results["improvement_roi"] = new_roi - portfolio.expected_roi
        optimization_results["improvement_risk"] = portfolio.risk_level - new_risk
        
        # Update portfolio
        portfolio.expected_roi = new_roi
        portfolio.risk_level = new_risk
        portfolio.last_updated = datetime.now()
        
        logger.info(f"⚡ Portfolio optimization complete: ROI improved by {optimization_results['improvement_roi']:.2f}")
        return optimization_results
    
    async def monitor_progress(self) -> MonitorProgressResult:
        """
        📊 Monitor progress of all research objectives
        
        Tracks progress, identifies bottlenecks, and suggests adjustments
        to research strategy based on current performance.
        """
        logger.info("📊 Monitoring research progress")
        
        progress_report = {
            "timestamp": datetime.now().isoformat(),
            "total_objectives": len(self.research_objectives),
            "status_breakdown": defaultdict(int),
            "progress_summary": {},
            "bottlenecks_identified": [],
            "recommendations": []
        }
        
        # Analyze objective statuses
        total_progress = 0
        for obj in self.research_objectives.values():
            progress_report["status_breakdown"][obj.status.value] += 1
            total_progress += obj.progress
        
        # Calculate average progress
        avg_progress = 0.0
        if self.research_objectives:
            avg_progress = total_progress / len(self.research_objectives)
            progress_report["progress_summary"]["average_progress"] = avg_progress
            
            # Identify bottlenecks
            if avg_progress < 0.3:
                progress_report["bottlenecks_identified"].append("Overall progress below expected rate")
                progress_report["recommendations"].append("Review resource allocation and priorities")
        
        # Check for overdue objectives
        overdue_count = 0
        for obj in self.research_objectives.values():
            if (obj.planned_start and 
                obj.planned_start < datetime.now() and 
                obj.status == ObjectiveStatus.IDENTIFIED):
                overdue_count += 1
        
        if overdue_count > 0:
            progress_report["bottlenecks_identified"].append(f"{overdue_count} objectives overdue to start")
            progress_report["recommendations"].append("Review scheduling and resource availability")
        
        progress_report["overdue_objectives"] = overdue_count
        
        logger.info(f"📊 Progress monitoring complete: {avg_progress:.1%} average progress")
        return progress_report
    
    async def adapt_strategy(self, performance_data: AdaptStrategyResult) -> AdaptStrategyResult:
        """
        🔄 Adapt research strategy based on performance data
        
        Automatically adjusts research priorities, resource allocation,
        and strategic focus based on ongoing results and changing conditions.
        """
        logger.info("🔄 Adapting research strategy based on performance")
        
        adaptations = {
            "timestamp": datetime.now().isoformat(),
            "trigger": "performance_review",
            "changes_made": [],
            "strategy_adjustments": {},
            "impact_estimate": {}
        }
        
        # Analyze performance trends
        high_performing_domains = []
        low_performing_domains = []
        
        # Group by domain and analyze performance
        domain_performance = defaultdict(list)
        for obj in self.research_objectives.values():
            domain_performance[obj.domain].append(obj.progress)
        
        for domain, progress_list in domain_performance.items():
            avg_domain_progress = np.mean(progress_list)
            if avg_domain_progress > 0.7:
                high_performing_domains.append(domain.value)
            elif avg_domain_progress < 0.3:
                low_performing_domains.append(domain.value)
        
        # Strategy adaptations
        if high_performing_domains:
            adaptations["changes_made"].append(f"Increased priority for high-performing domains: {high_performing_domains}")
            adaptations["strategy_adjustments"]["priority_boost"] = high_performing_domains
        
        if low_performing_domains:
            adaptations["changes_made"].append(f"Resource reallocation from low-performing domains: {low_performing_domains}")
            adaptations["strategy_adjustments"]["resource_reduction"] = low_performing_domains
        
        # Update domain expertise based on results
        for domain in ResearchDomain:
            if domain.value in high_performing_domains:
                self.domain_expertise[domain] = min(1.0, self.domain_expertise[domain] + 0.1)
            elif domain.value in low_performing_domains:
                self.domain_expertise[domain] = max(0.1, self.domain_expertise[domain] - 0.05)
        
        adaptations["impact_estimate"] = {
            "expected_roi_improvement": len(high_performing_domains) * 0.1,
            "risk_reduction": len(low_performing_domains) * 0.05,
            "efficiency_gain": 0.15 if adaptations["changes_made"] else 0.0
        }
        
        logger.info(f"🔄 Strategy adaptation complete: {len(adaptations['changes_made'])} changes made")
        return adaptations
    
    async def get_service_status(self) -> GetServiceStatusResult:
        """Get comprehensive service status"""
        return {
            "service_name": "Strategic Planner Service",
            "status": "operational",
            "version": "1.0.0",
            "statistics": {
                "knowledge_gaps_tracked": len(self.knowledge_gaps),
                "research_objectives": len(self.research_objectives),
                "active_portfolios": len(self.research_portfolios),
                "literature_insights": len(self.literature_insights),
                "domain_expertise_areas": len(self.domain_expertise)
            },
            "capabilities": [
                "Autonomous knowledge gap identification",
                "ROI-based research prioritization", 
                "Strategic portfolio optimization",
                "Real-time progress monitoring",
                "Adaptive strategy adjustment",
                "Interdisciplinary opportunity discovery"
            ],
            "active_domains": list(self.domain_expertise.keys()),
            "last_analysis": datetime.now().isoformat()
        }

# Global service instance
strategic_planner = StrategicPlannerService()

logger.info("🧠 Strategic Planner Service module loaded")
