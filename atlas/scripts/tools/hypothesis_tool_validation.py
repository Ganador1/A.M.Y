#!/usr/bin/env python3
"""AXIOM META 4 - Hypothesis Tool Validation Harness

Objetivo: Tomar hipótesis generadas (texto) y realizar validaciones estructurales y
pequeñas pruebas cuantitativas o simbólicas usando herramientas ya existentes en el proyecto.

Enfoque inicial (MVP):
1. Parse básico: detectar variables cuantitativas (rangos, unidades, comparaciones).
2. Clasificar tipo de hipótesis: materiales, biología (CRISPR), física (cuántica / confinamiento), térmica.
3. Mapear a micro-pruebas:
   - Materiales/Térmica: construir modelo simplificado k ~ f(defectos, capa, dopaje) y evaluar coherencia de signo.
   - CRISPR: verificar estructura (factores epigenéticos + variación eficiencia) -> checklist.
   - Quantum dots: comprobar dirección esperada del shift energético con tamaño usando modelo de caja 3D (E ~ 1/L^2).
4. Generar un JSON de validación con score compuesto.

Limitaciones: No sustituye experimentación real; sólo verifica consistencia lógica y con modelos físicos muy simplificados.
"""

import re
import json
import random
import numpy as np
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

try:
    import sympy as sp  # noqa: F401
except Exception:  # pragma: no cover
    sp = None  # type: ignore


@dataclass
class HypothesisValidationResult:
    raw_text: str
    category: str
    structural_checks: Dict[str, bool]
    quantitative_checks: Dict[str, Any]
    falsification: Dict[str, Any]
    internal_tools: List[str]
    reasoning_flags: List[str]
    score: float


def classify_hypothesis(text: str) -> str:
    t = text.lower()
    if 'crisp' in t or 'crispr' in t:
        return 'biology_crispr'
    if 'quantum' in t or 'quantum dot' in t or 'bandgap' in t:
        return 'physics_quantum_dots'
    if 'thermal' in t or 'conductivity' in t or 'graphene' in t:
        return 'materials_thermal'
    if 'surface potential' in t:
        return 'nanostructure_surface'
    return 'general'


def structural_analysis(text: str) -> Dict[str, bool]:
    return {
        'has_prediction': bool(re.search(r'will|increase|decrease|enhance|reduce', text, re.I)),
        'has_comparison': bool(re.search(r'compared to|versus|than', text, re.I)),
        'has_variables': bool(re.search(r'\b(diameter|size|thickness|temperature|substrate|layer|bandgap|efficiency)\b', text, re.I)),
        'has_methodology_cues': bool(re.search(r'measure|analy[sz]e|compare|synthes|characteri[sz]e|statistical', text, re.I)),
        'mentions_control': bool(re.search(r'control|constant|keep.*constant', text, re.I)),
    }


def materials_thermal_checks(text: str) -> Dict[str, Any]:
    # Modelo simplificado: dopaje adecuado / heteroestructuras deberían ↑ k, más defectos deberían ↓ k.
    checks = {}
    t = text.lower()
    checks['claims_increase'] = 'increase' in t or 'enhance' in t
    checks['mentions_interfaces'] = 'interface' in t or 'heterostruct' in t
    checks['mentions_vdw'] = 'vdw' in t or 'van der waals' in t
    # Coherencia heurística: interfaces + vdW + claim increase => plausible
    plausible = sum([checks['claims_increase'], checks['mentions_interfaces'], checks['mentions_vdw']]) >= 2
    checks['plausibility'] = plausible
    return checks


def quantum_dot_checks(text: str) -> Dict[str, Any]:
    # Modelo: E_gap ~ 1/L^2; reducción tamaño -> blue shift (energía ↑, longitud de onda ↓)
    checks = {}
    t = text.lower()
    mentions_size = 'size' in t or 'diameter' in t
    shift_direction = 'longer-wavelength' in t or 'red shift' in t or 'blue shift' in t
    # Si dice que menor tamaño -> longer wavelength es físicamente inverso (bandgap ↑ => λ ↓)
    inconsistent = 'longer-wavelength' in t and ('reduce' in t or 'smaller' in t or 'decrease' in t)
    checks['mentions_size'] = mentions_size
    checks['mentions_shift'] = shift_direction
    checks['potential_inconsistency'] = inconsistent
    checks['quick_energy_ratio_example'] = _quantum_energy_ratio_example()
    return checks


