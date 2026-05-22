#!/usr/bin/env python3
"""Herramienta interactiva para crear labels supervisadas manuales.

Muestra registros del dataset y permite al usuario etiquetar manualmente
como plausible (1) o implausible (0).

Uso:
    python create_manual_labels_v4.py --sample 100 --output manual_labels_v4.json
"""

import json
import random
import argparse
from pathlib import Path
from typing import Dict, List, Any

def load_candidates(file_path: Path) -> List[Dict[str, Any]]:
    """Cargar candidatos del archivo JSONL."""
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró {file_path}")
    
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def display_record(record: Dict[str, Any], index: int, total: int) -> None:
    """Mostrar un registro para etiquetado."""
    print(f"\n{'='*80}")
    print(f"REGISTRO {index + 1}/{total}")
    print(f"{'='*80}")
    print(f"ID: {record.get('paper_id', 'N/A')[:8]}...")
    print(f"Dominio: {record.get('domain', 'N/A')}")
    print(f"Fuente: {record.get('source', 'N/A')}")
    print()
    
    title = record.get('title', '').strip()
    abstract = record.get('abstract', '').strip()
    
    print(f"TÍTULO:")
    print(f"  {title}")
    print()
    
    print(f"ABSTRACT:")
    # Dividir en líneas de ~80 chars para legibilidad
    words = abstract.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 78:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
                current_length = 0
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        print(f"  {line}")
    print()

def get_user_label() -> int:
    """Obtener etiqueta del usuario."""
    print("¿Es esta hipótesis científicamente PLAUSIBLE?")
    print("  1 = SÍ (plausible, factible, razonable)")
    print("  0 = NO (implausible, inviable, sin sentido)")
    print("  s = SALTAR este registro")
    print("  q = SALIR y guardar")
    
    while True:
        choice = input("\nTu elección [1/0/s/q]: ").strip().lower()
        
        if choice in ['1', '0']:
            return int(choice)
        elif choice == 's':
            return -1  # Skip
        elif choice == 'q':
            return -2  # Quit
        else:
            print("Por favor ingresa 1, 0, s, o q")

def save_labels(labels: Dict[str, int], output_path: Path) -> None:
    """Guardar labels manuales."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'manual_labels': labels,
            'total_labeled': len(labels),
            'distribution': {
                'plausible': sum(1 for v in labels.values() if v == 1),
                'implausible': sum(1 for v in labels.values() if v == 0)
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nLabels guardados en: {output_path}")
    print(f"Total etiquetados: {len(labels)}")

def main():
    parser = argparse.ArgumentParser(description='Crear labels supervisadas manuales')
    parser.add_argument('--input', '-i', 
                       default='data/plausibility_training_v4_candidates.jsonl',
                       help='Archivo de candidatos JSONL')
    parser.add_argument('--sample', '-n', type=int, default=50,
                       help='Número de registros a etiquetar')
    parser.add_argument('--output', '-o', 
                       default='data/manual_labels_v4.json',
                       help='Archivo de salida para labels')
    parser.add_argument('--seed', type=int, default=42,
                       help='Semilla para sampling aleatorio')
    
    args = parser.parse_args()
    
    # Cargar datos
    candidates = load_candidates(Path(args.input))
    print(f"Cargados {len(candidates)} candidatos de {args.input}")
    
    # Sampling aleatorio
    random.seed(args.seed)
    if len(candidates) > args.sample:
        sample_records = random.sample(candidates, args.sample)
        print(f"Seleccionada muestra aleatoria de {args.sample} registros")
    else:
        sample_records = candidates
        print(f"Usando todos los {len(candidates)} registros")
    
    # Proceso de etiquetado
    labels = {}
    
    print(f"\n🏷️  INICIO DEL PROCESO DE ETIQUETADO MANUAL")
    print(f"📋  Se mostrarán {len(sample_records)} registros")
    print(f"💡  Para cada uno, evalúa si la hipótesis es científicamente plausible")
    
    for i, record in enumerate(sample_records):
        display_record(record, i, len(sample_records))
        
        user_label = get_user_label()
        
        if user_label == -2:  # Quit
            print("\n🛑 Proceso interrumpido por el usuario")
            break
        elif user_label == -1:  # Skip
            print("⏭️  Registro saltado")
            continue
        else:
            paper_id = record['paper_id']
            labels[paper_id] = user_label
            status = "✅ PLAUSIBLE" if user_label == 1 else "❌ IMPLAUSIBLE"
            print(f"🏷️  Etiquetado: {status}")
    
    # Guardar resultados
    if labels:
        save_labels(labels, Path(args.output))
        
        plausible = sum(1 for v in labels.values() if v == 1)
        implausible = len(labels) - plausible
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   Total etiquetados: {len(labels)}")
        print(f"   Plausibles: {plausible} ({plausible/len(labels)*100:.1f}%)")
        print(f"   Implausibles: {implausible} ({implausible/len(labels)*100:.1f}%)")
    else:
        print("\n⚠️  No se etiquetó ningún registro")

if __name__ == '__main__':
    main()
