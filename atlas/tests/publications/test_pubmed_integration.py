#!/usr/bin/env python3
"""
Test de integración con PubMed para validar acceso a literatura científica real
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pubmed_integration_service import PubMedIntegrationService


async def test_pubmed_integration():
    print("🧬 Testing PubMed Integration Service")
    print("=" * 60)
    
    pubmed = PubMedIntegrationService()
    
    try:
        # Test 1: Search for neuroscience papers
        print("🔍 Test 1: Searching neuroscience papers...")
        result = await pubmed.search_papers(
            query="nanoparticles neural regeneration",
            max_results=5,
            publication_years=(2020, 2024)
        )
        
        print(f"   Success: {result.success}")
        print(f"   Total results available: {result.total_results}")
        print(f"   Articles retrieved: {len(result.articles)}")
        print(f"   Search time: {result.search_time:.2f}s")
        
        if result.success and result.articles:
            print(f"\n📚 First article example:")
            article = result.articles[0]
            print(f"   PMID: {article.pmid}")
            print(f"   Title: {article.title[:100]}...")
            print(f"   Journal: {article.journal}")
            print(f"   Authors: {', '.join(article.authors[:3])}...")
            print(f"   Publication: {article.pub_date}")
            print(f"   DOI: {article.doi}")
            print(f"   Keywords: {len(article.keywords or [])}")
            print(f"   MeSH terms: {len(article.mesh_terms or [])}")
            print(f"   Abstract length: {len(article.abstract)} chars")
            
            # Test 2: Get related papers
            print(f"\n🔗 Test 2: Finding related papers to PMID {article.pmid}...")
            related = await pubmed.get_related_papers(article.pmid, max_results=3)
            print(f"   Related papers found: {len(related)}")
            
            if related:
                for i, rel_article in enumerate(related[:2], 1):
                    print(f"   {i}. {rel_article.title[:80]}...")
        
        # Test 3: Research trends analysis
        print(f"\n📈 Test 3: Analyzing neuroscience research trends...")
        trends = await pubmed.extract_research_trends("neuroscience", years_range=3)
        
        if trends.get("success"):
            print(f"   Domain: {trends['domain']}")
            print(f"   Papers analyzed: {trends['total_papers']}")
            print(f"   Time range: {trends['time_range']}")
            print(f"   Growth trend: {trends['growth_trend']}")
            
            if trends.get("top_journals"):
                print(f"\n   🏆 Top journals:")
                for journal, count in trends["top_journals"][:3]:
                    print(f"      • {journal}: {count} papers")
            
            if trends.get("top_keywords"):
                print(f"\n   🔑 Top keywords:")
                for keyword, count in trends["top_keywords"][:5]:
                    print(f"      • {keyword}: {count}")
        else:
            print(f"   ❌ Trends analysis failed: {trends.get('error')}")
        
        # Test 4: Materials science search
        print(f"\n🧪 Test 4: Materials science search...")
        materials_result = await pubmed.search_papers(
            query="biomaterials tissue engineering",
            max_results=3,
            publication_years=(2022, 2024)
        )
        
        print(f"   Success: {materials_result.success}")
        print(f"   Materials papers found: {len(materials_result.articles)}")
        
        if materials_result.articles:
            for i, article in enumerate(materials_result.articles, 1):
                print(f"   {i}. {article.title[:70]}...")
    
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")
    
    finally:
        await pubmed.close()
    
    print("=" * 60)
    print("✅ PubMed integration test completed")


if __name__ == "__main__":
    asyncio.run(test_pubmed_integration())
