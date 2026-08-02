# Raw data downloads

Every number displayed anywhere in this logbook comes from the single verdict JSON
below, produced by one run of the fixed command. The per-claim CSVs are mechanical
extracts of that same file, so any figure quoted on a claim page can be located in
`verdict.json` and checked against it.

| File | What it contains |
|---|---|
| [`raw/verdict.json`](raw/verdict.json) | Complete output of `uv run python repro/src/run_all.py` — every claim contract, every measured number, the environment record, seeds, runtimes and the independent-checker result |
| [`raw/claim_contract.json`](raw/claim_contract.json) | The six claim contracts: exact statement, anchor, assumptions, decision condition, falsification criterion. Written before any result was measured **except** for the four elements the file itself marks `POST-HOC` — C1 and C2's Table 1 vs Table 7 audits, C2's unit-invariance criterion, and C6's `p` criterion — each of which carries a `provenance` string saying when it was added and why |
| [`raw/source_audit.md`](raw/source_audit.md) | The frozen source audit: paper URL, SHA-256, Tables 1-2, verbatim theorem wording |
| [`raw/method.md`](raw/method.md) | How each contract becomes an executable check |
| [`raw/table1_asset.csv`](raw/table1_asset.csv) | Table 1, ASSET column: per-method MAE reproduced from the authors' released judge-score matrix, per seed and aggregated, next to the published value |
| [`raw/table2.csv`](raw/table2.csv) | Table 2, CivilComments and PKU-BETTER columns: all nine methods, per seed and aggregated, next to the published values |
| [`raw/c3_literal_audit.csv`](raw/c3_literal_audit.csv) | Claim 3: exact generated-pair decision and independent second-transcription controls |
| [`raw/c4_constant_search.csv`](raw/c4_constant_search.csv) | Claim 4: the attained supremum of the Theorem D.4 ratio per configuration, over the Frobenius and spectral-norm balls |
| [`raw/c5_rate.csv`](raw/c5_rate.csv) | Claim 5: literal sign/eigengap/Gaussian lower-bound evidence plus the preserved `n*(delta)` sweep, Davis-Kahan constant search, and independent rechecks. Full nested records remain in [`raw/verdict.json`](raw/verdict.json) |
| [`raw/c6_sigma_sweep.csv`](raw/c6_sigma_sweep.csv) | Claim 6: `n*` against `sigma_max`, `pi_min` and `p log(p/eps)`, plus the boundary probe of the weight bound |

## Source code

The complete verifier is published in this Space and is the same code that
produced `verdict.json`:

| File | Role |
|---|---|
| [`repro/src/run_all.py`](repro/src/run_all.py) | The fixed entrypoint; exits nonzero when any contract fails |
| [`repro/src/paper_source.py`](repro/src/paper_source.py) | Frozen transcription of Tables 1–2 and the prose quantifiers, plus the source SHA-256 |
| [`repro/src/claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py) | Claims 1–3: benchmark reproduction, table arithmetic, coverage audit, negative control |
| [`repro/src/claim_c4_prop41.py`](repro/src/claim_c4_prop41.py) | Claim 4: symbolic Theorem D.3, the exact Theorem D.4 constant, and the two counterexamples |
| [`repro/src/claim_c5_thm42.py`](repro/src/claim_c5_thm42.py) | Claim 5: literal sign/eigengap counterexamples, Gaussian lower bound, derivation audit, and preserved stage-decomposed rate |
| [`repro/src/claim_c6_thm43.py`](repro/src/claim_c6_thm43.py) | Claim 6: derivation audit, calibrated sample-complexity sweeps, boundary probe |
| [`repro/src/tensor_mom.py`](repro/src/tensor_mom.py) | Multi-view moments and the robust tensor power method of Anandkumar et al. (2014) |
| [`repro/src/independent_check.py`](repro/src/independent_check.py) | Independent checker — different routes for the same numbers |
| [`repro/src/threads.py`](repro/src/threads.py) | cgroup-aware thread pinning |
| [`repro/orx/run_hf_job.sh`](repro/orx/run_hf_job.sh) | The exact Hugging Face job bootstrap |
| [`repro/env/pyproject.toml`](repro/env/pyproject.toml), [`repro/env/uv.lock`](repro/env/uv.lock) | The pinned environment |

## External inputs

| Input | Pin |
|---|---|
| Paper source | `https://ar5iv.labs.arxiv.org/html/2603.00039`, SHA-256 `2e733a1609e1dd907dd839b9eed8d9fb7d88549f45d40fafbca7af94ee5e77ea` |
| Authors' code and judge-score matrices | `https://github.com/SprocketLab/CARE` @ `72f5b29a822d9934d31777c10a5c38369884c9dc` |

The judge-score CSVs are not copied into this Space — they are ~71 MB of the
authors' data and this Space is text-only — but they are pinned by commit SHA, so the
reproduction is byte-reproducible **from the public source, with network access**.

**Exactly how far an offline reader can get, stated plainly.** Every pin above is a
promise this artifact cannot keep on its own:

| Pin | Checkable from inside this Space? |
|---|---|
| Paper SHA-256 | **No** — the ar5iv HTML is not shipped. The table transcriptions are checkable against each other (`paper_source.py` versus the second, hand-typed copy in `independent_check.py`), not against the paper. |
| Authors' code SHA | **No** — checked at run time against a checkout that is not in this Space; the result is recorded as `official_repo_sha_matches_pin`. |
| `environment.git_sha` | **No** — there is no `.git` here. What *is* checked, at publication time, is that every `repro/src/*.py` file uploaded is byte-identical to the same path at that SHA; the gate is [`repro/publish/publish_space.py`](repro/publish/publish_space.py) and it refuses the upload on any drift. That makes the SHA a claim about *this* file set rather than an unattached string, but it is still not verifiable offline. |
| Shard `hf_job_id`s and their SHA | **No** — job records live on Hugging Face. |
| `repro/cache/bench/*.json` | **Yes** for ASSET and CivilComments — the benchmark shard outputs are shipped and **linked below**, so those Table 1/2 numbers can be traced to the JSON they came from. **Not** for PKU-BETTER, which has no shard because the label precondition blocks it before any accuracy is computed. Below that layer, the authors' judge CSVs are the boundary. |

Anything marked **No** should be read as asserted. That is a real limit on what a
network-isolated reviewer can conclude, and no amount of internal consistency substitutes
for it.


## The shard files themselves

A blind reviewer pointed out that the row above offered these files as the artifact's
one independently checkable layer while **no page linked to any of them** — so a reviewer
following the "links only" rule this logbook sets for itself could not reach the evidence
it was being pointed at. Every shard is listed here.

Each file records the seed, the per-method values, its own wall-clock runtime, the Git SHA
it ran at and its Hugging Face job id. `verdict.json`'s `per_seed` blocks are read back
from exactly these files, so any Table 1 or Table 2 per-seed number can be checked against
its shard directly.

| Shard file | Contents |
|---|---|
| [`t1-2024.json`](repro/cache/bench/t1-2024.json) | shard `t1-2024` |
| [`t1-2025.json`](repro/cache/bench/t1-2025.json) | shard `t1-2025` |
| [`t1-2026.json`](repro/cache/bench/t1-2026.json) | shard `t1-2026` |
| [`t1-2027.json`](repro/cache/bench/t1-2027.json) | shard `t1-2027` |
| [`t1-2028.json`](repro/cache/bench/t1-2028.json) | shard `t1-2028` |
| [`t2-civilcomments-2024-baselines.json`](repro/cache/bench/t2-civilcomments-2024-baselines.json) | shard `t2-civilcomments-2024-baselines` |
| [`t2-civilcomments-2024-main.json`](repro/cache/bench/t2-civilcomments-2024-main.json) | shard `t2-civilcomments-2024-main` |
| [`t2-civilcomments-2025-baselines.json`](repro/cache/bench/t2-civilcomments-2025-baselines.json) | shard `t2-civilcomments-2025-baselines` |
| [`t2-civilcomments-2025-main.json`](repro/cache/bench/t2-civilcomments-2025-main.json) | shard `t2-civilcomments-2025-main` |
| [`t2-civilcomments-2026-baselines.json`](repro/cache/bench/t2-civilcomments-2026-baselines.json) | shard `t2-civilcomments-2026-baselines` |
| [`t2-civilcomments-2026-main.json`](repro/cache/bench/t2-civilcomments-2026-main.json) | shard `t2-civilcomments-2026-main` |
| [`t2-civilcomments-2027-baselines.json`](repro/cache/bench/t2-civilcomments-2027-baselines.json) | shard `t2-civilcomments-2027-baselines` |
| [`t2-civilcomments-2027-main.json`](repro/cache/bench/t2-civilcomments-2027-main.json) | shard `t2-civilcomments-2027-main` |
| [`t2-civilcomments-2028-baselines.json`](repro/cache/bench/t2-civilcomments-2028-baselines.json) | shard `t2-civilcomments-2028-baselines` |
| [`t2-civilcomments-2028-main.json`](repro/cache/bench/t2-civilcomments-2028-main.json) | shard `t2-civilcomments-2028-main` |

There is no PKU-BETTER shard. That is not an omission: `label_audit.py` runs before any
accuracy is computed and blocks the column, so no shard was ever produced to ship.
