# Source audit — arXiv 2603.00039 (CARE)

| Field | Value |
|---|---|
| Title | CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation |
| Authors | Jitian Zhao, Changho Shin, Tzu-Heng Huang, Satya Sai Srinath Namburi GNVV, Frederic Sala |
| OpenReview | https://openreview.net/forum?id=3WPDFjZ1UT |
| Source retrieved | `https://ar5iv.labs.arxiv.org/html/2603.00039` |
| Retrieved (UTC) | 2026-08-01T04:20:00Z |
| User-Agent | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36` |
| SHA-256 of HTML | `2e733a1609e1dd907dd839b9eed8d9fb7d88549f45d40fafbca7af94ee5e77ea` |
| Bytes | 865,686 |
| Official code | https://github.com/SprocketLab/CARE @ `72f5b29a822d9934d31777c10a5c38369884c9dc` |

Reproduce the fetch and the hash:

```bash
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36" \
  "https://ar5iv.labs.arxiv.org/html/2603.00039" -o ar5iv.html
shasum -a 256 ar5iv.html
```

---

## Anchors, assumptions and exact quantifiers

### Table 1 — MAE, continuous scoring (Section 5.1)

| Method | ASSET | FeedbackQA | Review-5K | Summarize | UltraFeedback | Yelp |
|---|---|---|---|---|---|---|
| MV | 31.153 ± 0.000 | 0.822 ± 0.000 | 2.608 ± 0.000 | 1.417 ± 0.000 | 0.851 ± 0.000 | 0.923 ± 0.000 |
| AVG | 33.663 ± 0.000 | 0.830 ± 0.000 | 2.274 ± 0.000 | 1.394 ± 0.000 | 0.686 ± 0.000 | 1.037 ± 0.000 |
| WS | 29.073 ± 0.436 | 0.793 ± 0.009 | 2.593 ± 0.052 | 1.364 ± 0.007 | 0.829 ± 0.009 | 0.977 ± 0.008 |
| UWS | 33.928 ± 0.000 | 0.875 ± 0.000 | 2.602 ± 0.000 | 1.362 ± 0.000 | 0.680 ± 0.000 | 0.987 ± 0.000 |
| **CARE-SVD** | **27.629 ± 0.156** | **0.730 ± 0.002** | **1.957 ± 0.018** | **1.325 ± 0.004** | **0.623 ± 0.006** | **0.694 ± 0.004** |

### Table 7 — the same quantity, published again (Appendix E.8)

Appendix E.8 ablates which recovered latent factor is used as the quality direction. Its
setup sentence is quoted verbatim because the whole cross-table comparison depends on it:

> We use the same scoring-task setup as in Table 1. Beyond the default heuristic
> (choosing the first factor), we also evaluate all recovered latent factors with
> non-negligible eigenvalues (eigenvalue > 10⁻⁸).

So the **1st Factor** row is CARE-SVD under its default heuristic, on the same six
datasets, under the same metric — a second publication of Table 1's CARE-SVD row.
`–` marks a dataset with no further factor above the 10⁻⁸ eigenvalue floor.

| Factor | ASSET | FeedbackQA | Review-5K | Summarize | UltraFeedback | Yelp |
|---|---|---|---|---|---|---|
| **1st Factor** | **27.148 ± 0.133** | **0.753 ± 0.003** | **1.950 ± 0.006** | **1.325 ± 0.003** | **0.622 ± 0.006** | **0.694 ± 0.005** |
| 2nd Factor | 31.757 ± 0.100 | – | 2.222 ± 0.007 | – | 0.781 ± 0.045 | 1.067 ± 0.062 |
| 3rd Factor | 32.399 ± 0.159 | – | 3.115 ± 0.006 | – | 0.939 ± 0.010 | 0.955 ± 0.023 |
| 4th Factor | 30.529 ± 0.144 | – | 2.667 ± 0.004 | – | 0.996 ± 0.005 | 1.125 ± 0.012 |
| 5th Factor | 31.807 ± 0.170 | – | 3.369 ± 0.004 | – | 1.040 ± 0.062 | 1.099 ± 0.003 |

Compare the bold row here against the bold row of Table 1 above: on **FeedbackQA** and
**ASSET** they are not the same numbers. The audit of that is on
[Claim 1](#/claim-1-ultrafeedback) and [Claim 2](#/claim-2-average-improvement), with its
post-hoc provenance in [Limitations item 24](#/limitations). Appendix E.8's own claim
that the leading factor is best on every dataset is checkable from this table alone and
is checked.

### Table 2 — Accuracy, classification / preference (Section 5.1)

| Method | Chatbot-Arena | CivilComments | PKU-BETTER | PKU-SAFER | SHP | Summarize |
|---|---|---|---|---|---|---|
| MV | 0.517 | 0.691 | 0.701 | 0.698 | 0.626 | 0.600 |
| AVG | 0.551 | 0.690 | 0.726 | 0.717 | 0.634 | 0.683 |
| WS | 0.543 | 0.739 | 0.575 | 0.570 | 0.619 | 0.705 |
| UWS | 0.507 | 0.713 | 0.703 | 0.701 | 0.629 | 0.713 |
| Dawid–Skene | 0.546 | 0.735 | 0.551 | 0.548 | 0.612 | 0.705 |
| GLAD | 0.510 | 0.695 | 0.697 | 0.671 | 0.644 | 0.718 |
| MACE | 0.550 | 0.732 | 0.734 | **0.735** | 0.580 | 0.706 |
| CARE-SVD | **0.580** | **0.778** | 0.691 | 0.690 | 0.543 | 0.695 |
| CARE-Tensor | 0.564 | 0.749 | **0.779** | 0.731 | **0.695** | **0.814** |

### Prose quantifiers (Section 5.1)

> "Specially, it reduces error by up to 26.8% compared to MV on UltraFeedback.
> Averaged across scoring datasets, CARE-SVD yields a 17.37% relative improvement over AVG
> and a 12.75% improvement over MV.
> On classification and preference benchmarks, CARE achieves the best accuracy on 5 of 6 datasets,
> with CARE-Tensor leading on three (PKU-BETTER, SHP, and Summarize), including a 13.4% relative
> improvement in accuracy on Summarize over the strongest baseline."

### Proposition 4.1 (Section 4) — exact wording

> "Assume `K_HH = diag(d_1, …, d_h)` with `d_1 > ⋯ > d_h > 0` and the columns of `K_JH` are
> **orthogonal**. Then the columns of `K_JH` (equivalently, the latent directions encoded by `L`)
> are identifiable from `L` up to sign and permutation. Moreover, if `K_JH` is perturbed to
> `K̃_JH = K_JH + E`, letting `δ_i` denote the eigengap of `L` at eigenvector `u_i`, and `û_i` the
> eigenvector of the estimated low rank matrix `L̂`, then
> `‖û_i − u_i‖₂ ≲ ‖K_HH^{-1}‖₂ ‖E‖₂ / δ_i`  (i ∈ [h])."

**Appendix form.** Assumption D.2 states the columns of `K_JH` are **orthonormal**
(`K_JHᵀ K_JH = I_h`); the proof of Theorem D.3 says explicitly "Under Assumption D.2
*strengthened to orthonormal columns*". Theorem D.4 gives the explicit constant

`‖ũ_i − s_i u_i‖₂ ≤ 4 ‖K_HH^{-1}‖₂ ‖E‖₂ / δ_i + O(‖E‖₂²)`,  `δ_i := min{λ_i, min_{j≠i}|λ_i − λ_j|}`,

and its proof bounds `‖Δ‖₂ ≤ 2‖K_JH‖₂‖K_HH^{-1}‖₂‖E‖₂ + ‖K_HH^{-1}‖₂‖E‖₂²` **and then uses
`‖K_JH‖₂ = 1`, which holds only under orthonormality.**

### Theorem 4.2 (Section 4) = Theorem D.5

> "… for any `η > 0`, with probability at least `1 − 2e^{−η}`,
> `max_{i≤h} ‖û_i − u_i‖₂ = O( sqrt(η/n) · 1/(ξ(T) δ) )."

