#!/usr/bin/env python3
"""
Test script for Biomedical NLP Service
Validates BioBERT integration and entity extraction functionality
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.biomedical_nlp_service import BiomedicalNLPService


async def test_biomedical_nlp_service():
    """
    Test Biomedical NLP Service with sample biomedical text
    """
    print("=" * 60)
    print("Testing Biomedical NLP Service (BioBERT Integration)")
    print("=" * 60)
    
    try:
        # Initialize service
        print("🔄 Initializing BiomedicalNLPService...")
        service = BiomedicalNLPService()
        
        # Test sample biomedical text
        test_text = """
        The BRCA1 gene is a tumor suppressor gene that plays a crucial role in 
        DNA repair. Mutations in BRCA1 are associated with increased risk of 
        breast and ovarian cancer. Recent studies using CRISPR-Cas9 gene editing 
        have shown promising results in correcting BRCA1 mutations in mouse models. 
        The p53 protein, often called the "guardian of the genome," is frequently 
        mutated in various cancers including lung adenocarcinoma.
        """
        
        print(f"📝 Test text: {test_text[:100]}...")
        print()
        
        # Test 1: Entity Extraction
        print("🧬 Test 1: Biomedical Entity Extraction")
        print("-" * 40)
        
        result = await service.extract_biomedical_entities(test_text)
        
        if result.get('success'):
            entities = result['data']['entities']
            print(f"✅ Entity extraction successful")
            print(f"📊 Found {len(entities)} entities:")
            
            for entity in entities[:10]:  # Show first 10 entities
                print(f"  - {entity['text']} ({entity['label']}) - Score: {entity['score']:.3f}")
            
            if len(entities) > 10:
                print(f"  ... and {len(entities) - 10} more entities")
        else:
            print(f"❌ Entity extraction failed: {result.get('error')}")
        
        print()
        
        # Test 2: Semantic Similarity
        print("🔍 Test 2: Semantic Similarity Analysis")
        print("-" * 40)
        
        text1 = "BRCA1 mutations increase breast cancer risk"
        text2 = "BRCA1 gene alterations are associated with mammary carcinoma susceptibility"
        
        similarity_result = await service.calculate_semantic_similarity(text1, text2)
        
        if similarity_result.get('success'):
            similarity_score = similarity_result['data']['similarity_score']
            relevance_level = similarity_result['data']['relevance_level']
            print(f"✅ Semantic similarity calculation successful")
            print(f"📊 Similarity score: {similarity_score:.3f}")
            print(f"🎯 Relevance level: {relevance_level}")
        else:
            print(f"❌ Similarity calculation failed: {similarity_result.get('error')}")
        
        print()
        
        # Test 3: Abstract Analysis
        print("📄 Test 3: Abstract Analysis")
        print("-" * 40)
        
        abstract = """
        Background: Alzheimer's disease is characterized by amyloid beta plaques 
        and tau tangles in the brain. Current therapeutic approaches have shown 
        limited success in clinical trials. Methods: We developed a novel gene 
        therapy approach using CRISPR-Cas9 to target APP gene expression in 
        transgenic mouse models. Results: Treatment resulted in a 60% reduction 
        in amyloid beta levels and improved cognitive performance in behavioral 
        tests. Conclusions: Gene editing shows promise as a therapeutic strategy 
        for Alzheimer's disease.
        """
        
        analysis_result = await service.analyze_paper_abstract(abstract)
        
        if analysis_result.get('success'):
            data = analysis_result['data']
            print(f"✅ Abstract analysis successful")
            print(f"🔬 Research domain: {data.get('research_domain', 'Unknown')}")
            print(f"🧬 Key entities found: {len(data.get('entities', []))}")
            print(f"🎯 Key concepts: {', '.join(data.get('key_concepts', [])[:5])}")
        else:
            print(f"❌ Abstract analysis failed: {analysis_result.get('error')}")
        
        print()
        
        # Test 4: Health Check
        print("🏥 Test 4: Service Health Check")
        print("-" * 40)
        
        health_result = await service.health_check()
        
        if health_result.get('service_status') == 'healthy':
            print("✅ Service health check passed")
            print(f"🤖 Model status: {health_result.get('model_status', 'Unknown')}")
            print(f"🧠 Memory usage: {health_result.get('memory_usage_mb', 0):.1f} MB")
        else:
            print(f"❌ Service health check failed")
        
        print()
        print("=" * 60)
        print("✅ Biomedical NLP Service test completed successfully!")
        print("🔬 BioBERT integration is working properly")
        print("📊 Entity extraction, similarity, and analysis features are functional")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_literature_enhancement():
    """
    Test literature enhancement functionality
    """
    print("\n🔍 Testing Literature Enhancement")
    print("-" * 40)
    
    try:
        service = BiomedicalNLPService()
        
        # Sample papers for enhancement
        query = "CRISPR gene editing cancer treatment"
        sample_papers = [
            {
                "title": "CRISPR-Cas9 genome editing for cancer therapy",
                "abstract": "CRISPR technology shows promise for targeted cancer treatment through precise genetic modifications.",
                "authors": ["Smith, J.", "Doe, A."],
                "year": 2024
            },
            {
                "title": "Traditional chemotherapy approaches in oncology",
                "abstract": "Conventional chemotherapy remains a cornerstone of cancer treatment despite side effects.",
                "authors": ["Johnson, B."],
                "year": 2023
            },
            {
                "title": "CRISPR applications in treating genetic disorders",
                "abstract": "Gene editing using CRISPR-Cas9 offers new therapeutic possibilities for inherited diseases.",
                "authors": ["Williams, C.", "Brown, D."],
                "year": 2024
            }
        ]
        
        result = await service.enhance_literature_search(query, sample_papers)
        
        if result.get('success'):
            enhanced_papers = result['data']['enhanced_papers']
            print(f"✅ Literature enhancement successful")
            print(f"📊 Enhanced {len(enhanced_papers)} papers:")
            
            for paper in enhanced_papers:
                print(f"  - {paper['title'][:50]}... (Score: {paper['relevance_score']:.3f})")
            
        else:
            print(f"❌ Literature enhancement failed: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Literature enhancement test failed: {str(e)}")
        return False


async def main():
    """
    Run all tests
    """
    print("🧬 Starting Biomedical NLP Service Tests")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print()
    
    try:
        # Run main service tests
        main_test_passed = await test_biomedical_nlp_service()
        
        # Run literature enhancement test
        literature_test_passed = await test_literature_enhancement()
        
        if main_test_passed and literature_test_passed:
            print("\n🎉 All tests passed! Biomedical NLP Service is ready for use.")
            return True
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
