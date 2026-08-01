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
step is deterministic linear algebra on a fixed judge-score matrix; producing that matrix
is the GPU-bound step. Of Tables 1–2's twelve columns the authors released matrices for
three, and **two of those are reproduced here end-to-end** with the authors' own code at
`72f5b29`, over five seeds, with no synthetic substitute anywhere.

The third released column, PKU-BETTER, cannot be scored at all: every released label
source for it is constant, so an accuracy computed from it would be meaningless. An
executable precondition catches this before any number is produced, and the column is
BLOCKED rather than scored. The remaining nine columns have no released judge outputs
and would need GPU inference over 11–20 LLM judges — the paper's own Appendix E.2
reports up to 3 hours per dataset on an A100. Those are BLOCKED against that named
capability rather than replaced by a proxy.

**2. The theorem claims are decided by reconstructing the derivations, not by fitting a
slope.** A log-log slope on synthetic data cannot decide a universally quantified
theorem; it can only corroborate it on a measure-zero sample. Each theorem claim is now
addressed by a symbolic reconstruction of the paper's own derivation, by deriving
constants analytically, and — where the statement is false — by an exact
assumption-satisfying counterexample. Finite experiments appear only as calibrated
searches (binary search for `n*`, independent sweeps of each parameter), never by
substituting into the formula under test.

## Six results that cut against a flattering story, and one that does not

They are stated here rather than buried, because a reproduction that only ever confirms
its own hypotheses is not measuring anything -- and the one that came out in the paper's
favour is kept in the same list, because a reproduction that only ever finds fault is
not measuring anything either.

* A conjectured falsification of Theorem 4.3's weight bound **did not survive
  measurement**. Having found a missing `σ³` factor in the displayed derivation, we
  predicted the weight error would *grow* with `σ` along the sample-complexity boundary.
  It did not: the measured slope is 0.0605 ± 1.1149, whose 95 % interval excludes the 3
  a missing `σ³` predicts and includes the 0 the theorem predicts. The finding was
  downgraded from FALSIFIED to a documented gap in the displayed proof.
* A **different** part of Theorem 4.3 *was* falsified, and not the part we set out to
  attack. With `σ`, `δ` and `π_min` held fixed, the sample size needed for a fixed
  accuracy grows as `(p·log(p/ε))^{3.63 ± 0.80}` against a stated exponent of 1, with
  both `n*` estimators resolving the excess and the solver's restart budget ruled out.
* The full Algorithm-1 pipeline's empirical error exponent falls short of `n^{-1/2}` at
  our solver's iteration budget. That shortfall is attributed to our proximal-gradient
  solver, not to the theorem, and the attribution is demonstrated rather than asserted
  by a three-stage decomposition in which the theorem-governed stage is measured
  separately.

* The paper's headline **17.37% average improvement is not an average across
  benchmarks**, and this revision says so where the previous one flinched. "Improvement
  of the mean MAE" is identically an MAE-weighted mean of the per-dataset improvements,
  and because ASSET is scored on a 0–100 scale while the other five benchmarks sit near
  1, ASSET absorbs 84.4% of the weight. The statistic is therefore not invariant to a
  unit change on a single benchmark: report ASSET on 0–10 and the figure moves, and the
  paper's ordering — a larger gain over AVG than over MV — **reverses**. The
  unit-invariant across-benchmark average is 15.19%. The 2026-08-01 revision of that
  page had these numbers and still called it "a finding … not an error"; that was an
  error of nerve, and it is recorded rather than quietly fixed.
* A check that ran **in the paper's favour**. Asking whether any single CARE
  configuration attains "best on 5 of 6" found that none does — the best is CARE-Tensor
  at 3 — but also that CARE-Tensor held fixed across all six datasets is never worse
  than 2nd of 9 methods, against the strongest single baseline's 1 column. The headline
  integer needs a family reading; the superiority behind it does not.
* A Table 2 column we expected to reproduce turned out to be **unscoreable**. Reproducing
  PKU-BETTER returned accuracies of exactly 0.0 for four methods and exactly 1.0 for
  CARE-Tensor. Read carelessly, MV scoring 0.000 against a published 0.701 is a
  spectacular refutation of the paper. It is nothing of the sort: every released label
  source for that dataset is constant, so there is no accuracy to compute. The column is
  BLOCKED by a failed precondition and no verdict about CARE is drawn from it in either
  direction. Reporting it as a falsification would have been the most eye-catching result
  in this logbook and the wrong one.

All of them are also in [Limitations and deviations](#/limitations).

## How to check any of this

Every claim page carries the exact claim string, the paper's exact quantifiers, the
executable verifier, the raw numbers inline, a downloadable extract, and a negative
control with a stated failure mode. The [Visibility matrix](#/visibility-matrix) records
that per claim. Two gaps are named rather than papered over: Claim 3 has no permutation
control on the Table 2 *accuracy* path (only on the MAE path, under Claims 1–2), and
Claim 5's `sympy` reconstruction of the composed bound is checked by no second
implementation. Both are in [Limitations](#/limitations). The single
command and pinned environment are on
[Fixed command, environment, seeds, runtime](#/environment-and-command).

`repro/src/run_all.py` exits **1** whenever any claim contract or the independent
checker fails. It is not a report generator.
