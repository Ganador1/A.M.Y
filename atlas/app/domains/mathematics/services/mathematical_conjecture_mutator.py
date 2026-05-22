"""Mutation helpers for mathematical conjectures."""
from __future__ import annotations

from typing import Dict, Iterable, List

from app.domains.mathematics.services.mathematical_discovery_engine import Conjecture

__all__ = ["mutate_conjecture", "MathematicalConjectureMutator"]


def _permutation_variants(conj: Conjecture, limit: int) -> List[Conjecture]:
    base = conj.statement
    variants: List[Conjecture] = []
    for original, target in [("a", "b"), ("b", "c"), ("a", "c")]:
        if len(variants) >= limit:
            break
        if all(symbol in base for symbol in (original, target)):
            swapped = (
                base.replace(original, "__TMP__")
                .replace(target, original)
                .replace("__TMP__", target)
            )
            variants.append(
                Conjecture(
                    id=f"{conj.id}_perm_{original}{target}",
                    statement=swapped,
                    domain=conj.domain,
                    goal=conj.goal,
                    metadata={"mutation": "permute"},
                )
            )
    return variants


def _power_variant(conj: Conjecture) -> Conjecture | None:
    if "**2" not in conj.statement:
        return None
    return Conjecture(
        id=f"{conj.id}_pow3",
        statement=conj.statement.replace("**2", "**3"),
        domain=conj.domain,
        goal=conj.goal,
        metadata={"mutation": "power_raise"},
    )


def _cross_term_variant(conj: Conjecture) -> Conjecture | None:
    base = conj.statement
    if "a**2 + b**2" not in base or "a*b" in base:
        return None
    return Conjecture(
        id=f"{conj.id}_cross",
        statement=base.replace("a**2 + b**2", "a**2 + 2*a*b + b**2"),
        domain=conj.domain,
        goal=conj.goal,
        metadata={"mutation": "cross_term"},
    )


def mutate_conjecture(conj: Conjecture, max_variants: int = 3) -> List[Conjecture]:
    variants: List[Conjecture] = []
    if max_variants <= 0:
        return variants

    permutations = _permutation_variants(conj, max_variants)
    variants.extend(permutations)
    if len(variants) >= max_variants:
        return variants

    power_candidate = _power_variant(conj)
    if power_candidate is not None:
        variants.append(power_candidate)
        if len(variants) >= max_variants:
            return variants

    cross_candidate = _cross_term_variant(conj)
    if cross_candidate is not None:
        variants.append(cross_candidate)
    return variants


class MathematicalConjectureMutator:
    """Simple object wrapper so legacy imports receive the expected interface."""

    def __init__(self, default_variants: int = 3) -> None:
        self.default_variants = max(1, default_variants)

    def mutate(self, conj: Conjecture, max_variants: int | None = None) -> List[Conjecture]:
        return mutate_conjecture(conj, max_variants=max_variants or self.default_variants)

    async def mutate_async(self, conj: Conjecture, max_variants: int | None = None) -> List[Conjecture]:
        return self.mutate(conj, max_variants=max_variants)

    def mutate_batch(
        self, conjectures: Iterable[Conjecture], max_variants: int | None = None
    ) -> Dict[str, List[Conjecture]]:
        per_conjecture = max_variants or self.default_variants
        batches: Dict[str, List[Conjecture]] = {}
        for conj in conjectures:
            variants = mutate_conjecture(conj, max_variants=per_conjecture)
            if variants:
                batches[conj.id] = variants
        return batches
