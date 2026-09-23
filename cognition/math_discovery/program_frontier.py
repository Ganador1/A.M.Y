"""Safe executable-program frontier for finite mathematical constructions."""

from __future__ import annotations

import ast
import json
import math
import random
import re
import time
from dataclasses import dataclass
from typing import Any

from cognition.math_discovery.storage import (
    CampaignStore,
    canonical_json_bytes,
    sha256_bytes,
)
from cognition.math_discovery.provenance import CampaignProvenance
from core.model_broker import ModelBroker
from sandbox.executor import SandboxExecutor


_FENCED_PYTHON_RE = re.compile(
    r"```(?:python|py)\s*(.*?)```", re.DOTALL | re.IGNORECASE
)
_FORBIDDEN_CALLS = {
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "globals",
    "help",
    "input",
    "locals",
    "open",
    "vars",
    "__import__",
}


def extract_construct_program(text: str | None) -> str:
    """Extract one Python construction program from a worker text field."""

    source = text or ""
    fenced = _FENCED_PYTHON_RE.findall(source)
    candidates = fenced or ([source[source.find("def construct"):]] if "def construct" in source else [])
    for candidate in candidates:
        candidate = candidate.strip()
        try:
            validate_construct_program(candidate)
        except ValueError:
            continue
        return candidate + "\n"
    raise ValueError("no valid def construct() program found")


def validate_construct_program(source: str) -> None:
    """Restrict generated programs before Docker provides the hard boundary."""

    if len(source.encode("utf-8")) > 64_000:
        raise ValueError("program exceeds 64 KiB")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError(f"invalid Python syntax: {exc}") from exc
    if not tree.body or any(not isinstance(node, ast.FunctionDef) for node in tree.body):
        raise ValueError("top level may contain function definitions only")
    constructs = [node for node in tree.body if node.name == "construct"]
    if len(constructs) != 1 or constructs[0].args.args:
        raise ValueError("program must define exactly one zero-argument construct()")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.AsyncFunctionDef, ast.ClassDef)):
            raise ValueError("imports, async functions and classes are forbidden")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("dunder names are forbidden")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError("dunder attribute access is forbidden")
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _FORBIDDEN_CALLS
        ):
            raise ValueError(f"forbidden call: {node.func.id}")


_HARNESS = r'''
import json

def _audit(values):
    if not isinstance(values, (list, tuple, set)):
        return {"valid": False, "reason": "construct() must return a sequence"}
    if len(values) > 500:
        return {"valid": False, "reason": "trial limit is 500 elements"}
    if any(isinstance(x, bool) or not isinstance(x, int) for x in values):
        return {"valid": False, "reason": "all elements must be integers"}
    basis = sorted(set(values))
    if not basis or basis[0] < 0:
        return {"valid": False, "reason": "basis must be nonempty and nonnegative"}
    differences = {
        basis[j] - basis[i]
        for i in range(len(basis))
        for j in range(i + 1, len(basis))
    }
    first_missing = next(
        v for v in range(1, (max(differences) if differences else 0) + 2)
        if v not in differences
    )
    k = first_missing - 1
    if k < 1:
        return {"valid": False, "reason": "difference 1 is missing"}
    target = 49110
    missing = [value for value in range(1, target + 1) if value not in differences]
    return {
        "valid": True,
        "basis": basis,
        "size": len(basis),
        "covered_through": k,
        "ratio": len(basis) ** 2 / k,
        "missing_count_through_target": len(missing),
        "missing_sample": missing[:64],
        "target_covered": not missing,
    }

try:
    print(json.dumps(_audit(construct()), separators=(",", ":"), sort_keys=True))
except Exception as exc:
    print(json.dumps({"valid": False, "reason": type(exc).__name__ + ": " + str(exc)}))
'''


@dataclass(frozen=True)
class ProgramEvaluation:
    valid: bool
    ratio: float
    size: int | None
    covered_through: int | None
    basis: tuple[int, ...]
    reason: str | None
    execution: dict[str, Any]
    diagnostics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "ratio": self.ratio if math.isfinite(self.ratio) else None,
            "size": self.size,
            "covered_through": self.covered_through,
            "basis": list(self.basis),
            "reason": self.reason,
            "execution": self.execution,
            "diagnostics": self.diagnostics,
        }


