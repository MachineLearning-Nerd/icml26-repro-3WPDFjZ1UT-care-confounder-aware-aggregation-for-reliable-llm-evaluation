# Executive summary

---
<!-- trackio-cell
{"type":"markdown","id":"cell_care_exec_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Executive summary","pinned":true,"pinned_at":"2026-08-02T18:18:28+00:00"}
-->
This candidate audits all six current generated claims for *CARE: Confounder-Aware
Aggregation for Reliable LLM Evaluation* (OpenReview `3WPDFjZ1UT`; arXiv
`2603.00039`). The retained live-judge baseline is **4/12** at Hugging Face
revision `dc8ad3cbfe52bef166c0da1dfcf2c8fec9d01dc5`. Candidate evidence is not an
earned score; only the live judge can change that baseline.

| Claim | Evidence adjudication | Literal result |
| --- | --- | --- |
| 1 | **PARTIAL / BLOCKED** | exact printed reduction and full ASSET method rerun; UltraFeedback judge outputs were not released |
| 2 | **PARTIAL / BLOCKED** | exact pooled statistic and full ASSET method rerun; five Table 1 matrices were not released |
| 3 | **FALSIFIED AS STATED** | `0.814` versus `0.705` gives 15.461%, not 13.4%; the 5-of-6 conjunct holds |
| 4 | **VERIFIED / FALSIFIED BY SCOPE** | appendix proposition verifies with a tighter constant; the weaker main-text wording has exact counterexamples |
| 5 | **FALSIFIED AS STATED** | sign and zero-gap omissions admit exact counterexamples and an estimator-independent Gaussian lower bound |
| 6 | **FALSIFIED (displayed derivation)** | mean bound verifies; the theorem's displayed weight-bound derivation misses the unbounded factor `σ_max³`; no claim is made that a different proof is impossible |

“Falsified as stated” adjudicates the literal generated claim or theorem wording;
it is not a claim that every nearby corrected statement is false.

## Scope and cost

| Route | Scale | Compute | Cost |
| --- | --- | --- | --- |
| Benchmark source contract | official CARE code at `72f5b29`; released real judge matrices | local CPU | $0 |
| Claims 1–3 | exact table arithmetic; full five-seed ASSET and CivilComments reruns | local CPU | $0 |
| Claims 4–6 | symbolic/exact audits, controls, finite-sample probes, Gaussian minimax construction | local CPU | $0 |
| Full clean rerun | fixed entrypoint; all decision contracts and independent checker | **388.34 seconds** | $0 |
| Reproducibility repeat | identical scientific-payload SHA after runtime fields are removed | **391.54 seconds** | $0 |

No GPU, Hugging Face Job, Bucket, model, or dataset repository was used. Missing
benchmark matrices would require regenerating outputs from 11–20 LLM judges and are
therefore marked `BLOCKED — GPU`, not replaced by synthetic proxies.

Primary links:

- [Hugging Face Space](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT)
- [GitHub repository](https://github.com/MachineLearning-Nerd/icml26-repro-3WPDFjZ1UT-care-confounder-aware-aggregation-for-reliable-llm-evaluation)
- [Paper](https://arxiv.org/abs/2603.00039)
- [Official code](https://github.com/SprocketLab/CARE/tree/72f5b29a822d9934d31777c10a5c38369884c9dc)
- [Machine verdict](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/verdict.json)
- [Decision contract](https://huggingface.co/spaces/DineshAI/3WPDFjZ1UT/blob/main/raw/claim_contract.json)

---
<!-- trackio-cell
{"type":"figure","id":"cell_care_poster_20260802","created_at":"2026-08-02T18:18:28+00:00","title":"Reproduction poster","pinned":true,"pinned_at":"2026-08-02T18:18:28+00:00","poster":true}
-->
<iframe src="poster_embed.html" title="CARE six-claim CPU reproduction audit poster" width="100%" height="900" loading="lazy"></iframe>
