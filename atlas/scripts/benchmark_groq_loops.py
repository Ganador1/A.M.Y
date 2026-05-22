
import asyncio
import os
import sys
import time
import json
from datetime import datetime
from unittest.mock import MagicMock

# MOCK OLLAMA BEFORE IMPORTING APP
sys.modules["ollama"] = MagicMock()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now strict imports
from app.services.multi_model_hypothesis_service import multi_model_service, ModelProvider, ModelTier, ModelConfig
from app.services.ollama_service import HypothesisRequest
from app.core.bootstrap_logging import logger

# PATCH: Update Groq model name to what is in groq_provider.py
for config in multi_model_service.MODEL_CONFIGS:
    if config.provider == ModelProvider.GROQ:
        print(f"⚠️ Patching Groq model: {config.name} -> llama-3.1-70b-versatile")
        config.name = "llama-3.1-70b-versatile"
        # Re-initialize/enable because init might have skipped if it checked availability (it doesn't, but good to be safe)


# Configuration
DOMAINS = [
    {
        "domain": "biology", 
        "question": "What are the novel mechanisms for protein folding stability in high-temperature extremophiles?",
        "context": {"focus": "enzyme_stability", "application": "industrial_biotech"}
    },
    {
        "domain": "materials_science", 
        "question": "Propose a new candidate for room-temperature superconductivity based on hydride structures.",
        "context": {"pressure_limit": "200GPa", "structure_type": "clathrate"}
    },
    {
        "domain": "climate_science", 
        "question": "Evaluate the efficacy of enhanced weathering of basalt for carbon sequestration in tropical soils.",
        "context": {"region": "tropics", "time_scale": "50_years"}
    },
    {
        "domain": "physics", 
        "question": "Investigate the role of majorana fermions in topological quantum computing error correction.",
        "context": {"qubit_type": "topological", "error_model": "depolarizing"}
    },
    {
        "domain": "neuroscience", 
        "question": "Hypothesize the function of astrocytes in long-term memory consolidation during sleep.",
        "context": {"sleep_stage": "REM", "mechanism": "synaptic_pruning"}
    }
]

async def benchmark_domain(domain_config):
    domain = domain_config["domain"]
    question = domain_config["question"]
    context = domain_config.get("context", {})
    
    print(f"\\n🧪 Benchmarking Domain: {domain.upper()}...")
    print(f"   Question: {question}")
    
    req = HypothesisRequest(
        research_question=question,
        domain=domain,
        context=context,
        model_preference="llama-3.1-70b-versatile" # Asking for the corrected model name
    )
    
    start_time = time.time()
    try:
        print("   🚀 Sending request to Groq...")
        candidates = await multi_model_service.generate_hypothesis_parallel(
            request=req,
            num_models=1,
            tier=ModelTier.FAST # Groq is FAST tier
        )
        
        duration = time.time() - start_time
        
        if not candidates:
            print("   ❌ No candidates returned.")
            return {"domain": domain, "success": False, "error": "No candidates", "duration": duration}
            
        candidate = candidates[0]
        
        # Verify provider was indeed Groq (or fallback)
        provider_used = candidate.provider
        model_used = candidate.model_name
        
        print(f"   ✅ Success! Provider: {provider_used}, Model: {model_used}")
        print(f"   ⏱️  Duration: {duration:.2f}s")
        print(f"   📝 Hypothesis length: {len(candidate.hypothesis_text)} chars")
        print(f"   💡 Confidence: {candidate.confidence}")
        
        return {
            "domain": domain,
            "success": True,
            "duration": duration,
            "provider": provider_used,
            "model": model_used,
            "confidence": candidate.confidence,
            "tokens": getattr(candidate, "tokens_used", 0)
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"   ❌ Error: {str(e)}")
        return {"domain": domain, "success": False, "error": str(e), "duration": duration}

async def main():
    print("==================================================")
    print("🔬 STARTING GROQ BENCHMARK ON SCIENCE LOOPS")
    print("==================================================")
    
    results = []
    
    # Run sequentially to clearly see each output
    for config in DOMAINS:
        res = await benchmark_domain(config)
        results.append(res)
        
    print("\\n==================================================")
    print("📊 BENCHMARK SUMMARY")
    print("==================================================")
    
    api_key_status = "SET" if os.getenv("GROQ_API_KEY") else "MISSING"
    print(f"Groq API Key Status: {api_key_status}")
    
    total_time = 0
    successful = 0
    
    print(f"{'DOMAIN':<20} | {'STATUS':<10} | {'TIME':<10} | {'MODEL':<20}")
    print("-" * 70)
    
    for r in results:
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        time_str = f"{r['duration']:.2f}s"
        model_str = r.get("model", "N/A")
        print(f"{r['domain']:<20} | {status:<10} | {time_str:<10} | {model_str:<20}")
        
        if r["success"] and r.get("provider") == ModelProvider.GROQ:
            total_time += r["duration"]
            successful += 1
            
    print("-" * 70)
    
    avg_time = (total_time / successful) if successful > 0 else 0
    print(f"Average Latency (Groq): {avg_time:.2f}s")
    
    # Save results to JSON
    output_file = f"reports/groq_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("reports", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\\n📄 Detailed report saved to: {output_file}")
    
    await multi_model_service.close()

if __name__ == "__main__":
    asyncio.run(main())
