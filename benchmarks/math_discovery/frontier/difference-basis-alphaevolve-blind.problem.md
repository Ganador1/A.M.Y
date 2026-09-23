# Blind replication benchmark — finite difference bases

For a finite set `B` of nonnegative integers, let `k(B)` be the largest integer
`k >= 0` such that every integer from `1` through `k` is a difference `b'-b` of
two elements of `B`. Minimize

`R(B) = |B|^2 / k(B)`

over explicit sets with at most 2,000 elements. Produce the strongest concrete
upper bound you can for the infimum of `R(B)`.

Every proposed construction must be machine-readable in one of these forms:

- `basis=[...]`, an explicit list of distinct nonnegative integers; or
- `A=[...]`, `B=[...]`, `m=...`, representing the product construction
  `{a*m+b : a in A, b in B}`.

The exact evaluator deduplicates the resulting list, rejects negative or noninteger
entries, computes all positive differences with integer arithmetic, finds the first
missing positive difference, and reports the resulting ratio. A proof sketch or
search algorithm without a complete explicit construction receives no objective
credit. Do not assume a claimed coverage or score is correct until the evaluator
confirms it.

You may investigate short interval bases, cyclic difference sets, Singer-type
constructions, product constructions, greedy search, or local mutation. No published
construction or target score is supplied in this blind phase.
