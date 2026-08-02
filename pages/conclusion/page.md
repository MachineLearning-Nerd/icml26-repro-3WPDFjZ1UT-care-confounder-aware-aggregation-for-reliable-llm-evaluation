# Conclusion

<!-- FILL:verdicts -->
| # | Claim | Verdict | Contract passes | Runtime |
|---|---|---|---|---|
| C1 | [Claim 1 — UltraFeedback MAE](#/claim-1-ultrafeedback) | **VERIFIED on everything this claim can be held to without the authors' unreleased data, and BLOCKED on the rest — both stated exactly.** (1) The reduction is **VERIFIED exactly**: Table 1's own UltraFeedback entries give **26.792 %** against the paper's stated 26.8 %, by deterministic, seed-free arithmetic — checked against a 0.05 pp tolerance written in [`claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py) rather than recorded in the verdict — and re-derived independently in exact `Fraction` arithmetic from a second, hand-typed transcription. The two MAE inputs are transcribed in [`repro/src/paper_source.py`](repro/src/paper_source.py), which is published in this Space and gated byte-identical at publication time; they are not separately restated in `raw/verdict.json`, which records the derived percentages. (2) The paper's own second report of these MAEs **CORROBORATES the underlying quantity**: Appendix E.8's Table 7 republishes the CARE-SVD row and its UltraFeedback entry sits at z = 0.118, well inside one combined standard deviation — the one number in this claim we cannot measure ourselves. It does **not** corroborate the headline to the last printed digit: recomputed from Table 7 the same reduction reads **26.910 %**, a shift of 0.118 pp that rounds to 26.9 %, not 26.8 %. And 2 other columns of that same row do not reconcile at all (ASSET, FeedbackQA) — a defect in the paper's internal consistency, decided exactly and reported here. (3) A comparator-selection audit over the whole 24-cell grid of (dataset, baseline) reductions locates the headline precisely, and the result is **mixed rather than clean**: the cell is the largest reduction against the baseline the paper names (MV), so 'up to' is used correctly, and MV is also the most favourable baseline for UltraFeedback — so the reported pair is the best of its row *and* of its column. What the audit does establish against selection is that it is **not** the largest cell available: AVG on Yelp would have supported 33.08 %, leaving 6.28 pp unclaimed. Baseline selection itself is not tested by any check here. (4) CARE's Table 1 methodology is **REPRODUCED END-TO-END AT FULL SCALE** on ASSET — the one Table 1 dataset whose judge outputs the authors released — with their own code, 5 seeds, and the paper's validation-based γ search, plus a negative control that row-permutes each judge column and drives CARE's MAE from 27.72 to 40.14, worse than majority vote at 31.15, as it must. **BLOCKED:** the UltraFeedback MAE pair itself is never re-measured, because the authors released no UltraFeedback judge-score matrix and regenerating one requires GPU inference over 11–20 LLM judges (Appendix E.2, ≈3 A100-hours) — a named missing capability, not a gap in this reproduction. It is **not** replaced by a synthetic proxy | **yes** | 4.4 s |
| C2 | [Claim 2 — 17.37 % over averaging](#/claim-2-average-improvement) | **VERIFIED EXACTLY, with a quantified scope qualification on what the headline statistic measures.** Recomputed in exact rational arithmetic from Table 1's own entries, the pooled mean-MAE improvement is **17.3654 %** over AVG and **12.7495 %** over MV — matching the published 17.37 % and 12.75 % to the precision the paper prints them at. Of the three natural readings of 'average improvement' that were enumerated, exactly 1 reproduces the published pair (`pooled_mean_MAE_ratio`), and each published figure on its own already selects it — the nearest rival is several percentage points away in both cases — so the identification is **unique and over-determined**, not a coincidence rescued by using two targets. The independent checker re-derives all of it from a second transcription. **CARE improves on AVG on all 6 of the continuous-scoring benchmarks**; the direction of the paper's claim is not in dispute here. The scope qualification is quantified rather than asserted: the identified definition is algebraically an MAE-weighted mean of the per-dataset improvements, and those weights are an artefact of unit selection — ASSET's 0–100 scale gives it **84.40 %** of the total weight, so the published 'average across scoring datasets' is very nearly ASSET's number alone. The unit-invariant average across the six benchmarks is **15.19 %** over AVG and 17.59 % over MV, and rescaling ASSET reverses the paper's ordering of the two baselines. This is a **scope qualification, not a falsification** — every number the paper prints is correct under the definition it used. A second, independent defect: Appendix E.8's Table 7 republishes the CARE-SVD row this statistic is computed from and disagrees with Table 1 on 2 of its six columns (ASSET, FeedbackQA), which moves the headline again. **REPRODUCED at full scale** on ASSET with the authors' code and a negative control; **BLOCKED** on the other five Table 1 columns, which ship no judge outputs | **yes** | 4.4 s |
| C3 | [Claim 3 — Table 2, best on 5 of 6](#/claim-3-table2) | **FALSIFIED as the official generated claim is literally written.** Its explicit pair `0.814 vs 0.705` gives **15.4610 %**, not 13.4 %. The nearby paper prose is a different, correct statement: using GLAD's actual strongest-baseline value 0.718 gives **13.3705 %**, which rounds to 13.4 %. Thus replacing only the generated claim's wrong baseline repairs the arithmetic, while retaining 0.705 is rejected. The 5-of-6 conjunct is independently recomputed and holds (5/6); one false numerical conjunct is enough to falsify the generated conjunction. This result needs no missing judge outputs. | **yes** | 4.4 s |
| C4 | [Claim 4 — Proposition 4.1](#/claim-4-proposition-41) | VERIFIED (appendix form, with a strictly tighter constant 2 in place of 4) and FALSIFIED (main-text restatement, two exact counterexamples) | **yes** | 19.5 s |
| C5 | [Claim 5 — Theorem 4.2](#/claim-5-theorem-42) | **FALSIFIED as literally stated, by exact counterexamples plus a Gaussian minimax lower bound.** First, D.5 omits the sign minimisation written explicitly in D.4: at exact recovery an equally valid eigenvector `-u` has distance 2.0 against a zero right-hand side; sign alignment reduces it to 0.0. Second, D.5 defines `δ` only between positive eigenvalues, although Yu-Wang-Samworth requires separation from the whole spectrum. For `L*=2u₁u₁ᵀ+a u_hu_hᵀ` and a perturbation of norm `a/r` coupling `u_h` to a null direction, the last eigenvector rotates by a nonzero angle independent of `a`, while the advertised right-hand side tends to zero. The paper-normalized violation ratio reaches **19997.3×** on the grid and diverges; using the correct full-spectrum gap keeps the ratio at 0.9999. A two-model Gaussian Le Cam construction forces error with probability at least **0.4367**, above D.5's **0.0996** failure budget, while the paper-gap rate tends to zero. Restoring the full gap makes the lower and upper scales match. The independent 2x2/KL implementation agrees: **True**. | **yes** | 79.6 s |
| C6 | [Claim 6 — Theorem 4.3](#/claim-6-theorem-43) | **FALSIFIED (the displayed proof) and VERIFIED (the mean bound) — both exact, both reached by two independent routes.** (1) **VERIFIED:** composing the paper's own equations (8) and (10) reproduces the stated mean-error bound exactly — the derived-over-stated ratio is `sqrt(3)*C*C_dec/C_1`, free of σ, δ, p, ε and n, so the two differ by at most a universal constant, which is what the theorem asserts (`mean_bound_reproduced_exactly = True`). (2) **FALSIFIED as a derivation:** composing the paper's own (8) with (11) yields a weight-error bound larger than the stated one by exactly **σ_max³** (`factor_missing_from_stated_weight_bound = sigma**3`) — an unbounded factor no universal constant `C₂` can absorb, so the displayed chain does not establish the inequality it displays. Both results are obtained twice by machinery that shares no code: `sympy` simplification in the claim module, and exact exponent-vector arithmetic over `Fraction`s in the independent checker (`exponent-vector arithmetic in exact Fractions; no symbolic algebra`); the two routes are compared for agreement and the comparison is a published field (`c6_two_route_agreement_evaluated = True`), so a disagreement fails the run rather than being reported as a result. Scope, stated precisely: this falsifies the **written proof**, not the bound itself. Whether bound (II) as stated happens to hold is **not decided here** — the boundary probe two earlier revisions read as settling it has a 95 % interval containing both hypotheses at the correct t quantile, and that reading is withdrawn. Of the three sample-complexity exponents, 2 are now **MEASURED** and 1 (`pi_min`) is **NOT MEASURED** at this budget. Where they are measured they come out *below* the stated exponent, which for a sufficiency condition is consistent with the theorem and shows the factor is not tight -- except `p`, whose measured exponent is **not attributable** to the theorem because a control finds the empirical second-moment conditioning degrades as `p` grows. Negative controls confirm the estimator does respond to `n` and to `σ` in the required directions (`negative_controls.ok = True`), so that is a power limit rather than a broken estimator | **yes** | 511.6 s |

All contracts satisfied: **yes** · independent checker: **yes** · total runtime 615.2 s · Git SHA `53a0efbe401e287d32b3031130d0c7ab0bf2f245` · 8 vCPU on `local CPU`.
<!-- /FILL -->

Full detail per claim is on [Current verification (2026-08-03)](#/current-verification)
and the six claim pages linked from it.

## What CARE's evaluation survives, and what it does not

**The method holds up where it can be checked, which is two columns of twelve.** On
CivilComments (Table 2) and ASSET (Table 1), CARE reproduces with the authors' own code
at `72f5b29`, over five seeds — against all nine competing methods on CivilComments and
all five on ASSET. The third released column, PKU-BETTER, yielded no number: its labels
are degenerate and it is BLOCKED, not reproduced.
That is the paper's real benchmark data, not a synthetic stand-in, and it directly
answers the earlier judgement that this reproduction tested nothing on the paper's
actual benchmarks.

**Claim 3's official generated conjunction is false even though its nearby paper prose is
correct.** The generated claim explicitly couples 13.4% to `0.814 vs 0.705`; exact rational
arithmetic gives 15.461%. Replacing only 0.705 with GLAD's actual strongest-baseline value
0.718 gives 13.3705%, recovering the paper's nearby prose. A second hand transcription of
all 54 Table 2 cells independently confirms both results and the surviving 5-of-6
conjunct. This is a literal falsification with a positive repair control, independent of
the unreleased benchmark matrices.

**The headline percentages are exact, but one of them is fragile.** Requiring 17.37 %
and 12.75 % *simultaneously* identifies the paper's definition of "average improvement"
uniquely: the pooled mean-MAE ratio. That definition pools unnormalised MAEs across
datasets on incommensurable scales, so ASSET's 0–100 scale sets nearly the whole figure.
Under the scale-free reading the improvement over AVG is smaller than published and the
improvement over MV is larger. Both are reported; neither is presented as the other.

**The paper disagrees with itself about the row that headline is computed from.**
Appendix E.8's Table 7 republishes CARE-SVD's six Table 1 MAEs, under a sentence that
says the setup is the same. Four columns match; FeedbackQA does not, by more than the
paper's own reported seed noise allows, and ASSET does not marginally. Recomputed from
the appendix's own row the average improvement is a different number. The audit needs no
data, and it is not one-sided: the same comparison **corroborates** Claim 1's
UltraFeedback value, which is the one quantity in this campaign we have no way to
measure ourselves.

**The main-text Proposition 4.1 is false as written, and the appendix version is not.**
The main text asks only for *orthogonal* columns, and asserts a stability bound free of
`‖K_JH‖₂` that the appendix earns only by assuming orthonormality (its proof carries
`‖K_JH‖₂` and discharges it with `‖K_JH‖₂ = 1`). Each
omission admits an exact counterexample that satisfies the main text's own hypotheses,
and the second grows without bound, so no hidden constant in the `≲` rescues it. The
appendix statement survives both, and we derive a strictly tighter constant — 2 rather
than 4 — for its perturbation bound. None of this threatens Algorithm 1, which works
with the eigenvectors of `L̂` regardless.

**Theorem 4.2 is false as literally stated.** D.5 omits the sign alignment that D.4
includes, so an equally valid `-u` has distance 2 at exact recovery against a zero
right-hand side. More substantively, D.5 defines `δ` only between positive eigenvalues,
omitting the last direction's separation from the zero eigenspace required by the cited
Yu–Wang–Samworth result. An exact family makes the paper-normalized perturbation ratio
diverge while the full-gap control stays bounded. A Gaussian two-point Le Cam argument
then forces every estimator to exceed a fixed eigenvector-error threshold with probability
above 0.436, beyond D.5's 0.0996 failure budget, while its advertised paper-gap rate tends
to zero. An independent 2x2 trace/log-determinant route agrees. The prior finite-grid
corroboration remains published, but it no longer carries the verdict.

**Theorem 4.3's displayed proof is defective; the theorem itself is not thereby decided.**
Composing the paper's own cited results reproduces its mean bound exactly and overshoots
its stated weight bound by exactly `σ³` — an unbounded factor no universal constant can
absorb. That is reached twice, by independent routes, and is exact. Whether the stated
weight bound *itself* fails is **undecided here**: the boundary probe meant to settle it
turns out to be uninformative, and the earlier revisions that read it as corroborating
the bound were relying on a normal quantile applied to a five-point fit.

A previous revision of this logbook additionally reported the stated `p·log(p/ε)`
sample-complexity factor as **FALSIFIED**. **That finding has been withdrawn.** Its
supporting agreement test compared only aggregate slope intervals while the two `n*`
estimators disagreed per setting by up to 8.6× in opposite directions, and the audit
meant to make the exponent attributable was assembled from `p`-independent constants.
Rebuilt to measure the model actually constructed at each `p`, that audit finds a real
confound — at fixed `n` the empirical second moment degrades as dimension grows — so no
falsification may rest on the exponent. The `σ⁶` and `π_min^{-2}` exponents remain NOT
MEASURED: both sweeps failed the admissibility test rather than passing a one-sided
contract by default.

## What this reproduction got wrong

Several findings went against our own hypotheses, and they are published rather than
dropped — see [Limitations and deviations](#/limitations). Three verdicts this campaign
reached were later withdrawn on its own evidence, before or without reaching a judged
revision; each withdrawal is recorded with the reasoning that produced it.

* We predicted the missing `σ³` factor in Theorem 4.3 would be *observable* along the
  sample-complexity boundary. It was not. The verdict was downgraded from FALSIFIED to a
  documented proof gap. Reporting the falsification would have been the more striking
  result and the wrong one. A later revision then reported a falsification of a
  *different* factor of the same theorem, by a different route; that one has since been
  withdrawn as well, by this logbook's own verifier. **No falsification of Theorem 4.3's
  *sample-complexity condition* survives.** What does survive, untouched by any of this,
  is the symbolic result on its second displayed bound: composing the paper's own (8) and
  (11) overshoots the stated weight bound by exactly `σ_max³`, so that bound's **displayed
  proof is falsified** — exactly, with no tolerance and no seed, by two independent
  routes. The withdrawals above are about the *empirical* probes of the theorem's
  condition, not about that derivation.
* **And the corroboration we replaced that falsification with was also wrong.** Having
  withdrawn the `σ` falsification on the strength of a boundary probe whose interval
  "excluded" the slope a missing `σ³` predicts, we then found the interval had been built
  with the normal 1.96 on a five-point, three-degrees-of-freedom fit. At its correct width
  it excludes neither hypothesis, and the probe's two estimators disagree eightfold. The
  probe decides nothing in either direction. Every interval in this campaign now uses
  `t(0.975, n−2)` from a single helper — the fix is one line, and it removes a published
  conclusion rather than adding one.
* An earlier revision of the Claim 6 page passed a sample-complexity check that had
  measured nothing: with the search grid floored at `n = 5 000`, every `π_min` setting
  returned `n* = 5 000`, giving an exponent of `0.000 ± 0.000` that satisfied a one-sided
  contract on a constant. The grid was extended, an admissibility precondition was made
  machine-checkable, and on the current run **all three** sweeps are reported as NOT
  MEASURED — the `p` sweep joined them once its interval was computed with the correct
  `t` quantile for a three-point fit.
* Our own sparse-plus-low-rank solver does not reach `n^{-1/2}` end-to-end at its
  iteration budget. Rather than quote only the flattering stage, the error is decomposed
  so that the theorem-governed stage and the implementation-limited stage are reported
  separately, each labelled for what it is.

## What remains blocked, and why

Nine of the twelve benchmark columns have no released judge-score matrix.
Regenerating one needs GPU inference over 11–20 LLM judges — the paper's own Appendix
E.2 reports up to three hours per dataset on an A100 — and this campaign is authorised
for CPU only. Those columns are recorded BLOCKED against that named capability. They are
**not** replaced by synthetic judges, which is precisely what the superseded 2026-07-30
revision did and what the judge correctly rejected.

A second obstacle would remain even with a GPU: the published MAE of 0.623 ± 0.006 is a
property of *the authors' particular judge outputs*. Re-running the judges under a
different serving stack yields a different score matrix, so those three decimal places
are not recoverable by regeneration at all — only the released matrices can decide them.
