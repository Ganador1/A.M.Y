#!/usr/bin/env python3
"""
E2E scientific-pipeline validation — the real A.M.Y flow, everything on.

For one domain this script exercises the COMPLETE production path:

  1. REAL Atlas tool calls through the persistent worker (PySCF, SymPy, NumPy…)
     — no precomputed/fixture results anywhere.
  2. Provenance recorded per call (SHA-256 of full output + environment).
  3. Paper generated with every validated mechanism enabled:
       AMY_USE_LLM_ENHANCER=1   LLM-written, provenance-grounded Discussion
       AMY_USE_LLM_JUDGE=1      LLM scientific-debate ranking judge
       AMY_USE_EVOLUTION=1      Co-Scientist Evolution agent on top hypotheses
  4. E2E verification: provenance hashes recomputed, prepublication gate,
     reflection, full rubric + Discussion-only judge scores.

Outputs one JSON (path printed last) with every artifact + check, so an
auditing agent can verify each step independently.

Usage:
    .venv/bin/python scripts/run/run_e2e_validation.py --domain mathematics
    .venv/bin/python scripts/run/run_e2e_validation.py --list
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Everything ON — set before imports that read env at call time.
os.environ.setdefault("AMY_USE_LLM_ENHANCER", "1")
os.environ.setdefault("AMY_USE_LLM_JUDGE", "1")
os.environ.setdefault("AMY_USE_EVOLUTION", "1")

from core.atlas_tools import AtlasTools  # noqa: E402
from core.provenance import ProvenanceManager  # noqa: E402
from communication.paper_generator import PaperGenerator  # noqa: E402
from cognition.reflection_agent import reflect  # noqa: E402

OUT_DIR = ROOT / "experiments" / "e2e_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Evidence-grade tool plans per domain. Inputs follow ATLAS_TOOL_GUIDE formats;
# a failed tool is recorded (not fabricated around) and the run proceeds if at
# least two calls succeeded.
DOMAIN_PLANS = {
    "mathematics": {
        "topic": "Prime gap scaling across four decades of N",
        "calls": [
            ("prime_gap_analysis", "100000", "Prime gap analysis up to 1e5"),
            ("prime_gap_analysis", "1000000", "Prime gap analysis up to 1e6"),
            ("sympy_prime_analysis", "1000003", "Primality analysis of 1000003"),
        ],
    },
    "chemistry": {
        "topic": "Hartree-Fock binding of small diatomics versus Hückel π-systems",
        "calls": [
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 0.74", "HF/STO-3G energy of H2 at 0.74 Å"),
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 1.10", "HF/STO-3G energy of stretched H2 at 1.10 Å"),
            ("molecular_orbital_energy", "C4H6", "Hückel MO analysis of butadiene"),
        ],
    },
    "physics": {
        "topic": "Hydrogen Rydberg scaling as a quantum calibration control",
        "calls": [
            ("quantum_energy_levels", "5", "Hydrogen energy levels n=1..5"),
            ("quantum_energy_levels", "10", "Hydrogen energy levels n=1..10"),
        ],
    },
    "astronomy": {
        "topic": "Planck18 cosmological distances and blackbody peaks",
        "calls": [
            ("astropy_cosmology", "z=1.0", "Cosmological distances at z=1"),
            ("astropy_blackbody", "5778", "Blackbody spectrum at solar temperature"),
        ],
    },
    "statistics": {
        "topic": "Two-sample inference on synthetic measurement series",
        "calls": [
            ("numpy_statistics", "12.1, 11.8, 12.4, 12.0, 11.9, 12.3, 12.2", "Descriptive statistics of series A"),
            ("hypothesis_tester", "12.1,11.8,12.4,12.0 vs 12.9,13.1,12.7,13.0", "Two-sample t-test A vs B"),
        ],
    },
    "biology": {
        "topic": "Compositional analysis of a GC-rich coding fragment",
        "calls": [
            ("dna_analyzer", "ATGGCGCGCTAAGGCGCGATCGCGGCTA", "DNA composition analysis"),
            ("protein_properties", "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ", "Protein property analysis"),
        ],
    },
}

SECTION_STUB = [
    {"heading": "Introduction", "content": "E2E validation run."},
