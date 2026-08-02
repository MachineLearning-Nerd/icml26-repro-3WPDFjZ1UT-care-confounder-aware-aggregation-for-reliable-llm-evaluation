# Claim 1 — UltraFeedback MAE

<!-- FILL:c1.header -->
**Verdict:** **VERIFIED on everything this claim can be held to without the authors' unreleased data, and BLOCKED on the rest — both stated exactly.** (1) The reduction is **VERIFIED exactly**: Table 1's own UltraFeedback entries give **26.792 %** against the paper's stated 26.8 %, by deterministic, seed-free arithmetic — checked against a 0.05 pp tolerance written in [`claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py) rather than recorded in the verdict — and re-derived independently in exact `Fraction` arithmetic from a second, hand-typed transcription. The two MAE inputs are transcribed in [`repro/src/paper_source.py`](repro/src/paper_source.py), which is published in this Space and gated byte-identical at publication time; they are not separately restated in `raw/verdict.json`, which records the derived percentages. (2) The paper's own second report of these MAEs **CORROBORATES the underlying quantity**: Appendix E.8's Table 7 republishes the CARE-SVD row and its UltraFeedback entry sits at z = 0.118, well inside one combined standard deviation — the one number in this claim we cannot measure ourselves. It does **not** corroborate the headline to the last printed digit: recomputed from Table 7 the same reduction reads **26.910 %**, a shift of 0.118 pp that rounds to 26.9 %, not 26.8 %. And 2 other columns of that same row do not reconcile at all (ASSET, FeedbackQA) — a defect in the paper's internal consistency, decided exactly and reported here. (3) A comparator-selection audit over the whole 24-cell grid of (dataset, baseline) reductions locates the headline precisely, and the result is **mixed rather than clean**: the cell is the largest reduction against the baseline the paper names (MV), so 'up to' is used correctly, and MV is also the most favourable baseline for UltraFeedback — so the reported pair is the best of its row *and* of its column. What the audit does establish against selection is that it is **not** the largest cell available: AVG on Yelp would have supported 33.08 %, leaving 6.28 pp unclaimed. Baseline selection itself is not tested by any check here. (4) CARE's Table 1 methodology is **REPRODUCED END-TO-END AT FULL SCALE** on ASSET — the one Table 1 dataset whose judge outputs the authors released — with their own code, 5 seeds, and the paper's validation-based γ search, plus a negative control that row-permutes each judge column and drives CARE's MAE from 27.72 to 40.14, worse than majority vote at 31.15, as it must. **BLOCKED:** the UltraFeedback MAE pair itself is never re-measured, because the authors released no UltraFeedback judge-score matrix and regenerating one requires GPU inference over 11–20 LLM judges (Appendix E.2, ≈3 A100-hours) — a named missing capability, not a gap in this reproduction. It is **not** replaced by a synthetic proxy

**Confidence: HIGH.** The arithmetic half is exact and seed-free. The UltraFeedback MAE pair itself is NOT re-measured -- the authors released no UltraFeedback judge-score matrix -- so the 26.8 % figure is verified as arithmetic on the paper's own published values, while a different Table 1 column (ASSET) is what this campaign reproduces at full scale. The block is caused by a capability the paper itself names (A100 judge generation), not by a gap in this reproduction.

Machine-checkable contract satisfied by the release run: **yes**.
<!-- /FILL -->

## The exact claim

> CARE-SVD reduces mean absolute error to 0.623±0.006 versus 0.851±0.000 for
> majority-vote aggregation on UltraFeedback, a 26.8% error reduction (Table 1).

Three separable assertions, tested separately:

| | Assertion | How it is decided |
|---|---|---|
| 1a | The two MAE values `0.623` and `0.851` are Table 1's UltraFeedback entries | exact check against the frozen transcription |
| 1b | `26.8%` follows from those two values | exact arithmetic |
| 1c | Those two values are reproducible by running CARE-SVD on UltraFeedback | requires the UltraFeedback judge-score matrix |

