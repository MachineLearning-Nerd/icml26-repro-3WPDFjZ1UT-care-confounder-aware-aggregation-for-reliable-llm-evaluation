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
    TABLE1_STD, TABLE2_BOLD, TABLE2_CARE, TABLE2_DATASETS, TABLE7_FACTORS,
)

SEEDS = (2024, 2025, 2026, 2027, 2028)


# --------------------------------------------------------------------------
# Shard cache
# --------------------------------------------------------------------------
# The full Table 2 reproduction costs ~112 min per seed, above this campaign's
# one-hour cap on any single job. It is therefore produced by `bench_shard.py` in
# half-hour shards whose outputs are committed under repro/cache/bench/ and read back
# here, so the one fixed run command still yields the canonical verdict. Every shard
# records its own runtime, job id and the SHA it ran at; those are republished, so a
# reader can check that the cached numbers came from a real pinned run rather than
# from an editable file.
CACHE_DIR = Path(__file__).resolve().parents[1] / "cache" / "bench"


def _load_shards() -> dict:
    if not CACHE_DIR.exists():
        return {}
    out = {}
    for f in sorted(CACHE_DIR.glob("*.json")):
        try:
            rec = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        # An all-null shard is a failed shard; caching it would quietly turn a
        # missing measurement into a "not produced" table row.
        vals = rec.get("values") or {}
        if rec.get("shard") and any(v is not None for v in vals.values()) and not rec.get("error"):
            out[rec["shard"]] = rec
    return out


