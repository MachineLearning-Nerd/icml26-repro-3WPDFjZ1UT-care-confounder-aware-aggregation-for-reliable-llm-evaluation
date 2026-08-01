# Claim 2 — 17.37% average improvement over simple averaging

<!-- FILL:c2.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

> CARE achieves an average 17.37% improvement over simple averaging across
> continuous-scoring benchmarks (Table 1).

The paper states two such figures in the same sentence — **17.37%** against AVG and
**12.75%** against MV — over Table 1's six continuous-scoring datasets (ASSET,
FeedbackQA, Review-5K, Summarize, UltraFeedback, Yelp).

## The substantive question: what does "average improvement" mean?

The paper does not define it, and the choice matters: the candidate definitions
disagree by several percentage points. This claim is therefore decided by
**identifying** the definition rather than by assuming one. `table_arithmetic()`
enumerates three natural readings and evaluates each against **both** published
targets simultaneously — a definition only qualifies if it reproduces `17.37` *and*
`12.75`.

<!-- FILL:c2.definitions -->
*(pending release run)*
<!-- /FILL -->

Requiring both targets at once is what makes this a real test: any single target can be
hit by one of several definitions by coincidence, but hitting `17.37` and `12.75`
together identifies the definition **uniquely**.

### What that identification reveals

The pooled mean-MAE ratio is **dominated by ASSET**, whose MAE is on a 0–100 scale
(CARE-SVD 27.629, AVG 33.663) while the other five datasets are on 0–10 or smaller
scales. Pooling unnormalised MAEs across incommensurable scales means ASSET alone
sets nearly the whole figure. Under the scale-free reading — the mean of per-dataset
relative improvements — CARE's advantage over AVG is **15.19%**, not 17.37%, and its
advantage over MV is **17.59%**, larger than the 12.75% the paper reports.

This is reported as a **finding about the paper's headline statistic**, not as an error
in it: the arithmetic is exactly as stated once the definition is fixed. But a reader
who assumes "average improvement" means the average of the improvements will get a
different number, and the direction of the discrepancy is not the same for both
baselines.

## Per-dataset breakdown

<!-- FILL:c2.per_dataset -->
*(pending release run)*
<!-- /FILL -->

## Reproduction at full scale

The arithmetic above is exact and complete for the claim as stated. For the underlying
MAEs, **ASSET** — the only Table 1 dataset whose judge outputs the authors released — is
reproduced end-to-end with the authors' own code at `72f5b29` over seeds `2024…2028`,
including the paper's validation-based `γ` search.

<!-- FILL:c2.asset -->
*(pending release run)*
<!-- /FILL -->

The other five Table 1 datasets have no released judge-score matrices and regenerating
them requires GPU inference over 11–20 LLM judges (Appendix E.2: up to 3 hours per
dataset on an A100). They are recorded **BLOCKED** with that named missing capability
rather than replaced by synthetic judges. The coverage audit that enumerates exactly
which columns are reachable is part of the verifier output, not a prose assertion.

## Negative control

Column-wise row permutation of the ASSET judge matrix, which preserves every judge's
marginal distribution but destroys cross-judge row alignment. CARE's advantage over
plain averaging must disappear.

<!-- FILL:c2.control -->
*(pending release run)*
<!-- /FILL -->

## Independent check

[`independent_check.py`](repro/src/independent_check.py) recomputes all three candidate
definitions in exact `Fraction` arithmetic from a **second, independent transcription**
of Table 1, so the identification cannot be an artefact of a transcription slip.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as part of stage C1_C2_C3_tables
```

Record: [`raw/verdict.json`](raw/verdict.json); extract
[`raw/table1_asset.csv`](raw/table1_asset.csv). Code:
[`repro/src/claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py).
Environment and seeds: [Fixed command and environment](#/environment-and-command).

## Contract

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C2` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
