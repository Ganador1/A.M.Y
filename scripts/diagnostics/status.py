"""Reporte de estado de A.M.Y."""
import json
import datetime

# ─── Episodic Memory ───
entries = []
event_types = {}
with open("data/episodic_memory.jsonl") as f:
    for line in f:
        try:
            e = json.loads(line)
            entries.append(e)
            t = e["event_type"]
            event_types[t] = event_types.get(t, 0) + 1
        except Exception:
            pass

print(f"Memorias episodicas: {len(entries)}")
print(f"Por tipo: {event_types}")
t0 = datetime.datetime.fromtimestamp(entries[0]["timestamp"]).strftime("%H:%M:%S")
t1 = datetime.datetime.fromtimestamp(entries[-1]["timestamp"]).strftime("%H:%M:%S")
cycles = event_types.get("cognitive_cycle", 0)
searches = event_types.get("research", 0)
print(f"Periodo: {t0} → {t1}  |  {cycles} ciclos cognitivos  |  {searches} búsquedas")

# ─── Knowledge Graph ───
with open("data/knowledge_graph.json") as f:
    kg = json.load(f)
facts = kg.get("facts", {})
print(f"\nHechos aprendidos: {len(facts)}")

scored = sorted(facts.values(), key=lambda x: x.get("confidence", 0), reverse=True)[:15]
print("\nTOP 15 HECHOS MÁS CONFIABLES:")
for i, fact in enumerate(scored, 1):
    subj = fact.get("subject", "")[:32]
    pred = fact.get("predicate", "")[:16]
    obj = fact.get("object", "")[:60]
    conf = fact.get("confidence", 0)
    print(f"  {i:2d}. [{conf:.0%}] {subj:32s} | {pred:16s} | {obj}")

# ─── Últimos pensamientos ───
print("\nÚLTIMOS 5 CICLOS COGNITIVOS:")
cycles_only = [e for e in entries if e["event_type"] == "cognitive_cycle"]
for e in cycles_only[-5:]:
    t = datetime.datetime.fromtimestamp(e["timestamp"]).strftime("%H:%M:%S")
    print(f"  [{t}] {e['content'][:120]}")

# ─── Papers generados ───
import os
from pathlib import Path
papers_dir = Path("papers")
if papers_dir.exists():
    papers = sorted(papers_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    pdfs = sorted(papers_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime)
    if papers:
        print(f"\nPAPERS GENERADOS: {len(papers)} Markdown / {len(pdfs)} PDF")
        for p in papers[-5:]:
            size_kb = p.stat().st_size // 1024
            title = p.stem.replace("_", " ").rsplit(" ", 1)[0][:70]
            print(f"  📄 {title} ({size_kb}KB)")
    else:
        print("\nPAPERS GENERADOS: ninguno aún")

# ─── Scripts ejecutados ───
scripts_done = event_types.get("script_execution", 0)
papers_written = event_types.get("paper_written", 0)
if scripts_done or papers_written:
    print(f"\nEXPERIMENTOS: {event_types.get('experiment',0)} código Python | {scripts_done} scripts | {papers_written} papers escritos")

