# Claim 5 — Theorem 4.2 (finite-sample rate for the spectral path)

<!-- FILL:c5.header -->
**Verdict:** **FALSIFIED as literally stated, by exact counterexamples plus a Gaussian minimax lower bound.** First, D.5 omits the sign minimisation written explicitly in D.4: at exact recovery an equally valid eigenvector `-u` has distance 2.0 against a zero right-hand side; sign alignment reduces it to 0.0. Second, D.5 defines `δ` only between positive eigenvalues, although Yu-Wang-Samworth requires separation from the whole spectrum. For `L*=2u₁u₁ᵀ+a u_hu_hᵀ` and a perturbation of norm `a/r` coupling `u_h` to a null direction, the last eigenvector rotates by a nonzero angle independent of `a`, while the advertised right-hand side tends to zero. The paper-normalized violation ratio reaches **19997.3×** on the grid and diverges; using the correct full-spectrum gap keeps the ratio at 0.9999. A two-model Gaussian Le Cam construction forces error with probability at least **0.4367**, above D.5's **0.0996** failure budget, while the paper-gap rate tends to zero. Restoring the full gap makes the lower and upper scales match. The independent 2x2/KL implementation agrees: **True**.

**Confidence: HIGH.** The literal theorem has two exact formulation defects: it omits sign alignment even at zero noise and omits the last positive eigenvalue's gap to the zero eigenspace. The second defect is exercised by a symbolic family whose paper-normalized violation diverges while the corrected full-gap ratio remains bounded. A two-model Gaussian Le Cam bound then shows this is not merely a gap in the displayed proof: every estimator fails at probability above the theorem's budget on one model while the advertised paper-gap rate tends to zero. An independent 2x2 eigendecomposition and direct trace/log-determinant KL route agrees.

Machine-checkable contract satisfied by the release run: **yes**.
<!-- /FILL -->

## The exact claim

> Theorem 4.2 gives a finite-sample convergence rate of O(√(η/n)·1/(ξ(T)·δ)) for the
> spectral estimation path used to separate quality from confounders (Section 4).

