#!/usr/bin/env python3
"""
Análisis del estado actual de los loops
Basado en isolated_loops_results_20251029_211748.json
"""

import json
from pathlib import Path
from datetime import datetime


def main():
    # Leer archivo de resultados más reciente
    result_file = "isolated_loops_results_20251029_211748.json"
    
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 70)
    print("📊 ANÁLISIS DE ESTADO ACTUAL - AXIOM LOOPS")
    print("=" * 70)
    print(f"\n📁 Archivo: {result_file}")
    print(f"📅 Fecha: {data.get('timestamp', 'N/A')}")
    print(f"✅ Loops exitosos: {data.get('successful', 0)}/{data.get('total', 0)}")
    
    # Extraer scores por loop
    print("\n" + "=" * 70)
    print("📈 SUPPORT SCORES POR LOOP")
    print("=" * 70)
    
    loops_data = []
    
    for loop in data.get('results', []):
        name = loop.get('loop_name', 'Unknown')
        parsed = loop.get('parsed_summary', {})
        score = parsed.get('support_score', 0.0)
        duration = loop.get('duration_seconds', 0.0)
        num_candidates = parsed.get('num_candidates', 0)
        
        loops_data.append({
            'name': name,
            'score': score,
            'duration': duration,
            'candidates': num_candidates
        })
        
        # Emoji según score
        if score >= 0.5:
            emoji = "🌟"
        elif score >= 0.3:
            emoji = "✅"
        elif score >= 0.1:
            emoji = "⚠️"
        else:
            emoji = "❌"
        
        print(f"\n{emoji} {name}")
        print(f"   Score: {score:.4f}")
        print(f"   Candidatos: {num_candidates}")
        print(f"   Duración: {duration:.1f}s")
    
    # Estadísticas globales
    scores = [l['score'] for l in loops_data]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS GLOBALES")
    print("=" * 70)
    print(f"\n  Promedio: {avg_score:.4f}")
    print(f"  Máximo: {max_score:.4f}")
    print(f"  Mínimo: {min_score:.4f}")
    
    # Loops con mejor performance
    sorted_loops = sorted(loops_data, key=lambda x: x['score'], reverse=True)
    
    print("\n🏆 TOP 3 LOOPS:")
    for i, loop in enumerate(sorted_loops[:3], 1):
        print(f"  {i}. {loop['name']}: {loop['score']:.4f}")
    
    print("\n⚡ LOOPS MÁS RÁPIDOS:")
    sorted_by_speed = sorted(loops_data, key=lambda x: x['duration'])
    for i, loop in enumerate(sorted_by_speed[:3], 1):
        print(f"  {i}. {loop['name']}: {loop['duration']:.1f}s")
    
    print("\n🐌 LOOPS MÁS LENTOS:")
    for i, loop in enumerate(sorted_by_speed[-3:], 1):
        print(f"  {i}. {loop['name']}: {loop['duration']:.1f}s")
    
    # Loops que necesitan atención
    print("\n" + "=" * 70)
    print("🔍 LOOPS REQUIEREN ATENCIÓN")
    print("=" * 70)
    
    needs_attention = [l for l in loops_data if l['score'] < 0.1]
    if needs_attention:
        for loop in needs_attention:
            print(f"\n❌ {loop['name']}")
            print(f"   Score bajo: {loop['score']:.4f}")
            print(f"   Acción sugerida: Revisar rutas de evidencia")
    else:
        print("\n✅ Todos los loops tienen scores aceptables (>0.1)")
    
    # Mejoras proyectadas (Ronda 3)
    print("\n" + "=" * 70)
    print("🚀 MEJORAS PROYECTADAS - RONDA 3")
    print("=" * 70)
    
    print("\n📐 MathematicsLoop:")
    math_current = next((l for l in loops_data if l['name'] == 'MathematicsLoop'), None)
    if math_current:
        print(f"   Score actual: {math_current['score']:.4f}")
        print(f"   Mejora esperada: +10-15% (SymPyService)")
        projected = math_current['score'] * 1.125  # 12.5% increase
        print(f"   Score proyectado: {projected:.4f}")
    
    print("\n🧠 NeuroscienceLoop:")
    neuro_current = next((l for l in loops_data if l['name'] == 'NeuroscienceLoop'), None)
    if neuro_current:
        print(f"   Score actual: {neuro_current['score']:.4f}")
        print(f"   Mejora esperada: +50-100% (+2 rutas)")
        projected_min = neuro_current['score'] + 0.15
        projected_max = neuro_current['score'] + 0.25
        print(f"   Score proyectado: {projected_min:.4f} - {projected_max:.4f}")
    
    print("\n" + "=" * 70)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    main()
