"""Diagnostico del nuevo bucle."""
import json

with open("data/episodic_memory.jsonl") as f:
    raw = [l for l in f if l.strip()]

entries = [json.loads(l) for l in raw]
cycles = [e for e in entries if e["event_type"] == "cognitive_cycle"]

streak = 0
for e in reversed(cycles):
    a = e.get("metadata", {}).get("action_type", "")
    c = e.get("content", "")
    if a == "think_more" and "COMPLETE" in c:
        streak += 1
    else:
        break

print("Streak MISSION COMPLETE think_more:", streak)
print("Total ciclos:", len(cycles))

# Distribucion por accion en las 3 sesiones
actions_all = {}
for e in cycles:
    a = e.get("metadata", {}).get("action_type", "?")
    actions_all[a] = actions_all.get(a, 0) + 1
print("Distribucion total acciones:", actions_all)
