#!/usr/bin/env python3
"""
Unit Tests for Domain Templates Generator Service
Test suite for automated domain-specific research template generation

This test suite validates the functionality of the Domain Templates Generator,
ensuring reliable template creation, customization, and export capabilities.

Author: AXIOM Autonomous Laboratory System  
Date: September 13, 2025
"""

import pytest
import asyncio
from datetime import timedelta
import json
import yaml

from app.services.domain_templates_service import (
    DomainTemplatesService,
    ScientificDomain,
    ExperimentType,
    TemplateComplexity,
    ExperimentTemplate,
    WorkflowStep,
    DomainKnowledge
)

class TestDomainTemplatesService:
    """Test suite for Domain Templates Generator Service"""
    
    @pytest.fixture
    def service(self):
        """Create fresh service instance for each test"""
        return DomainTemplatesService()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initializes correctly with domain knowledge"""
        assert isinstance(service.domain_knowledge, dict)
        assert len(service.domain_knowledge) > 0
        assert len(service.workflow_library) > 0
        assert isinstance(service.templates, dict)
        assert isinstance(service.template_usage_stats, dict)
        
        # Check domain knowledge structure
        for domain, knowledge in service.domain_knowledge.items():
            assert isinstance(domain, ScientificDomain)
            assert isinstance(knowledge, DomainKnowledge)
            assert knowledge.domain == domain
            assert len(knowledge.common_methodologies) > 0
            assert len(knowledge.typical_equipment) > 0
    
    @pytest.mark.asyncio
    async def test_generate_basic_template(self, service):
        """Test basic template generation"""
        template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,
            experiment_type=ExperimentType.SIMULATION,
            complexity=TemplateComplexity.BASIC
        )
        
        assert isinstance(template, ExperimentTemplate)
        assert template.domain == ScientificDomain.COMPUTATIONAL_BIOLOGY
        assert template.experiment_type == ExperimentType.SIMULATION
        assert template.complexity == TemplateComplexity.BASIC
        assert len(template.objectives) > 0
        assert len(template.workflow_steps) > 0
        assert template.estimated_cost > 0
        assert template.estimated_duration > timedelta(0)
        
        # Check template is stored
        assert template.id in service.templates
        assert template.id in service.template_usage_stats
        assert service.template_usage_stats[template.id] == 0
    
    @pytest.mark.asyncio
    async def test_generate_advanced_template(self, service):
        """Test advanced template generation with more complexity"""
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.ADVANCED
        )
        
        assert template.complexity == TemplateComplexity.ADVANCED
        
        # Advanced templates should have more resources and higher costs
        basic_template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.BASIC
        )
        
        assert template.estimated_cost > basic_template.estimated_cost
        assert template.estimated_duration >= basic_template.estimated_duration
    
    @pytest.mark.asyncio
    async def test_generate_template_with_custom_requirements(self, service):
        """Test template generation with custom requirements"""
        custom_requirements = {
            "special_equipment": ["Advanced spectrometer"],
            "budget_constraint": 50000,
            "timeline_constraint": 60
        }
        
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.INTERMEDIATE,
            custom_requirements=custom_requirements
        )
        
        assert isinstance(template, ExperimentTemplate)
        assert template.domain == ScientificDomain.MATERIALS_SCIENCE
        assert template.experiment_type == ExperimentType.SYNTHESIS
        assert template.complexity == TemplateComplexity.INTERMEDIATE
    
    @pytest.mark.asyncio
    async def test_customize_template(self, service):
        """Test template customization functionality"""
        # First generate a template
        original_template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,
            experiment_type=ExperimentType.COMPUTATIONAL,
            complexity=TemplateComplexity.BASIC
        )
        
        # Customize it
        customizations = {
            "objectives": ["Additional custom objective"],
            "equipment": ["Custom equipment item"],
            "additional_steps": [
                {
                    "id": "custom_analysis",
                    "name": "Custom Analysis Step",
                    "description": "Custom analysis for specific requirements",
                    "category": "analysis",
                    "inputs": ["custom_input"],
                    "outputs": ["custom_output"],
                    "parameters": {"custom_param": "value"},
                    "duration_estimate": timedelta(days=1),
                    "dependencies": [],
                    "tools_required": ["custom_tool"],
                    "safety_requirements": [],
                    "best_practices": [],
                    "validation_criteria": []
                }
            ]
        }
        
        customized_template = await service.customize_template(
            template_id=original_template.id,
            customizations=customizations
        )
        
        # Verify customization
        assert customized_template.id != original_template.id
        assert "Additional custom objective" in customized_template.objectives
        assert "Custom equipment item" in customized_template.required_equipment
        assert len(customized_template.workflow_steps) == len(original_template.workflow_steps) + 1
        
        # Verify the custom step was added
        custom_step_found = False
        for step in customized_template.workflow_steps:
            if step.id == "custom_analysis":
                custom_step_found = True
                assert step.name == "Custom Analysis Step"
                break
        assert custom_step_found, "Custom analysis step should be added to workflow"
        
        # Check custom step is present
        custom_steps = [step for step in customized_template.workflow_steps if step.id == "custom_analysis"]
        assert len(custom_steps) == 1
        assert custom_steps[0].name == "Custom Analysis Step"
        
        # Verify customization is tracked
        assert customized_template.id in service.customizations
        assert service.customizations[customized_template.id] == customizations
    
    @pytest.mark.asyncio
    async def test_customize_nonexistent_template(self, service):
        """Test error handling when customizing non-existent template"""
        with pytest.raises(ValueError, match="Template .* not found"):
            await service.customize_template(
                template_id="nonexistent_template",
                customizations={"objectives": ["test"]}
            )
    
    @pytest.mark.asyncio
    async def test_export_template_yaml(self, service):
        """Test template export in YAML format"""
        template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.SIMULATION,
            complexity=TemplateComplexity.INTERMEDIATE
        )
        
        # Export as YAML
        yaml_content = await service.export_template(
            template_id=template.id,
            format_type="yaml"
        )
        
        assert isinstance(yaml_content, str)
        assert len(yaml_content) > 0
        
        # Verify it's valid YAML
        parsed_yaml = yaml.safe_load(yaml_content)
        assert isinstance(parsed_yaml, dict)
        assert "template_info" in parsed_yaml
        assert "workflow" in parsed_yaml
        assert "resources" in parsed_yaml
        assert parsed_yaml["template_info"]["id"] == template.id
    
    @pytest.mark.asyncio
    async def test_export_template_json(self, service):
        """Test template export in JSON format"""
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.BASIC
        )
        
        # Export as JSON
        json_content = await service.export_template(
            template_id=template.id,
            format_type="json"
        )
        
        assert isinstance(json_content, str)
        assert len(json_content) > 0
        
        # Verify it's valid JSON
        parsed_json = json.loads(json_content)
        assert isinstance(parsed_json, dict)
        assert "template_info" in parsed_json
        assert "workflow" in parsed_json
        assert "resources" in parsed_json
        assert parsed_json["template_info"]["id"] == template.id
    
    @pytest.mark.asyncio
    async def test_export_nonexistent_template(self, service):
        """Test error handling when exporting non-existent template"""
        with pytest.raises(ValueError, match="Template .* not found"):
            await service.export_template(
                template_id="nonexistent_template",
                format_type="yaml"
            )
    
    @pytest.mark.asyncio
    async def test_export_invalid_format(self, service):
        """Test error handling for invalid export format"""
        template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.COMPUTATIONAL,
            complexity=TemplateComplexity.BASIC
        )
        
        with pytest.raises(ValueError, match="Unsupported format"):
            await service.export_template(
                template_id=template.id,
                format_type="invalid_format"
            )
    
    @pytest.mark.asyncio
    async def test_get_template_recommendations_basic(self, service):
        """Test basic template recommendations"""
        # Generate some templates first
        await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,
            experiment_type=ExperimentType.SIMULATION,
            complexity=TemplateComplexity.BASIC
        )
        
        await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.INTERMEDIATE
        )
        
        # Get recommendations
        recommendations = await service.get_template_recommendations(
            research_goals=["molecular dynamics", "protein analysis"],
            available_resources={
                "equipment": ["High-performance computing clusters", "GPU workstations"],
                "budget": 20000
            },
            constraints={"budget": 25000, "timeline_days": 90}
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert "template_id" in rec
            assert "template_name" in rec
            assert "domain" in rec
            assert "relevance_score" in rec
            assert 0 <= rec["relevance_score"] <= 1
            assert "estimated_duration" in rec
            assert "estimated_cost" in rec
    
    @pytest.mark.asyncio
    async def test_get_template_recommendations_with_constraints(self, service):
        """Test recommendations with budget and timeline constraints"""
        # Generate expensive and cheap templates
        await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.ADVANCED
        )
        
        await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.DATA_ANALYSIS,
            complexity=TemplateComplexity.BASIC
        )
        
        # Request recommendations with tight budget
        recommendations = await service.get_template_recommendations(
            research_goals=["data analysis", "biology"],
            available_resources={"budget": 5000},
            constraints={"budget": 5000, "timeline_days": 30}
        )
        
        # Should prefer cheaper, faster templates
        if recommendations:
            top_rec = recommendations[0]
            # The basic biology template should score higher due to constraints
            assert top_rec["estimated_cost"] <= 5000
    
    @pytest.mark.asyncio
    async def test_get_service_status(self, service):
        """Test service status reporting"""
        # Generate some templates first
        await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.ADVANCED
        )
        
        status = await service.get_service_status()
        
        assert isinstance(status, dict)
        assert status["service_name"] == "Domain Templates Generator Service"
        assert status["status"] == "operational"
        assert "version" in status
        assert "statistics" in status
        assert "supported_domains" in status
        assert "capabilities" in status
        
        # Check statistics
        stats = status["statistics"]
        assert stats["total_templates"] >= 1
        assert stats["domains_supported"] > 0
        assert stats["workflow_steps_library"] > 0
        
        # Check capabilities
        capabilities = status["capabilities"]
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("template generation" in cap.lower() for cap in capabilities)
    
    def test_workflow_step_structure(self, service):
        """Test WorkflowStep dataclass structure"""
        step = WorkflowStep(
            id="test_step",
            name="Test Step",
            description="A test workflow step",
            category="test",
            inputs=["input1"],
            outputs=["output1"],
            parameters={"param1": "value1"},
            duration_estimate=timedelta(days=1)
        )
        
        assert step.id == "test_step"
        assert step.name == "Test Step"
        assert step.description == "A test workflow step"
        assert step.category == "test"
        assert step.inputs == ["input1"]
        assert step.outputs == ["output1"]
        assert step.parameters == {"param1": "value1"}
        assert step.duration_estimate == timedelta(days=1)
        assert step.dependencies == []  # Default empty list
        assert step.tools_required == []  # Default empty list
    
    def test_domain_knowledge_structure(self, service):
        """Test DomainKnowledge dataclass structure"""
        # Test one of the initialized domain knowledge bases
        comp_bio_knowledge = service.domain_knowledge[ScientificDomain.COMPUTATIONAL_BIOLOGY]
        
        assert comp_bio_knowledge.domain == ScientificDomain.COMPUTATIONAL_BIOLOGY
        assert isinstance(comp_bio_knowledge.common_methodologies, list)
        assert isinstance(comp_bio_knowledge.typical_equipment, list)
        assert isinstance(comp_bio_knowledge.software_tools, list)
        assert len(comp_bio_knowledge.common_methodologies) > 0
        assert len(comp_bio_knowledge.typical_equipment) > 0
        assert len(comp_bio_knowledge.software_tools) > 0
        
        # Check that key methodologies are included
        methodologies = [m.lower() for m in comp_bio_knowledge.common_methodologies]
        assert any("molecular dynamics" in m for m in methodologies)
        assert any("protein" in m for m in methodologies)
    
    @pytest.mark.asyncio
    async def test_template_name_generation(self, service):
        """Test that template names are generated correctly"""
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,
            experiment_type=ExperimentType.CHARACTERIZATION,
            complexity=TemplateComplexity.EXPERT
        )
        
        assert "Materials Science" in template.name or "materials" in template.name.lower()
        assert "Expert" in template.name or "expert" in template.name.lower()
    
    @pytest.mark.asyncio
    async def test_template_id_uniqueness(self, service):
        """Test that generated template IDs are unique"""
        template1 = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.SIMULATION,
            complexity=TemplateComplexity.BASIC
        )
        
        # Small delay to ensure different timestamp
        await asyncio.sleep(0.001)
        
        template2 = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.SIMULATION,
            complexity=TemplateComplexity.BASIC
        )
        
        assert template1.id != template2.id
        assert template1.id in service.templates
        assert template2.id in service.templates
    
    @pytest.mark.asyncio
    async def test_cost_estimation_by_complexity(self, service):
        """Test that cost estimation varies appropriately by complexity"""
        basic_template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.DATA_ANALYSIS,
            complexity=TemplateComplexity.BASIC
        )
        
        expert_template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.DATA_ANALYSIS,
            complexity=TemplateComplexity.EXPERT
        )
        
        # Expert templates should cost significantly more
        assert expert_template.estimated_cost > basic_template.estimated_cost * 2
    
    @pytest.mark.asyncio
    async def test_duration_estimation_by_complexity(self, service):
        """Test that duration estimation varies by complexity"""
        basic_template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.MODELING,
            complexity=TemplateComplexity.BASIC
        )
        
        advanced_template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.MODELING,
            complexity=TemplateComplexity.ADVANCED
        )
        
        # Advanced templates should take longer
        assert advanced_template.estimated_duration >= basic_template.estimated_duration
    
    @pytest.mark.asyncio
    async def test_template_tags_generation(self, service):
        """Test that appropriate tags are generated for templates"""
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.OPTIMIZATION,
            complexity=TemplateComplexity.INTERMEDIATE
        )
        
        assert isinstance(template.tags, list)
        assert len(template.tags) > 0
        assert "materials_science" in template.tags
        assert "optimization" in template.tags
        assert "intermediate" in template.tags
        assert "automated_template" in template.tags
    
    @pytest.mark.asyncio
    async def test_safety_protocols_generation(self, service):
        """Test that safety protocols are generated appropriately"""
        template = await service.generate_template(
            domain=ScientificDomain.MATERIALS_SCIENCE,  # Use available domain
            experiment_type=ExperimentType.SYNTHESIS,
            complexity=TemplateComplexity.ADVANCED
        )
        
        assert isinstance(template.safety_protocols, list)
        assert len(template.safety_protocols) > 0
        
        # Should include general safety protocols
        safety_text = " ".join(template.safety_protocols).lower()
        assert any(word in safety_text for word in ["safety", "risk", "emergency", "training"])
    
    @pytest.mark.asyncio
    async def test_data_management_plan_generation(self, service):
        """Test that data management plans are generated"""
        template = await service.generate_template(
            domain=ScientificDomain.COMPUTATIONAL_BIOLOGY,  # Use available domain
            experiment_type=ExperimentType.SCREENING,
            complexity=TemplateComplexity.INTERMEDIATE
        )
        
        assert isinstance(template.data_management, dict)
        assert "storage_requirements" in template.data_management
        assert "data_formats" in template.data_management
        assert "metadata_standards" in template.data_management
        assert "sharing_policy" in template.data_management
        
        # Check storage requirements structure
        storage = template.data_management["storage_requirements"]
        assert "primary_storage" in storage
        assert "backup_frequency" in storage
        assert "retention_period" in storage
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_domain(self, service):
        """Test error handling for invalid domain values"""
        # This should be caught at the enum level, but test our service handles it
        with pytest.raises((ValueError, AttributeError)):
            await service.generate_template(
                domain="invalid_domain",  # This will fail at enum creation
                experiment_type=ExperimentType.SIMULATION,
                complexity=TemplateComplexity.BASIC
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
