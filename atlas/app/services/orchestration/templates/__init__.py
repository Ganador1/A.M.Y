"""
Workflow Templates for Master Orchestration Service
Templates para diferentes tipos de pipelines de investigación
"""

import uuid
from typing import Dict, Any, List, Callable
from app.services.orchestration.models import PipelineTask, TaskPriority, PipelineStatus


class WorkflowTemplates:
    """Gestión de templates de workflows"""

    @staticmethod
    def create_literature_discovery_template() -> Callable:
        """Template for literature discovery workflow"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Comprehensive literature search
            tasks.append(PipelineTask(
                id=f"lit_search_{uuid.uuid4().hex[:8]}",
                name="Literature Search",
                service="literature",
                method="comprehensive_search",
                parameters={
                    'query': research_question,
                    'domain': domain,
                    'max_results': params.get('max_results', 100),
                    'semantic_search': True
                },
                dependencies=[],
                priority=TaskPriority.HIGH,
                timeout=300,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            ))

            # Task 2: Extract key concepts
            tasks.append(PipelineTask(
                id=f"concept_extract_{uuid.uuid4().hex[:8]}",
                name="Concept Extraction",
                service="literature",
                method="extract_key_concepts",
                parameters={
                    'text': '${lit_search.results[0].abstract}'  # Reference to previous task
                },
                dependencies=[tasks[0].id],
                priority=TaskPriority.MEDIUM,
                timeout=120,
                retry_count=0,
                max_retries=1,
                status=PipelineStatus.PENDING
            ))

            return tasks

        return template

    @staticmethod
    def create_automl_optimization_template() -> Callable:
        """Template for AutoML optimization workflow"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Auto-discover best model
            tasks.append(PipelineTask(
                id=f"automl_discover_{uuid.uuid4().hex[:8]}",
                name="AutoML Model Discovery",
                service="automl",
                method="auto_discover_model",
                parameters={
                    'X': params.get('dataset_X'),
                    'y': params.get('dataset_y'),
                    'domain': domain,
                    'time_limit': params.get('time_limit', 300)
                },
                dependencies=[],
                priority=TaskPriority.HIGH,
                timeout=600,
                retry_count=0,
                max_retries=1,
                status=PipelineStatus.PENDING
            ))

            # Task 2: Model evaluation
            tasks.append(PipelineTask(
                id=f"model_eval_{uuid.uuid4().hex[:8]}",
                name="Model Evaluation",
                service="automl",
                method="evaluate_model_performance",
                parameters={
                    'model_id': '${automl_discover.best_model.id}',
                    'test_data': params.get('test_data')
                },
                dependencies=[tasks[0].id],
                priority=TaskPriority.MEDIUM,
                timeout=180,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            ))

            return tasks

        return template

    @staticmethod
    def create_scientific_reasoning_template() -> Callable:
        """Template for scientific reasoning workflow"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Scientific reasoning
            tasks.append(PipelineTask(
                id=f"sci_reasoning_{uuid.uuid4().hex[:8]}",
                name="Scientific Reasoning",
                service="scientific_ai",
                method="scientific_reasoning_workflow",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'context': params.get('context', {})
                },
                dependencies=[],
                priority=TaskPriority.HIGH,
                timeout=600,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            ))

            return tasks

        return template

    @staticmethod
    def create_comprehensive_research_template() -> Callable:
        """Template for comprehensive research workflow"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Literature search
            lit_task = PipelineTask(
                id=f"lit_search_{uuid.uuid4().hex[:8]}",
                name="Literature Search",
                service="literature",
                method="comprehensive_search",
                parameters={
                    'query': research_question,
                    'domain': domain,
                    'max_results': 50,
                    'semantic_search': True
                },
                dependencies=[],
                priority=TaskPriority.HIGH,
                timeout=300,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(lit_task)

            # Task 2: Scientific reasoning
            reasoning_task = PipelineTask(
                id=f"sci_reasoning_{uuid.uuid4().hex[:8]}",
                name="Scientific Reasoning",
                service="scientific_ai",
                method="scientific_reasoning_workflow",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_context': f'${{{lit_task.id}.results}}'
                },
                dependencies=[lit_task.id],
                priority=TaskPriority.HIGH,
                timeout=600,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(reasoning_task)

            # Task 3: AI Scientist Analysis
            ai_scientist_task = PipelineTask(
                id=f"ai_scientist_{uuid.uuid4().hex[:8]}",
                name="AI Scientist Analysis",
                service="ai_scientist",
                method="generate_research_hypothesis",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_context': f'${{{lit_task.id}.results}}',
                    'reasoning_context': f'${{{reasoning_task.id}.results}}'
                },
                dependencies=[lit_task.id, reasoning_task.id],
                priority=TaskPriority.HIGH,
                timeout=600,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(ai_scientist_task)

            # Task 4: Code Analysis (if applicable)
            code_scientist_task = PipelineTask(
                id=f"code_scientist_{uuid.uuid4().hex[:8]}",
                name="Code Pattern Analysis",
                service="code_scientist",
                method="analyze_research_patterns",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'hypothesis': f'${{{ai_scientist_task.id}.hypothesis}}'
                },
                dependencies=[ai_scientist_task.id],
                priority=TaskPriority.MEDIUM,
                timeout=300,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(code_scientist_task)

            # Task 5: Research orchestration
            orchestration_task = PipelineTask(
                id=f"research_orch_{uuid.uuid4().hex[:8]}",
                name="Research Orchestration",
                service="research_orchestrator",
                method="orchestrate_research_cycle",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_results': f'${{{lit_task.id}.results}}',
                    'reasoning_results': f'${{{reasoning_task.id}.results}}',
                    'ai_scientist_results': f'${{{ai_scientist_task.id}.results}}',
                    'code_analysis_results': f'${{{code_scientist_task.id}.results}}'
                },
                dependencies=[lit_task.id, reasoning_task.id, ai_scientist_task.id, code_scientist_task.id],
                priority=TaskPriority.HIGH,
                timeout=900,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(orchestration_task)

            return tasks

        return template

    @staticmethod
    def create_advanced_scientific_research_template() -> Callable:
        """Template for advanced scientific research with AI and code analysis"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Comprehensive Literature Mining
            lit_task = PipelineTask(
                id=f"advanced_lit_{uuid.uuid4().hex[:8]}",
                name="Advanced Literature Mining",
                service="literature",
                method="comprehensive_search",
                parameters={
                    'query': research_question,
                    'domain': domain,
                    'max_results': 100,
                    'semantic_search': True,
                    'include_citations': True,
                    'filter_quality': True
                },
                dependencies=[],
                priority=TaskPriority.CRITICAL,
                timeout=600,
                retry_count=0,
                max_retries=3,
                status=PipelineStatus.PENDING
            )
            tasks.append(lit_task)

            # Task 2: AI Scientist Hypothesis Generation
            hypothesis_task = PipelineTask(
                id=f"hypothesis_{uuid.uuid4().hex[:8]}",
                name="Hypothesis Generation",
                service="ai_scientist",
                method="generate_research_hypothesis",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_context': f'${{{lit_task.id}.results}}',
                    'generate_multiple': True,
                    'include_methodology': True
                },
                dependencies=[lit_task.id],
                priority=TaskPriority.CRITICAL,
                timeout=900,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(hypothesis_task)

            # Task 3: Experimental Design
            experiment_task = PipelineTask(
                id=f"experiment_{uuid.uuid4().hex[:8]}",
                name="Experimental Design",
                service="ai_scientist",
                method="design_experiment",
                parameters={
                    'hypothesis': f'${{{hypothesis_task.id}.hypothesis}}',
                    'domain': domain,
                    'literature_context': f'${{{lit_task.id}.results}}',
                    'include_controls': True,
                    'statistical_power': 0.8
                },
                dependencies=[hypothesis_task.id],
                priority=TaskPriority.HIGH,
                timeout=600,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(experiment_task)

            # Task 4: Code Pattern Analysis
            code_analysis_task = PipelineTask(
                id=f"code_analysis_{uuid.uuid4().hex[:8]}",
                name="Code Pattern Analysis",
                service="code_scientist",
                method="analyze_research_patterns",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'hypothesis': f'${{{hypothesis_task.id}.hypothesis}}',
                    'experimental_design': f'${{{experiment_task.id}.design}}'
                },
                dependencies=[hypothesis_task.id, experiment_task.id],
                priority=TaskPriority.HIGH,
                timeout=450,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(code_analysis_task)

            # Task 5: Algorithm Discovery
            algorithm_task = PipelineTask(
                id=f"algorithm_{uuid.uuid4().hex[:8]}",
                name="Algorithm Discovery",
                service="code_scientist",
                method="discover_algorithms",
                parameters={
                    'domain': domain,
                    'problem_context': research_question,
                    'code_patterns': f'${{{code_analysis_task.id}.patterns}}',
                    'optimization_target': 'accuracy'
                },
                dependencies=[code_analysis_task.id],
                priority=TaskPriority.MEDIUM,
                timeout=600,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(algorithm_task)

            # Task 6: Scientific Reasoning
            reasoning_task = PipelineTask(
                id=f"reasoning_{uuid.uuid4().hex[:8]}",
                name="Scientific Reasoning",
                service="scientific_ai",
                method="scientific_reasoning_workflow",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_context': f'${{{lit_task.id}.results}}',
                    'hypothesis': f'${{{hypothesis_task.id}.hypothesis}}',
                    'experimental_design': f'${{{experiment_task.id}.design}}'
                },
                dependencies=[lit_task.id, hypothesis_task.id, experiment_task.id],
                priority=TaskPriority.HIGH,
                timeout=900,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(reasoning_task)

            # Task 7: AutoML Optimization (if applicable)
            automl_task = PipelineTask(
                id=f"automl_{uuid.uuid4().hex[:8]}",
                name="AutoML Optimization",
                service="automl",
                method="optimize_research_pipeline",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'algorithms': f'${{{algorithm_task.id}.algorithms}}',
                    'optimization_metric': 'f1_score'
                },
                dependencies=[algorithm_task.id],
                priority=TaskPriority.MEDIUM,
                timeout=1200,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(automl_task)

            # Task 8: Final Research Orchestration
            final_orchestration_task = PipelineTask(
                id=f"final_orch_{uuid.uuid4().hex[:8]}",
                name="Final Research Orchestration",
                service="research_orchestrator",
                method="orchestrate_research_cycle",
                parameters={
                    'research_question': research_question,
                    'domain': domain,
                    'literature_results': f'${{{lit_task.id}.results}}',
                    'hypothesis': f'${{{hypothesis_task.id}.hypothesis}}',
                    'experimental_design': f'${{{experiment_task.id}.design}}',
                    'code_analysis': f'${{{code_analysis_task.id}.results}}',
                    'algorithms': f'${{{algorithm_task.id}.algorithms}}',
                    'reasoning_results': f'${{{reasoning_task.id}.results}}',
                    'automl_results': f'${{{automl_task.id}.results}}'
                },
                dependencies=[lit_task.id, hypothesis_task.id, experiment_task.id,
                            code_analysis_task.id, algorithm_task.id, reasoning_task.id, automl_task.id],
                priority=TaskPriority.CRITICAL,
                timeout=1200,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(final_orchestration_task)

            return tasks

        return template

    @staticmethod
    def create_agent2_fair_ingestion_template() -> Callable:
        """Template for FAIR dataset ingestion from Agent 2"""

        def template(research_question: str, domain: str, params: Dict) -> List[PipelineTask]:
            tasks = []

            # Task 1: Discover Agent 2 Services
            discover_task = PipelineTask(
                id=f"discover_agent2_{uuid.uuid4().hex[:8]}",
                name="Discover Agent 2 Services",
                service="agent2_bridge",
                method="discover_services",
                parameters={
                    'timeout': 30,
                    'verify_connectivity': True
                },
                dependencies=[],
                priority=TaskPriority.HIGH,
                timeout=30,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(discover_task)

            # Task 2: Ingest FAIR Dataset from Agent 2
            ingest_task = PipelineTask(
                id=f"ingest_dataset_{uuid.uuid4().hex[:8]}",
                name="Ingest FAIR Dataset",
                service="agent2_bridge",
                method="ingest_dataset",
                parameters={
                    'dataset_id': params.get('dataset_id', '$input.dataset_id'),
                    'format': 'fair',
                    'metadata_requirements': {
                        'minimal': ['title', 'description', 'license', 'creators'],
                        'recommended': ['keywords', 'version', 'publication_date', 'domain']
                    },
                    'quality_checks': True,
                    'validation_strictness': 'strict'
                },
                dependencies=[discover_task.id],
                priority=TaskPriority.CRITICAL,
                timeout=300,
                retry_count=0,
                max_retries=3,
                status=PipelineStatus.PENDING
            )
            tasks.append(ingest_task)

            # Task 3: Validate FAIR Compliance
            validate_task = PipelineTask(
                id=f"validate_fair_{uuid.uuid4().hex[:8]}",
                name="Validate FAIR Compliance",
                service="data_scientist",
                method="validate_dataset_compliance",
                parameters={
                    'dataset': f'${{{ingest_task.id}.result}}',
                    'principles': ['F', 'A', 'I', 'R'],
                    'scoring_threshold': 0.8,
                    'generate_report': True
                },
                dependencies=[ingest_task.id],
                priority=TaskPriority.HIGH,
                timeout=120,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(validate_task)

            # Task 4: Register Dataset in Catalog
            register_task = PipelineTask(
                id=f"register_dataset_{uuid.uuid4().hex[:8]}",
                name="Register Dataset in Catalog",
                service="data_scientist",
                method="register_dataset",
                parameters={
                    'dataset': f'${{{ingest_task.id}.result}}',
                    'compliance_report': f'${{{validate_task.id}.result}}',
                    'catalog_type': 'scientific_research',
                    'make_public': params.get('make_public', False),
                    'access_level': 'restricted'
                },
                dependencies=[validate_task.id],
                priority=TaskPriority.MEDIUM,
                timeout=60,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(register_task)

            # Task 5: Generate Data Profile
            profile_task = PipelineTask(
                id=f"profile_dataset_{uuid.uuid4().hex[:8]}",
                name="Generate Data Profile",
                service="data_scientist",
                method="generate_data_profile",
                parameters={
                    'dataset': f'${{{ingest_task.id}.result}}',
                    'include_statistics': True,
                    'quality_metrics': True,
                    'schema_analysis': True
                },
                dependencies=[ingest_task.id],
                priority=TaskPriority.MEDIUM,
                timeout=90,
                retry_count=0,
                max_retries=2,
                status=PipelineStatus.PENDING
            )
            tasks.append(profile_task)

            return tasks

        return template


# Template registry
TEMPLATE_REGISTRY = {
    'literature_discovery': WorkflowTemplates.create_literature_discovery_template(),
    'automl_optimization': WorkflowTemplates.create_automl_optimization_template(),
    'scientific_reasoning': WorkflowTemplates.create_scientific_reasoning_template(),
    'comprehensive_research': WorkflowTemplates.create_comprehensive_research_template(),
    'advanced_scientific_research': WorkflowTemplates.create_advanced_scientific_research_template(),
    'ingest_fair_dataset_from_agent2': WorkflowTemplates.create_agent2_fair_ingestion_template()
}