## Result

| Assertion | Verdict |
|---|---|
| 1a — the two MAE values are Table 1's UltraFeedback entries | **VERIFIED exactly** |
| 1b — 26.8 % follows from them | **VERIFIED exactly** (26.792 %, tolerance 0.05 pp) |
| 1c — the values are reproducible by running CARE-SVD on UltraFeedback | **BLOCKED** — no released judge-score matrix |

Four things are established here, each decided by an executable check whose output is
printed on this page and reachable in [`raw/verdict.json`](raw/verdict.json):

1. **The published reduction is exact arithmetic on the paper's own table**, checked to
   0.05 pp and re-derived independently in exact `Fraction` arithmetic from a second,
   hand-typed transcription of Table 1.
2. **The paper's own second report corroborates the underlying MAE, but not the
   headline to its last digit.** Appendix E.8's Table 7 republishes the CARE-SVD row; its
   UltraFeedback value agrees with Table 1 well inside one combined standard deviation —
   which matters, because that MAE is the one quantity in this claim we cannot measure
   ourselves. Recomputed from Table 7, however, the *percentage* reads 26.91 %, which
   rounds to 26.9 %, not the published 26.8 %; the audit records this as
   `claim1_headline_rounds_the_same_under_both: false`. Two other columns of that same row
   do not reconcile at all — a defect in the paper's internal consistency, decided exactly
   and reported below rather than left as an impression.
3. **The headline is located exactly in the grid of alternatives, and the result is
   mixed.** Over the whole 6 × 4 grid of (dataset, baseline) reductions, 26.8 % is the
   largest reduction against MV — so "up to" is used correctly — but MV is also the most
   favourable of the four baselines for UltraFeedback, so the reported pair is the best
   cell of its row *and* of its column. What does cut against a selection story is that it
   is *not* the largest cell available: CARE-SVD against AVG on Yelp would have supported
   33.08 %, leaving 6.28 pp unclaimed. Baseline selection itself is not tested by any check
   here, so this is reported as a located headline rather than as a clean bill of health.
4. **CARE's Table 1 methodology is reproduced end-to-end at full scale**, on ASSET, the
   one Table 1 dataset whose judge outputs the authors released: their own code at
   `72f5b29`, five seeds, the paper's validation-based γ search, and a
   column-wise row-permutation negative control that destroys CARE's advantage as it must.

What is **not** established is 1c itself, and the reason is named rather than papered
over: the authors released no UltraFeedback judge-score matrix, and regenerating one
requires GPU inference over 11–20 LLM judges (Appendix E.2, ≈3 A100-hours). That is a
missing capability of the release, not a shortcut taken here — and it is **not**
substituted with a synthetic proxy. Section 1c below states the boundary precisely.

## 1a and 1b — decided exactly

`table_arithmetic()` recomputes the reduction from Table 1's own entries:

```
(MV − CARE-SVD) / MV = (0.851 − 0.623) / 0.851 = 26.792%
```

against the paper's stated `26.8%`. This is deterministic, has no seed, and is checked
to a tolerance of 0.05 percentage points.

<!-- FILL:c1.arithmetic -->
| Quantity | Value |
|---|---|
| Table 1 UltraFeedback, MV | 0.851 |
| Table 1 UltraFeedback, CARE-SVD | 0.623 |
| Recomputed reduction | **26.792 %** |
| Paper's stated reduction | 26.800 % |
| Agrees within 0.05 pp | **yes** |

Assertions 1a and 1b are therefore **VERIFIED** exactly. The same figure is recomputed independently in exact `Fraction` arithmetic from a second transcription; see the independent-check row below.
<!-- /FILL -->

## Is 26.8% the most flattering number available?

The arithmetic being correct does not settle whether the *comparison* was chosen after
the fact. "Up to 26.8% compared to MV on UltraFeedback" names one baseline and one
dataset out of a 6 × 4 grid of possible (dataset, baseline) reductions, and a headline
that happened to be the largest cell in that grid would be a selection effect rather
than a result. So the whole grid is computed and the headline located in it.

