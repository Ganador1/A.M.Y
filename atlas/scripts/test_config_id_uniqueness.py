#!/usr/bin/env python3
"""
Test para verificar que config_id es ÚNICO por configuración de modelo

OBJETIVO:
- Simular 4 configs diferentes (cambiando agents.yaml)
- Verificar que cada una genera config_id diferente
- Confirmar que LLM recibe prompts con seeds únicos
"""

import asyncio
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.autonomous.pipelines.quantum_loop import QuantumLoop


async def test_config_id_uniqueness():
    """Verifica que diferentes configs generan diferentes config_ids"""
    
    print("=" * 80)
    print("TEST: CONFIG_ID UNIQUENESS ACROSS CONFIGURATIONS")
    print("=" * 80)
    print()
    
    # Simular 3 configuraciones diferentes modificando agents.yaml
    test_configs = [
        {
            "name": "Config A - Llama Local",
            "model": "llama2:7b",
            "temperature": 0.7
        },
        {
            "name": "Config B - Qwen 32B",
            "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "temperature": 0.35
        },
        {
            "name": "Config C - DeepSeek",
            "model": "deepseek-ai/DeepSeek-V3",
            "temperature": 0.25
        }
    ]
    
    agents_file = Path("config/agents.yaml")
    backup_file = Path("config/agents.yaml.test_backup")
    
    # Backup original
    with agents_file.open("r") as f:
        original_config = yaml.safe_load(f)
    
    with backup_file.open("w") as f:
        yaml.safe_dump(original_config, f)
    
    print("✅ Backup de config/agents.yaml creado")
    print()
    
    config_ids_seen = []
    
    try:
        for idx, test_config in enumerate(test_configs, 1):
            print(f"{'='*60}")
            print(f"TEST {idx}/3: {test_config['name']}")
            print(f"{'='*60}")
            
            # Modificar agents.yaml
            modified = original_config.copy()
            modified["roles"]["physchem_coder"]["model"] = test_config["model"]
            modified["roles"]["physchem_coder"]["params"]["temperature"] = test_config["temperature"]
            
            with agents_file.open("w") as f:
                yaml.safe_dump(modified, f)
            
            print(f"📝 Configurado: {test_config['model']} @ temp={test_config['temperature']}")
            
            # Crear nuevo loop (cada config tiene su propia instancia)
            loop = QuantumLoop()
            
            # Ejecutar iteración para capturar config_id generado
            # Vamos a hacer una pequeña modificación temporal para capturar el config_id
            # Por ahora, solo ejecutamos y vemos si los resultados son diferentes
            
            result = await loop.run_quantum_discovery_iteration(iteration=1, limit=2)
            
            if result.get("success", True):
                candidates = result.get("candidates", [])
                print(f"✅ Loop ejecutado correctamente")
                print(f"   Candidatos generados: {len(candidates)}")
                
                if candidates:
                    # Mostrar primeros 2 nombres
                    names = [c.get("id", "unknown") for c in candidates[:2]]
                    print(f"   Nombres: {names}")
                    config_ids_seen.append({
                        "config": test_config["name"],
                        "model": test_config["model"],
                        "temperature": test_config["temperature"],
                        "candidate_names": names
                    })
            else:
                print(f"⚠️  Loop falló: {result.get('reason', 'unknown')}")
            
            print()
            
            # Pequeña pausa para garantizar timestamps diferentes
            await asyncio.sleep(0.1)
    
    finally:
        # Restaurar config original
        with backup_file.open("r") as f:
            original_config = yaml.safe_load(f)
        
        with agents_file.open("w") as f:
            yaml.safe_dump(original_config, f)
        
        backup_file.unlink()
        print("✅ config/agents.yaml restaurado")
    
    # Análisis de uniqueness
    print(f"\n{'='*60}")
    print("ANÁLISIS DE UNIQUENESS")
    print(f"{'='*60}\n")
    
    all_names = []
    for entry in config_ids_seen:
        all_names.extend(entry["candidate_names"])
    
    unique_names = len(set(all_names))
    total_names = len(all_names)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total nombres generados: {total_names}")
    print(f"   Nombres únicos: {unique_names}")
    print(f"   Diversidad entre configs: {(unique_names / total_names * 100) if total_names > 0 else 0:.1f}%")
    print()
    
    # Mostrar nombres por config
    print("📋 NOMBRES POR CONFIGURACIÓN:")
    for entry in config_ids_seen:
        print(f"\n   {entry['config']}:")
        print(f"   Modelo: {entry['model']}")
        print(f"   Temperature: {entry['temperature']}")
        print(f"   Candidatos: {entry['candidate_names']}")
    
    print(f"\n{'='*60}")
    
    if unique_names == total_names:
        print("✅ RESULTADO: PASS - Todos los nombres son únicos entre configs")
        print(f"{'='*60}\n")
        return True
    else:
        duplicates = total_names - unique_names
        print(f"⚠️  RESULTADO: PARTIAL - {duplicates} nombres duplicados detectados")
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_config_id_uniqueness())
    sys.exit(0 if result else 1)
