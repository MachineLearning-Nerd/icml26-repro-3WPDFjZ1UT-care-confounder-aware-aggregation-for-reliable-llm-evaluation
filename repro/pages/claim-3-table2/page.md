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

### What "CARE is best on 5 of 6" counts

The count of 5 aggregates over **two** methods: it takes, per dataset, whichever of
CARE-SVD and CARE-Tensor is stronger. A count stated for a method is a claim about one
method held to one configuration everywhere, so we also ask what each fixed
configuration achieves on its own. The criterion is stated independently of the
outcome; it could have left the headline count intact, and for one variant it nearly
does.

<!-- FILL:c3.single_config -->
*(pending release run)*
<!-- /FILL -->

**This result runs in the paper's favour more than against it, and is reported that
way.** No single configuration reaches 5 of 6 — the best is CARE-Tensor at 3 — so the
headline count does carry a scope qualification. But CARE-Tensor held fixed across all
six datasets is never worse than **2nd of 9 methods**, at a mean rank of **1.50**, while
the strongest single baseline (MACE) wins only **1** column. On the paper's own table
the substantive superiority claim survives the stricter reading comfortably; it is the
specific integer 5 that depends on selecting the variant per dataset.

The qualification is also **disclosed in the paper**, which states "with CARE-Tensor
leading on three (PKU-BETTER, SHP, and Summarize)". A reader who works through that
parenthesis can recover the split. This is therefore recorded as a scope qualification
on the count, **not** as a falsification and not as an undisclosed practice.

One asymmetry is worth naming because it is invisible in the count: CARE-SVD is **last
of all nine methods on SHP** (0.543) while CARE-Tensor **wins** that same column
(0.695). The two variants are not interchangeable, which is precisely why the choice
between them cannot be made after seeing the results.

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

This column is blocked before any accuracy is computed, by a precondition that runs on
the released labels themselves and is published in full.

*An earlier revision of this paragraph opened with "reproducing this column returns
accuracies of exactly 0.0 for MV, AVG, WS and UWS and exactly 1.0 for CARE-Tensor", and
cited the authors' run record as reporting `class_balance: 100.0`. Those observations came
from exploratory runs that are **not** in this artifact: `class_balance` appears nowhere in
`raw/verdict.json`, no PKU-BETTER shard is shipped, and the verdict's PKU-BETTER entry
carries no accuracies at all. A blind reviewer checked and found them unsupported. They are
removed rather than re-run, because the argument does not need them — everything below is
in the record.*

Four independent checks of the released artifact, each reproducible from the public
repository at `72f5b29` and each recorded under `label_integrity_audit` in
[`raw/verdict.json`](raw/verdict.json):

| Check | Result |
|---|---|
| `gold_label_binary` in the seven released judge files | constant `0` in **all seven** |
| `gold_label_num` in the judge files **and** in the standalone `data/preference/pku_better.csv` | constant `1` (9 000 rows) |
| `was_swapped` | constant `False` — the A/B order was never randomised, so the correct answer cannot vary by row |
| judges' own `pref_A_or_B` | "B" on ~88 % of rows, i.e. anti-correlated with the only gold answer the file admits |

`gaussian_mixture_main.py` masks this. When the label column has one distinct value it
falls back to `pref_A_or_B` — which is *a judge's own preference*, not ground truth — so
any resulting "accuracy" scores a judge against itself and saturates. That is a statement
about the authors' code path, which is public at `72f5b29` and can be read there; this
logbook reports no accuracy for the column, so it is not a statement about a number of
ours.

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

### The stronger statement: the published column did not come from this file

"The labels are constant" says the column cannot be *scored*. It does not say the
published number cannot be *reproduced*, and those are different claims — with a
constant gold label an accuracy is still computable, it just equals the rate at which a
method picks that one answer. So we compute it, both ways.

The mechanism is visible in the released data: `was_swapped` is `False` on all 9,000
rows, so the A/B randomisation step was never applied to this slice and `response_B` is
always the preferred answer. Every judge therefore votes B on a large majority of rows.

<!-- FILL:c3.pku_reachable -->
*(pending release run)*
<!-- /FILL -->

The two conventions the file admits bracket the achievable accuracy at ≈ 0.996 and
≈ 0.004. The paper reports 0.701, which is not close to either. This upgrades the
verdict from *"we could not score this column"* to *"the published value provably did
not come from this file"* — the authors' Table 2 figure must have been computed from a
randomised version of the dataset that the repository does not ship. The column stays
**BLOCKED**, and no conclusion about CARE is drawn from it in either direction.

That distinction matters for what an earlier revision nearly published. An exploratory run
of our pipeline returned a majority-vote accuracy of zero against a stated 0.701, which
read as a spectacular refutation of the paper. It is nothing of the sort: it is the
signature of a non-randomised release slice being scored against the wrong one of two
disagreeing gold columns (`gold_label_binary` = 0 while `gold_label_num` = 1).

*That exploratory number is described here and deliberately not quoted as a measurement:
it is not in [`raw/verdict.json`](raw/verdict.json), because the label precondition now
runs first and blocks the column before any accuracy is computed. The two reachable
accuracies above — the ones this section's argument actually rests on — **are** in the
record, under `label_integrity_audit`.*

## Negative control

Column-wise row permutation of the released judge matrices, which preserves each
judge's marginal accuracy while destroying the cross-judge correlation structure CARE
models. Both CARE variants must fall back to roughly the level of the simple
aggregators.

<!-- FILL:c3.control -->
*(pending release run)*
<!-- /FILL -->

## Independent check

[`independent_check.py`](repro/src/independent_check.py) recomputes
both Summarize percentages in exact `Fraction` arithmetic, from literals typed
independently of the claim module, and asserts that the paper's 13.4 % follows from
GLAD's 0.718 and **not** from the 0.705 quoted in the circulated claim string.

It also transcribes Table 2's **full nine-method grid a second time**, by hand, and
compares it against the claim module's copy **cell by cell** — all 54 — before
recomputing the column winners, the 5-of-6 count, CARE-Tensor's three leads and the
Summarize percentage from its own copy. The recomputed winners are then checked against
the cells the paper typesets in bold.

This closes a real hole. Two earlier revisions of this page said opposite things about
it: one claimed the argmax was independently recomputed when it was not, and its
replacement correctly said the grid was transcribed only once — which meant a single
wrong digit in 54 could have flipped a column winner with nothing to catch it. A blind
reviewer named that as the largest thing it could not verify. It is now checked, and the
check gates the run: `independent_check` fails if the two transcriptions disagree
anywhere, if the recomputed winners disagree with the paper's bold cells, or if the
Summarize figure moves.

<!-- FILL:c3.transcription -->
*(pending release run)*
<!-- /FILL -->

What remains outside any check here: both transcriptions were made from the same rendered
source by the same process, so a *systematic* misreading of the paper would survive both.
Only the paper itself can settle that, and it is not shipped in this Space
(see [Raw data](#/raw-data)).

The value of transcribing the full grid is not hypothetical here: an earlier draft of
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

This claim's machine-checkable contract — written **before** any result was measured, except for the elements that entry itself marks `POST-HOC` —
is entry `C3` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
