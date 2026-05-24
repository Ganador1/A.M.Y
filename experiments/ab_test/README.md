# A/B Test Harness

This directory keeps the scoring and regeneration scripts used to compare paper quality gates.

The public tree retains only the `real_improved/` papers generated after the provenance and reflection gates were wired into the pipeline. Older baseline and synthetic-improvement drafts were removed from the public release because they predated full SHA-256 provenance and contained known invalid tool-output markers.

To run a fresh comparison, regenerate local baseline drafts first, then run:

```bash
python experiments/ab_test/run_ab.py
python experiments/ab_test/scoring/score_paper.py
```

Fresh generated outputs should stay local unless they pass the release hygiene tests.
