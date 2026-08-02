# Claims

The six claim strings below are reproduced **verbatim** from the campaign record and
are the exact statements under test. Each links to the page holding its evidence.

| # | Claim (verbatim) | Verdict | Evidence |
|---|---|---|---|
| 1 | CARE-SVD reduces mean absolute error to 0.623±0.006 versus 0.851±0.000 for majority-vote aggregation on UltraFeedback, a 26.8% error reduction (Table 1). | see page | [Claim 1](#/claim-1-ultrafeedback) |
| 2 | CARE achieves an average 17.37% improvement over simple averaging across continuous-scoring benchmarks (Table 1). | see page | [Claim 2](#/claim-2-average-improvement) |
| 3 | On classification/preference datasets, CARE attains the best accuracy on 5 of 6 datasets, including a 13.4% relative improvement over the baseline on Summarize (0.814±0.001 vs 0.705±0.000) (Table 2). | **FALSIFIED literally** — the explicit pair gives 15.46%; the 5-of-6 conjunct holds | [Claim 3](#/claim-3-table2) |
| 4 | Proposition 4.1 establishes identifiability of latent-judge directions up to sign and permutation under shared confounders, with perturbation stability bounds (Section 4). | **FALSIFIED** (main text) / VERIFIED (appendix) | [Claim 4](#/claim-4-proposition-41) |
| 5 | Theorem 4.2 gives a finite-sample convergence rate of O(√(η/n)·1/(ξ(T)·δ)) for the spectral estimation path used to separate quality from confounders (Section 4). | **FALSIFIED literally** — missing sign alignment and the gap to the zero eigenspace | [Claim 5](#/claim-5-theorem-42) |
| 6 | Theorem 4.3 gives a sample complexity bound n ≳ σ_max^6/(δ²·π_min²)·p·log(p/ε) for recovering the mixture parameters (μ_qc, π_qc) (Section 4). | see page | [Claim 6](#/claim-6-theorem-43) |

Claim contracts — the machine-checkable form of each statement, its assumptions, its
domain and quantifiers, and the criterion that would falsify it — were written
**before** any result was measured and are on
[Source audit and exact quantifiers](#/source-audit). The paper's own wording for
each theorem, including the places where the main text and the appendix differ, is
transcribed there too.

The current generated challenge prompt is authoritative for the claim strings; the paper
and its exact anchors are authoritative for what the cited tables and theorems say. A
disagreement is reported rather than silently resolved. Two such cases are documented on
the relevant claim page:

* Claim 3's "0.705" is not the strongest Table 2 baseline on Summarize (GLAD's 0.718
  is); the claim string's own pair gives 15.46%, while the paper's stated 13.4%
  follows from the correct strongest baseline.
* Claim 4's "Proposition 4.1" exists in two inequivalent forms in the paper. Both
  were tested separately.
