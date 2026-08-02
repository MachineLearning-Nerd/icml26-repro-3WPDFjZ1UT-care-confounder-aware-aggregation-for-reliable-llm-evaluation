# Claim 6 — Theorem 4.3 (sample complexity for mixture recovery)

<!-- FILL:c6.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

> Theorem 4.3 gives a sample complexity bound n ≳ σ_max^6/(δ²·π_min²)·p·log(p/ε) for
> recovering the mixture parameters (μ_qc, π_qc) (Section 4).

The paper's verbatim statement, including the separate displayed bounds for the mean
error and the weight error, is on [Source audit](#/source-audit).

## Result

Theorem 4.3 has two displayed bounds. Both were audited symbolically, by two
implementations that share no code, and both audits are exact — no sampling, no
tolerance, no seed.

| Displayed bound | Verdict |
|---|---|
| (I) mean error `C₁(σ³/δ)√(p log(p/ε)/n)` | **VERIFIED exactly** — the paper's own equations (8) and (10) compose to it with a **zero residual**; the derived-over-stated ratio is the constant `√3·C_dec·C/C₁`, free of σ, δ, p, ε and n |
| (II) weight error `C₂√(p log(p/ε)/n)` | **FALSIFIED as a derivation** — composing the paper's own (8) with (11) yields a bound larger by **exactly `σ_max³`**, an unbounded factor no universal constant `C₂` can absorb |

Both results are obtained twice by machinery with nothing in common: `sympy`
simplification inside the claim module, and exact exponent-vector arithmetic over
`Fraction`s inside [`independent_check.py`](repro/src/independent_check.py). The two
routes are compared for agreement and the comparison is itself a published field, so a
disagreement would fail the run rather than be reported as a result.

**What this does and does not settle.** It falsifies the *written proof* of bound (II):
the displayed chain does not establish the inequality it displays. It does **not** decide
whether bound (II) as stated happens to hold by some other argument — that would require
either a correct alternative derivation or an assumption-satisfying counterexample, and
neither is produced here. Two earlier revisions of this page read an empirical boundary
probe as settling it; at the correct `t(0.975, 3)` quantile that probe's interval
contains both hypotheses, so the reading is withdrawn and the withdrawal is documented in
full below rather than quietly removed.

The sample-complexity **exponents** in σ, π_min and p are **NOT MEASURED** at this
compute budget; the page says so per-sweep instead of reporting an underpowered fit as a
finding. Negative controls confirm the estimator does respond to `n` and to `σ` in the
required directions, so the non-measurement is a power limit, not a broken estimator.

## How the σ³ gap was found, and one empirical hypothesis that failed


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

The honest reading of *this* probe is **not** a falsification. Nor, it turns out, is it a
corroboration — and saying so costs this logbook its tidiest sentence.

**What two earlier revisions said.** That the measured slope's 95 % interval *excludes*
the value 3 a missing `σ³` predicts while *including* 0, so the probe discriminates
between the two hypotheses and points at the derivation rather than the result.

**Why that is withdrawn.** The interval was `slope ± 1.96·se`. This is a five-point fit of
two parameters — **three residual degrees of freedom** — where the two-sided 95 % multiplier
is `t(0.975, 3) = 3.182`, not 1.96. At its correct width the interval **includes 3 as well
as 0**. It excludes neither hypothesis, so it decides nothing. A blind reviewer found this;
it was not caught by any gate here, because no gate checked which quantile was used.

Two further facts point the same way, and neither was load-bearing before:

* The independent checker's Theil–Sen refit of the same five points gives a slope roughly
  **eight times** the least-squares value. Two estimators that far apart on one small
  sample are not measuring a slope.
* The old one-sided check that the refit "agrees there is no `σ` growth" passed by
  clearing its 0.5 threshold by about 0.02 — a margin that is itself inside the noise.

Every interval in this campaign now uses `t(0.975, n−2)`, from a single helper
(`informativeness.t_crit`), and the boundary probe reports **whether it discriminates** as
a separate measured field rather than leaving that to prose.

<!-- FILL:c6.discrimination -->
*(pending release run)*
<!-- /FILL -->

**What survives.** The symbolic finding — that composing the paper's own eq. (8) and
eq. (11) overshoots the stated bound by exactly `σ³` — is untouched by any of this, and is
now reached by **two** independent routes. What does not survive is the claim that the
stated bound was empirically observed to hold in `σ`. That question is **undecided here**,
and reporting it as decided was an error of the same kind as the two falsifications this
logbook has already withdrawn: a conclusion outrunning a small sample.

This is recorded rather than quietly dropped because a reproduction that only reports
confirmations of its own hypotheses is not measuring anything — and because the correction
runs *against* this logbook's convenience, removing a result it had already published.

## The `p·log(p/ε)` factor: a falsification we published, then withdrew

**The 2026-08-01 revision recorded this claim as FALSIFIED. That verdict has been
withdrawn, by this logbook's own verifier, and the reasoning is kept here in full
because the retraction is the result.**

What was published: with `σ`, `δ` and `π_min` held fixed and `p` swept over six
settings, the sample size `n*` needed to reach a fixed accuracy appeared to grow as
`(p·log(p/ε))^{3.63 ± 0.80}` against a stated exponent of 1, "with both `n*` estimators
agreeing and the solver's restart budget ruled out".

Two things were wrong with it.

**1. The estimators were not agreeing.** The agreement test compared only the two
*aggregate* exponents' 95% intervals. **The figures in this paragraph are that withdrawn
revision's, not this run's** — this run's per-setting spreads are rendered further down,
and they are milder. In it, the two `n*` estimators differed per setting by up to
**8.6×, in opposite directions** (at `p = 18`: 2662 by curve-fitting against 308 by
crossing), across decay curves fitted at slopes of −0.076 to −0.260 — against the
theorem's own −0.5 — with r² as low as 0.38. At `p = 18` the error column was
`[0.0648, 0.0892, 0.0564, 0.0497, 0.0611, 0.0511]` against a target of 0.05: noise about
the target, not a decay, and `n*` was extrapolated from it. Two fits through noise
agreeing on a slope is not corroboration. The gate in
[`repro/src/informativeness.py`](repro/src/informativeness.py) now screens **each setting
individually** — the two estimators must agree within 3×, the decay fit must explain the
curve (r² ≥ 0.5), and the decay must be steep enough that extrapolating to the target
does not amplify noise (|slope| ≥ 0.15) — before that setting may enter an exponent fit.

**2. The confound audit could not have found a confound.** It reported `δ`, mean
separation, `cond(M₂)`, `σ` and `π_min` "identical to eight decimal places across every
`p`", but every one of those numbers was written into the table from a `p`-independent
constant, and its `ok` was hard-coded `True`. The previous version of this page even
named the risk — "a `p^{3.6}` growth is consistent with the estimator's conditioning
degrading in `p`… this campaign cannot separate those two" — and then reported a
falsification anyway.

That separation has now been made, and it comes out against the falsification.

<!-- FILL:c6.confound -->
*(pending release run)*
<!-- /FILL -->

Measured from the model actually built at each `p`, at fixed `n`: the empirical `M₂`
top-`k` condition number is **not** constant, and leakage outside the signal subspace
grows by two orders of magnitude across the sweep. At fixed `n` the empirical second
moment simply degrades as dimension grows, so part of any `n*(p)` growth is the moment
estimate deteriorating rather than the `p·log(p/ε)` factor being wrong. The exponent is
therefore **not attributable to the theorem**, and no falsification may rest on it.

With the sweep repeated at 21 seeds and each decay curve continued three points past its
crossing, the surviving settings give an exponent above 1 — but it is **not usable**, for
exactly the reason above.

**And it has since stopped being a measurement at all, for a second and independent
reason.** Three of six settings survive the per-setting screen, so the exponent is fitted
through three points: a two-parameter fit with **one** residual degree of freedom, where
the correct multiplier is `t(0.975, 1) = 12.7`. An earlier revision used the normal 1.96
here — the same defect as the σ probe (§ above) — and at that width both `n*` estimators
appeared to resolve an exponent and to agree. At the correct width the curve-crossing
estimator's interval covers zero: it resolves no exponent, and this logbook's own gate
refuses agreement with an unresolved estimator. The `p` sweep is therefore now reported
**NOT INFORMATIVE**, and the exponent above is not published as a measurement.

The two reasons are independent and both are fatal to any conclusion: the exponent is not
attributable to the theorem's factor (the confound above), *and* it is not resolved by the
data (the interval here). The rendered table below carries the machine-generated status.

**What this claim does establish** is on the rest of this page: the mean bound (I) is
reproduced exactly from the paper's own derivation chain, by two independent routes, and
the displayed proof of the weight bound (II) has a `σ³` gap that is symbolic and exact.
What it does **not** establish: whether bound (II) *as stated* holds — the boundary probe
that earlier revisions read as showing it does is uninformative — and **none** of the
three sample-complexity exponents, in `σ`, `π_min` or `p`, is measured at this budget.

**This test was not pre-registered, and that is recorded rather than hidden.** The
contract written at the start of this campaign
([`raw/claim_contract.json`](raw/claim_contract.json), entry `C6`) names only the `σ`
boundary criterion. The `p` criterion was added mid-campaign, after a censored run had
already shown a large exponent — so the decision to test the `p` factor was prompted by
seeing a large number. A reader who discounts post-hoc findings should discount it
accordingly; as it turns out, the finding did not survive its own gates either.

### Independent refit of the exponent

The `p` sweep carries this falsification, so it is refit by an estimator the claim module
never uses — Theil–Sen, in
[`independent_check.py`](repro/src/independent_check.py) — for **both** `n*` estimators.
An earlier revision of this page asserted such a check existed when it did not.

<!-- FILL:c6.p_refit -->
*(pending release run)*
<!-- /FILL -->

**Why none of these refits rescues the finding.** Every estimate of the exponent exceeds
1, and that was the basis of the withdrawn falsification. It is not sufficient. All of
them are fits to the same per-setting `n*` values, over the same screened settings, and
those values are what the per-setting screen calls into question. In this run the screen
drops half the settings, and it drops all of them for **one** reason: the two `n*`
estimators disagree by more than 3×. Every setting clears the `r²` floor and every decay
slope is steep enough to extrapolate from, so this run is *better behaved* than the one
the withdrawn falsification was computed on — and the finding still does not survive,
because half the sweep cannot be used and what remains is not attributable. The measured
spreads are rendered below rather than typed here, since an earlier revision quoted a
previous run's figures as if they were this one's:

<!-- FILL:c6.screen -->
*(pending release run)*
<!-- /FILL -->

An exponent that is stable across four *fitting methods* applied to the same unreliable
inputs is not thereby a measurement of the system. Independently of all of that, the
confound audit above shows the exponent is not attributable to the theorem's factor in
the first place.

**What the refit is and is not gated on.** The independent checker requires the
Theil–Sen and least-squares exponents to **agree**, and fails the run if they do not. An
earlier revision gated instead on the exponent *exceeding* the theorem's stated 1 — which
would have failed the whole verifier in precisely the case where the paper turned out to
be right. That is an inverted contract rather than a check, and it is gone. The same
revision also fed already-logged values into a helper that logs its inputs, so the two
published "Theil–Sen exponents" were slopes of `log log n`; both are fixed here.

## Calibrated sample-complexity measurement

The claim is a statement about **exponents**, so each parameter is swept independently
and `n*` — the sample size at which the parameter error first falls below
`TARGET = 0.05` — is located by search over a geometric grid:

<!-- FILL:c6.grid -->
*(pending release run)*
<!-- /FILL -->

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
disagree. The grid was also extended downward so the `π_min` search is no longer censored
from below.

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

**Are `σ`, `δ` and `π_min` really held fixed?** `σ` and `π_min` are sweep arguments and
the CP eigenvalues are `λ_i = π_i^{-1/2}`, a function of the mixture weights alone, so
those three are fixed *by construction* and reporting them as measurements that came out
constant would be a vacuous control. The quantities that genuinely could drift with `p`
are measured instead, and one of them does — see
[the withdrawn falsification above](#/claim-6-theorem-43), where that measurement is the
reason the `p`-exponent is not attributable to the theorem.

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

Both are medians over five seeds, with each point's seed range shown beside it. NC2 is the
one that bears on the σ probe: it fails exactly when the `σ`-dependence the theorem asserts
is absent from the estimator. Had NC2 been flat, the σ-sweep above would have been sweeping
a parameter the estimator does not respond to, and its null result would have been
uninformative for that reason as well as the one given there.

An earlier revision called NC2 "**the** discriminating one" on three seeds and bare
medians. That was stronger than the evidence: the reliability figures in the block above
are what decide whether either control discriminates, and they are measured rather than
claimed.

**How far NC2's pass reaches.** Its contract compares only the endpoints, `σ = 3` against
`σ = 1`, so a non-monotone interior would satisfy it. The block above therefore reports
separately whether the error rises at *every* step of the grid, and whether each control's
direction survives seed-to-seed variation at all — both rendered from the run, not asserted
here.

This section has been rewritten twice for reasons worth recording, because both were
measurement errors of ours rather than facts about the estimator.

* A blind reviewer found that NC1 and NC2 used **different seed offsets** at the one
  configuration they share — `σ = 1`, `n = 20 000` — and reported medians 5.2× apart
  there. That is a statement about seed noise, not about either control. They now draw
  from one seed stream, the shared point is literally the same measurement, and the
  identity of the two medians **gates the run**.
* An earlier revision of this paragraph then reported NC2 as **non-monotone**, rising from
  `σ = 1` to `σ = 2` and falling back at `σ = 3`, and attributed it to the estimator
  saturating at large `σ`. With the seeds unified and the count raised from three to five,
  it is monotone. The reversal was an artefact of three seeds and a mismatched offset, and
  the saturation story built on it is withdrawn — it was an explanation for something that
  was not happening.

What remains true, and is the honest limit on both controls: the tensor power method does
not always converge, so an occasional seed returns an error two orders of magnitude above
the median for its setting. That is why the block reports a **rank** statistic — the
fraction of endpoint seed pairs that move the way the control requires — rather than a
ratio of medians against a spread. A single non-convergent seed destroys any max/min
measure while leaving the median trend intact, and an intermediate revision of this page
used exactly such a measure and drew the wrong conclusion from it.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) refits every sweep with a
**Theil–Sen** estimator rather than least squares and re-derives the boundary algebra by
an independent symbolic route, then cross-checks agreement with the claim module.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C6_thm43
```

<!-- FILL:c6.runtime -->
*(pending release run)*
<!-- /FILL -->
 Record: [`raw/verdict.json`](raw/verdict.json) under `claims.C6_thm43`;
extract [`raw/c6_sigma_sweep.csv`](raw/c6_sigma_sweep.csv). Code:
[`repro/src/claim_c6_thm43.py`](repro/src/claim_c6_thm43.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured, except for the elements that entry itself marks `POST-HOC` —
is entry `C6` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
