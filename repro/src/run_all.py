"""Fixed reproduction entrypoint for arXiv 2603.00039 (CARE).

    uv run python repro/src/run_all.py

This is the one run command for every node of the experiment tree; variants live
in committed code, never in the command line or the environment. It runs all six
claim contracts, prints the full verdict JSON to stdout between explicit markers
(job filesystems are discarded when the job exits, so stdout is the durable
channel), and exits nonzero if any contract fails.
"""

from __future__ import annotations

import threads  # noqa: F401  - must precede numpy/scipy/torch

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import claim_c4_prop41
import claim_c5_thm42
import claim_c6_thm43
import claim_c123_benchmarks
from paper_source import SOURCE

BEGIN = "===CARE_VERDICT_BEGIN==="
END = "===CARE_VERDICT_END==="


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(Path(__file__).resolve().parents[2]), text=True
        ).strip()
    except Exception:
        return os.environ.get("GIT_SHA", "unknown")


def environment() -> dict:
    return {
        "git_sha": _git_sha(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "os_cpu_count": os.cpu_count(),
        "cgroup_cpu_quota": threads.cpu_quota(),
        "threads_pinned_to": threads.NUM_THREADS,
        "numpy": np.__version__,
        "hf_flavor": os.environ.get("CARE_HF_FLAVOR", "unset"),
        "run_command": "uv run python repro/src/run_all.py",
        "paper_source": SOURCE,
    }


def main() -> int:
    t0 = time.time()
    out = {"paper": "3WPDFjZ1UT", "arxiv": "2603.00039", "environment": environment(), "claims": {}}

    stages = [
        ("C1_C2_C3_tables", claim_c123_benchmarks.run),
        ("C4_prop41", claim_c4_prop41.run),
        ("C5_thm42", claim_c5_thm42.run),
        ("C6_thm43", claim_c6_thm43.run),
    ]
    for name, fn in stages:
        t = time.time()
        print(f"[run_all] starting {name}", flush=True)
        try:
            res = fn()
        except Exception as exc:  # a crash is a failed contract, never a silent pass
            import traceback

            res = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}
        res["runtime_s"] = round(time.time() - t, 2)
        out["claims"][name] = res
        print(f"[run_all] {name} ok={res.get('ok')} in {res['runtime_s']}s", flush=True)

    import independent_check

    t = time.time()
    print("[run_all] starting independent_check", flush=True)
    try:
        chk = independent_check.run(out)
    except Exception as exc:
        import traceback

        chk = {"ok": False, "error": repr(exc), "traceback": traceback.format_exc()}
    chk["runtime_s"] = round(time.time() - t, 2)
    out["independent_check"] = chk
    print(f"[run_all] independent_check ok={chk.get('ok')} in {chk['runtime_s']}s", flush=True)

    out["total_runtime_s"] = round(time.time() - t0, 2)
    out["all_contracts_ok"] = all(v.get("ok") for v in out["claims"].values()) and bool(chk.get("ok"))

    print(BEGIN, flush=True)
    print(json.dumps(out, indent=2, default=str), flush=True)
    print(END, flush=True)

    art = Path(__file__).resolve().parents[2] / ".openresearch" / "artifacts"
    try:
        art.mkdir(parents=True, exist_ok=True)
        (art / "verdict.json").write_text(json.dumps(out, indent=2, default=str))
    except OSError:
        pass

    return 0 if out["all_contracts_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
