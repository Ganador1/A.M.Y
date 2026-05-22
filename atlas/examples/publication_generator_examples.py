"""
Publication Generator Examples - AXIOM META 4
Practical examples demonstrating automated scientific publication generation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.publication_generator import PublicationGeneratorService
from app.logging_config import logger


async def example_basic_publication():
    """Example 1: Generate a basic autonomous research publication"""
    print("\n📝 Example 1: Basic Publication Generation")
    print("-" * 50)
    
    service = PublicationGeneratorService()
    
    request_data = {
        "action": "generate_publication",
        "title": "Autonomous Discovery of Novel Mathematical Patterns",
        "custom_content": {
            "abstract": """This study presents results from an autonomous mathematical discovery system 
                          that identified novel patterns in prime number distributions using advanced 
                          computational techniques and machine learning algorithms.""",
            "domains": ["mathematics", "computational_science", "artificial_intelligence"],
            "keywords": ["autonomous_discovery", "prime_numbers", "pattern_recognition", "ai_mathematics"],
            "authors": ["AXIOM Mathematics Agent", "Autonomous Discovery Team"],
            
            "introduction": """The automation of mathematical discovery represents a frontier in computational 
                              science where artificial intelligence systems can independently identify, formulate, 
                              and validate mathematical hypotheses. This work demonstrates a fully autonomous 
                              system capable of discovering novel mathematical patterns.""",
            
            "experimental_design": """Our autonomous system employed a multi-stage discovery pipeline:
                                     1) Pattern detection using advanced algorithms
                                     2) Hypothesis formulation through symbolic AI
                                     3) Computational verification using distributed computing
                                     4) Cross-validation using multiple mathematical frameworks""",
            
            "primary_findings": """The system successfully identified 12 novel patterns in prime number 
                                  distributions, with validation scores exceeding 0.95 confidence. 
                                  Three patterns showed potential applications in cryptographic algorithms.""",
            
            "interpretation": """These results demonstrate that autonomous systems can conduct meaningful 
                                mathematical research, potentially accelerating discovery in theoretical 
                                and applied mathematics.""",
            
            "conclusions": """This work establishes the feasibility of autonomous mathematical discovery 
                             systems and opens new avenues for AI-assisted theoretical research."""
        }
    }
    
    result = await service.process_request(request_data)
    
    if result["success"]:
        print("Publication generated successfully:")
        print(f"  📄 Title: Autonomous Discovery of Novel Mathematical Patterns")
        print(f"  🆔 ID: {result['pub_id']}")
        print(f"  📊 DOI: {result['doi']}")
        print(f"  📁 Path: {result['package_path']}")
        return result["pub_id"]
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None


async def example_interdisciplinary_publication():
    """Example 2: Generate interdisciplinary research publication"""
    print("\n🌐 Example 2: Interdisciplinary Research Publication")
    print("-" * 50)
    
    service = PublicationGeneratorService()
    
    request_data = {
        "action": "generate_publication",
        "title": "Convergence of AI, Biology, and Materials Science: A Computational Perspective",
        "custom_content": {
            "abstract": """This interdisciplinary study explores the convergence of artificial intelligence, 
                          computational biology, and materials science through autonomous research methodologies. 
                          We demonstrate cross-domain pattern recognition and knowledge transfer across 
                          traditionally separate scientific fields.""",
            
            "domains": ["artificial_intelligence", "computational_biology", "materials_science", "interdisciplinary_research"],
            
            "keywords": [
                "interdisciplinary_ai", "computational_biology", "materials_informatics", 
                "cross_domain_discovery", "autonomous_research", "knowledge_transfer"
            ],
            
            "authors": ["AXIOM Interdisciplinary Agent", "Cross-Domain Research Collective"],
            
            "cross_domain_insights": [
                {
                    "domain_pair": "AI + Biology",
                    "description": "Machine learning patterns in protein folding correlate with neural network optimization strategies"
                },
                {
                    "domain_pair": "Biology + Materials",
                    "description": "Biomimetic principles inform novel materials with adaptive properties"
                },
                {
                    "domain_pair": "Materials + AI", 
                    "description": "Materials discovery algorithms enhance AI hardware design principles"
                }
            ],
            
            "future_directions": [
                "Development of unified computational frameworks spanning multiple disciplines",
                "Creation of cross-domain knowledge graphs for autonomous discovery",
                "Integration of biological, materials, and AI optimization principles",
                "Autonomous hypothesis generation across scientific boundaries"
            ]
        }
    }
    
    result = await service.process_request(request_data)
    
    if result["success"]:
        print("Interdisciplinary publication generated:")
        print(f"  🧬 Domains: AI, Biology, Materials Science")
        print(f"  🆔 ID: {result['pub_id']}")
        print(f"  📊 DOI: {result['doi']}")
        return result["pub_id"]
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None


async def example_validation_focused_publication():
    """Example 3: Generate publication focused on validation methodology"""
    print("\n🔬 Example 3: Validation Methodology Publication") 
    print("-" * 50)
    
    service = PublicationGeneratorService()
    
    # Try to get real validation data
    validation_data = {}
    try:
        from app.operational_cross_validation_matrix import operational_matrix
        validation_services = ["ScientificHypothesisAgent", "LiteratureSearchService", "ResearchCycleManager"]
        validation_run = await operational_matrix.validate_cross_compatibility(validation_services)
        
        validation_data = {
            "aggregate_score": validation_run.aggregate_score,
            "confidence": validation_run.uncertainty_metrics.get("confidence_mean", 0.0),
            "uncertainty": validation_run.uncertainty_metrics.get("uncertainty_mean", 0.0),
            "domains_tested": len(validation_run.individual_scores),
            "individual_results": [
                {
                    "domain": score.domain.value,
                    "score": score.score,
                    "confidence": score.confidence
                } for score in validation_run.individual_scores[:5]
            ]
        }
        print(f"  ✅ Integrated real validation data (score: {validation_run.aggregate_score:.3f})")
        
    except Exception as e:
        print(f"  ⚠️ Using simulated validation data: {e}")
        validation_data = {
            "aggregate_score": 0.89,
            "confidence": 0.92,
            "uncertainty": 0.08,
            "domains_tested": 8,
            "individual_results": [
                {"domain": "computational_science", "score": 0.91, "confidence": 0.94},
                {"domain": "machine_learning", "score": 0.87, "confidence": 0.89},
                {"domain": "data_science", "score": 0.93, "confidence": 0.95}
            ]
        }
    
    request_data = {
        "action": "generate_publication",
        "title": "Multi-Domain Cross-Validation Framework for Autonomous Scientific Research",
        "custom_content": {
            "abstract": f"""We present a comprehensive cross-validation framework achieving 
                           {validation_data['aggregate_score']:.3f} aggregate validation score across 
                           {validation_data['domains_tested']} scientific domains. This framework enables 
                           autonomous validation of research findings with quantified uncertainty.""",
            
            "domains": ["validation_methodology", "computational_science", "research_automation"],
            
            "keywords": [
                "cross_validation", "uncertainty_quantification", "autonomous_validation",
                "multi_domain_research", "scientific_methodology", "research_quality"
            ],
            
            "validation_results": validation_data,
            
            "experimental_design": """Our validation framework employs a multi-tier approach:
                                     1) Service-level validation using operational matrices
                                     2) Cross-domain compatibility testing
                                     3) Uncertainty quantification with statistical modeling
                                     4) Consensus-based validation scoring""",
            
            "primary_findings": f"""The framework achieved {validation_data['aggregate_score']:.3f} 
                               aggregate validation score with {validation_data['confidence']:.3f} 
                               average confidence across all tested domains. Uncertainty quantification 
                               provides ±{validation_data['uncertainty']:.3f} bounds on all results.""",
            
            "significance": """This validation framework enables autonomous research systems to 
                              provide quantified confidence in their findings, addressing a critical 
                              need for trustworthy AI-generated research."""
        }
    }
    
    result = await service.process_request(request_data)
    
    if result["success"]:
        print("Validation methodology publication generated:")
        print(f"  📊 Validation Score: {validation_data['aggregate_score']:.3f}")
        print(f"  🆔 ID: {result['pub_id']}")
        print(f"  📊 DOI: {result['doi']}")
        return result["pub_id"]
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None


async def example_hypothesis_driven_publication():
    """Example 4: Generate publication from hypothesis persistence system"""
    print("\n💡 Example 4: Hypothesis-Driven Publication")
    print("-" * 50)
    
    service = PublicationGeneratorService()
    
    # Simulate hypothesis data (in real system, this would come from hypothesis persistence)
    hypothesis_id = "hyp_" + "example_001"
    
    request_data = {
        "action": "generate_publication",
        "hypothesis_id": hypothesis_id,
        "title": "AI-Discovered Correlations in Climate-Energy Systems",
        "custom_content": {
            "abstract": """An autonomous AI system generated and validated the hypothesis that 
                          renewable energy adoption patterns correlate with regional climate variability 
                          through previously unknown feedback mechanisms.""",
            
            "domains": ["climate_science", "energy_systems", "artificial_intelligence"],
            
            "keywords": [
                "climate_energy_correlation", "ai_hypothesis", "renewable_energy",
                "autonomous_discovery", "system_dynamics", "feedback_mechanisms"
            ],
            
            "hypothesis_background": f"""Hypothesis {hypothesis_id} was autonomously generated 
                                       by analyzing large-scale climate and energy datasets. 
                                       The AI system identified potential correlations that had 
                                       not been previously investigated in the literature.""",
            
            "hypothesis_validation": {
                "status": "validated",
                "confidence": 0.87,
                "evidence_strength": 0.82,
                "assessment": """Statistical analysis confirmed the hypothesized correlation 
                                with p < 0.001 across multiple regional datasets.""",
                "supporting_evidence": [
                    "Regional energy transition data shows 0.78 correlation with climate variability",
                    "Machine learning models predict energy adoption with 0.87 accuracy using climate features",
                    "Cross-validation across 15 geographic regions confirms relationship stability"
                ],
                "limitations": [
                    "Analysis limited to regions with complete data availability",
                    "Temporal scope restricted to 2010-2023 period",
                    "Causal mechanisms require further investigation"
                ]
            }
        }
    }
    
    result = await service.process_request(request_data)
    
    if result["success"]:
        print("Hypothesis-driven publication generated:")
        print(f"  💡 Hypothesis ID: {hypothesis_id}")
        print(f"  ✅ Status: Validated (87% confidence)")
        print(f"  🆔 ID: {result['pub_id']}")
        print(f"  📊 DOI: {result['doi']}")
        return result["pub_id"]
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        return None


async def demo_publication_management():
    """Demo: Publication management operations"""
    print("\n📚 Demo: Publication Management Operations")
    print("-" * 50)
    
    service = PublicationGeneratorService()
    
    # List all publications
    list_result = await service.process_request({"action": "list_publications"})
    
    if list_result["success"]:
        publications = list_result["publications"]
        print(f"📋 Found {len(publications)} total publications")
        
        if publications:
            print("\nRecent publications:")
            for pub in publications[:3]:
                print(f"  📄 {pub['title'][:60]}...")
                print(f"     DOI: {pub['doi']} | Domains: {', '.join(pub['domains'][:2])}")
                print(f"     Created: {pub['created_at'][:10]} | Score: {pub['consensus_score']:.3f}")
                
                # Validate this publication
                val_result = await service.process_request({
                    "action": "validate_publication",
                    "pub_id": pub["pub_id"]
                })
                
                if val_result["success"]:
                    validation = val_result["validation"]
                    status = "✅ Valid" if validation["hash_valid"] else "⚠️ Invalid"
                    blockchain = "🔐 Verified" if validation["blockchain_valid"] else "🔓 Unverified"
                    print(f"     {status} | {blockchain}")
                print()
    else:
        print("❌ Could not retrieve publication list")


async def run_publication_examples():
    """Run all publication generation examples"""
    print("🚀 AXIOM META 4 - Publication Generator Examples")
    print("=" * 60)
    
    # Run examples
    examples = [
        example_basic_publication,
        example_interdisciplinary_publication, 
        example_validation_focused_publication,
        example_hypothesis_driven_publication
    ]
    
    generated_pubs = []
    
    for example in examples:
        try:
            pub_id = await example()
            if pub_id:
                generated_pubs.append(pub_id)
        except Exception as e:
            print(f"❌ Example {example.__name__} failed: {e}")
            logger.error(f"Example failed: {example.__name__}", exc_info=True)
    
    # Demo management operations
    await demo_publication_management()
    
    print("=" * 60)
    print(f"✅ Generated {len(generated_pubs)} example publications")
    print("🎉 Publication system examples completed!")
    
    return len(generated_pubs) > 0


if __name__ == "__main__":
    success = asyncio.run(run_publication_examples())
    sys.exit(0 if success else 1)
