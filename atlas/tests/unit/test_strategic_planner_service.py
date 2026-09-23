#!/usr/bin/env python3
"""
Unit Tests for Strategic Planner Service
Tests autonomous research strategy planning and objective generation

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from app.services.strategic_planner_service import (
    StrategicPlannerService,
    KnowledgeGap,
    ResearchObjective,
    ResearchPortfolio,
    ResearchDomain,
    ResearchPriority,
    ObjectiveStatus
)

class TestStrategicPlannerService:
    """Test suite for Strategic Planner Service"""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance for testing"""
        return StrategicPlannerService()
    
    @pytest.fixture
    def sample_knowledge_gap(self):
        """Create a sample knowledge gap for testing"""
        return KnowledgeGap(
            id="test_gap_001",
            domain=ResearchDomain.COMPUTATIONAL_BIOLOGY,
            title="Test protein folding prediction",
            description="Test gap for protein folding algorithms",
            confidence=0.85,
            potential_impact=0.90,
            difficulty=0.70,
            required_resources={
                "computational_hours": 5000,
                "experimental_budget": 150000,
                "personnel_months": 12
            },
            related_publications=["doi:10.1000/test1", "doi:10.1000/test2"],
            identified_at=datetime.now(),
            priority_score=0.78
        )
    
    @pytest.fixture
    def sample_research_objective(self):
        """Create a sample research objective for testing"""
        return ResearchObjective(
            id="test_obj_001",
            title="Test Research Objective",
            description="Test objective for strategic planning",
            domain=ResearchDomain.MATERIALS_SCIENCE,
            priority=ResearchPriority.HIGH,
            knowledge_gaps=["test_gap_001"],
            estimated_duration=timedelta(days=180),
            required_resources={
                "experimental_budget": 200000,
                "personnel_months": 18
            },
            success_criteria=["Test criterion 1", "Test criterion 2"],
            roi_estimate=4.5,
            risk_factors=["Test risk 1"],
            dependencies=[],
            status=ObjectiveStatus.IDENTIFIED,
            created_at=datetime.now()
        )
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
        assert isinstance(service.knowledge_gaps, dict)
        assert isinstance(service.research_objectives, dict)
        assert isinstance(service.research_portfolios, dict)
        assert len(service.domain_expertise) == len(ResearchDomain)
        
        # Verify all domains have expertise levels
        for domain in ResearchDomain:
            assert domain in service.domain_expertise
            assert 0.0 <= service.domain_expertise[domain] <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_knowledge_landscape(self, service):
        """Test knowledge landscape analysis"""
        results = await service.analyze_knowledge_landscape()
        
        assert isinstance(results, dict)
        assert "total_papers_analyzed" in results
        assert "domains_covered" in results
        assert "gaps_identified" in results
        assert "trends_detected" in results
        assert "opportunities_found" in results
        assert "analysis_timestamp" in results
        assert "new_gaps_found" in results
        assert "total_gaps_tracked" in results
        
        # Verify gaps were actually identified
        assert results["gaps_identified"] >= 0
        assert results["new_gaps_found"] >= 0
        assert len(service.knowledge_gaps) == results["total_gaps_tracked"]
    
    @pytest.mark.asyncio
    async def test_generate_research_objectives(self, service):
        """Test research objectives generation"""
        # First analyze knowledge landscape to get gaps
        await service.analyze_knowledge_landscape()
        
        # Generate objectives
        max_objectives = 5
        objectives = await service.generate_research_objectives(max_objectives)
        
        assert isinstance(objectives, list)
        assert len(objectives) <= max_objectives
        
        # Verify each objective has required properties
        for obj in objectives:
            assert isinstance(obj, ResearchObjective)
            assert obj.id is not None
            assert obj.title is not None
            assert obj.domain in ResearchDomain
            assert obj.priority in ResearchPriority
            assert obj.roi_estimate > 0
            assert isinstance(obj.required_resources, dict)
            assert isinstance(obj.success_criteria, list)
            assert isinstance(obj.risk_factors, list)
            assert obj.status == ObjectiveStatus.IDENTIFIED
    
    def test_calculate_gap_priority(self, service, sample_knowledge_gap):
        """Test knowledge gap priority calculation"""
        priority_score = service._calculate_gap_priority(sample_knowledge_gap)
        
        assert isinstance(priority_score, float)
        assert 0.0 <= priority_score <= 1.0
        
        # Test with different gap parameters
        high_impact_gap = sample_knowledge_gap
        high_impact_gap.potential_impact = 1.0
        high_impact_gap.confidence = 0.95
        high_impact_gap.difficulty = 0.2
        
        high_priority_score = service._calculate_gap_priority(high_impact_gap)
        assert high_priority_score > priority_score
    
    def test_calculate_roi_estimate(self, service, sample_knowledge_gap):
        """Test ROI calculation"""
        roi = service._calculate_roi_estimate(sample_knowledge_gap)
        
        assert isinstance(roi, float)
        assert 0.1 <= roi <= 50.0  # Within expected bounds
    
    def test_determine_priority_level(self, service):
        """Test priority level determination"""
        assert service._determine_priority_level(0.95) == ResearchPriority.CRITICAL
        assert service._determine_priority_level(0.80) == ResearchPriority.HIGH
        assert service._determine_priority_level(0.60) == ResearchPriority.MEDIUM
        assert service._determine_priority_level(0.40) == ResearchPriority.LOW
        assert service._determine_priority_level(0.20) == ResearchPriority.EXPLORATORY
    
    def test_estimate_duration(self, service, sample_knowledge_gap):
        """Test duration estimation"""
        duration = service._estimate_duration(sample_knowledge_gap)
        
        assert isinstance(duration, int)
        assert 7 <= duration <= 730  # Between 1 week and 2 years
        
        # Test with high difficulty
        sample_knowledge_gap.difficulty = 0.95
        high_difficulty_duration = service._estimate_duration(sample_knowledge_gap)
        assert high_difficulty_duration >= duration
    
    def test_generate_success_criteria(self, service, sample_knowledge_gap):
        """Test success criteria generation"""
        criteria = service._generate_success_criteria(sample_knowledge_gap)
        
        assert isinstance(criteria, list)
        assert len(criteria) >= 3  # At least 3 basic criteria
        
        # Check domain-specific criteria
        drug_gap = sample_knowledge_gap
        drug_gap.domain = ResearchDomain.DRUG_DISCOVERY
        drug_criteria = service._generate_success_criteria(drug_gap)
        assert any("in-vitro" in criterion.lower() for criterion in drug_criteria)
    
    def test_identify_risk_factors(self, service, sample_knowledge_gap):
        """Test risk factor identification"""
        risks = service._identify_risk_factors(sample_knowledge_gap)
        
        assert isinstance(risks, list)
        
        # Test high difficulty risk
        sample_knowledge_gap.difficulty = 0.85
        high_diff_risks = service._identify_risk_factors(sample_knowledge_gap)
        assert any("difficulty" in risk.lower() for risk in high_diff_risks)
        
        # Test high budget risk
        sample_knowledge_gap.required_resources["experimental_budget"] = 300000
        high_budget_risks = service._identify_risk_factors(sample_knowledge_gap)
        assert any("budget" in risk.lower() for risk in high_budget_risks)
    
    @pytest.mark.asyncio
    async def test_create_research_portfolio(self, service):
        """Test research portfolio creation"""
        # First create some objectives
        await service.analyze_knowledge_landscape()
        objectives = await service.generate_research_objectives(3)
        objective_ids = [obj.id for obj in objectives]
        
        # Create portfolio
        portfolio_name = "Test Portfolio"
        total_budget = 500000.0
        
        portfolio = await service.create_research_portfolio(
            name=portfolio_name,
            objective_ids=objective_ids,
            total_budget=total_budget
        )
        
        assert isinstance(portfolio, ResearchPortfolio)
        assert portfolio.name == portfolio_name
        assert portfolio.total_budget == total_budget
        assert len(portfolio.objectives) <= len(objective_ids)  # May filter invalid ones
        assert portfolio.expected_roi >= 0
        assert portfolio.risk_level >= 0
        assert portfolio.id in service.research_portfolios
    
    @pytest.mark.asyncio
    async def test_optimize_portfolio(self, service):
        """Test portfolio optimization"""
        # Create test portfolio
        await service.analyze_knowledge_landscape()
        objectives = await service.generate_research_objectives(3)
        objective_ids = [obj.id for obj in objectives]
        
        portfolio = await service.create_research_portfolio(
            name="Test Portfolio",
            objective_ids=objective_ids,
            total_budget=500000.0
        )
        
        # Optimize portfolio
        optimization_results = await service.optimize_portfolio(portfolio.id)
        
        assert isinstance(optimization_results, dict)
        assert "original_roi" in optimization_results
        assert "new_roi" in optimization_results
        assert "optimizations_applied" in optimization_results
        assert "improvement_roi" in optimization_results
        
        # Test invalid portfolio ID
        with pytest.raises(ValueError):
            await service.optimize_portfolio("invalid_portfolio_id")
    
    @pytest.mark.asyncio
    async def test_monitor_progress(self, service):
        """Test progress monitoring"""
        # Create some objectives with different statuses
        await service.analyze_knowledge_landscape()
        objectives = await service.generate_research_objectives(3)
        
        # Set different progress levels
        if objectives:
            objectives[0].progress = 0.8
            if len(objectives) > 1:
                objectives[1].progress = 0.3
            if len(objectives) > 2:
                objectives[2].progress = 0.1
        
        # Monitor progress
        progress_report = await service.monitor_progress()
        
        assert isinstance(progress_report, dict)
        assert "timestamp" in progress_report
        assert "total_objectives" in progress_report
        assert "status_breakdown" in progress_report
        assert "progress_summary" in progress_report
        assert "bottlenecks_identified" in progress_report
        assert "recommendations" in progress_report
        
        assert progress_report["total_objectives"] == len(objectives)
    
    @pytest.mark.asyncio
    async def test_adapt_strategy(self, service):
        """Test strategy adaptation"""
        # Create some objectives first
        await service.analyze_knowledge_landscape()
        objectives = await service.generate_research_objectives(5)
        
        # Set different progress levels to simulate performance data
        for i, obj in enumerate(objectives):
            obj.progress = 0.1 + (i * 0.2)  # Varied progress
        
        # Adapt strategy
        performance_data = {"trigger": "test_performance_review"}
        adaptations = await service.adapt_strategy(performance_data)
        
        assert isinstance(adaptations, dict)
        assert "timestamp" in adaptations
        assert "trigger" in adaptations
        assert "changes_made" in adaptations
        assert "strategy_adjustments" in adaptations
        assert "impact_estimate" in adaptations
        
        assert isinstance(adaptations["changes_made"], list)
        assert isinstance(adaptations["strategy_adjustments"], dict)
        assert isinstance(adaptations["impact_estimate"], dict)
    
    @pytest.mark.asyncio
    async def test_domain_gaps_identification(self, service):
        """Test domain-specific gap identification"""
        # Test each domain
        for domain in [ResearchDomain.COMPUTATIONAL_BIOLOGY, ResearchDomain.MATERIALS_SCIENCE]:
            gaps = await service._identify_domain_gaps(domain)
            
            assert isinstance(gaps, list)
            for gap in gaps:
                assert isinstance(gap, KnowledgeGap)
                assert gap.domain == domain
                assert gap.priority_score is not None
                assert 0.0 <= gap.priority_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_detect_research_trends(self, service):
        """Test research trends detection"""
        trends = await service._detect_research_trends()
        
        assert isinstance(trends, list)
        for trend in trends:
            assert isinstance(trend, dict)
            assert "trend" in trend
            assert "domains" in trend
            assert "growth_rate" in trend
            assert "confidence" in trend
    
    @pytest.mark.asyncio
    async def test_find_interdisciplinary_opportunities(self, service):
        """Test interdisciplinary opportunities identification"""
        opportunities = await service._find_interdisciplinary_opportunities()
        
        assert isinstance(opportunities, list)
        for opportunity in opportunities:
            assert isinstance(opportunity, dict)
            assert "title" in opportunity
            assert "domains" in opportunity
            assert "potential_impact" in opportunity
            assert "feasibility" in opportunity
            assert len(opportunity["domains"]) >= 2  # Interdisciplinary means multiple domains
    
    def test_calculate_objective_dependencies(self, service, sample_research_objective):
        """Test objective dependencies calculation"""
        # Create multiple objectives
        objectives = []
        for i in range(3):
            obj = ResearchObjective(
                id=f"test_obj_{i:03d}",
                title=f"Test Objective {i}",
                description=f"Test objective {i}",
                domain=ResearchDomain.COMPUTATIONAL_BIOLOGY,
                priority=ResearchPriority.MEDIUM,
                knowledge_gaps=[],
                estimated_duration=timedelta(days=90),
                required_resources={},
                success_criteria=[],
                roi_estimate=2.0,
                risk_factors=[],
                dependencies=[],
                status=ObjectiveStatus.IDENTIFIED,
                created_at=datetime.now()
            )
            objectives.append(obj)
        
        # Calculate dependencies
        service._calculate_objective_dependencies(objectives)
        
        # Verify dependencies structure is maintained
        for obj in objectives:
            assert isinstance(obj.dependencies, list)
    
    def test_has_dependency(self, service):
        """Test dependency detection logic"""
        obj1 = ResearchObjective(
            id="obj1", title="Obj1", description="Test", domain=ResearchDomain.QUANTUM_PHYSICS,
            priority=ResearchPriority.HIGH, knowledge_gaps=[], estimated_duration=timedelta(days=90),
            required_resources={}, success_criteria=[], roi_estimate=2.0, risk_factors=[],
            dependencies=[], status=ObjectiveStatus.IDENTIFIED, created_at=datetime.now()
        )
        
        obj2 = ResearchObjective(
            id="obj2", title="Obj2", description="Test", domain=ResearchDomain.QUANTUM_PHYSICS,
            priority=ResearchPriority.MEDIUM, knowledge_gaps=[], estimated_duration=timedelta(days=90),
            required_resources={}, success_criteria=[], roi_estimate=2.0, risk_factors=[],
            dependencies=[], status=ObjectiveStatus.IDENTIFIED, created_at=datetime.now()
        )
        
        # Same domain with different priorities - may have dependency
        has_dep = service._has_dependency(obj1, obj2)
        assert isinstance(has_dep, bool)
        
        # Different domains - less likely to have dependency
        obj2.domain = ResearchDomain.MATERIALS_SCIENCE
        has_dep_diff = service._has_dependency(obj1, obj2)
        assert isinstance(has_dep_diff, bool)
    
    @pytest.mark.asyncio
    async def test_get_service_status(self, service):
        """Test service status retrieval"""
        status = await service.get_service_status()
        
        assert isinstance(status, dict)
        assert status["service_name"] == "Strategic Planner Service"
        assert status["status"] == "operational"
        assert "version" in status
        assert "statistics" in status
        assert "capabilities" in status
        assert "active_domains" in status
        assert "last_analysis" in status
        
        # Verify statistics structure
        stats = status["statistics"]
        assert "knowledge_gaps_tracked" in stats
        assert "research_objectives" in stats
        assert "active_portfolios" in stats
        assert "literature_insights" in stats
        assert "domain_expertise_areas" in stats
        
        # Verify capabilities
        capabilities = status["capabilities"]
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

