# Overview

## CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation

OpenReview: https://openreview.net/forum?id=3WPDFjZ1UT
arXiv: https://arxiv.org/abs/2603.00039
Authors' code: https://github.com/SprocketLab/CARE @ `72f5b29a822d9934d31777c10a5c38369884c9dc`

CARE models a judge-score matrix `X ∈ R^{n×p}` as driven by a latent true-quality
factor `Q` and shared confounders `C`. The observable precision splits as
`Θ = Σ_JJ^{-1} = S − L` with `S` sparse (judge–judge edges) and `L` low-rank
(latent–judge loadings); CARE-SVD reads the quality direction off the leading
eigenvector of `L̂`, and CARE-Tensor recovers a discrete mixture by tensor
decomposition over conditionally independent judge groups.

## What this reproduction does

Six anchored claims, twelve possible points. Three are benchmark claims about
Tables 1–2; three are theorem claims about Section 4.

**The benchmark claims are reproduced on the paper's real benchmarks**, not on
synthetic judges. CARE's aggregation is deterministic linear algebra on a fixed
judge-score matrix, and the authors released those matrices for ASSET (Table 1)
and for CivilComments and PKU-BETTER (Table 2). Those columns are reproduced
end-to-end with the authors' own code over five seeds. For the other eight columns
the authors released no judge scores, and regenerating them needs GPU inference
over 11–20 LLM judges — the paper reports up to 3 hours per dataset on an A100
(Appendix E.2). Those are recorded BLOCKED with that named missing capability.

**The theorem claims are addressed by reconstructing the proofs**, not by fitting a
slope to synthetic data. Theorem D.3's exact-recovery argument is re-derived
symbolically over a parameterised family; Theorem D.4's constant is *derived* (we
prove a strictly tighter first-order constant of 2 in place of 4) and its supremum
is then computed exactly as an operator norm; the Theorem 4.2 and 4.3 proof chains
are recomposed in `sympy` and their cited lemmas independently re-validated. Where
a finite experiment is used it is calibrated by search, never by substituting into
the formula under test.

All research compute ran on Hugging Face `cpu-upgrade` (8 vCPU). No GPU was used, and
no single job exceeded one hour: the benchmark stage is split into 25 shards, the
longest of which took 31 minutes.

## Honesty notes

This reproduction reports two negative results against itself, and one defect it found
in the released data rather than in the paper. A conjectured
falsification of Theorem 4.3's weight bound did not survive measurement, and is
reported as a gap in the written proof rather than as a refutation. The full
Algorithm-1 pipeline's empirical rate falls short of `n^{-1/2}` at our solver's
iteration budget, and that is attributed to the solver rather than to the theorem.
Both are stated in [Limitations and deviations](#/limitations).
