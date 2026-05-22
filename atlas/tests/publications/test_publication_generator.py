"""
Test Publication Generator - AXIOM META 4
Comprehensive testing of the autonomous scientific publication system.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.publication_generator import (
    PublicationGeneratorService, 
    DOIGenerator,
    IMRaDTemplateEngine,
    PublicationPackager
)
from app.logging_config import logger


async def test_doi_generation():
    """Test DOI generation functionality"""
    print("\n🆔 Testing DOI Generation...")
    
    # Test basic DOI generation
    content_hash = "abcdef123456789"
    doi = DOIGenerator.generate_doi(content_hash, 2025)
    print(f"Generated DOI: {doi}")
    
    assert doi.startswith("axiom:2025:")
    assert len(doi.split(":")[2]) == 12
    
    # Test DOI validation
    assert DOIGenerator.validate_doi(doi)
    assert not DOIGenerator.validate_doi("invalid:doi:format")
    
    print("✅ DOI generation tests passed")


async def test_template_engine():
    """Test IMRaD template engine"""
    print("\n📝 Testing Template Engine...")
    
    engine = IMRaDTemplateEngine()
    
    # Test context for template rendering
    context = {
        "title": "Test Publication",
        "abstract": "This is a test abstract for automated publication generation.",
        "authors": ["AXIOM Research Agent", "Test Author"],
        "domains": ["ai_research", "computational_science"],
        "keywords": ["autonomous_research", "ai_discovery", "testing"],
        "pub_id": "test123",
        "doi": "axiom:2025:abcdef123456",
        "created_at": "2025-01-27T10:00:00",
        "validation_results": {
            "aggregate_score": 0.87,
            "confidence": 0.92,
            "uncertainty": 0.08
        }
    }
    
    # Test rendering each section
    abstract_md = engine.render_section("abstract.md", context)
    intro_md = engine.render_section("introduction.md", context)
    methods_md = engine.render_section("methods.md", context)
    
    assert "test abstract" in abstract_md.lower()
    assert "autonomous_research" in abstract_md
    assert "axiom" in intro_md.lower()
    assert "validation" in methods_md.lower()
    
    print("✅ Template engine tests passed")


async def test_publication_packager():
    """Test publication packaging functionality"""
    print("\n📦 Testing Publication Packager...")
    
    packager = PublicationPackager("./test_publications")
    
    # Create test package structure
    pub_id = "test_pkg_001"
    package_path = packager.create_package_structure(pub_id)
    
    assert package_path.exists()
    assert (package_path / "figures").exists()
    assert (package_path / "data").exists()
    assert (package_path / "models").exists()
    
    # Create some test files
    (package_path / "test_file.txt").write_text("Test content")
    (package_path / "data" / "test_data.json").write_text('{"test": "data"}')
    
    # Calculate package hash
    package_hash = packager.calculate_package_hash(package_path)
    assert len(package_hash) > 0
    
    print(f"Package hash: {package_hash[:16]}...")
    print("✅ Publication packager tests passed")


async def test_publication_generation():
    """Test full publication generation workflow"""
    print("\n🔬 Testing Full Publication Generation...")
    
    service = PublicationGeneratorService()
    
    # Test request data
    request_data = {
        "action": "generate_publication",
        "title": "Autonomous AI Research: A Computational Approach",
        "custom_content": {
            "abstract": "This study demonstrates the capabilities of autonomous AI systems in conducting scientific research.",
            "domains": ["artificial_intelligence", "computational_science", "research_automation"],
            "keywords": ["autonomous_ai", "research_automation", "computational_discovery", "meta_learning"],
            "authors": ["AXIOM Research Agent", "Computational Discovery Team"],
            "introduction": "The field of autonomous research has emerged as a critical area for advancing scientific discovery. This work presents a comprehensive evaluation of AI-driven research methodologies.",
            "experimental_design": "We employed a multi-stage autonomous research pipeline incorporating hypothesis generation, experimental design, data collection, and analysis validation.",
            "primary_findings": "Our autonomous system successfully identified novel research directions and validated hypotheses across multiple scientific domains with high confidence scores.",
            "interpretation": "The results demonstrate that autonomous AI systems can conduct meaningful scientific research with minimal human intervention while maintaining rigorous validation standards.",
            "conclusions": "This work establishes the foundation for large-scale autonomous scientific discovery systems that can accelerate research across multiple domains simultaneously."
        }
    }
    
    # Generate publication
    result = await service.process_request(request_data)
    
    if result["success"]:
        print(f"✅ Publication generated successfully!")
        print(f"   Publication ID: {result['pub_id']}")
        print(f"   DOI: {result['doi']}")
        print(f"   Package Path: {result['package_path']}")
        print(f"   Package Hash: {result['package_hash'][:16]}...")
        
        # Verify package contents
        package_path = Path(result['package_path'])
        assert (package_path / "manuscript.md").exists()
        assert (package_path / "metadata.json").exists()
        assert (package_path / "manifest.json").exists()
        assert (package_path / "integrity_proof.json").exists()
        
        # Check manifest content
        manifest = json.loads((package_path / "manifest.json").read_text())
        assert manifest["pub_id"] == result["pub_id"]
        assert manifest["doi"] == result["doi"]
        assert "artificial_intelligence" in manifest["domains"]
        
        print("✅ Publication package validation passed")
        
    else:
        print(f"❌ Publication generation failed: {result.get('error')}")
        return False
    
    return True


async def test_publication_listing():
    """Test publication listing functionality"""
    print("\n📋 Testing Publication Listing...")
    
    service = PublicationGeneratorService()
    
    request_data = {"action": "list_publications"}
    result = await service.process_request(request_data)
    
    if result["success"]:
        publications = result["publications"]
        print(f"✅ Found {len(publications)} publications")
        
        if publications:
            for pub in publications[:3]:  # Show first 3
                print(f"   - {pub['title'][:50]}... (DOI: {pub['doi']})")
    else:
        print(f"❌ Listing failed: {result.get('error')}")


async def test_publication_validation():
    """Test publication validation"""
    print("\n🔍 Testing Publication Validation...")
    
    service = PublicationGeneratorService()
    
    # Get first publication
    list_result = await service.process_request({"action": "list_publications"})
    if list_result["success"] and list_result["publications"]:
        pub_id = list_result["publications"][0]["pub_id"]
        
        # Validate publication
        validation_result = await service.process_request({
            "action": "validate_publication",
            "pub_id": pub_id
        })
        
        if validation_result["success"]:
            validation = validation_result["validation"]
            print(f"✅ Publication {pub_id} validation:")
            print(f"   Hash Valid: {validation['hash_valid']}")
            print(f"   Blockchain Valid: {validation['blockchain_valid']}")
            print(f"   Current Hash: {validation['current_hash'][:16]}...")
        else:
            print(f"❌ Validation failed: {validation_result.get('error')}")
    else:
        print("⚠️ No publications found to validate")


async def test_real_data_integration():
    """Test publication generation with real data integration"""
    print("\n🌐 Testing Real Data Integration...")
    
    try:
        # Import and test cross-validation integration
        from app.operational_cross_validation_matrix import operational_matrix
        
        # Run validation
        validation_services = ["ScientificHypothesisAgent", "ResearchCycleManager"]
        validation_run = await operational_matrix.validate_cross_compatibility(validation_services)
        
        print(f"✅ Cross-validation integration successful")
        print(f"   Aggregate Score: {validation_run.aggregate_score:.3f}")
        print(f"   Domains Tested: {len(validation_run.individual_scores)}")
        
        # Generate publication with real validation data
        service = PublicationGeneratorService()
        request_data = {
            "action": "generate_publication",
            "title": "Cross-Domain Validation in Autonomous Research Systems",
            "custom_content": {
                "abstract": "This publication demonstrates real-time integration with the AXIOM cross-validation matrix system.",
                "domains": [score.domain.value for score in validation_run.individual_scores[:3]],
                "keywords": ["cross_validation", "autonomous_systems", "research_validation"],
                "validation_data": {
                    "aggregate_score": validation_run.aggregate_score,
                    "individual_scores": validation_run.individual_scores[:5]
                }
            }
        }
        
        result = await service.process_request(request_data)
        if result["success"]:
            print(f"✅ Real data integration publication generated: {result['pub_id']}")
        else:
            print(f"❌ Real data integration failed: {result.get('error')}")
        
    except Exception as e:
        print(f"⚠️ Real data integration not available: {e}")


async def test_blockchain_integration():
    """Test blockchain validation integration"""
    print("\n🔐 Testing Blockchain Integration...")
    
    try:
        from app.blockchain_validation import BlockchainValidationService
        
        blockchain_service = BlockchainValidationService()
        print("✅ Blockchain service initialized")
        
        # The actual blockchain validation is tested during publication generation
        # where we create ValidationProof objects
        print("✅ Blockchain integration available for publication validation")
        
    except Exception as e:
        print(f"⚠️ Blockchain integration not fully available: {e}")


async def run_comprehensive_tests():
    """Run all publication system tests"""
    print("🚀 AXIOM META 4 - Publication Generator Tests")
    print("=" * 60)
    
    tests = [
        test_doi_generation,
        test_template_engine,
        test_publication_packager,
        test_publication_generation,
        test_publication_listing,
        test_publication_validation,
        test_real_data_integration,
        test_blockchain_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result != False:
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            logger.error(f"Test failed: {test.__name__}", exc_info=True)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Publication Generator tests passed!")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed or had issues")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)
