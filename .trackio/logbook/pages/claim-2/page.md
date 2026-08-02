# Claim 2 — average improvement

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_c2_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Claim 2 audit"}
-->
## Literal claim

> CARE improves over averaging methods by 17.37% on average across the six
> continuous-scoring datasets.

## Result

**PARTIAL / BLOCKED, with an exact scope qualification.** Enumerating three natural
definitions shows that only the pooled mean-MAE ratio reproduces both reported
comparisons: **17.3654%** versus AVG and **12.7495%** versus MV. The independent exact
`Fraction` route agrees.

This pooled number is unit-sensitive: ASSET is scored on a 0–100 scale and contributes
84.40% of the denominator, while the other datasets use smaller scales. The
unit-invariant average of per-dataset improvements is 15.19% versus AVG. The published
number is therefore correct under its identifiable pooled definition, but it is not a
scale-free average.

Only ASSET can be rerun from released Table 1 judge outputs; the other five matrices are
absent and `BLOCKED — GPU` under the campaign rules.

- [Detailed claim page](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/pages/claim-2-average-improvement/page.md)
- [Flat Table 1 evidence](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/table1_asset.csv)
- [Decision contract](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/claim_contract.json)
