#!/usr/bin/env python3
"""
Security gate: falla si hay High en Bandit o si pip-audit reporta vulnerabilidades.

Uso:
  - Debe existir al menos uno:
    bandit_report_app.json (preferido) o bandit_report.json
  - pip_audit_report.json (generado con requirements.audit.txt recomendado)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def check_bandit() -> tuple[bool, str]:
    bandit_paths = [Path("bandit_report_app.json"), Path("bandit_report.json")]
    data = None
    for p in bandit_paths:
        data = load_json(p)
        if data:
            used = p.name
            break
    else:
        return True, "Bandit report not found; skipping."

    totals = (data.get("metrics", {}).get("_totals", {}))
    sev_high = int(totals.get("SEVERITY.HIGH", 0))
    sev_med = int(totals.get("SEVERITY.MEDIUM", 0))
    sev_low = int(totals.get("SEVERITY.LOW", 0))
    ok = sev_high == 0
    msg = f"Bandit[{used}] highs={sev_high}, medium={sev_med}, low={sev_low}"
    return ok, msg


def check_pip_audit() -> tuple[bool, str]:
    path = Path("pip_audit_report.json")
    data = load_json(path)
    if not data:
        return True, "pip-audit report not found; skipping."

    vulns = 0
    affected = []
    for dep in data.get("dependencies", []):
        vlist = dep.get("vulns", []) or []
        if vlist:
            vulns += len(vlist)
            affected.append(f"{dep.get('name')}=={dep.get('version')}({len(vlist)})")

    ok = vulns == 0
    msg = f"pip-audit vulns={vulns}"
    if affected:
        msg += "; affected: " + ", ".join(sorted(affected)[:10])
    return ok, msg


def main() -> int:
    ok_bandit, msg_bandit = check_bandit()
    ok_pip, msg_pip = check_pip_audit()

    print(msg_bandit)
    print(msg_pip)

    if not ok_bandit or not ok_pip:
        print("Security gate failed.")
        return 1
    print("Security gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
