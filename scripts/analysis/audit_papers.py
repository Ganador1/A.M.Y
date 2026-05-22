"""
Paper Audit Tool — Verify reproducibility and factual integrity of A.M.Y papers.

Checks:
1. Every experiment_id cited has a matching provenance file
2. Every numerical claim has an experiment_id nearby or is flagged
3. Citations in References section are verified against external databases
4. The code in provenance reproduces the claimed results
"""
import json
import re
import sys
import hashlib
from pathlib import Path

import structlog

from communication.citation_verifier import CitationVerifier
from communication.numeric_verifier import NumericVerifier
from core.atlas_tools import assess_tool_output
from sandbox.executor import SandboxExecutor

log = structlog.get_logger()

PAPERS_DIR = Path("papers")
EXPERIMENTS_DIR = Path("data/experiments")


ZERO_FAILURE_CLAIM_RE = re.compile(
    r"\b(?:zero|0|no)\s+(?:tool\s+)?failures?\b|"
    r"\bno\s+failures\b|"
    r"\bAll results are real experimental outputs with zero tool failures\b",
    re.IGNORECASE,
)


def extract_provenance_paths(text: str) -> dict[str, Path]:
    """Find modern provenance paths cited in a paper.

    Modern A.M.Y papers cite records as:
    - experiment_id: `data/experiments/experiment_id/provenance.json`
    """
    paths = {}
    pattern = re.compile(r"`([^`]*data/experiments/([^`/]+)/provenance\.json)`")
    for match in pattern.finditer(text):
        raw_path = match.group(1)
        experiment_id = match.group(2)
        paths[experiment_id] = Path(raw_path)
    return paths


