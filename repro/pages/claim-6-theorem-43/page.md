# Claim 6 — Theorem 4.3 (sample complexity for mixture recovery)

<!-- FILL:c6.header -->
*(pending release run)*
<!-- /FILL -->

## The exact claim

> Theorem 4.3 gives a sample complexity bound n ≳ σ_max^6/(δ²·π_min²)·p·log(p/ε) for
> recovering the mixture parameters (μ_qc, π_qc) (Section 4).

The paper's verbatim statement, including the separate displayed bounds for the mean
error and the weight error, is on [Source audit](#/source-audit).

## What was tested, and one hypothesis that failed

Theorem 4.3 has two parts: a **sample-complexity condition** and, under it, error
bounds on the recovered means `μ_qc` and weights `π_qc`. Both were examined.

While auditing the displayed proof we formed a specific falsification hypothesis: that
the stated weight bound **drops a factor of `σ³`**, and that consequently the weight
error would grow with `σ` along the sample-complexity boundary where the theorem
predicts it constant. The symbolic audit did find the missing factor:

<!-- FILL:c6.symbolic -->
*(pending release run)*
<!-- /FILL -->

**But the experiment refuted the consequence.** Along the boundary `n = 20000·σ⁶` the
measured weight error did not grow:

<!-- FILL:c6.boundary -->
*(pending release run)*
<!-- /FILL -->

The honest reading is therefore **not** a falsification. The theorem's *statement* is
not contradicted by any measurement we could make; what is defective is the *displayed
derivation*, which loses a `σ³` factor that the stated result nonetheless survives. We
report this as a documented gap in the written proof and record the verdict as
**VERIFIED (sample-complexity condition and mean bound) with a documented gap in the
displayed proof of the weight bound**.

This is recorded here rather than quietly dropped because a reproduction that only
reports confirmations of its own hypotheses is not measuring anything. It is also the
reason the claim is *not* reported as FALSIFIED: a bound whose own quantity is never
observed to be violated has not been falsified, however flawed its derivation.

## Calibrated sample-complexity measurement

The claim is a statement about **exponents**, so each parameter is swept independently
and `n*` — the sample size at which the parameter error first falls below
`TARGET = 0.05` — is located by search over a geometric grid
`n ∈ {200, 500, 1 250, 3 125, 5 000, 12 500, 31 250, 78 125, 195 312, 488 281, 1 220 703}`.
No sample size is computed from the formula under test.

Because the theorem is a sufficient condition (`n ≳ …`), each contract is **one-sided**:
the measured exponent must not *exceed* what the theorem requires.

| Parameter | Stated exponent | Contract |
|---|---|---|
| `σ_max` | 6 | measured `≤ 6 + 2·stderr` |
| `π_min` | −2 | measured `≥ −2 − 2·stderr` |
| `p·log(p/ε)` | 1 | measured `≤ 1 + 2·stderr` |

### Why a one-sided contract needs an informativeness precondition

A one-sided contract is satisfied by any sweep that does not *exceed* the stated
exponent — including a sweep that measured nothing at all. An earlier revision of this
page fell into exactly that trap: with the grid floor at `n = 5 000`, every `π_min`
setting returned `n* = 5 000` because the error was already below target at the first
grid point. The fitted exponent was `0.000 ± 0.000`, the contract `≥ −2` passed, and the
number was a property of the grid rather than of the estimator.

[`repro/src/informativeness.py`](repro/src/informativeness.py) now makes that
undetectable-by-reading condition machine-checkable. A sweep is admissible as evidence
only if it has ≥ 3 usable points, ≥ 3 *distinct* values of `n*`, no pinning of every
`n*` to a grid endpoint, and a fitted trend whose 95 % interval excludes zero. A sweep
failing any of these is reported **NOT INFORMATIVE**, contributes nothing in either
direction, and is excluded from the verdict — rather than passing because it failed to
disagree. The grid was also extended down to `n = 200` so the `π_min` search is no
longer censored from below.

### Results

<!-- FILL:c6.results -->
*(pending release run)*
<!-- /FILL -->

## The algorithm actually implemented

The claim names tensor-decomposition recovery, so
[`repro/src/tensor_mom.py`](repro/src/tensor_mom.py) implements the method the theorem
is about — multi-view method of moments with symmetrisation
(`A₁ = M₃₂ M₁₂⁺`, `A₂ = M₃₁ M₂₁⁺`), whitening `W = U diag(s^{-1/2})`, and the **robust
tensor power method** of Anandkumar et al. (2014) with 30 restarts, 60 iterations and 30
deflation iterations — not a convenient substitute such as EM or `k`-means.

Model: `K = 4` components with weights `(0.40, 0.30, 0.20, 0.10)`, three conditionally
independent views of 6 judges each (`p = 18`), component means drawn from QR-orthonormal
frames scaled by 3.0.

## Negative controls

| | Control | Contract it must satisfy |
|---|---|---|
| NC1 | Over-sample far past the boundary, `n = 20 000 × {1, 16, 128}`, everything else frozen | error at `128×` must be **strictly below** the error at `1×` |
| NC2 | Freeze `n = 20 000` and raise `σ ∈ {1.0, 2.0, 3.0}` | error at `σ = 3` must be **strictly above** the error at `σ = 1` |

Measured:

<!-- FILL:c6.controls -->
*(pending release run)*
<!-- /FILL -->

Both are medians over three seeds. NC2 is the discriminating one: it fails exactly when
the `σ`-dependence the theorem asserts is genuinely present in the estimator. Had NC2
been flat, the σ-sweep in the boundary probe above would have been measuring nothing,
and the null result reported there would have been uninformative rather than evidence.

## Independent check

[`independent_check.py`](repro/src/independent_check.py) refits every sweep with a
**Theil–Sen** estimator rather than least squares and re-derives the boundary algebra by
an independent symbolic route, then cross-checks agreement with the claim module.

## Reproduce

```
uv run python repro/src/run_all.py      # runs this claim as stage C6_thm43
```

Runtime 331.3 s on Hugging Face `cpu-upgrade` (8 vCPU / 32 GB), threads pinned to the
cgroup quota. Record: [`raw/verdict.json`](raw/verdict.json) under `claims.C6_thm43`;
extract [`raw/c6_sigma_sweep.csv`](raw/c6_sigma_sweep.csv). Code:
[`repro/src/claim_c6_thm43.py`](repro/src/claim_c6_thm43.py).

## Contract

This claim's machine-checkable contract — written **before** any result was measured —
is entry `C6` of [`raw/claim_contract.json`](raw/claim_contract.json): the exact
statement, its anchor in the paper, the paper's own assumptions, the condition that
decides it, and the criterion that would falsify it. The paper's verbatim wording and
exact quantifiers are on [Source audit](#/source-audit); what is and is not covered is
on [Limitations and deviations](#/limitations).
