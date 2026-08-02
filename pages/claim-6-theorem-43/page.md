# Claim 6 — Theorem 4.3 (sample complexity for mixture recovery)

<!-- FILL:c6.header -->
**Verdict:** **FALSIFIED (the displayed proof) and VERIFIED (the mean bound) — both exact, both reached by two independent routes.** (1) **VERIFIED:** composing the paper's own equations (8) and (10) reproduces the stated mean-error bound exactly — the derived-over-stated ratio is `sqrt(3)*C*C_dec/C_1`, free of σ, δ, p, ε and n, so the two differ by at most a universal constant, which is what the theorem asserts (`mean_bound_reproduced_exactly = True`). (2) **FALSIFIED as a derivation:** composing the paper's own (8) with (11) yields a weight-error bound larger than the stated one by exactly **σ_max³** (`factor_missing_from_stated_weight_bound = sigma**3`) — an unbounded factor no universal constant `C₂` can absorb, so the displayed chain does not establish the inequality it displays. Both results are obtained twice by machinery that shares no code: `sympy` simplification in the claim module, and exact exponent-vector arithmetic over `Fraction`s in the independent checker (`exponent-vector arithmetic in exact Fractions; no symbolic algebra`); the two routes are compared for agreement and the comparison is a published field (`c6_two_route_agreement_evaluated = True`), so a disagreement fails the run rather than being reported as a result. Scope, stated precisely: this falsifies the **written proof**, not the bound itself. Whether bound (II) as stated happens to hold is **not decided here** — the boundary probe two earlier revisions read as settling it has a 95 % interval containing both hypotheses at the correct t quantile, and that reading is withdrawn. Of the three sample-complexity exponents, 2 are now **MEASURED** and 1 (`pi_min`) is **NOT MEASURED** at this budget. Where they are measured they come out *below* the stated exponent, which for a sufficiency condition is consistent with the theorem and shows the factor is not tight -- except `p`, whose measured exponent is **not attributable** to the theorem because a control finds the empirical second-moment conditioning degrades as `p` grows. Negative controls confirm the estimator does respond to `n` and to `σ` in the required directions (`negative_controls.ok = True`), so that is a power limit rather than a broken estimator

**Confidence: MEDIUM.** What stands is exact and symbolic: composing the paper's own cited results reproduces the mean bound (I) with no residual factor, and fails to reproduce the stated weight bound (II) by exactly sigma_max^3 -- a factor that grows without bound, so no universal constant absorbs it. That is a defect in the displayed derivation, established in sympy and re-derived by a second route. It is NOT a falsification of bound (II) itself: whether that bound happens to hold by some other argument is not decided here, and the boundary probe two earlier revisions read as deciding it resolves nothing at the correct t quantile. What does NOT stand: two earlier revisions each reported a falsification of this theorem -- one in sigma, one in the p*log(p/eps) factor -- and BOTH have been withdrawn on this campaign's own evidence. The rebuilt confound audit finds a real confound in the second: at fixed n the empirical M2 conditioning degrades with p and subspace leakage grows by two orders of magnitude, so part of any n*(p) growth is the moment estimate deteriorating rather than the stated factor being wrong. The sample-complexity exponents in sigma, pi_min and p are therefore NOT MEASURED at this budget, and the delta^-2 factor is not independently variable in this generative model. MEDIUM, not HIGH, because the strongest result here is about a proof rather than about the theorem's truth.

Machine-checkable contract satisfied by the release run: **yes**.

**But 1 contract element was NOT MEASURED**: `n*(pi_min)`. A sweep that resolved no exponent cannot satisfy a one-sided contract and cannot violate one; it is excluded, and the 'satisfied' above refers only to the elements that were measured.
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
| (I) mean error `C₁(σ³/δ)√(p log(p/ε)/n)` | **VERIFIED exactly** — the paper's own equations (8) and (10) compose to it; the derived-over-stated ratio is `√3·C_dec·C/C₁`, free of σ, δ, p, ε and n, so the two differ by at most a universal constant |
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

**Two of the three sample-complexity exponents are now MEASURED**, and getting there was
a grid-resolution fix rather than more compute. The `σ` sweep produced a clean monotonic
`n*` at all seven settings, but the per-setting dual-estimator screen was discarding the
four smallest: `NS_GRID` stepped ~2.5× per point, so at `σ_max = 1.0` (`n* ≈ 353`) only
four grid points lay below `n*`, the two estimators of `n*` disagreed there, and the screen
— correctly — rejected the setting. Refining the grid to ~1.6× below `n = 5000`, which is
the cheap end because cost grows with `n`, raised the usable settings from 3 of 7 to 5 of 7.