def exact_difference_basis_metrics(
    values: list[int] | tuple[int, ...],
    *,
    max_size: int = 500,
) -> dict[str, Any]:
    """Return exact coverage plus diagnostics used by trusted local evolution."""

    basis = sorted(set(values))
    if not basis or basis[0] < 0 or len(basis) > max_size:
        return {"valid": False, "ratio": math.inf, "basis": basis}
    counts: dict[int, int] = {}
    for index, left in enumerate(basis):
        for right in basis[index + 1 :]:
            difference = right - left
            counts[difference] = counts.get(difference, 0) + 1
    first_missing = next(
        value for value in range(1, (max(counts) if counts else 0) + 2)
        if value not in counts
    )
    covered = first_missing - 1
    if covered < 1:
        return {"valid": False, "ratio": math.inf, "basis": basis}
    unique_marks = {
        mark: sum(
            counts.get(abs(mark - other), 0) == 1
            and abs(mark - other) <= covered
            for other in basis
            if other != mark
        )
        for mark in basis
    }
    return {
        "valid": True,
        "basis": basis,
        "size": len(basis),
        "covered_through": covered,
        "first_missing": first_missing,
        "ratio": len(basis) ** 2 / covered,
        "unique_coverage_by_mark": unique_marks,
    }


def singer_residue_set(
    q: int,
    *,
    linear_coefficient: int,
    constant_coefficient: int,
) -> list[int]:
    """Construct a Singer residue set from ``F_q[x]/(x^3+a*x+b)``.

    The returned exponents select powers of ``x`` whose quadratic coefficient
    vanishes.  Callers remain responsible for choosing a prime ``q`` and an
    irreducible polynomial for which ``x`` has the required projective order.
    The cardinality and cyclic-difference checks are deliberately left to the
    exact verifier rather than assumed from the construction.
    """

    if q < 2:
        raise ValueError("q must be at least two")
    modulus = q * q + q + 1
    c0, c1, c2 = 1, 0, 0
    residues: list[int] = []
    for exponent in range(modulus):
        if c2 % q == 0:
            residues.append(exponent)
        # x*(c0+c1*x+c2*x^2), with x^3 = -a*x-b.
        c0, c1, c2 = (
            (-constant_coefficient * c2) % q,
            (c0 - linear_coefficient * c2) % q,
            c1 % q,
        )
    return residues


def affine_residues(
    residues: list[int] | tuple[int, ...],
    *,
    modulus: int,
    multiplier: int,
    shift: int,
) -> list[int]:
    """Return a normalized affine representative of cyclic residues."""

    if modulus < 1:
        raise ValueError("modulus must be positive")
    return sorted({(multiplier * value + shift) % modulus for value in residues})


def layered_difference_basis(
    residues: list[int] | tuple[int, ...],
    *,
    modulus: int,
    heights: list[int] | tuple[int, ...],
) -> list[int]:
    """Lift one residue block through explicit integer-height shells."""

    if modulus < 1 or not residues or not heights:
        raise ValueError("modulus, residues, and heights must be nonempty")
    return sorted(
        {
            int(residue) + modulus * int(height)
            for height in heights
            for residue in residues
        }
    )


@dataclass(frozen=True)
class PopulationMember:
    basis: tuple[int, ...]
    ratio: float
    covered_through: int
    origin: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "basis": list(self.basis),
            "ratio": self.ratio,
            "covered_through": self.covered_through,
            "size": len(self.basis),
            "origin": self.origin,
        }