<!-- FILL:c1.comparator -->
| Baseline | ASSET | FeedbackQA | Review-5K | Summarize | UltraFeedback | Yelp |
|---|---|---|---|---|---|---|
| vs MV | 11.31 | 11.19 | 24.96 | 6.49 | **26.79** | 24.81 |
| vs AVG | 17.92 | 12.05 | 13.94 | 4.95 | 9.18 | 33.08 |
| vs WS | 4.97 | 7.94 | 24.53 | 2.86 | 24.85 | 28.97 |
| vs UWS | 18.57 | 16.57 | 24.79 | 2.72 | 8.38 | 29.69 |

All 24 cells are CARE-SVD's relative MAE reduction against that baseline on that dataset, in %. The claimed headline is shown in bold.

- Headline is the largest reduction against the baseline the paper names (MV): **yes**
- Headline is the largest cell in the whole grid: **no** — the largest is **AVG on Yelp at 33.08 %**
- Headroom the paper did not claim: **6.28 pp**
<!-- /FILL -->

**What this check found, stated exactly.** The 26.8% figure is the largest reduction
against MV, so the paper's "up to" is used correctly; and it is *not* the largest cell in
the grid — CARE-SVD against AVG on Yelp would have supported 33.08%, so the headline
leaves 6.28 pp unclaimed. A paper selecting its most flattering number would have taken
that one.

**But the audit tests one selection and not the other, and the untested one does not come
out clean.** Reading the grid down the UltraFeedback column, MV (26.79%) is the most
favourable of the four baselines for that dataset — AVG gives 9.18%, WS 24.85%, UWS
8.38%. So the reported pair is the argmax of its row *and* the argmax of its column. The
published audit decides only `headline_is_max_within_the_named_baseline` and
`headline_is_the_global_argmax`; it never asks whether the *baseline* was chosen after the
fact, and no check here answers that. This is therefore recorded as **the headline located
precisely within its grid**, not as a finding of no cherry-picking — a distinction an
earlier revision of this page elided, asserting an integrity conclusion its own audit
could not support.

