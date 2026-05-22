"""
DNABERT-2 Genomics Service (ligero)
Provee utilidades básicas inspiradas en DNABERT-2:
- encode_sequence: tokeniza secuencias de ADN en k-mers
- predict_motifs: heurística simple para motivos conocidos (TATA, CpG)
- classify_promoter: clasificación binaria sencilla basada en motivos

Nota: Implementación minimal sin modelo pesado. Lista para intercambiar por
un backend real (HF model) si se requiere.
"""

from __future__ import annotations

from typing import Dict, Any, List
from dataclasses import dataclass

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger


ALPHABET = set("ACGTN")


def _sanitize_sequence(seq: str) -> str:
    s = (seq or "").upper().replace("\n", "").replace(" ", "")
    if not s or any(ch not in ALPHABET for ch in s):
        raise ValueError("Invalid DNA sequence: must contain only A,C,G,T,N")
    return s


def _kmers(seq: str, k: int) -> List[str]:
    if k <= 0:
        raise ValueError("k must be > 0")
    if len(seq) < k:
        return []
    return [seq[i : i + k] for i in range(len(seq) - k + 1)]


@dataclass
class DNABert2Config:
    """
    Configuration for DNABERT-2 genomics service.
    
    Attributes:
        k: K-mer size for sequence tokenization (default: 6)
    """
    k: int = 6


class DNABERT2GenomicsService(BaseService):
    """
    Lightweight DNABERT-2 inspired genomics service.
    
    Provides basic genomic sequence analysis utilities including k-mer tokenization,
    motif prediction, and promoter classification. This is a simplified implementation
    that can be replaced with a full HuggingFace model backend when needed.
    
    Attributes:
        config: Service configuration including k-mer size
    """
    def __init__(self, config: DNABert2Config | None = None):
        super().__init__("DNABERT2Genomics")
        self.config = config or DNABert2Config()
        logger.info("✅ DNABERT2GenomicsService initialized (lightweight mode)")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = request_data.get("action", "")
            if action == "encode_sequence":
                return self.encode_sequence(request_data)
            if action == "predict_motifs":
                return self.predict_motifs(request_data)
            if action == "classify_promoter":
                return self.classify_promoter(request_data)
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": ["encode_sequence", "predict_motifs", "classify_promoter"],
            }
        except Exception as e:
            return self.handle_error(e, "process_request")

    def encode_sequence(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            seq = _sanitize_sequence(request_data.get("sequence", ""))
            k = int(request_data.get("k", self.config.k))
            tokens = _kmers(seq, k)
            return {"success": True, "k": k, "length": len(seq), "tokens": tokens}
        except Exception as e:
            return self.handle_error(e, "encode_sequence")

    def predict_motifs(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            seq = _sanitize_sequence(request_data.get("sequence", ""))
            motifs = {
                "TATA_box": [i for i in range(len(seq) - 3) if seq[i : i + 4] == "TATA"],
                "CpG_islands": [i for i in range(len(seq) - 1) if seq[i : i + 2] == "CG"],
            }
            return {"success": True, "sequence_length": len(seq), "motifs": motifs}
        except Exception as e:
            return self.handle_error(e, "predict_motifs")

    def classify_promoter(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            seq = _sanitize_sequence(request_data.get("sequence", ""))
            has_tata = "TATA" in seq
            cpg_count = sum(seq[i : i + 2] == "CG" for i in range(len(seq) - 1))
            # Heurística simple
            score = (0.6 if has_tata else 0.2) + min(0.4, cpg_count * 0.02)
            label = "promoter" if score >= 0.5 else "non_promoter"
            return {"success": True, "label": label, "confidence": round(score, 3), "cpg": cpg_count, "has_tata": has_tata}
        except Exception as e:
            return self.handle_error(e, "classify_promoter")

# Alias for backward compatibility
DNABERT2Service = DNABERT2GenomicsService

__all__ = ["DNABERT2GenomicsService", "DNABERT2Service"]