class DifferenceBasisLocalEvolution:
    """Deterministic, exact local population search without generated-code risk."""

    def __init__(self, *, population_size: int = 12, seed: int = 20260812):
        if population_size < 3:
            raise ValueError("population_size must be at least three")
        self.population_size = population_size
        self.random = random.Random(seed)

    @staticmethod
    def member(values: list[int] | tuple[int, ...], origin: str) -> PopulationMember | None:
        metrics = exact_difference_basis_metrics(values)
        if not metrics["valid"]:
            return None
        return PopulationMember(
            basis=tuple(metrics["basis"]),
            ratio=float(metrics["ratio"]),
            covered_through=int(metrics["covered_through"]),
            origin=origin,
        )

    @staticmethod
    def _rank(member: PopulationMember) -> tuple[float, int, int, tuple[int, ...]]:
        return (
            member.ratio,
            -member.covered_through,
            len(member.basis),
            member.basis,
        )

    def select(self, members: list[PopulationMember]) -> list[PopulationMember]:
        unique = {member.basis: member for member in members}
        ordered = sorted(unique.values(), key=self._rank)
        selected: list[PopulationMember] = []
        sizes: set[int] = set()
        for member in ordered:
            if len(selected) >= self.population_size:
                break
            if len(member.basis) not in sizes or len(selected) >= self.population_size // 2:
                selected.append(member)
                sizes.add(len(member.basis))
        for member in ordered:
            if len(selected) >= self.population_size:
                break
            if member not in selected:
                selected.append(member)
        return selected

    def mutations(self, parent: PopulationMember, count: int) -> list[PopulationMember]:
        basis = list(parent.basis)
        metrics = exact_difference_basis_metrics(basis)
        gap = int(metrics["first_missing"])
        maximum = max(basis)
        proposals: list[tuple[list[int], str]] = []
        if len(basis) >= 64:
            additions = sorted(
                {
                    value
                    for anchor in basis
                    for value in (anchor + gap, anchor - gap)
                    if 0 <= value <= max(maximum + gap, gap * 2)
                    and value not in basis
                },
                key=lambda value: (abs(value - maximum), value),
            )[: max(8, count * 2)]
            removable = sorted(
                basis,
                key=lambda mark: (
                    metrics["unique_coverage_by_mark"].get(mark, 0),
                    abs(mark - maximum // 2),
                    mark,
                ),
            )[: max(4, count)]
            for addition in additions:
                for removed in removable:
                    if removed == 0:
                        continue
                    proposals.append(
                        (
                            [value for value in basis if value != removed]
                            + [addition],
                            "exchange_first_gap",
                        )
                    )
                    if len(proposals) >= max(24, count * 8):
                        break
                if len(proposals) >= max(24, count * 8):
                    break
            radius = max(2, gap // 8)
            for _ in range(max(8, count * 2)):
                candidate = list(basis)
                index = self.random.randrange(1, len(candidate))
                candidate[index] = max(
                    0, candidate[index] + self.random.randint(-radius, radius)
                )
                proposals.append((candidate, "bounded_random_exchange"))
            members = [
                member
                for values, origin in proposals
                if (member := self.member(values, origin)) is not None
            ]
            return sorted(members, key=self._rank)[:count]
        # Target the first missing difference explicitly in both orientations.
        for anchor in basis:
            for value in (anchor + gap, anchor - gap):
                if 0 <= value <= max(maximum + gap * 2, gap * 4):
                    proposals.append((basis + [value], "add_first_gap"))
        removable = sorted(
            basis,
            key=lambda mark: (metrics["unique_coverage_by_mark"].get(mark, 0), mark),
        )
        for mark in removable[: max(2, len(basis) // 4)]:
            if mark != 0:
                proposals.append(([value for value in basis if value != mark], "remove_redundant"))
        radius = max(2, gap // 3)
        for _ in range(count * 3):
            candidate = list(basis)
            operation = self.random.choice(("move", "add", "remove", "reflect"))
            if operation == "move" and len(candidate) > 2:
                index = self.random.randrange(1, len(candidate))
                candidate[index] = max(0, candidate[index] + self.random.randint(-radius, radius))
            elif operation == "add":
                candidate.append(self.random.randint(0, maximum + gap * 2))
            elif operation == "remove" and len(candidate) > 3:
                candidate.pop(self.random.randrange(1, len(candidate)))
            else:
                pivot = maximum
                candidate = sorted(set(candidate) | {pivot - value for value in candidate})
            proposals.append((candidate, f"random_{operation}"))
        members = [
            member
            for values, origin in proposals
            if (member := self.member(values, origin)) is not None
        ]
        return sorted(members, key=self._rank)[:count]

    def crossover(
        self, left: PopulationMember, right: PopulationMember
    ) -> list[PopulationMember]:
        scale_left = max(left.basis) or 1
        scale_right = max(right.basis) or 1
        normalized_right = {
            round(value * scale_left / scale_right) for value in right.basis
        }
        proposals = (
            sorted(set(left.basis) | normalized_right),
            sorted(set(left.basis) & normalized_right),
            sorted(set(left.basis[::2]) | set(normalized_right)),
        )
        return [
            member
            for index, values in enumerate(proposals)
            if (member := self.member(values, f"crossover_{index}")) is not None
        ]

    def evolve(
        self,
        population: list[PopulationMember],
        *,
        rounds: int,
        mutations_per_parent: int,
    ) -> list[PopulationMember]:
        current = self.select(population)
        for _ in range(rounds):
            offspring = list(current)
            for parent in current:
                offspring.extend(self.mutations(parent, mutations_per_parent))
            for index in range(0, len(current) - 1, 2):
                offspring.extend(self.crossover(current[index], current[index + 1]))
            current = self.select(offspring)
        return current


class DifferenceBasisProgramRunner:
    """Execute generated constructors in fail-closed Docker and retain provenance."""

    def __init__(
        self,
        store: CampaignStore,
        *,
        executor: SandboxExecutor | None = None,
    ):
        self.store = store
        self.executor = executor or SandboxExecutor(
            {
                "use_docker": True,
                "require_isolation": True,
                "allow_network": False,
                "allow_subprocess": False,
                "max_execution_time": 20,
                "max_memory_mb": 512,
            }
        )

    async def evaluate(
        self,
        source: str,
        *,
        candidate_id: str,
        lane: str,
        generation: int,
    ) -> tuple[ProgramEvaluation, dict[str, Any]]:
        validate_construct_program(source)
        execution = await self.executor.execute(source + "\n" + _HARNESS, "python")
        payload: dict[str, Any]
        try:
            payload = json.loads(execution.get("stdout") or "")
        except (json.JSONDecodeError, TypeError):
            payload = {"valid": False, "reason": "executor returned invalid JSON"}
        valid = bool(execution.get("success")) and payload.get("valid") is True
        evaluation = ProgramEvaluation(
            valid=valid,
            ratio=float(payload["ratio"]) if valid else math.inf,
            size=int(payload["size"]) if valid else None,
            covered_through=int(payload["covered_through"]) if valid else None,
            basis=tuple(int(value) for value in payload.get("basis", ())) if valid else (),
            reason=None if valid else str(payload.get("reason") or execution.get("stderr")),
            execution={
                "success": bool(execution.get("success")),
                "return_code": execution.get("return_code"),
                "stderr": str(execution.get("stderr") or "")[:2000],
            },
            diagnostics={
                "basis_sha256": (
                    sha256_bytes(canonical_json_bytes(payload.get("basis", ())))
                    if valid
                    else None
                ),
                "missing_count_through_target": (
                    int(payload["missing_count_through_target"])
                    if valid and payload.get("missing_count_through_target") is not None
                    else None
                ),
                "missing_sample": (
                    [int(value) for value in payload.get("missing_sample", ())]
                    if valid
                    else []
                ),
                "target_covered": bool(payload.get("target_covered")) if valid else False,
                "strict_improvement": bool(
                    valid
                    and float(payload["ratio"]) < 129600.0 / 49109.0
                ),
            },
        )
        program_artifact = self.store.artifacts.write(
            f"{candidate_id}-construct.py", source.encode(), "text/x-python"
        )
        evaluation_artifact = self.store.artifacts.write(
            f"{candidate_id}-evaluation.json",
            canonical_json_bytes(evaluation.to_dict()) + b"\n",
            "application/json",
        )
        feedback = {
            "program": source,
            "evaluation": evaluation.to_dict(),
            "program_sha256": program_artifact["sha256"],
            "evaluation_sha256": evaluation_artifact["sha256"],
        }
        feedback_artifact = self.store.artifacts.write(
            f"{candidate_id}-feedback.json",
            json.dumps(feedback, indent=2, sort_keys=True).encode() + b"\n",
            "application/json",
        )
        basis_fingerprint = evaluation.diagnostics.get("basis_sha256")
        duplicate_of = next(
            (
                event.get("payload", {}).get("candidate_id")
                for event in self.store.event_log.records()
                if event.get("event_type") == "executable_candidate_evaluated"
                and basis_fingerprint is not None
                and event.get("payload", {})
                .get("evaluation", {})
                .get("diagnostics", {})
                .get("basis_sha256")
                == basis_fingerprint
            ),
            None,
        )
        self.store.event_log.append(
            "executable_candidate_evaluated",
            {
                "candidate_id": candidate_id,
                "lane": lane,
                "generation": generation,
                "evaluation": evaluation.to_dict(),
                "semantic_duplicate_of": duplicate_of,
                "artifacts": [
                    program_artifact,
                    evaluation_artifact,
                    feedback_artifact,
                ],
                "truth_scope": "finite construction checked by exact integer arithmetic",
            },
            actor="program_frontier",
        )
        return evaluation, feedback_artifact


class ConstructProgramCompiler:
    """Losslessly compile a retained mathematical draft into the program contract."""

    def __init__(
        self,
        store: CampaignStore,
        broker: ModelBroker,
        *,
        model: str,
        model_digest: str,
        num_ctx: int,
        max_tokens: int = 8192,
    ):
        self.store = store
        self.broker = broker
        self.model = model
        self.model_digest = model_digest
        self.num_ctx = num_ctx
        self.max_tokens = max_tokens
        self.provenance = CampaignProvenance(store)

    async def compile(
        self,
        *,
        candidate_id: str,
        lane: str,
        generation: int,
        draft: dict[str, Any],
        parent_feedback: dict[str, Any],
        parse_error: str,
    ) -> str:
        system_prompt = (
            "You are a restrictive code transcriber, not a mathematical inventor. "
            "Translate the retained proposal into one executable Python program. "
            "If the proposal is incomplete, preserve the parent program and make "
            "only changes explicitly supported by the proposal. Output only one "
            "```python fenced block. The code must define zero-argument construct(), "
            "use no imports or I/O, and return at most 500 nonnegative integers."
        )
        user_prompt = (
            f"LANE: {lane}\nGENERATION: {generation}\n"
            f"PARSER ERROR: {parse_error}\n\n"
            "PARENT EXECUTABLE AND EXACT RESULT:\n"
            + json.dumps(parent_feedback, ensure_ascii=False, sort_keys=True)
            + "\n\nRETAINED PROPOSAL JSON:\n"
            + json.dumps(draft, ensure_ascii=False, sort_keys=True)
        )
        parameters = {
            "temperature": 0.0,
            "max_tokens": self.max_tokens,
            "num_ctx": self.num_ctx,
            "think": False,
            "stage": "construct_program_compiler",
            "policy": "transcribe_or_preserve_parent",
        }
        started = time.monotonic()
        response = await self.broker.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=self.max_tokens,
            num_ctx=self.num_ctx,
            think=False,
            priority=5,
        )
        latency = time.monotonic() - started
        message = response.get("message", {}) or {}
        content = str(message.get("content") or "")
        thinking = str(message.get("thinking") or "")
        raw = content if content.strip() else thinking
        try:
            source = extract_construct_program(raw)
            normalized = source
            error = None
        except ValueError as exc:
            source = ""
            normalized = None
            error = str(exc)
        event = self.provenance.record_llm_call(
            job_id=f"job_compile_{candidate_id}",
            agent_id=f"agent_compile_{lane}",
            role="compiler",
            phase=f"program_compilation_{generation:02d}",
            model=self.model,
            model_digest=self.model_digest,
            parameters=parameters,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_response=json.dumps(response, ensure_ascii=False, sort_keys=True),
            normalized_response=normalized,
            usage={
                key: response.get(key)
                for key in ("prompt_eval_count", "eval_count", "done_reason")
                if response.get(key) is not None
            },
            latency_seconds=latency,
            attempt=1,
        )
        self.store.event_log.append(
            "construct_program_compiled",
            {
                "candidate_id": candidate_id,
                "lane": lane,
                "generation": generation,
                "success": normalized is not None,
                "error": error,
                "source_event_hash": event["event_hash"],
                "semantic_policy": "transcribe retained proposal or preserve parent",
            },
            actor="program_compiler",
        )
        if not source:
            raise ValueError(f"compiler produced no valid program: {error}")
        return source
