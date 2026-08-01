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

## 3d — reproduction at full scale, and a defect in the released data

Table 2's judge-score matrices were released for **CivilComments** and **PKU-BETTER**.
Only one of them can actually support an accuracy.

### CivilComments — reproduced

Reproduced end-to-end with the authors' code at `72f5b29` over five seeds
`2024…2028`, covering all nine methods: the four simple aggregators, the three
weak-supervision baselines (Dawid–Skene, GLAD, MACE) through the authors' own baseline
harness, and both CARE variants. Its released labels are valid and exactly balanced
(2 500 / 2 500).

<!-- FILL:c3.table2 -->
*(pending release run)*
<!-- /FILL -->

### PKU-BETTER — BLOCKED, because its released labels are constant

Reproducing this column returns accuracies of **exactly 0.0** for MV, AVG, WS and UWS
and **exactly 1.0** for CARE-Tensor. Those are not plausible accuracies, and the cause
is in the released data rather than in the aggregation. The authors' own run record
reports `class_balance: 100.0` — every test label is the same class.

Four independent checks of the released artifact, each reproducible from the public
repository at `72f5b29`:

| Check | Result |
|---|---|
| `gold_label_binary` in the seven released judge files | constant `0` in **all seven** |
| `gold_label_num` in the judge files **and** in the standalone `data/preference/pku_better.csv` | constant `1` (9 000 rows) |
| `was_swapped` | constant `False` — the A/B order was never randomised, so the correct answer cannot vary by row |
| judges' own `pref_A_or_B` | "B" on ~88 % of rows, i.e. anti-correlated with the only gold answer the file admits |

`gaussian_mixture_main.py` masks this. When the label column has one distinct value it
falls back to `pref_A_or_B` — which is *a judge's own preference*, not ground truth — so
the resulting "accuracy" scores a judge against itself. That is why it saturates at
exactly 0 or 1.

**We therefore report no accuracy for PKU-BETTER at all.** A number computed against a
constant label is meaningless rather than merely inaccurate, so this is recorded as
BLOCKED by a **failed integrity precondition**, and no verdict about the paper is
inferred from it in either direction. In particular this is *not* evidence against
CARE: the paper's published PKU-BETTER numbers were presumably computed against labels
that are not in the release.

This is a distinct blocking reason from the other four Table 2 columns
(Chatbot-Arena, PKU-SAFER, SHP, Summarize), which have **no released judge outputs at
all** and would need GPU inference to regenerate (≈3 A100-hours each, Appendix E.2).

The precondition is executable and published:
[`repro/src/label_audit.py`](repro/src/label_audit.py). It runs **before** any accuracy
is computed and is reported in `verdict.json` under `label_integrity_audit`.

<!-- FILL:c3.label_audit -->
*(pending release run)*
<!-- /FILL -->

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
both Summarize percentages in exact `Fraction` arithmetic, from literals typed
independently of the claim module, and asserts that the paper's 13.4 % follows from
GLAD's 0.718 and **not** from the 0.705 quoted in the circulated claim string.

Being exact about the limit of this check: it re-derives the *percentages*, not the
*argmax*. The nine-method grid is transcribed once, in the claim module; there is no
second transcription of it, and the 5-of-6 count is therefore not independently
recomputed. An earlier version of this page claimed otherwise.

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
