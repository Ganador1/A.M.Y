# Exact minimum-autocorrelation witness

This package proves an explicit feasible lower bound, **C ≥ 0.40863826**, by exact rational arithmetic. It does not prove global optimality, worldwide novelty, or a complete autonomous-discovery history.

```bash
python3 release_evidence/autocorrelation/verify.py
```

Python 3.10+; standard library only; no model, network or scientific-library installation is required. Run from any working directory by using the script's absolute path. The command checks the manifest, recomputes the bound, compares it with the pinned Russell rational value and rejects two corrupted certificates. It prints a JSON report without rewriting the package.

## Mathematical statement

For `C = sup_{0≠f≥0, f∈L¹(R)} min_{0≤t≤1} ∫f(x)f(x+t)dx / (∫f)²`, the witness gives

`C ≥ 25472093474917464906152750403804195198286625 / 62334087449348808708328853738083398757238922`.

The mathematical payload in candidate.json specifies nonnegative rational heights and a positive rational common cell width d. Let `f(x)=Σ h_i 1_[id,(i+1)d)(x)`. The overlap of two equal-width intervals is triangular in the shift, so their finite sum is affine between consecutive grid shifts. The minimum on [0,1] is therefore attained at a grid shift or at the endpoint 1. The verifier checks all such nodes using an interval-intersection method and a separate integer-correlation method; it also checks midpoint agreement and symmetry. The denominator is the square of L¹ mass, not the L² norm. This proves coverage of continuous shifts rather than extrapolating from a floating-point grid.

## Attribution and limits

The problem and inequality framework are due to Barnard and Steinerberger; the project starts from Kevin Russell's published step-function construction, with pinned comparison value `2378625/5958277`. Sources: https://arxiv.org/abs/1903.08731 and https://github.com/techno-optimist/minimum-autocorrelation-bound . The method is known; the proposed contribution is the stronger concrete witness.

AMY selected search requests within a supplied laboratory. Codex helped implement the optimizer and checkers; Ganador1 directs and reviews the project. SOURCE.json identifies the original mathematical artifact and its hash. The original source is retained separately; this compact package removes machine-specific paths and is a new derivative artifact. It does not replace the full run archive or authenticate provider identity.

The two arithmetic methods share the mathematical reduction and interpreter. External mathematical review and a broader priority check are still required before describing this as a new record. Earlier packages proving 0.40197195 remain historical evidence and are superseded by this witness for the proposed note.

Code and project-authored text: Apache-2.0, see LICENSE. No upstream certificate or paper text is redistributed here.
