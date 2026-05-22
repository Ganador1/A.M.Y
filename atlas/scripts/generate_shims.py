import os

services_map = {
    "ml": [
        "massive_automl_service", "scientific_automl_service", "scikit_learn_service", 
        "scipy_service", "surrogate_modeling", "bayesian_optimization", 
        "conformal_prediction_improved", "federated_learning_service",
        "adaptive_energy_sampler", "adaptive_loss_optimizer", "causal_discovery_service", 
        "huggingface_agent_wrapper", "improved_agent_prompts", "iterative_improvement_service", 
        "matscibert_service", "mlflow_auto_promotion_service", "mlflow_registry_service", 
        "model_management_service", "normalizer", "perturbation_engine", 
        "pipeline_optimization_service", "plausibility_dataset_builder", "scibert_service", 
        "synthetic_data_service", "transform_service"
    ],
    "math": [
        "analytical_geometry", "arithmetic", "complex_analysis_service", 
        "differential_equations_fixed", "graph_theory", "graphing", "number_theory", 
        "variational_calculus_service", "sympy_service", "sagemath_service", 
        "statistical_analysis", "statistical_validation", "statistical_validation_service", 
        "statistics_service_advanced", "fast_vpinns_accelerator", "pde_service"
    ],
    "literature": [
        "literature_analyzer", "literature_mining_service", "literature_offline_cache", 
        "literature_search_improved", "literature_service", "pubmed_integration_service", 
        "pubmed_service", "evidence_synthesis_service", "paper_analysis_service", 
        "paper_enhancement", "manuscript_assembly_service", "journal_formatter", 
        "reference_generator", "supplementary_materials_generator", "publication_generator", 
        "publication_system_registration"
    ],
    "infrastructure": [
        "audit_service", "auth_service", "automated_alerts", "circuit_breaker_service", 
        "cloud_integration_service", "cloud_lab_service", "advanced_cloud_lab_service", 
        "data_versioning", "data_versioning_service", "database_service", 
        "decision_ledger_service", "dynamic_priority_queue_service", "experiment_tracking", 
        "metrics_service", "monitoring_service", "observability_service", 
        "policy_engine_service", "provenance", "reproducibility", "reproducibility_database", 
        "reproducibility_service", "sandbox_executor_service", "workspace_manager_service",
        "benchmark_harness_service", "cost_metrics_service", "cryptography", 
        "domain_templates_service", "hypothesis_persistence", "lean4_installer_improved", 
        "matplotlib_service", "scientific_figure_generator", "scientific_ui_service"
    ],
    "scientific_ai": [
        "ai_scientist_service", "code_scientist_service", "scientific_ai", 
        "scientific_copilot", "scientific_hypothesis_agent", "multi_model_hypothesis_service", 
        "multimodal_reasoning_service", "ollama_service", "local_llm_service", 
        "llm_routing_service", "ai_researcher_adapter", "experimental_design_service", 
        "experimental_protocols", "experimental_toolkit_hub", "hypothesis_tournament_service"
    ],
    "advanced": [
        "advanced_earth_sciences_service", "advanced_knowledge_graph_service", 
        "advanced_peer_review_service", "advanced_scientific_database_service", 
        "advanced_segmentation_service", "advanced_torch_operations", 
        "optimization_service_advanced", "time_series_service_advanced",
        "digital_twins_service", "lab_automation_service", "virtual_microscopes"
    ],
    "verification": [
        "consistency_checker_service_improved", "formal_verification_service", 
        "hybrid_verification_service", "experimental_validator", "scientific_evaluation_service", 
        "plausibility_scoring_service_improved", "reproducibility_risk_service",
        "active_reproducibility_engine", "autonomous_peer_review_service", 
        "counterexample_fuzzer", "cvc5_service", "peer_review_service", "stress_testing_service"
    ],
    "earth_sciences": ["earth_sciences_service", "earth_sciences_light_service"],
    "data_services": ["knowledge_graph_service", "scientific_data_lake_service", "structural_database_service", "vector_store"],
    "orchestration": [
        "agent2_bridge_service", "experiment_scheduler_v3", "policy_aware_scheduler", 
        "strategic_planner_service", "tool_evidence_orchestrator"
    ],
    "orchestration/management": [
        "master_orchestration_service_refactored", "multi_agent_coordinator", 
        "multi_agent_orchestrator", "research_cycle_manager", "unified_research_orchestrator", 
        "workflow_orchestration"
    ],
    "domains/engineering/services": ["additive_manufacturing_service", "gnome_materials_service", "materials_discovery_service"],
    "domains/medicine/services": ["advanced_clinical_validation_service", "advanced_medical_imaging_service", "cardiac_region_models", "personalized_medicine_service"],
    "domains/biology/services": ["computational_biology", "dnabert2_service"],
    "domains/chemistry/services": ["computational_chemistry", "molecular_dynamics", "xray_crystallography_service"],
    "domains/physics/services": ["particle_physics_service", "solid_state_physics"],
    "domains/neuroscience/services": ["neuroscience_light_service"]
}

base_path = "/Volumes/Ganador disk/atlas/app/services"

for subfolder, services in services_map.items():
    for service in services:
        if subfolder.startswith("domains"):
            full_path = f"app.{subfolder.replace('/', '.')}.{service}"
        else:
            full_path = f"app.services.{subfolder.replace('/', '.')}.{service}"
        
        shim_content = f'"""\nCompatibility shim for {service}.\nRe-exports from {full_path}\n"""\n\nfrom {full_path} import *\n'
        shim_path = os.path.join(base_path, f"{service}.py")
        with open(shim_path, "w") as f:
            f.write(shim_content)
        print(f"Created shim: {shim_path}")

# Special shims for core
core_services = ["base_service", "async_processor"]
for service in core_services:
    full_path = f"app.core.{service}"
    shim_content = f'"""\nCompatibility shim for {service}.\nRe-exports from {full_path}\n"""\n\nfrom {full_path} import *\n'
    shim_path = os.path.join(base_path, f"{service}.py")
    with open(shim_path, "w") as f:
        f.write(shim_content)
    print(f"Created core shim: {shim_path}")