Proof chain (Appendix D.6): Chandrasekaran et al. (2012) Thm 4.1 gives
`‖L̂_n − L*‖₂ ≤ C₁ sqrt(ε/n)/ξ(T)`; Yu et al. (2015) Thm 2 gives
`‖û_i − u_i‖₂ ≤ 2^{3/2}‖L̂_n − L*‖₂/δ`; composing gives the stated rate, inverted to
`n ≥ 8C₁²η/(ξ(T)²δ²α²)`.

### Theorem 4.3 (Section 4) = Theorem D.9

> "… there exist **universal constants** `C₁, C₂ > 0` such that if
> `n ≥ C₁ σ_max⁶/(δ² π_min²) · p log(p/ε)`, then with probability at least `1 − ε`,
> `max_{q,c} ‖μ̂_qc − μ_qc‖₂ ≤ C₁ (σ_max³/δ) sqrt(p log(p/ε)/n)` and
> `max_{q,c} |π̂_qc − π_qc| ≤ C₂ sqrt(p log(p/ε)/n)."

Proof chain (Appendix D.6): eq. (8) `‖M̂ − M‖_op ≤ C σ_max³ sqrt(p log(p/ε)/n)`;
eq. (10)+(12) mean error `≤ √3 C_dec ‖E‖_op/δ`; eq. (11) weight error `≤ C_π ‖E‖_op`.

### Computing resources declared by the paper (Appendix E.2)

> "We used a server equipped with an NVIDIA A100 (40GB). Generating LLM judge outputs took up to
> 3 hours per dataset."

This is the concrete blocking capability for the eight Table 1 / Table 2 columns whose judge-score
matrices were not released.

---

## What the official repository ships

`SprocketLab/CARE @ 72f5b29` contains `judge_outputs/` for exactly three datasets:

* `judge_outputs/fully_gaussian/asset/` — 11 judge CSVs (Table 1, ASSET)
* `judge_outputs/gaussian_mixture/civilcomments/` — 24 judge CSVs (Table 2, CivilComments)
* `judge_outputs/gaussian_mixture/allenai_preference_test_sets_pku_better.tar.gz` (Table 2, PKU-BETTER)

Its `README.md` documents two run entrypoints, `scripts/fully_gaussian_main.py` (Table 1) and
`scripts/gaussian_mixture_main.py` (Table 2). Both are pure CPU: `torch`/`vllm`/`transformers` are
needed only by `scripts/save_judge_outputs.py`, the judge-generation step.


## Machine-checkable claim contracts

Each claim's contract — its exact statement, anchor, the paper's assumptions, the
condition that decides it, and the criterion that would falsify it — was written
**before** any result was measured and is published verbatim at
[`raw/claim_contract.json`](raw/claim_contract.json). It also records the source URL,
retrieval date, SHA-256 and User-Agent, the pinned official-code SHA, the list of
datasets whose judge-score matrices the authors actually released, and the one fixed
run command.

The method note describing how each contract is turned into an executable check is at
[`raw/method.md`](raw/method.md).
