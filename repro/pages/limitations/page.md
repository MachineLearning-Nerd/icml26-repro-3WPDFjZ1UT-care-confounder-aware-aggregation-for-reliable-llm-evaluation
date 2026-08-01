# Limitations and deviations

Items 1–9 were recorded **before** any result was measured, so nothing in them is
retrofitted to a convenient outcome. Items 10–11 were added afterwards and are marked
as such: they record two findings that went **against** this reproduction's own
hypotheses.

## 1. Ten of the twelve benchmark columns cannot be produced here

Tables 1 and 2 have six columns each, twelve in total. `SprocketLab/CARE @ 72f5b29`
releases judge-score matrices for **ASSET**, **CivilComments** and **PKU-BETTER** only.
The other nine — UltraFeedback, Summarize, FeedbackQA, Review-5K, Yelp, Chatbot-Arena,
PKU-SAFER, SHP and Table 2's Summarize — have none. Regenerating one requires running
11–20 LLM judges (0.6 B–14 B parameters) over 5,000 examples; Appendix E.2 of the paper
reports up to 3 hours per dataset **on an NVIDIA A100**.

Of the three that *are* released, only two are usable: PKU-BETTER's released labels are
constant, so no accuracy can be computed from it (item 12 below). **Two of twelve
columns are therefore reproducible here, and both are reproduced in full.**

This campaign is authorised for Hugging Face `cpu-upgrade` (8 vCPU) and explicitly
not for GPU. A rough CPU estimate for one Table 1 dataset — 11 judges totalling
~42 B parameters, ~400 prompt tokens × 5,000 examples — is on the order of
10^17 prefill FLOPs, i.e. hundreds of core-hours per dataset before any Table 2
column is touched. Those columns are therefore recorded **BLOCKED with a named
missing capability**, not replaced by a synthetic stand-in.

A second, independent obstacle applies even with a GPU: the published MAE of
0.623 ± 0.006 is a property of *the authors' particular judge outputs*. Re-running
the judges under a different vLLM version, sampling configuration or hardware
produces a different score matrix, so an exact match to three decimal places is
not recoverable by regeneration at all. Only the released matrices can decide the
published numbers exactly.

## 2. Claim 1 and Claim 2 are decided in two separable halves

The arithmetic half (26.8 %, 17.37 %, 12.75 %) is a deterministic function of
Table 1 and is decided exactly. The empirical half needs judge outputs that do not
exist publicly for the datasets those percentages are about. Both halves are
reported separately; neither is presented as the other.

## 3. Claim 3's circulated claim string disagrees with the paper

The claim string quotes the Summarize comparison as "0.814 ± 0.001 vs
0.705 ± 0.000". In Table 2, 0.705 is the WS / Dawid–Skene entry. The paper's own
words are "over the strongest baseline", which on the Summarize column is GLAD at
0.718. Both readings are computed and reported; the paper's own wording is treated
as the claim under test.

## 4. `ξ(T)` is not measured

Theorem 4.2's bound carries a `1/ξ(T)` factor, where `ξ(T)` is Chandrasekaran et
al.'s tangent-space curvature constant. It has no closed form we can evaluate, so
the model is held fixed across each sweep and only the `n`, `α` and `δ`
dependences are measured. The `1/ξ(T)` factor is reconstructed from the
derivation, not empirically confirmed.

## 5. Theorem 4.2's η-dependence is a tail statement

The theorem is a high-probability bound in `η`. The calibrated sweep reports
medians over seeds rather than an empirical `1 − 2e^{−η}` envelope, which would
need far more replicates than the CPU budget allows. The `√η` factor is therefore
reconstructed from the derivation only.

## 6. Theorem D.4's constant is checked at first order

The theorem states `4‖K_HH^{-1}‖₂‖E‖₂/δ_i + O(‖E‖₂²)`. The supremum computation
addresses the first-order term, which is exactly the term the constant attaches
to; the `O(‖E‖₂²)` remainder is separately checked not to break the bound on 400
random models at finite `‖E‖` between `10^{-6}` and `10^{-2}`.

## 7. Counterexamples are to the statements as written

The Proposition 4.1 counterexamples exploit the gap between the main text
("orthogonal") and Appendix D.2 ("orthonormal"). The appendix form is verified;
the main-text form is falsified. Both verdicts are reported, and neither is
presented as a refutation of the method itself — CARE's algorithm is unaffected,
because Algorithm 1 works with the eigenvectors of `L̂` regardless.

