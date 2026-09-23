# An exact rational witness for the minimum-autocorrelation functional

Technical note accompanying the exact witness.

**Responsible maintainer:** Ganador1. Computer-assisted construction and verification using AMY, operator-supplied optimization code and Codex implementation assistance.

## Abstract

We provide a nonnegative rational step function yielding a lower bound of 0.40863826 for the minimum-autocorrelation functional on shifts in [0,1]. The certificate is checked using exact interval intersections and integer correlation sums. The comparison improves a specified public witness by Kevin Russell. No global optimality or worldwide-priority claim is made. The computational contribution is an explicit witness in a known family, rather than a new reduction theorem.

## Statement

For nonnegative, nonzero integrable functions on the real line, let

\[
 C=\sup_f\frac{\min_{0\le t\le1}\int_{\mathbb R}f(x)f(x+t)\,dx}
 {(\int_{\mathbb R}f(x)\,dx)^2}.
\]

The finite witness supplied with this note establishes

\[
 C\ge\frac{25472093474917464906152750403804195198286625}
 {62334087449348808708328853738083398757238922}
 >0.40863826.
\]

The decimal on the right is rounded downward. This does not imply the rounded-up statement C ≥ 0.40863827.

## Finite certificate and proof

The file candidate.json contains 960 nonnegative rational heights, their common denominator, and a positive rational cell width d. Set

\[
 f(x)=\sum_{i=0}^{959}h_i\mathbf1_{[id,(i+1)d)}(x),\qquad
 S_k=\sum_i h_i h_{i+k},
\]

with out-of-range heights zero. For t=(k+θ)d, 0≤θ≤1, the autocorrelation equals

\[
 a_f(t)=d[(1-\theta)S_k+\theta S_{k+1}].
\]

This follows by summing interval overlaps. Hence a_f is affine between grid shifts, and its minimum on [0,1] occurs at a grid shift in that interval or at t=1. Checking the endpoint is essential when 1/d is not integral. The mass is dΣh_i. Exact arithmetic at these finitely many points, divided by the square of that mass, gives the fraction above.

The supplied verifier checks 740 nodes/endpoints and 739 midpoints for this representation. Midpoints check implementation agreement; the affine argument establishes continuous coverage. The second method computes interval intersections separately from the correlation sums. Deliberately increasing the declared ratio or altering one height causes rejection. Both methods share the proof reduction and Python interpreter; independent external review remains desirable.

## Attribution, comparison and limitations

The underlying question is due to Barnard and Steinerberger, [Three Convolution Inequalities on the Real Line with Connections to Additive Combinatorics](https://arxiv.org/abs/1903.08731). The construction lineage starts from [Kevin Russell's minimum-autocorrelation witness](https://github.com/techno-optimist/minimum-autocorrelation-bound), whose pinned ratio is 2378625/5958277. The step-function finite reduction is known; it is not claimed as a new AMY theorem.

The observed research process used AMY-selected requests with supplied deterministic optimization and verification code. This compact note does not establish the complete historical search chronology, and it does not attribute independent invention of the algorithm to AMY. The compact witness does not include a complete search-lineage archive, exhaustive priority review or external mathematical review.

## Reproduction

From the repository root, run `python release_evidence/autocorrelation/verify.py`. The compact package uses the standard library and requires no network, cloud model or optimization library. See its README, SOURCE.json and manifest for the distinction between the mathematical payload and the original research artifact.
