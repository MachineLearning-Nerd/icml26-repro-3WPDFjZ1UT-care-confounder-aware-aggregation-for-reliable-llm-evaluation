# Claim 5 — Theorem 4.2

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_c5_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Claim 5 audit"}
-->
## Result

**FALSIFIED AS LITERALLY STATED.** Three routes decide the statement:

1. At exact recovery, the equally valid eigenvector `−u` gives distance 2 against a
   zero right-hand side because D.5 omits sign alignment. The aligned control is zero.
2. D.5's `δ` excludes the last positive eigenvalue's gap to zero. An exact 2×2 family
   keeps eigenvector error nonzero while the paper-gap rate tends to zero; its violation
   ratio reaches 19,997.3 and diverges symbolically. The corrected full-spectrum gap
   keeps the ratio at 0.9999.
3. Two CARE-compatible Gaussian models make the theorem statistically impossible for
   every estimator: n-sample KL stays below 0.033, so Le Cam forces error with probability
   at least 0.4367, exceeding the theorem's 0.0996 failure budget while its advertised
   rate vanishes.

An independent implementation uses direct 2×2 eigendecomposition and the Gaussian
trace/log-determinant KL formula; it agrees without importing the claim module.

- [Detailed claim page](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/pages/claim-5-theorem-42/page.md)
- [Flat lower-bound evidence](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/c5_rate.csv)
- [Primary implementation](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/claim_c5_thm42.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/independent_check.py)
- [Exact judged-page archive](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/archive/dc8ad3cb/pages/claim-5-theorem-42/page.md)
