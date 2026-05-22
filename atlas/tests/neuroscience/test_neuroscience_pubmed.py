#!/usr/bin/env python3
"""
Test directo del ToolEvidenceOrchestrator para validar integración con PubMed
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService


async def test_neuroscience_tools_with_pubmed():
    print("🧪 Testing ToolEvidenceOrchestrator with PubMed integration")
    print("=" * 65)
    
    orchestrator = ToolEvidenceOrchestratorService()
    
    # Mock hypothesis for neuroscience
    hypothesis = {
        "title": "Nanoparticle Functionalization for Neural Tissue Regeneration",
        "description": "Testing if functionalized nanoparticles improve neural tissue regeneration",
        "domain": "neuroscience",
        "variables": ["nanoparticle_concentration", "growth_factors", "neural_survival"],
        "assumptions": ["biocompatible nanoparticles", "controlled delivery"],
        "expected_outcome": "Improved neural cell survival and growth"
    }
    
    print(f"📋 Hypothesis: {hypothesis['title']}")
    print(f"🔬 Domain: {hypothesis['domain']}")
    print(f"🔧 Variables: {', '.join(hypothesis['variables'])}")
    
    print("\n🚀 Executing corroboration with PubMed integration...")
    
    try:
        result = await orchestrator.process_request({
            "action": "corroborate",
            "hypothesis": hypothesis,
            "domain": "neuroscience"
        })
        
        print(f"\n📊 RESULTS:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            evidence_items = result.get('evidence_items', [])
            aggregate = result.get('aggregate', {})
            
            print(f"   Evidence Items: {len(evidence_items)}")
            print(f"   Coverage: {aggregate.get('coverage', 0):.3f}")
            print(f"   Support Score: {aggregate.get('support_score', 0):.3f}")
            print(f"   Diversity: {aggregate.get('diversity', 0):.3f}")
            
            print(f"\n🛠️ TOOL EXECUTION DETAILS:")
            pubmed_found = False
            for i, item in enumerate(evidence_items, 1):
                status = "✅" if item.get('success') else "❌"
                source = item.get('source', 'Unknown')
                operation = item.get('operation', 'Unknown')
                signal = item.get('signal_strength', 0)
                duration = item.get('duration_seconds', 0)
                
                if source == "PubMedService":
                    pubmed_found = True
                    print(f"   🧬 {i}. PUBMED: {source}.{operation}")
                else:
                    print(f"   {status} {i}. {source}.{operation}")
                    
                print(f"      Signal: {signal:.3f}, Duration: {duration:.2f}s")
                
                # Show PubMed specific results
                if source == "PubMedService" and item.get('success'):
                    raw = item.get('raw_result', {})
                    if raw.get('literature_evidence'):
                        lit_ev = raw['literature_evidence']
                        print(f"      📚 Papers found: {lit_ev.get('papers_found', 0)}")
                        print(f"      🎯 Evidence strength: {lit_ev.get('evidence_strength', 0):.3f}")
                        print(f"      🔬 Recent research: {lit_ev.get('recent_research', False)}")
                
                if not item.get('success'):
                    error = item.get('error', 'Unknown error')
                    raw_error = item.get('raw_result', {}).get('error', None)
                    if raw_error:
                        error = raw_error
                    print(f"      Error: {error}")
            
            if pubmed_found:
                print(f"\n🎉 SUCCESS: PubMed integration is working!")
            else:
                print(f"\n⚠️ PubMed not found in results - may need investigation")
        else:
            error = result.get('error', 'Unknown error')
            print(f"   Error: {error}")
    
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
    
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_neuroscience_tools_with_pubmed())
