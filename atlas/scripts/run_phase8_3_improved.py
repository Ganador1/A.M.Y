#!/usr/bin/env python3
"""
AXIOM ATLAS - Model Comparison Phase 8.3
Mejoras de diversidad: Quantum fix + prompts optimizados

Solo ejecuta: Neuroscience, Mathematics, Quantum
(Chemistry ya fue bien en Phase 8.2)
"""
import subprocess
import sys

def main():
    print("=" * 80)
    print("🚀 AXIOM ATLAS - Model Comparison Phase 8.3")
    print("=" * 80)
    print("\n📋 Configuración:")
    print("  - Quantum loop: ARREGLADO (ahora retorna 'outcomes')")
    print("  - Prompts: MEJORADOS (temp +0.10 a +0.15, tokens +128 a +200)")
    print("  - Dominios: Neuroscience, Mathematics, Quantum")
    print("  - Chemistry: SKIP (ya ejecutado en 8.2 con buenos resultados)")
    print("\n" + "=" * 80)
    
    confirm = input("\n¿Ejecutar comparación Phase 8.3? (si/no): ").strip().lower()
    if confirm not in ['si', 's', 'yes', 'y']:
        print("❌ Cancelado por el usuario")
        return 1
    
    print("\n🔧 Ejecutando run_model_comparison_phase8.py con filtro de dominios...")
    print("-" * 80)
    
    cmd = [
        "python3",
        "run_model_comparison_phase8.py",
        "--domains", "neuroscience,mathematics,quantum"
    ]
    
    result = subprocess.run(cmd, check=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ Phase 8.3 completado exitosamente")
        print("=" * 80)
        print("\n📊 Siguientes pasos:")
        print("  1. Revisar JSON generado")
        print("  2. Comparar diversidad vs Phase 8.2")
        print("  3. Validar que Quantum ahora genera outcomes")
        print("  4. Analizar si Neuroscience/Mathematics muestran diferencias")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ Phase 8.3 falló")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
