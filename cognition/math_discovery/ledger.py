"""Claim ledger with explicit, independently reviewed promotion gates."""
from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from cognition.math_discovery.models import Claim, ClaimStatus, TERMINAL_STATUSES
from cognition.math_discovery.storage import CampaignStore, canonical_json_bytes, sha256_bytes


_HASH = re.compile(r"^[0-9a-f]{64}$")
_VERIFICATION_METHODS = {"lean", "z3", "exact_computation"}
_VERIFICATION_TOOLS = {
    "lean": "lean_compile",
    "z3": "z3_unsat_check",
    "exact_computation": "exact_python_finite_enumeration",
}


def claim_statement_sha256(claim: Claim) -> str:
    """Bind the declared statement AND its assumptions/quantifiers, not a label."""
    return sha256_bytes(canonical_json_bytes({
        "statement": claim.statement,
        "domain": claim.domain,
        "quantifiers": list(claim.quantifiers),
        "assumptions": list(claim.assumptions),
    }))

_NEXT: dict[ClaimStatus, set[ClaimStatus]] = {
    ClaimStatus.PROPOSED: {ClaimStatus.COMPUTATIONALLY_SUPPORTED},
    ClaimStatus.COMPUTATIONALLY_SUPPORTED: {ClaimStatus.LITERATURE_CHECKED},
    ClaimStatus.LITERATURE_CHECKED: {ClaimStatus.ADVERSARIALLY_SURVIVED},
    ClaimStatus.ADVERSARIALLY_SURVIVED: {ClaimStatus.INDEPENDENTLY_REDERIVED},
    ClaimStatus.INDEPENDENTLY_REDERIVED: {
        ClaimStatus.FORMALLY_VERIFIED,
        ClaimStatus.EXPERT_REVIEW_PENDING,
    },
    ClaimStatus.FORMALLY_VERIFIED: {ClaimStatus.EXPERT_REVIEW_PENDING},
    ClaimStatus.EXPERT_REVIEW_PENDING: {ClaimStatus.RELEASE_CANDIDATE},
}

_FAILURE_STATES = {
    ClaimStatus.REFUTED,
    ClaimStatus.DUPLICATE,
    ClaimStatus.UNSUPPORTED,
    ClaimStatus.STALLED,
    ClaimStatus.WITHDRAWN,
}