| Exponent | Measured (95 % CI) | Stated | Reading |
|---|---|---|---|
| `σ` | **[2.62, 5.41]** | 6 | **MEASURED**; excludes 6 |
| `p` | **[2.78, 3.17]** | 1 | **MEASURED** but **NOT ATTRIBUTABLE** — see below |
| `π_min` | [−0.32, 0.26] | −2 | **NOT MEASURED** — screen still blocks it |

**What the `σ` result means, and what it does not.** The interval excludes the stated 6, but
Theorem 4.3 states a *sufficiency* condition — `n ≳ σ⁶…` samples suffice. Needing fewer
than a sufficient condition demands is **entirely consistent with the theorem**. This is
evidence that the `σ⁶` factor is **not tight** in this generative model, not that it is
wrong, and it is recorded that way.

**Why the `p` exponent is reported but not used.** Its interval [2.78, 3.17] sits far above
the stated 1, which is the direction that *would* indicate the stated condition is
insufficient — the most consequential result available on this page. It is **not claimed**,
because the confound audit that runs alongside it finds a real confound: the empirical
second-moment top-`k` condition number is not constant across `p`, and subspace leakage
grows **259×** between `p = 15` and `p = 36` at fixed `n`. Part of the measured growth is
therefore the moment estimate deteriorating rather than the `p log(p/ε)` factor being
wrong, and the audit reports `measured_quantities_held_fixed: false`. An earlier revision
of this campaign published exactly this exponent as a falsification and had to withdraw it;
it is not being published as one again.

**Why `π_min` still reads NOT MEASURED with all seven settings usable.** Its own interval
[−0.32, 0.26] does exclude the stated −2. But the dual-estimator screen requires *both*
estimators of `n*` to resolve an exponent, and the curve-fitting estimator's interval covers
zero — agreement with an estimator that resolved nothing is not evidence. **That screen was
left in place rather than relaxed**, which is precisely why the `σ` and `p` numbers above
can be trusted.

Negative controls confirm the estimator does respond to `n` and to `σ` in the required
directions, so what remains unmeasured is a power limit, not a broken estimator.

## How the σ³ gap was found, and one empirical hypothesis that failed


Theorem 4.3 has two parts: a **sample-complexity condition** and, under it, error
bounds on the recovered means `μ_qc` and weights `π_qc`. Both were examined.

While auditing the displayed proof we formed a specific falsification hypothesis: that
the stated weight bound **drops a factor of `σ³`**, and that consequently the weight
error would grow with `σ` along the sample-complexity boundary where the theorem
predicts it constant. The symbolic audit did find the missing factor:

<!-- FILL:c6.symbolic -->
| Quantity | Value |
|---|---|
| `mean_bound_reproduced_exactly` | **yes** |
| `factor_missing_from_stated_weight_bound` | `sigma**3` |
| `derived_over_stated_on_boundary` | `C*C_pi*sigma**3/C_2` |
| `grows_without_bound_in_sigma` | **yes** |
<!-- /FILL -->

**But the experiment did not decide the consequence either way.** Along the boundary
`n = 20000·σ⁶` the measured weight error showed no growth *at the precision this probe
achieves* — and that precision turns out to be too low to distinguish "no growth" from
the growth a missing `σ³` predicts. Two earlier revisions read the same numbers as a
refutation. They were wrong, for a reason set out immediately below:

<!-- FILL:c6.boundary -->
| σ_max | n on the boundary | median weight error `max|π̂−π|` | stated bound unit `√(p log(p/ε)/n)` | ratio error / bound unit |
|---|---|---|---|---|
| 1.00 | 20000 | 0.0210 | 0.0684 | 0.3071 |
| 1.25 | 76294 | 0.0419 | 0.0350 | 1.1965 |
| 1.50 | 227812 | 0.0074 | 0.0203 | 0.3671 |
| 1.75 | 574458 | 0.0070 | 0.0128 | 0.5506 |
| 2.00 | 1280000 | 0.0038 | 0.0085 | 0.4403 |

