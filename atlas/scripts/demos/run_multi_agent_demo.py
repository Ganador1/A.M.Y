"""Demo de ejecución del pipeline multi-agente (~7B modelos especializados).
Uso:
  python scripts/run_multi_agent_demo.py --goal "Mejorar estabilidad térmica de un biopolímero" --backend ollama

Asume que Ollama está corriendo y modelos están disponibles (pull previo).
"""
from __future__ import annotations
import argparse
import os
import sys

# Permitir ejecución directa
sys.path.append(os.path.abspath('.'))

from app.services.multi_agent_coordinator import MultiAgentCoordinator, DEFAULT_ROLE_MODELS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--goal', required=True, help='Objetivo científico / research goal')
    parser.add_argument('--override', action='append', default=[], help='Override rol=modelo (ej: reviewer=qwen:7b)')
    args = parser.parse_args()

    role_models = DEFAULT_ROLE_MODELS.copy()
    for ov in args.override:
        if '=' in ov:
            role, model = ov.split('=', 1)
            role_models[role.strip()] = model.strip()

    coordinator = MultiAgentCoordinator(role_models=role_models)
    result = coordinator.run_pipeline(args.goal)

    print("=== RESULTADOS PIPELINE MULTI-AGENTE ===")
    if result.get('success'):
        artifact = result['artifact']
        print(f"Session: {artifact['session_id']}")
        print("\n-- Plan --\n", artifact['plan'][:800])
        print("\n-- Hipótesis --\n", artifact['hypothesis'][:800])
        print("\n-- Diseño --\n", artifact['design'][:800])
        print("\n-- Revisión --\n", artifact['review'][:800])
        print("\n-- Publicación (inicio) --\n", artifact['publication'][:800])
        out_path = os.path.join('logs', 'agents', f"artifact_{artifact['session_id']}.json")
        print(f"\nArtefacto completo guardado en: {out_path}")
    else:
        print("ERROR:", result.get('error'))


if __name__ == '__main__':
    main()
