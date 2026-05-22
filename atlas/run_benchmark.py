import asyncio
import sys
import json
from tabulate import tabulate
from run_agent_with_tools import autonomous_research_agent

# List of models to benchmark
MODELS = [
    "rnj-1:8b-cloud",               # Baseline: Hit 7/10 in biology
    "gemini-3-flash-preview:cloud",
    "glm-4.7:cloud",
    "minimax-m2.1:cloud",
    "deepseek-v3.2:cloud"
]

DOMAIN = "mathematics"
TOPIC = """Investigate the Goldbach Conjecture through computational verification:
1. Verify Goldbach's conjecture for even numbers up to 10,000
2. Analyze the distribution of prime pairs that satisfy the conjecture
3. Use formal theorem proving to establish auxiliary lemmas
4. Discover patterns in prime gap distributions related to Goldbach partitions
Use the available mathematical tools: z3_verify_theorem, number_theory_advanced, conjecture_engine, automated_prover, sequence_analyzer."""

async def run_benchmark():
    results = []
    
    print(f"🚀 STARTING MODEL BENCHMARK TOURNAMENT (ROUND 2)")
    print(f"Domain: {DOMAIN}")
    print(f"Topic: {TOPIC}")
    print(f"Models to test: {len(MODELS)}\n")
    
    for model_name in MODELS:
        print(f"----------------------------------------------------------------")
        print(f"🤖 TESTING MODEL: {model_name}")
        print(f"----------------------------------------------------------------")
        
        try:
            # Run the agent with higher base iterations
            result = await autonomous_research_agent(DOMAIN, TOPIC, model_name=model_name, max_iterations=3)
            
            # Extract metrics
            score = result.get("final_score", 0)
            status = result.get("status", "failed")
            iterations = result.get("iterations_used", 0)
            
            print(f"✅ RESULT: Score {score}/10 | Status: {status} | Iterations: {iterations}")
            
            results.append({
                "model": model_name,
                "score": score,
                "status": status,
                "iterations": iterations,
                "paper_preview": result.get("paper", "")[:100].replace("\n", " ") + "..."
            })
            
        except Exception as e:
            print(f"❌ FAILED: {model_name} | Error: {str(e)}")
            results.append({
                "model": model_name,
                "score": 0,
                "status": "error",
                "iterations": 0,
                "error": str(e)
            })
            
    # Print Summary Table
    print("\n\n🏆 BENCHMARK RESULTS 🏆")
    table_data = [[r["model"], r["score"], r["iterations"], r["status"]] for r in results]
    headers = ["Model", "Score", "Iters", "Status"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Identify Winner
    best_result = max(results, key=lambda x: x["score"])
    print(f"\n🥇 WINNER: {best_result['model']} with Score {best_result['score']}/10")

    # Save details to file
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(" detailed results saved to benchmark_results.json")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
