"""Plausibility Dataset Builder

Objetivo: ensamblar un dataset etiquetado (weak supervision) para entrenar el modelo de plausibilidad.
Incluye stubs para fuentes externas (PeerRead, OpenAlex, Retracted) que el usuario completará.

Flujo:
 1. Cargar registros base (title, abstract, meta) -> lista de dicts
 2. Enriquecer con métricas (citations, decisiones, flags retract) -> merge
 3. Asignar etiqueta weak (label)
 4. Calcular features estructurales + semánticas sencillas (sin embeddings pesados todavía)
 5. Emitir JSONL listo para training

NOTA: Las descargas reales de datasets externos se marcan como TODO para evitar llamadas de red.
"""
from __future__ import annotations
from typing import List, Dict, Any, Iterable, Optional
import json
import math
from pathlib import Path
import random
import aiofiles
import asyncio

# --------------------------- Fuentes (Stubs) ---------------------------------

def load_peerread_metadata(path: str = "external/peerread") -> List[Dict[str, Any]]:
    """Carga subset PeerRead.
    Esperado: registros con keys: paper_id, title, abstract, decision ('accept'/'reject'), year, venue
    TODO: Implementar parsing real. Aquí devolvemos lista vacía si no existe.
    """
    p = Path(path)
    if not p.exists():
        return []
    # TODO: parse real JSON / *.txt
    return []

def load_retracted_index(path: str = "external/retracted") -> List[str]:
    """Lista de paper_ids retractados (stub)."""
    p = Path(path) / "retracted_ids.txt"
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]

def enrich_with_openalex(records: List[Dict[str, Any]]):
    """Stub para enriquecer cada registro con cited_by_count, concepts.
    TODO: Integrar cliente OpenAlex offline / cache.
    """
    for r in records:
        r.setdefault("cited_by_count", random.randint(0, 50))  # proxy
        r.setdefault("concepts", ["computer science"])  # proxy single concept

# --------------------------- Etiquetado ---------------------------------------

def assign_weak_label(record: Dict[str, Any], retract_ids: Optional[Iterable[str]] = None) -> int:
    retract_ids = set(retract_ids or [])
    if record.get("paper_id") in retract_ids:
        return 0
    decision = (record.get("decision") or "").lower()
    if decision == "accept":
        return 1
    if decision == "reject":
        return 0
    # fallback heurístico: citas altas implican más plausibilidad
    cites = record.get("cited_by_count", 0)
    return 1 if cites >= 5 else 0

# --------------------------- Feature Engineering -----------------------------

TECH_TOKENS = {"quantum","entropy","gradient","protein","enzyme","nanoparticle","bayesian","inference","coherence"}


def compute_features(record: Dict[str, Any]) -> Dict[str, float]:
    title = (record.get("title") or "").strip()
    abstract = (record.get("abstract") or "").strip()
    cited = int(record.get("cited_by_count", 0))
    words = abstract.split()
    length = len(words)
    tech_count = sum(1 for w in words if w.lower().strip('.,;:()') in TECH_TOKENS)
    technical_density = tech_count / length if length else 0.0
    title_len_norm = min(1.0, len(title)/160.0)
    abstract_len_norm = min(1.0, len(abstract)/2000.0)
    citation_bucket = math.log1p(cited) / math.log(1+100)  # normaliza citaciones (0..~1)
    has_question = 1.0 if "?" in title else 0.0
    features = {
        "title_len": title_len_norm,
        "abstract_len": abstract_len_norm,
        "citation_norm": citation_bucket,
        "technical_density": technical_density,
        "has_question": has_question,
    }
    return features

# --------------------------- Builder Principal -------------------------------

def build_dataset(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    peer = load_peerread_metadata()
    retract_ids = load_retracted_index()
    records = peer  # se podrían añadir otras fuentes
    enrich_with_openalex(records)
    out: List[Dict[str, Any]] = []
    for rec in records:
        label = assign_weak_label(rec, retract_ids)
        feats = compute_features(rec)
        out.append({
            "paper_id": rec.get("paper_id"),
            "title": rec.get("title"),
            "abstract": rec.get("abstract"),
            "label": label,
            "year": rec.get("year"),
            "venue": rec.get("venue"),
            "features": feats
        })
    if limit:
        out = out[:limit]
    return out

# --------------------------- Persistencia ------------------------------------

def write_jsonl(records: List[Dict[str, Any]], path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

__all__ = [
    "build_dataset",
    "write_jsonl",
    "compute_features",
    "assign_weak_label"
]
