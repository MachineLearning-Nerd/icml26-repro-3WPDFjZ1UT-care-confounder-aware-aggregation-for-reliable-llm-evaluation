# Claim 1 — UltraFeedback MAE

<!-- FILL:c1.header -->
*(pending release run)*
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

## 1a and 1b — decided exactly

`table_arithmetic()` recomputes the reduction from Table 1's own entries:

```
(MV − CARE-SVD) / MV = (0.851 − 0.623) / 0.851 = 26.792%
```

against the paper's stated `26.8%`. This is deterministic, has no seed, and is checked
to a tolerance of 0.05 percentage points.

<!-- FILL:c1.arithmetic -->
*(pending release run)*
<!-- /FILL -->

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
*(pending release run)*
<!-- /FILL -->

This is real-benchmark evidence for the *method*; it is deliberately not presented as
evidence for the UltraFeedback numbers, which remain BLOCKED.

## Negative control

The ASSET judge matrix is row-permuted **column by column**, destroying the
row-alignment between judges while preserving every marginal distribution. CARE's
advantage must vanish, because the mechanism it exploits — correlated judge errors on
the *same* item — has been destroyed.

<!-- FILL:c1.control -->
*(pending release run)*
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

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C1` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
