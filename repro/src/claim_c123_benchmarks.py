"""Claims 1-3 - the Table 1 / Table 2 benchmark numbers.

Claim 1: CARE-SVD reaches MAE 0.623 +- 0.006 vs 0.851 +- 0.000 for majority vote on
         UltraFeedback, a 26.8% error reduction (Table 1).
Claim 2: CARE achieves an average 17.37% improvement over simple averaging across
         the continuous-scoring benchmarks (Table 1).
Claim 3: On classification/preference datasets CARE attains the best accuracy on 5
         of 6 datasets, including a 13.4% relative improvement over the strongest
         baseline on Summarize (0.814 +- 0.001 vs 0.705 +- 0.000) (Table 2).

What is reachable.  CARE's aggregation is deterministic linear algebra on a fixed
n x p judge-score matrix; producing that matrix is the expensive step, and the
paper reports doing it on an NVIDIA A100 (Appendix E.2: "Generating LLM judge
outputs took up to 3 hours per dataset").  The authors' repository releases the
judge-score matrices for ASSET (Table 1) and for CivilComments and PKU-BETTER
(Table 2), and for nothing else.  So:

  * every Table 1 / Table 2 column with released judge outputs is reproduced here
    end-to-end at full scale with the authors' own code, no proxy and no synthetic
    substitute;
  * UltraFeedback, Summarize, FeedbackQA, Review-5K, Yelp, Chatbot-Arena,
    PKU-SAFER and SHP have no released judge outputs, and regenerating them needs
    GPU inference over 11-20 LLM judges, which this campaign is not authorised to
    buy.  Those are recorded BLOCKED with that exact missing capability.

Separately, the *arithmetic* content of Claims 1-3 -- the 26.8%, 17.37%, 12.75%
and 13.4% figures -- is a deterministic function of Tables 1-2 and is decided here
exactly, including which definition of "average relative improvement" the paper
actually used.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

from paper_source import (
    PROSE, SOURCE, TABLE1_DATASETS, TABLE1_MAE, TABLE2_ACC, TABLE2_BASELINES,
    TABLE2_BOLD, TABLE2_CARE, TABLE2_DATASETS,
)

SEEDS = (2024, 2025, 2026, 2027, 2028)


# --------------------------------------------------------------------------
# Arithmetic contracts on the published tables
# --------------------------------------------------------------------------
def table_arithmetic() -> dict:
    """Decide every percentage quoted in Section 5.1 against Tables 1-2 exactly."""
    mv = np.array(TABLE1_MAE["MV"], dtype=float)
    avg = np.array(TABLE1_MAE["AVG"], dtype=float)
    care = np.array(TABLE1_MAE["CARE-SVD"], dtype=float)

    per_dataset_vs_avg = (avg - care) / avg * 100.0
    per_dataset_vs_mv = (mv - care) / mv * 100.0

    defs = {
        "mean_of_per_dataset_relative_improvement": {
            "vs_AVG": float(per_dataset_vs_avg.mean()),
            "vs_MV": float(per_dataset_vs_mv.mean()),
        },
        "pooled_mean_MAE_ratio": {
            "vs_AVG": float((avg.mean() - care.mean()) / avg.mean() * 100.0),
            "vs_MV": float((mv.mean() - care.mean()) / mv.mean() * 100.0),
        },
        "median_of_per_dataset_relative_improvement": {
            "vs_AVG": float(np.median(per_dataset_vs_avg)),
            "vs_MV": float(np.median(per_dataset_vs_mv)),
        },
    }

    target_avg = PROSE["avg_relative_improvement_over_AVG_pct"]
    target_mv = PROSE["avg_relative_improvement_over_MV_pct"]
    matches = {
        name: {
            "vs_AVG_matches": abs(v["vs_AVG"] - target_avg) < 0.01,
            "vs_MV_matches": abs(v["vs_MV"] - target_mv) < 0.01,
        }
        for name, v in defs.items()
    }
    identified = [k for k, v in matches.items() if v["vs_AVG_matches"] and v["vs_MV_matches"]]

    # Claim 1's own percentage, on UltraFeedback.
    i_uf = TABLE1_DATASETS.index("UltraFeedback")
    uf_reduction = float((mv[i_uf] - care[i_uf]) / mv[i_uf] * 100.0)

    # Claim 3, part 1: "CARE attains the best accuracy on 5 of 6 datasets, with
    # CARE-Tensor leading on three (PKU-BETTER, SHP, Summarize)".
    best_per_dataset, care_wins, tensor_leads = {}, 0, []
    for j, ds in enumerate(TABLE2_DATASETS):
        col = {m: v[j] for m, v in TABLE2_ACC.items() if v[j] is not None}
        winner = max(col, key=col.get)
        best_per_dataset[ds] = {"winner": winner, "accuracy": col[winner]}
        if winner in TABLE2_CARE:
            care_wins += 1
        if winner == "CARE-Tensor":
            tensor_leads.append(ds)
    bold_agrees = all(
        best_per_dataset[ds]["winner"] == TABLE2_BOLD[ds] for ds in TABLE2_DATASETS
    )
    five_of_six = (care_wins, len(TABLE2_DATASETS)) == tuple(PROSE["table2_best_of_n_datasets"])
    tensor_ok = sorted(tensor_leads) == sorted(PROSE["table2_care_tensor_leads_on"])

    # Claim 3, part 2: the Summarize percentage, decided under both readings.
    i_sum = TABLE2_DATASETS.index("Summarize")
    baseline_col = {m: TABLE2_ACC[m][i_sum] for m in TABLE2_BASELINES}
    strongest_name = max(baseline_col, key=baseline_col.get)
    strongest = baseline_col[strongest_name]
    care_tensor_sum = TABLE2_ACC["CARE-Tensor"][i_sum]
    summarize_rel = float((care_tensor_sum - strongest) / strongest * 100.0)
    a, b = PROSE["summarize_claimstring_pair"]
    summarize_claimstring_rel = float((a - b) / b * 100.0)

    claim3_ok = (
        five_of_six
        and tensor_ok
        and bold_agrees
        and abs(summarize_rel - PROSE["summarize_relative_improvement_pct"]) < 0.1
    )

    return {
        "ok": bool(identified)
        and abs(uf_reduction - PROSE["ultrafeedback_mv_reduction_pct"]) < 0.05
        and claim3_ok,
        "per_dataset_relative_improvement_vs_AVG_pct": dict(
            zip(TABLE1_DATASETS, [round(float(x), 3) for x in per_dataset_vs_avg])
        ),
        "per_dataset_relative_improvement_vs_MV_pct": dict(
            zip(TABLE1_DATASETS, [round(float(x), 3) for x in per_dataset_vs_mv])
        ),
        "candidate_definitions": defs,
        "definition_matching_paper": identified,
        "paper_targets": {"vs_AVG_pct": target_avg, "vs_MV_pct": target_mv},
        "note_on_definition": (
            "Only the pooled mean-MAE ratio reproduces both 17.37% and 12.75%. The "
            "arithmetic average of per-dataset relative improvements gives 15.19% "
            "(vs AVG) and 17.59% (vs MV). The pooled figure is dominated by ASSET, "
            "whose MAE is on a 0-100 scale while the other five datasets are on 0-10 "
            "or smaller scales."
        ),
        "claim1_ultrafeedback_reduction_vs_MV_pct": uf_reduction,
        "claim1_paper_value_pct": PROSE["ultrafeedback_mv_reduction_pct"],
        "claim3_best_method_per_dataset": best_per_dataset,
        "claim3_bold_cells_agree_with_recomputed_winners": bool(bold_agrees),
        "claim3_care_best_on_n_of_6": care_wins,
        "claim3_five_of_six_holds": bool(five_of_six),
        "claim3_care_tensor_leads_on": tensor_leads,
        "claim3_care_tensor_leads_matches_paper": bool(tensor_ok),
        "claim3_dataset_where_care_loses": [
            ds for ds, v in best_per_dataset.items() if v["winner"] not in TABLE2_CARE
        ],
        "claim3_summarize_strongest_baseline": {"method": strongest_name, "accuracy": strongest},
        "claim3_summarize_care_tensor": care_tensor_sum,
        "claim3_summarize_relative_improvement_pct": summarize_rel,
        "claim3_paper_value_pct": PROSE["summarize_relative_improvement_pct"],
        "claim3_claimstring_pair_relative_pct": summarize_claimstring_rel,
        "claim3_note": (
            "The paper's own wording is 'a 13.4% relative improvement in accuracy on "
            "Summarize over the strongest baseline'. The strongest Summarize baseline in "
            f"Table 2 is {strongest_name} at {strongest}, and "
            f"({care_tensor_sum} - {strongest})/{strongest} = {summarize_rel:.2f}%, which "
            "reproduces 13.4% exactly. The value 0.705 quoted in the circulated claim "
            "string is the WS / Dawid-Skene entry, not the strongest baseline; that pair "
            f"would give {summarize_claimstring_rel:.2f}%."
        ),
    }


# --------------------------------------------------------------------------
# End-to-end reproduction from the authors' released judge outputs
# --------------------------------------------------------------------------
def _official_root() -> Path | None:
    p = os.environ.get("CARE_OFFICIAL_DIR")
    candidates = [Path(p)] if p else []
    candidates += [Path.cwd() / "external" / "CARE", Path("/opt/CARE")]
    for c in candidates:
        if (c / "src" / "pgm_tools.py").exists():
            return c
    return None


def _official_sha(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return None


def _run_script(root: Path, script: str, args: list[str], outdir: Path) -> int:
    # Job filesystems are discarded, so subprocess stdout goes to a file that nobody
    # can read; without this line a multi-hour stage looks identical to a hang.
    started = time.time()
    print(f"[bench] start {script} {' '.join(args)}", flush=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{root / 'src'}:{root / 'scripts'}:" + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / script), *args],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        timeout=7200,
    )
    (outdir / f"{script}.stdout.txt").write_text(proc.stdout[-200000:])
    (outdir / f"{script}.stderr.txt").write_text(proc.stderr[-200000:])
    print(f"[bench] done  {script} rc={proc.returncode} {time.time() - started:.1f}s", flush=True)
    if proc.returncode != 0:
        print(f"[bench] stderr tail: {proc.stderr[-1500:]}", flush=True)
    return proc.returncode


def reproduce_table1_asset(root: Path, outdir: Path) -> dict:
    """Table 1, ASSET column: MV / AVG / WS / UWS / CARE-SVD MAE over five seeds."""
    per_seed = {}
    for seed in SEEDS:
        d = outdir / f"t1_seed{seed}"
        d.mkdir(parents=True, exist_ok=True)
        rc = _run_script(
            root,
            "fully_gaussian_main.py",
            ["--seed", str(seed), "--datasets", "asset", "--output-dir", str(d), "--skip-baselines"],
            d,
        )
        f = d / "fully_gaussian_main.csv"
        if rc != 0 or not f.exists():
            per_seed[seed] = {"error": f"returncode {rc}"}
            continue
        df = pd.read_csv(f)
        per_seed[seed] = {
            str(r["pred"]): (None if pd.isna(r["mae"]) else float(r["mae"]))
            for _, r in df.iterrows()
        }

    label = {"mv": "MV", "avg": "AVG", "ws": "WS", "uws": "UWS", "care_svd": "CARE-SVD"}
    i = TABLE1_DATASETS.index("ASSET")
    rows = []
    for key, name in label.items():
        vals = [v[key] for v in per_seed.values() if isinstance(v, dict) and v.get(key) is not None]
        if not vals:
            rows.append({"method": name, "status": "not produced"})
            continue
        rows.append(
            {
                "method": name,
                "paper_mae": TABLE1_MAE[name][i],
                "reproduced_mae_mean": float(np.mean(vals)),
                "reproduced_mae_std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                "n_seeds": len(vals),
                "abs_diff": abs(float(np.mean(vals)) - TABLE1_MAE[name][i]),
                "rel_diff_pct": abs(float(np.mean(vals)) - TABLE1_MAE[name][i])
                / TABLE1_MAE[name][i]
                * 100.0,
            }
        )
    care = next((r for r in rows if r["method"] == "CARE-SVD"), None)
    mv = next((r for r in rows if r["method"] == "MV"), None)
    avg = next((r for r in rows if r["method"] == "AVG"), None)
    care_best = care is not None and all(
        "reproduced_mae_mean" not in r or r["reproduced_mae_mean"] >= care["reproduced_mae_mean"]
        for r in rows
    )
    return {
        "ok": bool(care is not None and "reproduced_mae_mean" in care and care_best),
        "dataset": "ASSET",
        "seeds": list(SEEDS),
        "per_seed": per_seed,
        "table": rows,
        "care_svd_is_best": bool(care_best),
        "reduction_vs_MV_pct": (
            float((mv["reproduced_mae_mean"] - care["reproduced_mae_mean"]) / mv["reproduced_mae_mean"] * 100.0)
            if care and mv and "reproduced_mae_mean" in care and "reproduced_mae_mean" in mv
            else None
        ),
        "improvement_vs_AVG_pct": (
            float((avg["reproduced_mae_mean"] - care["reproduced_mae_mean"]) / avg["reproduced_mae_mean"] * 100.0)
            if care and avg and "reproduced_mae_mean" in care and "reproduced_mae_mean" in avg
            else None
        ),
    }


def reproduce_table2(root: Path, outdir: Path) -> dict:
    """Table 2, CivilComments and PKU-BETTER columns, over five seeds."""
    per_seed = {}
    for seed in SEEDS:
        d = outdir / f"t2_seed{seed}"
        d.mkdir(parents=True, exist_ok=True)
        out = d / "gaussian_mixture_results.csv"
        rc = _run_script(
            root,
            "gaussian_mixture_main.py",
            [
                "--seed", str(seed),
                "--datasets", "civilcomments", "pku_better",
                "--output", str(out),
                "--state-dir", str(d / "state"),
                "--cache-path", str(d / "cache.json"),
                "--baseline-output", str(d / "baselines.csv"),
                "--baseline-methods", "dawid_skene", "glad", "mace",
            ],
            d,
        )
        if rc != 0 or not out.exists():
            per_seed[seed] = {"error": f"returncode {rc}"}
            continue
        df = pd.read_csv(out)
        entry = {
            str(r["dataset"]): {
                m: (None if pd.isna(r.get(m)) else float(r.get(m)))
                for m in ("mv", "avg", "ws", "uws", "care_svd", "care_tensor")
            }
            for _, r in df.iterrows()
        }
        bl = d / "baselines.csv"
        if bl.exists():
            bdf = pd.read_csv(bl)
            for _, r in bdf.iterrows():
                ds, m = str(r["dataset"]), str(r["method"])
                if ds in entry and not pd.isna(r.get("accuracy")):
                    entry[ds][m] = float(r["accuracy"])
        per_seed[seed] = entry

    name_map = {"civilcomments": "CivilComments", "pku_better": "PKU-BETTER"}
    label = {
        "mv": "MV", "avg": "AVG", "ws": "WS", "uws": "UWS",
        "dawid_skene": "Dawid-Skene", "glad": "GLAD", "mace": "MACE",
        "care_svd": "CARE-SVD", "care_tensor": "CARE-Tensor",
    }
    out_rows = []
    for ds_key, ds_name in name_map.items():
        i = TABLE2_DATASETS.index(ds_name)
        entry = {"dataset": ds_name, "methods": []}
        best_method, best_acc = None, -1.0
        for m in (
            "mv", "avg", "ws", "uws", "dawid_skene", "glad", "mace", "care_svd", "care_tensor"
        ):
            vals = [
                v[ds_key][m]
                for v in per_seed.values()
                if isinstance(v, dict) and ds_key in v and v[ds_key].get(m) is not None
            ]
            if not vals:
                continue
            mean = float(np.mean(vals))
            rec = {
                "method": {"care_svd": "CARE-SVD", "care_tensor": "CARE-Tensor"}.get(m, label.get(m, m)),
                "reproduced_acc_mean": mean,
                "reproduced_acc_std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                "n_seeds": len(vals),
            }
            paper = TABLE2_ACC.get(rec["method"], [None] * 6)[i] if rec["method"] in TABLE2_ACC else None
            if paper is not None:
                rec["paper_acc"] = paper
                rec["abs_diff"] = abs(mean - paper)
            entry["methods"].append(rec)
            if mean > best_acc:
                best_acc, best_method = mean, rec["method"]
        entry["best_method"] = best_method
        entry["care_wins"] = bool(best_method in ("CARE-SVD", "CARE-Tensor"))
        out_rows.append(entry)

    produced = [e for e in out_rows if e["methods"]]
    return {
        "ok": bool(produced) and all(e["care_wins"] for e in produced),
        "seeds": list(SEEDS),
        "per_seed": per_seed,
        "datasets": out_rows,
        "n_datasets_reproduced": len(produced),
        "n_datasets_in_table2": len(TABLE2_DATASETS),
    }


def coverage_audit(root: Path | None) -> dict:
    """Exactly which Table 1 / Table 2 columns have released judge outputs."""
    reachable_t1, reachable_t2 = [], []
    if root is not None:
        fg = root / "judge_outputs" / "fully_gaussian"
        gm = root / "judge_outputs" / "gaussian_mixture"
        alias = {
            "asset": "ASSET", "civilcomments": "CivilComments", "pku_better": "PKU-BETTER",
            "allenai_preference_test_sets_pku_better": "PKU-BETTER",
        }
        if fg.exists():
            reachable_t1 = sorted({alias.get(d.name, d.name) for d in fg.iterdir() if d.is_dir()})
        if gm.exists():
            names = {alias.get(d.name, d.name) for d in gm.iterdir() if d.is_dir()}
            names |= {alias.get(f.stem.replace(".tar", ""), f.stem) for f in gm.glob("*.tar.gz")}
            reachable_t2 = sorted(n for n in names if n in TABLE2_DATASETS)
    blocked_t1 = [d for d in TABLE1_DATASETS if d not in reachable_t1]
    blocked_t2 = [d for d in TABLE2_DATASETS if d not in reachable_t2]
    return {
        "ok": True,
        "official_repo": SOURCE["official_code"],
        "official_repo_sha_pinned": SOURCE["official_code_sha"],
        "table1_reachable": reachable_t1,
        "table1_blocked": blocked_t1,
        "table2_reachable": reachable_t2,
        "table2_blocked": blocked_t2,
        "blocking_capability": (
            "The authors did not release judge-score matrices for these datasets. "
            "Regenerating them requires running 11-20 LLM judges (0.6B-14B) over 5,000 "
            "examples per dataset; Appendix E.2 of the paper reports doing this on an "
            "NVIDIA A100 at up to 3 hours per dataset. This campaign is authorised for "
            "CPU only, so those columns cannot be produced here."
        ),
    }


def negative_controls(root: Path | None, outdir: Path) -> dict:
    """A control that must fail: permuted judge scores must destroy CARE's advantage."""
    if root is None:
        return {"ok": False, "reason": "official repository not available"}
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root / "scripts"))
    try:
        import pgm_tools  # noqa: E402
        from data_tools import load_judge_dataset_bundle  # noqa: E402
        from eval_tools import collect_metrics  # noqa: E402
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "reason": f"import failed: {exc}"}

    judge_df, human = load_judge_dataset_bundle(
        "asset", project_root=root, allow_trim=True, valid_ratio_threshold=0.7
    )
    judge_df = judge_df.reset_index(drop=True)
    human = human.reset_index(drop=True)

    rng = np.random.default_rng(0)
    scrambled = judge_df.copy()
    for c in scrambled.columns:
        scrambled[c] = rng.permutation(scrambled[c].to_numpy())

    real_mae, _ = collect_metrics(
        pgm_tools.caresl_aggregate(
            judge_df, gamma=1.0, verbose=False,
            corr_matrix=pgm_tools.sanitize_correlation(judge_df.corr()),
            max_iters=10000,
        ),
        human,
    )
    scr_mae, _ = collect_metrics(
        pgm_tools.caresl_aggregate(
            scrambled, gamma=1.0, verbose=False,
            corr_matrix=pgm_tools.sanitize_correlation(scrambled.corr()),
            max_iters=10000,
        ),
        human,
    )
    mv_mae, _ = collect_metrics(pgm_tools.majority_vote(judge_df), human)
    ok = float(scr_mae) > float(real_mae) and float(scr_mae) > float(mv_mae) * 0.9
    return {
        "ok": bool(ok),
        "care_mae_real_judge_scores": float(real_mae),
        "care_mae_row_permuted_judge_scores": float(scr_mae),
        "majority_vote_mae": float(mv_mae),
        "control_behaves_as_intended": bool(ok),
        "why": "Row-permuting each judge column preserves every marginal but destroys the "
               "shared latent structure CARE exploits; if CARE still won, the advantage "
               "would not be coming from confounder-aware aggregation.",
    }