def extract_provenance_cited_hashes(text: str) -> dict[str, str | None]:
    """Find output SHA-256 values cited next to provenance paths."""
    hashes: dict[str, str | None] = {}
    pattern = re.compile(
        r"`([^`]*data/experiments/([^`/]+)/provenance\.json)`"
        r"(?:\s*\((?:output\s+)?SHA-256:\s*`?([a-fA-F0-9]+)`?\))?",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        experiment_id = match.group(2)
        cited_hash = match.group(3)
        hashes[experiment_id] = cited_hash.lower() if cited_hash else None
    return hashes


def extract_experiment_ids(text: str) -> list[str]:
    """Find experiment IDs mentioned in the paper."""
    modern_ids = list(extract_provenance_paths(text).keys())

    # Match experiment IDs in backticks, plain text, or Data Availability section
    pattern = re.compile(r"(?<![a-f0-9])`?([a-f0-9]{32})`?(?![a-f0-9])", re.IGNORECASE)
    found = pattern.findall(text)
    # Filter to those that appear near "experiment" or "provenance" or "Data Availability"
    valid = list(modern_ids)
    for f in found:
        # search context around the match
        for m in re.finditer(rf"`?{re.escape(f)}`?", text, re.IGNORECASE):
            start = max(0, m.start() - 100)
            end = min(len(text), m.end() + 100)
            context = text[start:end].lower()
            if any(k in context for k in ["experiment", "provenance", "data availability", "reproducibility"]):
                valid.append(f)
                break
    return list(dict.fromkeys(valid))


def extract_references(text: str) -> list[str]:
    """Extract numbered references from the References section."""
    refs = []
    in_refs = False
    for line in text.split("\n"):
        if line.strip().startswith("## References") or line.strip().startswith("## references"):
            in_refs = True
            continue
        if in_refs:
            if line.strip().startswith("##"):
                break
            stripped = line.strip()
            if re.match(r"^\d+\.\s+", stripped):
                refs.append(re.sub(r"^\d+\.\s+", "", stripped))
            elif re.match(r"^\[\d+\]\s+", stripped):
                refs.append(re.sub(r"^\[\d+\]\s+", "", stripped))
    return refs


def detect_operational_output_issues(text: str) -> dict:
    """Detect manuscript text that treats tool failures as scientific output."""
    code_blocks = re.findall(r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)```", text, flags=re.DOTALL)
    unusable_blocks = []
    for block in code_blocks:
        assessment = assess_tool_output(block)
        if not assessment.get("usable", False):
            unusable_blocks.append(
                {
                    "markers": assessment.get("markers", []),
                    "preview": block.strip()[:300],
                }
            )

    full_text_assessment = assess_tool_output(text)
    full_text_markers = full_text_assessment.get("markers", [])
    if full_text_markers and not any(
        set(full_text_markers).issubset(set(block.get("markers", [])))
        for block in unusable_blocks
    ):
        unusable_blocks.append(
            {
                "markers": full_text_markers,
                "preview": full_text_assessment.get("preview", text[:300]),
            }
        )

    zero_failure_claim = bool(ZERO_FAILURE_CLAIM_RE.search(text))
    contradictions = []
    if zero_failure_claim and unusable_blocks:
        contradictions.append("claims_zero_failures_but_contains_unusable_tool_output")

    return {
        "zero_failure_claim": zero_failure_claim,
        "unusable_output_blocks": unusable_blocks,
        "contradictions": contradictions,
        "ok": not unusable_blocks and not contradictions,
    }


def verify_provenance(experiment_ids: list[str], provenance_paths: dict[str, Path] | None = None) -> dict:
    """Check that every experiment_id has a provenance file."""
    results = {}
    provenance_paths = provenance_paths or {}
    for eid in experiment_ids:
        prov_path = provenance_paths.get(eid) or EXPERIMENTS_DIR / eid / "provenance.json"
        if not prov_path.exists():
            prov_path = EXPERIMENTS_DIR / f"{eid}.json"
        results[eid] = prov_path.exists()
    return results


def _verify_modern_provenance(prov_path: Path) -> dict:
    """Verify a modern provenance directory with output hash."""
    if not prov_path.exists():
        return {"exists": False}

    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"exists": True, "valid_json": False, "error": str(e), "reproducible": False}

    output_path = prov_path.parent / "output.txt"
    tool = prov.get("tool", {})
    expected_hash = tool.get("output_hash")
    success = bool(tool.get("success", False))

    hash_ok = None
    if expected_hash and output_path.exists():
        actual_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
        hash_ok = actual_hash == expected_hash

    return {
        "exists": True,
        "valid_json": True,
        "has_code": False,
        "success": success,
        "output_path": str(output_path) if output_path.exists() else None,
        "output_hash_ok": hash_ok,
        "reproducible": success and hash_ok is True,
        "tool": tool.get("name"),
        "input": tool.get("input"),
    }


def verify_cited_hashes(
    experiment_ids: list[str],
    provenance_paths: dict[str, Path],
    cited_hashes: dict[str, str | None],
) -> dict[str, dict]:
    """Verify that hashes printed in the paper match provenance output hashes."""
    results = {}
    for eid in experiment_ids:
        cited_hash = cited_hashes.get(eid)
        prov_path = provenance_paths.get(eid) or EXPERIMENTS_DIR / eid / "provenance.json"
        expected_hash = None
        try:
            prov = json.loads(prov_path.read_text(encoding="utf-8"))
            expected_hash = prov.get("tool", {}).get("output_hash")
        except (OSError, json.JSONDecodeError):
            pass

        if not cited_hash:
            status = "missing"
            ok = False
        elif not expected_hash:
            status = "no_provenance_hash"
            ok = False
        elif not re.fullmatch(r"[a-f0-9]{64}", cited_hash):
            status = "not_full_sha256"
            ok = False
        elif cited_hash != expected_hash.lower():
            status = "mismatch"
            ok = False
        else:
            status = "match"
            ok = True

        results[eid] = {
            "ok": ok,
            "status": status,
            "cited_hash": cited_hash,
            "expected_hash": expected_hash,
        }
    return results


def verify_reproducibility(experiment_id: str, provenance_paths: dict[str, Path] | None = None) -> dict:
    """Re-run the experiment code and compare key outputs."""
    import asyncio

    provenance_paths = provenance_paths or {}
    modern_path = provenance_paths.get(experiment_id) or EXPERIMENTS_DIR / experiment_id / "provenance.json"
    if modern_path.exists():
        return _verify_modern_provenance(modern_path)

    prov_path = EXPERIMENTS_DIR / f"{experiment_id}.json"
    if not prov_path.exists():
        return {"exists": False}

    prov = json.loads(prov_path.read_text())
    code = prov.get("code", "")
    if not code:
        return {"exists": True, "has_code": False}

    async def _run():
        executor = SandboxExecutor({"use_docker": True, "max_execution_time": 300})
        return await executor.execute(code, language="python")

    result = asyncio.run(_run())

    # Heuristic comparison: check if key claimed numbers appear in reproduction
    orig_stdout = prov.get("stdout", "")
    new_stdout = result.get("stdout", "")

    # Extract p-values and statistics mentioned in original
    claimed_numbers = re.findall(r"(p[\s<>=]+[\d\.e\-]+|W\s*=\s*[\d\.]+|D\s*=\s*[\d\.]+|mean\s*=\s*[\d\.]+|skewness\s*=\s*[\d\.]+)", orig_stdout, re.IGNORECASE)
    matches = sum(1 for n in claimed_numbers if n.lower() in new_stdout.lower())

    return {
        "exists": True,
        "has_code": True,
        "success": result.get("success"),
        "numbers_claimed": len(claimed_numbers),
        "numbers_matched": matches,
        "reproducible": result.get("success") and matches >= max(1, len(claimed_numbers) * 0.8),
    }


def audit_paper(paper_path: Path) -> dict:
    """Full audit of a single paper."""
    text = paper_path.read_text(encoding="utf-8")

    provenance_paths = extract_provenance_paths(text)
    cited_hashes = extract_provenance_cited_hashes(text)
    experiment_ids = extract_experiment_ids(text)
    references = extract_references(text)
    operational_result = detect_operational_output_issues(text)

    # Provenance check
    prov_check = verify_provenance(experiment_ids, provenance_paths=provenance_paths)
    cited_hash_check = verify_cited_hashes(experiment_ids, provenance_paths, cited_hashes)

    # Reproducibility check. Modern provenance verification is cheap because it
    # checks saved output hashes, so verify every modern experiment. Legacy
    # code re-execution can be expensive, so keep that capped.
    repro_checks = {}
    modern_ids = []
    legacy_ids = []
    for eid in experiment_ids:
        modern_path = provenance_paths.get(eid) or EXPERIMENTS_DIR / eid / "provenance.json"
        if modern_path.exists():
            modern_ids.append(eid)
        else:
            legacy_ids.append(eid)

    for eid in modern_ids + legacy_ids[:2]:
        repro_checks[eid] = verify_reproducibility(eid, provenance_paths=provenance_paths)

    # Numeric verifier
    num_v = NumericVerifier()
    num_result = num_v.verify_text(text, experiment_ids=experiment_ids)

    # Citation verifier (in-text)
    cit_v = CitationVerifier()
    cit_result = cit_v.verify_citations(text)

    # Reference list check (lightweight keyword check for common fake patterns)
    fake_flags = []
    for ref in references:
        # Common LLM hallucination patterns
        if re.search(r"Wang R\.? et al\.? \(2024\)", ref):
            fake_flags.append((ref, "Known hallucinated citation"))
        elif "Optimal Biological Ordering Principles" in ref:
            fake_flags.append((ref, "Known hallucinated title"))

    return {
        "paper": str(paper_path),
        "experiment_ids": experiment_ids,
        "provenance_ok": all(prov_check.values()) if prov_check else None,
        "provenance_details": prov_check,
        "provenance_paths": {eid: str(path) for eid, path in provenance_paths.items()},
        "cited_hashes": cited_hashes,
        "cited_hash_details": cited_hash_check,
        "cited_hash_ok": (
            all(item["ok"] for item in cited_hash_check.values())
            if cited_hash_check else None
        ),
        "provenance_hash_ok": (
            all(r.get("output_hash_ok") is True for r in repro_checks.values())
            and all(item["ok"] for item in cited_hash_check.values())
            if repro_checks and any("output_hash_ok" in r for r in repro_checks.values())
            else None
        ),
        "reproducibility": repro_checks,
        "numeric_claims": num_result["claims"],
        "numeric_flagged": num_result["flagged"],
        "numeric_safe": num_result["safe"],
        "in_text_citations_total": cit_result["total"],
        "in_text_citations_verified": cit_result["verified"],
        "references_count": len(references),
        "suspicious_references": fake_flags,
        "operational_integrity": operational_result,
        "overall_score": _score(
            num_result,
            cit_result,
            prov_check,
            repro_checks,
            fake_flags,
            cited_hash_check,
            operational_result,
        ),
    }


def _score(
    num_result,
    cit_result,
    prov_check,
    repro_checks,
    fake_flags,
    cited_hash_check=None,
    operational_result=None,
) -> int:
    """Simple 0-100 score for paper trustworthiness."""
    score = 50
    hash_checks = [r for r in repro_checks.values() if "output_hash_ok" in r]
    cited_hash_check = cited_hash_check or {}
    if num_result["safe"]:
        score += 20
    if cit_result["total"] > 0 and cit_result["all_verified"]:
        score += 15
    if prov_check and all(prov_check.values()):
        score += 15
    if hash_checks and all(r.get("output_hash_ok") is True for r in hash_checks):
        score += 10
    if cited_hash_check:
        if all(item["ok"] for item in cited_hash_check.values()):
            score += 10
        else:
            score -= 25
    for r in repro_checks.values():
        if r.get("reproducible"):
            score += 10
    score -= len(fake_flags) * 20
    if operational_result:
        score -= len(operational_result.get("unusable_output_blocks", [])) * 15
        score -= len(operational_result.get("contradictions", [])) * 30
        if operational_result.get("contradictions"):
            score = min(score, 20)
        elif operational_result.get("unusable_output_blocks"):
            score = min(score, 60)
    return max(0, min(100, score))


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    papers = [Path(target)] if target else sorted(PAPERS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    for paper in papers:
        print(f"\n{'='*70}")
        print(f"AUDIT: {paper.name}")
        print(f"{'='*70}")
        result = audit_paper(paper)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
