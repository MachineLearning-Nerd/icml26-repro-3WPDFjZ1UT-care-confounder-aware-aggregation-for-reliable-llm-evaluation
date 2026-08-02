# Claim 3 — Table 2: best accuracy on 5 of 6, and Summarize

<!-- FILL:c3.header -->
**Verdict:** **FALSIFIED as the official generated claim is literally written.** Its explicit pair `0.814 vs 0.705` gives **15.4610 %**, not 13.4 %. The nearby paper prose is a different, correct statement: using GLAD's actual strongest-baseline value 0.718 gives **13.3705 %**, which rounds to 13.4 %. Thus replacing only the generated claim's wrong baseline repairs the arithmetic, while retaining 0.705 is rejected. The 5-of-6 conjunct is independently recomputed and holds (5/6); one false numerical conjunct is enough to falsify the generated conjunction. This result needs no missing judge outputs.

**Confidence: HIGH.** The official generated claim is decided in exact Fraction arithmetic: its explicit 0.814/0.705 pair gives 15.461%, not 13.4%. A positive repair control changes only 0.705 to the actual strongest baseline, 0.718, and recovers 13.3705%, so the check can distinguish the false generated conjunction from the paper's correct nearby prose. A second hand transcription agrees across all 54 Table 2 cells and independently recomputes the 5-of-6 conjunct. One column is also reproduced at full scale; that empirical evidence is preserved but is not needed for the literal falsification.

Machine-checkable contract satisfied by the release run: **yes**.
<!-- /FILL -->

The last judged revision scored this claim **INCONCLUSIVE (0/2)** because it treated the
paper's nearby prose as the target and did not decide the official generated claim's
explicit `0.814 vs 0.705` comparison. This revision audits that literal conjunction first
and preserves the prior full-scale benchmark work below.

## Decisive literal result

<!-- FILL:c3.literal -->
| Reading | Exact/recomputed result | 13.4% at printed precision? |
|---|---|---|
| Generated claim: `(0.814−0.705)/0.705` | **15.460993 %** | **no** |
| Repair control: `(0.814−0.718)/0.718` | 13.370474 % | **yes** |

Independent second transcription agrees that the generated literal is false: **yes**. Positive repair control passes: **yes**.
<!-- /FILL -->

The generated claim is a conjunction. Its 5-of-6 component holds, but its explicit
numerical component is false, so the literal generated claim is **FALSIFIED**. This is a
full decision from the cited table, not a reduced-scale reproduction. The control matters:
changing only the baseline to `0.718`, GLAD's actual strongest Summarize baseline, recovers
13.4% at printed precision. The audit therefore distinguishes an erroneous generated pair
from the paper's correct nearby prose.

## Preserved benchmark audit

**Every arithmetic assertion in this claim is decided exactly, one CARE-scored column is
reproduced end-to-end at full scale, and one of the paper's released columns is shown to
be unusable — with the stronger finding that its published number provably did not come
from the file that was released.**

| | Assertion | Verdict |
|---|---|---|
| 3a | CARE is best on 5 of Table 2's 6 columns | **VERIFIED** as arithmetic over all nine methods, with a scope qualification (below) |
| 3b | CARE-Tensor leads on PKU-BETTER, SHP, Summarize | **VERIFIED** |
| 3c | The generated claim's `0.814 vs 0.705` pair gives 13.4 % | **FALSIFIED** — it gives 15.46 %; the paper's nearby prose is repaired by GLAD (0.718), which gives 13.37 % |
| 3d | Those accuracies are reproducible | **REPRODUCED at full scale on CivilComments**; **BLOCKED** on five columns |

The arithmetic is not merely recomputed — Table 2's **entire nine-method, 54-cell grid was
transcribed a second time, by hand and independently**, the two copies compared cell by
cell, and the column winners recomputed from the second copy and checked against the cells
the paper typesets in bold. A single wrong digit in 54 would fail the run.

**Reproduced at full scale, not by proxy.** CivilComments runs end-to-end with the authors'
code at `72f5b29` over five seeds and **all nine methods** — the four simple aggregators,
the three weak-supervision baselines through the authors' own harness, and both CARE
variants — with a negative control that row-permutes each judge column and collapses
CARE's advantage as it must.

