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

### What the identified definition actually is

Identifying the definition is not the end of the matter, because the identified
definition is not an average across benchmarks. That is an algebraic fact, not an
opinion about wording:

```
(mean(AVG) - mean(CARE)) / mean(AVG)  ==  Σ_i w_i · r_i  ,   w_i = AVG_i / Σ_j AVG_j
```

where `r_i` is dataset `i`'s own relative improvement. "Improvement of the mean MAE"
**is identically** a weighted mean of the per-dataset improvements, with weights fixed by
how large each benchmark's MAE happens to be. The verifier checks this identity rather
than asserting it, and the independent checker re-derives it in exact rationals.

<!-- FILL:c2.weights -->
*(pending release run)*
<!-- /FILL -->

Those weights are not a modelling choice anyone defended. They are an artefact of unit
selection: ASSET's judges score on a 0–100 scale, so its MAE is ≈ 30 while the other five
benchmarks sit near 1, and ASSET therefore absorbs **84.4%** of the weight. The published
"average across scoring datasets" is, to within a rounding error, ASSET's number alone.

### The test that decides it: invariance to units

Any statistic that deserves to be called an average *across benchmarks* must be
unchanged when one benchmark is re-expressed in different units — reporting ASSET on
0–10 instead of 0–100 changes no method's ranking, no method's relative advantage, and
nothing about CARE. So we rescale ASSET's whole column by a constant and recompute.

<!-- FILL:c2.invariance -->
*(pending release run)*
<!-- /FILL -->

The paper's statistic is not invariant, and the failure is not marginal. It ranges over
several percentage points under unit changes well inside the range of scales the six
benchmarks actually use, and — the substantive consequence — **the qualitative
conclusion reverses.** The paper reports a larger gain over AVG (17.37%) than over MV
(12.75%). Express ASSET on a 0–10 scale and the ordering flips: 15.60% over AVG against
16.89% over MV. Which baseline CARE beats by more is, under this statistic, a
consequence of a unit convention on one dataset.

The unit-invariant quantity — the average across the six benchmarks of CARE-SVD's
improvement — is **15.19% over AVG** and **17.59% over MV**, identical under every
rescaling (exactly, as set-equality over rationals, not to a tolerance).

### Verdict

The claim under test asserts *"an average 17.37% improvement over simple averaging
across continuous-scoring benchmarks."* The quantity it names is unit-invariant and
equals **15.19%**. The published 17.37% is a different, unit-dependent statistic that
the paper does not define and that places 84.4% of its weight on one benchmark. This
claim is therefore **FALSIFIED as worded**, with the exact alternative statistic
identified and reproduced to four significant figures.

Two things this verdict does *not* say, to keep its scope honest. It does not allege an
arithmetic error: every number the paper prints is correct under the definition it
used. And it does not say CARE fails to beat AVG — CARE improves on AVG on all six
benchmarks, by 15.19% on average. What is falsified is the specific published
figure's status as an across-benchmark average.

**How this finding was arrived at, stated plainly.** The discrepancy between the pooled
and unweighted readings was found by exploration, not predicted in advance, and the
2026-08-01 revision of this page reported it as "a finding about the paper's headline
statistic, **not as an error in it**". That framing was too weak, and it was mine. The
unit-invariance criterion applied here is not fitted to the data — it is a property any
across-benchmark average must have, stated independently of what the numbers turned out
to be. See [Limitations item 21](#/limitations).

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

`c2_unit_invariance_exact` additionally re-decides the falsification above in exact
rational arithmetic. This is not redundancy for its own sake: the verdict turns on one
statistic being *exactly* invariant while another is not, and floating point is the
wrong instrument for confirming an exact invariance — `spread == 0.0` in `float64`
could be rounding. Over `Fraction`s the invariance is set-equality of exact rationals,
and the weighted-mean identity is an exact `==` rather than a residual below a
threshold. The checker fails if the two implementations disagree on
`falsified_as_worded`, so the verdict cannot rest on one implementation.

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