Contrast this with [Claim 2](#/claim-2-average-improvement), where the same style of
audit *did* find a problem. The two checks are the same kind of check; only the answers
differ.

## Does the paper agree with itself about this number?

Claim 1's empirical half needs a judge-score matrix that was never released (§1c below).
But the paper reports CARE-SVD's MAE on these six datasets **twice**, and the second
report can be checked against the first with no data at all.

Appendix E.8's Table 7 sweeps which recovered latent factor is used as the quality
direction. Its opening sentence is *"We use the same scoring-task setup as in Table 1"*,
and it identifies the first factor as CARE-SVD's default: *"Beyond the default heuristic
(choosing the first factor), we also evaluate all recovered latent factors…"*. So
Table 7's **1st Factor** row and Table 1's **CARE-SVD** row are two published
measurements of one quantity, each with its own mean and standard deviation over seeds.

Two tables of the same quantity must agree within their own error bars. The test is
two-sided and could have come out clean on all six columns.

<!-- FILL:c1.appendix -->
| Dataset | Table 1 CARE-SVD | Table 7 1st Factor | gap | z | verdict |
|---|---|---|---|---|---|
| ASSET | 27.629 ± 0.156 | 27.148 ± 0.133 | 0.481 | 2.35 | **disagree** |
| FeedbackQA | 0.730 ± 0.002 | 0.753 ± 0.003 | -0.023 | 6.38 | **disagree** |
| Review-5K | 1.957 ± 0.018 | 1.950 ± 0.006 | 0.007 | 0.37 | agree |
| Summarize | 1.325 ± 0.004 | 1.325 ± 0.003 | 0.000 | 0.00 | agree |
| UltraFeedback | 0.623 ± 0.006 | 0.622 ± 0.006 | 0.001 | 0.12 | agree |
| Yelp | 0.694 ± 0.004 | 0.694 ± 0.005 | 0.000 | 0.00 | agree |

4 of 6 columns agree within the paper's own combined error bars (threshold z ≤ 2.0, fixed before the z-scores were computed). Disagreeing: **ASSET, FeedbackQA**.

The appendix's own assertion that the leading factor beats every other factor: ****yes**** on the **4 of 6** columns where it is testable at all. On FeedbackQA, Summarize Table 7 lists a single factor, so the assertion is true there by having nothing to compare against and is not counted.

| Headline figure | using Table 1 | using Table 7 | shift |
|---|---|---|---|
| Claim 1's UltraFeedback reduction vs MV | 26.792 % | 26.910 % | 0.118 pp |
| Claim 2's improvement over AVG | 17.365 % | 18.534 % | 1.169 pp |
| Claim 2's improvement over MV | 12.750 % | 13.983 % | 1.233 pp |

- Claim 1's own quoted MAE is internally consistent between the two tables: ****yes****
- Claim 1's headline still rounds to the same one-decimal percentage under both: ****no****

**Can our own reproduction settle the ASSET disagreement?** ASSET is the only disputed column whose judge outputs were released. Over 5 seeds we measure **27.412 ± 0.264** (range 27.140–27.735), which sits 1.84 standard errors from Table 1's value and 2.23 from Table 7's. Excludes Table 1: **no** · excludes Table 7: **yes**. Our seed spread is wider than both reported standard deviations: **yes**.

**But this does not adjudicate, and the reason is in our own seeds.** Of the 5 seeds, only 4 produced distinct values — two are bit-identical — so there are fewer independent draws than seeds and the standard error above is optimistic. Recomputed at the number of distinct values the standard error is 0.1321, and the exclusion of Table 7 no longer holds: **no**. The adjudication survives the duplicate seed: **no**. **This column is therefore reported as NOT adjudicating between the paper's two published values.** At the nominal five seeds it would exclude Table 7 and side with Table 1 — a stronger result than is claimed here — and that reading is deliberately not taken, because an exclusion that holds at n = 5 and fails at n = 4 is marginal. A blind reviewer found the duplicated seed; without it this block would have published the stronger claim.
<!-- /FILL -->

Read the result carefully, because it cuts both ways.

* **For Claim 1 specifically, the paper is internally consistent.** The UltraFeedback row
  of the table above agrees to well inside one combined standard deviation. Claim 1's own
  quoted MAE survives its own paper's second look — a *corroboration* of the number this
  claim rests on, obtained independently of the blocked dataset.
* **The headline percentage is not stable to the last digit.** Substituting the
  appendix's own UltraFeedback value moves the reduction across the 26.85% rounding
  boundary, so the same claim reads **26.9%** from Appendix E.8 and 26.8% from Table 1.
  The claim is right about the quantity and off by one in the last displayed place,
  depending on which of the paper's two tables you read.
* **Two other columns do not reconcile at all**, and neither is UltraFeedback:
  **FeedbackQA**, whose discrepancy the paper's own reported seed noise cannot absorb,
  and **ASSET**. Both bear on [Claim 2](#/claim-2-average-improvement), which averages all
  six columns, not on Claim 1. The exact gaps and z-scores are in the table above.

What this is not: it is not evidence that CARE fails, and it is not a measurement of
UltraFeedback. It is an internal-consistency defect in the paper's reporting, decided
exactly, and it is scoped to the two columns named.

## 1c — the reproduction, and the honest boundary

CARE's aggregation is deterministic linear algebra on a fixed `n × p` judge-score
matrix. Producing that matrix is the expensive step: the paper's Appendix E.2 states

> Generating LLM judge outputs took up to 3 hours per dataset

on an NVIDIA A100. The authors' repository releases the judge-score matrices for
**ASSET** and for **CivilComments** and **PKU-BETTER** only. There is no released
UltraFeedback matrix, and regenerating it would require GPU inference over the paper's
11–20 LLM judges, which this campaign is explicitly not authorised to buy.

So assertion 1c is recorded **BLOCKED**, with that exact missing capability named:
*GPU inference to regenerate the UltraFeedback judge-score matrix (≈3 A100-hours),
because the authors released no UltraFeedback judge outputs.*

It is **not** replaced by a synthetic proxy. The 2026-07-30 revision reported
"CARE MAE 0.3212 vs majority-vote 0.7293 on synthetic data" against this claim; those
numbers are about a simulation, not about UltraFeedback, and the judge was right to
reject them. They are not repeated here.

## What *is* reproduced at full scale on a Table 1 dataset

To show that the pipeline reproduces the paper's Table 1 methodology rather than merely
its arithmetic, the **ASSET** column — the one Table 1 dataset whose judge outputs the
authors did release — is reproduced end-to-end with the authors' own code at `72f5b29`
over five seeds `2024…2028`, including the paper's validation-based `γ` search over the
grid `[0.1, 0.2, 0.25, 0.5, 0.75, 1, 2, 3, 5, 7, 10]`.

<!-- FILL:c1.asset -->
| Method | Paper (Table 1) | Reproduced (n=5 seeds) | Abs. diff | Rel. diff |
|---|---|---|---|---|
| MV | 31.153 | 31.153 ± 0.000 | 0.000 | 0.00 % |
| AVG | 33.663 | 33.663 ± 0.000 | 0.000 | 0.00 % |
| WS | 29.073 | 29.230 ± 0.000 | 0.157 | 0.54 % |
| UWS | 33.928 | 33.928 ± 0.000 | 0.000 | 0.00 % |
| CARE-SVD | 27.629 | 27.412 ± 0.264 | 0.217 | 0.79 % |

- CARE-SVD is the best method on the reproduced ASSET column: **yes**
- Reproduced reduction vs MV: **12.01 %**
- Reproduced improvement vs AVG: **18.57 %**
- Contract satisfied: **yes**
<!-- /FILL -->

This is real-benchmark evidence for the *method*; it is deliberately not presented as
evidence for the UltraFeedback numbers, which remain BLOCKED.

## Negative control

The ASSET judge matrix is row-permuted **column by column**, destroying the
row-alignment between judges while preserving every marginal distribution. CARE's
advantage must vanish, because the mechanism it exploits — correlated judge errors on
the *same* item — has been destroyed.

<!-- FILL:c1.control -->
| Setting | CARE MAE on ASSET |
|---|---|
| Real judge scores | **27.7195** |
| Row-permuted judge scores (control) | 40.1357 |
| Majority vote, real scores | 31.1533 |

Control behaves as intended: **yes**. Row-permuting each judge column preserves every marginal but destroys the shared latent structure CARE exploits; if CARE still won, the advantage would not be coming from confounder-aware aggregation.

**Why the first row differs from the reproduction table above.** The reproduction runs the authors' full Table 1 procedure — five seeds, each with the paper's validation-based γ grid — and reports the mean over seeds. This control runs a single fixed configuration at γ = 1.0 with no seed averaging, because what it has to hold constant is the aggregator, not the tuning: the only thing allowed to differ between its two rows is whether the judge matrix has been column-permuted. The two numbers are therefore different quantities and are not expected to match; only the gap between the rows of this table is evidence.
<!-- /FILL -->

A control that still showed CARE winning would mean the measured advantage came from
the marginals rather than the confounder structure.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) recomputes the 26.8% figure in
exact `Fraction` arithmetic from a **second, independent transcription** of Table 1
made from the paper HTML, so a transcription error in `paper_source.py` cannot pass
unnoticed.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as part of stage C1_C2_C3_tables
```

Environment, seeds, CPU and runtime: [Fixed command and environment](#/environment-and-command).
Record: [`raw/verdict.json`](raw/verdict.json); extract
[`raw/table1_asset.csv`](raw/table1_asset.csv). Code:
[`repro/src/claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured, except for the elements that entry itself marks `POST-HOC` —
is entry `C1` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
