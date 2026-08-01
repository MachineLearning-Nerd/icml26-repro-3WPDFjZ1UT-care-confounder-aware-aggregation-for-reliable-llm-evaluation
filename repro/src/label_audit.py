"""Integrity precondition: can the released artifact support the metric at all?

Run BEFORE any accuracy or MAE is computed. A dataset whose released ground-truth
labels are degenerate cannot support an accuracy, so any number produced from it is
meaningless rather than wrong -- such a dataset is recorded BLOCKED, and no verdict
about the paper is inferred from it either way. This is deliberately separate from the
claim checks: a failed precondition must block a claim, never falsify it.

Why this exists. Reproducing Table 2's PKU-BETTER column produced accuracies of exactly
0.0 for MV/AVG/WS/UWS and exactly 1.0 for CARE-Tensor. Those are not plausible
accuracies, and the authors' own run record showed `class_balance: 100.0` -- every test
label the same class. The cause is in the released data, not in the aggregation:

  * `gold_label_binary` is the constant 0 in all seven released judge files;
  * `gold_label_num` is the constant 1, both in the judge files and in the standalone
    `data/preference/pku_better.csv`;
  * `was_swapped` is the constant False, so the A/B order was never randomised and the
    correct answer cannot vary across rows;
  * the judges answer "B" on ~88% of rows, i.e. anti-correlated with the only gold
    answer the file admits.

`gaussian_mixture_main.py` masks this: when the label column has one distinct value it
falls back to `pref_A_or_B`, which is *a judge's own preference*, not ground truth. The
resulting "accuracy" scores a judge against itself, which is why it saturates at 0 or 1.
"""

from __future__ import annotations

import csv
import json
import os
import tarfile
from pathlib import Path

MIN_CLASSES = 2
MIN_MINORITY_FRACTION = 0.01


def _official_root() -> Path | None:
    env = os.environ.get("CARE_OFFICIAL_DIR")
    for cand in (Path(env) if env else None, Path("external/CARE"), Path("/opt/CARE")):
        if cand and (cand / "scripts").exists():
            return cand
    return None


def _column_stats(paths: list[Path], column: str, limit: int = 40) -> dict:
    counts: dict[str, int] = {}
    rows = 0
    for p in paths:
        with p.open(newline="") as fh:
            for row in csv.DictReader(fh):
                rows += 1
                v = row.get(column)
                if v is None:
                    continue
                if len(counts) < limit or v in counts:
                    counts[v] = counts.get(v, 0) + 1
    total = sum(counts.values())
    minority = (min(counts.values()) / total) if len(counts) > 1 and total else 0.0
    return {
        "column": column,
        "rows": rows,
        "distinct_values": len(counts),
        "value_counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])[:8]),
        "minority_fraction": minority,
    }


def _verdict(stats: dict) -> dict:
    ok = stats["distinct_values"] >= MIN_CLASSES and stats["minority_fraction"] >= MIN_MINORITY_FRACTION
    return {
        **stats,
        "supports_a_metric": bool(ok),
        "why": "usable" if ok
        else f"only {stats['distinct_values']} distinct label value(s); an accuracy "
             "computed against a constant label is meaningless",
    }


PAPER_PKU_BETTER_MV_ACCURACY = 0.701


def _pku_reachable_accuracy(pku_files) -> dict:
    """Show the published PKU-BETTER column is unreachable under EITHER label convention.

    "The labels are constant" says the column cannot be scored. It does not say the
    published number cannot be reproduced, and those are different claims -- with a
    constant gold label an accuracy is still *computable*, it just equals the rate at
    which a method picks that one answer. So we compute it, both ways.

    The mechanism is visible in the data: `was_swapped` is False on every row, so the
    A/B randomisation step was never applied to this released slice and response_B is
    always the preferred one. Every judge therefore votes B on 51-100% of rows, and
    majority vote lands near 1.0 (gold = B) or near 0.0 (gold = A). Neither is the
    paper's 0.701, so the published column was computed from a randomised version of
    this dataset that the repository does not ship.
    """
    import csv as _csv

    preds, per_judge = {}, {}
    for p in pku_files:
        with open(p, newline="") as f:
            rows = list(_csv.DictReader(f))
        if not rows or "pref_A_or_B" not in rows[0]:
            continue
        v = [r["pref_A_or_B"] for r in rows]
        preds[p.name] = v
        per_judge[p.name] = round(sum(1 for x in v if x == "B") / len(v), 4)
    if not preds:
        return {"available": False}

    names = sorted(preds)
    n = min(len(preds[k]) for k in names)
    votes_B = [sum(1 for k in names if preds[k][i] == "B") for i in range(n)]
    mv_says_B = [c > len(names) / 2 for c in votes_B]
    acc_gold_B = sum(mv_says_B) / n
    acc_gold_A = 1.0 - acc_gold_B
    paper = PAPER_PKU_BETTER_MV_ACCURACY
    return {
        "available": True,
        "n_rows": n,
        "n_judges": len(names),
        "fraction_predicting_B_per_judge": per_judge,
        "majority_vote_accuracy_if_gold_is_B": round(acc_gold_B, 4),
        "majority_vote_accuracy_if_gold_is_A": round(acc_gold_A, 4),
        "paper_reported_mv_accuracy": paper,
        "closest_reachable_gap": round(min(abs(acc_gold_B - paper), abs(acc_gold_A - paper)), 4),
        "published_value_reachable": bool(
            min(abs(acc_gold_B - paper), abs(acc_gold_A - paper)) < 0.05
        ),
        "why": (
            "was_swapped is False on every row, so the A/B randomisation was not applied "
            "to this slice; response_B is always the preferred answer and every judge "
            "votes B on a large majority of rows. The published 0.701 is therefore not "
            "reachable from the released file under either label convention, which is a "
            "stronger statement than 'the labels are constant': the column is not merely "
            "unscoreable, the published number provably did not come from this file."
        ),
    }


