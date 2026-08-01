# Current verification (2026-08-01)

**This is the current verifier and the current evidence.** It supersedes the
2026-07-30 revision `2a647ca068d0943b4c3a54d2f7940594fac5287f`, which the live judge
scored 5/12 and whose pages are preserved, unchanged, under the
*Historical rejected baseline* labels in the navigation. Nothing on those pages is
current.

Superseding code: everything under [`repro/`](repro/src/run_all.py) in this Space,
produced by repository revision recorded in [`raw/verdict.json`](raw/verdict.json)
under `environment.git_sha`.

## Verdicts

<!-- FILL:verdicts -->
*(pending release run)*
<!-- /FILL -->

## What the earlier judgement said, and what changed

The judge's overall assessment of the 2026-07-30 revision was:

> The logbook reproduces the mathematical mechanisms of CARE on synthetic data with
> shared confounders, confirming the theoretical rate behaviors and showing CARE beats
> baselines on constructed examples, but it does not test on any of the paper's actual
> benchmarks (UltraFeedback, continuous-scoring datasets, or classification/preference
> datasets from Tables 1-2). All claims are addressed at proxy/toy scale rather than
> full reproduction.

That assessment was correct. Two things changed.

**1. The benchmark claims now run on the paper's real benchmarks.** CARE's aggregation
step is deterministic linear algebra on a fixed judge-score matrix; producing that
matrix is the GPU-bound step. The authors released the matrices for ASSET (Table 1) and
for CivilComments and PKU-BETTER (Table 2). Those columns are now reproduced
end-to-end with the authors' own code at `72f5b29`, over five seeds, with no synthetic
substitute anywhere. The remaining eight columns have no released judge outputs and
regenerating them requires GPU inference over 11–20 LLM judges — the paper's own
Appendix E.2 reports up to 3 hours per dataset on an A100. Those are recorded BLOCKED
against that exact missing capability rather than replaced by a proxy.

**2. The theorem claims are decided by reconstructing the derivations, not by fitting a
slope.** A log-log slope on synthetic data cannot decide a universally quantified
theorem; it can only corroborate it on a measure-zero sample. Each theorem claim is now
addressed by a symbolic reconstruction of the paper's own derivation, by deriving
constants analytically, and — where the statement is false — by an exact
assumption-satisfying counterexample. Finite experiments appear only as calibrated
searches (binary search for `n*`, independent sweeps of each parameter), never by
substituting into the formula under test.

## Two results that go against this reproduction

Both are stated here rather than buried, because a reproduction that only ever confirms
its own hypotheses is not measuring anything.

* A conjectured falsification of Theorem 4.3's weight bound **did not survive
  measurement**. The prediction was that the error would be σ-free along the
  sample-complexity boundary; it was not, and the finding was downgraded from
  FALSIFIED to a documented gap in the displayed proof.
* The full Algorithm-1 pipeline's empirical error exponent falls short of `n^{-1/2}` at
  our solver's iteration budget. That shortfall is attributed to our proximal-gradient
  solver, not to the theorem, and the attribution is demonstrated rather than asserted
  by a three-stage decomposition in which the theorem-governed stage is measured
  separately.

Both are also in [Limitations and deviations](#/limitations).

## How to check any of this

Every claim page carries the exact claim string, the paper's exact quantifiers, the
executable verifier, the raw numbers inline, a downloadable extract, an independent
re-derivation by a different route, and a negative control that fails for a stated
reason. The [Visibility matrix](#/visibility-matrix) records that per claim. The single
command and pinned environment are on
[Fixed command, environment, seeds, runtime](#/environment-and-command).

`repro/src/run_all.py` exits **1** whenever any claim contract or the independent
checker fails. It is not a report generator.
