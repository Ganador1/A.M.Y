---
name: Scientific Validation Issue
about: Report scientific accuracy, reproducibility, or methodology concerns
title: '[SCIENCE] '
labels: scientific-validation
assignees: ''
---

## Scientific Issue

**Type:**
- [ ] Incorrect algorithm implementation
- [ ] Reproducibility failure
- [ ] Inaccurate results
- [ ] Missing validation
- [ ] Wrong assumptions/simplifications
- [ ] Citation/attribution issue
- [ ] Ethics or safety concern

**Domain:**
- [ ] Biology (genomics, proteins, etc.)
- [ ] Chemistry (molecular dynamics, reactions)
- [ ] Physics (quantum computing, simulations)
- [ ] Mathematics (algorithms, proofs)
- [ ] Medicine (clinical, imaging)
- [ ] Neuroscience
- [ ] Engineering
- [ ] Other: ___________

## Issue Description

**Scientific claim or functionality:**
<!-- What algorithm/method/result is in question? -->

**Expected (correct) behavior:**
<!-- What should happen according to scientific literature? -->

**Observed (incorrect) behavior:**
<!-- What is currently happening? -->

**Impact:**
- [ ] Critical - Produces scientifically invalid results
- [ ] High - Significant error affecting accuracy
- [ ] Medium - Minor error but noticeable
- [ ] Low - Edge case or rare scenario

## Evidence

**Reproduction steps:**
1.
2.
3.

**Minimal code to reproduce:**
```python
# Code that demonstrates the issue

```

**Expected output:**
<!-- What should the result be? -->

**Actual output:**
<!-- What is the result? -->

**Reference implementation:**
<!-- Link to correct implementation or reference code -->

## Scientific References

**Key papers:**
<!-- Scientific publications that describe the correct method -->
1.
2.

**Authoritative sources:**
<!-- Textbooks, standards, or established implementations -->
-
-

**Comparison with other tools:**
<!-- How do other established tools handle this? -->
- Tool/Library:
- Version:
- Result:

## Suggested Fix

**Proposed correction:**
<!-- How should this be fixed? -->

**Algorithm/mathematical correction:**
<!-- If applicable, provide correct equations or pseudocode -->

**Code suggestion (if applicable):**
```python
# Suggested fix

```

## Reproducibility Details

**If this is a reproducibility issue:**

**Environment used:**
- [ ] Local (CPU)
- [ ] Local (GPU)
- [ ] Docker
- [ ] Cloud (specify):

**Random seed set:**
- [ ] Yes, seed: ___________
- [ ] No

**Data source:**
<!-- Exact dataset or input used -->

**Expected reproducibility:**
- [ ] Exact numerical match
- [ ] Statistical equivalence (within tolerance)
- [ ] Qualitative agreement

**Observed variance:**
<!-- How different are the results? -->

## Safety and Ethics

**Is this a safety concern?**
- [ ] Yes - Could lead to harmful research
- [ ] Yes - Ethics gate bypass
- [ ] No
- [ ] Unsure

**If yes, describe:**
<!-- What are the safety/ethics implications? -->

## Additional Context

**Affected components:**
<!-- Which services, routers, or modules are affected? -->
-
-

**Version where issue occurs:**
<!-- AXIOM ATLAS version or commit hash -->

**Test coverage:**
<!-- Is there a test for this functionality? Does it pass? -->

## Checklist

- [ ] I have verified this against scientific literature
- [ ] I have provided references to support the claim
- [ ] I have included reproduction steps
- [ ] I have checked if tests exist for this functionality
- [ ] I have considered safety/ethics implications
- [ ] I can provide a corrected implementation (if willing)
