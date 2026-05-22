"""Auditoría profunda de A.M.Y — análisis completo."""
import json
import datetime
from pathlib import Path
from collections import Counter

entries = [json.loads(l) for l in open('data/episodic_memory.jsonl') if l.strip()]
types = Counter(e.get('event_type','?') for e in entries)

print('=== DISTRIBUCION DE EVENTOS ===')
for t,c in types.most_common():
    print(f'  {t}: {c}')

# Experimentos
exps = [e for e in entries if e['event_type']=='experiment']
print(f'\n=== EXPERIMENTOS EJECUTADOS ({len(exps)}) ===')
for e in exps:
    m = e.get('metadata',{})
    r = m.get('result',{})
    print(f'  Hipótesis: {str(e.get("content",""))[:120]}')
    print(f'  Éxito: {r.get("success")} | stdout: {str(r.get("stdout",""))[:200]}')
    code = str(m.get("code",""))
    print(f'  Código: {len(code.splitlines())} líneas')
    print()

# Scripts
scripts = [e for e in entries if e['event_type']=='script_execution']
print(f'=== SCRIPTS EJECUTADOS ({len(scripts)}) ===')
for e in scripts:
    m = e.get('metadata',{})
    print(f'  {str(e.get("content",""))[:80]} ok={m.get("success")}')

# Papers
papers = [e for e in entries if e['event_type']=='paper_written']
print(f'\n=== PAPERS ESCRITOS ({len(papers)}) ===')
for e in papers:
    m = e.get('metadata',{})
    print(f'  words={m.get("word_count",0)} | {str(m.get("markdown_path",""))[-55:]}')

# Análisis de acciones cognitivas
print('\n=== DISTRIBUCIÓN DE ACCIONES ===')
actions = Counter()
for e in entries:
    if e.get('event_type') == 'cognitive_cycle':
        a = e.get('metadata',{}).get('action_type','?')
        actions[a] = actions.get(a,0) + 1
for a,c in actions.most_common():
    print(f'  {a}: {c}')

# Análisis de queries de research
print('\n=== QUERIES MÁS FRECUENTES (top 15) ===')
queries = []
for e in entries:
    if e.get('event_type') == 'research':
        q = e.get('metadata',{}).get('query','')
        if q:
            # Tomar primeras 5 palabras como fingerprint
            fp = ' '.join(q.split()[:5]).lower()
            queries.append(fp)
freq = Counter(queries)
for q,c in freq.most_common(15):
    print(f'  [{c}x] {q}')

# Resultados de búsqueda vacíos
empty_searches = sum(1 for e in entries if e.get('event_type')=='research' and e.get('metadata',{}).get('results_count',0)==0)
total_searches = sum(1 for e in entries if e.get('event_type')=='research')
print(f'\n=== BÚSQUEDAS VACÍAS: {empty_searches}/{total_searches} ({100*empty_searches/max(total_searches,1):.0f}%) ===')

# Knowledge graph analysis
print('\n=== KNOWLEDGE GRAPH ===')
with open('data/knowledge_graph.json') as f:
    kg = json.load(f)
facts = kg.get('facts',{})
print(f'Total hechos: {len(facts)}')

# Confidence distribution
confs = [f.get('confidence',0) for f in facts.values()]
buckets = {'>90%': 0, '80-90%': 0, '60-80%': 0, '40-60%': 0, '<40%': 0}
for c in confs:
    if c > 0.9: buckets['>90%'] += 1
    elif c > 0.8: buckets['80-90%'] += 1
    elif c > 0.6: buckets['60-80%'] += 1
    elif c > 0.4: buckets['40-60%'] += 1
    else: buckets['<40%'] += 1
print('Distribución de confianza:')
for b,c in buckets.items():
    print(f'  {b}: {c} hechos')

# Predicates más comunes
preds = Counter(f.get('predicate','') for f in facts.values())
print('\nPredicados más comunes:')
for p,c in preds.most_common(10):
    print(f'  {p}: {c}')

# Sample low confidence facts
print('\nHECHOS DE BAJA CONFIANZA (para verificación):')
low_conf = sorted(facts.values(), key=lambda x: x.get('confidence',0))[:5]
for f in low_conf:
    print(f'  [{f.get("confidence",0):.0%}] {f.get("subject","")[:30]} | {f.get("predicate","")[:20]} | {f.get("object","")[:60]}')

# Timeline analysis
print('\n=== TIMELINE ===')
cogs = [e for e in entries if e.get('event_type')=='cognitive_cycle']
if cogs:
    # Group by hour
    hourly = Counter()
    for e in cogs:
        ts = e.get('timestamp',0)
        if isinstance(ts, (int,float)):
            h = datetime.datetime.fromtimestamp(ts).strftime('%H:00')
            hourly[h] += 1
    print('Ciclos por hora:')
    for h in sorted(hourly.keys()):
        bar = '█' * (hourly[h] // 5)
        print(f'  {h} | {hourly[h]:4d} | {bar}')