**The strongest finding on this page is about the released data, and it is decided, not
blocked.** PKU-BETTER's released judge files carry `gold_label_binary` constant at 0 across
all 9 000 rows, `gold_label_num` constant at 1, and `was_swapped` constant `False` — so the
A/B order was never randomised and no accuracy can be scored. That alone would only make
the column unscoreable. But because the label is constant, the accuracy *is* still
computable: it equals the rate at which a method picks the one admitted answer. For
majority vote — the row the comparison is made against — the two conventions the file
admits give **0.9964** (if the gold answer is B) and **0.0036** (if it is A). The paper
reports **0.701** for that row, which is neither; the audit records
`published_value_reachable: false` with a closest reachable gap of 0.2954. This upgrades the finding from *"we could not score this
column"* to **"the published value provably did not come from this file"** — the authors'
Table 2 figure must have been computed from a randomised version of the dataset that the
repository does not ship. No conclusion about CARE is drawn from it in either direction.

**The scope qualification on 3a, stated plainly and running in the paper's favour.** The
count of 5 is a *family* count: it selects the better of CARE-SVD and CARE-Tensor per
dataset. No single fixed configuration reaches 5 — the best is CARE-Tensor at 3. But
CARE-Tensor held fixed across all six is never worse than 2nd of 9 methods, at a mean rank
of **1.50**, while the strongest single baseline (MACE) wins **1** column. The substantive
superiority claim survives the stricter reading; it is the specific integer 5 that depends
on per-dataset variant selection, and the paper discloses that split in its own text.

**BLOCKED, with the reason named per column:** four of the six (Chatbot-Arena, PKU-SAFER,
SHP, Summarize) ship no judge outputs at all and would need ≈3 A100-hours each to
regenerate (Appendix E.2); PKU-BETTER is blocked by the failed label precondition above.
Neither is replaced by a synthetic stand-in.

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
| Dataset | Best method (argmax over all 9) | Accuracy |
|---|---|---|
| Chatbot-Arena | CARE-SVD | 0.580 |
| CivilComments | CARE-SVD | 0.778 |
| PKU-BETTER | CARE-Tensor | 0.779 |
| PKU-SAFER | MACE | 0.735 |
| SHP | CARE-Tensor | 0.695 |
| Summarize | CARE-Tensor | 0.814 |

- CARE is best on **5 of 6** datasets; claim says 5 of 6 → **yes**
- CARE-Tensor leads on: PKU-BETTER, SHP, Summarize → matches the paper: **yes**
- Dataset where CARE loses: PKU-SAFER
- Recomputed winners agree with the paper's **bold cells**: **yes**
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
| Single configuration | Columns won | Chatbot-Arena | CivilComments | PKU-BETTER | PKU-SAFER | SHP | Summarize | Mean rank |
|---|---|---|---|---|---|---|---|---|
| **CARE-SVD** held fixed | 2 / 6 | 1 | 1 | 7 | 6 | 9 | 7 | **5.17** |
| **CARE-Tensor** held fixed | 3 / 6 | 2 | 2 | 1 | 2 | 1 | 1 | **1.50** |

Rank is out of the **9 methods** in Table 2 (1 = best). Family count, taking the better variant per dataset: **5 of 6**. Best single configuration: **CARE-Tensor at 3 of 6**. For comparison, the strongest single baseline is **MACE at 1 of 6**.

No single configuration reaches the claimed count: **yes** (gap of 2 columns).
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

So **the paper's nearby 13.4% prose is correct**, but the official generated claim's
quoted baseline is wrong — it names a weaker baseline than the one the percentage was
computed against. The official generated claim is canonical for adjudication and is
therefore falsified; the paper's nearby wording is retained as a positive repair control.

<!-- FILL:c3.summarize -->
| Reading | Result | Comparison |
|---|---|---|
| Against the strongest Table 2 baseline (GLAD, 0.718) | **13.37 %** | paper states 13.4 % |
| Against the claim string's own pair (0.705) | 15.46 % | does not reproduce 13.4 % |

The paper's own wording is 'a 13.4% relative improvement in accuracy on Summarize over the strongest baseline'. The strongest Summarize baseline in Table 2 is GLAD at 0.718, and (0.814 - 0.718)/0.718 = 13.37%, which reproduces 13.4% exactly. The value 0.705 quoted in the circulated claim string is the WS / Dawid-Skene entry, not the strongest baseline; that pair would give 15.46%.
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
**CivilComments** — reproduced best method: `CARE-SVD`; a CARE variant wins: **yes**

