"""Run one benchmark shard, small enough to finish inside the one-hour job cap.

    python repro/src/bench_shard.py t1 <seed>
    python repro/src/bench_shard.py t2 <dataset> <seed> <main|baselines>

The full Table 2 reproduction costs ~112 min per seed for both datasets and all nine
methods, which no single job may run. It is therefore split along the axes the authors'
own CLI already exposes -- `--datasets` and `--skip-main` / `--skip-baselines` -- into
shards of roughly half an hour. Sharding changes *where* the work runs, not what is
computed: each shard invokes the same script with the same seed, and every seed keeps
its own `--cache-path`, because the authors' cache is keyed by dataset rather than by
seed and sharing it would silently collapse the seed-to-seed variation.

The result is printed to stdout between markers, because job filesystems are discarded.
Collected shards are committed under `repro/cache/bench/` and consumed by
`claim_c123_benchmarks.py`, so the one fixed run command still produces the canonical
verdict.

A shard that exceeds BUDGET_S aborts and reports the overrun rather than running on:
the job cap is a constraint on this campaign, so breaching it is a result to record,
not an inconvenience to absorb.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import threads  # noqa: F401  - must precede numpy/scipy/torch

import pandas as pd

BEGIN = "===CARE_SHARD_BEGIN==="
END = "===CARE_SHARD_END==="

# The job cap is one hour. Leave room for image pull, uv sync and the git clones.
BUDGET_S = 45 * 60

T2_DATASETS = ("civilcomments", "pku_better")
T2_MAIN_METHODS = ("mv", "avg", "ws", "uws", "care_svd", "care_tensor")
T2_BASELINE_METHODS = ("dawid_skene", "glad", "mace")
T1_METHODS = ("mv", "avg", "ws", "uws", "care_svd")


def _official_root() -> Path:
    env = os.environ.get("CARE_OFFICIAL_DIR")
    for cand in (Path(env) if env else None, Path("external/CARE"), Path("/opt/CARE")):
        if cand and (cand / "scripts").exists():
            return cand
    raise SystemExit("official CARE checkout not found; set CARE_OFFICIAL_DIR")


def _run(root: Path, script: str, args: list[str], budget: float) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{root / 'src'}:{root / 'scripts'}:" + env.get("PYTHONPATH", "")
    try:
        proc = subprocess.run(
            [sys.executable, str(root / "scripts" / script), *args],
            cwd=str(root), env=env, capture_output=True, text=True, timeout=budget,
        )
    except subprocess.TimeoutExpired:
        return 124, f"exceeded shard budget of {budget:.0f}s"
    return proc.returncode, proc.stderr[-2000:]


def shard_t1(seed: int) -> dict:
    root = _official_root()
    d = Path(tempfile.mkdtemp(prefix=f"t1_{seed}_"))
    started = time.time()
    rc, err = _run(
        root, "fully_gaussian_main.py",
        ["--seed", str(seed), "--datasets", "asset", "--output-dir", str(d), "--skip-baselines"],
        BUDGET_S,
    )
    out = {"shard": f"t1:asset:{seed}", "seed": seed, "returncode": rc,
           "runtime_s": round(time.time() - started, 1)}
    csv = d / "fully_gaussian_main.csv"
    if rc != 0 or not csv.exists():
        out["error"] = err or "no output csv"
        return out
    # Long format: one row per method, with columns `pred` and `mae`.
    df = pd.read_csv(csv)
    out["values"] = {
        str(r["pred"]): (None if pd.isna(r["mae"]) else float(r["mae"]))
        for _, r in df.iterrows()
    }
    return out


def shard_t2(dataset: str, seed: int, part: str) -> dict:
    if dataset not in T2_DATASETS:
        raise SystemExit(f"unknown dataset {dataset}; expected one of {T2_DATASETS}")
    if part not in ("main", "baselines"):
        raise SystemExit(f"unknown part {part}; expected main or baselines")
    root = _official_root()
    d = Path(tempfile.mkdtemp(prefix=f"t2_{dataset}_{seed}_{part}_"))
    out_csv, bl_csv = d / "results.csv", d / "baselines.csv"
    args = [
        "--seed", str(seed), "--datasets", dataset,
        "--output", str(out_csv), "--state-dir", str(d / "state"),
        "--cache-path", str(d / "cache.json"), "--baseline-output", str(bl_csv),
    ]
    args += (["--skip-baselines"] if part == "main"
             else ["--skip-main", "--baseline-methods", *T2_BASELINE_METHODS])

    started = time.time()
    rc, err = _run(root, "gaussian_mixture_main.py", args, BUDGET_S)
    out = {"shard": f"t2:{dataset}:{seed}:{part}", "dataset": dataset, "seed": seed,
           "part": part, "returncode": rc, "runtime_s": round(time.time() - started, 1)}

    values = {}
    if part == "main" and out_csv.exists():
        df = pd.read_csv(out_csv)
        for _, r in df.iterrows():
            if str(r["dataset"]) == dataset:
                values = {m: (None if pd.isna(r.get(m)) else float(r.get(m)))
                          for m in T2_MAIN_METHODS}
                # Provenance, and the fields that distinguish a real accuracy from a
                # degenerate split: an accuracy of exactly 0 or 1 usually means the
                # test labels collapsed to one class, not that a method is perfect.
                out["diagnostics"] = {
                    k: (None if pd.isna(r.get(k)) else r.get(k))
                    for k in ("n_examples", "n_judges", "class_balance",
                              "val_size", "test_size", "care_svd_gamma", "val_acc")
                }
    elif part == "baselines" and bl_csv.exists():
        bdf = pd.read_csv(bl_csv)
        for _, r in bdf.iterrows():
            if str(r["dataset"]) == dataset and not pd.isna(r.get("accuracy")):
                values[str(r["method"])] = float(r["accuracy"])

    if rc != 0 or not values:
        out["error"] = err or "no usable output"
    out["values"] = values
    return out


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "t1":
        res = shard_t1(int(argv[1]))
    elif len(argv) >= 4 and argv[0] == "t2":
        res = shard_t2(argv[1], int(argv[2]), argv[3])
    else:
        print(__doc__)
        return 2

    usable = {k: v for k, v in (res.get("values") or {}).items() if v is not None}
    if not usable:
        res.setdefault("error", "shard produced no non-null values")
    res["n_values"] = len(usable)
    res["threads_pinned_to"] = threads.NUM_THREADS
    res["budget_s"] = BUDGET_S
    res["within_budget"] = res["runtime_s"] <= BUDGET_S
    print(BEGIN, flush=True)
    print(json.dumps(res, indent=2, default=str), flush=True)
    print(END, flush=True)
    return 0 if usable and not res.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
