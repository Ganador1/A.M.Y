"""Fact-checking: verificar referencias y claims numéricas."""
import json
import re
from pathlib import Path
from collections import Counter

# 1. Extraer referencias de papers
all_refs = []
for p in Path('papers').glob('*.md'):
    text = p.read_text()
    if '## References' in text:
        ref_section = text.split('## References')[-1]
        refs = [l.strip() for l in ref_section.split('\n') if l.strip() and l.strip()[0].isdigit()]
        all_refs.extend(refs)

unique = set()
for r in all_refs:
    clean = re.sub(r'^\d+\.\s*', '', r).strip()
    unique.add(clean[:100])

print(f'Total citas en papers: {len(all_refs)}')
print(f'Citas únicas: {len(unique)}')
print('\nCITAS RECOPILADAS (verificar si son reales):')
for i, r in enumerate(sorted(unique)[:30], 1):
    print(f'  {i}. {r}')

# 2. Claims numéricas del knowledge graph
print('\n=== CLAIMS VERIFICABLES CON DATOS NUMERICOS ===')
with open('data/knowledge_graph.json') as f:
    kg = json.load(f)
facts = kg.get('facts', {})

numeric_claims = []
for fk, fv in facts.items():
    obj = str(fv.get('object', ''))
    if any(c.isdigit() for c in obj) and float(fv.get('confidence', 0)) > 0.7:
        numeric_claims.append(fv)

print(f'Claims con datos numéricos (confianza >70%): {len(numeric_claims)}')
for c in sorted(numeric_claims, key=lambda x: -x.get('confidence', 0))[:20]:
    subj = str(c.get('subject', ''))[:30]
    pred = str(c.get('predicate', ''))[:25]
    obj = str(c.get('object', ''))[:80]
    conf = c.get('confidence', 0)
    print(f'  [{conf:.0%}] {subj} | {pred} | {obj}')

# 3. Repetición de papers
print('\n=== REPETITIVIDAD DE PAPERS ===')
paper_titles = []
for p in sorted(Path('papers').glob('*.md'), key=lambda x: x.stat().st_mtime):
    text = p.read_text()
    title = text.split('\n')[0].replace('# ', '')
    paper_titles.append(title[:80])
    
title_counts = Counter(paper_titles)
for t, c in title_counts.most_common(5):
    print(f'  [{c}x] {t}')

# 4. Diversidad de contenido entre papers
print('\n=== DIVERSIDAD ENTRE PAPERS ===')
md_files = sorted(Path('papers').glob('*.md'), key=lambda x: x.stat().st_mtime)
if len(md_files) >= 2:
    first = md_files[0].read_text()
    last = md_files[-1].read_text()
    fw = set(first.lower().split())
    lw = set(last.lower().split())
    overlap = len(fw & lw) / max(len(fw | lw), 1)
    print(f'Overlap léxico primer vs último paper: {overlap:.0%}')
    print(f'Palabras primer paper: {len(first.split())}')
    print(f'Palabras último paper: {len(last.split())}')

# 5. Qué tan diversas son las queries?
print('\n=== DIVERSIDAD DE QUERIES ===')
entries = [json.loads(l) for l in open('data/episodic_memory.jsonl') if l.strip()]
research = [e for e in entries if e.get('event_type') == 'research']
queries = [e.get('metadata', {}).get('query', '') for e in research]
unique_q = set(q[:60] for q in queries)
print(f'Queries totales: {len(queries)}')
print(f'Queries únicas (60 chars): {len(unique_q)}')
print(f'Repetición: {100*(1-len(unique_q)/max(len(queries),1)):.0f}%')