class CampaignLedger:
    def __init__(self, store: CampaignStore):
        self.store = store

    def create_claim(self, claim: Claim) -> dict[str, Any]:
        if (
            claim.status is not ClaimStatus.PROPOSED
            or claim.truth_verified
            or claim.verification_method is not None
        ):
            raise ValueError("new claims must start proposed and unverified")
        if claim.claim_id in self.claims():
            raise ValueError(f"claim already exists: {claim.claim_id}")
        return self.store.ledger_log.append(
            "claim_created",
            {"claim": claim.to_dict()},
            actor=claim.created_by_job,
        )

    def transition(
        self,
        claim_id: str,
        to_status: ClaimStatus | str,
        *,
        reviewer_job_id: str,
        evidence_hashes: list[str],
        reason: str,
        verification_method: str | None = None,
        verification_event_hash: str | None = None,
    ) -> dict[str, Any]:
        claims = self.claims()
        if claim_id not in claims:
            raise KeyError(f"unknown claim: {claim_id}")
        current = claims[claim_id]
        target = ClaimStatus(to_status)
        if current.status in TERMINAL_STATUSES:
            raise ValueError(f"terminal claim cannot transition from {current.status.value}")
        allowed = _NEXT.get(current.status, set()) | _FAILURE_STATES
        if target not in allowed:
            raise ValueError(
                f"invalid claim transition: {current.status.value} -> {target.value}"
            )
        if not reason.strip():
            raise ValueError("transition reason cannot be empty")
        normalized_hashes = list(dict.fromkeys(evidence_hashes))
        if not normalized_hashes or any(_HASH.fullmatch(item) is None for item in normalized_hashes):
            raise ValueError("every transition requires at least one lowercase SHA-256 evidence hash")
        is_promotion = target not in _FAILURE_STATES
        if is_promotion and reviewer_job_id == current.created_by_job:
            raise ValueError("a claim creator cannot promote its own claim")
        formal_receipt = None
        if target is ClaimStatus.FORMALLY_VERIFIED:
            if verification_method not in _VERIFICATION_METHODS:
                raise ValueError("formal verification requires lean, z3, or exact_computation")
            formal_receipt = self.require_formal_receipt(
                current,
                reviewer_job_id=reviewer_job_id,
                evidence_hashes=normalized_hashes,
                verification_method=verification_method,
                verification_event_hash=verification_event_hash,
            )
        elif verification_method is not None:
            raise ValueError("verification_method is only valid for formally_verified")
        elif verification_event_hash is not None:
            raise ValueError("verification_event_hash is only valid for formally_verified")
        return self.store.ledger_log.append(
            "claim_transition",
            {
                "claim_id": claim_id,
                "from_status": current.status.value,
                "to_status": target.value,
                "evidence_hashes": normalized_hashes,
                "reason": reason,
                "verification_method": verification_method,
                "verification_event_hash": verification_event_hash,
                "verification_scope": (
                    "declared_formal_input" if target is ClaimStatus.FORMALLY_VERIFIED else None
                ),
                "verification_trust": (
                    "local_runner_observation" if target is ClaimStatus.FORMALLY_VERIFIED else None
                ),
                "authenticated": False,
                "reported_axioms": (
                    formal_receipt["payload"]["metadata"].get("reported_axioms", [])
                    if formal_receipt is not None else []
                ),
                "truth_verified": target is ClaimStatus.FORMALLY_VERIFIED,
            },
            actor=reviewer_job_id,
        )

    def claims(self) -> dict[str, Claim]:
        chain = self.store.ledger_log.verify()
        if not chain["integrity_verified"]:
            raise ValueError(f"invalid claim ledger integrity: {chain['errors']}")
        state: dict[str, Claim] = {}
        for event in self.store.ledger_log.records():
            payload = event["payload"]
            if event["event_type"] == "claim_created":
                raw = payload["claim"]
                if (raw.get("status") != ClaimStatus.PROPOSED.value
                        or raw.get("truth_verified") is not False
                        or raw.get("verification_method") is not None
                        or event.get("actor") != raw.get("created_by_job")):
                    raise ValueError("new claims must replay as proposed and unverified")
                claim = Claim(
                    statement=raw["statement"],
                    domain=raw["domain"],
                    created_by_job=raw["created_by_job"],
                    claim_id=raw["claim_id"],
                    quantifiers=tuple(raw.get("quantifiers", [])),
                    assumptions=tuple(raw.get("assumptions", [])),
                    parent_claim_ids=tuple(raw.get("parent_claim_ids", [])),
                    confidence=raw.get("confidence"),
                )
                if claim.claim_id in state:
                    raise ValueError(f"duplicate claim creation: {claim.claim_id}")
                state[claim.claim_id] = claim
            elif event["event_type"] == "claim_transition":
                claim = state[payload["claim_id"]]
                target = ClaimStatus(payload["to_status"])
                if payload.get("from_status") != claim.status.value:
                    raise ValueError(f"transition source mismatch for {claim.claim_id}")
                if claim.status in TERMINAL_STATUSES:
                    raise ValueError(f"terminal claim cannot transition from {claim.status.value}")
                if not isinstance(payload.get("reason"), str) or not payload["reason"].strip():
                    raise ValueError("transition reason cannot be empty")
                allowed = _NEXT.get(claim.status, set()) | _FAILURE_STATES
                if target not in allowed:
                    raise ValueError(
                        f"invalid replayed transition: {claim.status.value} -> {target.value}"
                    )
                evidence_items = payload.get("evidence_hashes", [])
                if not evidence_items or any(_HASH.fullmatch(item) is None for item in evidence_items):
                    raise ValueError(f"invalid evidence hashes for {claim.claim_id}")
                if target not in _FAILURE_STATES and event.get("actor") == claim.created_by_job:
                    raise ValueError(f"self-promotion replayed for {claim.claim_id}")
                method = payload.get("verification_method")
                if target is ClaimStatus.FORMALLY_VERIFIED:
                    if method not in _VERIFICATION_METHODS or payload.get("truth_verified") is not True:
                        raise ValueError(f"invalid formal verification for {claim.claim_id}")
                    receipt = self.require_formal_receipt(
                        claim,
                        reviewer_job_id=event.get("actor"),
                        evidence_hashes=evidence_items,
                        verification_method=method,
                        verification_event_hash=payload.get("verification_event_hash"),
                    )
                    if (payload.get("verification_scope") != "declared_formal_input"
                            or payload.get("verification_trust") != "local_runner_observation"
                            or payload.get("authenticated") is not False
                            or payload.get("reported_axioms") !=
                            receipt["payload"]["metadata"].get("reported_axioms", [])):
                        raise ValueError("formal transition misstates receipt scope, trust or axioms")
                elif method is not None or payload.get("truth_verified") is not False:
                    raise ValueError(f"unexpected truth assertion for {claim.claim_id}")
                elif payload.get("verification_event_hash") is not None:
                    raise ValueError(f"unexpected formal receipt for {claim.claim_id}")
                supporting = tuple(
                    dict.fromkeys(
                        claim.supporting_artifact_hashes
                        + (tuple(evidence_items) if target is not ClaimStatus.REFUTED else ())
                    )
                )
                contradicting = tuple(
                    dict.fromkeys(
                        claim.contradicting_artifact_hashes
                        + (tuple(evidence_items) if target is ClaimStatus.REFUTED else ())
                    )
                )
                state[claim.claim_id] = replace(
                    claim,
                    status=target,
                    supporting_artifact_hashes=supporting,
                    contradicting_artifact_hashes=contradicting,
                    truth_verified=(
                        target not in _FAILURE_STATES
                        and (claim.truth_verified or bool(payload.get("truth_verified")))
                    ),
                    verification_method=(
                        None if target in _FAILURE_STATES else
                        (payload.get("verification_method") or claim.verification_method)
                    ),
                )
            else:
                raise ValueError(f"unknown ledger event type: {event['event_type']}")
        return state

    def require_formal_receipt(
        self,
        claim: Claim,
        *,
        reviewer_job_id: str,
        evidence_hashes: list[str] | tuple[str, ...],
        verification_method: str,
        verification_event_hash: str | None,
    ) -> dict[str, Any]:
        """Require a retained, claim-bound tool receipt, never just a method string.

        This checks local execution evidence, not authenticated origin or the
        equivalence of natural language with a prover's input. Rehashing the
        entire local history remains outside this unauthenticated guarantee.
        """
        if (not isinstance(verification_event_hash, str)
                or _HASH.fullmatch(verification_event_hash) is None):
            raise ValueError("formal verification requires a retained tool execution receipt")
        if verification_method not in _VERIFICATION_TOOLS:
            raise ValueError("unsupported formal verification method")
        if verification_method == "exact_computation":
            raise ValueError(
                "finite exact_computation receipts provide scoped computational support, "
                "not FORMALLY_VERIFIED claim coverage"
            )
        if not evidence_hashes:
            raise ValueError("formal verification requires retained evidence")
        try:
            for digest in evidence_hashes:
                self.store.artifacts.read_by_hash(digest)
        except (OSError, TypeError, ValueError) as exc:
            raise ValueError(f"formal verification requires retained evidence: {exc}") from exc
        event_chain = self.store.event_log.verify()
        if not event_chain["integrity_verified"]:
            raise ValueError("formal execution receipt has an invalid event chain")
        matches = [event for event in self.store.event_log.records()
                   if event.get("event_hash") == verification_event_hash]
        if len(matches) != 1:
            raise ValueError("formal execution receipt is missing or ambiguous")
        event = matches[0]
        payload = event.get("payload")
        if event.get("event_type") != "tool_call" or not isinstance(payload, dict):
            raise ValueError("formal execution receipt must identify a tool_call")
        if (payload.get("job_id") != reviewer_job_id
                or not isinstance(payload.get("agent_id"), str)
                or not payload["agent_id"]
                or event.get("actor") != payload["agent_id"]):
            raise ValueError("formal execution receipt reviewer/actor mismatch")
        if payload.get("tool_name") != _VERIFICATION_TOOLS[verification_method]:
            raise ValueError("formal execution receipt method/tool mismatch")
        if (type(payload.get("exit_code")) is not int or payload["exit_code"] != 0
                or payload.get("result_status") != "PROVEN"):
            raise ValueError("formal execution receipt is not a successful PROVEN result")
        metadata = payload.get("metadata")
        if (not isinstance(metadata, dict) or metadata.get("result_verified") is not True
                or metadata.get("result_decisive") is not True):
            raise ValueError("formal execution receipt does not report verified tool output")
        binding = metadata.get("verification_binding")
        expected = {
            "claim_id": claim.claim_id,
            "exact_statement_sha256": claim_statement_sha256(claim),
            "verification_method": verification_method,
        }
        if not isinstance(binding, dict) or any(binding.get(k) != v for k, v in expected.items()):
            raise ValueError("formal execution receipt claim/statement/method binding mismatch")
        if verification_method == "lean":
            axioms = metadata.get("reported_axioms")
            if (not isinstance(axioms, (list, tuple))
                    or any(not isinstance(axiom, str) for axiom in axioms)
                    or any(axiom not in {"propext", "Classical.choice", "Quot.sound"}
                           for axiom in axioms)):
                raise ValueError("formal Lean receipt has missing or forbidden axiom evidence")
        artifacts = payload.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError("formal execution receipt requires retained stdin/stdout/stderr")
        names = set()
        retained = {}
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise ValueError("malformed formal execution artifact")
            valid, error = self.store.artifacts.verify(artifact)
            if not valid:
                raise ValueError(f"formal execution artifact invalid: {error}")
            if artifact.get("sha256") not in evidence_hashes:
                raise ValueError("formal execution artifacts are absent from claim evidence")
            names.add(artifact.get("name"))
            retained[artifact.get("name")] = self.store.artifacts.read_by_hash(artifact["sha256"])
        required = {f"{reviewer_job_id}-{part}.bin" for part in ("stdin", "stdout", "stderr")}
        if not required.issubset(names):
            raise ValueError("formal execution receipt requires retained stdin/stdout/stderr")
        stdin = retained[f"{reviewer_job_id}-stdin.bin"]
        stdout = retained[f"{reviewer_job_id}-stdout.bin"]
        stderr = retained[f"{reviewer_job_id}-stderr.bin"]
        command = payload.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ValueError("formal execution receipt requires its actual command")
        if (binding.get("formal_input_sha256") != sha256_bytes(stdin)
                or binding.get("command_sha256") != sha256_bytes(command.encode("utf-8"))
                or binding.get("scope") != "declared_formal_input"):
            raise ValueError("formal execution receipt input/command/scope binding mismatch")
        self._require_checker_contract(claim, verification_method, metadata, stdin, stdout, stderr)
        return event

    @staticmethod
    def _require_checker_contract(
        claim: Claim, method: str, metadata: dict, stdin: bytes, stdout: bytes, stderr: bytes,
    ) -> None:
        """Check retained runner contracts, without executing untrusted package code.

        Kernel/solver execution itself is trusted to the local runner. These
        checks do not authenticate a local writer or replay a proof kernel.
        """
        try:
            source = stdin.decode("utf-8")
            output = (stdout + b"\n" + stderr).decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("formal checker input/output must be valid UTF-8") from exc
        if claim.quantifiers or claim.assumptions:
            raise ValueError("formal input must contain all quantifiers and assumptions explicitly")
        if method == "lean":
            from cognition.math_discovery.tools.lean_runner import LeanRunner
            theorem = metadata.get("theorem_name")
            if not isinstance(theorem, str) or not theorem.isidentifier():
                raise ValueError("Lean receipt requires the checked theorem name")
            suffix = f"\n\n#print axioms {theorem}\n"
            if (not source.endswith(suffix)
                    or metadata.get("audited_source_sha256") != sha256_bytes(stdin)
                    or LeanRunner._validate(source[:-len(suffix)], theorem) is not None):
                raise ValueError("Lean receipt does not contain the checked audited source")
            if claim.statement.strip() != source[:-len(suffix)].strip():
                raise ValueError("claim must be the literal checked Lean source, not a declared translation")
            parsed_axioms = LeanRunner._parse_axioms(output, theorem)
            if (parsed_axioms is None or parsed_axioms != metadata.get("reported_axioms")
                    or "sorryAx" in output):
                raise ValueError("Lean receipt output does not verify its reported axiom scope")
            identity = metadata.get("toolchain_identity")
            if not isinstance(identity, dict):
                raise ValueError("Lean receipt requires toolchain identity")
            if identity.get("execution") == "container":
                image = metadata.get("container_identity")
                if not isinstance(image, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None:
                    raise ValueError("Lean receipt requires the executed container digest")
            else:
                digest = identity.get("sha256")
                if (identity.get("execution") != "explicit_local_opt_in"
                        or not isinstance(digest, str) or _HASH.fullmatch(digest) is None):
                    raise ValueError("Lean receipt requires the executed verifier digest")
        elif method == "z3":
            from cognition.math_discovery.tools.z3_runner import Z3Runner
            framed = re.fullmatch(
                r"\(set-option :timeout [1-9][0-9]*\)\n"
                r"\(set-option :memory_max_size [1-9][0-9]*\)\n"
                r"(.+)\n\(check-sat\)\n", source, flags=re.DOTALL,
            )
            digest = metadata.get("binary_sha256")
            if (framed is None or Z3Runner._validate(framed.group(1)) is not None
                    or stdout.strip() != b"unsat" or stderr.strip()
                    or metadata.get("proof_semantics") != "negated claim must be UNSAT"
                    or not isinstance(digest, str) or _HASH.fullmatch(digest) is None):
                raise ValueError("Z3 receipt must retain its verifier, assertions and clean UNSAT output")
            if claim.statement.strip() != "UNSAT\n" + framed.group(1).strip():
                raise ValueError("claim must identify UNSAT of the literal checked SMT-LIB assertions")

    def verify(self) -> dict[str, Any]:
        chain = self.store.ledger_log.verify()
        if not chain["integrity_verified"]:
            return chain
        try:
            self.claims()
        except (KeyError, TypeError, ValueError) as exc:
            chain["integrity_verified"] = False
            chain["errors"].append(f"invalid ledger semantics: {type(exc).__name__}: {exc}")
        return chain