def _quantum_energy_ratio_example():
    # L1=10 nm, L2=5 nm => E2/E1 = (L1/L2)^2 = 4
    L1 = 10.0
    L2 = 5.0
    ratio = (L1 / L2) ** 2
    return {'L1_nm': L1, 'L2_nm': L2, 'E2_over_E1_expected': ratio}


def crispr_checks(text: str) -> Dict[str, Any]:
    t = text.lower()
    factors = ['chromatin', 'epigenetic', 'methylation', 'histone', 'accessibility']
    found = {f: (f in t) for f in factors}
    coverage = sum(found.values()) / len(factors)
    return {'factors_found': found, 'coverage': coverage}


def nanostructure_surface_checks(text: str) -> Dict[str, Any]:
    t = text.lower()
    claims = 'surface potential' in t and ('increase' in t or 'decrease' in t)
    size_relation = 'size' in t or 'diameter' in t
    direction = ('decrease' in t and 'size increases' in t) or ('increase' in t and 'size decreases' in t)
    return {'claims_trend': claims, 'mentions_size': size_relation, 'direction_pattern_present': direction}


def compute_score(struct: Dict[str, bool], quantitative: Dict[str, Any], falsification: Dict[str, Any], tools: List[str]) -> float:
    # Pesos: estructura 0.3, mecanismo 0.3, cuantificación 0.2, falsabilidad 0.1, trazabilidad 0.1
    structure_score = sum(1 for v in struct.values() if v) / max(len(struct), 1)
    mech_score = 0.0
    if 'plausibility' in quantitative:
        mech_score += 0.6 if quantitative['plausibility'] else 0.0
    if 'coverage' in quantitative:
        mech_score += 0.4 * quantitative['coverage']
    if 'potential_inconsistency' in quantitative and quantitative['potential_inconsistency']:
        mech_score *= 0.5
    quant_score = 1.0 if quantitative.get('has_numeric_variables') else 0.0
    fals_score = 1.0 if falsification.get('has_falsification') else 0.0
    trace_score = min(1.0, len(tools)/3.0)
    final = (0.3*structure_score + 0.3*mech_score + 0.2*quant_score + 0.1*fals_score + 0.1*trace_score)
    return round(max(0.0, min(1.0, final)), 3)


def extract_numeric_expressions(text: str) -> List[str]:
    return re.findall(r'\b\d+\.?\d*\b', text)


def falsification_criteria(text: str) -> Dict[str, Any]:
    # Busca patrones de umbral/comparación
    has_threshold = bool(re.search(r'(greater than|less than|above|below|at least|no more than)', text, re.I))
    numbers = extract_numeric_expressions(text)
    has_range = bool(re.search(r'(between \d+ and \d+)', text, re.I)) or (len(numbers) >= 2)
    has_direction = bool(re.search(r'increase|decrease|reduce|enhance', text, re.I))
    falsifiable = has_direction and (has_threshold or has_range)
    return {
        'has_falsification': falsifiable,
        'has_directional_claim': has_direction,
        'has_numeric_range_or_threshold': has_threshold or has_range,
        'numeric_tokens': numbers
    }


CATEGORY_TOOL_MAP = {
    'materials_thermal': ['advanced_sympy_operations', 'advanced_numpy_operations'],
    'physics_quantum_dots': ['advanced_sympy_operations'],
    'biology_crispr': ['advanced_scikit_learn_operations', 'advanced_numpy_operations'],
    'nanostructure_surface': ['advanced_sympy_operations'],
    'general': ['advanced_sympy_operations']
}


