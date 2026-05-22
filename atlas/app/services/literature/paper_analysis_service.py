"""Paper Analysis Service (Stub v0)
Reutiliza LiteratureSearchService para:
 - Obtener papers (ya buscados o cache)
 - Calcular métricas de calidad heurísticas
 - Extraer claims simples (regex)
 - Mapear cobertura contra variables de una hipótesis (si se proveen)
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timezone

from app.services.literature_search import LiteratureSearchService
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.database_models import ClaimRecord, PaperQualityMetrics, ClaimRelation
import hashlib
from app.exceptions.domain.mathematics import MathematicsError
from app.types.paper_analysis_service_types import (
    RedFlagsResult,
    MapClaimsToHypothesisResult,
    AnalyzePapersResult,
)


class PaperAnalysisService:
    def __init__(self):
        self.version = "v0"
        self.lit = LiteratureSearchService()
        self._embedder = None  # placeholder para futura carga perezosa

    # --- Quality Metrics (heurísticas) ---
    def _quality_metrics(self, paper: Dict[str, Any]) -> Dict[str, float]:
        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or "").lower()
        text = title + "\n" + abstract
        metrics: Dict[str, float] = {}
        # Transparencia
        transparency_terms = ["code", "dataset", "open source", "supplementary", "github"]
        metrics["transparency_index"] = min(1.0, 0.2 + 0.15 * sum(t in text for t in transparency_terms))
        # Metodología
        method_terms = ["method", "algorithm", "experiment", "protocol", "baseline"]
        metrics["method_score"] = min(1.0, 0.3 + 0.1 * sum(t in text for t in method_terms))
        # Hallazgos
        finding_terms = ["we show", "we demonstrate", "results indicate", "significant"]
        metrics["finding_strength"] = min(1.0, 0.2 + 0.2 * sum(t in text for t in finding_terms))
        # Citas proxy (si disponible)
        citations = paper.get("citations") or 0
        metrics["citation_influence"] = min(1.0, (citations / 100.0))
        # Score agregado simple
        metrics["quality_score"] = round(
            0.3 * metrics["transparency_index"]
            + 0.3 * metrics["method_score"]
            + 0.2 * metrics["finding_strength"]
            + 0.2 * metrics["citation_influence"], 4
        )
        return metrics

    # --- Claim Extraction (regex simple) ---
    CLAIM_PATTERNS = [
        r"we (show|demonstrate|prove|find) that ([^.]{10,160})",
        r"results (indicate|show|suggest) that ([^.]{10,160})",
    ]

    def _extract_claims(self, paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        abstract = paper.get("abstract") or ""
        claims: List[Dict[str, Any]] = []
        for pat in self.CLAIM_PATTERNS:
            for m in re.finditer(pat, abstract, flags=re.IGNORECASE):
                span = m.group(0)
                core = m.group(2) if m.lastindex and m.lastindex >= 2 else span
                claims.append({
                    "text": span.strip(),
                    "core": core.strip(),
                    "confidence": 0.6,  # heurístico fijo
                })
        return claims

    # --- Red Flags heurísticos ---
    def _red_flags(self, paper: RedFlagsResult, claims: List[RedFlagsResult]) -> RedFlagsResult:
        abstract = (paper.get("abstract") or "").lower()
        flags: List[str] = []
        # Exceso de "significant"
        sig_count = abstract.count("significant")
        if sig_count >= 5:
            flags.append("significant_word_inflation")
        # Ausencia de tamaño de muestra típico (n=, sample size)
        if "n=" not in abstract and "sample size" not in abstract:
            flags.append("missing_sample_size")
        # Sin claims extraídos
        if not claims:
            flags.append("no_claims_extracted")
        return {"flags": flags, "significant_mentions": sig_count}

    # --- Embeddings stub (opcional) ---
    def _maybe_embed(self, text: str) -> Optional[List[float]]:
        # Placeholder: no cargar libs pesadas aún.
        return None

    # --- Persistencia best-effort ---
    def _persist(self, paper_payload: Dict[str, Any]) -> None:
        db: Optional[Session] = None
        try:
            db = SessionLocal()
            # Guardar claims
            for idx, c in enumerate(paper_payload.get("claims", [])):
                h = hashlib.sha256(c["core"].encode("utf-8")).hexdigest()[:32]
                rec = ClaimRecord(
                    paper_id=paper_payload.get("paper_id"),
                    paper_title=paper_payload.get("title"),
                    claim_text=c["text"],
                    claim_hash=h,
                    claim_type="finding" if "we show" in c["text"].lower() else None,
                    confidence_score=c.get("confidence", 0.0),
                    extraction_method="heuristic",
                    position=idx,
                    claim_metadata={"core": c["core"]},
                )
                db.add(rec)
            # Agregar PaperQualityMetrics
            metrics_entry = PaperQualityMetrics(
                paper_id=paper_payload.get("paper_id"),
                paper_title=paper_payload.get("title"),
                metrics=paper_payload.get("metrics"),
                claims_summary={
                    "total": len(paper_payload.get("claims", [])),
                },
                coverage_ratio=paper_payload.get("coverage_ratio"),
                ranking_score=paper_payload.get("ranking_score"),
                red_flags=paper_payload.get("red_flags"),
                embeddings=None,
            )
            db.add(metrics_entry)
            db.commit()
        except Exception:
            if db is not None:
                try:
                    db.rollback()
                except Exception:
                    pass
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    def map_claims_to_hypothesis(self, hypothesis_id: str, hypothesis_variables: Optional[List[str]] = None, limit_claims: int = 50) -> MapClaimsToHypothesisResult:
        """Crea ClaimRelation supports cuando core claim contiene alguna variable de la hipótesis.

        Estrategia simple: buscar últimos claims y hacer matching substring lower().
        """
        hypothesis_variables = [v.lower() for v in (hypothesis_variables or []) if isinstance(v, str)]
        if not hypothesis_variables:
            return {"success": False, "error": "No variables provided"}
        db: Optional[Session] = None
        created = 0
        scanned = 0
        try:
            db = SessionLocal()
            # Obtener últimos claims
            q = db.query(ClaimRecord).order_by(ClaimRecord.created_at.desc()).limit(limit_claims)
            claim_rows = q.all()
            for cr in claim_rows:
                scanned += 1
                core = (cr.claim_metadata or {}).get("core") if hasattr(cr, "claim_metadata") else None
                if not core:
                    continue
                lc = core.lower()
                if any(v in lc for v in hypothesis_variables):
                    rel = ClaimRelation(
                        claim_id=cr.id,
                        hypothesis_id=hypothesis_id,
                        relation_type="supports",
                        strength=0.6,
                        evidence={"matched_variables": [v for v in hypothesis_variables if v in lc]},
                    )
                    db.add(rel)
                    created += 1
            db.commit()
            return {"success": True, "created_relations": created, "scanned_claims": scanned}
        except MathematicsError as e:
            if db is not None:
                try:
                    db.rollback()
                except MathematicsError:
                    pass
            return {"success": False, "error": str(e), "created_relations": created, "scanned_claims": scanned}
        finally:
            if db is not None:
                try:
                    db.close()
                except MathematicsError:
                    pass

    def analyze_papers(self, papers: List[AnalyzePapersResult], hypothesis_variables: Optional[List[str]] = None) -> AnalyzePapersResult:
        enriched: List[Dict[str, Any]] = []
        hypothesis_variables = hypothesis_variables or []
        for p in papers:
            metrics = self._quality_metrics(p)
            claims = self._extract_claims(p)
            coverage_hits = 0
            for v in hypothesis_variables:
                if any(v.lower() in (c["core"].lower()) for c in claims):
                    coverage_hits += 1
            coverage_ratio = (coverage_hits / len(hypothesis_variables)) if hypothesis_variables else 0.0
            payload = {
                "paper_id": p.get("paper_id"),
                "title": p.get("title"),
                "metrics": metrics,
                "claims": claims,
                "coverage_ratio": round(coverage_ratio, 3),
            }
            # Red flags
            payload["red_flags"] = self._red_flags(p, claims)
            enriched.append(payload)
        # Ranking por quality_score * (1 + coverage)
        for e in enriched:
            qs = e["metrics"]["quality_score"]
            e["ranking_score"] = round(qs * (1 + e["coverage_ratio"]), 4)
            # Persist best-effort
            self._persist(e)
        enriched.sort(key=lambda x: x["ranking_score"], reverse=True)
        return {
            "version": self.version,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "count": len(enriched),
            "papers": enriched,
        }

paper_analysis_service = PaperAnalysisService()
