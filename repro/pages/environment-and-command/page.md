# Fixed command, environment, seeds, runtime

Everything below is what an evaluator needs to re-run this reproduction from
scratch. The full source of every file referenced here is published in this Space
under `repro/`.

## The one run command

```bash
uv run python repro/src/run_all.py
```

This is the single fixed command for every node of the experiment tree, and it produced
every number on Claims 4-6. Two qualifications, both of which an earlier version of this
page omitted:

* It is **not self-contained for Claims 1-3**. Those consume cached benchmark shards
  produced by a separate documented command; see
  [Limitations item 19](#/limitations).
* Two environment variables **are** load-bearing: `CARE_OFFICIAL_DIR` selects the
  authors' pinned checkout, and `CARE_ENTRY` selects the shard entrypoint inside the job
  bootstrap. Neither selects a scientific variant — those live in committed code — but
  the flat claim below was wrong and is corrected here.

Experimental variants
alternate command line. The script exits **1** if any claim contract or the
independent checker fails, and prints the complete verdict JSON to stdout between
`===CARE_VERDICT_BEGIN===` and `===CARE_VERDICT_END===`.

## Bootstrap actually used on Hugging Face

Published here as [`repro/orx/run_hf_job.sh`](repro/orx/run_hf_job.sh):

```bash
BRANCH=main
CARE_SHA=72f5b29a822d9934d31777c10a5c38369884c9dc
REPO=https://github.com/MachineLearning-Nerd/icml26-repro-3WPDFjZ1UT-care-confounder-aware-aggregation-for-reliable-llm-evaluation.git

git clone --depth 1 --branch "$BRANCH" "$REPO" repo && cd repo
git clone --filter=blob:none https://github.com/SprocketLab/CARE.git external/CARE
git -C external/CARE checkout "$CARE_SHA"
export CARE_OFFICIAL_DIR="$PWD/external/CARE"
export PYTHONHASHSEED=0
uv sync --frozen
uv run python repro/src/run_all.py
```

The authors' repository is pinned by SHA, so the judge-score matrices are
byte-identical across runs.

## Pinned environment

`uv` with a committed lockfile; exactly one repository-level `.venv`, reused by
every experiment node. Both inputs are published here as byte-identical copies of the
repository-root files that `uv sync --frozen` actually reads:
[`repro/env/pyproject.toml`](repro/env/pyproject.toml) and
[`repro/env/uv.lock`](repro/env/uv.lock).

<!-- FILL:env.packages -->
*(pending release run)*
<!-- /FILL -->

`torch` is pinned to the CPU wheel index explicitly rather than through
`[tool.uv] torch-backend`, which not every `uv` version honours;
`grep -c nvidia uv.lock` returns **0**.

## Compute

| | |
|---|---|
| Provider | Hugging Face Jobs |
| Flavor requested | `cpu-upgrade` |
| Estimated cores needed beforehand | 4–8 (small dense linear algebra, no BLAS-bound kernels above 40×40; the Table 2 stage is single-threaded in the authors' code) |
| CPU quota actually granted | 8 vCPU (read from `/sys/fs/cgroup/cpu.max` at runtime and recorded in the verdict JSON) |
| RAM | 32 GB |
| Accelerator | none — **no GPU was used at any point** |
| Price | $0.03 / hour |

### Measured cost per stage

Rendered from this run's own `verdict.json`, not typed. An earlier revision typed this
table as prose and it drifted out of agreement with every claim page — which is the
argument for rendering it.

<!-- FILL:env.runtimes -->
*(pending release run)*
<!-- /FILL -->

The benchmark stages are the expensive ones and they run as committed shards rather than
inside the release run; their measured per-shard runtimes and job ids are in
`shard_provenance` in the same file, and the shard costs are: Table 1 ASSET, 5 seeds of
`fully_gaussian_main.py` with a γ-grid of 11 values each, 30–83 s per seed after the
first (the first additionally fetches the authors' ~71 MB judge data); Table 2
CivilComments + PKU-BETTER, 5 seeds of `gaussian_mixture_main.py` over nine methods
including the Dawid–Skene / GLAD / MACE harness, ≈ 112 min per seed.

Table 2 dominates by two orders of magnitude. The per-seed cost is genuine, not an
artefact of thread starvation: each seed must get its **own** `--cache-path`, because
the authors' cache is keyed by dataset rather than by seed, so sharing one cache across
seeds would make seeds 2–5 return seed 1's cached result and silently collapse the
seed-to-seed variation the standard deviations are computed from. Paying five full
fits is the correct choice, and the reason the run takes hours rather than minutes.

The seed count was **not** reduced to shorten the run.

`repro/src/threads.py` is imported before numpy, scipy and torch and pins
`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
`NUMEXPR_NUM_THREADS` and `VECLIB_MAXIMUM_THREADS` to that cgroup quota. Without
it these libraries size their pools from the *host's* core count, and the job runs
20–40× slower through pure thread contention.

## Seeds

| Stage | Seeds |
|---|---|
| Table 1 (ASSET) and Table 2 (CivilComments, PKU-BETTER) | `2024, 2025, 2026, 2027, 2028` — passed to the authors' `--seed`, which drives the validation split and numpy RNG |
| Claim 4 adversarial supremum | `20260801` |
| Claim 4 finite-perturbation sweep | `7`, 400 random models |
| Claim 4 negative controls | `3` |
| Claim 5 Davis–Kahan search | `5`, 4,000 random symmetric perturbations |
| Claim 5 calibrated rate | model seed `4242`, replicate seeds `0…6` |
| Claim 6 model | `20260801`; replicate seeds `0…4` |
| Independent checker | `99` (finite differences) |

`PYTHONHASHSEED=0` is exported in the job, so dictionary-ordering effects cannot
vary between runs.

## Where the numbers come from

Every number displayed anywhere in this logbook is read out of the single verdict
JSON produced by the command above, which is published verbatim at
[`raw/verdict.json`](raw/verdict.json). The per-claim CSV extracts under `raw/`
are derived from that same file.