def run(outdir: Path | None = None) -> dict:
    outdir = Path(outdir or tempfile.mkdtemp(prefix="care_bench_"))
    outdir.mkdir(parents=True, exist_ok=True)
    root = _official_root()
    arith = table_arithmetic()
    cov = coverage_audit(root)

    if root is None:
        return {
            "claim": "C1/C2/C3 - Tables 1 and 2",
            "table_arithmetic": arith,
            "coverage_audit": cov,
            "ok": False,
            "verdict": "BLOCKED - official repository (judge-score matrices) not present",
        }

    sha = _official_sha(root)
    sha_ok = sha == SOURCE["official_code_sha"]
    t1 = reproduce_table1_asset(root, outdir)
    t2 = reproduce_table2(root, outdir)
    nc = negative_controls(root, outdir)

    return {
        "claim": "C1/C2/C3 - Tables 1 and 2 (real benchmarks, authors' released judge outputs)",
        "official_repo_sha": sha,
        "official_repo_sha_matches_pin": bool(sha_ok),
        "table_arithmetic": arith,
        "coverage_audit": cov,
        "table1_asset": t1,
        "table2_civilcomments_pku_better": t2,
        "negative_controls": nc,
        "ok": bool(sha_ok and arith["ok"] and t1["ok"] and t2["ok"] and nc["ok"]),
    }


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1]) if len(sys.argv) > 1 else None), indent=2, default=str))
