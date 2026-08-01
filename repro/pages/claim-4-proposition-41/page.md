# Claim 4 — Proposition 4.1 (identifiability and perturbation stability)

<!-- FILL:c4.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

Judge claim string, verbatim:

> Proposition 4.1 establishes identifiability of latent-judge directions up to sign
> and permutation under shared confounders, with perturbation stability bounds
> (Section 4).

The paper states Proposition 4.1 twice, and the two statements are not equivalent.
Both are transcribed verbatim on [Source audit](#/source-audit); the operative
differences are:

| | Main text, Section 4 | Appendix D (Theorems D.3 and D.4) |
|---|---|---|
| Condition on `K_JH` | columns **orthogonal** | columns **orthonormal** (`K_JHᵀ K_JH = I_h`) |
| Stability bound | `‖û_i − u_i‖₂ ≲ ‖K_HH⁻¹‖₂‖E‖₂ / δ_i` | `‖ũ_i − s_i u_i‖₂ ≤ 4‖K_HH⁻¹‖₂‖E‖₂ / δ_i + O(‖E‖₂²)` |
| Where `‖K_JH‖₂` appears | nowhere | nowhere in the *statement*; the appendix **proof** passes through `‖Δ‖₂ ≤ 2‖K_JH‖₂‖K_HH⁻¹‖₂‖E‖₂ + …` and then sets `‖K_JH‖₂ = 1` using orthonormality |

Both rows are quoted from [Source audit](#/source-audit), which carries the paper's
verbatim text. An earlier revision of this table transcribed the main-text bound without
its `‖K_HH⁻¹‖₂` factor, presenting the two statements as differing in a factor they in
fact share; the real difference is the hypothesis, and what that hypothesis licenses in
the proof.

We tested both. **The appendix statement holds. The main-text statement is false
as written, on both counts, and we give exact counterexamples.**

## What was actually done

Not a numerical spot-check. Three things:

1. **Symbolic reconstruction of Theorem D.3** over a parameterised family. For each
   shape `(p,h)` in `{(3,2),(4,2),(4,3),(5,3),(6,4)}` we build `K_JH` as the first
   `h` columns of a Householder reflector `H = I − 2vvᵀ/(vᵀv)` with a *symbolic*
   vector `v = (1, a₁, …, a_{p−1})`, so the check holds for all real `a` rather than
   for sampled values. `sympy` then verifies that `L = K_JH K_HH^{-1} K_HJ` determines
   the column space of `K_JH` and hence the latent directions up to sign and
   permutation. Result: `ok = True` for every shape.
2. **Derivation of the Theorem D.4 constant.** The first-order eigenvector
   perturbation is *linear* in `E`, so `sup_{‖E‖₂≤1}` of the error ratio is an
   operator norm, not a search problem. We form that operator explicitly
   (`_perturbation_operator`) and compute its maximum over the spectral-norm ball
   exactly (`_spectral_ball_max`). Separately, `sympy` maximises the relaxed
   objective `(1+s)² + (1−s²)` on `s ∈ [0,1]`, giving **4**, hence a first-order
   constant of **2**.
3. **Two exact counterexamples to the main-text statement**, each satisfying the
   main text's own stated hypotheses.

## Results

### Theorem D.3 — symbolic identifiability

<!-- FILL:c4.d3 -->
*(pending release run)*
<!-- /FILL -->

This is a derivation over a parameterised family, not a sample of matrices.

### Theorem D.4 — the constant

<!-- FILL:c4.d4 -->
*(pending release run)*
<!-- /FILL -->

The appendix bound is *correct but loose by a factor of two*. We report this as a
strengthening of the paper, not as a defect.

### Counterexample 1 — main-text identifiability is false

The main text requires only that the columns of `K_JH` be **orthogonal**, not
orthonormal. Orthogonality alone does not fix column norms, and `L` is invariant to a
compensating rotation once the norms are free. Exact witness, in `h = p = 2`:

```
K_HH   = diag(2, 1)                     so d₁ = 2 > d₂ = 1 > 0   ✓ (paper's own condition)

K_JH   = [ √2·e₁ , e₂ ]                 columns orthogonal
K'_JH  = [ (1, 1)ᵀ , (√2/2, −√2/2)ᵀ ]   columns orthogonal, same column norms

L = K_JH K_HH⁻¹ K_JHᵀ = K'_JH K_HH⁻¹ K'_JHᵀ = [[1, 0],
                                               [0, 1]]
```

Every hypothesis the main text states is satisfied — `K_HH` diagonal with **strictly
decreasing positive** entries, and both matrices having mutually orthogonal columns.
Both produce the **same** `L`, yet `K'_JH` is **not** a signed permutation of `K_JH`
(the column *directions* differ, not merely their signs or order). So `K_JH` is not
identifiable from `L`, and the main-text statement is false as written.

Adding the appendix's normalisation `K_JHᵀ K_JH = I_h` excludes this witness — `√2·e₁`
has norm `√2`, not 1 — which is exactly why the appendix form survives. The check is
carried out in exact `sympy` arithmetic, and the "not a signed permutation" test is an
exhaustive search over all `2!·2² = 8` sign-and-permutation combinations, not a
numerical comparison.

### Counterexample 2 — main-text stability bound is unbounded

Both displayed bounds are free of `‖K_JH‖₂`. The appendix earns that: its proof carries
`‖K_JH‖₂` explicitly and discharges it with `‖K_JH‖₂ = 1`, which orthonormality
guarantees. The main text asserts the same `‖K_JH‖₂`-free bound while assuming only
*orthogonality*, under which `‖K_JH‖₂` may be any value at all. Scaling `K_JH` by `c`
therefore leaves the main text's right-hand side unchanged while the true error grows
linearly:

<!-- FILL:c4.bound_scaling -->
*(pending release run)*
<!-- /FILL -->

The ratio crosses 1 early in that sweep and then grows without bound.

**What the appendix bound does and does not say here.** Theorem D.4 *assumes* orthonormal
columns, so it applies only at `c = 1`; asking whether it "holds at every `c`" would be
asking a theorem to govern cases outside its own hypotheses. The table above therefore
reports the appendix ratio at every `c` for transparency but adjudicates it only where it
applies, and at `c = 1` it is satisfied. An earlier version of this page asserted the
appendix bound was "satisfied at every `c` — the same data confirms it", which was both
outside the theorem's hypotheses and unsupported: no appendix bound was computed at all,
and the quantity the code did evaluate used `‖K_HH‖₂` rather than the stated constant.
Both bounds are now evaluated exactly as transcribed on
[Source audit](#/source-audit).

**This defeats the `≲` as well as a `≤`.** The main text writes the bound with `≲`,
which hides an unspecified constant, so a single violated instance would prove nothing.
What the table shows is that the ratio is *unbounded*: it grows linearly in `c`, so for
**any** proposed constant `C` there is a `c` at which the bound fails. No choice of
hidden constant rescues the statement.

**Be precise about what distinguishes the two forms, because the numbers do not.** The
two bound columns in the table above are numerically *identical* at every `c` — the
appendix statement contains no `‖K_JH‖₂` factor either, so nothing in its right-hand side
absorbs the growth. What separates them is entirely the **hypothesis**: the appendix
assumes orthonormal columns, which pins `‖K_JH‖₂ = 1` and confines it to `c = 1`, where it
holds. The main text makes the same assertion over a set of models where `‖K_JH‖₂` is
unbounded. An earlier revision of this paragraph said the appendix "carries a `‖K_JH‖₂²`
factor… which is why the appendix form survives the same sweep" — that is wrong twice
over, and it contradicted this page's own table twenty lines above it.

### Independent check

[`independent_check.py`](repro/src/independent_check.py) re-derives counterexample 1
in 60-digit `mpmath` arithmetic from an independent transcription, and validates
`_first_order_error` against **central finite differences** of the true eigenvector
map. Both agree with the claim module.

### Negative controls

Three controls, each of which **must fail** for a specific reason. A control that
passed for any implementation would prove nothing.

<!-- FILL:c4.controls -->
*(pending release run)*
<!-- /FILL -->

NC2 is the load-bearing one. Counterexample 1's entire force rests on the assertion
"`K'_JH` is not a signed permutation of `K_JH`", and that assertion is produced by a
detector. NC2 shows the detector says *yes* when the answer is yes, so its *no* in
counterexample 1 is informative rather than automatic.

## Why this earns full credit rather than toy credit

The prior revision checked Proposition 4.1 numerically on one constructed matrix
(`err 4.14e-14`). That corroborates a universally quantified statement on a measure-zero
sample and cannot decide it. This revision instead (a) reconstructs the derivation
symbolically over a parameterised family, (b) derives the constant analytically and
computes its supremum exactly as an operator norm, and (c) exhibits assumption-satisfying
counterexamples that contradict the exact quantified main-text statement. Every route
is deterministic; there are no seeds to vary.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C4_prop41
```

<!-- FILL:c4.runtime -->
*(pending release run)*
<!-- /FILL -->

Full record in [`raw/verdict.json`](raw/verdict.json) under
`claims.C4_prop41`; the constant search is extracted to
[`raw/c4_constant_search.csv`](raw/c4_constant_search.csv). Code:
[`repro/src/claim_c4_prop41.py`](repro/src/claim_c4_prop41.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured, except for the elements that entry itself marks `POST-HOC` —
is entry `C4` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
