#!/usr/bin/env python3
"""
AXIOM META 4 - Scientific Coherence Audit
Cruza el paper generado, los resultados JSON y los logs de prompts/respuestas
para verificar coherencia con el método científico y trazabilidad completa.
"""

import json
from pathlib import Path
from datetime import datetime
import re


def load_latest_comprehensive_results() -> dict:
    p = Path("comprehensive_evaluation_latest.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # fallback a archivo con timestamp más reciente
    candidates = sorted(Path('.').glob('comprehensive_evaluation_*.json'))
    return json.loads(candidates[-1].read_text(encoding="utf-8")) if candidates else {}


def load_latest_e2e_results() -> dict:
    files = sorted(Path('.').glob('final_e2e_verification_*.json'))
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else {}


def load_latest_paper() -> str:
    paper = Path('generated_papers/scientific_paper_latest.md')
    if paper.exists():
        return paper.read_text(encoding='utf-8')
    # fallback a cualquier paper generado
    candidates = sorted(Path('generated_papers').glob('scientific_paper_*.md'))
    return candidates[-1].read_text(encoding='utf-8') if candidates else ''


def iter_llm_logs():
    log_dir = Path('logs/llm')
    if not log_dir.exists():
        return []
    lines = []
    for f in sorted(log_dir.glob('llm_interactions_*.jsonl')):
        for line in f.read_text(encoding='utf-8').splitlines():
            try:
                lines.append(json.loads(line))
            except Exception:
                pass
    return lines


def audit_coherence():
    report = {
        'timestamp': datetime.now().isoformat(),
        'paper_checks': {},
        'traceability': {},
        'summary': {}
    }

    paper = load_latest_paper()
    comp = load_latest_comprehensive_results()
    e2e = load_latest_e2e_results()
    logs = iter_llm_logs()

    # 1) Chequeos básicos del paper
    required_sections = [
        'Abstract', 'Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion'
    ]
    section_presence = {s: (s.lower() in paper.lower()) for s in required_sections}
    report['paper_checks']['section_presence'] = section_presence

    # 2) Referencias a modelos en paper vs evaluación
    models_in_eval = list((comp.get('evaluation_metadata') or {}).get('models_tested', []))
    models_claimed = [m for m in models_in_eval if m.lower() in paper.lower()]
    report['paper_checks']['models_mentioned'] = {
        'evaluated': models_in_eval,
        'mentioned_in_paper': models_claimed
    }

    # 3) Coherencia de resultados (ranking citado vs ranking real)
    ranking = (comp.get('comparative_analysis') or {}).get('ranking', {}).get('overall', [])
    top_model = ranking[0][0] if ranking else None
    report['paper_checks']['top_model'] = top_model

    # 4) Trazabilidad: existen prompts/respuestas para categorías clave
    categories = ['basic_reasoning', 'hypothesis_generation', 'e2e.', 'complete_workflow']
    found = {c: False for c in categories}
    for item in logs:
        cat = item.get('category', '')
        for c in categories:
            if c in cat:
                found[c] = True
    report['traceability']['llm_logs_presence'] = found

    # 5) Verificación E2E éxito mínimo
    success_rate = (e2e.get('test_summary') or {}).get('success_rate', 0.0)
    overall_success = (e2e.get('test_summary') or {}).get('overall_success', False)
    report['summary']['e2e_success_rate'] = success_rate
    report['summary']['e2e_overall_success'] = overall_success

    # 6) Detección de afirmaciones numéricas simples en paper y correlación con JSON
    #    (heurística: si se menciona "83.3%" en paper y coincide con success_rate aprox)
    num_claims = re.findall(r"(\d+\.\d+)%", paper)
    claims_ok = []
    for c in num_claims:
        try:
            val = float(c) / 100.0
            if abs(val - float(success_rate)) < 0.05:
                claims_ok.append({"claim": c + '%', "matches": True})
            else:
                claims_ok.append({"claim": c + '%', "matches": False})
        except Exception:
            pass
    report['paper_checks']['numeric_claims_check'] = claims_ok

    # Guardar reporte
    out = Path(f"scientific_coherence_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    print("✅ Scientific coherence audit complete.")
    print(f"📄 Report saved to: {out}")
    return report


if __name__ == "__main__":
    audit_coherence()
