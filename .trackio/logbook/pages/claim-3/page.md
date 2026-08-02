# Claim 3 — Table 2

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_c3_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Claim 3 audit"}
-->
## Literal claim

> CARE achieves the best accuracy on five of six datasets, including a 13.4%
> relative improvement on Summarize (`0.814` versus `0.705`).

## Result

**FALSIFIED AS STATED.** The generated claim is a conjunction. Its 5-of-6 component
is true, but its explicit numerical component is false:

```text
(0.814 − 0.705) / 0.705 = 15.460993%, not 13.4%.
```

The nearby paper prose uses the actual strongest Summarize baseline, GLAD at `0.718`:
`(0.814−0.718)/0.718 = 13.370474%`, which rounds to 13.4%. Replacing only the generated
claim's wrong baseline repairs the arithmetic; keeping `0.705` is a fail-closed negative
control. Two independently typed 54-cell Table 2 transcriptions agree cell by cell.

- [Detailed claim page](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/pages/claim-3-table2/page.md)
- [Literal arithmetic audit](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/c3_literal_audit.csv)
- [Claim implementation](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/repro/src/claim_c123_benchmarks.py)
- [Exact judged-page archive](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/archive/dc8ad3cb/pages/claim-3-table2/page.md)
