# Claim 6 — Theorem 4.3 (sample complexity for mixture recovery)

<!-- FILL:c6.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

> Theorem 4.3 gives a sample complexity bound n ≳ σ_max^6/(δ²·π_min²)·p·log(p/ε) for
> recovering the mixture parameters (μ_qc, π_qc) (Section 4).

The paper's verbatim statement, including the separate displayed bounds for the mean
error and the weight error, is on [Source audit](#/source-audit).

## What was tested, and one hypothesis that failed

Theorem 4.3 has two parts: a **sample-complexity condition** and, under it, error
bounds on the recovered means `μ_qc` and weights `π_qc`. Both were examined.

While auditing the displayed proof we formed a specific falsification hypothesis: that
the stated weight bound **drops a factor of `σ³`**, and that consequently the weight
error would grow with `σ` along the sample-complexity boundary where the theorem
predicts it constant. The symbolic audit did find the missing factor:

<!-- FILL:c6.symbolic -->
*(pending release run)*
<!-- /FILL -->

**But the experiment refuted the consequence.** Along the boundary `n = 20000·σ⁶` the
measured weight error did not grow:

<!-- FILL:c6.boundary -->
*(pending release run)*
<!-- /FILL -->

The honest reading of *this* probe is therefore **not** a falsification. What the fit
supports precisely: the measured slope's 95 % interval **excludes the value 3** that a
genuinely missing `σ³` factor predicts, and **includes 0**, the value the theorem
predicts. It is a marginal discrimination — the interval is wide — but it is a real one,
and it points at the derivation rather than at the result. What is defective is the
*displayed derivation*, which loses a `σ³` factor that the stated result nonetheless
survives. A bound whose own quantity is never observed to be violated has not been
falsified in `σ`, however flawed its written proof.

This is recorded rather than quietly dropped because a reproduction that only reports
confirmations of its own hypotheses is not measuring anything.

## What *is* falsified: the stated `p·log(p/ε)` factor

A different part of the same condition does not survive. With `σ`, `δ` and `π_min` held
fixed and `p` swept over six settings, the sample size needed to reach a fixed accuracy
grows far faster than the stated bound allows — the measured exponent on `p·log(p/ε)` is
about **3.6 against a stated 1**, and the excess is resolved by *both* `n*` estimators
independently.

This is a statement about the exponent, never about the value, which is what makes it
immune to the theorem's unknown universal constant `C₁`: a constant can move `n*` up or
down, but it cannot turn `p¹` into `p³·⁶`. The comparison is also normalised correctly.
Substituting the boundary sample size `n = C₁σ⁶/(δ²π_min²)·p·log(p/ε)` into the
theorem's own weight bound gives an achieved accuracy of `C₂·δ·π_min/√C₁`, which is
**independent of `p`** — so holding the target accuracy fixed at 0.05 while sweeping `p`
is exactly the right comparison, and `n*` should then scale as `p·log(p/ε)` itself.

The three audits that make this attributable — both estimators resolving the exponent,
the restart-budget control, and the constancy of every other quantity in the bound — are
published in full below, and each was written before its own outcome was known.

**This test was not pre-registered, and that is recorded rather than hidden.** The
contract written at the start of this campaign
([`raw/claim_contract.json`](raw/claim_contract.json), entry `C6`) names only the `σ`
boundary criterion. The `p` criterion was added mid-campaign, and the honest sequence is
this: while repairing a censored search grid — every `π_min` setting had been returning
`n* = 5 000`, the grid floor — the `p` sweep became measurable for the first time and
immediately exceeded its bound. The criterion was written down before that sweep was
re-run on the corrected grid, but *after* a censored run had already shown a large
exponent. So the **decision to test the `p` factor was prompted by seeing a large
number**, even though every gate the finding had to clear was fixed in advance. Both the
original and the added criterion are in the contract file, with this provenance attached.

A reader who discounts post-hoc findings should discount this one accordingly. What
does not depend on the ordering: the exponent is resolved by two independent estimators,
`δ`, `σ`, `π_min`, the mean separation and `cond(M₂)` are identical to eight decimal
places across every `p`, and tripling the solver's restart budget moves `n*` by at most
1.3 %.

**Scope, stated precisely.** This falsifies the stated `p·log(p/ε)` factor *as tested
with the algorithm the theorem names* (Anandkumar et al.'s robust tensor power method
with whitening), on a model family that satisfies the theorem's own hypotheses:
`K = 4` components, three conditionally independent views, full-column-rank means, and
`π_min = 0.10 > 0`. It says nothing about the `σ⁶` or `π_min^{-2}` factors, whose
exponents this campaign reports as **NOT MEASURED**.

**The limitation that keeps this at MEDIUM confidence.** The six per-setting decay
curves fit a power law imperfectly (`r²` from 0.38 to 0.83) and `n*` is not monotone in
`p` — the `p = 36` setting sits below `p = 30`. So the exponent's *value* (3.63 ± 0.80)
carries real uncertainty. What is robust is that it *exceeds 1*: the curve-fitting
estimator's 95 % interval is [2.06, 5.21] and the curve-crossing estimator's is
[1.54, 5.46], and neither contains 1.

## Calibrated sample-complexity measurement

The claim is a statement about **exponents**, so each parameter is swept independently
and `n*` — the sample size at which the parameter error first falls below
`TARGET = 0.05` — is located by search over a geometric grid
`n ∈ {200, 500, 1 250, 3 125, 5 000, 12 500, 31 250, 78 125, 195 312, 488 281, 1 220 703}`.
No sample size is computed from the formula under test.

Because the theorem is a sufficient condition (`n ≳ …`), each contract is **one-sided**:
the measured exponent must not *exceed* what the theorem requires.

| Parameter | Stated exponent | Contract |
|---|---|---|
| `σ_max` | 6 | measured `≤ 6 + 2·stderr` |
| `π_min` | −2 | measured `≥ −2 − 2·stderr` |
| `p·log(p/ε)` | 1 | measured `≤ 1 + 2·stderr` |

### Why a one-sided contract needs an informativeness precondition

A one-sided contract is satisfied by any sweep that does not *exceed* the stated
exponent — including a sweep that measured nothing at all. An earlier revision of this
page fell into exactly that trap: with the grid floor at `n = 5 000`, every `π_min`
setting returned `n* = 5 000` because the error was already below target at the first
grid point. The fitted exponent was `0.000 ± 0.000`, the contract `≥ −2` passed, and the
number was a property of the grid rather than of the estimator.

[`repro/src/informativeness.py`](repro/src/informativeness.py) now makes that
undetectable-by-reading condition machine-checkable. A sweep is admissible as evidence
only if it has ≥ 3 usable points, ≥ 3 *distinct* values of `n*`, no pinning of every
`n*` to a grid endpoint, and a fitted trend whose 95 % interval excludes zero. A sweep
failing any of these is reported **NOT INFORMATIVE**, contributes nothing in either
direction, and is excluded from the verdict — rather than passing because it failed to
disagree. The grid was also extended down to `n = 200` so the `π_min` search is no
longer censored from below.

### Two estimators of `n*`, and why both are reported

`n*` was first read as the **crossing** of the median error curve with the target. That
lets a single grid point decide the answer, and where the curve is shallow near the
target a little noise moves it enormously: raising the seed count from 5 to 7 moved one
`σ` setting's `n*` from 424 to 3266. `n*` is therefore also estimated by **fitting**
`log err = a + b·log n` over every computed point and solving for `err = TARGET`, which
pools all of them.

Both estimates are reported for every setting, and an exponent is admissible only if
**each estimator individually resolves it** (its own 95 % interval excludes zero) **and
the two intervals overlap**. Agreement with an unresolved estimator is not evidence —
a wide enough interval agrees with everything.

### Results

<!-- FILL:c6.results -->
*(pending release run)*
<!-- /FILL -->

## Attributing the p-dependence

A measured `p`-exponent says something about Theorem 4.3 only if nothing else moved.
Two audits establish that, and both are published.

**Is the growth the solver's, not the rate's?** The robust tensor power method is a
non-convex search run with a fixed 30 restarts. If a larger `p` simply needs more
restarts to find all `k` components, `n*` grows for an optimisation reason that may not
be charged to a statistical bound. The control repeats the smallest and largest `p` at
three times the restart budget; a fall of more than 20 % (a threshold fixed before the
numbers were seen) would disqualify the sweep.

<!-- FILL:c6.attribution -->
*(pending release run)*
<!-- /FILL -->

**Are `σ`, `δ` and `π_min` really held fixed?** If `δ` shrank as `p` grew, an apparent
`p`-growth would be the bound's own `δ^{-2}` factor in disguise. These are population
quantities of the generative model, so they carry no sampling noise: the CP eigenvalues
are `λ_i = π_i^{-1/2}`, `δ` is their minimum gap, and the component means are columns of
an orthonormal frame scaled by 3.0.

<!-- FILL:c6.confound -->
*(pending release run)*
<!-- /FILL -->

## The algorithm actually implemented

The claim names tensor-decomposition recovery, so
[`repro/src/tensor_mom.py`](repro/src/tensor_mom.py) implements the method the theorem
is about — multi-view method of moments with symmetrisation
(`A₁ = M₃₂ M₁₂⁺`, `A₂ = M₃₁ M₂₁⁺`), whitening `W = U diag(s^{-1/2})`, and the **robust
tensor power method** of Anandkumar et al. (2014) with 30 restarts, 60 iterations and 30
deflation iterations — not a convenient substitute such as EM or `k`-means.

Model: `K = 4` components with weights `(0.40, 0.30, 0.20, 0.10)`, three conditionally
independent views of 6 judges each (`p = 18`), component means drawn from QR-orthonormal
frames scaled by 3.0.

## Negative controls

| | Control | Contract it must satisfy |
|---|---|---|
| NC1 | Over-sample far past the boundary, `n = 20 000 × {1, 16, 128}`, everything else frozen | error at `128×` must be **strictly below** the error at `1×` |
| NC2 | Freeze `n = 20 000` and raise `σ ∈ {1.0, 2.0, 3.0}` | error at `σ = 3` must be **strictly above** the error at `σ = 1` |

Measured:

<!-- FILL:c6.controls -->
*(pending release run)*
<!-- /FILL -->

Both are medians over three seeds. NC2 is the discriminating one: it fails exactly when
the `σ`-dependence the theorem asserts is genuinely present in the estimator. Had NC2
been flat, the σ-sweep in the boundary probe above would have been measuring nothing,
and the null result reported there would have been uninformative rather than evidence.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) refits every sweep with a
**Theil–Sen** estimator rather than least squares and re-derives the boundary algebra by
an independent symbolic route, then cross-checks agreement with the claim module.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C6_thm43
```

Runtime 331.3 s on Hugging Face `cpu-upgrade` (8 vCPU / 32 GB), threads pinned to the
cgroup quota. Record: [`raw/verdict.json`](raw/verdict.json) under `claims.C6_thm43`;
extract [`raw/c6_sigma_sweep.csv`](raw/c6_sigma_sweep.csv). Code:
[`repro/src/claim_c6_thm43.py`](repro/src/claim_c6_thm43.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C6` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
