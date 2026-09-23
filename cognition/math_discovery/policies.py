"""Role capabilities and information-flow policy."""
from __future__ import annotations

from dataclasses import dataclass

from cognition.math_discovery.models import ResearchRole


@dataclass(frozen=True)
class RolePolicy:
    include_dependency_outputs: bool
    permit_explicit_artifacts: bool
    may_refute_branch: bool = False


ROLE_POLICIES: dict[ResearchRole, RolePolicy] = {
    ResearchRole.EXPLORER: RolePolicy(False, False),
    ResearchRole.CONSTRUCTOR: RolePolicy(False, True),
    ResearchRole.FALSIFIER: RolePolicy(False, True, may_refute_branch=True),
    ResearchRole.SYNTHESIZER: RolePolicy(True, True),
    ResearchRole.HOSTILE_REFEREE: RolePolicy(True, True, may_refute_branch=True),
    ResearchRole.INDEPENDENT_REDERIVER: RolePolicy(False, False),
    ResearchRole.FORMALIZER: RolePolicy(True, True),
    ResearchRole.NOVELTY_AUDITOR: RolePolicy(True, True),
}


def allowed_hashes_for_role(
    role: ResearchRole,
    *,
    explicit_hashes: tuple[str, ...],
    dependency_hashes: tuple[str, ...],
) -> tuple[str, ...]:
    policy = ROLE_POLICIES[role]
    selected: list[str] = []
    if policy.permit_explicit_artifacts:
        selected.extend(explicit_hashes)
    if policy.include_dependency_outputs:
        selected.extend(dependency_hashes)
    return tuple(dict.fromkeys(selected))

