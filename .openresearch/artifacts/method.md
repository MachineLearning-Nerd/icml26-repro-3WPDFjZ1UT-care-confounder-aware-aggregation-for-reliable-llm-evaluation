# Method

One fixed run command, inherited unchanged by every node of the experiment tree:

```bash
uv run python repro/src/run_all.py
```

All variants live in committed code. Nothing is switched by an environment variable
or an alternate command line. All research compute runs on Hugging Face
`cpu-upgrade` (8 vCPU, 32 GB); the local machine is used only to read and edit the
repository. `repro/src/threads.py` is imported before numpy/scipy/torch and pins
every BLAS/OpenMP pool to the container's real cgroup quota, without which these
jobs run 20–40× slower than they should.

## Claims 1–3 — Tables 1 and 2

CARE's aggregation is deterministic linear algebra on a fixed `n × p` judge-score
matrix. Producing that matrix is the expensive step and the paper reports doing it
on an A100. The authors released the matrices for **ASSET**, **CivilComments** and
**PKU-BETTER** and for nothing else. Two of those three columns are reproduced
end-to-end at full scale with the authors' own code (`scripts/fully_gaussian_main.py`
and `scripts/gaussian_mixture_main.py`, official repo pinned at `72f5b29`), over
five seeds `{2024, 2025, 2026, 2027, 2028}`, with all nine Table 2 methods
(MV, AVG, WS, UWS, Dawid–Skene, GLAD, MACE, CARE-SVD, CARE-Tensor).

Independently, the *arithmetic* content of the three claims — 26.8 %, 17.37 %,
12.75 %, 13.4 %, and "best on 5 of 6" — is decided exactly against the published
tables, including which definition of "average relative improvement" the paper
actually used. This is done twice: once in `claim_c123_benchmarks.py` in floating
point, and once in `independent_check.py` in exact `Fraction` arithmetic against a
separate hand transcription of Table 1.

**Negative control.** Each judge column of the ASSET matrix is independently
row-permuted. This preserves every judge's marginal distribution but destroys the
shared latent structure CARE exploits, so CARE's advantage must disappear. A
control that still passed would show the advantage is not coming from
confounder-aware aggregation.

**Blocked.** UltraFeedback, Summarize, FeedbackQA, Review-5K, Yelp, Chatbot-Arena,
PKU-SAFER and SHP have no released judge-score matrices. Regenerating one costs
11–20 LLM judges (0.6 B–14 B) over 5,000 examples; Appendix E.2 puts that at up to
3 hours per dataset on an A100. GPU spend is not authorised for this campaign, so
those columns are recorded BLOCKED with that exact missing capability rather than
substituted by a synthetic proxy.

## Claim 4 — Proposition 4.1

Finite experiments cannot settle a universally quantified statement, so the route
taken is an independently reconstructed derivation plus assumption-satisfying
counterexamples.

1. **Theorem D.3, symbolically.** `K_JH` is built as the first `h` columns of a
   Householder reflector with a symbolic parameter vector, so `K_JHᵀK_JH = I_h`
   holds as a rational identity rather than at one numeric point. `sympy` then
   proves `L k_i = λ_i k_i` and `rank(L − λ_i I) = p − 1` for `(p,h)` in
   `{(3,2),(4,2),(4,3),(5,3),(6,4)}`.
2. **Theorem D.4's constant, derived not assumed.** Writing `M = [K W]ᵀE`, row `i`
   and column `i` of `M` each have norm ≤ `‖E‖₂`. Cauchy–Schwarz on the exact
   first-order eigenvector perturbation gives
   `ratio² ≤ (1+s)² + (1−s²) ≤ 4` for `s ∈ [0,1]`, i.e. a first-order constant of
   **2**, strictly tighter than the paper's 4. The supremum is then *measured* by
   adversarial optimisation over `E` across six spectra including near-degenerate
   gaps, and separately checked at finite `‖E‖` on 400 random models.
