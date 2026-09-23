# Recovery campaign scientific contracts

The launcher calls `labs.run(name, parameters, unique_output_directory)` and retains every request, response, candidate and trace. These tools make no model calls. The model selects a bounded request; fixed Python implementations generate and check the numerical results. A successful execution is not evidence of novelty.

## AR(1) early-warning benchmark

Each seed block fixes 128 calibration trajectories and 128 independent evaluation trajectories. A block uses distinct calibration and evaluation seeds. The same evaluation innovations pair three arms: stationary phi=0.6, the same stationary process plus a linear positive deterministic trend of total amplitude8, and increasing phi from0.2 to0.9. Each trajectory has512 observations after256 burn-in observations. The positive arm burns in atphi0.2; null arms atphi0.6.

The statistic is the OLS slope over time of rolling lag1 Pearson correlation with stride16, using either64 or128 observations per window. Each method is calibrated against its own stationary-null distribution using the empirical95th percentile (higher order statistic). Strict exceedance is detection. Report numerator, denominator and Wilson95% intervals; overlapping windows are not counted as independent replicates. The raw method is always paired with the selected detrending method. Linear detrending removes the deterministic linear nuisance up to floating arithmetic by construction.

These are Monte Carlo measurements, not exact mathematical certificates. Repeated model selection across blocks and methods makes comparisons exploratory. Do not call the reported intervals simultaneous, claim a guaranteed5% false-positive rate, or treat a100% observed positive-control detection rate as a universal guarantee. A later confirmatory comparison needs new seeds frozen after method selection.

## SSH constrained gap

Exactly21 rational hoppings (22 sites), each in[1/4,7/4], with exact sum21. The tool rejects resource changes rather than renormalizing silently. It returns an existing exact finite-open-chain half-filling squared-gap certificate and independently replays its verifier, checking that the certificate matches the requested hoppings. Increasing the overall scale is therefore unavailable as a trivial improvement. Comparisons should use nonoverlapping certified intervals when claiming a larger actual gap; a better lower bound alone can reflect certificate tightness. No certificate implies topology, an infinite-system statement, physical validation or novelty.

## Autocorrelation

Search begins from the hash-pinned best local1920-cell witness, not a weaker legacy baseline. The existing bounded trust-region LP actually runs; candidate generation is followed by an independent exact rational verifier. The iteration limit is20 and LP-search time budget is at most30seconds. Exact certificate generation/verification is additional work, so this is not a hard wall-clock timeout for the entire call. Source, candidate and trace must be retained. Strict improvement means exact rational comparison against this frozen local witness. Failure to improve is a legitimate result. It proves neither a global optimum nor world priority. All candidates in this campaign use the same baseline; the launcher must explicitly implement any later adoption policy, not imply adaptive adoption that did not happen.
