# Visibility matrix

This table is the evaluator's index. Each row states, for one claim, where the
canonical page is and whether every required item is reachable **from
[the entrypoint](#/index) by following links only** — no repository knowledge, no
unpublished branches, no external logs.

The matrix was filled by downloading the candidate revision into a fresh empty
directory and traversing it blind. Rows are not marked complete on the basis of
knowing where a file lives.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | [Claim 1](#/claim-1-ultrafeedback) | | | | | | | |
| 2 | [Claim 2](#/claim-2-average-improvement) | | | | | | | |
| 3 | [Claim 3](#/claim-3-table2) | | | | | | | |
| 4 | [Claim 4](#/claim-4-proposition-41) | | | | | | | |
| 5 | [Claim 5](#/claim-5-theorem-42) | | | | | | | |
| 6 | [Claim 6](#/claim-6-theorem-43) | | | | | | | |

Column meanings:

* **Code visible** — the executable verifier for this claim is published in this
  Space and linked from the claim page, not merely named.
* **Data inline** — the numbers that decide the claim are printed on the page, not
  only in a download.
* **Raw link** — a downloadable CSV/JSON of the same numbers.
* **Checker** — output of an independent re-derivation by a different route.
* **Control** — a negative control that *fails* for the intended reason, plus
  evidence it actually fails.
* **Exact claim tested** — the page tests the paper's quantified statement, not a
  nearby proxy.

Shared items, reachable from every claim page:
[fixed command, pinned environment, Git SHA, seeds, CPU and runtime](#/environment-and-command);
[raw downloads](#/raw-data); [limitations and deviations](#/limitations);
[source audit with exact quantifiers](#/source-audit).

The verifier [`repro/src/run_all.py`](repro/src/run_all.py) exits nonzero whenever any
claim contract fails; it does not merely report.