Fitted exponent **0.0605 ± 1.1149** (95 % CI -3.488 to 3.609). Predicted if the σ³ factor were genuinely missing: 3.0; predicted if the theorem is correct as stated: 0.0. **Excludes the σ³ hypothesis (slope 3):** **no** · **excludes the theorem's prediction (slope 0):** **no** · **decides between them:** **no**. The interval contains both hypotheses, so this probe supports neither. An earlier revision printed here 'σ³ violation hypothesis supported by the data: **yes**', rendered from the block's `ok` field — which means only that the least-squares fit returned two finite numbers and could not have read 'no' unless the probe crashed. A blind reviewer found it; it asserted a falsification of Theorem 4.3 that this page's own verdict header denies.

The exponent is fitted to the **ratio** column, which is the quantity the theorem bounds by a constant; the raw weight error itself falls with σ because n rises as σ⁶ along the boundary. Both columns are shown so the two cannot be confused.

**Do not read this table against the negative controls below.** They share the nominal configuration σ_max = 1, n = 20 000, but they draw from *different seed streams* — the boundary probe seeds `1000 + 17·s`, the controls `500 + 13·s` — and at that shared point their medians differ by about 1.8×. That spread is between-stream noise, not a disagreement between two measurements of one quantity. An earlier revision of this page invited exactly that comparison, which was the same defect a blind reviewer had already found between NC1 and NC2; those two were unified onto one stream, the boundary probe was not. The published `shared_configuration_cross_check` quantifies stream-to-stream spread for the controls only.
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
| Quantity | Value |
|---|---|
| Measured slope (least squares) | 0.0605 |
| Standard error | 1.1149 |
| Points fitted / residual dof | 5 / 3 |
| 95 % multiplier used | t(0.975, 3) = 3.182 |
| 95 % interval | [-3.4876, 3.6086] |
| Excludes the σ³ hypothesis (slope 3) | **no** |
| Excludes the theorem's prediction (slope 0) | **no** |
| **Discriminates between them** | **no** |
| Same points, Theil–Sen | 0.4801 |
| Gap between the two estimators | 0.4195 |
| Estimators agree | **no** |

the interval must exclude exactly one of the two hypotheses to decide between them; excluding neither means the probe measured nothing about the sigma-dependence in either direction. the two estimators disagree by far more than either one's own claimed precision, so the boundary probe resolves no slope and must not be read as evidence for or against the missing sigma^3 factor.
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
| p | min ‖μᵢ−μⱼ‖ | empirical cond(M̂₂) on top-k | leakage outside top-k |
|---|---|---|---|
| 12 | 4.242641 | 3.9415 | n/a |
| 15 | 4.242641 | 4.2053 | 0.0017 |
| 18 | 4.242641 | 4.3613 | 0.0215 |
| 24 | 4.242641 | 3.8274 | 0.1715 |
| 30 | 4.242641 | 4.0243 | 0.1454 |
| 36 | 4.242641 | 13.1168 | 0.4422 |

**Fixed by construction, not measured:** `sigma_max` = 1.0000, `pi_min` = 0.1000, `delta_cp_eigenvalue_gap` = 0.2446, `population_m2_condition_number` = 4.0000. sigma and pi_min are sweep arguments; lambda_i = pi_i^{-1/2} depends only on PI_TRUE; population M2 eigenvalues are pi_i * MEAN_SCALE^2 for an orthonormal mean frame. None is a function of p.

**Measured, and held fixed across the sweep:** min_pairwise_mean_separation **yes**, empirical_m2_topk_condition_number **no**

Leakage outside the signal subspace grows **259×** between `p` = 15 and `p` = 36 at fixed `n` — the smallest and largest `p` at which it is defined; it is undefined at `p` = 12, where there is no subspace outside the top `k`. A measured p-exponent is attributable to the theorem's own factor: **no**. the empirical M2 top-k condition number is not constant across p, and subspace leakage grows 259x between p = 15 and p = 36 at fixed n.
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
| Estimator | Exponent on p·log(p/ε) | Computed by |
|---|---|---|
| least squares, fitted n* | 2.946 | claim module |
| least squares, crossing n* | 2.632 | claim module |
| **Theil–Sen, fitted n*** | **3.058** | independent checker |
| **Theil–Sen, crossing n*** | **2.987** | independent checker |

All four are fitted over the **same** settings — the 4 that survive the per-setting screen (`p` = 12, 15, 24, 36). An earlier revision fitted the robust estimator over all six and called the difference "estimator".

