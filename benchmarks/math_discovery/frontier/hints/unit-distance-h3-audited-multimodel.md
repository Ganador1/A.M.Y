# H3 audited multi-model starting point

Investigate the proposed negative resolution of the planar unit-distance bound,
but do not treat the number-field skeleton as established. Any repaired route must
close every item below with explicit inequalities and exact distance preservation.

## Candidate skeleton

The attempted route uses totally real fields of growing degree and bounded root
discriminant, CM extensions, split prime ideals, class-group collisions, norm-one
elements, a bounded Minkowski-lattice region, and projection to one complex
coordinate. It aims to produce enough planar unit steps to violate
`nu(n) <= n^(1 + C/log log n)` for every fixed `C > 0` along arbitrarily large
sizes.

## Fatal obligations already found

1. A large fibre in a class-group map does not by itself make the relevant ideals
   principal. Prove the exact principal-ideal count; do not cite pigeonhole alone.
2. Bounds on `h_K R_K` do not imply that `2^d / h_K` stays exponential. Track class
   number and regulator losses separately and numerically.
3. Multiplying by units only shifts an archimedean log vector by a discrete lattice.
   It does not guarantee exact zero at all embeddings. Approximate modulus is not
   exact unit distance.
4. If an element is an algebraic integer and every conjugate has modulus one,
   Kronecker forces it to be a root of unity. Any fractional/S-unit workaround must
   control a common denominator and height without losing the count.
5. A generic injective projection on a finite point set does not preserve prescribed
   Euclidean lengths. Prove that each counted difference has modulus exactly one in
   the selected complex embedding.
6. For every proposed step vector, count how many translated pairs remain inside the
   finite planar point set and control multiplicity and collisions.
7. Derive explicit functions `n(d)` and `M(d)`. To refute the statement, prove
   `log M(d) * log log n(d) / log n(d)` is unbounded, not merely positive or larger
   than one fixed constant.
8. Preserve the quantifiers: for every `C > 0` and every `N`, produce `n >= N`.
   One fixed positive exponent or the classical Erdos lower-bound constant is not
   enough unless all preceding planar steps are rigorous.

## Search policy

Repair the skeleton only if all obligations can close simultaneously. Otherwise
isolate the strongest rigorously provable obstruction and switch to a genuinely
different representation. A correct impossibility result for this skeleton is
valuable but is not a resolution of the original open problem.