The paper's verbatim statement, its assumptions (incoherence, curvature constant
`ξ(T)`, eigengap `δ`, regularisation `λ_n ≍ 1/√n`) and the two results it composes are
transcribed on [Source audit](#/source-audit).

## Decisive literal result

<!-- FILL:c5.counterexamples -->
| a | ‖E‖₂=a/r | aligned error | error ÷ (‖E‖/δpaper) | error ÷ (‖E‖/δfull) |
|---|---|---|---|---|
| 0.1000 | 0.00078125 | 0.00781184 | 18.998 | 0.999916 |
| 0.0100 | 0.00007812 | 0.00781184 | 198.983 | 0.999916 |
| 0.0010 | 0.00000781 | 0.00781184 | 1998.832 | 0.999916 |
| 0.0001 | 0.00000078 | 0.00781184 | 19997.322 | 0.999916 |

Sign counterexample: raw distance 2.0, right-hand side 0.0; sign-aligned control 0.0.

Paper-gap ratio diverges: **yes**. Corrected full-gap ratio stays bounded: **yes**. Gaussian two-point lower bound falsifies the statistical rate itself: **yes**; its minimum Le Cam error probability is 0.4367 against the theorem's 0.0996 failure budget. Independent 2×2/KL route passes: **yes**.
<!-- /FILL -->

### 1. The statement omits sign alignment

At exact recovery, `L_hat=L*`, both `u` and `-u` are valid eigenvectors. Choosing
`u_hat=-u` gives `||u_hat-u||₂=2` while the right-hand side is zero. Appendix Theorem D.4
explicitly uses a sign `s_i∈{±1}`; D.5 omits it. The sign-aligned control returns zero.

### 2. Its gap omits the zero eigenspace

Let `u₁,u_h,v` be orthonormal, with `v` in the nullspace, and set

```text
L* = 2 u₁u₁ᵀ + a u_hu_hᵀ
E  = (a/r)(u_hvᵀ + vu_hᵀ),       a>0, fixed r>0.
```

The affected 2x2 block is `[[a,a/r],[a/r,0]]`, so `tan(2θ)=2/r`. The aligned error
`sqrt(2-2cos θ)` is positive and independent of `a`. D.5 defines
`δ_paper=2-a`, hence

```text
error / (||E||₂/δ_paper) = error * r(2-a)/a  -> +infinity.
```

Yu-Wang-Samworth's required full-spectrum gap is `δ_full=min(a,2-a)=a`, for which the
normalized ratio is `r*error`, bounded and approximately one. This is also the gap
definition CARE itself uses correctly in D.4.

The cited minimum-signal condition does not restore the claim. Couple `n=(r/a)^2`; then
`||E||₂=1/sqrt(n)` and `a/sqrt(p/n)=r/sqrt(p)`. Selecting one fixed sufficiently large
`r` satisfies any finite signal constant, after which the paper-normalized violation
still diverges as `a->0`. The dense orthonormal basis and the tangent space remain fixed
throughout the family, so incoherence and curvature cannot absorb the missing `1/a`.

### 3. Gaussian two-point lower bound

The deterministic family shows D.5 cannot follow from its stated spectral-error premise.
To rule out a different proof of the same statistical rate, the audit constructs two
CARE-compatible Gaussian models with sparse component `S=4I` and

```text
L0 = 2u₁u₁ᵀ + a u_hu_hᵀ
L1 = 2u₁u₁ᵀ + a vθvθᵀ,       vθ = cos(θ)u_h + sin(θ)v.
```

Each `Lj` is positive semidefinite and has the required
`K_JH K_HH^{-1} K_HJ` factorization; the observed precision `Pj=S-Lj` retains a
positive-definite margin of 2. For `n=(c/a)^2` and `θ=1/c`, the exact n-sample Gaussian
divergence is

```text
KL(P0^n || P1^n) = n a^2 sin^2(θ) / (2*4*(4-a)),
```

which stays below 0.033 as `a->0`. Le Cam's inequality therefore forces every estimator,
on at least one model, to make eigenvector error at least half the fixed separation with
probability above 0.436. At `η=3`, D.5 permits failure probability only
`2e^-3=0.0996`, while its advertised rate with `δ_paper=2-a` tends to zero. With the
corrected `δ_full=a`, the upper-rate scale is nonvanishing and matches the lower-bound
order. The independent checker recomputes both the 2x2 eigensystem and KL through the
direct trace/log-determinant Gaussian formula.

This decides the literal theorem. The older finite-grid measurements below remain
published as useful corroboration and limitation analysis, but none is needed to turn an
asymptotic slope fit into a falsification.

## Preserved finite-grid audit (not the deciding evidence)

**One exact symbolic check is VERIFIED. The headline rate exponent is NOT confirmed — it
lands on the shallow side of the stated −1/2, and this page does not read that as
support.**

| What was checked | Verdict |
|---|---|
| Inverting the stated bound reproduces the paper's own stated sample complexity | **VERIFIED exactly** — `sympy` *solves* `stated = α` for `n` and returns `8C₁²η/(α²δ²ξ²)`, matching the expression the paper states separately in Appendix D.6 |
| The cited Davis–Kahan constant `2√2 = 2^{3/2}` | **HOLDS over the search** — no violation found, worst error/bound 0.357; the search is random, not adversarial |
| That the composed expression equals the stated one | **NOT EVIDENCE** — this flag cannot fail as written; see below |
| The stated rate over the measured range | **HOLDS with a certificate** — `err(n)·√n` is bounded across the whole grid |
| The `n`-exponent on the spectral step | **NOT CONFIRMED as exactly −1/2** — −0.4724, CI [−0.4950, −0.4499], shallower; the bound still holds, its constant drifts |
| The `η` tail exponent | **HOLDS, conservatively** — 0.206 against a stated 1/2 |

**The bound HOLDS across the measured range, with an explicit constant.** An `O(·)`
upper bound has a free constant, so no finite grid can falsify it and none is claimed to.
The informative question is the dual one: *what constant does the bound actually require
here, and is it bounded?* With `η`, `ξ` and `δ` fixed across this sweep, that implied
constant is `C(n) = err(n)·√n`, and the verifier now computes it at every grid point. It
is **bounded over the whole grid** — the stated `O(√(η/n))` rate is therefore **satisfied
across 2.7 decades of `n` with a concrete certificate**, which is a decided positive result
rather than an absence of one.

<!-- FILL:c5.certificate -->
| `n` | stage-2 error | implied `C(n) = err·√n` |
|---|---|---|
| 800 | 0.6343 | 17.94 |
| 1600 | 0.5358 | 21.43 |
| 3200 | 0.3952 | 22.35 |
| 6400 | 0.2824 | 22.59 |
| 12800 | 0.1818 | 20.57 |
| 25600 | 0.1406 | 22.49 |
| 51200 | 0.0945 | 21.37 |
| 102400 | 0.0691 | 22.10 |
| 204800 | 0.0521 | 23.58 |
| 409600 | 0.0375 | 24.01 |

**max `C(n)` over the grid: 24.01** -- bounded, so the stated rate holds across the measured range. `C(n)` drifts upward by a factor of 1.338 from the smallest `n` to the largest. err(n)*sqrt(n) is bounded over the whole grid, so the stated O(sqrt(eta/n)) rate HOLDS across the measured range with that constant. It drifts upward by the factor reported, consistent with the fitted exponent being slightly shallower than -1/2, so the certificate is NOT extrapolated beyond the grid.
<!-- /FILL -->

The certificate comes with its own limit, stated rather than glossed: `C(n)` **drifts
upward** over the range, which is the same fact as the fitted exponent being slightly
shallower than −1/2. The certificate is therefore **not extrapolated beyond the grid**, and
this page makes no claim about the asymptotic regime.

**The `n`-exponent points the other way, and saying so costs this page its cleanest
sentence.** An error decaying as `n^{-0.4724}` decays *more slowly* than `n^{-1/2}`. For an
`O(√(η/n))` upper bound that is the direction which eventually breaks the bound, not the
one that satisfies it, and the entire 95 % interval lies on that side —
`stage_2_exponent_statistically_consistent_with_minus_half` is **false**. Over this finite
grid it is **not** a violation, because a constant absorbs a factor of `n^{0.028}`; but it
is not confirmation either, and it must not be presented as agreement.

**The contract row that marks this "yes" passes against a threshold of `slope <= -0.42`** —
16 % of slack below the theoretical −0.5. The verifier's own source comment says the test
"passes for −0.472 and equally for −0.9, so it never tested that the rate IS `n^{-1/2}`".
That threshold is stated here because an earlier revision of this page printed only
"Predicted −0.5 / Contract **yes**" for this row while printing explicit thresholds for the
`n*(α)` and `n*(δ)` rows, which reads as a stronger result than it is.

**Why the inversion is a real check and the composition is not.** Only the inversion has
teeth. The composed expression is *built* by multiplying the cited Chandrasekaran step by
the Davis–Kahan factor, and the "stated" expression is that same product written another
way — so `sympy` is asked whether two spellings of one product agree, and it always will.
The inversion instead **solves** the stated bound for `n` and compares the result against
an expression transcribed separately from the paper's Appendix D.6, so a wrong constant or
wrong power in the paper's own inversion would surface as a mismatch.

*An earlier revision of this section claimed the proof of that non-vacuity was on the
Claim 6 page — that "the same check applied to Theorem 4.3 fails by exactly σ³". **That
citation was false** and is withdrawn: the Theorem 4.3 module performs no sample-complexity
inversion at all (`sp.solve` does not appear in it). What fails there is the
composition-family check — derived-from-cited-steps versus stated-in-the-theorem — which is
structurally the family this page calls unable to fail. The accurate lesson is the opposite
of the one claimed: that family has teeth **when the derivation is composed independently
of the stated result**, as it is on Claim 6 and is not here. The defect is in this
instance's implementation, not in the family.*

**The Davis–Kahan constant, and exactly how independent the second route is.** The
constant holds across the claim module's search (no violation, worst error/bound 0.357),
and the independent checker re-runs the search on its **own** random draws under its own
seed over 500 trials, finding it holds there too (worst error/bound 0.303). That second
run is a genuine independent confirmation of the constant.

The flag named `two_routes_agree_on_eigvec_distance` is **not** what makes it independent,
and should not be read that way: inside one function it compares `‖û − u‖` against
`2·sin(arccos|û·u|/2)`, which are two formulas for the same quantity on the same pair of
vectors — a trigonometric identity that can only fail to floating-point tolerance. It is a
numerical sanity check, not a second opinion.

Neither search is adversarial; both sample perturbations at random. So the constant is
corroborated over the region reached, not proved.

**The `δ` sweep is now MEASURED, and getting there found a defect in our own design
rather than a shortage of compute.** Three earlier revisions reported `n*(δ)` as NOT
MEASURED on a fit of `0.6023 ± 0.5641` — a 95 % interval of [−1.82, 3.03] that decided
nothing. The cause was not noise. The sweep set the spectrum to
`[4.0, 2.0, 0.5] if d >= 2.0 else [2.0+d, 2.0, 2.0-d]`, under a source comment claiming
the overall scale was held fixed. It was not: `d = 2.0` was special-cased onto a different
spectrum family, and for `d < 2` the smallest eigenvalue `2−d` moved with `d` as well, so
changing the eigengap also changed the conditioning of `L*`. The measured `n*(δ)` came out
**non-monotonic** — 25694, 5649, 3060, 7839 for `δ` = 2, 1, 0.5, 0.25 — which is the wrong
sign at the top of the range and was the real signal that the design, not the estimator,
was at fault.

Rebuilt so that **both ends of the spectrum are pinned** (`λ₁ = 4.0`, `λ₃ = 1.0` at every
setting) and only the middle eigenvalue moves, over 7 settings instead of 4, the sweep
resolves cleanly:

| `δ` | 0.25 | 0.5 | 0.75 | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|---|---|---|
| `n*` | 5536 | 5518 | 5506 | 5500 | 5517 | 5660 | 6750 |

The fitted exponent is **0.0530 ± 0.0341**, a 95 % interval of **[−0.035, 0.141]** — a
width of 0.18 where the confounded design gave 4.85. `n*` is essentially **flat in `δ`
across a tenfold change**.

**What that does and does not mean.** The interval **excludes the predicted −2** decisively.
For a *sufficiency* bound that is **not a violation**: Theorem 4.2 says a sample size of
order `δ^{-2}` suffices, and needing *fewer* samples than a sufficient condition demands is
entirely consistent with it. What it does show is that the `δ^{-2}` factor is **not tight**
over `δ ∈ [0.25, 2.5]` in this generative model — the theorem's stated `δ`-dependence is not
visible in the sample size actually required. This is reported as a measured property of
the bound's tightness, not as a falsification, and the verifier records exactly that
distinction in `what_was_measured`.

*This also required changing our own informativeness gate, and that change is disclosed
rather than buried. The gate's predicate was "the 95 % interval excludes zero" — it could
not distinguish "too noisy to say anything" from "precisely measured, and the exponent is
zero", and the second is a real finding when the theorem predicts −2. A sweep now counts as
informative when its interval excludes zero **or** excludes the predicted exponent, and is
uninformative only when it covers both. That is not a threshold tuned to pass: Claim 6's
`σ` sweep has interval [−0.71, 12.81], covers both 0 and its predicted 6, and remains NOT
INFORMATIVE under the same rule.*

**NOT MEASURED:** `ξ(T)`, which has no closed form we can evaluate.
**DECIDED False, not unmeasured:** the end-to-end pipeline exponent
(`stage_3_full_pipeline_check: false`), which falls short of `n^{-1/2}` at our solver's
iteration budget. This page attributes that shortfall to the solver, and that attribution
is an argument from the stage decomposition below — not a separate executable test, and it
is not counted as one.

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
| Contract | Result |
|---|---|
| `composition_reproduces_stated_bound` | **yes** |
| `sample_complexity_inversion_matches_paper` | **yes** |

Route A overall: **yes**.
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
| Route | Trials | Worst attained error ÷ bound | Bound ever violated |
|---|---|---|---|
| Claim module — direct ‖û − u‖ | 4000 | **0.3573** | **no** |
| Independent checker — principal angle, `‖û − u‖ = 2 sin(θ/2)` | 500 | 0.3034 | **no** |

The two routes agree on the eigenvector distance to 1e-6 relative: **yes**, so the constant is not an artefact of either route's sign-alignment bookkeeping.
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
The `n*(α)` sweep is monotone over five settings and lands 36 standard errors from zero.
Read it as an **internal consistency check rather than independent corroboration**: given
the stage-2 power-law exponent of −0.472 already reported above, an `n*(α)` exponent near
−2.1 follows algebraically, so the two are not independent observations. See
[Limitations item 20](#/limitations). `n*(δ)` fails the test — 1.1 standard errors
from zero — and is therefore excluded entirely, supporting neither the `δ^{-2}` factor
nor any bound on it; see [Limitations item 14](#/limitations).

### Results

<!-- FILL:c5.results -->
| Sweep | Measured exponent | Predicted | Contract | Theil–Sen refit / status |
|---|---|---|---|---|
| Stage 1 — ‖Θ̂ − Θ‖₂ vs n | -0.5089 ± 0.0125 | −0.5 | **yes** | -0.5129 |
| **Stage 2 — eigenvector error, exact sparse part** (the theorem's object) | **-0.4724 ± 0.0098** | −0.5 | **yes** | -0.4765 |
| Stage 3 — full pipeline (our solver, *not* the theorem) | -0.3477 ± 0.0134 | −0.5 | **no** | — |
| n\*(α) — stage 2 | -1.958 ± 0.054 | -2.0 | slope >= -2.6 (grows no faster than alpha^-2) | MEASURED |
| n\*(δ) — stage 2 | 0.053 ± 0.034 | -2.0 | slope >= -2.4 (grows no faster than delta^-2) | MEASURED |

Contract outcome per element, exactly as `verdict.json` records it: `stage1_precision_exponent` = **True** · `stage2_oracle_spectral_exponent` = **True** · `stage3_full_pipeline_exponent` = **False** · `alpha_exponent` = **True** · `delta_exponent` = **True**. `NOT MEASURED` is published as itself rather than as a pass; the verifier's gate treats an unmeasured sweep as non-failing, which is a different statement from a satisfied contract.

Grid: `n ∈ [800, 1600, 3200, 6400, 12800, 25600, 51200, 102400, 204800, 409600]`. Saturated points are excluded from every fit, so each exponent is read from the regime where the bound is active. The stage-2 row is the one Theorem 4.2 governs; the stage-3 row describes our solver.
<!-- /FILL -->

## Route D — the `η` dependence, previously reported as NOT MEASURED

Earlier revisions listed `η` among the contract elements this campaign could not
measure, on the grounds that it is a tail parameter rather than something the sweep
varies. That was a failure of imagination, not a real obstacle: the theorem holds *with
probability at least* `1 − 2e^{−η}`, so reading the stage-2 error's own quantiles across
confidence levels measures `η` directly, at fixed `n`, with no constant fitted.

The level-`q` quantile is by definition the tightest bound that holds with probability
`q`. Setting `1 − 2e^{−η} = q` gives `η(q) = −log((1−q)/2)`, and the theorem predicts
`quantile(q) ∝ √(η(q))` — a log-log slope of `1/2`. Only quantiles the sample can
actually resolve are used: nothing beyond the `1 − 1/N` order statistic, so no
extrapolation is dressed up as measurement.

<!-- FILL:c5.eta -->
| confidence q | η(q) = −log((1−q)/2) | stage-2 error quantile |
|---|---|---|
| 0.500 | 1.3863 | 0.30873 |
| 0.600 | 1.6094 | 0.32113 |
| 0.700 | 1.8971 | 0.32919 |
| 0.800 | 2.3026 | 0.34307 |
| 0.900 | 2.9957 | 0.35908 |
| 0.950 | 3.6889 | 0.37574 |
| 0.975 | 4.3820 | 0.39605 |

Fitted tail exponent: **0.2059**, 95 % interval [0.1632, 0.2433], over 240 independent replicates at n = 12800.

Interval method: nonparametric bootstrap over the 240 independent replicates, 400 resamples; the quantiles are recomputed inside each resample. For comparison, treating the quantiles as independent observations and using the OLS residual standard error 0.0073 would report [0.1872, 0.2246] — the seven fitted points are order statistics of one sample and are strongly dependent, so residual-based standard errors understate the uncertainty; the bootstrap interval below is the one every verdict on this page uses

- Bound holds (tail grows no faster than √η): **yes**
- Measurement resolves a non-zero exponent: **yes**
- Stated √η is *tight* (0.5 inside the interval): **no**

The measured tail exponent is well below the stated 1/2, so Theorem 4.2's eta-dependence HOLDS and is CONSERVATIVE: the error's upper tail grows more slowly with the confidence parameter than sqrt(eta) requires. This is a statement about tightness, not a violation. It is scoped corroboration -- one model, one n, one estimator -- not a proof about all instances.
<!-- /FILL -->

**The interval above is a bootstrap, and an earlier revision's was not honest.** The seven
fitted points are quantiles of one sample of 240 replicates, so they are order statistics
and move together. An earlier revision computed the interval from the fit's OLS residuals
as though the seven were independent observations, which made it far too narrow; a blind
reviewer flagged it. It is now resampled: the 240 replicates — the things that really are
independent — are drawn with replacement 400 times and the whole quantile-to-slope
pipeline is re-run inside each resample. The old interval is printed beside the new one so
the difference is visible rather than asserted — both are rendered from the run, not typed
here. The point estimate is unchanged; only the uncertainty attached to it is, and every
conclusion below is read off the bootstrap interval.

The contract is one-sided, because Theorem 4.2 is an upper bound: the tail must grow no
*faster* than `√η`. That one-sided form is not vacuous here, because the same fit must
also resolve a **non-zero** exponent — a run in which the error had no `η`-dependence at
all would fail rather than pass by measuring nothing. Both conditions are reported
separately above.

The measured exponent is well below `1/2`. Read correctly, that means the theorem's
`η`-dependence **holds and is conservative**: the upper tail of the error grows more
slowly with the confidence parameter than `√η` requires. It is a statement about
tightness, not a violation — and it is scoped corroboration on one model at one `n`,
not a proof about every instance.

## Negative controls

Both run on the same model and the same grid `n ∈ {1 600, 12 800, 102 400}`, with medians
over five seeds, and both have an explicit numeric contract rather than a visual
judgement.

<!-- FILL:c5.controls -->
| Control | Behaves as required |
|---|---|
| `nc1_raw_precision_without_S_plus_L_stays_biased` | **yes** |
| `nc2_column_scrambled_data_never_recovers` | **yes** |

All controls: **yes**.
<!-- /FILL -->

NC1 is the load-bearing control. It isolates the single mechanism the theorem is about:
with a genuinely non-trivial sparse component `S`, omitting the split leaves the
recovered directions biased, so the error floors out instead of decaying. If NC1 had
*also* decayed at `n^{-1/2}`, the positive result would have been consistent with the
confounder correction doing nothing at all.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) does three things for this claim,
and it is worth being exact about which:

* `theorem_d5_counterexamples_independent` recomputes the sign and missing-zero-gap
  counterexamples from a direct 2×2 eigendecomposition, then obtains the Gaussian
  two-model divergence from the trace/log-determinant KL formula at 80-digit precision.
  It shares neither the claim module's closed-form angle nor its simplified KL formula.
* `davis_kahan_by_principal_angle` re-derives the eigenvector distance by a **different
  route** — via the principal angle, `‖û − u‖ = 2 sin(θ/2)` — rather than by the norm
  difference the claim module uses, and re-checks the `2^{3/2}` constant against it.
* `recheck_c5_stage_slopes` refits the stage-1 and stage-2 exponents with a **Theil–Sen**
  estimator instead of least squares, so a single outlying point cannot carry the fit.

The preserved Route A `sympy` reconstruction of the paper's composed bound still has no
second implementation; it is not the evidence that decides the literal theorem. The
decisive sign, eigengap, and minimax results do have the independent route above.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C5_thm42
```

<!-- FILL:c5.runtime -->
Runtime **79.6 s** for this stage on Hugging Face `unset` (8 vCPU / 32 GB), threads pinned to the cgroup quota; 615.2 s for the whole run.
<!-- /FILL -->
 Record: [`raw/verdict.json`](raw/verdict.json) under `claims.C5_thm42`;
extract [`raw/c5_rate.csv`](raw/c5_rate.csv). Code:
[`repro/src/claim_c5_thm42.py`](repro/src/claim_c5_thm42.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured, except for the elements that entry itself marks `POST-HOC` —
is entry `C5` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
