#!/usr/bin/env python3
"""
Test del servicio PubMed simplificado para validar integración con el laboratorio autónomo
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pubmed_service import PubMedService


async def test_pubmed_service():
    print("🧬 Testing PubMed Service for Autonomous Lab")
    print("=" * 60)
    
    pubmed = PubMedService()
    
    try:
        # Test 1: Basic neuroscience search
        print("🔍 Test 1: Neuroscience literature search...")
        result = await pubmed.search_papers(
            query="nanoparticles neural regeneration",
            max_results=5,
            recent_years=3
        )
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Papers found: {result['total_found']}")
            print(f"   Papers retrieved: {len(result['articles'])}")
            print(f"   Evidence score: {result['evidence_score']:.3f}")
            print(f"   Search time: {result['search_time']:.2f}s")
            
            if result['articles']:
                article = result['articles'][0]
                print(f"\n   📚 Example paper:")
                print(f"      PMID: {article.pmid}")
                print(f"      Title: {article.title[:80]}...")
                print(f"      Journal: {article.journal}")
                print(f"      Year: {article.pub_date}")
                print(f"      Authors: {article.authors_count}")
                print(f"      DOI: {article.doi}")
        
        # Test 2: Domain evidence integration
        print(f"\n🔬 Test 2: Domain evidence for neuroscience...")
        domain_result = await pubmed.get_domain_evidence(
            domain="neuroscience",
            hypothesis_keywords=["nanoparticles", "regeneration", "tissue engineering"]
        )
        
        print(f"   Success: {domain_result['success']}")
        if domain_result['success']:
            evidence = domain_result['literature_evidence']
            print(f"   Domain: {domain_result['domain']}")
            print(f"   Papers found: {evidence['papers_found']}")
            print(f"   Evidence strength: {evidence['evidence_strength']:.3f}")
            print(f"   Recent research: {evidence['recent_research']}")
            print(f"   Query: {evidence['query_used']}")
            
            if domain_result['top_papers']:
                print(f"\n   🏆 Top papers:")
                for i, paper in enumerate(domain_result['top_papers'][:3], 1):
                    print(f"      {i}. {paper['title']} ({paper['year']})")
                    print(f"         Journal: {paper['journal']}")
        
        # Test 3: Materials science search
        print(f"\n🧪 Test 3: Materials science domain...")
        materials_result = await pubmed.get_domain_evidence(
            domain="materials_science",
            hypothesis_keywords=["biomaterials", "scaffold", "regeneration"]
        )
        
        print(f"   Success: {materials_result['success']}")
        if materials_result['success']:
            evidence = materials_result['literature_evidence']
            print(f"   Materials papers: {evidence['papers_found']}")
            print(f"   Evidence strength: {evidence['evidence_strength']:.3f}")
            
        # Test 4: Genomics domain
        print(f"\n🧬 Test 4: Genomics domain...")
        genomics_result = await pubmed.get_domain_evidence(
            domain="genomics",
            hypothesis_keywords=["CRISPR", "gene therapy", "neural"]
        )
        
        print(f"   Success: {genomics_result['success']}")
        if genomics_result['success']:
            evidence = genomics_result['literature_evidence']
            print(f"   Genomics papers: {evidence['papers_found']}")
            print(f"   Evidence strength: {evidence['evidence_strength']:.3f}")
        
        print(f"\n✅ All tests completed successfully!")
        print(f"📊 PubMed integration ready for autonomous lab")
    
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")
    
    finally:
        await pubmed.close()
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_pubmed_service())