Stated exponent: **1**. Every estimate exceeds it: **yes** (lowest 2.987, highest 3.058). The robust estimates **bracket** the least-squares value rather than falling below it, so no single outlying setting is carrying the fit — which removes the one remaining reason to think the exponent's *value* was an artefact of least squares.

Theil–Sen agrees with least squares within 1.0: **yes**, and **that** is what the independent checker gates on. It does **not** gate on the exponent exceeding 1: an earlier revision did, which would have failed the entire verifier in exactly the case where the theorem turned out to be right. None of this rescues the withdrawn falsification, because agreement between estimators fitted to the same inputs says nothing about whether those inputs are attributable to the theorem — and the confound audit says they are not.
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
| p | n* (fitted) | n* (crossing) | estimator ratio | r² | decay slope | screen |
|---|---|---|---|---|---|---|
| 12 | 107.9 | 141.2 | 1.31× | 0.965 | -0.386 | usable |
| 15 | 255.2 | 392.8 | 1.54× | 0.835 | -0.281 | usable |
| 18 | 1536.7 | 438.3 | 3.51× | 0.670 | -0.147 | **dropped** |
| 24 | 1570.9 | 2656.6 | 1.69× | 0.736 | -0.201 | usable |
| 30 | 6955.6 | 1906.1 | 3.65× | 0.716 | -0.191 | **dropped** |
| 36 | 4827.5 | 3982.8 | 1.21× | 0.735 | -0.213 | usable |

Across the 6 settings: `r²` ranges **0.670 to 0.965** against the screen's floor of 0.5, the two `n*` estimators disagree by up to **3.65×** against a limit of 3×, and every decay slope clears the |slope| ≥ 0.15 floor (shallowest 0.147). **4 of 6** settings survive; the fit that produces the exponent uses only those. Reasons the rest were dropped: `p` = 18 — the two n* estimators disagree by 3.5x (limit 3.0x); the decay is too shallow to extrapolate (slope=-0.147, |slope| < 0.15); n* amplifies noise by ~7x; `p` = 30 — the two n* estimators disagree by 3.6x (limit 3.0x).
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
`n ∈ {20, 32, 50, 80, 125, 200, 320, 500, 800, 1 250, 2 000, 3 200, 5 000, 12 500, 31 250, 78 125, 195 312, 488 281, 1 220 703}`

Target accuracy: `max_(q,c) |π̂ − π| ≤ 0.050`.
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
| Parameter | Stated exponent | Measured | One-sided contract | Status | Passes |
|---|---|---|---|---|---|
| σ_max | 6.0 | 4.010 ± 0.486 | `exponent <= 6 + 2*stderr` | MEASURED | **yes** |
| π_min | -2.0 | -0.033 ± 0.110 | `exponent >= -2 - 2*stderr` | NOT INFORMATIVE | n/a |
| p·log(p/ε) | 1.0 | 2.946 ± 0.150 | `exponent <= 1 + 2*stderr` | MEASURED | **no** |

Per-parameter contract outcome: sigma = **True** · pi_min = **NOT MEASURED** · p = **False**. `NOT MEASURED` is published as itself rather than collapsed to a pass — the verifier's own gate treats an unmeasured sweep as non-failing, which is correct (absence of evidence is not failed evidence) and is not the same statement as a satisfied contract. Informative sweeps: ['sigma', 'p']; uninformative: ['pi_min']. A sweep marked NOT INFORMATIVE contributes no evidence in either direction and is excluded from the verdict; it is shown here so the exclusion is visible rather than silent.

* **π_min — NOT INFORMATIVE.** the curve-fitting estimator's own 95% interval covers zero, so it resolved no exponent; agreement with an unresolved estimator is not evidence

Independent Theil–Sen refit of the σ boundary probe: slope 0.4801 against least squares 0.0605, differing by 0.4195. The two estimators **do not agree on the magnitude** — the difference is of the same order as the smaller of them. An earlier revision printed here that both 'fall under the 0.5 threshold for no σ-growth: **yes**'; the Theil–Sen figure clears that threshold by about 0.02, a margin this logbook elsewhere calls inside the noise, so printing it as an affirmative in the results block of a claim whose verdict is 'decides nothing' invited exactly the misreading a blind reviewer flagged. The disagreement is itself the finding: it is a second reason the σ probe is not measuring a slope.