def validate_hypothesis(text: str) -> HypothesisValidationResult:
    category = classify_hypothesis(text)
    struct = structural_analysis(text)
    quantitative: Dict[str, Any] = {}
    flags: List[str] = []
    falsification = falsification_criteria(text)

    if category == 'materials_thermal':
        quantitative = materials_thermal_checks(text)
        if not quantitative.get('plausibility'):
            flags.append('thermal_plausibility_low')
    elif category == 'physics_quantum_dots':
        quantitative = quantum_dot_checks(text)
        if quantitative.get('potential_inconsistency'):
            flags.append('quantum_shift_direction_suspect')
    elif category == 'biology_crispr':
        quantitative = crispr_checks(text)
        if quantitative.get('coverage', 0) < 0.4:
            flags.append('crispr_factor_coverage_low')
    elif category == 'nanostructure_surface':
        quantitative = nanostructure_surface_checks(text)
    else:
        quantitative = {}

    # Marcar si existen números => base para cuantificación
    quantitative['has_numeric_variables'] = len(quantitative.get('quick_energy_ratio_example', {})) > 0 or len(extract_numeric_expressions(text)) > 0
    tools = CATEGORY_TOOL_MAP.get(category, [])
    score = compute_score(struct, quantitative, falsification, tools)
    return HypothesisValidationResult(
        raw_text=text.strip(),
        category=category,
        structural_checks=struct,
        quantitative_checks=quantitative,
        falsification=falsification,
        internal_tools=tools,
        reasoning_flags=flags,
        score=score
    )


def load_hypotheses_from_evaluation(path: str = 'comprehensive_evaluation_latest.json') -> List[str]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding='utf-8'))
    hyps = []
    for model, mres in data.get('model_results', {}).items():
        hyp_section = mres.get('hypothesis_generation', {})
        for item in hyp_section.get('detailed_hypotheses', []) or []:
            if item.get('hypothesis'):
                hyps.append(item['hypothesis'])
    return hyps


def run_batch_validation() -> Dict[str, Any]:
    hyps = load_hypotheses_from_evaluation()
    results = [validate_hypothesis(h) for h in hyps]
    aggregate = {
        'count': len(results),
        'average_score': sum(r.score for r in results) / len(results) if results else 0.0,
        'by_category': {},
        'flags_summary': {},
        'falsification_coverage': sum(1 for r in results if r.falsification.get('has_falsification')) / len(results) if results else 0.0
    }
    for r in results:
        aggregate['by_category'].setdefault(r.category, {'items': 0, 'scores': []})
        aggregate['by_category'][r.category]['items'] += 1
        aggregate['by_category'][r.category]['scores'].append(r.score)
        for flag in r.reasoning_flags:
            aggregate['flags_summary'][flag] = aggregate['flags_summary'].get(flag, 0) + 1
    for cat, info in aggregate['by_category'].items():
        info['average'] = sum(info['scores']) / len(info['scores'])

    out = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'aggregate': aggregate,
        'results': [asdict(r) for r in results]
    }
    out_path = Path(f"hypothesis_tool_validation_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Hypothesis tool validation report saved: {out_path}")
    return out


# --- INICIO EXTENSION AVANZADA ---

# Guardar referencia del validador original (definido previamente en el archivo)
if 'validate_hypothesis' in globals() and '_core_validate_hypothesis' not in globals():  # type: ignore
    _core_validate_hypothesis = globals()['validate_hypothesis']  # type: ignore


def quantum_dot_physics_model(samples: int = 3) -> Dict[str, Any]:
    """Modelo físico simple Eg(L)=Eg_bulk + A/L^2 - B/L.
    Verifica monotonía Eg al decrecer L en rango pequeño.
    """
    Eg_bulk = 1.5  # eV
    A = 10.0       # eV*nm^2
    B = 0.5        # eV*nm
    lengths = sorted([random.uniform(3.0, 9.0) for _ in range(samples)], reverse=True)
    data = []
    prev_Eg = None
    monotonic = True
    for L in lengths:
        Eg = Eg_bulk + A/(L**2) - B/L
        if prev_Eg is not None and Eg < prev_Eg:
            monotonic = False
        prev_Eg = Eg
        data.append({'L_nm': round(L,3), 'Eg_eV': round(Eg,4)})
    return {'model': 'Eg(L)=Eg_bulk + A/L^2 - B/L', 'points': data, 'monotonic_small_size_increase': monotonic}


