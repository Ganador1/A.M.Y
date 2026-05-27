# A.M.Y Security Review

Date: 2026-05-27

## Executive Summary

This review covered the Python/FastAPI application surface, A.M.Y to Atlas tool execution, sandbox execution, security diagnostics, public API defaults, and secret hygiene. The largest risk class is agentic tool abuse: prompt injection or untrusted API input causing privileged tools to run unintended actions. The current branch improves that posture by adding deterministic fail-closed checks on A.M.Y's direct tool path, fixing the security control verifier, replacing dynamic Python evaluation in Atlas numeric tools, tightening public API defaults, and protecting the Lean4 management router with an admin scope.

The project is safer than the previous public state, but it should still be treated as a research preview until router-level authorization is made consistent across all public APIs and the sandbox is isolated by default for any untrusted public execution.

## Threat Model Snapshot

Primary assets:
- Local credentials and API tokens in environment variables, `.env`, encrypted key stores, and Atlas config.
- Tool execution capability across math, code, literature, lab, Lean4, and cloud/lab integrations.
- Paper provenance, experiment outputs, audit logs, and generated manuscripts.
- Availability budget for paid model APIs and external scientific APIs.

Main attacker capabilities assumed:
- Remote user can send API requests if the FastAPI app is exposed.
- Remote user can influence prompts, paper content, tool inputs, or literature/query text.
- Local contributor can modify project files before release.

Main boundaries:
- User/API input to FastAPI routers.
- A.M.Y reasoning output to Atlas tool execution.
- Atlas worker subprocess and sandbox subprocess execution.
- Outbound HTTP calls to scientific APIs.
- Generated papers/provenance to public artifacts.

## Critical

### C-1: Dynamic Python evaluation in Atlas numeric tools

Status: Fixed in this branch.

Location: `atlas/app/run_agent_with_tools_legacy.py` around numeric/statistical tool parsing.

Evidence: The previous implementation used `np.array(eval(...))` in `numpy_statistics`, `numpy_correlation`, and `hypothesis_tester`. That allowed tool input text to be interpreted as Python code before statistical computation.

Impact: If a dangerous input reached these tools, it could execute local Python side effects under the Atlas process.

Fix applied: Added `_parse_numeric_array_literal()` using `ast.literal_eval` and replaced all `np.array(eval(...))` uses. Added regression coverage in `tests/test_security_guardrails.py`.

## High

### H-1: Router authorization remains inconsistent

Status: Partially fixed.

Locations:
- `atlas/app/main.py:50` to `atlas/app/main.py:63` registers domain routers and automatic routers.
- `atlas/app/routers/workspaces.py:146` creates a workspace router without a router-level auth dependency.
- `atlas/app/routers/literature_search.py:143` and `atlas/app/routers/literature_search.py:187` expose literature search routes without a router-level auth dependency.
- `atlas/app/routers/lean4_management.py:37` was fixed to require `system:admin`.

Impact: Publicly exposed routes can create workspaces, consume external API budget, trigger compute, or expose operational state unless every sensitive router is protected by a consistent default-deny policy.

Recommended next fix: Add a central protected router registry policy: default all non-health routes to authenticated access, require explicit public allowlist for `/health`, maybe `/status`, and read-only showcase endpoints. Then add a test that fails when a new state-changing route lacks `Depends(require_scopes(...))` or a documented public exemption.

### H-2: Agentic prompt injection remains a residual risk

Status: Mitigated, not eliminated.

Locations:
- `core/heartbeat.py:412` to `core/heartbeat.py:460` fail-closed side-effect gate.
- `core/heartbeat.py:757` to `core/heartbeat.py:761` now gates direct scientific tool execution too.
- `core/atlas_tools.py:69` to `core/atlas_tools.py:122` fail-closed Atlas misuse and shared safety checks.
- `atlas/app/security/misuse_guard.py` contains rule-based misuse prevention.

Impact: A malicious paper, prompt, or external content can still try to steer A.M.Y into allowed-but-abusive tool sequences. Rule-based filters reduce obvious abuse but do not prove the model cannot be confused.

Recommended next fix: Add a capability-scoped tool broker. Each mission should get an explicit allowlist of tools, domains, max cost, max runtime, network policy, and write policy. High-risk tools should require a deterministic approval object, not only natural-language intent.

References: OWASP lists prompt injection and insecure output handling as major LLM application risks; NCSC emphasizes that agentic systems should constrain tool privileges because model outputs remain inherently confusable.

### H-3: Public API production defaults were unsafe

Status: Fixed in this branch.

Locations:
- `atlas/main.py:55` to `atlas/main.py:89`
- `atlas/main.py:315` to `atlas/main.py:317`
- `atlas/app/main.py:42` to `atlas/app/main.py:48`
- `atlas/app/security/auth.py:37` to `atlas/app/security/auth.py:59`