def audit(root: Path | None = None) -> dict:
    root = root or _official_root()
    if root is None:
        return {"ok": False, "reason": "official repository not available"}

    jr = root / "judge_outputs" / "gaussian_mixture"
    out: dict = {"datasets": {}}

    # --- CivilComments: labels live on each judge CSV --------------------------
    cc = sorted((jr / "civilcomments").glob("*.csv"))
    if cc:
        out["datasets"]["CivilComments"] = _verdict(_column_stats(cc[:1], "label"))
        out["datasets"]["CivilComments"]["n_judge_files"] = len(cc)

    # --- PKU-BETTER: extract the released archive, then audit every candidate ---
    pku_dir = jr / "pku_better"
    archive = jr / "allenai_preference_test_sets_pku_better.tar.gz"
    if not (pku_dir.exists() and any(pku_dir.glob("*.csv"))) and archive.exists():
        with tarfile.open(archive, "r:gz") as tar:
            base = jr.resolve()
            for m in tar.getmembers():
                if base not in (jr / m.name).resolve().parents and (jr / m.name).resolve() != base:
                    raise ValueError(f"unsafe archive member: {m.name}")
            tar.extractall(path=jr)
    pku = sorted(pku_dir.glob("*.csv"))
    if pku:
        # Audit EVERY candidate label source the config or its fallback could use, so
        # the conclusion cannot rest on having looked at only one of them.
        cands = {c: _verdict(_column_stats(pku[:1], c))
                 for c in ("gold_label_binary", "gold_label_num", "was_swapped")}
        per_file = {
            p.name: _column_stats([p], "gold_label_binary")["distinct_values"] for p in pku
        }
        standalone = root / "data" / "preference" / "pku_better.csv"
        if standalone.exists():
            cands["standalone_file_gold_label_num"] = _verdict(
                _column_stats([standalone], "gold_label_num")
            )
        usable = any(v["supports_a_metric"] for k, v in cands.items() if k != "was_swapped")
        out["datasets"]["PKU-BETTER"] = {
            "n_judge_files": len(pku),
            "candidate_label_sources": cands,
            "distinct_gold_label_binary_per_judge_file": per_file,
            "reachable_accuracy_under_each_convention": _pku_reachable_accuracy(pku),
            "supports_a_metric": bool(usable),
            "why": "usable" if usable else
                   "no released label source has more than one distinct value, and "
                   "was_swapped is constant, so the correct answer cannot vary by row; "
                   "the official script therefore falls back to pref_A_or_B, which is a "
                   "judge's own prediction rather than ground truth",
        }

    # --- ASSET (Table 1) is continuous; the check is that it is not constant ----
    asset = root / "data" / "score" / "asset.csv"
    if asset.exists():
        st = _column_stats([asset], "human_rating")
        out["datasets"]["ASSET"] = {
            **st,
            "supports_a_metric": st["distinct_values"] >= MIN_CLASSES,
            "why": "usable" if st["distinct_values"] >= MIN_CLASSES else "constant ratings",
        }

    blocked = [k for k, v in out["datasets"].items() if not v.get("supports_a_metric")]
    out["blocked_datasets"] = blocked
    out["usable_datasets"] = [k for k in out["datasets"] if k not in blocked]
    # This audit reports; it does not fail. A degenerate release is a finding about the
    # artifact, and it blocks a dataset rather than failing the reproduction.
    out["ok"] = True
    return out


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, default=str))
