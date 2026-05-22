"""Atlas misuse-prevention guard for research and tool execution.

This module lives inside ``app/security`` so the FastAPI app, Atlas tool
registry, and A.M.Y bridge can share the same abuse policy. It blocks
operational assistance for weaponization, cyber abuse, unsafe human
experimentation, and guardrail tampering while allowing benign scientific work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re
import uuid
from typing import Any, Dict, Iterable, Optional

try:
    from fastapi import HTTPException, status
except Exception:  # pragma: no cover - lets non-FastAPI scripts import policy.
    HTTPException = None  # type: ignore
    status = None  # type: ignore


@dataclass(frozen=True)
class MisuseDecision:
    allowed: bool
    action: str
    risk_level: str
    reasons: list[str]
    matched_rules: list[str] = field(default_factory=list)
    decision_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor_id: str = "anonymous"
    operation: str = ""
    domain: str = ""
    tool_name: str = ""
    review_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MisuseRule:
    rule_id: str
    reason: str
    patterns: tuple[str, ...]
    risk_level: str = "critical"
    action: str = "block"

    def matches(self, text: str) -> bool:
        return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in self.patterns)


MISUSE_RULES: tuple[MisuseRule, ...] = (
    MisuseRule(
        rule_id="CHEMICAL_WEAPONIZATION",
        reason="Operational chemical weapon, toxin, or explosive assistance",
        patterns=(
            r"\bchemical weapon synthesis\b",
            r"\b(how to|instructions?|protocol|recipe|steps?)\b.{0,120}\b(make|synthesi[sz]e|manufacture|produce)\b.{0,120}\b(chemical weapon|nerve agent|sarin|vx|tabun|soman|mustard gas|ricin|explosive)\b",
            r"\b(optimi[sz]e|increase|improve|maximi[sz]e)\b.{0,120}\b(synthesis|production|manufacturing|route)\b.{0,120}\b(sarin|vx|tabun|soman|mustard gas|nerve agent|toxin|ricin|explosive)\b",
            r"\b(synthesi[sz]e|manufacture|produce|purify|weaponi[sz]e)\b.{0,120}\b(sarin|vx|tabun|soman|mustard gas|ricin|nerve agent|toxin)\b",
            r"\b(optimi[sz]e|increase|improve|maximi[sz]e)\b.{0,120}\b(yield|potency|purity|toxicity|lethality)\b.{0,120}\b(sarin|vx|nerve agent|toxin|ricin|explosive)\b",
            r"\b(tatp|anfo)\b.{0,120}\b(synthesi[sz]e|manufacture|detonate|blast|yield|stability)\b",
            r"\b(explosive device|detonator|blast radius)\b.{0,120}\b(design|build|optimi[sz]e|increase)\b",
        ),
    ),
    MisuseRule(
        rule_id="BIO_WEAPONIZATION",
        reason="Operational biological weaponization or pathogen enhancement",
        patterns=(
            r"\bbioweapon\b",
            r"\bweaponi[sz]e\b.{0,120}\b(pathogen|virus|bacteria|anthrax|smallpox)\b",
            r"\bgain[- ]of[- ]function\b.{0,120}\b(pathogen|virus|influenza|coronavirus)\b",
            r"\b(increase|enhance|improve|maximi[sz]e)\b.{0,120}\b(virulence|transmissibility|contagiousness|immune evasion)\b",
            r"\b(aerosoli[sz]e|evade biosafety|bypass biosafety)\b.{0,120}\b(pathogen|virus|bacteria|anthrax)\b",
            r"\b(protocol|steps?|instructions?)\b.{0,120}\b(culture|engineer|modify)\b.{0,120}\b(pathogen|virus|anthrax|smallpox)\b",
        ),
    ),
    MisuseRule(
        rule_id="CYBER_ABUSE",
        reason="Malware, credential theft, unauthorized access, or evasion assistance",
        patterns=(
            r"\b(write|build|create|deploy|modify)\b.{0,120}\b(malware|ransomware|stealer|keylogger|credential harvester|botnet)\b",
            r"\b(steal|exfiltrate|dump|harvest)\b.{0,120}\b(api keys?|passwords?|tokens?|credentials?|cookies?)\b",
            r"\b(bypass|disable|evade)\b.{0,120}\b(auth|authentication|authorization|edr|antivirus|guardrails?|safety checks?)\b",
            r"\b(phishing kit|credential harvester|persistence mechanism|privilege escalation chain)\b",
        ),
    ),
    MisuseRule(
        rule_id="UNAUTHORIZED_HUMAN_EXPERIMENTATION",
        reason="Human-subject experimentation without consent or ethics approval",
        patterns=(
            r"\bunauthori[sz]ed human experimentation\b",
            r"\b(run|start|perform|deploy)\b.{0,120}\b(clinical trial|human trial|human subject experiment)\b.{0,120}\b(without|no)\b.{0,60}\b(consent|approval|irb|ethics)\b",
            r"\b(skip|avoid|bypass)\b.{0,120}\b(consent|irb|ethics committee|patient safety monitoring)\b",
        ),
    ),
    MisuseRule(
        rule_id="GUARDRAIL_TAMPERING",
        reason="Attempt to remove, disable, or bypass Atlas/A.M.Y safety controls",
        patterns=(
            r"\b(delete|remove|disable|bypass|patch out)\b.{0,120}\b(safety|guardrails?|security gate|ethics gate|misuse guard|risk policy)\b",
            r"\b(make|force)\b.{0,120}\b(safety|guardrails?|misuse guard)\b.{0,120}\b(not run|ignore|return allow)\b",
        ),
    ),
    MisuseRule(
        rule_id="FISSILE_MATERIALS",
        reason="Operational fissile material synthesis, enrichment, or weaponization",
        patterns=(
            r"\b(uranium|plutonium|U-235|U-238|Pu-239|HEU)\b.{0,120}\b(enrich|enrichment|synthesi[sz]e|weapon|warhead|critical mass|implosion|gun-type)\b",
            r"\b(centrifuge cascade|gaseous diffusion|laser enrichment|SILEX)\b.{0,120}\b(uranium|fissile|weapon-grade|HEU)\b",
            r"\b(critical mass|implosion lens|neutron initiator|tamper)\b.{0,120}\b(design|geometry|optimi[sz]e|build|fabricate)\b",
            r"\b(dirty bomb|radiological dispersal|RDD)\b.{0,120}\b(build|design|construct|assemble|optimi[sz]e)\b",
            r"\b(plutonium|polonium|americium|cobalt-60|cesium-137)\b.{0,120}\b(weapon|disperse|aerosoli[sz]e)\b",
        ),
    ),
    MisuseRule(
        rule_id="MASS_SURVEILLANCE_AND_TARGETING",
        reason="Operational mass surveillance, individual targeting, or identification of named persons",
        patterns=(
            r"\b(track|surveil|monitor|locate|identify|deanonymi[sz]e|dox)\b.{0,200}\b(individual|named person|specific person|dissident|journalist|activist|protester|minority group)\b",
            r"\b(facial recognition|gait analysis|voice fingerprint|biometric)\b.{0,200}\b(mass|population|covert|without consent|without knowledge)\b",
            r"\b(social credit|social scoring|profile)\b.{0,120}\b(political|religious|ethnic|sexual orientation)\b",
            r"\b(intercept|surveil|hack)\b.{0,200}\b(communications?|messages|calls|emails)\b.{0,120}\b(without warrant|covertly|individuals?|targets?)\b",
            r"\b(generate|create|fabricate)\b.{0,120}\b(deepfake|impersonation|false identity)\b.{0,120}\b(target|victim|specific person|named individual)\b",
        ),
    ),
    MisuseRule(
        rule_id="CRITICAL_INFRASTRUCTURE_ATTACK",
        reason="Operational attack planning on critical infrastructure",
        patterns=(
            r"\b(attack|disable|sabotage|destroy|cripple|disrupt)\b.{0,200}\b(power grid|electrical grid|water supply|water treatment|gas pipeline|nuclear plant|hospital network|emergency services|air traffic control)\b",
            r"\b(SCADA|ICS|PLC|industrial control)\b.{0,200}\b(exploit|attack|disable|payload|malware)\b",
            r"\b(rig|manipulate|attack|hack|fraud|tamper|fake|forge|stuff)\b.{0,200}\b(election|voting|ballot|polling|vote count)\b",
            r"\b(election|voting|ballot|polling)\b.{0,200}\b(rig|manipulate|attack|hack|fraud|tamper|tampering|fake|forge|stuff)\b",
        ),
    ),
)


def _normalize_text(*parts: Any) -> str:
    return "\n".join(str(part or "") for part in parts).lower()


def _flatten_payload(payload: Any, *, max_chars: int = 12000) -> str:
    if isinstance(payload, dict):
        chunks = []
        for key, value in payload.items():
            chunks.append(str(key))
            chunks.append(_flatten_payload(value, max_chars=max_chars))
        text = "\n".join(chunks)
    elif isinstance(payload, (list, tuple, set)):
        text = "\n".join(_flatten_payload(item, max_chars=max_chars) for item in payload)
    else:
        text = str(payload or "")
    return text[:max_chars]


class MisuseGuard:
    """Policy engine for actor misuse attempts."""

    def __init__(self):
        self.rules = MISUSE_RULES
        self._actor_attempts: dict[str, list[datetime]] = {}
        self._blocked_until: dict[str, datetime] = {}
        self.block_after_attempts = 3
        self.window = timedelta(minutes=10)
        self.block_duration = timedelta(minutes=15)

    def evaluate(
        self,
        *,
        operation: str,
        content: Any,
        domain: str = "",
        tool_name: str = "",
        actor_id: str = "anonymous",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MisuseDecision:
        now = datetime.now(timezone.utc)
        actor = str(actor_id or "anonymous")

        blocked_until = self._blocked_until.get(actor)
        if blocked_until and blocked_until > now:
            decision = MisuseDecision(
                allowed=False,
                action="block",
                risk_level="critical",
                reasons=["Actor temporarily blocked after repeated misuse attempts"],
                matched_rules=["ACTOR_TEMPORARILY_BLOCKED"],
                actor_id=actor,
                operation=operation,
                domain=domain,
                tool_name=tool_name,
            )
            self._audit(decision, content, metadata)
            return decision

        text = _normalize_text(operation, domain, tool_name, _flatten_payload(content))
        matched_rules: list[str] = []
        reasons: list[str] = []
        risk = "low"

        for rule in self.rules:
            if rule.matches(text):
                matched_rules.append(rule.rule_id)
                reasons.append(rule.reason)
                risk = rule.risk_level

        if matched_rules:
            decision = MisuseDecision(
                allowed=False,
                action="block",
                risk_level=risk,
                reasons=reasons,
                matched_rules=matched_rules,
                actor_id=actor,
                operation=operation,
                domain=domain,
                tool_name=tool_name,
            )
            self._record_actor_attempt(actor, now)
        else:
            decision = MisuseDecision(
                allowed=True,
                action="allow",
                risk_level="low",
                reasons=[],
                matched_rules=[],
                actor_id=actor,
                operation=operation,
                domain=domain,
                tool_name=tool_name,
            )

        self._audit(decision, content, metadata)
        return decision

    def evaluate_payload(
        self,
        payload: Dict[str, Any],
        *,
        operation: str = "api.request",
        actor_id: str = "anonymous",
    ) -> MisuseDecision:
        return self.evaluate(
            operation=operation,
            content=payload,
            domain=str(payload.get("domain", "")),
            tool_name=str(payload.get("tool_name", payload.get("tool", ""))),
            actor_id=actor_id,
            metadata={"payload_keys": sorted(str(key) for key in payload.keys())},
        )

    def enforce_safe_operation(
        self,
        *,
        operation: str,
        content: Any,
        domain: str = "",
        tool_name: str = "",
        actor_id: str = "anonymous",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MisuseDecision:
        decision = self.evaluate(
            operation=operation,
            content=content,
            domain=domain,
            tool_name=tool_name,
            actor_id=actor_id,
            metadata=metadata,
        )
        if decision.allowed:
            return decision

        if HTTPException is None:
            raise RuntimeError(format_blocked_message(decision))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Blocked by Atlas misuse policy",
                "decision": decision.to_dict(),
            },
        )

    def _record_actor_attempt(self, actor_id: str, now: datetime) -> None:
        attempts = [
            timestamp
            for timestamp in self._actor_attempts.get(actor_id, [])
            if timestamp > now - self.window
        ]
        attempts.append(now)
        self._actor_attempts[actor_id] = attempts
        if len(attempts) >= self.block_after_attempts:
            self._blocked_until[actor_id] = now + self.block_duration

    def _audit(self, decision: MisuseDecision, content: Any, metadata: Optional[Dict[str, Any]]) -> None:
        try:
            from app.security.audit_logger import audit_logger

            text = _flatten_payload(content)
            audit_logger.log_security_event(
                event_type="misuse_guard_decision",
                severity="warning" if decision.allowed else "critical",
                description="Atlas misuse policy evaluated operation",
                details={
                    "decision_id": decision.decision_id,
                    "allowed": decision.allowed,
                    "action": decision.action,
                    "risk_level": decision.risk_level,
                    "matched_rules": decision.matched_rules,
                    "operation": decision.operation,
                    "domain": decision.domain,
                    "tool_name": decision.tool_name,
                    "actor_hash": sha256(decision.actor_id.encode("utf-8")).hexdigest(),
                    "content_sha256": sha256(text.encode("utf-8")).hexdigest(),
                    "content_length": len(text),
                    "metadata": metadata or {},
                },
            )
        except Exception:
            return


def format_blocked_message(decision: MisuseDecision | Dict[str, Any]) -> str:
    data = decision.to_dict() if isinstance(decision, MisuseDecision) else decision
    reasons = "; ".join(data.get("reasons") or ["Misuse policy violation"])
    rules = ",".join(data.get("matched_rules") or [])
    return (
        "Blocked by Atlas misuse policy: "
        f"{reasons} (rules={rules}; decision_id={data.get('decision_id')})"
    )


def evaluate_misuse(
    *,
    operation: str,
    content: Any,
    domain: str = "",
    tool_name: str = "",
    actor_id: str = "anonymous",
    metadata: Optional[Dict[str, Any]] = None,
) -> MisuseDecision:
    return misuse_guard.evaluate(
        operation=operation,
        content=content,
        domain=domain,
        tool_name=tool_name,
        actor_id=actor_id,
        metadata=metadata,
    )


def require_safe_operation(
    *,
    operation: str,
    content: Any,
    domain: str = "",
    tool_name: str = "",
    actor_id: str = "anonymous",
    metadata: Optional[Dict[str, Any]] = None,
) -> MisuseDecision:
    return misuse_guard.enforce_safe_operation(
        operation=operation,
        content=content,
        domain=domain,
        tool_name=tool_name,
        actor_id=actor_id,
        metadata=metadata,
    )


misuse_guard = MisuseGuard()


__all__ = [
    "MISUSE_RULES",
    "MisuseDecision",
    "MisuseGuard",
    "MisuseRule",
    "evaluate_misuse",
    "format_blocked_message",
    "misuse_guard",
    "require_safe_operation",
]