Evidence fixed: Wildcard CORS with credentials, always-on docs, development reload, weak auth fallback, and old API title were changed to safer defaults. Production docs now require opt-in, CORS uses explicit local origins by default, credentials are off unless configured, reload is opt-in dev-only, auth fails closed in production, and the public API title is `A.M.Y API`.

## Medium

### M-1: The lightweight FastAPI entrypoint lacks the full middleware stack

Status: Open.

Location: `atlas/app/main.py:42` to `atlas/app/main.py:63`

Impact: This entrypoint now has safer docs defaults, but it does not visibly apply the same request size limits, rate limiting, TrustedHost enforcement, and security headers configured in `atlas/main.py`.

Recommended next fix: Extract shared `configure_security_middleware(app)` and call it from both entrypoints. Add tests for CORS, TrustedHost, request-size rejection, and security headers using FastAPI TestClient.

### M-2: Sandbox is policy-gated but not isolated by default

Status: Open.

Location: `sandbox/executor.py:50` to `sandbox/executor.py:71`, `sandbox/executor.py:98` to `sandbox/executor.py:154`

Impact: The sandbox blocks many dangerous patterns and strips sensitive environment variables, but default execution still runs as a local subprocess. Static filters are useful defense-in-depth, not a complete boundary for public untrusted code.

Recommended next fix: Use Docker or another OS-level isolation mode by default for any public/API-driven execution, with read-only mounts, no network unless explicitly required, CPU/memory/pid limits, and a clean working directory.

### M-3: SSRF protection exists but is not uniformly enforced

Status: Open.

Locations:
- `atlas/app/security/ssrf_guard.py:121` defines URL validation.
- `atlas/app/autonomous/interfaces/external_apis.py:82` creates a general HTTP client with redirects enabled.

Impact: Some outbound HTTP surfaces validate URLs, but the codebase still has direct HTTP clients. Any future route that accepts user-controlled URLs could bypass SSRF protections unless validation is centralized.

Recommended next fix: Expose a single outbound HTTP helper that validates destination host, scheme, resolved IP, port, redirect targets, and timeout. Add a static test that flags direct `requests`/`httpx` calls in app code unless explicitly exempted.

## Low

### L-1: Security diagnostics now run, but should be added to CI

Status: Fixed locally, CI integration recommended.

Location: `scripts/diagnostics/verify_security_controls.py`

Fix applied: The script now resolves the real repo root and checks the numeric literal parser, guardrail tests, sandbox gate, secret hygiene verifier, and ignore policies.

Recommended next fix: Run `scripts/diagnostics/verify_security_controls.py` and `scripts/diagnostics/verify_secret_hygiene.py` in the release workflow.

## Verification Performed

- `.venv/bin/python -m pytest tests/test_security_guardrails.py::test_heartbeat_scientific_tool_direct_path_blocks_before_tool_call tests/test_security_guardrails.py::test_security_control_diagnostic_resolves_repo_paths tests/test_security_guardrails.py::test_public_api_entrypoints_use_safe_security_defaults -q`
- `.venv/bin/python -m pytest tests/test_security_guardrails.py::test_atlas_registry_numeric_tools_parse_literals_without_eval -q`
- `.venv/bin/python -m py_compile atlas/main.py atlas/app/main.py atlas/app/security/auth.py atlas/app/routers/lean4_management.py atlas/app/run_agent_with_tools_legacy.py core/heartbeat.py scripts/diagnostics/verify_security_controls.py`
- `.venv/bin/python scripts/diagnostics/verify_security_controls.py`
- `.venv/bin/python scripts/diagnostics/verify_secret_hygiene.py`
- `.venv/bin/python -m pytest tests/test_security_guardrails.py tests/test_atlas_misuse_guard.py tests/test_heartbeat_paper_pipeline.py tests/test_public_release_hygiene.py tests/test_scientific_hardening.py -q`
- `.venv/bin/python tests/test_amy_quick.py`
- `.venv/bin/python tests/test_cognitive_cycle.py`

Note: `.venv/bin/python tests/test_amy_atlas_integration.py` was interrupted after several minutes because the Atlas worker stayed idle without producing output. The narrower cognitive-cycle integration passed and exercised the modified `numpy_statistics` and `hypothesis_tester` paths.

## External Guidance Used

- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- FastAPI dependencies and security dependency model: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI CORS guidance: https://fastapi.tiangolo.com/de/tutorial/cors/
- OWASP CSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- NCSC prompt injection guidance: https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection
- OWASP MCP Top 10: https://owasp.org/www-project-mcp-top-10/
