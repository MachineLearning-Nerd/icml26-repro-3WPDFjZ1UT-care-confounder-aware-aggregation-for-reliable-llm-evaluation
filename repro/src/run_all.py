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

import base64
import hashlib
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


def _run_input_sha256() -> str:
    """Hash every code/cache byte used by the fixed entrypoint."""
    root = Path(__file__).resolve().parents[2]
    paths = list((root / "repro" / "src").rglob("*.py"))
    paths += [p for p in (root / "repro" / "cache").rglob("*") if p.is_file()]
    paths += [root / "pyproject.toml", root / "uv.lock"]
    digest = hashlib.sha256()
    for path in sorted((p for p in paths if p.exists()), key=lambda p: str(p.relative_to(root))):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def environment() -> dict:
    return {
        "git_sha": _git_sha(),
        "run_input_sha256": _run_input_sha256(),
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


def seed_record() -> dict:
    """The seeds table, read out of the code rather than typed onto a page.

    A blind reviewer found the published seeds table understating Claim 6's main sweeps
    by 4x: it said `0...4` where `sample_complexity_sweeps` runs 21 seeds. Prose drifts
    from code; a table generated from `inspect.signature` cannot. Every seed parameter is
    reported with the value the run actually used.

    The `run()` of each module calls these with no arguments, so the defaults *are* what
    ran. That premise is checked below rather than assumed -- if a call site ever starts
    overriding a seed, this raises instead of publishing a table that has quietly become
    false.
    """
    import ast
    import inspect

    sources = [
        ("Claim 4", "exact Davis-Kahan constant", claim_c4_prop41.thm_d4_exact_constant),
        ("Claim 4", "adversarial supremum", claim_c4_prop41.thm_d4_adversarial_constant),
        ("Claim 4", "finite-perturbation sweep", claim_c4_prop41.thm_d4_finite_perturbation),
        ("Claim 4", "negative controls", claim_c4_prop41.negative_controls),
        ("Claim 5", "Davis-Kahan adversarial search", claim_c5_thm42.davis_kahan_constant_check),
        ("Claim 5", "calibrated rate", claim_c5_thm42.calibrated_rate),
        ("Claim 5", "negative controls", claim_c5_thm42.negative_controls),
        ("Claim 5", "eta tail measurement", claim_c5_thm42.eta_tail_measurement),
        ("Claim 6", "sample-complexity sweeps (sigma, pi_min, p)",
         claim_c6_thm43.sample_complexity_sweeps),
        ("Claim 6", "sigma boundary probe", claim_c6_thm43.sigma_sweep),
        ("Claim 6", "restart-budget attribution", claim_c6_thm43.restart_budget_attribution),
        ("Claim 6", "negative controls", claim_c6_thm43.negative_controls),
    ]

    overridden = []
    for mod in (claim_c4_prop41, claim_c5_thm42, claim_c6_thm43):
        tree = ast.parse(inspect.getsource(mod.run))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg and "seed" in kw.arg:
                        overridden.append(f"{mod.__name__}.run passes {kw.arg}=")
    if overridden:
        raise AssertionError(
            "a seed is set at the call site, so the signature defaults published as the "
            "seeds table would be wrong: " + "; ".join(overridden)
        )

    rows = []
    for claim, what, fn in sources:
        params = inspect.signature(fn).parameters
        # Exactly the seed parameters. `n_seeds` is a replicate count, not a seed, and
        # listing it in a seeds table would misreport what was fixed.
        used = {k: v.default for k, v in params.items()
                if k in ("seed", "seeds", "seed0", "model_seed")}
        rows.append({
            "claim": claim,
            "stage": what,
            "function": f"{fn.__module__}.{fn.__name__}",
            "seeds": {k: (list(v) if isinstance(v, tuple) else v) for k, v in used.items()},
            "n_seeds": sum(len(v) if isinstance(v, tuple) else 1 for v in used.values()),
        })
    return {
        "generated_from": "inspect.signature of the functions run() actually calls",
        "call_sites_override_a_seed": bool(overridden),
        "rows": rows,
        "benchmark_shards": {
            "note": "passed to the authors' --seed; drives their validation split and numpy RNG",
            "seeds": [2024, 2025, 2026, 2027, 2028],
        },
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "unset"),
    }


def main() -> int:
    t0 = time.time()
    out = {"paper": "3WPDFjZ1UT", "arxiv": "2603.00039", "environment": environment(), "claims": {}}
    out["seed_record"] = seed_record()

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

    payload = json.dumps(out, indent=2, default=str)
    # The published verdict has to parse strictly, or an evaluator cannot open it.
    json.loads(payload)
    # Job filesystems are discarded, so the verdict leaves via stdout -- but the log
    # transport decodes JSON escapes, which silently turns an escaped newline inside a
    # string into a real control character and corrupts the file on the way out. base64
    # has no escapes for the transport to touch, so what is collected is byte-identical
    # to what was produced.
    print(BEGIN, flush=True)
    print(base64.b64encode(payload.encode()).decode(), flush=True)
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
