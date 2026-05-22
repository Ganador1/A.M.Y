"""Prometheus-style metrics exposure (lightweight, no external deps).

Extensión:
 - Soporte de labels (fase, dominio, etc.).
 - Counters, Gauges, Histograms.
 - Proveedor de tiempo inyectable para tests.
 - Métricas de éxito de fases sin romper compatibilidad previa.
"""
from __future__ import annotations
import threading
import time
from typing import Dict, List, Tuple, Optional, Callable

_LOCK = threading.RLock()

# Internal storage (metric -> {labelset -> value|list})
LabelSet = Tuple[Tuple[str, str], ...]
_COUNTERS: Dict[str, Dict[LabelSet, float]] = {}
_HISTOGRAMS: Dict[str, Dict[LabelSet, List[float]]] = {}
_GAUGES: Dict[str, Dict[LabelSet, float]] = {}

# Cardinalidad máxima de series por métrica (para evitar explosión)
_MAX_SERIES_PER_METRIC = 50
_OVERFLOW_LABELSET: LabelSet = (('overflow', 'true'),)

_DEFAULT_BUCKETS = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

_time_provider: Callable[[], float] = time.time


# --------------------- Utilidades de tiempo ---------------------
def set_time_provider(fn: Callable[[], float]):  # pragma: no cover
    global _time_provider
    _time_provider = fn


def reset_time_provider():  # pragma: no cover
    global _time_provider
    _time_provider = time.time


def _now() -> float:
    return _time_provider()


# --------------------- Helpers de labels ---------------------
def _norm_labels(labels: Optional[Dict[str, str]]) -> LabelSet:
    if not labels:
        return tuple()
    return tuple(sorted((str(k), str(v)) for k, v in labels.items()))


def _labels_to_text(labelset: LabelSet) -> str:
    if not labelset:
        return ''
    inner = ','.join(f'{k}="{v}"' for k, v in labelset)
    return '{' + inner + '}'


def _merge_label(base: str, le_value: str) -> str:
    # base: '' o '{phase="x",domain="y"}'
    if not base:
        return f'{{le="{le_value}"}}'
    inner = base[1:-1]
    # Construimos la llave final fuera del f-string para evitar necesidad de escapar
    return '{' + inner + f',le="{le_value}"' + '}'


