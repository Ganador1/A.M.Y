#!/usr/bin/env python3
"""
Phase 9 Final Validation - Individual Config Execution
======================================================

Ejecuta cada config individualmente para evitar timeouts acumulados.
Implementa diversity_bonus=0.30 y retry logic.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')

from app.autonomous.pipelines.quantum_loop import QuantumLoop
from app.config.config_loader import load_config_section
from rich.console import Console
from rich.panel import Panel
import shutil

console = Console()


def backup_yaml_file(filename: str):
    """Backup a YAML config file"""
    source = Path(f"config/{filename}.yaml")
    backup = Path(f"config/{filename}.backup")
    if source.exists():
        shutil.copy(source, backup)
        return backup
    return backup  # Return backup path anyway for consistency


def restore_yaml_file(filename: str, backup_path: Path):
    """Restore a YAML config file from backup"""
    target = Path(f"config/{filename}.yaml")
    if backup_path and backup_path.exists():
        shutil.copy(backup_path, target)
        backup_path.unlink()  # Remove backup

# Configuraciones a probar
CONFIGS = {
    "baseline_local": {
        "name": "Baseline Local (Ollama 7-8B)",
        "models": {
            "bio_hypothesis": "mistral:7b",
            "orchestrator": "deepseek-r1:8b",
            "physchem_coder": "llama2:7b",
            "publisher": "llama2:7b",
            "reviewer": "deepseek-r1:8b"
        }
    },
    "hf_deepseek_v3": {
        "name": "DeepSeek-V3 Planner + Scientific Mix",
        "models": {
            "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",
            "orchestrator": "deepseek-ai/DeepSeek-V3",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "reviewer": "deepseek-ai/DeepSeek-V3"
        }
    },
    "hf_qwen72_science": {
        "name": "Qwen2.5-72B Science Specialist",
        "models": {
            "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",
            "orchestrator": "Qwen/Qwen2.5-72B-Instruct",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "publisher": "Qwen/Qwen2.5-72B-Instruct",
            "reviewer": "Qwen/Qwen2.5-72B-Instruct"
        }
    },
    "hf_frontier_reflect": {
        "name": "Frontier Reflection (DeepSeek-R1 + Llama-405B)",
        "models": {
            "bio_hypothesis": "Qwen/QwQ-32B-Preview",
            "orchestrator": "deepseek-ai/DeepSeek-R1",
            "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "reviewer": "deepseek-ai/DeepSeek-R1"
        }
    }
}


def run_single_config(config_id: str, config_data: dict, iteration: int = 1) -> dict:
    """Ejecuta una configuración individual"""
    console.print(Panel(
        f"[bold cyan]Config: {config_data['name']}[/bold cyan]\n"
        f"Iteration: {iteration}",
        title=f"⚙️ Running {config_id}",
        border_style="cyan"
    ))
    
    # Backup current agents.yaml
    backup_path = backup_yaml_file("agents")
    
    try:
        # Load and modify agents.yaml
        agents_config = load_config_section("agents")
        
        # Update models
        for role, model in config_data["models"].items():
            if "roles" in agents_config and role in agents_config["roles"]:
                agents_config["roles"][role]["model"] = model
        
        # Save modified config
        import yaml
        config_path = Path("config/agents.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(agents_config, f, default_flow_style=False, allow_unicode=True)
        
        console.print(f"✅ agents.yaml actualizado para '{config_id}'")
        
        # Initialize and run
        start_time = time.time()
        loop = QuantumLoop()
        
        console.print(f"🔧 Diversity bonus: {loop.scorer.weights.diversity_bonus}")
        console.print(f"🔧 Stochastic top-k: {loop.scheduler.stochastic_topk}")
        
        # Run iteration (sync method)
        result = loop.run_iteration(iteration=iteration, limit=4)
        duration = time.time() - start_time
        
        # Extract metrics
        score = result.get("final_score", 0.0)
        evidence = result.get("evidence_strength", 0.0)
        outcomes = result.get("outcomes", [])
        candidates = [o.get("name", "Unknown") for o in outcomes]
        
        console.print(Panel(
            f"[green]✅ Completado en {duration:.1f}s[/green]\n"
            f"Score: {score:.3f}\n"
            f"Evidence: {evidence:.3f}\n"
            f"Candidates: {len(candidates)}\n"
            f"Names: {', '.join(candidates[:3])}...",
            title=f"📊 Results: {config_id}",
            border_style="green"
        ))
        
        return {
            "config_id": config_id,
            "config_name": config_data["name"],
            "iteration": iteration,
            "duration_s": duration,
            "score": score,
            "evidence": evidence,
            "num_candidates": len(candidates),
            "candidate_names": candidates,
            "success": True
        }
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return {
            "config_id": config_id,
            "config_name": config_data["name"],
            "iteration": iteration,
            "error": str(e),
            "success": False
        }
    finally:
        # Restore original agents.yaml
        if backup_path and Path(backup_path).exists():
            restore_yaml_file("agents", backup_path)
            console.print("✅ agents.yaml restaurado")


async def main():
    console.print(Panel(
        "[bold magenta]Phase 9 Final Validation[/bold magenta]\n"
        "diversity_bonus=0.30 | HuggingFace API retry logic",
        title="🚀 AXIOM ATLAS - Model Comparison",
        border_style="magenta"
    ))
    
    results = []
    
    for config_id, config_data in CONFIGS.items():
        result = run_single_config(config_id, config_data, iteration=1)
        results.append(result)
        
        # Wait between configs to avoid API rate limiting
        if result["success"]:
            console.print("\n⏸️ Esperando 4s antes de la siguiente configuración...\n")
            await asyncio.sleep(4)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"phase9_final_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "diversity_bonus": 0.30,
            "retry_logic_enabled": True,
            "results": results
        }, f, indent=2)
    
    console.print(Panel(
        f"[green]✅ Results saved to {results_file}[/green]",
        title="💾 Save Complete",
        border_style="green"
    ))
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[bold]📊 FINAL RESULTS SUMMARY[/bold]")
    console.print("="*70)
    
    successful = [r for r in results if r["success"]]
    
    if successful:
        console.print(f"\n✅ Successful configs: {len(successful)}/{len(results)}\n")
        
        for r in successful:
            console.print(f"{r['config_id']:20s} | Score: {r['score']:.3f} | Candidates: {', '.join(r['candidate_names'][:3])}")
        
        # Check for empate
        scores = [r["score"] for r in successful]
        if len(scores) >= 2:
            max_score = max(scores)
            min_score = min(scores)
            diff = max_score - min_score
            diff_pct = (diff / max_score * 100) if max_score > 0 else 0
            
            console.print(f"\n🎯 Score range: {min_score:.3f} - {max_score:.3f}")
            console.print(f"🎯 Difference: {diff:.3f} ({diff_pct:.2f}%)")
            
            if diff_pct > 2.0:
                console.print(f"[green]✅ Empate RESOLVED (>{2.0}% difference)[/green]")
            else:
                console.print(f"[yellow]⚠️ Empate still present (<{2.0}% difference)[/yellow]")
    else:
        console.print("[red]❌ All configs failed[/red]")
    
    console.print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
