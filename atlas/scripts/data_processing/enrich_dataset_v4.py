from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import re

IN_PATH = Path('data/plausibility_training_v4_candidates.jsonl')
OUT_PATH = Path('data/plausibility_training_v4_enriched.jsonl')
OUT_PARQUET = Path('data/plausibility_training_v4_enriched.parquet')

try:
    import pandas as pd  # optional
except ImportError:  # pragma: no cover
    pd = None

def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]


def write_jsonl(p: Path, rows: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def compute_features(r: Dict[str, Any]) -> Dict[str, Any]:
    title = (r.get('title') or '').strip()
    abstract = (r.get('abstract') or '').strip()
    year = r.get('year')
    if not isinstance(year, int):
        # Intentar derivar de campos de fecha comunes con formatos variados
        candidate_fields = (
            'published_print','published_online','publication_date','date','created','updated','release_date','first_seen'
        )
        for k in candidate_fields:
            v = r.get(k)
            # Posibles estructuras: dict {'date-parts': [[YYYY,MM,DD]]}, lista, string
            if isinstance(v, dict):
                # Crossref style
                dp = v.get('date-parts') or v.get('date_parts')
                if isinstance(dp, list) and dp and isinstance(dp[0], list) and dp[0] and isinstance(dp[0][0], int):
                    year = dp[0][0]
                    break
            if isinstance(v, (list, tuple)) and v:
                # Listas con números o strings
                first = v[0]
                if isinstance(first, int) and 1500 < first <= datetime.utcnow().year:
                    year = first
                    break
                if isinstance(first, str) and re.match(r'^\d{4}$', first):
                    year = int(first)
                    break
            if isinstance(v, str):
                # Buscar primer año razonable en la cadena
                m = re.search(r'(19|20)\d{2}', v)
                if m:
                    y = int(m.group(0))
                    if 1900 <= y <= datetime.utcnow().year:
                        year = y
                        break
    current_year = datetime.utcnow().year
    citation_count = r.get('citation_count') or r.get('citations') or 0
    influential_count = r.get('influential_citation_count') or 0
    fields = r.get('fields_of_study') or r.get('fields') or []
    if fields is None:
        fields = []

    title_len = len(title.split()) if title else 0
    abstract_len = len(abstract.split()) if abstract else 0
    influential_ratio = (influential_count / citation_count) if citation_count else 0.0
    recency = (current_year - year) if isinstance(year, int) else None
    fields_count = len(fields) if isinstance(fields, list) else 0
    abstract_density = abstract_len / title_len if title_len else 0.0

    # Persistir el year derivado aunque no estuviera originalmente
    # Validación simple: descartar años futuros improbables (> current_year)
    if isinstance(year, int):
        if year > current_year or year < 1900:
            year = None
            recency = None
    else:
        year = None

    return {
        **r,
        'year': year,  # asegurar que quede en el registro enriquecido
        'title_len': title_len,
        'abstract_len': abstract_len,
        'citation_count': citation_count,
        'influential_citation_count': influential_count,
        'influential_ratio': influential_ratio,
        'recency_years': recency,
        'fields_count': fields_count,
        'abstract_title_len_ratio': abstract_density,
    }


def main():
    rows = read_jsonl(IN_PATH)
    if not rows:
        print('No hay datos para enriquecer.')
        return
    enriched = [compute_features(r) for r in rows]
    write_jsonl(OUT_PATH, enriched)
    print(f'Archivo enriquecido JSONL: {OUT_PATH} ({len(enriched)} registros)')
    if pd is not None:
        try:
            import pandas as _pd
            df = _pd.DataFrame(enriched)
            df.to_parquet(OUT_PARQUET, index=False)
            print(f'Archivo Parquet: {OUT_PARQUET}')
        except Exception as e:  # pragma: no cover
            print(f'No se pudo escribir parquet: {e}')


if __name__ == '__main__':
    main()
