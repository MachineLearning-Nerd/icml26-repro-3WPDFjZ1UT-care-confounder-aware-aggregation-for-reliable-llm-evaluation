# Claim 6 — Theorem 4.3

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_c6_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Claim 6 audit"}
-->
## Result

**FALSIFIED AT THE DISPLAYED DERIVATION.** Composing the paper's equations (8) and (10) reproduces the
mean-error bound exactly up to a universal constant. Composing (8) and (11) yields a
weight-error bound larger than the displayed statement by exactly `σ_max³`, an unbounded
factor a universal constant cannot absorb. Two independent routes agree: `sympy` in the
claim implementation and exact exponent-vector arithmetic over rational numbers in the
independent checker.

This falsifies the displayed derivation, not necessarily the weight bound itself. The
finite-sample boundary probe is explicitly inconclusive at the correct Student-t
quantile, and all three sample-complexity exponent sweeps are marked `NOT MEASURED`.
Negative controls show the estimator responds to `n` and `σ`; no result is promoted from
an uninformative sweep.

- [Detailed claim page](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/pages/claim-6-theorem-43/page.md)
- [Flat audit](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/c6_sigma_sweep.csv)
- [Primary implementation](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/claim_c6_thm43.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/independent_check.py)