3. **Counterexamples to the main-text restatement.** Proposition 4.1 assumes only
   *orthogonal* columns. With `K_JH = [√2 e₁, e₂]`, `K'_JH = [√2 f₁, f₂]`,
   `f₁ = (e₁+e₂)/√2`, `f₂ = (e₁−e₂)/√2` and `K_HH = diag(2,1)`, both satisfy every
   stated hypothesis and give the same `L = I₂`, yet their columns are not related
   by sign and permutation. Separately, rescaling `K_JH → c K_JH` leaves
   `‖K_HH^{-1}‖₂` fixed, multiplies `δ_i` by `c²` and the true error by `1/c`, so
   the main-text bound is violated by a factor growing linearly in `c` — the
   appendix proof needs the `‖K_JH‖₂` factor that the main text drops.

## Claim 5 — Theorem 4.2

1. **Derivation.** The two cited bounds are composed in `sympy` and checked to
   reproduce both the stated rate and the stated `n ≥ 8C₁²η/(ξ(T)²δ²α²)`.
2. **The cited constant, independently.** 4,000 random symmetric perturbations
   search for a violation of `‖û−u‖ ≤ 2^{3/2}‖Δ‖₂/gap` — the Yu et al. (2015)
   variant the proof invokes — rather than taking it on trust.
3. **Calibrated, non-circular scaling.** Algorithm 1's estimator is implemented
   directly (proximal-gradient sparse-plus-low-rank on the sample precision with a
   PSD projection on `L`, then rank-`h` eigen-decomposition). We *search* for the
   smallest `n` reaching a target accuracy `α`, over a geometric grid and a range
   of `α` and of `δ`, and fit the exponents. No sample size is ever taken from the
   formula under test.

**Negative controls.** (a) Skipping the sparse-plus-low-rank step and
eigen-decomposing the raw precision must stay biased at every `n` — otherwise the
`S+L` step is doing nothing and the check is vacuous. (b) Column-scrambled data
must never recover the directions.

**Limitation.** `ξ(T)` is Chandrasekaran et al.'s curvature constant and has no
closed form we can evaluate, so it is held fixed across each sweep: its `1/ξ(T)`
factor is reconstructed from the derivation, not measured.

## Claim 6 — Theorem 4.3

1. **Derivation.** The paper's own eq. (8), (10)–(12) and (11) are composed in
   `sympy`. Composing (10) with (8) reproduces the stated mean bound exactly.
   Composing (11) with (8) gives `C_π C σ_max³ sqrt(p log(p/ε)/n)`, while the
   theorem states `C₂ sqrt(p log(p/ε)/n)`: a factor of `σ_max³` is missing.
2. **Measurement of the bound's own quantity.** The mixture of Assumption D.8 is
   simulated with `μ`, `π`, `δ`, `p` and `ε` all frozen and only `σ_max` varying,
   with `n` set at the theorem's own threshold `n = n₀ σ_max⁶`. Along that boundary
   the *stated* bound decays like `σ_max^{-3}` while the proof chain predicts a
   `σ`-free error, because the relative perturbation `‖E‖_op/δ` is constant there.
   The recovery uses the algorithm the assumption names — multi-view moments plus
   Anandkumar et al.'s robust tensor power method with deflation — not a nearby
   substitute.
3. **Robustness to the unknown constants.** The violation factor grows like
   `σ_max³` for *any* fixed `C₁, C₂`, so no choice of universal constants rescues
   the stated weight bound.

**Negative controls.** Over-sampling far past the boundary must drive the error
down; freezing `n` while raising `σ_max` must drive it up. Either failing would
mean the measurement is saturated rather than informative.

## Independent checker

`repro/src/independent_check.py` re-derives the load-bearing numbers by different
routes: exact `Fraction` arithmetic on a second transcription of Table 1;
60-digit `mpmath` for the Proposition 4.1 counterexample; central finite
differences against the analytic first-order perturbation formula; and a Theil–Sen
slope for the Theorem 4.3 sweep instead of least squares.

## Exit contract

`run_all.py` exits `1` if any claim contract or the independent checker fails, and
prints the complete verdict JSON to stdout between `===CARE_VERDICT_BEGIN===` and
`===CARE_VERDICT_END===` — job filesystems are discarded on exit, so stdout is the
only durable channel.