# --------------------- API de métricas ---------------------
def inc(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
    labelset = _norm_labels(labels)
    with _LOCK:
        series = _COUNTERS.setdefault(name, {})
        if labelset not in series and len(series) >= _MAX_SERIES_PER_METRIC and labelset != _OVERFLOW_LABELSET:
            # Redirigir a serie overflow
            series = _COUNTERS[name]
            series[_OVERFLOW_LABELSET] = series.get(_OVERFLOW_LABELSET, 0.0) + value
            return
        series[labelset] = series.get(labelset, 0.0) + value


def gauge_set(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    labelset = _norm_labels(labels)
    with _LOCK:
        series = _GAUGES.setdefault(name, {})
        if labelset not in series and len(series) >= _MAX_SERIES_PER_METRIC and labelset != _OVERFLOW_LABELSET:
            series[_OVERFLOW_LABELSET] = float(value)
            return
        series[labelset] = float(value)


def gauge_inc(name: str, delta: float = 1.0, labels: Optional[Dict[str, str]] = None):  # pragma: no cover
    labelset = _norm_labels(labels)
    with _LOCK:
        series = _GAUGES.setdefault(name, {})
        if labelset not in series and len(series) >= _MAX_SERIES_PER_METRIC and labelset != _OVERFLOW_LABELSET:
            series[_OVERFLOW_LABELSET] = series.get(_OVERFLOW_LABELSET, 0.0) + delta
            return
        series[labelset] = series.get(labelset, 0.0) + delta


def observe(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    labelset = _norm_labels(labels)
    with _LOCK:
        series = _HISTOGRAMS.setdefault(name, {})
        # Redirigir overflow si excede cardinalidad
        if labelset not in series and len(series) >= _MAX_SERIES_PER_METRIC and labelset != _OVERFLOW_LABELSET:
            labelset = _OVERFLOW_LABELSET
        lst = series.setdefault(labelset, [])
        lst.append(value)
        if len(lst) > 5000:  # evitar crecimiento ilimitado
            series[labelset] = lst[-5000:]


# --------------------- Métricas derivadas ---------------------
def update_phase_success_ratio(phase: str, domain: Optional[str] = None):
    """Actualiza gauge de ratio de éxito por fase (éxitos/(éxitos+fallos)).

    Se apoya en counters existentes:
      - atlas_phase_success_total (con y sin labels)
      - atlas_phase_failures_total (con y sin labels)
    """
    with _LOCK:
        success_series = _COUNTERS.get("atlas_phase_success_total", {})
        failure_series = _COUNTERS.get("atlas_phase_failures_total", {})
        # Etiquetas específicas
        base_labels: Dict[str, str] = {"phase": phase}
        if domain:
            base_labels["domain"] = domain
        labelset = _norm_labels(base_labels)
        succ = success_series.get(labelset, 0.0)
        fail = failure_series.get(labelset, 0.0)
        if succ + fail > 0:
            ratio = succ / (succ + fail)
            gseries = _GAUGES.setdefault("atlas_phase_success_ratio", {})
            gseries[labelset] = ratio
        # Global (sin labels)
        g_succ = success_series.get(tuple(), 0.0)
        g_fail = failure_series.get(tuple(), 0.0)
        if g_succ + g_fail > 0:
            gseries = _GAUGES.setdefault("atlas_phase_success_ratio", {})
            gseries[tuple()] = g_succ / (g_succ + g_fail)


# --------------------- Render de histogramas ---------------------
def _count_le(sorted_vals: List[float], bound: float) -> int:
    c = 0
    for v in sorted_vals:
        if v <= bound:
            c += 1
        else:
            break
    return c


def _histogram_lines(name: str, values: List[float], labelset: LabelSet) -> List[str]:
    sorted_vals = sorted(values)
    total = len(sorted_vals)
    base = _labels_to_text(labelset)
    lines: List[str] = []
    for b in _DEFAULT_BUCKETS:
        cnt = _count_le(sorted_vals, b)
        lines.append(f"{name}_bucket{_merge_label(base, str(b))} {cnt}")
    lines.append(f"{name}_bucket{_merge_label(base, '+Inf')} {total}")
    lines.append(f"{name}_sum{base} {sum(sorted_vals):.6f}")
    lines.append(f"{name}_count{base} {total}")
    return lines


# --------------------- HELP/TYPE heurístico ---------------------
def _auto_help(name: str) -> str:
    if name.startswith('atlas_phase_duration'):
        return 'Duration of research cycle phases (seconds)'
    if name.startswith('atlas_convergence_time'):
        return 'Time to convergence in refinement loop (seconds)'
    if name.startswith('atlas_phase_failures'):
        return 'Phase failures count'
    if name.startswith('atlas_phase_success'):
        return 'Phase successes count'
    if name.startswith('atlas_refinement_iterations'):
        return 'Refinement iterations'
    if name.startswith('atlas_refinement_cycles'):
        return 'Refinement cycles'
    if name.startswith('atlas_feedback_total'):
        return 'Total feedback events'
    if name.startswith('atlas_active_cycles'):
        return 'Active research cycles'
    if name.startswith('atlas_phase_success_ratio'):
        return 'Phase success ratio (success/(success+failures))'
    if name.startswith('atlas_cycle_total_duration'):
        return 'Total duration of complete research cycles (seconds)'
    if name.startswith('atlas_refinement_iterations_per_cycle'):
        return 'Refinement iterations distribution per cycle'
    if name.startswith('atlas_phase_active'):
        return 'Number of phases active concurrently'
    return name


# --------------------- Scrape ---------------------
def scrape() -> str:
    with _LOCK:
        parts: List[str] = []

        def emit_help_type(metric: str, mtype: str):
            parts.append(f"# HELP {metric} {_auto_help(metric)}")
            parts.append(f"# TYPE {metric} {mtype}")

        # Counters
        for name, series in _COUNTERS.items():
            emit_help_type(name, 'counter')
            for labelset, val in series.items():
                parts.append(f"{name}{_labels_to_text(labelset)} {val}")
        # Gauges
        for name, series in _GAUGES.items():
            emit_help_type(name, 'gauge')
            for labelset, val in series.items():
                parts.append(f"{name}{_labels_to_text(labelset)} {val}")
        # Histograms
        for name, series in _HISTOGRAMS.items():
            emit_help_type(name, 'histogram')
            for labelset, vals in series.items():
                parts.extend(_histogram_lines(name, vals, labelset))
        return "\n".join(parts) + "\n"


# --------------------- Reset ---------------------
def reset_metrics():  # pragma: no cover
    with _LOCK:
        _COUNTERS.clear()
        _HISTOGRAMS.clear()
        _GAUGES.clear()
    reset_time_provider()


# --------------------- PhaseTimer ---------------------
class PhaseTimer:
    def __init__(self, domain: Optional[str] = None):
        self._start: float | None = None
        self.domain = domain
    def start(self):
        self._start = _now()
        # Incrementar gauge de fase activa si conocemos la fase luego en stop (solo al finalizar sabremos la fase) -> no posible aún
    def stop(self, phase: str):
        if self._start is None:
            return
        duration = _now() - self._start
        # Compat (métricas antiguas sin labels)
        observe("atlas_phase_duration_seconds", duration)
        inc(f"atlas_phase_count_{phase}")
        # Éxitos agregados (nuevo)
        inc("atlas_phase_success_total")  # global sin labels
        inc(f"atlas_phase_success_{phase}")  # específico por fase (compat estilo antiguo)
        # Versión con labels
        labels = {"phase": phase}
        if self.domain:
            labels["domain"] = self.domain
        observe("atlas_phase_duration_seconds", duration, labels=labels)
        inc("atlas_phase_success_total", labels=labels)
        # Actualizar ratio éxito tras cada fin de fase
        try:
            update_phase_success_ratio(phase, self.domain)
        except Exception:  # pragma: no cover
            pass
        self._start = None


class phase_activity:
    """Context manager para exponer gauge atlas_phase_active{phase,domain}."""
    def __init__(self, phase: str, domain: Optional[str] = None):
        self.phase = phase
        self.domain = domain
    def __enter__(self):
        try:
            gauge_inc("atlas_phase_active", 1, labels={k: v for k, v in {"phase": self.phase, "domain": self.domain}.items() if v})
            gauge_inc("atlas_phase_active", 1)
        except Exception:  # pragma: no cover
            pass
        return self
    def __exit__(self, exc_type, exc, tb):
        try:
            gauge_inc("atlas_phase_active", -1, labels={k: v for k, v in {"phase": self.phase, "domain": self.domain}.items() if v})
            gauge_inc("atlas_phase_active", -1)
        except Exception:  # pragma: no cover
            pass


def phase_timer(domain: Optional[str] = None) -> PhaseTimer:
    return PhaseTimer(domain=domain)
