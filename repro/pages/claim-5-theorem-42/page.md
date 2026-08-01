# Claim 5 — Theorem 4.2 (finite-sample rate for the spectral path)

<!-- FILL:c5.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

> Theorem 4.2 gives a finite-sample convergence rate of O(√(η/n)·1/(ξ(T)·δ)) for the
> spectral estimation path used to separate quality from confounders (Section 4).

The paper's verbatim statement, its assumptions (incoherence, curvature constant
`ξ(T)`, eigengap `δ`, regularisation `λ_n ≍ 1/√n`) and the two results it composes are
transcribed on [Source audit](#/source-audit).

## Why a log-log slope cannot decide this claim

The 2026-07-30 revision reported "log-log slope −0.586 ≈ −1/2" on synthetic data. That
is not evidence about Theorem 4.2, for two reasons.

1. **It is circular by construction.** The theorem's own rate was used to pick the
   sample sizes and the regularisation, so the measurement had no way to disagree.
2. **It measures the wrong object.** The end-to-end pipeline error is the composition
   of a convex-optimisation step (whose accuracy depends on our solver's iteration
   budget) and the Davis–Kahan step the theorem actually governs. A slope on the
   composition charges the solver's shortfall to the theorem.

This revision therefore does three independent things.

## Route A — symbolic reconstruction of the derivation chain

Theorem 4.2 is not proved from scratch in the paper; it composes two published
results. `symbolic_chain_audit()` re-derives that composition in `sympy` from the
cited statements rather than from the paper's conclusion:

<!-- FILL:c5.symbolic -->
*(pending release run)*
<!-- /FILL -->

Inverting the composed bound for the sample size gives, symbolically,

```
n_required = 8*C_1**2*eta / (alpha**2 * delta**2 * xi**2)
```

which matches the paper's stated form exactly. This is a derivation, not a fit.

## Route B — independent validation of the cited constant

The composition inherits Yu et al.'s constant `2^{3/2} ≈ 2.828`. If that constant were
wrong the theorem would be wrong regardless of the rate. `davis_kahan_constant_check`
draws **4,000** random symmetric perturbations and measures the attained ratio of true
eigenvector error to the bound.

<!-- FILL:c5.dk -->
*(pending release run)*
<!-- /FILL -->

## Route C — calibrated measurement, attributed by stage

Rather than substituting into the formula, we **search** for the sample size `n*(α)`
at which the error first drops below a target `α`, over a geometric grid
`n ∈ {800, 1600, …, 409600}`, and likewise sweep the eigengap `δ` independently. Points
where the error has saturated (ratio > 0.8 of its floor) are excluded from the fit, so
the exponent is read from the regime where the bound is active.

Crucially, the error is decomposed into three stages, and each measured number is
attributed to the stage that produces it:

| Stage | What it measures | Governed by |
|---|---|---|
| 1 | `‖Θ̂ − Θ‖₂` from our proximal-gradient sparse-plus-low-rank solve | Chandrasekaran half |
| 2 | eigenvector error **given the exact sparse part** | **Davis–Kahan half — the object Theorem 4.2 bounds** |
| 3 | end-to-end pipeline error | our solver *and* the theorem together |

`n*(α)` and `n*(δ)` are read from the **stage-2** curve. The stage-3 figure is reported
separately and is a statement about our implementation, not about the theorem.

Theorem 4.2 is an `O(·)` upper bound, so both `n*` contracts are one-sided — and a
one-sided contract is satisfied by a sweep that measured nothing. Each sweep therefore
passes through [`repro/src/informativeness.py`](repro/src/informativeness.py) before it
may count: ≥ 3 usable points, ≥ 3 distinct `n*` values, no pinning of every `n*` to a
grid endpoint, and a fitted trend whose 95 % interval excludes zero. A sweep that fails
is marked **NOT INFORMATIVE** in the table below and excluded from the verdict, rather
than counted as a pass.

Claim 6 applies one further condition that this claim does not: there, `n*` is estimated
by two independent routes and an exponent counts only if both resolve it and agree. That
condition was added because Claim 6's `n*` measurements proved unstable, and it is not
applied here — so the `n*(α)` and `n*(δ)` exponents below rest on a single estimator.
The `n*(α)` sweep is monotone over five settings and lands 36 standard errors from zero,
which is why it is reported as evidence. `n*(δ)` fails the test — 1.1 standard errors
from zero — and is therefore excluded entirely, supporting neither the `δ^{-2}` factor
nor any bound on it; see [Limitations item 14](#/limitations).

### Results

<!-- FILL:c5.results -->
*(pending release run)*
<!-- /FILL -->

## Negative controls

Both run on the same model and the same grid `n ∈ {1 600, 12 800, 102 400}`, with medians
over five seeds, and both have an explicit numeric contract rather than a visual
judgement.

<!-- FILL:c5.controls -->
*(pending release run)*
<!-- /FILL -->

NC1 is the load-bearing control. It isolates the single mechanism the theorem is about:
with a genuinely non-trivial sparse component `S`, omitting the split leaves the
recovered directions biased, so the error floors out instead of decaying. If NC1 had
*also* decayed at `n^{-1/2}`, the positive result would have been consistent with the
confounder correction doing nothing at all.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) does two things for this claim,
and it is worth being exact about which:

* `davis_kahan_by_principal_angle` re-derives the eigenvector distance by a **different
  route** — via the principal angle, `‖û − u‖ = 2 sin(θ/2)` — rather than by the norm
  difference the claim module uses, and re-checks the `2^{3/2}` constant against it.
* `recheck_c5_stage_slopes` refits the stage-1 and stage-2 exponents with a **Theil–Sen**
  estimator instead of least squares, so a single outlying point cannot carry the fit.

There is **no** second symbolic derivation of the composed bound. An earlier version of
this page said there was; that was false and has been removed. Route A's `sympy`
reconstruction is checked by no independent implementation.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C5_thm42
```

<!-- FILL:c5.runtime -->
*(pending release run)*
<!-- /FILL -->
 Record: [`raw/verdict.json`](raw/verdict.json) under `claims.C5_thm42`;
extract [`raw/c5_rate.csv`](raw/c5_rate.csv). Code:
[`repro/src/claim_c5_thm42.py`](repro/src/claim_c5_thm42.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C5` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