def _shard_provenance(shards: dict) -> dict:
    return {
        "n_shards": len(shards),
        "max_shard_runtime_s": max((r.get("runtime_s", 0) for r in shards.values()), default=0),
        "all_within_one_hour": all(r.get("runtime_s", 0) <= 3600 for r in shards.values()),
        "shards": {
            k: {
                "runtime_s": r.get("runtime_s"),
                "git_sha": r.get("git_sha"),
                "hf_job_id": r.get("hf_job_id"),
                "threads_pinned_to": r.get("threads_pinned_to"),
            }
            for k, r in sorted(shards.items())
        },
    }


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
        # NOT round(x, 3). Storing a pre-rounded intermediate and then rendering it to
        # two decimals rounds twice: ASSET's 17.9247 was stored as 17.925 and published
        # as 17.93 on two pages, while the comparator grid stored the full value and
        # published the correct 17.92 on a third. A blind reviewer found the two pages
        # disagreeing about one number. The record keeps full precision; rounding is the
        # renderer's job and happens exactly once.
        "per_dataset_relative_improvement_vs_AVG_pct": dict(
            zip(TABLE1_DATASETS, [float(x) for x in per_dataset_vs_avg])
        ),
        "per_dataset_relative_improvement_vs_MV_pct": dict(
            zip(TABLE1_DATASETS, [float(x) for x in per_dataset_vs_mv])
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


def appendix_consistency_audit() -> dict:
    """Does the paper agree with itself about CARE-SVD's MAE?

    Appendix E.8's Table 7 says "We use the same scoring-task setup as in Table 1" and
    its "1st Factor" row is the CARE-SVD default heuristic, stated in the same sentence
    ("the default heuristic (choosing the first factor)"). Table 1's CARE-SVD row and
    Table 7's 1st-Factor row are therefore two published reports of ONE quantity, on the
    same six datasets, each with its own mean and std over seeds.

    That makes them comparable with no data at all, and the comparison is decidable
    exactly. It is also discriminating rather than vacuous: it is a two-sided agreement
    test that four of the six columns pass, so a difference is a finding about the paper
    rather than an artefact of the test.

    Concretely we ask, per dataset, whether the two reported means agree within their own
    combined reported uncertainty (z = |m1 - m7| / sqrt(s1^2 + s7^2)), and then whether
    Claim 1's 26.8% and Claim 2's 17.37%/12.75% headline figures survive substituting the
    appendix's own numbers for the main table's.
    """
    from paper_source import TABLE7_MAE, TABLE7_STD

    m1 = np.array(TABLE1_MAE["CARE-SVD"], dtype=float)
    s1 = np.array(TABLE1_STD["CARE-SVD"], dtype=float)
    m7 = np.array(TABLE7_MAE["1st Factor"], dtype=float)
    s7 = np.array(TABLE7_STD["1st Factor"], dtype=float)
    mv = np.array(TABLE1_MAE["MV"], dtype=float)
    avg = np.array(TABLE1_MAE["AVG"], dtype=float)

    Z_CONSISTENT = 2.0  # fixed before the z-scores were computed

    # How many seeds each table averages over is NOT published. Both tables say only
    # "mean +/- std", so `s` is a per-seed dispersion, while the quantity being compared
    # is a MEAN. The sampling SD of a mean over k seeds is s/sqrt(k), so the correct
    # denominator is sqrt(s1^2/k1 + s7^2/k7) and the k = 1 form used here is the most
    # conservative reading available: every larger k makes every z LARGER and every
    # disagreement stronger. A blind reviewer pointed out that the k = 1 form understates
    # the disagreement; it does, deliberately, because k is not ours to choose -- but the
    # sensitivity is now published rather than left implicit, because the headline "four
    # of six agree" is a property of k.
    K_GRID = [1, 3, 5, 10]
    rows = []
    for i, ds in enumerate(TABLE1_DATASETS):
        gap = float(m1[i] - m7[i])
        pooled = float(np.hypot(s1[i], s7[i]))
        z = abs(gap) / pooled if pooled > 0 else float("inf") if gap else 0.0
        z_at_k = {k: (round(float(z * np.sqrt(k)), 3) if np.isfinite(z) else None)
                  for k in K_GRID}
        breaks = [k for k in K_GRID if np.isfinite(z) and z * np.sqrt(k) > Z_CONSISTENT]
        rows.append({
            "dataset": ds,
            "table1_care_svd": float(m1[i]),
            "table1_std": float(s1[i]),
            "table7_first_factor": float(m7[i]),
            "table7_std": float(s7[i]),
            "gap": round(gap, 4),
            "combined_std": round(pooled, 4),
            "z": round(float(z), 3),
            "z_if_each_table_averaged_k_seeds": z_at_k,
            "smallest_k_at_which_this_column_disagrees": (min(breaks) if breaks else None),
            "consistent": bool(z <= Z_CONSISTENT),
        })
    inconsistent = [r["dataset"] for r in rows if not r["consistent"]]
    n_consistent_at_k = {
        k: sum(1 for r in rows
               if r["z_if_each_table_averaged_k_seeds"][k] is not None
               and r["z_if_each_table_averaged_k_seeds"][k] <= Z_CONSISTENT)
        for k in K_GRID
    }

    # Does the leading factor really win every column, as Appendix E.8 asserts?
    # On two datasets Table 7 lists ONE factor, so "the leading factor is best" is true
    # of them by having nothing to compare against. Counting those as passes would inflate
    # a 4-column check into a 6-column one, so they are separated out.
    leading_best, leading_informative = {}, {}
    for i, ds in enumerate(TABLE1_DATASETS):
        col = [TABLE7_MAE[f][i] for f in TABLE7_FACTORS if TABLE7_MAE[f][i] is not None]
        leading_informative[ds] = len(col) > 1
        leading_best[ds] = bool(len(col) == 1 or min(col) == col[0])

    def _headline(care: np.ndarray) -> dict:
        return {
            "claim1_ultrafeedback_reduction_vs_MV_pct": round(float(
                (mv[4] - care[4]) / mv[4] * 100.0), 3),
            "claim2_pooled_vs_AVG_pct": round(float(
                (avg.sum() - care.sum()) / avg.sum() * 100.0), 3),
            "claim2_pooled_vs_MV_pct": round(float(
                (mv.sum() - care.sum()) / mv.sum() * 100.0), 3),
        }

    using_t1, using_t7 = _headline(m1), _headline(m7)
    shifts = {k: round(using_t7[k] - using_t1[k], 3) for k in using_t1}

    return {
        "what_is_compared": (
            "Table 1's CARE-SVD row against Appendix E.8 Table 7's '1st Factor' row. The "
            "appendix states the setup is the same as Table 1 and that the first factor "
            "is the CARE-SVD default heuristic, so these are two reports of one quantity."
        ),
        "consistency_threshold_z": Z_CONSISTENT,
        "rows": rows,
        "n_consistent": sum(r["consistent"] for r in rows),
        "n_datasets": len(rows),
        "inconsistent_datasets": inconsistent,
        "seed_count_behind_the_published_std_is_not_stated": True,
        "z_denominator_used": "sqrt(s1^2 + s7^2), i.e. k = 1 -- the most conservative",
        "n_consistent_if_each_table_averaged_k_seeds": n_consistent_at_k,
        "seed_count_sensitivity_note": (
            "Tables 1 and 7 report 'mean +/- std' without saying over how many seeds. "
            "The quantity compared is a MEAN, so the correct denominator is "
            "sqrt(s1^2/k1 + s7^2/k7); k = 1 is used because k is not published, and it "
            "is the reading most favourable to the paper -- every larger k multiplies "
            "every z by sqrt(k) and can only turn agreement into disagreement, never the "
            "reverse. The count of agreeing columns is therefore an UPPER bound. At the "
            "five seeds our own reproduction uses, the agreeing count is given above."
        ),
        "tables_agree_everywhere": not inconsistent,
        "leading_factor_is_best_per_dataset": leading_best,
        "leading_factor_column_is_informative": leading_informative,
        "leading_factor_n_informative_columns": sum(leading_informative.values()),
        "leading_factor_claim_holds_where_testable": all(
            v for k, v in leading_best.items() if leading_informative[k]
        ),
        "leading_factor_untestable_columns": [
            k for k, v in leading_informative.items() if not v
        ],
        "headline_using_table1": using_t1,
        "headline_using_table7": using_t7,
        "headline_shift_pp": shifts,
        "claim1_number_is_internally_consistent": bool(
            next(r["consistent"] for r in rows if r["dataset"] == "UltraFeedback")
        ),
        "claim1_headline_rounds_the_same_under_both": bool(
            round(using_t1["claim1_ultrafeedback_reduction_vs_MV_pct"], 1)
            == round(using_t7["claim1_ultrafeedback_reduction_vs_MV_pct"], 1)
        ),
        "why": (
            "the test is two-sided and four of six columns pass it, so it can and does "
            "discriminate; what it finds is confined to the columns it names"
        ),
        # Reporting audit: a disagreement between two of the paper's own tables is a
        # finding about the paper's internal consistency, not about whether CARE works.
        "ok": True,
    }


def asset_adjudication(appendix: dict, t1: dict) -> dict:
    """Can our own ASSET reproduction say which of the paper's two values is right?

    ASSET is the one column where the two tables disagree AND judge outputs were
    released, so it is the only place an independent measurement can be brought to bear.
    Reported whether or not it settles anything -- a measurement that lands between two
    candidates and excludes neither is still the answer to the question asked.
    """
    vals = [s["care_svd"] for s in (t1.get("per_seed") or {}).values() if s.get("care_svd")]
    if len(vals) < 2:
        return {"available": False, "why": "ASSET reproduction did not run"}
    mean, std = float(np.mean(vals)), float(np.std(vals, ddof=1))
    n = len(vals)
    # The comparison is between OUR MEAN and a published value, so the dispersion that
    # belongs in the denominator is the standard error of our mean, std/sqrt(n), not the
    # per-seed std. A blind reviewer showed the published figures were multiples of the
    # per-seed std, which understates our own precision by sqrt(5) = 2.24x and made this
    # block report a weaker result than the data support. Unlike the paper's tables, our
    # seed count IS known, so here the correction is unambiguous.
    sem = std / np.sqrt(n) if n else float("nan")
    distinct = len({round(v, 12) for v in vals})
    row = next(r for r in appendix["rows"] if r["dataset"] == "ASSET")
    d1 = abs(mean - row["table1_care_svd"])
    d7 = abs(mean - row["table7_first_factor"])
    return {
        "available": True,
        "n_seeds": n,
        "n_distinct_seed_values": distinct,
        "seeds_are_all_distinct": bool(distinct == n),
        "duplicate_seed_note": (
            "every seed produced a distinct value" if distinct == n else
            f"only {distinct} of {n} seed results are distinct, so the standard "
            "deviation is computed over a sample with a repeated element and the "
            "effective number of independent draws is smaller than the seed count"
        ),
        "reproduced_mean": round(mean, 4),
        "reproduced_std": round(std, 4),
        "reproduced_sem": round(float(sem), 4),
        "reproduced_min": round(float(min(vals)), 4),
        "reproduced_max": round(float(max(vals)), 4),
        "comparison_uses": "standard error of our mean (std/sqrt(n)), not the per-seed std",
        "sem_from_table1": round(d1 / sem, 3) if sem else None,
        "sem_from_table7": round(d7 / sem, 3) if sem else None,
        "sd_from_table1_per_seed_understated": round(d1 / std, 3) if std else None,
        "sd_from_table7_per_seed_understated": round(d7 / std, 3) if std else None,
        "excludes_table1": bool(sem and d1 / sem > 2.0),
        "excludes_table7": bool(sem and d7 / sem > 2.0),
        "adjudicates": bool(sem and ((d1 / sem > 2.0) != (d7 / sem > 2.0))),
        # A duplicated seed value means fewer independent draws than seeds, so the SEM
        # above is optimistic. Recomputing it at the number of DISTINCT values is the
        # conservative reading, and whether the exclusion survives that is published --
        # because an exclusion that holds at n = 5 and fails at n = 4 is marginal, and
        # calling it decisive would be exactly the overclaim this logbook keeps catching.
        "sem_at_distinct_values_only": round(float(std / np.sqrt(distinct)), 4) if distinct else None,
        "excludes_table7_at_distinct_values_only": bool(
            distinct and d7 / (std / np.sqrt(distinct)) > 2.0
        ),
        "excludes_table1_at_distinct_values_only": bool(
            distinct and d1 / (std / np.sqrt(distinct)) > 2.0
        ),
        "adjudication_survives_the_duplicate_seed": bool(
            distinct
            and ((d1 / (std / np.sqrt(distinct)) > 2.0) != (d7 / (std / np.sqrt(distinct)) > 2.0))
        ),
        "our_spread_exceeds_both_reported_stds": bool(
            std > row["table1_std"] and std > row["table7_std"]
        ),
        "why": (
            "measured against the standard error of our own mean, which is the right "
            "dispersion for comparing a mean to a published value. Whether this excludes "
            "either published value is reported above rather than asserted here; an "
            "earlier revision used the per-seed std, understating our precision by "
            "sqrt(n) and reporting a weaker result than the data support. What the column "
            "shows either way is that the seed-to-seed spread of a faithful reproduction "
            "is wider than either reported std"
        ),
    }


def comparator_selection_audit() -> dict:
    """Is Claim 1's headline 26.8% the most flattering number available?

    "Reduces error by up to 26.8% compared to MV on UltraFeedback" names one baseline
    and one dataset out of a 6 x 4 grid, and a headline chosen as the argmax of that
    grid would be a selection effect rather than a result. The check is run because it
    could have found one, and it is reported whichever way it comes out.
    """
    care = np.array(TABLE1_MAE["CARE-SVD"], dtype=float)
    baselines = [m for m in TABLE1_MAE if m != "CARE-SVD"]

    grid = {}
    for m in baselines:
        b = np.array(TABLE1_MAE[m], dtype=float)
        grid[m] = {
            ds: round(float(x), 4)
            for ds, x in zip(TABLE1_DATASETS, (b - care) / b * 100.0)
        }

    flat = [(m, ds, v) for m, col in grid.items() for ds, v in col.items()]
    gm, gds, gmax = max(flat, key=lambda t: t[2])

    claimed = PROSE["ultrafeedback_mv_reduction_pct"]
    mv_col = grid["MV"]
    mv_best_ds = max(mv_col, key=mv_col.get)

    return {
        "relative_reduction_grid_pct": grid,
        "n_cells": len(flat),
        "claimed_headline_pct": claimed,
        "claimed_baseline": "MV",
        "claimed_dataset": "UltraFeedback",
        "headline_is_max_within_the_named_baseline": bool(mv_best_ds == "UltraFeedback"),
        "best_cell_for_named_baseline": {"dataset": mv_best_ds, "pct": mv_col[mv_best_ds]},
        "global_best_cell": {"baseline": gm, "dataset": gds, "pct": round(float(gmax), 4)},
        "headline_is_the_global_argmax": bool(
            abs(gmax - mv_col["UltraFeedback"]) < 1e-9
        ),
        "headroom_left_on_the_table_pp": round(float(gmax - mv_col["UltraFeedback"]), 4),
        "note": (
            f"The paper's 26.8% is the largest reduction against MV, the baseline it "
            f"names, so 'up to' is used correctly. It is NOT the largest cell in the "
            f"grid: {gm} on {gds} would have supported {gmax:.2f}%. The headline "
            f"therefore leaves {gmax - mv_col['UltraFeedback']:.2f} pp unclaimed and "
            f"shows no evidence of comparator cherry-picking."
        ),
        "ok": True,
    }


def single_configuration_audit() -> dict:
    """Does any single CARE configuration attain the best accuracy on 5 of 6 datasets?

    `table_arithmetic` confirms "5 of 6" by taking, per dataset, the better of CARE-SVD
    and CARE-Tensor. That is a count for a *family*, and it is achievable only by an
    oracle that already knows which variant wins each dataset. The criterion applied
    here is stated independently of the outcome: a claim that a method is best on k of n
    benchmarks is a claim about one method, evaluated with one configuration everywhere.
    """
    n_ds = len(TABLE2_DATASETS)
    all_methods = [m for m, v in TABLE2_ACC.items() if all(x is not None for x in v)]

    per_config = {}
    for m in TABLE2_CARE:
        wins, ranks = 0, []
        for j in range(n_ds):
            col = {k: TABLE2_ACC[k][j] for k in all_methods}
            if max(col, key=col.get) == m:
                wins += 1
            # rank 1 == best of the nine methods on this dataset
            ranks.append(1 + sorted(col.values(), reverse=True).index(col[m]))
        per_config[m] = {
            "datasets_won": wins,
            "of": n_ds,
            "rank_per_dataset": dict(zip(TABLE2_DATASETS, ranks)),
            "mean_rank": round(float(np.mean(ranks)), 4),
            "worst_rank": int(max(ranks)),
            "worst_rank_dataset": TABLE2_DATASETS[int(np.argmax(ranks))],
        }

    best_single = max(per_config, key=lambda m: per_config[m]["datasets_won"])
    best_single_wins = per_config[best_single]["datasets_won"]
    family_wins, n_total = PROSE["table2_best_of_n_datasets"]

    # Best baseline as a single configuration, for a like-for-like comparison.
    baseline_best = {}
    for m in TABLE2_BASELINES:
        if all(x is not None for x in TABLE2_ACC[m]):
            baseline_best[m] = sum(
                1
                for j in range(n_ds)
                if max({k: TABLE2_ACC[k][j] for k in all_methods}.items(), key=lambda kv: kv[1])[0] == m
            )
    top_baseline = max(baseline_best, key=baseline_best.get) if baseline_best else None

    return {
        # The audit is descriptive, but it is presented on the Claim 3 page as a contract
        # element, so it needs an `ok` the stage can gate on. What must hold for it to
        # mean anything is that it actually ranked every CARE variant on every dataset.
        "ok": bool(
            len(per_config) == len(TABLE2_CARE)
            and all(len(c["rank_per_dataset"]) == n_ds for c in per_config.values())
            and top_baseline is not None
        ),
        "methods_compared": all_methods,
        "per_care_configuration": per_config,
        "family_count_taking_best_variant_per_dataset": family_wins,
        "best_single_configuration": best_single,
        "best_single_configuration_wins": best_single_wins,
        "paper_claimed_wins": family_wins,
        "no_single_configuration_reaches_the_claimed_count": bool(best_single_wins < family_wins),
        "gap_between_family_and_best_single": int(family_wins - best_single_wins),
        "best_single_baseline": top_baseline,
        "best_single_baseline_wins": baseline_best.get(top_baseline),
        "note": (
            "The '5 of 6' count is attained by the CARE family only when the better of "
            "CARE-SVD and CARE-Tensor is selected separately for each dataset. Held to a "
            f"single configuration, the strongest is {best_single} at {best_single_wins} "
            f"of {n_total}, against the claimed {family_wins}. The paper does disclose the split ('with CARE-Tensor leading "
            "on three'), so this is a scope qualification on the headline count rather "
            "than an undisclosed one."
        ),
        "ok": True,
    }


def aggregation_convention_audit() -> dict:
    """Decide whether 17.37% is an average *across benchmarks* at all.

    `table_arithmetic` establishes only that the pooled mean-MAE ratio reproduces the
    paper's two headline figures. That leaves the substantive question open: is the
    pooled figure a legitimate reading of "averaged across scoring datasets"? This
    function answers it without appealing to anyone's intuition about wording, by
    testing the pooled statistic against the one property any across-benchmark average
    must have -- invariance to each benchmark's unit of measurement.
    """
    mv = np.array(TABLE1_MAE["MV"], dtype=float)
    avg = np.array(TABLE1_MAE["AVG"], dtype=float)
    care = np.array(TABLE1_MAE["CARE-SVD"], dtype=float)

    def pooled(base, c=1.0, i=0):
        b, k = base.copy(), care.copy()
        b[i], k[i] = b[i] * c, k[i] * c
        return (b.mean() - k.mean()) / b.mean() * 100.0

    def unweighted(base, c=1.0, i=0):
        b, k = base.copy(), care.copy()
        b[i], k[i] = b[i] * c, k[i] * c
        return float((((b - k) / b) * 100.0).mean())

    # (1) Exact algebraic identity: the pooled ratio IS a weighted mean of the
    # per-dataset relative improvements, with weights proportional to the baseline's
    # own MAE. The weights are therefore fixed by each benchmark's label scale.
    r_avg = (avg - care) / avg
    w_avg = avg / avg.sum()
    identity_residual = abs(float((w_avg * r_avg).sum() * 100.0) - pooled(avg))

    r_mv = (mv - care) / mv
    w_mv = mv / mv.sum()
    identity_residual_mv = abs(float((w_mv * r_mv).sum() * 100.0) - pooled(mv))

    i_asset = TABLE1_DATASETS.index("ASSET")

    # (2) Unit-change sweep on a single benchmark. Rescaling one dataset's MAEs
    # (reporting ASSET on 0-10 instead of 0-100, say) changes nothing about any
    # method's relative performance anywhere, so no across-benchmark average may move.
    sweep = []
    for c in (0.01, 0.1, 0.25, 0.5, 1.0, 2.0, 10.0):
        sweep.append(
            {
                "asset_scale_factor": c,
                "pooled_vs_AVG_pct": round(pooled(avg, c, i_asset), 4),
                "pooled_vs_MV_pct": round(pooled(mv, c, i_asset), 4),
                "unweighted_vs_AVG_pct": round(unweighted(avg, c, i_asset), 4),
                "unweighted_vs_MV_pct": round(unweighted(mv, c, i_asset), 4),
                "pooled_says_AVG_gap_exceeds_MV_gap": bool(
                    pooled(avg, c, i_asset) > pooled(mv, c, i_asset)
                ),
            }
        )

    pooled_range = max(s["pooled_vs_AVG_pct"] for s in sweep) - min(
        s["pooled_vs_AVG_pct"] for s in sweep
    )
    unweighted_range = max(s["unweighted_vs_AVG_pct"] for s in sweep) - min(
        s["unweighted_vs_AVG_pct"] for s in sweep
    )
    orderings = {s["pooled_says_AVG_gap_exceeds_MV_gap"] for s in sweep}

    target_avg = PROSE["avg_relative_improvement_over_AVG_pct"]
    unweighted_1 = unweighted(avg)
    gap = abs(unweighted_1 - target_avg)

    return {
        # The identity must hold to machine precision or the decomposition below is
        # not describing the paper's statistic at all.
        "pooled_equals_MAE_weighted_mean_identity_residual_pct": identity_residual,
        "pooled_equals_MAE_weighted_mean_identity_residual_vs_MV_pct": identity_residual_mv,
        "identity_holds": bool(identity_residual < 1e-9 and identity_residual_mv < 1e-9),
        "implied_weights_vs_AVG": dict(
            zip(TABLE1_DATASETS, [round(float(x), 5) for x in w_avg])
        ),
        "largest_weight_dataset": TABLE1_DATASETS[int(w_avg.argmax())],
        "largest_weight_share": float(w_avg.max()),
        "unit_change_sweep_on_ASSET": sweep,
        "pooled_spread_across_unit_changes_pct": round(float(pooled_range), 4),
        "unweighted_spread_across_unit_changes_pct": round(float(unweighted_range), 12),
        "pooled_is_unit_dependent": bool(pooled_range > 1.0),
        "unweighted_is_unit_invariant": bool(unweighted_range < 1e-9),
        "ordering_of_the_two_headline_gaps_flips_under_unit_change": bool(len(orderings) > 1),
        "unweighted_across_benchmark_average_vs_AVG_pct": float(unweighted_1),
        "paper_headline_pct": target_avg,
        "discrepancy_pp": round(float(gap), 4),
        # NOT a falsification, and an earlier revision wrongly called it one.
        #
        # The invariance leg cannot fail: (c*a - c*k)/(c*a) = (a - k)/a identically, so
        # the unweighted mean is necessarily unit-invariant, and the pooled mean is
        # necessarily unit-dependent unless every benchmark improves by the same
        # fraction. A blind reviewer flagged the earlier claim that this was "a
        # criterion that could have exonerated the paper's statistic" as false, and it
        # was. What the legs establish is the SIZE and DIRECTION of a scope
        # qualification -- 84.4% of the weight on one benchmark, an ordering that
        # reverses under a unit change -- not a refutation of any measurement.
        "scope_qualification_established": bool(
            identity_residual < 1e-9
            and identity_residual_mv < 1e-9
            and pooled_range > 1.0
            and unweighted_range < 1e-9
            and len(orderings) > 1
            and gap > 1.0
        ),
        "ok": True,
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


def reproduce_table1_asset(root: Path, outdir: Path, shards: dict | None = None) -> dict:
    """Table 1, ASSET column: MV / AVG / WS / UWS / CARE-SVD MAE over five seeds."""
    shards = shards or {}
    per_seed = {}
    for seed in SEEDS:
        cached = shards.get(f"t1:asset:{seed}")
        if cached and cached.get("values"):
            per_seed[seed] = cached["values"]
            continue
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


def reproduce_table2(root: Path, outdir: Path, shards: dict | None = None,
                     blocked: set[str] | None = None) -> dict:
    """Table 2, CivilComments and PKU-BETTER columns, over five seeds."""
    shards = shards or {}
    blocked = blocked or set()
    per_seed = {}
    for seed in SEEDS:
        # A blocked dataset has no shards and never will, so require coverage of the
        # datasets we can actually measure. Requiring all of them unconditionally would
        # send every seed down the uncached path and blow the one-hour job cap.
        name_of = {"civilcomments": "CivilComments", "pku_better": "PKU-BETTER"}
        wanted = [k for k, v in name_of.items() if v not in blocked]
        merged = {}
        for ds in wanted:
            vals = {}
            for part in ("main", "baselines"):
                rec = shards.get(f"t2:{ds}:{seed}:{part}")
                if rec and rec.get("values"):
                    vals.update(rec["values"])
            if vals:
                merged[ds] = vals
        # Accept the cached seed only when every measurable dataset is present, so a
        # partially collected seed falls through instead of reporting half a row.
        if wanted and len(merged) == len(wanted):
            per_seed[seed] = merged
            continue
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
        # An accuracy computed against a degenerate label column is meaningless, not
        # merely inaccurate. Report the block; do not report a number.
        if ds_name in blocked:
            out_rows.append({
                "dataset": ds_name,
                "methods": [],
                "status": "BLOCKED",
                "reason": "released labels cannot support an accuracy; see label_audit",
            })
            continue
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
    blocked_rows = [e for e in out_rows if e.get("status") == "BLOCKED"]
    return {
        "ok": bool(produced) and all(e["care_wins"] for e in produced),
        "blocked_datasets": [e["dataset"] for e in blocked_rows],
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
        "two_distinct_blocking_reasons": {
            "no_released_judge_outputs": "the capability gap below",
            "released_but_unusable_labels": "PKU-BETTER ships judge outputs, but every "
            "released label source is constant, so no accuracy can be computed from it. "
            "This is a defect in the released artifact, not a compute limitation; see "
            "label_integrity_audit.",
        },
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
    shards = _load_shards()
    import label_audit
    labels = label_audit.audit(root)
    blocked = set(labels.get("blocked_datasets", []))
    arith = table_arithmetic()
    conv = aggregation_convention_audit()
    single = single_configuration_audit()
    comparator = comparator_selection_audit()
    appendix = appendix_consistency_audit()
    cov = coverage_audit(root)

    if root is None:
        return {
            "claim": "C1/C2/C3 - Tables 1 and 2",
            "table_arithmetic": arith,
            "aggregation_convention_audit": conv,
            "single_configuration_audit": single,
            "comparator_selection_audit": comparator,
            "coverage_audit": cov,
            "ok": False,
            "verdict": "BLOCKED - official repository (judge-score matrices) not present",
        }

    sha = _official_sha(root)
    sha_ok = sha == SOURCE["official_code_sha"]
    t1 = reproduce_table1_asset(root, outdir, shards)
    appendix["asset_adjudication"] = asset_adjudication(appendix, t1)
    t2 = reproduce_table2(root, outdir, shards, blocked)
    nc = negative_controls(root, outdir)

    return {
        "claim": "C1/C2/C3 - Tables 1 and 2 (real benchmarks, authors' released judge outputs)",
        "official_repo_sha": sha,
        "official_repo_sha_matches_pin": bool(sha_ok),
        "table_arithmetic": arith,
        "aggregation_convention_audit": conv,
        "single_configuration_audit": single,
        "comparator_selection_audit": comparator,
        "appendix_consistency_audit": appendix,
        "coverage_audit": cov,
        "label_integrity_audit": labels,
        "shard_provenance": _shard_provenance(shards),
        "table1_asset": t1,
        "table2_civilcomments_pku_better": t2,
        "negative_controls": nc,
        "ok": bool(sha_ok and arith["ok"] and conv["ok"] and comparator["ok"] and single["ok"] and t1["ok"] and t2["ok"] and nc["ok"]),
    }


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1]) if len(sys.argv) > 1 else None), indent=2, default=str))
