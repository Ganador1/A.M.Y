#!/usr/bin/env python3
"""
AXIOM Domain Templates Generator Demonstration
Functional demonstration of automated domain-specific research template generation

This demonstration showcases the complete capabilities of the Domain Templates Generator,
including template generation, customization, export, and intelligent recommendations.

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import asyncio
import json
import traceback

from app.services.domain_templates_service import (
    domain_templates,
    ScientificDomain,
    ExperimentType,
    TemplateComplexity
)

async def demonstrate_domain_templates_generator():
    """
    🧬 Complete Domain Templates Generator Demonstration
    
    Demonstrates the full workflow of automated template generation:
    1. Service initialization and status
    2. Template generation across domains
    3. Template customization
    4. Export functionality
    5. Intelligent recommendations
    6. Analytics and reporting
    """
    print("\n" + "="*80)
    print("🧬 AXIOM Domain Templates Generator - Complete Demonstration")
    print("="*80)
    
    try:
        # Phase 1: Service Status and Capabilities
        print("\n📊 Phase 1: Service Status and Capabilities")
        print("-" * 50)
        
        status = await domain_templates.get_service_status()
        print(f"✅ Service: {status['service_name']}")
        print(f"📊 Status: {status['status']}")
        print(f"🔢 Version: {status['version']}")
        print(f"🧬 Supported Domains: {len(status['supported_domains'])}")
        print(f"🧪 Experiment Types: {len(status['supported_experiment_types'])}")
        print(f"📈 Complexity Levels: {len(status['supported_complexity_levels'])}")
        print(f"⚡ Capabilities: {len(status['capabilities'])}")
        
        # Phase 2: Template Generation Across Domains
        print("\n🏭 Phase 2: Multi-Domain Template Generation")
        print("-" * 50)
        
        generation_scenarios = [
            {
                "name": "Computational Biology Simulation (Advanced)",
                "domain": ScientificDomain.COMPUTATIONAL_BIOLOGY,
                "experiment_type": ExperimentType.SIMULATION,
                "complexity": TemplateComplexity.ADVANCED
            },
            {
                "name": "Materials Science Synthesis (Expert)",
                "domain": ScientificDomain.MATERIALS_SCIENCE,
                "experiment_type": ExperimentType.SYNTHESIS,
                "complexity": TemplateComplexity.EXPERT
            },
            {
                "name": "Drug Discovery Screening (Intermediate)",
                "domain": ScientificDomain.DRUG_DISCOVERY,
                "experiment_type": ExperimentType.SCREENING,
                "complexity": TemplateComplexity.INTERMEDIATE
            },
            {
                "name": "Climate Science Modeling (Basic)",
                "domain": ScientificDomain.CLIMATE_SCIENCE,
                "experiment_type": ExperimentType.MODELING,
                "complexity": TemplateComplexity.BASIC
            }
        ]
        
        generated_templates = []
        for scenario in generation_scenarios:
            print(f"\n🧬 Generating: {scenario['name']}")
            
            template = await domain_templates.generate_template(
                domain=scenario['domain'],
                experiment_type=scenario['experiment_type'],
                complexity=scenario['complexity']
            )
            
            generated_templates.append(template)
            
            print(f"   📋 Template ID: {template.id}")
            print(f"   📝 Name: {template.name}")
            print(f"   🔬 Domain: {template.domain.value}")
            print(f"   🧪 Type: {template.experiment_type.value}")
            print(f"   📊 Complexity: {template.complexity.value}")
            print(f"   🎯 Objectives: {len(template.objectives)}")
            print(f"   ⚡ Workflow Steps: {len(template.workflow_steps)}")
            print(f"   🛠️ Equipment Required: {len(template.required_equipment)}")
            print(f"   🧪 Materials Required: {len(template.required_materials)}")
            print(f"   💻 Software Required: {len(template.required_software)}")
            print(f"   ⏱️ Estimated Duration: {template.estimated_duration.days} days")
            print(f"   💰 Estimated Cost: ${template.estimated_cost:,.2f}")
            print(f"   🏷️ Tags: {', '.join(template.tags[:3])}...")
        
        print(f"\n✅ Generated {len(generated_templates)} templates successfully!")
        
        # Phase 3: Template Customization
        print("\n✏️ Phase 3: Template Customization")
        print("-" * 50)
        
        # Customize the computational biology template
        comp_bio_template = generated_templates[0]
        print(f"🧬 Customizing: {comp_bio_template.name}")
        
        customizations = {
            "objectives": [
                "Integrate machine learning analysis",
                "Generate publication-ready figures",
                "Perform sensitivity analysis"
            ],
            "equipment": [
                "High-memory workstation",
                "GPU cluster access",
                "Advanced visualization software"
            ],
            "additional_steps": [
                {
                    "id": "ml_analysis",
                    "name": "Machine Learning Analysis",
                    "description": "Apply ML algorithms to analyze simulation results",
                    "category": "analysis",
                    "inputs": ["simulation_results", "feature_data"],
                    "outputs": ["ml_predictions", "model_metrics"],
                    "parameters": {"algorithm": "random_forest", "cross_validation": 5},
                    "duration_estimate": {"days": 3},
                    "dependencies": ["statistical_analysis"],
                    "tools_required": ["scikit-learn", "tensorflow"],
                    "safety_requirements": ["data_validation"],
                    "best_practices": ["feature_selection", "hyperparameter_tuning"],
                    "validation_criteria": ["model_accuracy > 0.85"]
                }
            ]
        }
        
        # Convert timedelta for the additional step
        from datetime import timedelta
        for step in customizations.get("additional_steps", []):
            if "duration_estimate" in step and isinstance(step["duration_estimate"], dict):
                days = step["duration_estimate"].get("days", 1)
                step["duration_estimate"] = timedelta(days=days)
        
        customized_template = await domain_templates.customize_template(
            template_id=comp_bio_template.id,
            customizations=customizations
        )
        
        print(f"✅ Customized Template ID: {customized_template.id}")
        print(f"   📈 Original Steps: {len(comp_bio_template.workflow_steps)}")
        print(f"   📈 Customized Steps: {len(customized_template.workflow_steps)}")
        print(f"   🎯 Additional Objectives: {len(customizations['objectives'])}")
        print(f"   🛠️ Additional Equipment: {len(customizations['equipment'])}")
        print(f"   ⏱️ New Duration: {customized_template.estimated_duration.days} days")
        print(f"   💰 New Cost: ${customized_template.estimated_cost:,.2f}")
        
        # Phase 4: Template Export
        print("\n📄 Phase 4: Template Export")
        print("-" * 50)
        
        # Export in YAML format
        print("🗂️ Exporting customized template in YAML format...")
        yaml_export = await domain_templates.export_template(
            template_id=customized_template.id,
            format_type="yaml"
        )
        
        print(f"✅ YAML Export Length: {len(yaml_export)} characters")
        print("📄 YAML Preview (first 500 chars):")
        print(yaml_export[:500] + "..." if len(yaml_export) > 500 else yaml_export)
        
        # Export in JSON format
        print("\n🗂️ Exporting materials science template in JSON format...")
        materials_template = generated_templates[1]
        json_export = await domain_templates.export_template(
            template_id=materials_template.id,
            format_type="json"
        )
        
        print(f"✅ JSON Export Length: {len(json_export)} characters")
        
        # Parse and show structure
        json_data = json.loads(json_export)
        print("📄 JSON Structure Overview:")
        for key in json_data.keys():
            if isinstance(json_data[key], dict):
                print(f"   📂 {key}: {len(json_data[key])} items")
            elif isinstance(json_data[key], list):
                print(f"   📋 {key}: {len(json_data[key])} items")
            else:
                print(f"   📝 {key}: {type(json_data[key]).__name__}")
        
        # Phase 5: Intelligent Recommendations
        print("\n🎯 Phase 5: Intelligent Template Recommendations")
        print("-" * 50)
        
        # Scenario 1: Protein research with limited budget
        print("🧬 Scenario 1: Protein Research (Limited Budget)")
        recommendations1 = await domain_templates.get_template_recommendations(
            research_goals=[
                "protein structure analysis",
                "molecular dynamics simulation", 
                "computational biology"
            ],
            available_resources={
                "equipment": [
                    "High-performance computing clusters",
                    "GPU workstations",
                    "Standard laboratory computers"
                ],
                "budget": 15000,
                "personnel": 2
            },
            constraints={
                "budget": 15000,
                "timeline_days": 45,
                "complexity_preference": "intermediate"
            }
        )
        
        print(f"📊 Found {len(recommendations1)} relevant templates")
        for i, rec in enumerate(recommendations1[:3], 1):
            print(f"   {i}. {rec['template_name']}")
            print(f"      🎯 Relevance: {rec['relevance_score']:.3f}")
            print(f"      🔬 Domain: {rec['domain']}")
            print(f"      📊 Complexity: {rec['complexity']}")
            print(f"      ⏱️ Duration: {rec['estimated_duration']} days")
            print(f"      💰 Cost: ${rec['estimated_cost']:,.2f}")
            print(f"      ✨ Benefits: {', '.join(rec['key_benefits'])}")
        
        # Scenario 2: Materials research with advanced resources
        print("\n🔬 Scenario 2: Advanced Materials Research")
        recommendations2 = await domain_templates.get_template_recommendations(
            research_goals=[
                "materials synthesis",
                "characterization",
                "advanced materials science"
            ],
            available_resources={
                "equipment": [
                    "X-ray diffractometers",
                    "Electron microscopes",
                    "Furnaces and reactors",
                    "Advanced spectrometers"
                ],
                "budget": 75000,
                "timeline_days": 120
            },
            constraints={
                "budget": 75000,
                "timeline_days": 120,
                "complexity_preference": "expert"
            }
        )
        
        print(f"📊 Found {len(recommendations2)} relevant templates")
        for i, rec in enumerate(recommendations2[:2], 1):
            print(f"   {i}. {rec['template_name']}")
            print(f"      🎯 Relevance: {rec['relevance_score']:.3f}")
            print(f"      🔬 Domain: {rec['domain']}")
            print(f"      📊 Complexity: {rec['complexity']}")
            print(f"      ⏱️ Duration: {rec['estimated_duration']} days")
            print(f"      💰 Cost: ${rec['estimated_cost']:,.2f}")
            print(f"      ✨ Benefits: {', '.join(rec['key_benefits'])}")
        
        # Phase 6: Analytics and Usage Statistics
        print("\n📈 Phase 6: Service Analytics")
        print("-" * 50)
        
        # Update usage stats by accessing some templates
        for template in generated_templates[:2]:
            domain_templates.template_usage_stats[template.id] = domain_templates.template_usage_stats.get(template.id, 0) + 3
        
        # Get updated status with statistics
        final_status = await domain_templates.get_service_status()
        stats = final_status['statistics']
        
        print("📊 Service Statistics:")
        print(f"   📋 Total Templates: {stats['total_templates']}")
        print(f"   🧬 Domains Supported: {stats['domains_supported']}")
        print(f"   🔧 Workflow Steps Library: {stats['workflow_steps_library']}")
        print(f"   📊 Total Usage: {stats['total_template_usage']}")
        print(f"   ✏️ Customizations: {stats['customizations_created']}")
        
        # Show domain distribution
        domain_distribution = {}
        for template in domain_templates.templates.values():
            domain = template.domain.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        print("\n🌐 Domain Distribution:")
        for domain, count in sorted(domain_distribution.items()):
            print(f"   {domain.replace('_', ' ').title()}: {count} templates")
        
        # Phase 7: Advanced Workflow Analysis
        print("\n⚡ Phase 7: Advanced Workflow Analysis")
        print("-" * 50)
        
        # Analyze workflow complexity across templates
        workflow_analysis = {
            "total_steps": 0,
            "step_categories": {},
            "average_duration": 0,
            "common_tools": {}
        }
        
        for template in generated_templates:
            workflow_analysis["total_steps"] += len(template.workflow_steps)
            workflow_analysis["average_duration"] += template.estimated_duration.days
            
            for step in template.workflow_steps:
                category = step.category
                workflow_analysis["step_categories"][category] = workflow_analysis["step_categories"].get(category, 0) + 1
                
                for tool in step.tools_required:
                    workflow_analysis["common_tools"][tool] = workflow_analysis["common_tools"].get(tool, 0) + 1
        
        workflow_analysis["average_duration"] = workflow_analysis["average_duration"] / len(generated_templates)
        
        print("🔬 Workflow Analysis Results:")
        print(f"   ⚡ Total Workflow Steps: {workflow_analysis['total_steps']}")
        print(f"   📊 Average Duration: {workflow_analysis['average_duration']:.1f} days")
        print(f"   📂 Step Categories: {len(workflow_analysis['step_categories'])}")
        
        print("\n📂 Most Common Step Categories:")
        for category, count in sorted(workflow_analysis["step_categories"].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {category.title()}: {count} steps")
        
        print("\n🛠️ Most Common Tools:")
        for tool, count in sorted(workflow_analysis["common_tools"].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {tool}: {count} occurrences")
        
        # Final Summary
        print("\n" + "="*80)
        print("🎉 DOMAIN TEMPLATES GENERATOR DEMONSTRATION COMPLETE")
        print("="*80)
        
        print(f"✅ Templates Generated: {len(generated_templates)}")
        print("✏️ Customizations Applied: 1")
        print("📄 Export Formats: YAML, JSON")
        print(f"🎯 Recommendations Provided: {len(recommendations1) + len(recommendations2)}")
        print("📈 Analytics Generated: Service stats, workflow analysis")
        print(f"🧬 Domains Covered: {len(set(t.domain for t in generated_templates))}")
        print(f"🧪 Experiment Types: {len(set(t.experiment_type for t in generated_templates))}")
        print(f"📊 Complexity Levels: {len(set(t.complexity for t in generated_templates))}")
        
        print("\n🚀 The Domain Templates Generator successfully demonstrated:")
        print("   • Automated generation of domain-specific research templates")
        print("   • Template customization with additional objectives and steps")
        print("   • Multi-format export capabilities (YAML, JSON)")
        print("   • Intelligent recommendations based on research goals and constraints")
        print("   • Comprehensive analytics and usage tracking")
        print("   • Advanced workflow analysis and tool identification")
        print("   • Cost and timeline estimation for research planning")
        
        return {
            "success": True,
            "templates_generated": len(generated_templates),
            "domains_covered": len(set(t.domain for t in generated_templates)),
            "total_workflow_steps": workflow_analysis["total_steps"],
            "recommendations_provided": len(recommendations1) + len(recommendations2),
            "service_status": final_status
        }
        
    except Exception as e:
        print(f"\n❌ Demonstration Error: {str(e)}")
        print(f"📍 Error Details: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

async def demonstrate_domain_templates_api():
    """
    🌐 API Integration Demonstration
    
    Shows how to interact with the Domain Templates service via API endpoints
    """
    print("\n" + "="*80)
    print("🌐 AXIOM Domain Templates Generator - API Integration Demo")
    print("="*80)
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        print("\n📡 Testing API Endpoints")
        print("-" * 40)
        
        # Test service status endpoint
        print("1️⃣ Testing service status...")
        response = client.get("/domain-templates/status")
        assert response.status_code == 200
        status_data = response.json()
        print(f"   ✅ Service: {status_data['service_name']}")
        print(f"   📊 Status: {status_data['status']}")
        
        # Test supported domains endpoint
        print("\n2️⃣ Testing supported domains...")
        response = client.get("/domain-templates/domains")
        assert response.status_code == 200
        domains_data = response.json()
        print(f"   ✅ Domains available: {len(domains_data['domains'])}")
        
        # Test template generation endpoint
        print("\n3️⃣ Testing template generation...")
        response = client.post("/domain-templates/generate", params={
            "domain": "computational_biology",
            "experiment_type": "simulation",
            "complexity": "intermediate"
        })
        assert response.status_code == 200
        template_data = response.json()
        print(f"   ✅ Template generated: {template_data['template_id']}")
        print(f"   📋 Name: {template_data['name']}")
        print(f"   ⚡ Workflow steps: {len(template_data['workflow_steps'])}")
        
        template_id = template_data['template_id']
        
        # Test template details endpoint
        print("\n4️⃣ Testing template details...")
        response = client.get(f"/domain-templates/templates/{template_id}")
        assert response.status_code == 200
        details_data = response.json()
        print("   ✅ Template details retrieved")
        print(f"   💰 Cost: ${details_data['estimates']['cost_usd']:,.2f}")
        print(f"   ⏱️ Duration: {details_data['estimates']['duration_days']} days")
        
        # Test template export endpoint  
        print("\n5️⃣ Testing template export...")
        response = client.get(f"/domain-templates/templates/{template_id}/export?format=yaml")
        assert response.status_code == 200
        export_data = response.json()
        print("   ✅ Template exported in YAML format")
        print(f"   📄 Export size: {len(export_data['content'])} characters")
        
        # Test recommendations endpoint
        print("\n6️⃣ Testing recommendations...")
        recommendations_request = {
            "research_goals": ["computational biology", "molecular simulation"],
            "available_resources": {
                "equipment": ["HPC cluster", "GPU workstation"],
                "budget": 20000
            },
            "constraints": {
                "budget": 20000,
                "timeline_days": 60
            }
        }
        
        response = client.post("/domain-templates/recommendations", json=recommendations_request)
        assert response.status_code == 200
        rec_data = response.json()
        print(f"   ✅ Recommendations received: {len(rec_data['recommendations'])}")
        
        if rec_data['recommendations']:
            top_rec = rec_data['recommendations'][0]
            print(f"   🥇 Top recommendation: {top_rec['template_name']}")
            print(f"   🎯 Relevance score: {top_rec['relevance_score']:.3f}")
        
        print("\n✅ All API endpoints tested successfully!")
        
        return {
            "success": True,
            "endpoints_tested": 6,
            "template_generated": template_id,
            "api_status": "fully_functional"
        }
        
    except Exception as e:
        print(f"\n❌ API Demo Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("🧬 Starting AXIOM Domain Templates Generator Demonstrations...")
    
    # Run service demonstration
    print("\n🚀 Running Service Demonstration...")
    service_results = asyncio.run(demonstrate_domain_templates_generator())
    
    # Run API demonstration
    print("\n\n🌐 Running API Integration Demonstration...")
    api_results = asyncio.run(demonstrate_domain_templates_api())
    
    # Final summary
    print("\n" + "="*80)
    print("📊 COMPLETE DEMONSTRATION SUMMARY")
    print("="*80)
    
    if service_results["success"]:
        print("✅ Service Demonstration: SUCCESS")
        print(f"   📋 Templates Generated: {service_results['templates_generated']}")
        print(f"   🧬 Domains Covered: {service_results['domains_covered']}")
        print(f"   ⚡ Total Workflow Steps: {service_results['total_workflow_steps']}")
        print(f"   🎯 Recommendations: {service_results['recommendations_provided']}")
    else:
        print("❌ Service Demonstration: FAILED")
        print(f"   Error: {service_results['error']}")
    
    if api_results["success"]:
        print("\n✅ API Integration: SUCCESS")
        print(f"   📡 Endpoints Tested: {api_results['endpoints_tested']}")
        print(f"   📋 Template ID: {api_results['template_generated']}")
        print(f"   🌐 API Status: {api_results['api_status']}")
    else:
        print("\n❌ API Integration: FAILED")
        print(f"   Error: {api_results['error']}")
    
    overall_success = service_results["success"] and api_results["success"]
    print(f"\n🏆 OVERALL RESULT: {'SUCCESS' if overall_success else 'PARTIAL/FAILED'}")
    
    if overall_success:
        print("\n🎉 The AXIOM Domain Templates Generator is fully operational!")
        print("🧬 Ready for production use in autonomous laboratory environments.")
    else:
        print("\n⚠️ Some issues detected. Review logs for debugging information.")
