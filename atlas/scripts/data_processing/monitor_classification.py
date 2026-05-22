#!/usr/bin/env python3
"""Monitor script para seguir el progreso de clasificación masiva."""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_classification_progress():
    """Monitorear progreso de la clasificación."""
    
    output_file = Path("data/massive_llm_classifications_full.jsonl")
    log_file = Path("classification_full.log")
    
    print("🔍 MONITOR DE CLASIFICACIÓN MASIVA")
    print("=" * 50)
    
    if not log_file.exists():
        print("❌ Log file not found. Process may not have started.")
        return
    
    target_papers = 500
    start_time = time.time()
    last_count = 0
    
    while True:
        try:
            # Check output file
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    current_count = len([l for l in lines if l.strip()])
            else:
                current_count = 0
            
            # Calculate progress
            progress = (current_count / target_papers) * 100
            elapsed = time.time() - start_time
            
            if current_count > last_count:
                papers_per_minute = (current_count - last_count) / 1.0  # Since we check every minute
                eta_minutes = (target_papers - current_count) / papers_per_minute if papers_per_minute > 0 else 0
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 Progreso: {current_count}/{target_papers} ({progress:.1f}%)")
                print(f"⏱️  Tiempo transcurrido: {elapsed/3600:.1f}h")
                print(f"🚀 Velocidad: {papers_per_minute:.1f} papers/min")
                print(f"⏰ ETA: {eta_minutes/60:.1f}h restantes")
                
                # Show last few lines of log
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_lines = f.readlines()
                        if log_lines:
                            print(f"🔄 Último log: {log_lines[-1].strip()}")
            
            last_count = current_count
            
            # Check if completed
            if current_count >= target_papers:
                print(f"\n🎉 ¡CLASIFICACIÓN COMPLETADA!")
                print(f"📊 Total procesado: {current_count} papers")
                print(f"⏱️  Tiempo total: {elapsed/3600:.1f} horas")
                break
            
            # Wait 1 minute before next check
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor detenido por usuario")
            break
        except Exception as e:
            print(f"❌ Error en monitor: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_classification_progress()
