"""
Experimental Design Assistant Service for ATLAS Autonomous Laboratory

This service suggests optimal experimental designs based on research objectives,
available resources, statistical requirements, and domain-specific constraints.

Author: ATLAS Autonomous Laboratory System
Date: September 11, 2025
"""

import hashlib
import logging
import math
import numpy as np
from datetime import datetime, timezone as tz
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from app.exceptions.domain.biology import BiologyError
from app.types.experimental_design_service_types import (
    GetDesignHealthStatusResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UTC = tz.utc

class ExperimentType(Enum):
    """Types of experimental designs"""
    RANDOMIZED_CONTROLLED = "randomized_controlled"
    FACTORIAL = "factorial"
    REPEATED_MEASURES = "repeated_measures"
    CROSSOVER = "crossover"
    DOSE_RESPONSE = "dose_response"
    TIME_SERIES = "time_series"
    CASE_CONTROL = "case_control"
    COHORT = "cohort"
    OBSERVATIONAL = "observational"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    MIXED_METHODS = "mixed_methods"

class StudyPhase(Enum):
    """Phases of experimental studies"""
    PILOT = "pilot"
    PHASE_I = "phase_i"
    PHASE_II = "phase_ii"  
    PHASE_III = "phase_iii"
    PHASE_IV = "phase_iv"
    EXPLORATORY = "exploratory"
    CONFIRMATORY = "confirmatory"
    VALIDATION = "validation"

class ResourceConstraint(Enum):
    """Types of resource constraints"""
    BUDGET = "budget"
    TIME = "time"
    PARTICIPANTS = "participants"
    EQUIPMENT = "equipment"
    EXPERTISE = "expertise"
    ETHICAL = "ethical"
    REGULATORY = "regulatory"

class PowerAnalysisMethod(Enum):
    """Methods for statistical power analysis"""
    T_TEST = "t_test"
    ANOVA = "anova"
    CHI_SQUARE = "chi_square"
    REGRESSION = "regression"
    SURVIVAL_ANALYSIS = "survival_analysis"
    NON_PARAMETRIC = "non_parametric"

@dataclass
class ResearchObjective:
    """Definition of research objective"""
    id: str
    title: str
    description: str
    primary_outcome: str
    secondary_outcomes: List[str]
    domain: str
    hypothesis: str
    effect_size_expected: float
    clinical_significance: Optional[float] = None
    priority: int = 1  # 1 = highest, 5 = lowest

@dataclass
class ResourceConstraints:
    """Available resources and constraints"""
    budget: Optional[float] = None
    time_months: Optional[int] = None
    max_participants: Optional[int] = None
    available_equipment: Optional[List[str]] = None
    staff_expertise: Optional[List[str]] = None
    ethical_approvals: Optional[List[str]] = None
    regulatory_requirements: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.available_equipment is None:
            self.available_equipment = []
        if self.staff_expertise is None:
            self.staff_expertise = []
        if self.ethical_approvals is None:
            self.ethical_approvals = []
        if self.regulatory_requirements is None:
            self.regulatory_requirements = []

@dataclass
class StatisticalRequirements:
    """Statistical requirements for the study"""
    alpha: float = 0.05
    power: float = 0.80
    beta: float = 0.20
    effect_size: Optional[float] = None
    variance_estimate: Optional[float] = None
    correlation_expected: Optional[float] = None
    dropout_rate: float = 0.15
    interim_analyses: int = 0
    multiple_comparisons: bool = False

@dataclass
class ExperimentalGroup:
    """Definition of an experimental group"""
    id: str
    name: str
    intervention: str
    sample_size: int
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    measurement_schedule: List[str]
    special_requirements: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.special_requirements is None:
            self.special_requirements = []

@dataclass
class MeasurementPlan:
    """Plan for data collection and measurements"""
    primary_endpoint: str
    secondary_endpoints: List[str]
    measurement_frequency: str
    data_collection_methods: List[str]
    quality_control_measures: List[str]
    data_management_plan: str
    statistical_analysis_plan: str

@dataclass
class ExperimentalDesign:
    """Complete experimental design specification"""
    id: str
    title: str
    design_type: ExperimentType
    study_phase: StudyPhase
    research_objectives: List[ResearchObjective]
    experimental_groups: List[ExperimentalGroup]
    measurement_plan: MeasurementPlan
    statistical_requirements: StatisticalRequirements
    total_sample_size: int
    duration_months: int
    estimated_cost: float
    feasibility_score: float
    power_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    recommendations: List[str]
    alternatives: List[str]
    created_at: datetime

class ExperimentalDesignAssistantService:
    """
    Advanced service for designing optimal scientific experiments
    """
    
    def __init__(self):
        """Initialize the experimental design service"""
        self.design_templates = self._initialize_design_templates()
        self.domain_expertise = self._initialize_domain_expertise()
        self.power_calculators = self._initialize_power_calculators()
        self.cost_models = self._initialize_cost_models()
        logger.info("✅ ExperimentalDesignAssistantService initialized")
    
    def _initialize_design_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize experimental design templates"""
        return {
            "clinical_trial": {
                "phases": ["pilot", "phase_i", "phase_ii", "phase_iii"],
                "typical_duration": {"pilot": 3, "phase_i": 12, "phase_ii": 18, "phase_iii": 36},
                "sample_sizes": {"pilot": 20, "phase_i": 50, "phase_ii": 200, "phase_iii": 1000},
                "primary_endpoints": ["safety", "efficacy", "dosing", "comparative_effectiveness"],
                "regulatory_requirements": ["FDA_IND", "IRB_approval", "informed_consent"]
            },
            "basic_research": {
                "types": ["factorial", "repeated_measures", "dose_response"],
                "typical_duration": 6,
                "sample_sizes": {"small": 30, "medium": 100, "large": 300},
                "replication_factor": 3,
                "controls": ["negative", "positive", "vehicle"]
            },
            "observational_study": {
                "types": ["cohort", "case_control", "cross_sectional"],
                "typical_duration": {"short": 6, "medium": 24, "long": 60},
                "sample_sizes": {"small": 100, "medium": 500, "large": 2000},
                "follow_up_periods": [6, 12, 24, 60]
            }
        }
    
    def _initialize_domain_expertise(self) -> Dict[str, Dict[str, Any]]:
        """Initialize domain-specific design knowledge"""
        return {
            "medicine": {
                "common_designs": ["randomized_controlled", "crossover", "dose_response"],
                "ethical_considerations": ["patient_safety", "informed_consent", "equipoise"],
                "regulatory_bodies": ["FDA", "EMA", "ICH"],
                "typical_effect_sizes": {"small": 0.2, "medium": 0.5, "large": 0.8},
                "dropout_rates": {"low": 0.05, "medium": 0.15, "high": 0.30}
            },
            "psychology": {
                "common_designs": ["repeated_measures", "factorial", "quasi_experimental"],
                "effect_sizes": {"small": 0.1, "medium": 0.25, "large": 0.4},
                "sample_size_multiplier": 1.2,
                "control_conditions": ["placebo", "wait_list", "treatment_as_usual"]
            },
            "biology": {
                "common_designs": ["factorial", "dose_response", "time_series"],
                "replication_requirements": 3,
                "controls": ["negative", "positive", "vehicle", "sham"],
                "typical_variance": 0.15
            },
            "engineering": {
                "common_designs": ["factorial", "response_surface", "robust_design"],
                "optimization_focus": True,
                "measurement_precision": 0.01,
                "environmental_factors": ["temperature", "humidity", "vibration"]
            }
        }
    
    def _initialize_power_calculators(self) -> Dict[PowerAnalysisMethod, Any]:
        """Initialize statistical power calculation methods"""
        return {
            PowerAnalysisMethod.T_TEST: self._calculate_ttest_power,
            PowerAnalysisMethod.ANOVA: self._calculate_anova_power,
            PowerAnalysisMethod.CHI_SQUARE: self._calculate_chi_square_power,
            PowerAnalysisMethod.REGRESSION: self._calculate_regression_power
        }
    
    def _initialize_cost_models(self) -> Dict[str, Dict[str, float]]:
        """Initialize cost estimation models"""
        return {
            "personnel": {
                "principal_investigator": 150.0,  # per hour
                "research_coordinator": 35.0,
                "research_assistant": 25.0,
                "statistician": 100.0,
                "data_manager": 45.0
            },
            "participants": {
                "recruitment_cost": 50.0,  # per participant
                "compensation": 25.0,      # per visit
                "screening_cost": 75.0    # per participant
            },
            "equipment": {
                "basic_lab": 1000.0,      # per month
                "specialized_equipment": 5000.0,
                "imaging": 500.0,         # per scan
                "laboratory_tests": 100.0 # per test
            },
            "overhead": {
                "institutional": 0.30,    # 30% overhead
                "regulatory": 0.05,       # 5% for regulatory compliance
                "contingency": 0.15       # 15% contingency
            }
        }
    
    async def design_experiment(
        self,
        research_objectives: List[ResearchObjective],
        resource_constraints: ResourceConstraints,
        statistical_requirements: Optional[StatisticalRequirements] = None,
        design_preferences: Optional[Dict[str, Any]] = None
    ) -> ExperimentalDesign:
        """
        Design optimal experiment based on objectives and constraints
        
        Args:
            research_objectives: Research questions and hypotheses
            resource_constraints: Available resources and limitations
            statistical_requirements: Statistical power and significance requirements
            design_preferences: Optional preferences for design characteristics
            
        Returns:
            ExperimentalDesign with complete experimental plan
        """
        try:
            # Generate design ID
            design_id = hashlib.sha256(
                f"{len(research_objectives)}_{datetime.now(UTC).isoformat()}".encode()
            ).hexdigest()[:12]
            
            logger.info(f"🧪 Designing experiment: {design_id}")
            
            # Initialize defaults
            if statistical_requirements is None:
                statistical_requirements = StatisticalRequirements()
            
            design_preferences = design_preferences or {}
            
            # Step 1: Analyze objectives and determine optimal design type
            design_type, study_phase = await self._determine_design_type(
                research_objectives, design_preferences
            )
            
            # Step 2: Calculate required sample size
            sample_size_analysis = await self._calculate_sample_size(
                research_objectives, statistical_requirements, design_type
            )
            
            # Step 3: Check feasibility against constraints
            feasibility_assessment = await self._assess_feasibility(
                sample_size_analysis, resource_constraints, design_type
            )
            
            # Step 4: Design experimental groups
            experimental_groups = await self._design_experimental_groups(
                research_objectives, design_type, sample_size_analysis
            )
            
            # Step 5: Create measurement plan
            measurement_plan = await self._create_measurement_plan(
                research_objectives, design_type, resource_constraints
            )
            
            # Step 6: Estimate timeline and costs
            timeline = await self._create_timeline(
                design_type, experimental_groups, measurement_plan
            )
            
            cost_estimate = await self._estimate_costs(
                experimental_groups, measurement_plan, timeline, resource_constraints
            )
            
            # Step 7: Conduct power analysis
            power_analysis = await self._conduct_power_analysis(
                research_objectives, experimental_groups, statistical_requirements
            )
            
            # Step 8: Risk assessment
            risk_assessment = await self._assess_risks(
                design_type, experimental_groups, resource_constraints
            )
            
            # Step 9: Generate recommendations
            recommendations = await self._generate_recommendations(
                feasibility_assessment, power_analysis, risk_assessment
            )
            
            # Step 10: Suggest alternatives
            alternatives = await self._suggest_alternatives(
                research_objectives, resource_constraints, feasibility_assessment
            )
            
            # Create final design
            design = ExperimentalDesign(
                id=design_id,
                title=f"Experimental Design: {research_objectives[0].title}",
                design_type=design_type,
                study_phase=study_phase,
                research_objectives=research_objectives,
                experimental_groups=experimental_groups,
                measurement_plan=measurement_plan,
                statistical_requirements=statistical_requirements,
                total_sample_size=sample_size_analysis["total_sample_size"],
                duration_months=timeline[-1]["month"] if timeline else 12,
                estimated_cost=cost_estimate["summary"]["total_cost"],
                feasibility_score=feasibility_assessment["overall_score"],
                power_analysis=power_analysis,
                risk_assessment=risk_assessment,
                timeline=timeline,
                recommendations=recommendations,
                alternatives=alternatives,
                created_at=datetime.now(UTC)
            )
            
            logger.info(f"✅ Experimental design completed: {design_id}")
            return design
            
        except BiologyError as e:
            logger.error(f"Failed to design experiment: {e}")
            raise
    
    async def _determine_design_type(
        self,
        objectives: List[ResearchObjective],
        preferences: Dict[str, Any]
    ) -> Tuple[ExperimentType, StudyPhase]:
        """Determine optimal experimental design type"""
        
        # Extract domain information
        domains = set(obj.domain for obj in objectives)
        primary_domain = list(domains)[0] if len(domains) == 1 else "multidisciplinary"
        
        # Get domain expertise
        domain_info = self.domain_expertise.get(primary_domain, self.domain_expertise["biology"])
        
        # Consider user preferences
        preferred_type = preferences.get("design_type")
        if preferred_type:
            design_type = ExperimentType(preferred_type)
        else:
            # Select based on objectives and domain
            common_designs = domain_info["common_designs"]
            design_type = ExperimentType(common_designs[0])  # Default to first common design
        
        # Determine study phase
        if any("safety" in obj.primary_outcome.lower() for obj in objectives):
            study_phase = StudyPhase.PHASE_I
        elif any("efficacy" in obj.primary_outcome.lower() for obj in objectives):
            study_phase = StudyPhase.PHASE_II
        elif any("comparative" in obj.primary_outcome.lower() for obj in objectives):
            study_phase = StudyPhase.PHASE_III
        else:
            study_phase = StudyPhase.EXPLORATORY
        
        return design_type, study_phase
    
    async def _calculate_sample_size(
        self,
        objectives: List[ResearchObjective],
        stat_requirements: StatisticalRequirements,
        design_type: ExperimentType
    ) -> Dict[str, Any]:
        """Calculate required sample size based on power analysis"""
        
        # Use primary objective for sample size calculation
        primary_objective = objectives[0]
        
        # Get effect size
        effect_size = primary_objective.effect_size_expected or stat_requirements.effect_size or 0.5
        
        # Calculate sample size per group
        if design_type == ExperimentType.FACTORIAL:
            # Factorial design - more complex calculation
            n_per_group = self._calculate_factorial_sample_size(
                effect_size, stat_requirements.alpha, stat_requirements.power
            )
            total_groups = 2 ** len([obj for obj in objectives if obj.priority <= 2])  # Main factors
        else:
            # Simple two-group comparison
            n_per_group = self._calculate_two_group_sample_size(
                effect_size, stat_requirements.alpha, stat_requirements.power
            )
            total_groups = 2
        
        # Adjust for dropout
        n_per_group_adjusted = math.ceil(n_per_group / (1 - stat_requirements.dropout_rate))
        
        total_sample_size = n_per_group_adjusted * total_groups
        
        return {
            "n_per_group": n_per_group,
            "n_per_group_adjusted": n_per_group_adjusted,
            "total_groups": total_groups,
            "total_sample_size": total_sample_size,
            "effect_size_used": effect_size,
            "dropout_adjustment": stat_requirements.dropout_rate
        }
    
    def _calculate_two_group_sample_size(self, effect_size: float, alpha: float, power: float) -> int:
        """Calculate sample size for two-group comparison"""
        # Simplified power calculation (Cohen's formula approximation)
        z_alpha = self._get_z_score(1 - alpha/2)
        z_beta = self._get_z_score(power)
        
        n = ((z_alpha + z_beta) ** 2) * 2 / (effect_size ** 2)
        return math.ceil(n)
    
    def _calculate_factorial_sample_size(self, effect_size: float, alpha: float, power: float) -> int:
        """Calculate sample size for factorial design"""
        # More conservative calculation for factorial designs
        base_n = self._calculate_two_group_sample_size(effect_size, alpha, power)
        # Increase for multiple comparisons
        return math.ceil(base_n * 1.3)
    
    def _get_z_score(self, p: float) -> float:
        """Get z-score for given probability"""
        # Simplified z-score approximation
        z_scores = {
            0.95: 1.96, 0.90: 1.645, 0.80: 0.845, 0.975: 1.96, 0.99: 2.576
        }
        return z_scores.get(p, 1.96)  # Default to 1.96 (95% confidence)
    
    async def _assess_feasibility(
        self,
        sample_size_analysis: Dict[str, Any],
        constraints: ResourceConstraints,
        design_type: ExperimentType
    ) -> Dict[str, Any]:
        """Assess feasibility of proposed design against constraints"""
        
        feasibility_scores = {}
        
        # Sample size feasibility
        if constraints.max_participants:
            sample_feasibility = min(1.0, constraints.max_participants / sample_size_analysis["total_sample_size"])
        else:
            sample_feasibility = 1.0
        feasibility_scores["sample_size"] = sample_feasibility
        
        # Budget feasibility (rough estimate)
        estimated_cost = self._rough_cost_estimate(sample_size_analysis["total_sample_size"])
        if constraints.budget:
            budget_feasibility = min(1.0, constraints.budget / estimated_cost)
        else:
            budget_feasibility = 1.0
        feasibility_scores["budget"] = budget_feasibility
        
        # Time feasibility
        estimated_duration = self._estimate_duration(design_type, sample_size_analysis["total_sample_size"])
        if constraints.time_months:
            time_feasibility = min(1.0, constraints.time_months / estimated_duration)
        else:
            time_feasibility = 1.0
        feasibility_scores["time"] = time_feasibility
        
        # Equipment feasibility
        required_equipment = self._get_required_equipment(design_type)
        available_equipment = set(constraints.available_equipment or [])
        if required_equipment:
            equipment_coverage = len(required_equipment.intersection(available_equipment)) / len(required_equipment)
        else:
            equipment_coverage = 1.0
        feasibility_scores["equipment"] = equipment_coverage
        
        # Overall feasibility
        overall_score = np.mean(list(feasibility_scores.values()))
        
        return {
            "individual_scores": feasibility_scores,
            "overall_score": overall_score,
            "limiting_factors": [
                factor for factor, score in feasibility_scores.items() 
                if score < 0.8
            ],
            "estimated_cost": estimated_cost,
            "estimated_duration": estimated_duration
        }
    
    def _rough_cost_estimate(self, sample_size: int) -> float:
        """Rough cost estimation"""
        cost_per_participant = 500  # Base cost per participant
        fixed_costs = 10000  # Fixed study costs
        return sample_size * cost_per_participant + fixed_costs
    
    def _estimate_duration(self, design_type: ExperimentType, sample_size: int) -> int:
        """Estimate study duration in months"""
        base_duration = {
            ExperimentType.RANDOMIZED_CONTROLLED: 12,
            ExperimentType.FACTORIAL: 8,
            ExperimentType.REPEATED_MEASURES: 6,
            ExperimentType.DOSE_RESPONSE: 9,
            ExperimentType.OBSERVATIONAL: 18
        }
        
        duration = base_duration.get(design_type, 12)
        
        # Adjust for large sample sizes
        if sample_size > 500:
            duration += 6
        elif sample_size > 200:
            duration += 3
        
        return duration
    
    def _get_required_equipment(self, design_type: ExperimentType) -> Set[str]:
        """Get required equipment for design type"""
        equipment_map = {
            ExperimentType.RANDOMIZED_CONTROLLED: {"clinical_monitors", "data_capture_system"},
            ExperimentType.FACTORIAL: {"measurement_devices", "randomization_system"},
            ExperimentType.DOSE_RESPONSE: {"dosing_equipment", "analytical_instruments"}
        }
        
        return equipment_map.get(design_type, set())
    
    async def _design_experimental_groups(
        self,
        objectives: List[ResearchObjective],
        design_type: ExperimentType,
        sample_analysis: Dict[str, Any]
    ) -> List[ExperimentalGroup]:
        """Design experimental groups based on objectives and design type"""
        
        groups = []
        n_per_group = sample_analysis["n_per_group_adjusted"]
        
        if design_type == ExperimentType.RANDOMIZED_CONTROLLED:
            # Treatment and control groups
            groups.append(ExperimentalGroup(
                id="treatment",
                name="Treatment Group",
                intervention=objectives[0].title,
                sample_size=n_per_group,
                inclusion_criteria=["meets_eligibility", "informed_consent"],
                exclusion_criteria=["contraindications", "prior_treatment"],
                measurement_schedule=["baseline", "week_4", "week_8", "week_12"]
            ))
            
            groups.append(ExperimentalGroup(
                id="control",
                name="Control Group",
                intervention="placebo_or_standard_care",
                sample_size=n_per_group,
                inclusion_criteria=["meets_eligibility", "informed_consent"],
                exclusion_criteria=["contraindications", "prior_treatment"],
                measurement_schedule=["baseline", "week_4", "week_8", "week_12"]
            ))
        
        elif design_type == ExperimentType.FACTORIAL:
            # Multiple factor combinations
            factors = [obj for obj in objectives if obj.priority <= 2]
            for i, combination in enumerate(self._generate_factorial_combinations(factors)):
                groups.append(ExperimentalGroup(
                    id=f"group_{i+1}",
                    name=f"Group {i+1}: {combination}",
                    intervention=combination,
                    sample_size=n_per_group,
                    inclusion_criteria=["meets_eligibility"],
                    exclusion_criteria=["contraindications"],
                    measurement_schedule=["baseline", "post_treatment"]
                ))
        
        elif design_type == ExperimentType.DOSE_RESPONSE:
            # Multiple dose levels
            doses = ["low_dose", "medium_dose", "high_dose", "control"]
            for dose in doses:
                groups.append(ExperimentalGroup(
                    id=dose,
                    name=f"{dose.replace('_', ' ').title()}",
                    intervention=dose,
                    sample_size=n_per_group,
                    inclusion_criteria=["dose_tolerance"],
                    exclusion_criteria=["dose_contraindications"],
                    measurement_schedule=["baseline", "dose_response_curve"]
                ))
        
        else:
            # Default: simple comparison
            groups.append(ExperimentalGroup(
                id="experimental",
                name="Experimental Group",
                intervention=objectives[0].title,
                sample_size=n_per_group,
                inclusion_criteria=["eligibility_criteria"],
                exclusion_criteria=["exclusion_criteria"],
                measurement_schedule=["pre", "post"]
            ))
        
        return groups
    
    def _generate_factorial_combinations(self, factors: List[ResearchObjective]) -> List[str]:
        """Generate all factorial combinations"""
        combinations = ["control"]  # Always include control
        
        for factor in factors[:2]:  # Limit to 2 factors for simplicity
            new_combinations = []
            for combo in combinations:
                new_combinations.extend([combo, f"{combo}_{factor.title}"])
            combinations = new_combinations
        
        return combinations[:4]  # Limit to 4 groups
    
    async def _create_measurement_plan(
        self,
        objectives: List[ResearchObjective],
        design_type: ExperimentType,
        constraints: ResourceConstraints
    ) -> MeasurementPlan:
        """Create comprehensive measurement plan"""
        
        primary_objective = objectives[0]
        
        # Determine measurement frequency
        if design_type in [ExperimentType.TIME_SERIES, ExperimentType.REPEATED_MEASURES]:
            frequency = "multiple_timepoints"
        else:
            frequency = "pre_post"
        
        # Data collection methods based on domain
        methods = ["standardized_instruments", "objective_measures"]
        if "biology" in primary_objective.domain:
            methods.extend(["laboratory_assays", "biomarkers"])
        if "psychology" in primary_objective.domain:
            methods.extend(["questionnaires", "behavioral_observation"])
        
        return MeasurementPlan(
            primary_endpoint=primary_objective.primary_outcome,
            secondary_endpoints=[obj.primary_outcome for obj in objectives[1:]],
            measurement_frequency=frequency,
            data_collection_methods=methods,
            quality_control_measures=[
                "double_data_entry",
                "range_checks", 
                "missing_data_procedures"
            ],
            data_management_plan="secure_database_with_backup",
            statistical_analysis_plan="intention_to_treat_and_per_protocol"
        )
    
    async def _create_timeline(
        self,
        design_type: ExperimentType,
        groups: List[ExperimentalGroup],
        measurement_plan: MeasurementPlan
    ) -> List[Dict[str, Any]]:
        """Create detailed project timeline"""
        
        timeline = []
        current_month = 1
        
        # Setup phase
        timeline.append({
            "month": current_month,
            "phase": "setup",
            "activities": ["protocol_finalization", "regulatory_approvals", "staff_training"],
            "deliverables": ["approved_protocol", "trained_staff"]
        })
        current_month += 2
        
        # Recruitment phase
        recruitment_duration = max(2, len(groups) * len(groups[0].inclusion_criteria))
        timeline.append({
            "month": current_month,
            "phase": "recruitment",
            "activities": ["participant_recruitment", "screening", "enrollment"],
            "deliverables": [f"enrolled_{sum(g.sample_size for g in groups)}_participants"]
        })
        current_month += recruitment_duration
        
        # Intervention phase
        if design_type == ExperimentType.REPEATED_MEASURES:
            intervention_duration = 6
        else:
            intervention_duration = 3
        
        timeline.append({
            "month": current_month,
            "phase": "intervention",
            "activities": ["treatment_delivery", "data_collection", "safety_monitoring"],
            "deliverables": ["intervention_completed", "primary_data_collected"]
        })
        current_month += intervention_duration
        
        # Analysis phase
        timeline.append({
            "month": current_month,
            "phase": "analysis",
            "activities": ["data_analysis", "report_writing", "manuscript_preparation"],
            "deliverables": ["final_report", "publication_manuscript"]
        })
        current_month += 3
        
        return timeline
    
    async def _estimate_costs(
        self,
        groups: List[ExperimentalGroup],
        measurement_plan: MeasurementPlan,
        timeline: List[Dict[str, Any]],
        constraints: ResourceConstraints
    ) -> Dict[str, Any]:
        """Estimate detailed project costs"""
        
        costs = {}
        
        # Personnel costs
        total_months = timeline[-1]["month"] if timeline else 12
        costs["personnel"] = {
            "principal_investigator": self.cost_models["personnel"]["principal_investigator"] * 40 * total_months,
            "research_coordinator": self.cost_models["personnel"]["research_coordinator"] * 160 * total_months,
            "statistician": self.cost_models["personnel"]["statistician"] * 20 * total_months
        }
        
        # Participant costs
        total_participants = sum(group.sample_size for group in groups)
        costs["participants"] = {
            "recruitment": self.cost_models["participants"]["recruitment_cost"] * total_participants,
            "compensation": self.cost_models["participants"]["compensation"] * total_participants * 4,  # 4 visits avg
            "screening": self.cost_models["participants"]["screening_cost"] * total_participants
        }
        
        # Equipment and supplies
        costs["equipment"] = {
            "basic_supplies": 1000 * total_months,
            "specialized_equipment": 5000 if len(measurement_plan.data_collection_methods) > 2 else 2000
        }
        
        # Calculate totals
        personnel_total = sum(costs["personnel"].values())
        participants_total = sum(costs["participants"].values())
        equipment_total = sum(costs["equipment"].values())
        
        direct_total = personnel_total + participants_total + equipment_total
        
        # Overhead and indirect costs
        overhead = direct_total * self.cost_models["overhead"]["institutional"]
        contingency = direct_total * self.cost_models["overhead"]["contingency"]
        
        total_cost = direct_total + overhead + contingency
        
        costs["summary"] = {
            "direct_costs": direct_total,
            "overhead": overhead,
            "contingency": contingency,
            "total_cost": total_cost
        }
        
        return costs
    
    async def _conduct_power_analysis(
        self,
        objectives: List[ResearchObjective],
        groups: List[ExperimentalGroup],
        stat_requirements: StatisticalRequirements
    ) -> Dict[str, Any]:
        """Conduct comprehensive statistical power analysis"""
        
        primary_objective = objectives[0]
        effect_size = primary_objective.effect_size_expected or 0.5
        n_per_group = groups[0].sample_size if groups else 50
        
        # Primary analysis power
        primary_power = self._calculate_power(
            effect_size, stat_requirements.alpha, n_per_group, len(groups)
        )
        
        # Secondary analyses power
        secondary_powers = []
        for obj in objectives[1:3]:  # Limit to first 2 secondary objectives
            sec_effect = obj.effect_size_expected or effect_size * 0.7  # Smaller effect
            sec_power = self._calculate_power(sec_effect, stat_requirements.alpha, n_per_group, len(groups))
            secondary_powers.append({
                "objective": obj.title,
                "power": sec_power,
                "effect_size": sec_effect
            })
        
        # Sensitivity analysis
        sensitivity = {
            "small_effect": self._calculate_power(0.2, stat_requirements.alpha, n_per_group, len(groups)),
            "medium_effect": self._calculate_power(0.5, stat_requirements.alpha, n_per_group, len(groups)),
            "large_effect": self._calculate_power(0.8, stat_requirements.alpha, n_per_group, len(groups))
        }
        
        return {
            "primary_analysis": {
                "power": primary_power,
                "effect_size": effect_size,
                "sample_size_per_group": n_per_group,
                "alpha": stat_requirements.alpha
            },
            "secondary_analyses": secondary_powers,
            "sensitivity_analysis": sensitivity,
            "recommendations": self._power_recommendations(primary_power, sensitivity)
        }
    
    def _calculate_power(self, effect_size: float, alpha: float, n_per_group: int, n_groups: int) -> float:
        """Calculate statistical power for given parameters"""
        # Simplified power calculation
        # In practice, this would use proper statistical libraries
        
        z_alpha = self._get_z_score(1 - alpha/2)
        z_effect = effect_size * math.sqrt(n_per_group / (2 * n_groups))
        
        power = 1 - self._normal_cdf(z_alpha - z_effect)
        return max(0.0, min(1.0, power))
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal cumulative distribution function"""
        # Simple approximation
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _power_recommendations(self, primary_power: float, sensitivity: Dict[str, float]) -> List[str]:
        """Generate power analysis recommendations"""
        recommendations = []
        
        if primary_power < 0.8:
            recommendations.append(f"Primary power ({primary_power:.2f}) is below 0.8. Consider increasing sample size.")
        
        if sensitivity["small_effect"] < 0.5:
            recommendations.append("Study may not detect small effect sizes. Consider if this is acceptable.")
        
        if primary_power > 0.95:
            recommendations.append("Study is overpowered. Consider reducing sample size to save resources.")
        
        return recommendations
    
    async def _assess_risks(
        self,
        design_type: ExperimentType,
        groups: List[ExperimentalGroup],
        constraints: ResourceConstraints
    ) -> Dict[str, Any]:
        """Assess project risks and mitigation strategies"""
        
        risks = {
            "recruitment": {
                "risk_level": "medium",
                "description": "Difficulty recruiting sufficient participants",
                "probability": 0.3,
                "impact": "high",
                "mitigation": ["broaden_inclusion_criteria", "multiple_sites", "recruitment_incentives"]
            },
            "retention": {
                "risk_level": "medium",
                "description": "Participant dropout higher than expected",
                "probability": 0.4,
                "impact": "medium",
                "mitigation": ["retention_strategies", "interim_analysis", "over_recruitment"]
            },
            "budget": {
                "risk_level": "low" if constraints.budget and constraints.budget > 50000 else "high",
                "description": "Cost overruns",
                "probability": 0.2,
                "impact": "high",
                "mitigation": ["detailed_budgeting", "contingency_funds", "cost_monitoring"]
            },
            "timeline": {
                "risk_level": "medium",
                "description": "Delays in study milestones",
                "probability": 0.5,
                "impact": "medium",
                "mitigation": ["realistic_timeline", "milestone_monitoring", "contingency_time"]
            }
        }
        
        # Calculate overall risk score
        risk_scores = [0.2 if r["risk_level"] == "low" else 0.5 if r["risk_level"] == "medium" else 0.8 
                      for r in risks.values()]
        overall_risk = np.mean(risk_scores)
        
        return {
            "individual_risks": risks,
            "overall_risk_score": overall_risk,
            "high_priority_risks": [
                name for name, risk in risks.items() 
                if risk["risk_level"] == "high"
            ],
            "risk_mitigation_plan": self._create_risk_mitigation_plan(risks)
        }
    
    def _create_risk_mitigation_plan(self, risks: Dict[str, Any]) -> List[str]:
        """Create comprehensive risk mitigation plan"""
        plan = []
        
        for risk_name, risk_info in risks.items():
            if risk_info["risk_level"] in ["medium", "high"]:
                plan.extend([
                    f"{risk_name.title()}: {strategy}" 
                    for strategy in risk_info["mitigation"]
                ])
        
        return plan
    
    async def _generate_recommendations(
        self,
        feasibility: Dict[str, Any],
        power_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive design recommendations"""
        
        recommendations = []
        
        # Feasibility recommendations
        if feasibility["overall_score"] < 0.8:
            limiting_factors = feasibility["limiting_factors"]
            recommendations.append(f"Address limiting factors: {', '.join(limiting_factors)}")
        
        if "sample_size" in feasibility["limiting_factors"]:
            recommendations.append("Consider multi-site collaboration to increase recruitment capacity")
        
        if "budget" in feasibility["limiting_factors"]:
            recommendations.append("Explore additional funding sources or reduce study scope")
        
        # Power analysis recommendations
        recommendations.extend(power_analysis["recommendations"])
        
        # Risk-based recommendations
        if risk_assessment["overall_risk_score"] > 0.6:
            recommendations.append("Implement comprehensive risk mitigation strategies")
        
        # General best practices
        recommendations.extend([
            "Conduct pilot study to validate procedures",
            "Establish data safety monitoring board",
            "Plan for interim analyses and futility stopping",
            "Ensure adequate staff training and certification"
        ])
        
        return recommendations[:10]  # Limit to top 10
    
    async def _suggest_alternatives(
        self,
        objectives: List[ResearchObjective],
        constraints: ResourceConstraints,
        feasibility: Dict[str, Any]
    ) -> List[str]:
        """Suggest alternative design approaches"""
        
        alternatives = []
        
        # If sample size is limiting
        if "sample_size" in feasibility["limiting_factors"]:
            alternatives.extend([
                "Adaptive design with interim sample size re-estimation",
                "Sequential design with early stopping rules",
                "Bayesian design with informative priors"
            ])
        
        # If budget is limiting
        if "budget" in feasibility["limiting_factors"]:
            alternatives.extend([
                "Pragmatic design using existing care infrastructure",
                "Cluster randomized design to reduce per-participant costs",
                "Historical control design (if appropriate)"
            ])
        
        # If time is limiting
        if "time" in feasibility["limiting_factors"]:
            alternatives.extend([
                "Parallel group design instead of crossover",
                "Surrogate endpoints for faster results",
                "Pilot study with planned follow-up study"
            ])
        
        # General alternatives
        alternatives.extend([
            "Stepped wedge design for implementation studies",
            "N-of-1 trials for personalized medicine",
            "Platform trial for multiple interventions"
        ])
        
        return alternatives[:8]  # Limit to top 8 alternatives
    
    # Power calculation methods
    def _calculate_ttest_power(self, effect_size: float, alpha: float, n: int) -> float:
        """Calculate power for t-test"""
        return self._calculate_power(effect_size, alpha, n, 2)
    
    def _calculate_anova_power(self, effect_size: float, alpha: float, n: int, groups: int = 3) -> float:
        """Calculate power for ANOVA"""
        return self._calculate_power(effect_size, alpha, n, groups)
    
    def _calculate_chi_square_power(self, effect_size: float, alpha: float, n: int) -> float:
        """Calculate power for chi-square test"""
        return self._calculate_power(effect_size, alpha, n, 2)
    
    def _calculate_regression_power(self, effect_size: float, alpha: float, n: int) -> float:
        """Calculate power for regression analysis"""
        return self._calculate_power(effect_size * 0.8, alpha, n, 2)  # Adjust for regression context
    
    async def get_design_health_status(self) -> GetDesignHealthStatusResult:
        """Get health status of the experimental design service"""
        return {
            "service_name": "ExperimentalDesignAssistantService",
            "status": "healthy",
            "supported_design_types": [dt.value for dt in ExperimentType],
            "supported_study_phases": [sp.value for sp in StudyPhase],
            "power_analysis_methods": [pam.value for pam in PowerAnalysisMethod],
            "domain_expertise": list(self.domain_expertise.keys()),
            "design_templates": list(self.design_templates.keys()),
            "version": "1.0.0",
            "last_check": datetime.now(UTC).isoformat()
        }
