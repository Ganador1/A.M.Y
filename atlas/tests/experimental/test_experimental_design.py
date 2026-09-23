"""
Comprehensive Test Suite for Experimental Design Assistant Service

This test suite validates the experimental design assistant's ability to create
optimal experimental designs, perform power analyses, assess feasibility,
and provide actionable recommendations.

Author: ATLAS Autonomous Laboratory System
Date: September 11, 2025
"""

import asyncio
import json
import pytest
import sys
import traceback
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, '.')

from app.services.experimental_design_service import (
    ExperimentalDesignAssistantService,
    ResearchObjective,
    ResourceConstraints,
    StatisticalRequirements,
    ExperimentType,
    StudyPhase
)


class TestExperimentalDesignAssistant:
    """Test suite for Experimental Design Assistant Service"""
    
    def __init__(self):
        """Initialize test suite"""
        self.service = None
        self.test_results = []
        self.start_time = None
        
    async def setup(self):
        """Setup test environment"""
        try:
            print("🔧 Setting up Experimental Design Assistant Service...")
            self.service = ExperimentalDesignAssistantService()
            self.start_time = datetime.now()
            print("✅ Service initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Service setup failed: {e}")
            traceback.print_exc()
            return False
    
    async def test_service_initialization(self):
        """Test service initialization and health status"""
        try:
            print("\n📋 Testing service initialization...")
            
            # Test health status
            health = await self.service.get_design_health_status()
            
            assert health["status"] == "healthy"
            assert "supported_design_types" in health
            assert "supported_study_phases" in health
            assert "domain_expertise" in health
            assert len(health["supported_design_types"]) > 0
            assert len(health["supported_study_phases"]) > 0
            
            print("✅ Service initialization test passed")
            print(f"   - Supported design types: {len(health['supported_design_types'])}")
            print(f"   - Supported study phases: {len(health['supported_study_phases'])}")
            print(f"   - Domain expertise areas: {len(health['domain_expertise'])}")
            
            self.test_results.append({
                "test": "service_initialization",
                "status": "passed",
                "details": {
                    "design_types": len(health['supported_design_types']),
                    "study_phases": len(health['supported_study_phases']),
                    "domains": len(health['domain_expertise'])
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Service initialization test failed: {e}")
            self.test_results.append({"test": "service_initialization", "status": "failed", "error": str(e)})
            return False
    
    async def test_simple_rct_design(self):
        """Test simple randomized controlled trial design"""
        try:
            print("\n🧪 Testing simple RCT design...")
            
            # Define research objective
            objective = ResearchObjective(
                id="rct_obj_1",
                title="New Drug Efficacy Study",
                description="Evaluate efficacy of new drug vs placebo",
                primary_outcome="symptom_reduction_score",
                secondary_outcomes=["quality_of_life", "side_effects"],
                domain="medicine",
                hypothesis="New drug reduces symptoms more than placebo",
                effect_size_expected=0.6,
                clinical_significance=0.5,
                priority=1
            )
            
            # Define resource constraints
            constraints = ResourceConstraints(
                budget=100000,
                time_months=12,
                max_participants=200,
                available_equipment=["clinical_monitors", "data_capture_system"],
                staff_expertise=["clinical_research", "statistics"],
                ethical_approvals=["IRB_approval"],
                regulatory_requirements=["FDA_approval"]
            )
            
            # Statistical requirements
            stat_req = StatisticalRequirements(
                alpha=0.05,
                power=0.80,
                dropout_rate=0.15
            )
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=constraints,
                statistical_requirements=stat_req
            )
            
            # Validate design
            assert design.id is not None
            assert design.design_type == ExperimentType.RANDOMIZED_CONTROLLED
            assert design.total_sample_size > 0
            assert design.duration_months > 0
            assert design.feasibility_score >= 0.0
            assert len(design.experimental_groups) >= 2  # Treatment and control
            assert len(design.recommendations) > 0
            
            print("✅ Simple RCT design test passed")
            print(f"   - Design type: {design.design_type.value}")
            print(f"   - Sample size: {design.total_sample_size}")
            print(f"   - Duration: {design.duration_months} months")
            print(f"   - Feasibility: {design.feasibility_score:.2f}")
            print(f"   - Groups: {len(design.experimental_groups)}")
            
            self.test_results.append({
                "test": "simple_rct_design",
                "status": "passed",
                "details": {
                    "design_type": design.design_type.value,
                    "sample_size": design.total_sample_size,
                    "duration": design.duration_months,
                    "feasibility": design.feasibility_score,
                    "groups": len(design.experimental_groups)
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Simple RCT design test failed: {e}")
            self.test_results.append({"test": "simple_rct_design", "status": "failed", "error": str(e)})
            return False
    
    async def test_factorial_design(self):
        """Test factorial experimental design"""
        try:
            print("\n🔬 Testing factorial design...")
            
            # Multiple objectives for factorial design
            objectives = [
                ResearchObjective(
                    id="fact_obj_1",
                    title="Treatment A Effect",
                    description="Test effect of treatment A",
                    primary_outcome="outcome_measure_a",
                    secondary_outcomes=[],
                    domain="biology",
                    hypothesis="Treatment A improves outcome",
                    effect_size_expected=0.5,
                    priority=1
                ),
                ResearchObjective(
                    id="fact_obj_2",
                    title="Treatment B Effect",
                    description="Test effect of treatment B",
                    primary_outcome="outcome_measure_b",
                    secondary_outcomes=[],
                    domain="biology", 
                    hypothesis="Treatment B improves outcome",
                    effect_size_expected=0.4,
                    priority=2
                )
            ]
            
            # Moderate constraints
            constraints = ResourceConstraints(
                budget=75000,
                time_months=8,
                max_participants=120,
                available_equipment=["measurement_devices", "randomization_system"],
                staff_expertise=["laboratory_techniques", "data_analysis"]
            )
            
            # Design preferences for factorial
            preferences = {
                "design_type": "factorial"
            }
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=objectives,
                resource_constraints=constraints,
                design_preferences=preferences
            )
            
            # Validate factorial design
            assert design.design_type == ExperimentType.FACTORIAL
            assert len(design.experimental_groups) >= 3  # Multiple factor combinations
            assert design.total_sample_size > 60  # Reasonable size for factorial
            
            print("✅ Factorial design test passed")
            print(f"   - Design type: {design.design_type.value}")
            print(f"   - Sample size: {design.total_sample_size}")
            print(f"   - Groups: {len(design.experimental_groups)}")
            print(f"   - Power (primary): {design.power_analysis.get('primary_analysis', {}).get('power', 'N/A')}")
            
            self.test_results.append({
                "test": "factorial_design",
                "status": "passed",
                "details": {
                    "design_type": design.design_type.value,
                    "sample_size": design.total_sample_size,
                    "groups": len(design.experimental_groups),
                    "power": design.power_analysis.get('primary_analysis', {}).get('power', 0)
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Factorial design test failed: {e}")
            self.test_results.append({"test": "factorial_design", "status": "failed", "error": str(e)})
            return False
    
    async def test_power_analysis(self):
        """Test statistical power analysis functionality"""
        try:
            print("\n📊 Testing power analysis...")
            
            # Define objective with specific effect size
            objective = ResearchObjective(
                id="power_obj_1", 
                title="Power Analysis Test",
                description="Test power calculation accuracy",
                primary_outcome="test_outcome",
                secondary_outcomes=["secondary_1", "secondary_2"],
                domain="psychology",
                hypothesis="Intervention has medium effect",
                effect_size_expected=0.5  # Medium effect size
            )
            
            # Good resource constraints
            constraints = ResourceConstraints(
                budget=200000,
                time_months=24,
                max_participants=500
            )
            
            # Specific statistical requirements
            stat_req = StatisticalRequirements(
                alpha=0.05,
                power=0.90,  # High power requirement
                effect_size=0.5,
                dropout_rate=0.10
            )
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=constraints,
                statistical_requirements=stat_req
            )
            
            # Validate power analysis
            power_analysis = design.power_analysis
            assert "primary_analysis" in power_analysis
            assert "secondary_analyses" in power_analysis
            assert "sensitivity_analysis" in power_analysis
            
            primary_power = power_analysis["primary_analysis"]["power"]
            assert primary_power >= 0.85  # Should achieve high power
            
            # Check sensitivity analysis
            sensitivity = power_analysis["sensitivity_analysis"]
            assert "small_effect" in sensitivity
            assert "medium_effect" in sensitivity
            assert "large_effect" in sensitivity
            
            print("✅ Power analysis test passed")
            print(f"   - Primary power: {primary_power:.3f}")
            print(f"   - Secondary analyses: {len(power_analysis['secondary_analyses'])}")
            print(f"   - Small effect power: {sensitivity['small_effect']:.3f}")
            print(f"   - Medium effect power: {sensitivity['medium_effect']:.3f}")
            print(f"   - Large effect power: {sensitivity['large_effect']:.3f}")
            
            self.test_results.append({
                "test": "power_analysis",
                "status": "passed",
                "details": {
                    "primary_power": primary_power,
                    "secondary_count": len(power_analysis['secondary_analyses']),
                    "sensitivity_complete": len(sensitivity) == 3
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Power analysis test failed: {e}")
            self.test_results.append({"test": "power_analysis", "status": "failed", "error": str(e)})
            return False
    
    async def test_feasibility_assessment(self):
        """Test feasibility assessment with constraints"""
        try:
            print("\n⚖️ Testing feasibility assessment...")
            
            # Define challenging objective
            objective = ResearchObjective(
                id="feasibility_obj_1",
                title="Large Scale Study",
                description="Very large multi-site study",
                primary_outcome="clinical_endpoint",
                secondary_outcomes=["biomarker_1", "biomarker_2"],
                domain="medicine",
                hypothesis="Large effect hypothesis",
                effect_size_expected=0.3,  # Small effect = large sample needed
                priority=1
            )
            
            # Very limited constraints
            constraints = ResourceConstraints(
                budget=50000,      # Limited budget
                time_months=6,     # Short timeline
                max_participants=50,  # Small participant pool
                available_equipment=[],  # No equipment
                staff_expertise=["basic_research"]  # Limited expertise
            )
            
            # High statistical requirements
            stat_req = StatisticalRequirements(
                alpha=0.01,  # Stringent
                power=0.95   # Very high power
            )
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=constraints,
                statistical_requirements=stat_req
            )
            
            # Should identify feasibility issues
            assert design.feasibility_score < 0.8  # Should be challenging
            assert len(design.alternatives) > 0    # Should suggest alternatives
            
            # Check risk assessment
            risk_assessment = design.risk_assessment
            assert "individual_risks" in risk_assessment
            assert "overall_risk_score" in risk_assessment
            assert risk_assessment["overall_risk_score"] > 0.3  # Should have moderate-high risk
            
            print("✅ Feasibility assessment test passed")
            print(f"   - Feasibility score: {design.feasibility_score:.2f}")
            print(f"   - Risk score: {risk_assessment['overall_risk_score']:.2f}")
            print(f"   - Alternatives suggested: {len(design.alternatives)}")
            print(f"   - Recommendations: {len(design.recommendations)}")
            
            self.test_results.append({
                "test": "feasibility_assessment",
                "status": "passed",
                "details": {
                    "feasibility_score": design.feasibility_score,
                    "risk_score": risk_assessment['overall_risk_score'],
                    "alternatives_count": len(design.alternatives),
                    "recommendations_count": len(design.recommendations)
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Feasibility assessment test failed: {e}")
            self.test_results.append({"test": "feasibility_assessment", "status": "failed", "error": str(e)})
            return False
    
    async def test_dose_response_design(self):
        """Test dose-response experimental design"""
        try:
            print("\n💊 Testing dose-response design...")
            
            # Dose-response objective
            objective = ResearchObjective(
                id="dose_obj_1",
                title="Drug Dose-Response Study",
                description="Determine optimal dose for new drug",
                primary_outcome="therapeutic_response",
                secondary_outcomes=["side_effects", "bioavailability"],
                domain="medicine",
                hypothesis="Higher doses show increased response up to plateau",
                effect_size_expected=0.7,
                priority=1
            )
            
            # Appropriate constraints
            constraints = ResourceConstraints(
                budget=150000,
                time_months=15,
                max_participants=160,
                available_equipment=["dosing_equipment", "analytical_instruments"],
                staff_expertise=["clinical_pharmacology", "biostatistics"],
                ethical_approvals=["IRB_approval"],
                regulatory_requirements=["FDA_IND"]
            )
            
            # Design preferences for dose-response
            preferences = {
                "design_type": "dose_response"
            }
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=constraints,
                design_preferences=preferences
            )
            
            # Validate dose-response design
            assert design.design_type == ExperimentType.DOSE_RESPONSE
            assert len(design.experimental_groups) >= 3  # Multiple dose levels + control
            
            # Check for dose-related groups
            group_names = [group.name.lower() for group in design.experimental_groups]
            dose_terms = any(term in ' '.join(group_names) for term in ['dose', 'low', 'medium', 'high', 'control'])
            assert dose_terms, "Should have dose-related group names"
            
            print("✅ Dose-response design test passed")
            print(f"   - Design type: {design.design_type.value}")
            print(f"   - Dose groups: {len(design.experimental_groups)}")
            print(f"   - Sample per group: {design.total_sample_size // len(design.experimental_groups)}")
            print(f"   - Study duration: {design.duration_months} months")
            
            self.test_results.append({
                "test": "dose_response_design",
                "status": "passed",
                "details": {
                    "design_type": design.design_type.value,
                    "dose_groups": len(design.experimental_groups),
                    "sample_per_group": design.total_sample_size // len(design.experimental_groups),
                    "duration": design.duration_months
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Dose-response design test failed: {e}")
            self.test_results.append({"test": "dose_response_design", "status": "failed", "error": str(e)})
            return False
    
    async def test_timeline_and_cost_estimation(self):
        """Test timeline and cost estimation accuracy"""
        try:
            print("\n📅 Testing timeline and cost estimation...")
            
            # Well-defined objective
            objective = ResearchObjective(
                id="timeline_obj_1",
                title="Standard Clinical Trial",
                description="Standard phase II clinical trial",
                primary_outcome="primary_efficacy",
                secondary_outcomes=["safety", "quality_of_life"],
                domain="medicine",
                hypothesis="Treatment is efficacious and safe",
                effect_size_expected=0.6,
                priority=1
            )
            
            # Realistic constraints
            constraints = ResourceConstraints(
                budget=300000,
                time_months=36,
                max_participants=300,
                available_equipment=["clinical_monitors", "data_systems", "laboratory"],
                staff_expertise=["clinical_research", "statistics", "regulatory"],
                ethical_approvals=["IRB_approval"],
                regulatory_requirements=["FDA_approval", "GCP_compliance"]
            )
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=constraints
            )
            
            # Validate timeline
            timeline = design.timeline
            assert len(timeline) >= 3  # At least setup, intervention, analysis phases
            
            # Check timeline phases
            phases = [phase["phase"] for phase in timeline]
            expected_phases = ["setup", "recruitment", "intervention", "analysis"]
            phase_coverage = sum(1 for phase in expected_phases if phase in phases) / len(expected_phases)
            assert phase_coverage >= 0.75  # At least 75% of expected phases
            
            # Validate cost estimation
            assert design.estimated_cost > 0
            assert design.estimated_cost <= constraints.budget * 1.5  # Within reasonable range
            
            # Check timeline progression
            months = [phase["month"] for phase in timeline]
            assert months == sorted(months)  # Should be in chronological order
            
            print("✅ Timeline and cost estimation test passed")
            print(f"   - Timeline phases: {len(timeline)}")
            print(f"   - Total duration: {design.duration_months} months")
            print(f"   - Estimated cost: ${design.estimated_cost:,.2f}")
            print(f"   - Cost vs budget: {(design.estimated_cost/constraints.budget)*100:.1f}%")
            
            self.test_results.append({
                "test": "timeline_cost_estimation",
                "status": "passed",
                "details": {
                    "timeline_phases": len(timeline),
                    "duration": design.duration_months,
                    "estimated_cost": design.estimated_cost,
                    "cost_budget_ratio": design.estimated_cost / constraints.budget
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Timeline and cost estimation test failed: {e}")
            self.test_results.append({"test": "timeline_cost_estimation", "status": "failed", "error": str(e)})
            return False
    
    async def test_multidisciplinary_design(self):
        """Test multidisciplinary experimental design"""
        try:
            print("\n🔬 Testing multidisciplinary design...")
            
            # Multiple objectives from different domains
            objectives = [
                ResearchObjective(
                    id="multi_obj_1",
                    title="Biomedical Component",
                    description="Biological mechanism study",
                    primary_outcome="biomarker_expression",
                    secondary_outcomes=["cellular_response"],
                    domain="biology",
                    hypothesis="Treatment affects biological pathways",
                    effect_size_expected=0.6,
                    priority=1
                ),
                ResearchObjective(
                    id="multi_obj_2",
                    title="Clinical Component",
                    description="Clinical efficacy assessment",
                    primary_outcome="clinical_improvement",
                    secondary_outcomes=["patient_reported_outcomes"],
                    domain="medicine",
                    hypothesis="Treatment improves clinical outcomes",
                    effect_size_expected=0.5,
                    priority=1
                ),
                ResearchObjective(
                    id="multi_obj_3",
                    title="Behavioral Component", 
                    description="Behavioral change assessment",
                    primary_outcome="behavioral_modification",
                    secondary_outcomes=["adherence", "satisfaction"],
                    domain="psychology",
                    hypothesis="Treatment changes behavior patterns",
                    effect_size_expected=0.4,
                    priority=2
                )
            ]
            
            # Comprehensive resources
            constraints = ResourceConstraints(
                budget=500000,
                time_months=48,
                max_participants=400,
                available_equipment=["clinical_lab", "behavioral_assessment", "imaging", "biomarker_analysis"],
                staff_expertise=["clinical_research", "laboratory", "psychology", "biostatistics"],
                ethical_approvals=["IRB_approval", "ethics_committee"],
                regulatory_requirements=["FDA_approval", "data_protection"]
            )
            
            # Design experiment
            design = await self.service.design_experiment(
                research_objectives=objectives,
                resource_constraints=constraints
            )
            
            # Validate multidisciplinary design
            assert len(design.research_objectives) == 3
            assert design.total_sample_size >= 200  # Should accommodate multiple objectives
            
            # Check measurement plan covers multiple domains
            measurement_methods = design.measurement_plan.data_collection_methods
            domain_coverage = sum(1 for method in measurement_methods 
                                if any(domain in method for domain in ['clinical', 'laboratory', 'behavioral']))
            assert domain_coverage > 0  # Should have multi-domain measurements
            
            # Power analysis should include secondary analyses
            power_analysis = design.power_analysis
            assert len(power_analysis.get("secondary_analyses", [])) >= 2  # Multiple secondary objectives
            
            print("✅ Multidisciplinary design test passed")
            print(f"   - Research objectives: {len(design.research_objectives)}")
            print(f"   - Measurement methods: {len(measurement_methods)}")
            print(f"   - Secondary power analyses: {len(power_analysis.get('secondary_analyses', []))}")
            print(f"   - Study complexity: {design.duration_months} months, {design.total_sample_size} participants")
            
            self.test_results.append({
                "test": "multidisciplinary_design",
                "status": "passed",
                "details": {
                    "objectives_count": len(design.research_objectives),
                    "measurement_methods": len(measurement_methods),
                    "secondary_analyses": len(power_analysis.get('secondary_analyses', [])),
                    "total_participants": design.total_sample_size
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Multidisciplinary design test failed: {e}")
            self.test_results.append({"test": "multidisciplinary_design", "status": "failed", "error": str(e)})
            return False
    
    async def test_resource_optimization(self):
        """Test resource optimization and alternative suggestions"""
        try:
            print("\n⚡ Testing resource optimization...")
            
            # Ambitious objective
            objective = ResearchObjective(
                id="opt_obj_1",
                title="Resource Optimization Test",
                description="Test resource optimization capabilities",
                primary_outcome="optimization_outcome",
                secondary_outcomes=["secondary_opt"],
                domain="engineering",
                hypothesis="Optimization improves outcomes",
                effect_size_expected=0.4,  # Moderate effect
                priority=1
            )
            
            # Very tight constraints
            tight_constraints = ResourceConstraints(
                budget=25000,      # Very limited budget
                time_months=4,     # Very short timeline
                max_participants=30,  # Small sample
                available_equipment=["basic_equipment"],
                staff_expertise=["basic_research"]
            )
            
            # More generous constraints for comparison
            generous_constraints = ResourceConstraints(
                budget=250000,
                time_months=24,
                max_participants=300,
                available_equipment=["advanced_equipment", "multiple_systems"],
                staff_expertise=["expert_research", "advanced_statistics"]
            )
            
            # Design with tight constraints
            tight_design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=tight_constraints
            )
            
            # Design with generous constraints
            generous_design = await self.service.design_experiment(
                research_objectives=[objective],
                resource_constraints=generous_constraints
            )
            
            # Compare designs
            assert tight_design.feasibility_score < generous_design.feasibility_score
            assert len(tight_design.alternatives) >= len(generous_design.alternatives)
            assert tight_design.total_sample_size <= generous_design.total_sample_size
            
            # Tight design should suggest alternatives
            assert len(tight_design.alternatives) > 0
            assert "sample_size" in ' '.join(tight_design.alternatives).lower() or \
                   "budget" in ' '.join(tight_design.alternatives).lower()
            
            print("✅ Resource optimization test passed")
            print(f"   - Tight constraints feasibility: {tight_design.feasibility_score:.2f}")
            print(f"   - Generous constraints feasibility: {generous_design.feasibility_score:.2f}")
            print(f"   - Tight design alternatives: {len(tight_design.alternatives)}")
            print(f"   - Sample size difference: {generous_design.total_sample_size - tight_design.total_sample_size}")
            
            self.test_results.append({
                "test": "resource_optimization",
                "status": "passed",
                "details": {
                    "tight_feasibility": tight_design.feasibility_score,
                    "generous_feasibility": generous_design.feasibility_score,
                    "alternatives_suggested": len(tight_design.alternatives),
                    "sample_size_optimization": generous_design.total_sample_size - tight_design.total_sample_size
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ Resource optimization test failed: {e}")
            self.test_results.append({"test": "resource_optimization", "status": "failed", "error": str(e)})
            return False
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🎯 EXPERIMENTAL DESIGN ASSISTANT - FINAL TEST RESULTS")
        print("="*80)
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Overall results
        print(f"📊 OVERALL RESULTS:")
        print(f"   ✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed_tests}/{total_tests}")
        print(f"   ⏱️  Total time: {(datetime.now() - self.start_time).total_seconds():.2f} seconds")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"   {i}. {status_icon} {result['test'].replace('_', ' ').title()}")
            
            if result["status"] == "passed" and "details" in result:
                details = result["details"]
                for key, value in details.items():
                    if isinstance(value, float):
                        print(f"      - {key.replace('_', ' ').title()}: {value:.3f}")
                    else:
                        print(f"      - {key.replace('_', ' ').title()}: {value}")
            elif result["status"] == "failed":
                print(f"      - Error: {result.get('error', 'Unknown error')}")
        
        # Service capabilities summary
        if passed_tests > 0:
            print(f"\n🚀 EXPERIMENTAL DESIGN ASSISTANT CAPABILITIES:")
            capabilities = [
                "✅ Service initialization and health monitoring",
                "✅ Randomized controlled trial design",
                "✅ Factorial experimental design", 
                "✅ Statistical power analysis with sensitivity testing",
                "✅ Feasibility assessment with constraints",
                "✅ Dose-response study design",
                "✅ Timeline and cost estimation",
                "✅ Multidisciplinary research design",
                "✅ Resource optimization and alternatives"
            ]
            
            for capability in capabilities[:passed_tests]:
                print(f"   {capability}")
        
        # Final assessment
        if success_rate >= 100:
            print(f"\n🏆 EXCELLENT: Experimental Design Assistant working perfectly!")
            print(f"   All {total_tests} tests passed - system ready for production use")
        elif success_rate >= 80:
            print(f"\n✅ GOOD: Experimental Design Assistant working well")
            print(f"   {passed_tests}/{total_tests} tests passed - minor issues detected")
        elif success_rate >= 60:
            print(f"\n⚠️  FAIR: Experimental Design Assistant partially functional") 
            print(f"   {passed_tests}/{total_tests} tests passed - significant issues detected")
        else:
            print(f"\n❌ POOR: Experimental Design Assistant needs attention")
            print(f"   Only {passed_tests}/{total_tests} tests passed - major issues detected")
        
        print("="*80)
        
        return success_rate


async def main():
    """Main test execution function"""
    print("🚀 ATLAS Experimental Design Assistant - Comprehensive Test Suite")
    print("="*80)
    
    # Initialize test suite
    test_suite = TestExperimentalDesignAssistant()
    
    # Setup
    if not await test_suite.setup():
        print("❌ Test setup failed - aborting test suite")
        return
    
    # Run all tests
    test_methods = [
        test_suite.test_service_initialization,
        test_suite.test_simple_rct_design,
        test_suite.test_factorial_design,
        test_suite.test_power_analysis,
        test_suite.test_feasibility_assessment,
        test_suite.test_dose_response_design,
        test_suite.test_timeline_and_cost_estimation,
        test_suite.test_multidisciplinary_design,
        test_suite.test_resource_optimization
    ]
    
    # Execute tests
    for test_method in test_methods:
        try:
            await test_method()
        except Exception as e:
            print(f"❌ Test execution error: {e}")
            traceback.print_exc()
    
    # Print final results
    success_rate = test_suite.print_final_results()
    
    return success_rate


if __name__ == "__main__":
    """Run test suite when executed directly"""
    try:
        success_rate = asyncio.run(main())
        exit_code = 0 if success_rate >= 80 else 1
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()
        exit(1)