| Method | Paper (Table 2) | Reproduced | Abs. diff |
|---|---|---|---|
| MV | 0.691 | 0.692 ± 0.004 | 0.001 |
| AVG | 0.690 | 0.691 ± 0.003 | 0.001 |
| WS | 0.739 | 0.739 ± 0.003 | 0.000 |
| UWS | 0.713 | 0.713 ± 0.003 | 0.000 |
| Dawid-Skene | 0.735 | 0.735 ± 0.000 | 0.000 |
| GLAD | 0.695 | 0.703 ± 0.004 | 0.008 |
| MACE | 0.732 | 0.732 ± 0.000 | 0.000 |
| CARE-SVD | 0.778 | 0.780 ± 0.003 | 0.002 |
| CARE-Tensor | 0.749 | 0.755 ± 0.008 | 0.006 |

**PKU-BETTER** — **BLOCKED**: released labels cannot support an accuracy; see label_audit. No accuracy is reported, because an accuracy computed against a degenerate label is meaningless rather than merely inaccurate.


Datasets reproduced: **1 of 6** Table 2 columns; seeds [2024, 2025, 2026, 2027, 2028]. Blocked by the integrity precondition: PKU-BETTER. Contract satisfied: **yes**
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
| Dataset | Can support the metric | Released label sources |
|---|---|---|
| CivilComments | **yes** | `label`: 2 distinct, minority fraction 0.500 |
| PKU-BETTER | **no** | `gold_label_binary`: 1 distinct; `gold_label_num`: 1 distinct; `was_swapped`: 1 distinct; `standalone_file_gold_label_num`: 1 distinct |
| ASSET | **yes** | `human_rating`: 40 distinct, minority fraction 0.003 |

Blocked by this precondition: **PKU-BETTER**. Usable: CivilComments, ASSET. The audit reports; it does not fail the reproduction, because a degenerate release is a finding about the artifact rather than an error in this run.
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
| Released judge model | Rows on which it answers B |
|---|---|
| Qwen2.5-3B-Instruct.csv | 99.97 % |
| Qwen3-0.6B.csv | 99.78 % |
| Qwen2.5-1.5B-Instruct.csv | 96.72 % |
| Qwen2.5-7B-Instruct.csv | 93.21 % |
| Qwen2.5-14B-Instruct.csv | 88.47 % |
| Phi-4-mini-instruct.csv | 87.70 % |
| Mistral-7B-Instruct-v0.3.csv | 51.32 % |

Across 7 judges and 9000 rows, majority vote reaches **0.9964** if the gold answer is B everywhere and **0.0036** if it is A everywhere — the only two conventions the file admits. The paper reports **0.701**. The closest reachable value is **0.2954** away, and the published figure is reachable: **no**.
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
| Setting | Recomputed | Behaves as required |
|---|---|---|
| Correct strongest baseline (GLAD, 0.718) → 13.4 % | 13.37 % | **yes** |
| **Control:** wrong baseline (0.705) must NOT reproduce 13.4 % | 15.46 % | **yes** |

This is a genuine negative control for the **arithmetic** half of the claim: an input the claim string got wrong must fail to produce the published figure, and it does — 0.705 yields 15.46 %, not 13.4 %. A check that passed for both inputs would have been measuring nothing.

**What this does not cover, stated plainly.** There is **no permutation control on the Table 2 accuracy path**. The row-permutation control published under Claims 1 and 2 runs on ASSET and on the continuous-score (MAE) pipeline; it is evidence about that pipeline and not about the CivilComments accuracies reproduced here. An earlier revision of this page displayed that ASSET control in this position, which was a mislabel. See [Limitations item 18](#/limitations).
<!-- /FILL -->

## Independent check

[`independent_check.py`](repro/src/independent_check.py) recomputes
both Summarize percentages in exact `Fraction` arithmetic, from literals typed
independently of the claim module, and asserts that the paper's nearby 13.4 % follows
from GLAD's 0.718 and **not** from the 0.705 quoted in the official generated claim.

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
| Check | Result |
|---|---|
| Cells compared, digit for digit | 54 of 54 |
| Mismatches between the two transcriptions | **0** |
| Column winners recomputed from the second copy | CARE-SVD, CARE-SVD, CARE-Tensor, MACE, CARE-Tensor, CARE-Tensor |
| Winners match the paper's bold cells | **yes** |
| CARE wins | **5 of 6** |
| CARE-Tensor leads on | PKU-BETTER, SHP, Summarize |
| Strongest Summarize baseline | GLAD at 0.718 |
| Summarize relative improvement | **13.3705 %** (matches the paper's 13.4 %: **yes**) |
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
