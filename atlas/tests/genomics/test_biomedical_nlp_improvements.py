#!/usr/bin/env python3
"""
Test script for BiomedicalNLPService improvements
"""

import sys
import os
import asyncio

# Mock all the problematic modules
class MockBaseService:
    def __init__(self, service_name=None):
        self.service_name = service_name

class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")

# Mock all modules that cause import issues
sys.modules['app.core.bootstrap_logging'] = type('MockModule', (), {'logger': MockLogger()})()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services'))

async def test_biomedical_nlp_improvements():
    """Test the improved BiomedicalNLPService"""
    print("🧪 Testing BiomedicalNLPService Improvements")
    print("=" * 60)
    
    try:
        # Import the service directly
        from biomedical_nlp_service import BiomedicalNLPService
        
        # Create service instance
        service = BiomedicalNLPService()
        
        print(f"✅ Service created successfully")
        print(f"📊 Version: {service.version}")
        print(f"🔧 Advanced config: {len(service.advanced_config)} parameters")
        
        # Test text for analysis
        test_text = """
        BRCA1 mutations are associated with increased risk of breast cancer. 
        The protein p53 plays a crucial role in DNA repair and tumor suppression.
        CRISPR technology has revolutionized gene editing capabilities.
        """
        
        # Test 1: Entity Extraction
        print("\n🔬 Testing Entity Extraction...")
        entity_result = await service.extract_biomedical_entities(test_text)
        if entity_result['success']:
            entities = entity_result['data']['entities']
            print(f"✅ Entity extraction successful")
            print(f"   Entities found: {len(entities)}")
            print(f"   Methods used: {entity_result['data']['methods_used']}")
            print(f"   Confidence distribution: {entity_result['data']['confidence_distribution']}")
            for entity in entities[:3]:  # Show first 3 entities
                print(f"   - {entity['text']} ({entity['label']}, score: {entity['score']:.3f})")
        else:
            print(f"❌ Entity extraction failed: {entity_result['error']}")
        
        # Test 2: Semantic Similarity
        print("\n🎯 Testing Semantic Similarity...")
        text1 = "BRCA1 mutations cause breast cancer"
        text2 = "Genetic mutations in BRCA1 lead to increased cancer risk"
        similarity_result = await service.calculate_semantic_similarity(text1, text2)
        if similarity_result['success']:
            similarity_data = similarity_result['data']
            print(f"✅ Semantic similarity successful")
            print(f"   Similarity score: {similarity_data['similarity_score']:.3f}")
            print(f"   Relevance level: {similarity_data['relevance_level']}")
            print(f"   Confidence: {similarity_data['confidence']:.3f}")
            if similarity_data['embedding_similarity']:
                print(f"   Embedding similarity: {similarity_data['embedding_similarity']:.3f}")
            if similarity_data['tfidf_similarity']:
                print(f"   TF-IDF similarity: {similarity_data['tfidf_similarity']:.3f}")
        else:
            print(f"❌ Semantic similarity failed: {similarity_result['error']}")
        
        # Test 3: Relation Extraction
        print("\n🔗 Testing Relation Extraction...")
        relation_text = "Aspirin treats inflammation and inhibits COX-2 enzyme"
        relation_result = await service.extract_relations(relation_text)
        if relation_result['success']:
            relations = relation_result['data']['relations']
            print(f"✅ Relation extraction successful")
            print(f"   Relations found: {len(relations)}")
            for relation in relations[:2]:  # Show first 2 relations
                print(f"   - {relation['subject']} {relation['predicate']} {relation['object']} (confidence: {relation['confidence']:.3f})")
        else:
            print(f"❌ Relation extraction failed: {relation_result['error']}")
        
        # Test 4: Topic Modeling
        print("\n📊 Testing Topic Modeling...")
        texts = [
            "Cancer research focuses on understanding tumor biology and developing treatments",
            "Gene therapy uses genetic engineering to treat inherited diseases",
            "Immunotherapy harnesses the immune system to fight cancer cells",
            "CRISPR technology enables precise gene editing for therapeutic applications"
        ]
        topic_result = await service.perform_topic_modeling(texts, num_topics=3)
        if topic_result['success']:
            topic_data = topic_result['data']
            print(f"✅ Topic modeling successful")
            print(f"   Topics found: {len(topic_data['topics'])}")
            print(f"   Coherence score: {topic_data['coherence_score']:.3f}")
            print(f"   Perplexity: {topic_data['perplexity']:.3f}")
            for i, topic in enumerate(topic_data['topics']):
                print(f"   Topic {i}: {', '.join(topic['top_words'])}")
        else:
            print(f"❌ Topic modeling failed: {topic_result['error']}")
        
        # Test 5: Literature Search Enhancement
        print("\n📚 Testing Literature Search Enhancement...")
        query = "BRCA1 breast cancer treatment"
        papers = [
            {"title": "BRCA1 mutations in breast cancer", "abstract": "This study examines BRCA1 mutations and their role in breast cancer development"},
            {"title": "Gene therapy approaches", "abstract": "Novel gene therapy methods for treating genetic diseases"},
            {"title": "Cancer immunotherapy", "abstract": "Immunotherapy strategies for cancer treatment"}
        ]
        search_result = await service.enhance_literature_search(query, papers)
        if search_result['success']:
            enhanced_papers = search_result['data']['enhanced_papers']
            print(f"✅ Literature search enhancement successful")
            print(f"   Papers processed: {len(enhanced_papers)}")
            print(f"   Query entities: {len(search_result['data']['query_entities'])}")
            for i, paper in enumerate(enhanced_papers[:2]):  # Show first 2 papers
                print(f"   Paper {i+1}: {paper['title']}")
                print(f"     Relevance: {paper['relevance_score']:.3f}")
                print(f"     Domain: {paper['research_domain']}")
                print(f"     Entities: {paper['entity_count']}")
        else:
            print(f"❌ Literature search enhancement failed: {search_result['error']}")
        
        # Test 6: Abstract Analysis
        print("\n📄 Testing Abstract Analysis...")
        abstract = """
        This study investigates the role of BRCA1 mutations in breast cancer development. 
        We analyzed 500 patients and found significant associations between BRCA1 variants 
        and increased cancer risk. Our findings suggest that early detection and targeted 
        therapy could improve patient outcomes.
        """
        analysis_result = await service.analyze_paper_abstract(abstract)
        if analysis_result['success']:
            analysis_data = analysis_result['data']
            print(f"✅ Abstract analysis successful")
            print(f"   Entities: {analysis_data['entity_count']}")
            print(f"   Relations: {analysis_data['relation_count']}")
            print(f"   Research domain: {analysis_data['research_domain']}")
            print(f"   Key concepts: {', '.join(analysis_data['key_concepts'][:5])}")
            print(f"   Sentiment: {analysis_data['sentiment_analysis']['overall_sentiment']}")
            print(f"   Readability: {analysis_data['complexity_metrics']['readability_score']:.1f}")
            print(f"   Confidence: {analysis_data['analysis_confidence']:.3f}")
        else:
            print(f"❌ Abstract analysis failed: {analysis_result['error']}")
        
        # Test 7: Health Check
        print("\n🏥 Testing Health Check...")
        health_result = await service.health_check()
        if health_result['service_status'] == 'healthy':
            print(f"✅ Health check successful")
            print(f"   Service status: {health_result['service_status']}")
            print(f"   Model readiness: {health_result['model_readiness']:.1%}")
            print(f"   Capabilities: {len(health_result['capabilities'])}")
            for capability in health_result['capabilities']:
                print(f"     - {capability}")
        else:
            print(f"❌ Health check failed: {health_result.get('error', 'Unknown error')}")
        
        print("\n🎉 Biomedical NLP Service Improvements Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run async test"""
    return asyncio.run(test_biomedical_nlp_improvements())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
