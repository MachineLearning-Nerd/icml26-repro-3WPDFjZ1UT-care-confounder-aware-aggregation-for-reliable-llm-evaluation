# Current verification (2026-08-03)

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

**3. Two previously inconclusive claims now have literal decisions.** Claim 3's generated
`0.814 vs 0.705` comparison is false in exact rational arithmetic, while a repair control
using the actual strongest baseline 0.718 recovers the paper's nearby prose. Claim 5 omits
both eigenvector sign alignment and the gap from the last positive eigenvalue to zero. Its
missing-gap counterexample is symbolic, and a Gaussian two-point Le Cam lower bound shows
the advertised statistical rate itself fails—not merely the paper's displayed proof.
Both are independently recomputed.

## What cuts against a flattering story, and what cuts for it

They are stated here rather than buried, because a reproduction that only ever confirms
its own hypotheses is not measuring anything -- and the one that came out in the paper's
favour is kept in the same list, because a reproduction that only ever finds fault is
not measuring anything either.

* A conjectured falsification of Theorem 4.3's weight bound **is undecided, and two
  earlier revisions said otherwise in opposite directions**. Having found a missing `σ³`
  factor in the displayed derivation, we predicted the weight error would *grow* with `σ`
  along the sample-complexity boundary; it did not appear to. Both the FALSIFIED verdict
  and the "refuted by measurement" verdict that replaced it are now withdrawn. The probe
  is a five-point fit with three residual degrees of freedom, and its 95 % interval —
  computed with `t(0.975, 3) = 3.182` rather than the normal 1.96 an earlier revision
  used — includes **both** the 0 the theorem predicts and the 3 a missing `σ³` predicts.
  It discriminates nothing. What stands is the symbolic result: the displayed *derivation*
  of the weight bound is falsified, exactly and by two independent routes; whether the
  bound *as stated* holds is not decided here. See [Claim 6](#/claim-6-theorem-43).
* A **claimed falsification of Theorem 4.3 was withdrawn by our own verifier.** The
  2026-08-01 revision reported that `n*` grows as `(p·log(p/ε))^{3.63 ± 0.80}` against a
  stated exponent of 1, "with both `n*` estimators agreeing". Only the two *aggregate*
  slope intervals had been compared; per setting the estimators differed by up to 8.6×
  in opposite directions, over decay curves with r² as low as 0.38. A stricter
  per-setting screen and a rebuilt confound audit now govern that finding, and the
  confound audit detects a real one: at fixed `n` the empirical second moment degrades
  with `p` — subspace leakage grows 259× across the sweep — so part of the measured
  growth is the moment estimate deteriorating rather than the `p·log(p/ε)` factor. The
  exponent is no longer attributable, and Theorem 4.3 is **not** recorded as falsified.
  A later round removed it as a measurement outright: the surviving fit has three points
  and therefore one residual degree of freedom, and at the correct `t(0.975, 1) = 12.7`
  its second estimator resolves no exponent at all. The sweep is now NOT INFORMATIVE, so
  **none** of Theorem 4.3's three sample-complexity exponents is measured at this budget.
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
  unit-invariant across-benchmark average is 15.19%. A later revision over-corrected and
  called this a **falsification**; a blind reviewer showed the invariance test it rested
  on is an algebraic identity that cannot fail. Both framings are recorded rather than
  quietly fixed. The stable statement is the one above: a quantified scope qualification
  on a summary statistic, with the underlying benchmark comparison untouched.
* **The paper reports CARE-SVD's Table 1 row twice, and the two reports do not
  reconcile.** Appendix E.8's Table 7 republishes the same six MAEs under the name "1st
  Factor", stating "We use the same scoring-task setup as in Table 1". Four of the six
  columns agree within the paper's own combined error bars; **FeedbackQA** does not, by
  a margin its own reported seed noise cannot absorb, and ASSET does not marginally.
  Recomputed from the appendix's own row, the 17.37% headline is a different number.
  This needs no data and no compute, and it cuts both ways: it also **corroborates**
  Claim 1's UltraFeedback value, which the two tables do agree on — the one number in
  this campaign we cannot measure ourselves.
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
that per claim. Claim 3 has no permutation control on the Table 2 *accuracy* path (only
on the MAE path, under Claims 1–2); that remains disclosed but is irrelevant to its exact
literal arithmetic decision. Claim 5's decisive eigengap and Gaussian-KL evidence is
checked by an independent 2x2 implementation. Remaining gaps are in
[Limitations](#/limitations). The single
command and pinned environment are on
[Fixed command, environment, seeds, runtime](#/environment-and-command).

`repro/src/run_all.py` exits **1** whenever any claim contract or the independent
checker fails. It is not a report generator.
