#!/usr/bin/env python3
"""
Benchmark de Modelos Ollama Cloud para Investigación Matemática Autónoma
=========================================================================

Compara el rendimiento de diferentes modelos LLM en tareas de investigación
matemática usando el pipeline autónomo de ATLAS.

Modelos a probar:
- gemini-3-flash-preview:cloud
- minimax-m2.1:cloud
- glm-4.7:cloud
- deepseek-v3.2:cloud
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Setup path
sys.path.insert(0, "/Volumes/Ganador disk/atlas")
os.environ["PYTHONPATH"] = "/Volumes/Ganador disk/atlas"

# Suppress some warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODELS_TO_TEST = [
    "gemini-3-flash-preview:cloud",
    "minimax-m2.1:cloud",
    "glm-4.7:cloud",
    "deepseek-v3.2:cloud",
]

MATH_TOPIC = "prime gap patterns and their distribution"
MAX_ITERATIONS = 1  # Quick test per model


async def run_single_model_test(model_name: str) -> dict:
    """Run a single model test and return results."""
    from app.run_agent_with_tools_legacy import autonomous_research_agent
    
    print(f"\n{'='*70}")
    print(f"🧪 TESTING MODEL: {model_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        result = await autonomous_research_agent(
            domain="mathematics",
            topic=MATH_TOPIC,
            max_iterations=MAX_ITERATIONS,
            target_score=7,  # Lower target for quick test
            model_name=model_name
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        return {
            "model": model_name,
            "status": result.get("status", "unknown"),
            "final_score": result.get("final_score", 0),
            "iterations_used": result.get("iterations_used", 0),
            "elapsed_seconds": round(elapsed, 2),
            "success": True,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        return {
            "model": model_name,
            "status": "error",
            "final_score": 0,
            "iterations_used": 0,
            "elapsed_seconds": round(end_time - start_time, 2),
            "success": False,
            "error": str(e)
        }


async def main():
    """Run benchmark across all models."""
    print("="*70)
    print("🔬 ATLAS MATH RESEARCH BENCHMARK - OLLAMA CLOUD MODELS")
    print(f"📅 {datetime.now().isoformat()}")
    print(f"📝 Topic: {MATH_TOPIC}")
    print(f"🔄 Iterations per model: {MAX_ITERATIONS}")
    print("="*70)
    
    results = []
    
    for model in MODELS_TO_TEST:
        result = await run_single_model_test(model)
        results.append(result)
        
        # Brief pause between models
        print(f"\n⏸️  Pausing before next model...")
        await asyncio.sleep(2)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("="*70)
    
    print(f"\n{'Model':<35} {'Score':<8} {'Time (s)':<10} {'Status':<15}")
    print("-"*70)
    
    best_model = None
    best_score = -1
    
    for r in results:
        model_short = r["model"][:33]
        score = r["final_score"] or 0
        time_s = r["elapsed_seconds"]
        status = r["status"]
        
        print(f"{model_short:<35} {score:<8.2f} {time_s:<10.1f} {status:<15}")
        
        if score > best_score:
            best_score = score
            best_model = r["model"]
    
    print("-"*70)
    print(f"\n🏆 BEST MODEL: {best_model} (Score: {best_score:.2f})")
    
    # Save results to JSON
    output_file = "/Volumes/Ganador disk/atlas/artifacts/benchmark_ollama_models.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "topic": MATH_TOPIC,
            "iterations_per_model": MAX_ITERATIONS,
            "results": results,
            "best_model": best_model,
            "best_score": best_score
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
