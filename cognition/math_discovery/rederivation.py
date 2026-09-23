"""Blind rederivation comparison without treating lexical overlap as proof."""
from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "a", "an", "and", "by", "for", "from", "if", "in", "is", "of", "or",
    "the", "then", "to", "with",
}
_ALIASES = {
    "two": "2",
    "three": "3",
    "five": "5",
    "divisible": "divide",
    "divisibility": "divide",
    "divides": "divide",
}


@dataclass(frozen=True)
class BlindDerivation:
    job_id: str
    artifact_hash: str
    mechanism: str
    lemmas: tuple[str, ...]
    gaps: tuple[str, ...] = ()


@dataclass(frozen=True)
class RederivationReport:
    passed: bool
    overlap_score: float
    aligned_lemma_pairs: tuple[tuple[int, int], ...]
    evidence_hashes: tuple[str, ...]
    gaps: tuple[str, ...]


def _tokens(value: str) -> set[str]:
    return {
        _ALIASES.get(token, token)
        for token in _TOKEN.findall(value.lower())
        if token not in _STOP
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def compare_blind_derivations(
    left: BlindDerivation,
    right: BlindDerivation,
    *,
    minimum_lemma_overlap: float = 0.25,
) -> RederivationReport:
    """Check whether two distinct blind jobs independently recover a mechanism.

    This is a workflow gate, not mathematical verification. It blocks empty or
    gapped derivations and records exactly which lemma descriptions aligned.
    """
    if left.job_id == right.job_id:
        raise ValueError("blind rederivations must come from distinct jobs")
    if not 0.0 <= minimum_lemma_overlap <= 1.0:
        raise ValueError("minimum_lemma_overlap must be between zero and one")
    gaps = tuple(dict.fromkeys((*left.gaps, *right.gaps)))
    left_lemmas = [_tokens(item) for item in left.lemmas]
    right_lemmas = [_tokens(item) for item in right.lemmas]
    aligned: list[tuple[int, int]] = []
    scores: list[float] = []
    for left_index, left_tokens in enumerate(left_lemmas):
        candidates = [
            (_jaccard(left_tokens, right_tokens), right_index)
            for right_index, right_tokens in enumerate(right_lemmas)
        ]
        if not candidates:
            continue
        score, right_index = max(candidates)
        if score >= minimum_lemma_overlap:
            aligned.append((left_index, right_index))
            scores.append(score)
    mechanism_overlap = _jaccard(_tokens(left.mechanism), _tokens(right.mechanism))
    overlap = max([mechanism_overlap, *scores], default=0.0)
    if not left.lemmas or not right.lemmas:
        gaps = (*gaps, "both blind derivations must provide explicit lemmas")
    if not aligned and mechanism_overlap < minimum_lemma_overlap:
        gaps = (*gaps, "central mechanism was not independently recovered")
    return RederivationReport(
        passed=not gaps,
        overlap_score=overlap,
        aligned_lemma_pairs=tuple(aligned),
        evidence_hashes=(left.artifact_hash, right.artifact_hash),
        gaps=tuple(gaps),
    )
