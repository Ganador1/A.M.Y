#!/usr/bin/env python3
"""
Quick Benchmark: Compare Ollama Cloud Models for Math Research
==============================================================
Single iteration per model, focused on speed and quality comparison.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, "/Volumes/Ganador disk/atlas")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODELS = [
    "gemini-3-flash-preview:cloud",
    "minimax-m2.1:cloud", 
    "glm-4.7:cloud",
    "deepseek-v3.2:cloud",
]


async def quick_test_model(model_name: str) -> dict:
    """Quick single-iteration test."""
    from app.services.llm_providers.ollama_provider import ollama_provider
    from app.services.verification.autonomous_peer_review_service import AutonomousPeerReviewService, ScientificDomain
    
    print(f"\n{'='*60}")
    print(f"🧪 MODEL: {model_name}")
    print(f"{'='*60}")
    
    start = time.time()
    
    # TEST 1: Hypothesis Generation Quality
    prompt = """Generate a mathematical hypothesis about prime number gaps in JSON format:
{
  "title": "A specific, testable conjecture title",
  "statement": "The mathematical statement with precise notation",
  "variables": ["list of variables"],
  "assumptions": ["list of mathematical assumptions"],
  "expected_outcome": "What the conjecture predicts"
}"""
    
    try:
        result = await ollama_provider.generate_async(
            prompt=prompt,
            model=model_name,
            max_tokens=800,
            temperature=0.7
        )
        
        hypothesis_text = result.get("text", "")
        hypothesis_quality = len(hypothesis_text)
        
        # Try to parse JSON
        try:
            import re
            json_match = re.search(r'\{.*\}', hypothesis_text, re.DOTALL)
            if json_match:
                hypothesis_json = json.loads(json_match.group())
                has_valid_json = True
                title = hypothesis_json.get("title", "")[:50]
            else:
                has_valid_json = False
                title = hypothesis_text[:50]
        except:
            has_valid_json = False
            title = hypothesis_text[:50]
        
        gen_time = time.time() - start
        
        # TEST 2: Peer Review Score
        peer_review = AutonomousPeerReviewService()
        review_start = time.time()
        
        review = await peer_review._simulate_peer_review(
            agent_name="math_reviewer",
            agent_config={"domain": ScientificDomain.MATHEMATICS},
            experiment_id=f"test_{model_name.replace(':', '_')}",
            hypothesis=hypothesis_text[:500],
            methodology="Computational verification and statistical analysis",
            results={"sample_size": 10000}
        )
        
        review_time = time.time() - review_start
        total_time = time.time() - start
        
        return {
            "model": model_name,
            "success": True,
            "hypothesis_length": hypothesis_quality,
            "has_valid_json": has_valid_json,
            "title_preview": title,
            "generation_time": round(gen_time, 2),
            "peer_review_score": review.overall_score,
            "scientific_validity": review.scientific_validity,
            "methodological_rigor": review.methodological_rigor,
            "novelty": review.novelty_contribution,
            "approved": review.approved,
            "total_time": round(total_time, 2)
        }
        
    except Exception as e:
        return {
            "model": model_name,
            "success": False,
            "error": str(e),
            "total_time": round(time.time() - start, 2)
        }


async def main():
    print("="*60)
    print("🔬 QUICK OLLAMA MODEL BENCHMARK FOR MATHEMATICS")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("="*60)
    
    results = []
    
    for model in MODELS:
        result = await quick_test_model(model)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Score: {result['peer_review_score']:.2f}")
            print(f"   📊 Validity: {result['scientific_validity']:.2f}")
            print(f"   ⏱️  Time: {result['total_time']}s")
        else:
            print(f"   ❌ Error: {result['error']}")
        
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("📊 BENCHMARK SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    if successful:
        best = max(successful, key=lambda x: x["peer_review_score"])
        fastest = min(successful, key=lambda x: x["total_time"])
        
        print(f"\n{'Model':<35} {'Score':<8} {'Valid.':<8} {'Time':<8}")
        print("-"*60)
        for r in results:
            if r["success"]:
                marker = "🏆" if r["model"] == best["model"] else "  "
                print(f"{marker}{r['model']:<33} {r['peer_review_score']:<8.2f} {r['scientific_validity']:<8.2f} {r['total_time']:<8.1f}s")
            else:
                print(f"❌ {r['model']:<33} FAILED")
        
        print("-"*60)
        print(f"\n🏆 BEST QUALITY: {best['model']} (Score: {best['peer_review_score']:.2f})")
        print(f"⚡ FASTEST: {fastest['model']} (Time: {fastest['total_time']}s)")
    
    # Save
    with open("/Volumes/Ganador disk/atlas/artifacts/quick_benchmark_results.json", "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, indent=2)
    
    print(f"\n📁 Results saved to artifacts/quick_benchmark_results.json")


if __name__ == "__main__":
    asyncio.run(main())
