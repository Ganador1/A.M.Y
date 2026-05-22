"""Analisis profundo de calidad del razonamiento de A.M.Y."""
import json
from collections import Counter

with open("data/episodic_memory.jsonl") as f:
    entries = [json.loads(l) for l in f if l.strip()]

cycles = [e for e in entries if e["event_type"] == "cognitive_cycle"]
researches = [e for e in entries if e["event_type"] == "research"]

# Distribucion de acciones total
all_actions = Counter(e.get("metadata", {}).get("action_type", "?") for e in cycles)
recent_actions = Counter(e.get("metadata", {}).get("action_type", "?") for e in cycles[-50:])
print("ACCIONES TOTAL   (426 ciclos):", dict(all_actions))
print("ACCIONES ULTIMOS 50 ciclos:   ", dict(recent_actions))

# Nuevo bucle: think_more MISSION COMPLETE
mission_complete = [
    e for e in cycles
    if "MISSION" in e.get("content", "") or "COMPLETE" in e.get("content", "")
]
print(f"\nCiclos 'MISSION COMPLETE': {len(mission_complete)}")
print("(A.M.Y cree haber terminado pero el heartbeat sigue corriendo)")

# Skill library
import os, pathlib
skills_path = pathlib.Path("data/skill_library/index.json")
if skills_path.exists():
    with open(skills_path) as f:
        skills = json.load(f)
    print(f"\nSKILLS CREADAS: {len(skills)}")
    for name, info in skills.items():
        print(f"  - {name}: {info.get('description','')[:90]}")

# Ver el contenido REAL de una de las conclusiones
print("\n\n=== CONTENIDO REAL DE LA ULTIMA CONCLUSION ===")
for e in reversed(cycles):
    if "MISSION" in e.get("content", "") and len(e["content"]) > 300:
        print(e["content"][:2000])
        break

# Verificar si los hechos del KG son reales o inventados
with open("data/knowledge_graph.json") as f:
    kg = json.load(f)
facts = kg.get("facts", {})

# Hechos sobre tratamientos especificos
treatment_facts = {k: v for k, v in facts.items()
                   if any(w in k.lower() for w in ["car-t", "dcvax", "dnx", "pvsripo",
                                                     "oncolytic", "nanopart", "focused",
                                                     "convection", "checkpoint", "braf",
                                                     "egfr", "idh", "personalized"])}
print(f"\n\nHECHOS ESPECIFICOS SOBRE TRATAMIENTOS: {len(treatment_facts)}")
for k, v in list(treatment_facts.items())[:20]:
    conf = v.get("confidence", 0)
    subj = v.get("subject", "")[:35]
    pred = v.get("predicate", "")[:20]
    obj = v.get("object", "")[:70]
    print(f"  [{conf:.0%}] {subj:35s} | {pred:20s} | {obj}")