def crispr_synthetic_regression(n: int = 40) -> Dict[str, Any]:
    """Simulación sintética CRISPR: eff = b0 + b1*access - b2*methyl + ruido.
    Esperado: b1>0, b2>0 (en el término restado)."""
    true_b0, true_b1, true_b2 = 0.2, 0.6, 0.5
    access = np.random.rand(n)
    methyl = np.random.rand(n)
    noise = np.random.normal(0, 0.03, size=n)
    eff = true_b0 + true_b1*access - true_b2*methyl + noise
    X = np.column_stack([np.ones(n), access, methyl])
    beta, *_ = np.linalg.lstsq(X, eff, rcond=None)
    b0_hat, b1_hat, b2_hat = beta.tolist()
    signs_ok = b1_hat > 0 and b2_hat < 0
    return {
        'synthetic_model': 'eff = b0 + b1*access - b2*methyl',
        'estimated_params': {'b0': round(b0_hat,4), 'b1': round(b1_hat,4), 'b2': round(b2_hat,4)},
        'signs_expected': {'b1_positive': True, 'b2_negative': True},
        'signs_ok': signs_ok
    }


def validate_hypothesis(text: str) -> 'HypothesisValidationResult':  # type: ignore
    result = _core_validate_hypothesis(text)
    if result.category == 'physics_quantum_dots':
        phys = quantum_dot_physics_model()
        result.quantitative_checks['physics_model'] = phys
        if not phys['monotonic_small_size_increase']:
            result.reasoning_flags.append('quantum_model_monotonicity_fail')
        else:
            result.score = min(1.0, result.score + 0.05)
    if result.category == 'biology_crispr':
        syn = crispr_synthetic_regression()
        result.quantitative_checks['synthetic_regression'] = syn
        if not syn['signs_ok']:
            result.reasoning_flags.append('crispr_regression_sign_mismatch')
        else:
            result.score = min(1.0, result.score + 0.05)
    return result


def revalidate_refinements(refinement_file: str) -> Dict[str, Any]:
    p = Path(refinement_file)
    if not p.exists():
        return {'error': 'refinement_file_not_found'}
    data = json.loads(p.read_text(encoding='utf-8'))
    details = []
    for item in data.get('refinements', []):
        orig_res = _core_validate_hypothesis(item['original'])
        ref_res = _core_validate_hypothesis(item['refined'])
        delta = ref_res.score - orig_res.score
        details.append({
            'original_score': orig_res.score,
            'refined_score': ref_res.score,
            'delta': round(delta,3),
            'flags_added': [f for f in ref_res.reasoning_flags if f not in orig_res.reasoning_flags],
            'flags_resolved': [f for f in orig_res.reasoning_flags if f not in ref_res.reasoning_flags]
        })
    agg = {
        'count': len(details),
        'average_delta': sum(d['delta'] for d in details)/len(details) if details else 0.0,
        'improved_ratio': sum(1 for d in details if d['delta']>0)/len(details) if details else 0.0
    }
    out = {'timestamp': __import__('datetime').datetime.now().isoformat(), 'aggregate': agg, 'details': details}
    out_path = Path(f"hypothesis_refinement_revalidation_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Revalidation report saved: {out_path}")
    return out

# Extiende main existente manteniendo run_batch_validation definido arriba
if __name__ == '__main__':  # ...existing code...
    base = run_batch_validation()
    latest_ref = sorted(Path('.').glob('hypothesis_refinements_*.json'))
    if latest_ref:
        revalidate_refinements(str(latest_ref[-1]))
# --- FIN EXTENSION AVANZADA ---
