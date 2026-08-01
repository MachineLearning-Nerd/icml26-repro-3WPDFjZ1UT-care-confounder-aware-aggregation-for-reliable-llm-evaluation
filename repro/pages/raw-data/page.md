# Raw data downloads

Every number displayed anywhere in this logbook comes from the single verdict JSON
below, produced by one run of the fixed command. The per-claim CSVs are mechanical
extracts of that same file, so any figure quoted on a claim page can be located in
`verdict.json` and checked against it.

| File | What it contains |
|---|---|
| [`raw/verdict.json`](raw/verdict.json) | Complete output of `uv run python repro/src/run_all.py` — every claim contract, every measured number, the environment record, seeds, runtimes and the independent-checker result |
| [`raw/claim_contract.json`](raw/claim_contract.json) | The six claim contracts, written before any result was measured: exact statement, anchor, assumptions, decision condition, falsification criterion |
| [`raw/source_audit.md`](raw/source_audit.md) | The frozen source audit: paper URL, SHA-256, Tables 1-2, verbatim theorem wording |
| [`raw/method.md`](raw/method.md) | How each contract becomes an executable check |
| [`raw/table1_asset.csv`](raw/table1_asset.csv) | Table 1, ASSET column: per-method MAE reproduced from the authors' released judge-score matrix, per seed and aggregated, next to the published value |
| [`raw/table2.csv`](raw/table2.csv) | Table 2, CivilComments and PKU-BETTER columns: all nine methods, per seed and aggregated, next to the published values |
| [`raw/c4_constant_search.csv`](raw/c4_constant_search.csv) | Claim 4: the attained supremum of the Theorem D.4 ratio per configuration, over the Frobenius and spectral-norm balls |
| [`raw/c5_rate.csv`](raw/c5_rate.csv) | Claim 5: the stage-1 / stage-2 / stage-3 error curves against `n`, and the `n*(alpha)` and `n*(delta)` search results |
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
| [`repro/src/claim_c5_thm42.py`](repro/src/claim_c5_thm42.py) | Claim 5: derivation audit, Davis–Kahan constant search, stage-decomposed rate |
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
authors' data and this Space is text-only — but they are pinned by commit SHA, so
the reproduction is byte-reproducible from the public source.
