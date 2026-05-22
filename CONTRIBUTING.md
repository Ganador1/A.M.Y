# Contributing to A.M.Y

Thank you for considering a contribution to A.M.Y. The project welcomes pull requests, issues, scientific feedback, and new tool adapters.

## Before you start

1. Read the SCIENCE_MANIFESTO.md and the USE_POLICY.md. Both express the spirit of the project.
2. Run the regression tests locally: `.venv/bin/python -m pytest tests/test_atlas_misuse_guard.py tests/test_security_guardrails.py tests/test_science_gates.py`. They should pass 30/30 before you start.
3. If you are about to touch the safety policy, read SECURITY.md as well.

## Setting up your environment

```bash
git clone <your fork>
cd A.M.Y
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
cp .env.example .env
# add your Ollama Cloud key to .env
```

Atlas has its own venv at atlas/.venv_new. See ENVIRONMENT.md.

## What to contribute

### Adding a new Atlas tool

1. Add a wrapper function in atlas/app/extended_science_tools.py.
2. Register a ToolDescriptor with name, domain, description, input_format.
3. Add a test in tests/.
4. Add an entry under the matching domain in SCIENCE_MANIFESTO.md and README.md.

### Improving the rubric scorer

The rubric scorer at experiments/ab_test/scoring/score_paper.py is deliberately deterministic. New checks are welcome but each new check should:

- Be regex- or provenance-based (no LLM judge for scoring).
- Have a documented weight.
- Come with a paired test that demonstrates the metric responds to the intended signal.

### New cognitive agents

A.M.Y v1.0 ships with Ranking and Reflection. If you propose a new agent (planning, memory, simulation), it should:

- Live under cognition/.
- Be wireable into communication/paper_generator.py without breaking existing behaviour.
- Pass the existing 30/30 tests.
- Come with a measurement of its effect on the rubric (an A/B in experiments/).

## Style

- Code in English, comments only when WHY is non-obvious.
- Black or ruff format; ruff is configured in atlas/.
- Async by default for IO; never sleep in hot paths.
- Never bypass the misuse_guard. Tests in tests/test_atlas_misuse_guard.py must keep passing.

## Pull requests

- One feature per PR.
- Include before/after numbers when you claim a rubric improvement.
- If your PR modifies the safety policy, please ping the maintainer privately first.
- Do not add Co-Authored-By lines for AI assistants in commit messages; commits should be attributed to the human who reviewed and merged them.

## Reporting issues

Use the GitHub issue tracker. For security-sensitive issues use SECURITY.md instead.

## Code of conduct

Be kind, be precise, be honest about what your code does and does not do.
