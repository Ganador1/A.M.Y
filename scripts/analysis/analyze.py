"""Analisis conductual de A.M.Y."""
import json
from collections import Counter

with open("data/episodic_memory.jsonl") as f:
    entries = [json.loads(l) for l in f if l.strip()]

cycles = [e for e in entries if e["event_type"] == "cognitive_cycle"]
researches = [e for e in entries if e["event_type"] == "research"]

# Acciones de los ultimos 35 ciclos
actions = [e.get("metadata", {}).get("action_type", "?") for e in cycles[-35:]]
print("ACCIONES ultimos 35 ciclos:", Counter(actions))

# ver si hubo reflect/decompose
decompose = [e for e in entries if e.get("metadata", {}).get("action_type") == "decompose_goal"]
think_more = [e for e in entries if e.get("metadata", {}).get("action_type") == "think_more"]
print(f"\ndecompose_goal ejecutado: {len(decompose)} veces")
print(f"think_more ejecutado: {len(think_more)} veces")

# Ver sub-goals creados
with open("data/knowledge_graph.json") as f:
    kg = json.load(f)
facts = kg.get("facts", {})
print(f"\nTotal hechos KG: {len(facts)}")

# Queries de las ultimas 20 busquedas
queries20 = [e["content"].replace("Searched: ", "")[:85] for e in researches[-20:]]
unique_q = len(set(queries20))
dups = len(queries20) - unique_q
print(f"\nUltimas 20 queries: {unique_q} unicas, {dups} duplicadas")
print("\nULTIMAS 20 QUERIES:")
seen = set()
for q in queries20:
    mark = "DUP" if q in seen else "NEW"
    seen.add(q)
    print(f"  [{mark}] {q}")
