# A.M.Y research probe: C(13) >= 37 after power-loss recovery

We seek an explicit set of 37 distinct lattice points in `[0,12]^3` such that
no five selected points are coplanar or cospherical. Any proposed witness must
survive independent enumeration of all `C(37,5)=435897` five-subsets using
exact integer determinants.

Established exact facts and current search state:

- A canonical exact-valid 36-point witness exists; SHA-256
  `333d36ece36e3d845cd2f5bb26e5460f78d881c00418c92cae8bd5215ab0629a`.
- It is saturated: no single grid point can be added.
- Exhaustive exact local analysis proves no `r-out/(r+1)-in` escape for
  `r <= 5` from this witness.
- A gain-two search from many exact-valid 35-point states has so far produced
  no joint compatible insertion set.
- Mixed antipodal-shell/residue ruin-and-rebuild explored more than 619000
  rebuilds without a canonically new exact-valid 36-set.
- The active exact lazy MILP has 2197 binary variables, cardinality 37, exact
  overlap 30 with the record36 seed, coordinate-layer constraints `<=4`, and
  exact global surface cuts `sum(surface cells)<=4` generated from violated
  planes/spheres. It has audited 23 integer candidates and accumulated 3207
  exact cuts. The latest candidate had 38 bad five-subsets. A timeout recovery
  now rotates deterministic objective epochs while preserving all cuts.
- A Rust cut generator checks all 435897 five-subsets and emits both weak
  conflict cuts and normalized global plane/sphere cuts. A separate Python
  Bareiss audit is the final truth gate.
- Maximum three concurrent workers and moderate RAM are hard constraints.

Task:

1. Diagnose the strongest structural bottleneck in the current methods.
2. Propose up to three concrete algorithmic interventions that are genuinely
   different from merely increasing runtime or changing random seeds.
3. For each intervention give an implementable formulation, the exact
   invariant/correctness gate, likely computational cost, and a small pilot
   whose outcome would falsify the idea quickly.
4. Pay special attention to decomposition methods (Benders/column generation),
   symmetry-aware diversification away from the record36 basin, conflict
   hypergraph formulations, and whether overlap=30 should be relaxed or staged.
5. If you can derive a valid stronger inequality than existing surface cuts,
   state it precisely and prove why it is globally valid. Do not invent an
   inequality without proof.

Return a technically detailed research memo. Distinguish proved statements,
heuristics, and conjectures. Do not claim C(13)>=37 unless an explicit exact
witness is supplied.
