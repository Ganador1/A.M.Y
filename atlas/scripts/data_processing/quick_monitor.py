#!/usr/bin/env python3
"""Script de monitoreo simple para ver el progreso de la clasificación."""

import os
import json
from pathlib import Path
from datetime import datetime

def check_progress():
    """Verificar progreso actual de la clasificación."""
    
    output_file = Path("data/final_llm_classifications.jsonl")
    log_file = Path("classification_night.log")
    target_papers = 500
    
    print(f"🌙 MONITOR CLASIFICACIÓN NOCTURNA - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Check if process is running
    ps_output = os.popen("ps aux | grep enhanced_llm_classifier | grep -v grep").read()
    if ps_output.strip():
        print("✅ Proceso ejecutándose")
        process_count = len([line for line in ps_output.strip().split('\n') if line])
        print(f"📊 Procesos activos: {process_count}")
    else:
        print("⚠️ Proceso no encontrado")
    
    # Check progress
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            completed = len([line for line in f if line.strip()])
        progress = (completed / target_papers) * 100
        
        print(f"\n📈 Progreso: {completed}/{target_papers} papers ({progress:.1f}%)")
        
        if completed > 0:
            # Show latest classified paper
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_paper = json.loads(lines[-1])
                    title = last_paper['title'][:50] + "..." if len(last_paper['title']) > 50 else last_paper['title']
                    confidence = last_paper.get('confidence', 0)
                    plausible = "✅" if last_paper.get('plausible', False) else "❌"
                    print(f"🔄 Último procesado: {plausible} {title} (conf: {confidence:.2f})")
        
        # Estimate time remaining
        if completed > 0:
            # Rough estimation based on our test (17.5 seconds per paper)
            remaining_papers = target_papers - completed
            estimated_minutes = remaining_papers * 17.5 / 60
            print(f"⏰ Tiempo estimado restante: {estimated_minutes:.1f} minutos ({estimated_minutes/60:.1f} horas)")
    else:
        print("📄 Archivo de salida aún no creado")
    
    # Check log file
    if log_file.exists() and log_file.stat().st_size > 0:
        print(f"\n📝 Log disponible ({log_file.stat().st_size} bytes)")
        # Show last few lines of log
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print("📋 Últimas líneas del log:")
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
    else:
        print("\n📝 Log aún vacío")
    
    print("\n💡 Para monitorear en tiempo real:")
    print("   tail -f classification_night.log")
    print("   watch -n 30 'python quick_monitor.py'")

if __name__ == "__main__":
    check_progress()
