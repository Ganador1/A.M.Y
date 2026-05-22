from __future__ import annotations
"""Comparador de modelos de plausibilidad v4.

Entrada potencial:
 - models/plausibility_v4_rf.pkl (baseline, incluye alt_models / calibration / temporal)
 - models/plausibility_v4_rf_regularized.pkl (opcional)
 - models/plausibility_v4_no_cits.pkl (opcional)
 - models/plausibility_v4_logreg.pkl (opcional)

Salida:
 - models/plausibility_v4_comparison.json
 - models/plausibility_v4_comparison.md
"""
import json
from pathlib import Path
import joblib
from datetime import datetime

BASE = Path('models/plausibility_v4_rf.pkl')
OUT_JSON = Path('models/plausibility_v4_comparison.json')
OUT_MD = Path('models/plausibility_v4_comparison.md')
CANDIDATES = {
    'baseline_rf': BASE,
    'rf_regularized': Path('models/plausibility_v4_rf_regularized.pkl'),
    'no_cits_rf': Path('models/plausibility_v4_no_cits.pkl'),
    'logreg': Path('models/plausibility_v4_logreg.pkl'),
}


def load_model(path: Path):
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None


def extract_metrics(obj) -> dict:
    if obj is None:
        return {'available': False}
    def pick(keys):
        return {k: obj.get(k) for k in keys if k in obj}
    meta = {'available': True}
    meta.update(pick(['auc','f1','f1_opt','threshold_opt','brier','ece','overfit_risk']))
    for k in ['calibration','alt_models','temporal_metrics','cv']:
        if k in obj and obj.get(k):
            meta[k] = obj[k]
    return meta


def main():
    baseline = load_model(BASE)
    results = {
        'generated_at': datetime.utcnow().isoformat()+'Z',
        'models': {
            'baseline_rf': extract_metrics(baseline)
        }
    }

    # Modelos adicionales
    for name, path in CANDIDATES.items():
        if name == 'baseline_rf':
            continue
        obj = load_model(path)
        payload = obj.get('model_meta', obj) if obj else None
        results['models'][name] = extract_metrics(payload)

    base_auc = results['models']['baseline_rf'].get('auc')
    comparisons = []
    for name, data in results['models'].items():
        if name == 'baseline_rf' or not data.get('available'):
            continue
        delta = (data.get('auc') - base_auc) if (base_auc and data.get('auc')) else None
        comparisons.append({
            'model': name,
            'auc': data.get('auc'),
            'delta_auc_vs_baseline': delta,
            'f1_opt': data.get('f1_opt')
        })
    results['comparisons'] = comparisons

    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

    # Markdown
    lines = [
        '# Plausibility Model Comparison (v4)',
        '',
        f"Generated: {results['generated_at']}",
        '\n## Baseline',
        json.dumps(results['models']['baseline_rf'], ensure_ascii=False, indent=2),
        '\n## Other Models'
    ]
    lines.extend([f"- {c['model']}: AUC={c.get('auc')} ΔAUC={c.get('delta_auc_vs_baseline')} F1_opt={c.get('f1_opt')}" for c in comparisons])
    OUT_MD.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f"Comparación guardada en {OUT_JSON} y {OUT_MD}")

if __name__ == '__main__':
    main()