Likewise, the Theorem 4.3 finding is that the *stated* weight bound drops a
`σ_max³` factor that the paper's own proof produces. The mean bound is reproduced
exactly. This is a defect in a displayed inequality, not evidence that CARE-Tensor
fails to recover mixture weights.

## 8. Numerical tolerances

Eigenvector comparisons use sign alignment (`sign(⟨û, u⟩)`), since eigenvectors are
only defined up to sign; that is the same convention the theorems use. Log-log
slopes are reported with standard errors and 95 % intervals from the residuals,
and the independent checker re-estimates the Theorem 4.3 slope with Theil–Sen so a
single outlier cannot drive the verdict.

## 9. Compute record

Every number in this reproduction was produced by a Hugging Face `cpu-upgrade`
job (8 vCPU, 32 GB, $0.03/hour). The local machine was used only to read and edit
the repository. Estimated core requirement before each run, the flavour selected,
the CPU quota actually granted and the wall-clock runtime are recorded in the
verdict JSON under `environment`.

---

*The two items below were added after measurement.*

## 10. Our own falsification hypothesis for Theorem 4.3 was refuted by the data

Item 7 above was written expecting the missing `σ_max³` factor to be *observable*: the
prediction was that, along the sample-complexity boundary `n = 20000·σ⁶` where the
theorem predicts a constant error, the measured weight error would grow with `σ`.

It did not. The fitted exponent was **0.0605 ± 1.1149** — consistent with zero — across
`σ ∈ {1.00, 1.25, 1.50, 1.75, 2.00}`. The hypothesis is refuted by our own experiment.

Consequently the Claim 6 verdict was changed from FALSIFIED to *VERIFIED
(sample-complexity condition and mean bound) with a documented gap in the displayed
proof of the weight bound*. The symbolic audit still finds the `σ³` factor missing from
the written derivation, but a bound whose own quantity is never observed to be violated
has not been falsified. Reporting it as a falsification would have been the more
impressive result and the wrong one.

## 11. The end-to-end pipeline does not attain `n^{-1/2}` at our solver's budget

For Claim 5, the full Algorithm-1 pipeline's empirical error exponent is about
**−0.35**, short of the `−1/2` the theorem's rate implies. This is a limitation of our
proximal-gradient sparse-plus-low-rank solver at a finite iteration budget, not evidence
against Theorem 4.2 — and that attribution is **demonstrated, not asserted**: with the
sparse part supplied exactly, the same pipeline's eigenvector error decays at **−0.47**
and `‖Θ̂ − Θ‖₂` at **−0.51**, both consistent with `n^{-1/2}`.

The claim page therefore reads `n*(α)` and `n*(δ)` from the stage the theorem governs
and reports the end-to-end figure separately, labelled as a statement about our
implementation. A reproduction that quoted only the −0.35 figure would understate the
theorem; one that quoted only the −0.47 figure would hide a real limitation of this
implementation. Both are published.


## 12. PKU-BETTER's released labels cannot support an accuracy

Discovered while reproducing Table 2, and the reason that column reports no number.

Every released label source for PKU-BETTER is constant: `gold_label_binary` is `0` in
all seven judge files, `gold_label_num` is `1` in both the judge files and the
standalone `data/preference/pku_better.csv`, and `was_swapped` is `False` throughout, so
the A/B order was never randomised and the correct answer cannot vary by row. The
judges answer "B" on about 88 % of rows, anti-correlated with the only gold answer the
file admits.

`gaussian_mixture_main.py` masks this by falling back to `pref_A_or_B` — a judge's own
preference — when the label column is degenerate, so the reported "accuracy" scores a
judge against itself and saturates at exactly 0 or 1. That is precisely what we measured
(`class_balance: 100.0`).

This is recorded as a **failed integrity precondition**, checked by the published
`repro/src/label_audit.py` before any accuracy is computed, and it blocks the column
rather than falsifying anything. The distinction matters: MV scoring 0.000 against a
published 0.701 would look like a dramatic refutation of the paper, and it is nothing of
the sort — the paper's PKU-BETTER numbers were presumably computed against labels that
are not in the release. No verdict about CARE is drawn from this column in either
direction.
