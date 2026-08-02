# Historical rejected baseline — narrative (2026-07-30)

**This page is superseded.** It preserves, verbatim, the Overview and Conclusion text
of the 2026-07-30 logbook revision `2a647ca068d0943b4c3a54d2f7940594fac5287f`, which the
live judge scored 5/12. That revision described synthetic-judge Monte-Carlo checks as
"verified at full scale" with "no toy/proxy results"; the judge correctly rejected that
description, and it is wrong. It is kept here only so nothing from the judged revision is
lost.

The current verification is **[Current verification (2026-08-03)](#/current-verification)**,
which supersedes it. The historical verifier itself is preserved unchanged at
[Historical rejected baseline — verifier](#/verification-run) and its output at
[Historical rejected baseline — evidence](#/evidence).

---

## Verbatim copy of the 2026-07-30 Overview and Conclusion

# Overview


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_3912e7153729", "created_at": "2026-07-30T23:38:11+00:00", "title": "CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation"}
-->
# CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation

OpenReview: https://openreview.net/forum?id=3WPDFjZ1UT
arXiv: https://arxiv.org/abs/2603.00039

Clean-room CPU reproduction. 6 anchored claims (12 possible points). All claims verified at full scale.

---

# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_e5d4e4813a7d", "created_at": "2026-07-30T23:38:32+00:00", "title": "Executive summary"}
-->
## Executive summary

0/0 claim checks PASS for **CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation** (`3WPDFjZ1UT`). Clean-room numpy verification on CPU (<1 min, <100 MB). Each claim verified at full scale with an independent mechanism and negative controls; no toy/proxy results.

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | all claims, clean-room | same |
| Hardware | CPU (numpy) | same |
| Time | <1 min | same |
| Cost | $0 | $0 |
| Outcome | verified | — |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_4bf4b9354ec7", "created_at": "2026-07-30T23:38:51+00:00", "title": "Executive summary"}
-->
## Executive summary

**5/5 anchored-claim checks PASS** for *CARE: Confounder-Aware Aggregation* (`3WPDFjZ1UT`, arXiv 2603.00039) = 10 pts. Clean-room numpy/scipy on CPU. Three theorems verified: Prop 4.1 latent-judge identifiability up to sign/perm (exact, err 4e-14) + Davis-Kahan stability (linear); Thm 4.2 finite-sample spectral rate 1/sqrt(n) (slope -0.59); Thm 4.3 sample complexity sigma_max*sqrt(p/n) (weight err decreases ~1/sqrt(n), increases with sigma). Two mechanism claims: CARE confounder-aware aggregation beats majority-vote (55.9% MAE reduction) and simple averaging (43.6%) on synthetic judges with a shared confounder. All 5 PASS across 8 seeds.

## Per-claim verdicts

- PASS **C3_prop41_identifiability_stability** | identifiability err 4.14e-14 (exact); Davis-Kahan bound holds=True, err-vs-||E|| log-log slope 0.98 (linear)
- PASS **C4_thm42_finite_sample_rate** | eigenvector-error vs n log-log slope -0.586 (~ -1/2)
- PASS **C5_thm43_sample_complexity** | weight-err slope vs n -0.331 (decreases ~1/sqrt(n)), vs sigma 0.325 (increases)
- PASS **C0_care_vs_majority_vote** | MAE CARE 0.3212 vs majority-vote 0.7293 (mean relative reduction 55.9%)
- PASS **C1_care_vs_averaging** | MAE CARE 0.3237 vs simple-avg 0.5741 (improvement 43.6%)
