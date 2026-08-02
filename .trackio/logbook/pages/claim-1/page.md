# Claim 1 — UltraFeedback MAE

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_c1_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Claim 1 audit"}
-->
## Literal claim

> CARE-SVD reduces MAE by up to 26.8% on UltraFeedback (`0.623` versus `0.851`).

## Result

**PARTIAL / BLOCKED.** Exact arithmetic gives
`100 × (0.851−0.623)/0.851 = 26.7920%`, matching 26.8% at printed precision.
A second transcription independently agrees. The authors' full CARE-SVD procedure was
rerun for five fixed seeds on ASSET, the only Table 1 dataset whose judge-score matrix
was released, including a row-permutation negative control.

The literal UltraFeedback MAEs cannot be remeasured: the pinned official repository has
no UltraFeedback judge matrix, and Appendix E.2 says regeneration requires GPU inference
over 11–20 LLM judges. This campaign used no GPU and does not substitute a synthetic
matrix.

- [Detailed claim page](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/pages/claim-1-ultrafeedback/page.md)
- [Machine verdict](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/verdict.json)
- [Benchmark implementation](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/claim_c123_benchmarks.py)
- [Official code pin](https://github.com/SprocketLab/CARE/tree/72f5b29a822d9934d31777c10a5c38369884c9dc)
