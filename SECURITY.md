# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in A.M.Y, please report it responsibly.

**Do NOT open a public issue.** Instead, email the maintainer directly:

- **Contact:** giovanniaramgio@gmail.com
- **Subject prefix:** `[A.M.Y SECURITY]`

Please include:

1. A clear description of the vulnerability.
2. Steps to reproduce.
3. Affected component(s) (e.g. `core/atlas_worker.py`, `atlas/app/security/misuse_guard.py`).
4. Your assessment of severity and potential impact.
5. Any suggested mitigation.

We aim to acknowledge reports within **72 hours** and provide a remediation plan within **14 days** for high-severity issues.

## What counts as a security issue

We treat the following as in-scope:

- **Misuse guard bypass.** Inputs that cause the `misuse_guard` policy ([atlas/app/security/misuse_guard.py](atlas/app/security/misuse_guard.py)) to incorrectly allow operations it should block (chemical/biological weapons, fissile materials, mass surveillance, critical infrastructure attacks, etc.).
- **Provenance forgery.** Ways to make a generated paper claim a SHA-256 hash that does not match the underlying tool output.
- **Sandbox escape.** Code-execution paths that escape the experiment sandbox ([sandbox/executor.py](sandbox/executor.py)) and access host resources.
- **Secret exfiltration.** Any path by which the system leaks API keys, environment variables, or other secrets to outputs, logs, or generated papers.
- **Worker protocol confusion.** Inputs that cause the Atlas worker JSON protocol to be corrupted (stdout pollution, deserialization issues).
- **Reflection / Ranking bypass.** Ways to make a paper pass the Reflection gate while containing claims that the gate is designed to block.

## What is NOT in scope

- Bugs in third-party libraries (PySCF, AstroPy, ASE, etc.). Please report these upstream.
- The fact that, once cloned, anyone can edit the code and remove the guards. This is a property of open-source software, not a vulnerability.
- Issues that require unrealistic threat models (e.g. attacker with physical access and root on your machine).
- Quality issues in generated papers that the Reflection Agent already flags as `high` or `medium` severity. The rubric is designed to surface these; they are not vulnerabilities.

## Coordinated disclosure

We follow a 90-day coordinated-disclosure timeline by default:

1. **Day 0** — report received, acknowledgement sent.
2. **Day 0-14** — investigation and reproduction.
3. **Day 14-60** — fix developed and tested.
4. **Day 60-90** — fix released; reporter credited unless anonymity is requested.
5. **Day 90+** — vulnerability disclosed publicly.

If a vulnerability is being actively exploited in the wild, we may accelerate this timeline.

## Hall of Fame

Security researchers who report valid vulnerabilities will be credited here (with their consent).

*(empty so far — be the first!)*

## Why the guards matter

A.M.Y deliberately ships with a `misuse_guard` that fails closed (denies by default if the policy engine cannot be loaded). The guard covers:

- Chemical weaponisation
- Biological weaponisation
- Cyber abuse
- Unauthorised human experimentation
- Guardrail tampering
- Fissile material synthesis / weaponisation
- Mass surveillance and individual targeting
- Critical infrastructure attack

Bypasses in these categories are treated as **critical-severity** issues.

The capabilities that A.M.Y orchestrates (PySCF, ASE, RDKit, AstroPy, etc.) are all independently available in PyPI without guardrails. A.M.Y's value, including from a security perspective, is that it adds *organisation, provenance, and refusal* on top of those capabilities. Helping us keep those refusals correct is a contribution to the whole ecosystem.

Thank you for helping keep A.M.Y safe.