Not measured: delta is the CP eigenvalue gap of Anandkumar et al. (2014) Theorem 5.1 and is not a free parameter of the generative model we can set independently, so its delta^-2 factor is reconstructed from the derivation but not measured.
<!-- /FILL -->

## Attributing the p-dependence

A measured `p`-exponent says something about Theorem 4.3 only if nothing else moved.
Two audits establish that, and both are published.

**Is the growth the solver's, not the rate's?** The robust tensor power method is a
non-convex search run with a fixed 30 restarts. If a larger `p` simply needs more
restarts to find all `k` components, `n*` grows for an optimisation reason that may not
be charged to a statistical bound. The control repeats the smallest and largest `p` at
three times the restart budget and compares `n*`.

**This control cannot exonerate the sweep, and the reason is structural rather than
empirical.** It runs two `p` settings, while its own admissibility gate requires at least
three ratios before it will report an attribution — so `ok` is `False` on every possible
run, and `p_exponent_attributable_to_the_theorem` is set `False` regardless of what the
comparison finds. The 20 % fall that an earlier revision of this paragraph described as
the operative disqualifier is therefore never operative. What the comparison did return is
reported below for what it is worth (both ratios came out above 0.9, i.e. no restart-driven
collapse was observed at the two settings tested), but **no attribution rests on it**, and
the `p` exponent is NOT MEASURED for the independent reasons given above. Naming a live
threshold over a gate that can never open is the kind of vacuous pass this logbook has had
to remove elsewhere; it is left visible here rather than quietly deleted.

<!-- FILL:c6.attribution -->
| p | n* at 30 restarts | n* at 90 restarts | ratio |
|---|---|---|---|
| 12 | 108 | 108 | 1.0000 |
| 36 | 4828 | 4680 | 0.9694 |

Solver-bound: **no**. p-exponent attributable to the theorem rather than to the search budget: **no**. only 2 setting(s) produced an n* at both restart budgets; the solver cannot be ruled out, so the p-exponent is treated as unattributable
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
| Setting | Median weight error | seed min – max (spread) | seeds used |
|---|---|---|---|
| NC1 — n = 20000 | 0.0119 | 0.0069 – 0.0757 (11.0×) | 5 |
| NC1 — n = 320000 | 0.0030 | 0.0012 – 0.0419 (35.9×) | 5 |
| NC1 — n = 2560000 | 0.0004 | 0.0003 – 0.1810 (546.2×) | 5 |
| NC2 — σ = 1.00, n = 20000 | 0.0119 | 0.0069 – 0.0757 (11.0×) | 5 |
| NC2 — σ = 2.00, n = 20000 | 0.0658 | 0.0174 – 0.0970 (5.6×) | 5 |
| NC2 — σ = 3.00, n = 20000 | 0.1452 | 0.0310 – 0.4012 (12.9×) | 5 |

**Does each control survive seed variation?** Across the 25 endpoint seed pairs, NC1 goes the required way in 20 of them (0.800; 0.5 is chance) — reliable across seeds: **yes**. NC2 goes the required way in 23 of 25 (0.920) — reliable across seeds: **yes**. This is a rank statistic, not a ratio of medians against a max/min spread: the tensor power method fails to converge on an occasional seed, and one such run makes any max/min measure meaningless while leaving the median trend intact. An earlier revision published bare medians with no dispersion at all, and the revision after that used exactly the max/min measure this replaces.

**Is the shared configuration stable under a change of seed stream?** σ = 1 at n = 20000, measured twice from independent seed offsets: 0.01189 against 0.00808, a ratio of 1.47× against a limit of 3.0× — stable: **yes**. This gates the run. Two earlier revisions got this wrong in opposite ways: the first let NC1 and NC2 use mismatched offsets and reported medians 5.2× apart at this one shared point, and the second unified them onto a single deterministic call and then published the resulting identity as a gate — which tested only that the interpreter is deterministic. A blind reviewer named the tautology; this version draws a genuinely independent stream, so it can fail.

NC1 (over-sampling reduces error): **yes** · NC2 (frozen n, larger σ raises error): **yes** · NC2 monotone across the whole σ grid: **yes** · overall **yes**.

the error rises at every step of the sigma grid, not only between endpoints
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
Runtime **511.6 s** for this stage on Hugging Face `unset` (8 vCPU / 32 GB), threads pinned to the cgroup quota; 615.2 s for the whole run.
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
