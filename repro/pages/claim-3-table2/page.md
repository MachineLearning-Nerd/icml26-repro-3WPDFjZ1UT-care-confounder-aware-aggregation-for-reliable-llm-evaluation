# Claim 3 — Table 2: best accuracy on 5 of 6, and Summarize

<!-- FILL:c3.header -->
*(pending release run)*
<!-- /FILL -->

The 2026-07-30 revision did not address this claim at all; the judge scored it
**INCONCLUSIVE (0/2)**. It is addressed here in full.

## The exact claim

> On classification/preference datasets, CARE attains the best accuracy on 5 of 6
> datasets, including a 13.4% relative improvement over the baseline on Summarize
> (0.814±0.001 vs 0.705±0.000) (Table 2).

Four separable assertions:

| | Assertion |
|---|---|
| 3a | CARE (SVD or Tensor) has the highest accuracy in 5 of Table 2's 6 columns |
| 3b | CARE-Tensor specifically leads on PKU-BETTER, SHP and Summarize |
| 3c | The relative improvement on Summarize is 13.4% |
| 3d | Those accuracies are reproducible by running CARE on the datasets |

Table 2 contains **nine** methods — MV, AVG, WS, UWS, Dawid–Skene, GLAD, MACE,
CARE-SVD, CARE-Tensor. Assertions 3a–3c are recomputed by taking the column-wise
argmax over all nine, never over a subset.

## 3a and 3b — recomputed from Table 2

<!-- FILL:c3.recompute -->
*(pending release run)*
<!-- /FILL -->

The check is stricter than the claim: as well as counting CARE wins, the recomputed
column winners are compared cell-by-cell against the **bold cells** the paper typesets,
so a mismatch between the paper's prose and its own table would be caught.

## 3c — the Summarize figure, and a defect in the claim string

The claim string quotes the pair `0.814 ± 0.001` vs `0.705 ± 0.000`. In Table 2:

* `0.814` is CARE-Tensor on Summarize — correct.
* `0.705` is **not the strongest baseline** on Summarize. It is the WS / Dawid–Skene
  value. The strongest non-CARE method on Summarize is **GLAD at 0.718**.

Both readings are computed and reported:

| Reading | Arithmetic | Result |
|---|---|---|
| Against the strongest Table 2 baseline (GLAD, 0.718) | `(0.814 − 0.718) / 0.718` | **13.37% ≈ 13.4%** ✓ matches the paper |
| Against the claim string's own pair (0.705) | `(0.814 − 0.705) / 0.705` | 15.46% ✗ does not match |

So **the paper's stated 13.4% is correct** and the *claim string's* quoted baseline
value is wrong — it names a weaker baseline than the one the percentage was computed
against. The claim is adjudicated against the paper, and the discrepancy is reported
rather than resolved silently in either direction.

<!-- FILL:c3.summarize -->
*(pending release run)*
<!-- /FILL -->

## 3d — reproduction at full scale

Table 2's judge-score matrices were released by the authors for **CivilComments** and
**PKU-BETTER**. Both columns are reproduced end-to-end with the authors' own code at
`72f5b29` over five seeds `2024…2028`, covering **all nine methods** — the four simple
aggregators, the three weak-supervision baselines (Dawid–Skene, GLAD, MACE) run through
the authors' own baseline harness, and both CARE variants.

<!-- FILL:c3.table2 -->
*(pending release run)*
<!-- /FILL -->

Chatbot-Arena, PKU-SAFER, SHP and Summarize have no released judge outputs. Note that
this specifically blocks the *reproduction* of the Summarize pair `0.814 / 0.718`, even
though the arithmetic in 3c is decided exactly. Those four columns are recorded
**BLOCKED** with the named missing capability: *GPU inference to regenerate the judge
outputs (≈3 A100-hours per dataset), because the authors released none for these
datasets.*

## Negative control

Column-wise row permutation of the released judge matrices, which preserves each
judge's marginal accuracy while destroying the cross-judge correlation structure CARE
models. Both CARE variants must fall back to roughly the level of the simple
aggregators.

<!-- FILL:c3.control -->
*(pending release run)*
<!-- /FILL -->

## Independent check

[`independent_check.py`](repro/src/independent_check.py) recomputes the column-wise
argmax and both Summarize percentages in exact `Fraction` arithmetic from a **second,
independent transcription** of Table 2's full nine-method grid.

The value of the second transcription is not hypothetical here: an earlier draft of
this reproduction transcribed only four of Table 2's nine methods and consequently
computed the Summarize improvement as 15.46%. Reading the complete table is what
produced the correct 13.37%.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as part of stage C1_C2_C3_tables
```

Record: [`raw/verdict.json`](raw/verdict.json); extract
[`raw/table2.csv`](raw/table2.csv). Code:
[`repro/src/claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py).
Environment and seeds: [Fixed command and environment](#/environment-and-command).

## Contract

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C3` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
