from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

# Demostración de teoremas / verificación formal
theorems_proven = Counter("theorems_proven_total", "Total de teoremas demostrados")
proof_time = Histogram("proof_time_seconds", "Tiempo de verificación/demostración")
proof_complexity = Gauge("proof_complexity", "Complejidad de la última prueba (heurística)")

# SMT
smt_verifications = Counter("smt_verifications_total", "Total verificaciones SMT ejecutadas")
smt_refutations = Counter("smt_refutations_total", "Total refutaciones SMT encontradas")

# Computación cuántica
quantum_circuits_run = Counter("quantum_circuits_total", "Circuitos cuánticos ejecutados")
quantum_depth = Histogram("quantum_circuit_depth", "Profundidad de circuitos cuánticos")
quantum_advantage = Gauge("quantum_advantage_ratio", "Ventaja cuántica estimada")

# Astronomía
transit_candidates = Counter("astro_transit_candidates_total", "Candidatos a tránsito detectados")

# Partículas
lhc_events_analyzed = Counter("lhc_events_analyzed_total", "Eventos analizados (stub)")
jets_detected = Histogram("lhc_jets_detected", "Conteo de jets detectados por evento (stub)")