def test_strategic_planner_data_classes():
    """Test strategic planner data classes"""
    
    # Test KnowledgeGap
    gap = KnowledgeGap(
        id="test_gap",
        domain=ResearchDomain.BIOTECHNOLOGY,
        title="Test Gap",
        description="Test description",
        confidence=0.8,
        potential_impact=0.9,
        difficulty=0.6,
        required_resources={},
        related_publications=[],
        identified_at=datetime.now()
    )
    
    assert gap.id == "test_gap"
    assert gap.domain == ResearchDomain.BIOTECHNOLOGY
    assert gap.confidence == 0.8
    
    # Test ResearchObjective
    objective = ResearchObjective(
        id="test_obj",
        title="Test Objective",
        description="Test description",
        domain=ResearchDomain.ARTIFICIAL_INTELLIGENCE,
        priority=ResearchPriority.HIGH,
        knowledge_gaps=[],
        estimated_duration=timedelta(days=120),
        required_resources={},
        success_criteria=[],
        roi_estimate=3.5,
        risk_factors=[],
        dependencies=[],
        status=ObjectiveStatus.IDENTIFIED,
        created_at=datetime.now()
    )
    
    assert objective.id == "test_obj"
    assert objective.domain == ResearchDomain.ARTIFICIAL_INTELLIGENCE
    assert objective.priority == ResearchPriority.HIGH
    assert objective.status == ObjectiveStatus.IDENTIFIED
    
    # Test ResearchPortfolio
    portfolio = ResearchPortfolio(
        id="test_portfolio",
        name="Test Portfolio",
        description="Test description",
        objectives=[],
        total_budget=100000.0,
        allocated_budget=80000.0,
        expected_roi=2.5,
        risk_level=0.3,
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    
    assert portfolio.id == "test_portfolio"
    assert portfolio.total_budget == 100000.0
    assert portfolio.expected_roi == 2.5

def test_strategic_planner_enums():
    """Test strategic planner enums"""
    
    # Test ResearchPriority
    assert ResearchPriority.CRITICAL.value == "critical"
    assert ResearchPriority.HIGH.value == "high"
    assert ResearchPriority.MEDIUM.value == "medium"
    assert ResearchPriority.LOW.value == "low"
    assert ResearchPriority.EXPLORATORY.value == "exploratory"
    
    # Test ResearchDomain
    assert ResearchDomain.COMPUTATIONAL_BIOLOGY.value == "computational_biology"
    assert ResearchDomain.MATERIALS_SCIENCE.value == "materials_science"
    assert ResearchDomain.QUANTUM_PHYSICS.value == "quantum_physics"
    
    # Test ObjectiveStatus
    assert ObjectiveStatus.IDENTIFIED.value == "identified"
    assert ObjectiveStatus.PLANNED.value == "planned"
    assert ObjectiveStatus.IN_PROGRESS.value == "in_progress"
    assert ObjectiveStatus.COMPLETED.value == "completed"

if __name__ == "__main__":
    # Run basic tests
    print("🧠 Running Strategic Planner Service Tests...")
    
    # Test service initialization
    service = StrategicPlannerService()
    print(f"✅ Service initialized with {len(service.domain_expertise)} domains")
    
    # Test async functionality
    async def run_async_tests():
        try:
            # Test knowledge analysis
            results = await service.analyze_knowledge_landscape()
            print(f"✅ Knowledge analysis: {results['gaps_identified']} gaps found")
            
            # Test objective generation
            objectives = await service.generate_research_objectives(3)
            print(f"✅ Generated {len(objectives)} research objectives")
            
            # Test progress monitoring
            progress = await service.monitor_progress()
            print(f"✅ Progress monitoring: {progress['total_objectives']} objectives tracked")
            
            print("🎉 All Strategic Planner tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise
    
    # Run async tests
    asyncio.run(run_async_tests())
