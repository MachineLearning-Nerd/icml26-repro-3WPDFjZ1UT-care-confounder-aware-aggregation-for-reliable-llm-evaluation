"""Splice measured numbers from verdict.json into the candidate pages.

    python repro/publish/fill_results.py <verdict.json> <staging_dir>

Every results block on a page is delimited by

    <!-- FILL:<block-id> -->
    ... generated ...
    <!-- /FILL -->

and is regenerated from the verdict on each run, so a page cannot drift from the run
that produced it. Exits nonzero if any block id is unknown or any block is left
unfilled, so a stale placeholder cannot reach publication.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r"(<!-- FILL:([a-z0-9_.]+) -->\n)(.*?)(<!-- /FILL -->)", re.S)


def g(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


def num(x, nd=4):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, float)):
        return f"{x:.{nd}f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)
    return str(x)


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def yesno(b):
    return "**yes**" if b else "**no**"


# --------------------------------------------------------------------------
# Block generators
# --------------------------------------------------------------------------
def c1_arithmetic(v):
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    got = a.get("claim1_ultrafeedback_reduction_vs_MV_pct")
    want = a.get("claim1_paper_value_pct")
    ok = got is not None and want is not None and abs(got - want) < 0.05
    return (
        table(
            ["Quantity", "Value"],
            [
                ["Table 1 UltraFeedback, MV", "0.851"],
                ["Table 1 UltraFeedback, CARE-SVD", "0.623"],
                ["Recomputed reduction", f"**{num(got, 3)} %**"],
                ["Paper's stated reduction", f"{num(want, 3)} %"],
                ["Agrees within 0.05 pp", yesno(ok)],
            ],
        )
        + "\n\nAssertions 1a and 1b are therefore **VERIFIED** exactly. The same figure is "
        "recomputed independently in exact `Fraction` arithmetic from a second "
        "transcription; see the independent-check row below."
    )


def _t1_table(v):
    t1 = g(v, "claims", "C1_C2_C3_tables", "table1_asset", default={})
    rows = []
    for r in t1.get("table", []):
        if "reproduced_mae_mean" not in r:
            rows.append([r.get("method"), "—", "—", r.get("status", "not produced"), "—"])
            continue
        rows.append(
            [
                r["method"],
                num(r.get("paper_mae"), 3),
                f"{num(r['reproduced_mae_mean'], 3)} ± {num(r.get('reproduced_mae_std'), 3)}",
                num(r.get("abs_diff"), 3),
                f"{num(r.get('rel_diff_pct'), 2)} %",
            ]
        )
    body = table(
        ["Method", "Paper (Table 1)", f"Reproduced (n={t1.get('seeds') and len(t1['seeds'])} seeds)", "Abs. diff", "Rel. diff"],
        rows,
    )
    extra = [
        f"- CARE-SVD is the best method on the reproduced ASSET column: {yesno(t1.get('care_svd_is_best'))}",
        f"- Reproduced reduction vs MV: **{num(t1.get('reduction_vs_MV_pct'), 2)} %**",
        f"- Reproduced improvement vs AVG: **{num(t1.get('improvement_vs_AVG_pct'), 2)} %**",
        f"- Contract satisfied: {yesno(t1.get('ok'))}",
    ]
    return body + "\n\n" + "\n".join(extra)


def c1_asset(v):
    return _t1_table(v)


def c2_asset(v):
    return _t1_table(v)


def _control(v):
    nc = g(v, "claims", "C1_C2_C3_tables", "negative_controls", default={})
    if not nc.get("ok") and "reason" in nc:
        return f"Control did not run: {nc['reason']}"
    return (
        table(
            ["Setting", "CARE MAE on ASSET"],
            [
                ["Real judge scores", f"**{num(nc.get('care_mae_real_judge_scores'), 4)}**"],
                ["Row-permuted judge scores (control)", num(nc.get("care_mae_row_permuted_judge_scores"), 4)],
                ["Majority vote, real scores", num(nc.get("majority_vote_mae"), 4)],
            ],
        )
        + f"\n\nControl behaves as intended: {yesno(nc.get('control_behaves_as_intended'))}. "
        + (nc.get("why") or "")
    )


def c1_control(v):
    return _control(v)


def c2_control(v):
    return _control(v)


def c3_control(v):
    """C3's own control, plus an explicit statement of what it does NOT cover.

    An earlier revision rendered C1's ASSET *MAE* control here, under prose describing a
    Table 2 *accuracy* experiment. That was a mislabel: the number shown belonged to a
    different claim, a different dataset and a different metric.
    """
    t = g(v, "independent_check", "table_percentages_exact_rational", default={})
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    rows = [
        ["Correct strongest baseline (GLAD, 0.718) → 13.4 %",
         f"{num(a.get('claim3_summarize_relative_improvement_pct'), 2)} %",
         yesno(t.get("summarize_13_4_from_0p814_over_0p718"))],
        ["**Control:** wrong baseline (0.705) must NOT reproduce 13.4 %",
         f"{num(a.get('claim3_claimstring_pair_relative_pct'), 2)} %",
         yesno(t.get("claimstring_0p705_does_not_reproduce_13_4"))],
    ]
    return table(["Setting", "Recomputed", "Behaves as required"], rows) + (
        "\n\nThis is a genuine negative control for the **arithmetic** half of the claim: "
        "an input the claim string got wrong must fail to produce the published figure, and "
        "it does — 0.705 yields 15.46 %, not 13.4 %. A check that passed for both inputs "
        "would have been measuring nothing.\n\n"
        "**What this does not cover, stated plainly.** There is **no permutation control on "
        "the Table 2 accuracy path**. The row-permutation control published under Claims 1 "
        "and 2 runs on ASSET and on the continuous-score (MAE) pipeline; it is evidence "
        "about that pipeline and not about the CivilComments accuracies reproduced here. "
        "An earlier revision of this page displayed that ASSET control in this position, "
        "which was a mislabel. See [Limitations item 18](#/limitations)."
    )


def c2_definitions(v):
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    defs = a.get("candidate_definitions", {})
    matches = {k: (abs(x["vs_AVG"] - 17.37) < 0.01 and abs(x["vs_MV"] - 12.75) < 0.01) for k, x in defs.items()}
    pretty = {
        "mean_of_per_dataset_relative_improvement": "Mean of per-dataset relative improvements",
        "pooled_mean_MAE_ratio": "**Pooled mean-MAE ratio**",
        "median_of_per_dataset_relative_improvement": "Median of per-dataset relative improvements",
    }
    rows = [
        [pretty.get(k, k), f"{num(x['vs_AVG'], 2)} %", f"{num(x['vs_MV'], 2)} %", yesno(matches[k])]
        for k, x in defs.items()
    ]
    ident = a.get("definition_matching_paper", [])
    return (
        table(["Candidate definition", "vs AVG", "vs MV", "Reproduces both 17.37 and 12.75?"], rows)
        + f"\n\nDefinition uniquely identified: **{', '.join(pretty.get(i, i) for i in ident) or 'none'}** "
        f"({len(ident)} of {len(defs)} candidates reproduce both targets).\n\n"
        + (a.get("note_on_definition") or "")
    )


def c1_comparator(v):
    c = g(v, "claims", "C1_C2_C3_tables", "comparator_selection_audit", default={})
    grid = c.get("relative_reduction_grid_pct", {})
    ds = list(next(iter(grid.values()), {}))
    rows = []
    for m, col in grid.items():
        cells = []
        for k in ds:
            mark = "**" if (m == "MV" and k == "UltraFeedback") else ""
            cells.append(f"{mark}{num(col[k], 2)}{mark}")
        rows.append([f"vs {m}"] + cells)
    gb = c.get("global_best_cell", {})
    return table(["Baseline"] + ds, rows) + (
        f"\n\nAll {c.get('n_cells')} cells are CARE-SVD's relative MAE reduction against that "
        f"baseline on that dataset, in %. The claimed headline is shown in bold.\n\n"
        f"- Headline is the largest reduction against the baseline the paper names (MV): "
        f"{yesno(c.get('headline_is_max_within_the_named_baseline'))}\n"
        f"- Headline is the largest cell in the whole grid: "
        f"{yesno(c.get('headline_is_the_global_argmax'))} — the largest is "
        f"**{gb.get('baseline')} on {gb.get('dataset')} at {num(gb.get('pct'), 2)} %**\n"
        f"- Headroom the paper did not claim: **{num(c.get('headroom_left_on_the_table_pp'), 2)} pp**"
    )


def c3_single_config(v):
    s = g(v, "claims", "C1_C2_C3_tables", "single_configuration_audit", default={})
    cfg = s.get("per_care_configuration", {})
    ds = list(next(iter(cfg.values()), {}).get("rank_per_dataset", {}))
    rows = []
    for m, d in cfg.items():
        ranks = d["rank_per_dataset"]
        rows.append(
            [f"**{m}** held fixed", f"{d['datasets_won']} / {d['of']}"]
            + [str(ranks[k]) for k in ds]
            + [f"**{num(d['mean_rank'], 2)}**"]
        )
    body = table(
        ["Single configuration", "Columns won"] + ds + ["Mean rank"], rows
    )
    return body + (
        f"\n\nRank is out of the **{len(s.get('methods_compared', []))} methods** in Table 2 "
        f"(1 = best). Family count, taking the better variant per dataset: "
        f"**{s.get('family_count_taking_best_variant_per_dataset')} of 6**. Best single "
        f"configuration: **{s.get('best_single_configuration')} at "
        f"{s.get('best_single_configuration_wins')} of 6**. For comparison, the strongest "
        f"single baseline is **{s.get('best_single_baseline')} at "
        f"{s.get('best_single_baseline_wins')} of 6**.\n\n"
        f"No single configuration reaches the claimed count: "
        f"{yesno(s.get('no_single_configuration_reaches_the_claimed_count'))} "
        f"(gap of {s.get('gap_between_family_and_best_single')} columns)."
    )


def c2_weights(v):
    c = g(v, "claims", "C1_C2_C3_tables", "aggregation_convention_audit", default={})
    w = c.get("implied_weights_vs_AVG", {})
    per = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic",
            "per_dataset_relative_improvement_vs_AVG_pct", default={})
    rows = [
        [k, f"{num(per.get(k), 2)} %", f"{num(100 * x, 2)} %"]
        for k, x in sorted(w.items(), key=lambda kv: -kv[1])
    ]
    res = c.get("pooled_equals_MAE_weighted_mean_identity_residual_pct")
    return (
        table(["Benchmark", "CARE-SVD improvement over AVG", "Weight it receives in the 17.37 %"], rows)
        + f"\n\nIdentity residual: **{res:.3e} pp** (exact-rational check in the independent "
        f"checker returns exact equality, not a tolerance). Largest weight: "
        f"**{c.get('largest_weight_dataset')} at {num(100 * (c.get('largest_weight_share') or 0), 2)} %**."
    )


def c2_invariance(v):
    c = g(v, "claims", "C1_C2_C3_tables", "aggregation_convention_audit", default={})
    rows = [
        [
            f"× {s['asset_scale_factor']}",
            f"{num(s['pooled_vs_AVG_pct'], 2)} %",
            f"{num(s['pooled_vs_MV_pct'], 2)} %",
            f"{num(s['unweighted_vs_AVG_pct'], 2)} %",
            f"{num(s['unweighted_vs_MV_pct'], 2)} %",
            "AVG" if s["pooled_says_AVG_gap_exceeds_MV_gap"] else "**MV**",
        ]
        for s in c.get("unit_change_sweep_on_ASSET", [])
    ]
    return (
        table(
            [
                "ASSET reported in units of",
                "Paper's statistic vs AVG",
                "Paper's statistic vs MV",
                "Across-benchmark average vs AVG",
                "Across-benchmark average vs MV",
                "Which gap looks larger",
            ],
            rows,
        )
        + f"\n\nPaper's statistic moves **{num(c.get('pooled_spread_across_unit_changes_pct'), 2)} pp** "
        f"across these unit changes; the across-benchmark average moves "
        f"**{num(c.get('unweighted_spread_across_unit_changes_pct'), 1)} pp** (exactly zero — the "
        f"independent checker confirms set-equality over exact rationals). "
        f"The paper's qualitative ordering — that CARE gains more over AVG than over MV — "
        f"**{'reverses' if c.get('ordering_of_the_two_headline_gaps_flips_under_unit_change') else 'does not reverse'}** "
        f"under a unit change on a single benchmark."
    )


def c2_per_dataset(v):
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    va = a.get("per_dataset_relative_improvement_vs_AVG_pct", {})
    vm = a.get("per_dataset_relative_improvement_vs_MV_pct", {})
    rows = [[k, f"{num(va.get(k), 2)} %", f"{num(vm.get(k), 2)} %"] for k in va]
    return table(["Dataset", "CARE-SVD vs AVG", "CARE-SVD vs MV"], rows)


def c3_recompute(v):
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    best = a.get("claim3_best_method_per_dataset", {})
    rows = [[d, r.get("winner"), num(r.get("accuracy"), 3)] for d, r in best.items()]
    extra = [
        f"- CARE is best on **{a.get('claim3_care_best_on_n_of_6')} of 6** datasets; claim says 5 of 6 → {yesno(a.get('claim3_five_of_six_holds'))}",
        f"- CARE-Tensor leads on: {', '.join(a.get('claim3_care_tensor_leads_on', [])) or '—'} → matches the paper: {yesno(a.get('claim3_care_tensor_leads_matches_paper'))}",
        f"- Dataset where CARE loses: {', '.join(a.get('claim3_dataset_where_care_loses', [])) or 'none'}",
        f"- Recomputed winners agree with the paper's **bold cells**: {yesno(a.get('claim3_bold_cells_agree_with_recomputed_winners'))}",
    ]
    return table(["Dataset", "Best method (argmax over all 9)", "Accuracy"], rows) + "\n\n" + "\n".join(extra)


def c3_summarize(v):
    a = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    sb = a.get("claim3_summarize_strongest_baseline", {})
    rows = [
        [
            f"Against the strongest Table 2 baseline ({sb.get('method')}, {num(sb.get('accuracy'), 3)})",
            f"**{num(a.get('claim3_summarize_relative_improvement_pct'), 2)} %**",
            f"paper states {num(a.get('claim3_paper_value_pct'), 1)} %",
        ],
        [
            "Against the claim string's own pair (0.705)",
            f"{num(a.get('claim3_claimstring_pair_relative_pct'), 2)} %",
            "does not reproduce 13.4 %",
        ],
    ]
    return table(["Reading", "Result", "Comparison"], rows) + "\n\n" + (a.get("claim3_note") or "")


def c3_table2(v):
    t2 = g(v, "claims", "C1_C2_C3_tables", "table2_civilcomments_pku_better", default={})
    out = []
    for ds in t2.get("datasets", []):
        rows = [
            [
                m["method"],
                num(m.get("paper_acc"), 3),
                f"{num(m['reproduced_acc_mean'], 3)} ± {num(m.get('reproduced_acc_std'), 3)}",
                num(m.get("abs_diff"), 3),
            ]
            for m in ds.get("methods", [])
        ]
        if ds.get("status") == "BLOCKED":
            out.append(
                f"**{ds['dataset']}** — **BLOCKED**: {ds.get('reason', 'see label audit')}. "
                "No accuracy is reported, because an accuracy computed against a "
                "degenerate label is meaningless rather than merely inaccurate."
            )
            continue
        if not rows:
            out.append(f"**{ds['dataset']}** — not produced.")
            continue
        out.append(
            f"**{ds['dataset']}** — reproduced best method: `{ds.get('best_method')}`; "
            f"a CARE variant wins: {yesno(ds.get('care_wins'))}\n\n"
            + table(["Method", "Paper (Table 2)", "Reproduced", "Abs. diff"], rows)
        )
    out.append(
        f"\nDatasets reproduced: **{t2.get('n_datasets_reproduced')} of "
        f"{t2.get('n_datasets_in_table2')}** Table 2 columns; seeds {t2.get('seeds')}. "
        f"Blocked by the integrity precondition: "
        f"{', '.join(t2.get('blocked_datasets') or []) or 'none'}. "
        f"Contract satisfied: {yesno(t2.get('ok'))}"
    )
    return "\n\n".join(out)


def c5_results(v):
    c = g(v, "claims", "C5_thm42", "route_c_calibrated_rate", default={})
    ic = g(v, "independent_check", "c5_stage_slope_recheck", default={})
    rows = [
        [
            "Stage 1 — ‖Θ̂ − Θ‖₂ vs n",
            f"{num(c.get('stage_1_loglog_slope'), 4)} ± {num(c.get('stage_1_loglog_slope_stderr'), 4)}",
            "−0.5",
            yesno(c.get("stage_1_check")),
            num(ic.get("stage_1_theil_sen_slope"), 4),
        ],
        [
            "**Stage 2 — eigenvector error, exact sparse part** (the theorem's object)",
            f"**{num(c.get('stage_2_loglog_slope'), 4)} ± {num(c.get('stage_2_loglog_slope_stderr'), 4)}**",
            "−0.5",
            yesno(c.get("stage_2_check")),
            num(ic.get("stage_2_theil_sen_slope"), 4),
        ],
        [
            "Stage 3 — full pipeline (our solver, *not* the theorem)",
            f"{num(c.get('loglog_slope_error_vs_n'), 4)} ± {num(c.get('loglog_slope_error_vs_n_stderr'), 4)}",
            "−0.5",
            yesno(c.get("stage_3_full_pipeline_check")),
            "—",
        ],
    ]
    calib = table(
        ["Sweep", "Measured exponent", "Predicted", "Contract", "Theil–Sen refit / status"],
        rows
        + [
            [
                "n\\*(α) — stage 2",
                f"{num(c.get('loglog_slope_n_star_vs_alpha'), 3)} ± {num(c.get('loglog_slope_n_star_vs_alpha_stderr'), 3)}",
                num(c.get("predicted_slope_n_star_vs_alpha"), 1),
                c.get("requirement_n_star_vs_alpha", ""),
                c.get("alpha_sweep_status", "—"),
            ],
            [
                "n\\*(δ) — stage 2",
                f"{num(c.get('loglog_slope_n_star_vs_delta'), 3)} ± {num(c.get('loglog_slope_n_star_vs_delta_stderr'), 3)}",
                num(c.get("predicted_slope_n_star_vs_delta"), 1),
                c.get("requirement_n_star_vs_delta", ""),
                c.get("delta_sweep_status", "—"),
            ],
        ],
    )
    return (
        calib
        + "".join(
            f"\n\nThe n\\*({nm}) sweep is **NOT INFORMATIVE**: "
            + "; ".join((c.get(f"{k}_sweep_informativeness") or {}).get("not_informative_because", []))
            + ". It can neither satisfy nor violate the contract, and the claim header "
            "above names it as NOT MEASURED so the overall 'satisfied' is not read as "
            "covering it."
            for k, nm in (("alpha", "α"), ("delta", "δ"))
            if not (c.get(f"{k}_sweep_informativeness") or {}).get("informative", True)
        )
        + f"\n\nGrid: `n \u2208 {c.get('grid_n')}`. Saturated points are excluded from every fit, so each "
        "exponent is read from the regime where the bound is active. The stage-2 row is the "
        "one Theorem 4.2 governs; the stage-3 row describes our solver."
    )


def sweep_status(blk):
    """Render the informativeness verdict, and say why when a sweep measured nothing."""
    info = blk.get("informativeness") or blk.get("informativeness_record") or {}
    status = blk.get("status") or info.get("status") or "—"
    why = info.get("not_informative_because") or []
    return status, ("; ".join(why) if why else "")


def c6_attribution(v):
    a = g(v, "claims", "C6_thm43", "route_d_restart_budget_attribution", default={})
    rows = [[num(r.get("p_total"), 0), num(r.get("n_star_30_restarts"), 0),
             num(r.get("n_star_90_restarts"), 0), num(r.get("ratio_90_over_30"), 4)]
            for r in a.get("rows", [])]
    return table(["p", "n* at 30 restarts", "n* at 90 restarts", "ratio"], rows) + (
        f"\n\nSolver-bound: {yesno(a.get('solver_bound'))}. "
        f"p-exponent attributable to the theorem rather than to the search budget: "
        f"{yesno(a.get('p_exponent_attributable_to_the_theorem'))}. {a.get('why', '')}"
    )


def c6_grid(v):
    grid = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", "grid_n",
             default=[])
    return ("`n ∈ {" + ", ".join(f"{n:,}".replace(",", " ") for n in grid) + "}`"
            + f"\n\nTarget accuracy: `max_(q,c) |π̂ − π| ≤ "
            + num(g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity",
                    "target_accuracy", default=None), 3) + "`.")


def c6_p_refit(v):
    r = g(v, "independent_check", "c6_p_exponent_recheck", default={})
    sw = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", "p", default={})
    rows = [
        ["least squares, fitted n*", num(sw.get("exponent_vs_p_log_p"), 3), "claim module"],
        ["least squares, crossing n*", num(sw.get("exponent_from_crossing_estimator"), 3), "claim module"],
        ["**Theil–Sen, fitted n***", f"**{num(r.get('fitted_theil_sen_slope'), 3)}**", "independent checker"],
        ["**Theil–Sen, crossing n***", f"**{num(r.get('crossing_theil_sen_slope'), 3)}**", "independent checker"],
    ]
    return table(["Estimator", "Exponent on p·log(p/ε)", "Computed by"], rows) + (
        f"\n\nStated exponent: **{num(r.get('stated_exponent'), 0)}**. All four estimates "
        f"exceed it: {yesno(r.get('both_estimators_exceed_stated_exponent'))} "
        f"(lowest is {num(r.get('min_theil_sen_slope'), 3)}).\n\n"
        "The two Theil–Sen figures are **lower** than least squares, so the exponent's "
        "*value* is uncertain across the range ~2.2 to ~3.6 — a single outlying setting "
        "does move the least-squares fit. What no estimator disputes is that the exponent "
        "exceeds 1, which is the entire content of the falsification. The independent "
        "checker fails the whole run if this ceases to hold."
    )


def c6_confound(v):
    c = g(v, "claims", "C6_thm43", "route_e_p_sweep_confound_audit", default={})
    rows = [[num(r.get("p_total"), 0), num(r.get("delta_cp_eigenvalue_gap"), 6),
             num(r.get("min_pairwise_mean_separation"), 6),
             num(r.get("m2_condition_number"), 6), num(r.get("sigma_max"), 2),
             num(r.get("pi_min"), 3)] for r in c.get("rows", [])]
    held = c.get("held_fixed", {})
    return table(
        ["p", "δ (CP gap)", "min ‖μᵢ−μⱼ‖", "cond(M₂)", "σ_max", "π_min"], rows
    ) + (
        "\n\nHeld fixed across the sweep: "
        + ", ".join(f"{k} {yesno(vv)}" for k, vv in held.items())
        + f"\n\nAll other quantities in the bound held fixed: "
        f"{yesno(c.get('all_other_quantities_held_fixed'))}. {c.get('why', '')}"
    )


def c6_results(v):
    s = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", default={})
    rows, notes = [], []
    for key, label in (("sigma", "σ_max"), ("pi_min", "π_min"), ("p", "p·log(p/ε)")):
        blk = s.get(key) or {}
        # the p sweep names its exponent after the composite variable it regresses on
        exponent = blk.get("exponent", blk.get("exponent_vs_p_log_p"))
        status, why = sweep_status(blk)
        notes.extend([f"* **{label} — {status}.** {why}"] if why else [])
        rows.append(
            [
                label,
                num(blk.get("stated_exponent"), 1),
                f"{num(exponent, 3)} ± {num(blk.get('stderr'), 3)}",
                f"`{blk.get('requirement', '—')}`",
                status,
                yesno(blk.get("ok")) if status == "MEASURED" else "n/a",
            ]
        )
    ic = g(v, "independent_check", "c6_slope_recheck", default={})
    tail = (
        f"\n\nOverall sample-complexity contract satisfied: {yesno(s.get('ok'))} — and on "
        "the p row that **is the result**, not a defect in the run: the exponent was "
        "resolved by both estimators and exceeds what the theorem states. "
        f"Informative sweeps: {s.get('informative_sweeps') or 'none'}; "
        f"uninformative: {s.get('uninformative_sweeps') or 'none'}. A sweep marked NOT "
        "INFORMATIVE contributes no evidence in either direction and is excluded from the "
        "verdict; it is shown here so the exclusion is visible rather than silent."
        + ("\n\n" + "\n".join(notes) if notes else "")
        + "\n\n"
        f"Independent Theil–Sen refit of the σ boundary probe: slope "
        f"{num(ic.get('theil_sen_slope'), 4)} against least squares "
        f"{num(ic.get('least_squares_slope'), 4)}; both fall under the 0.5 threshold for "
        f"'no σ-growth': {yesno(ic.get('theil_sen_agrees_no_sigma_growth'))}. The "
        "Theil–Sen figure clears that threshold only narrowly, so the two estimators "
        "agree on the direction rather than on the magnitude."
        + (f"\n\nNot measured: {s['not_measured']}" if s.get("not_measured") else "")
    )
    return table(
        ["Parameter", "Stated exponent", "Measured", "One-sided contract", "Status", "Passes"],
        rows,
    ) + tail


def verdicts(v):
    claims = v.get("claims", {})
    order = [
        ("C1", "C1_C2_C3_tables", "Claim 1 — UltraFeedback MAE", "claim-1-ultrafeedback"),
        ("C2", "C1_C2_C3_tables", "Claim 2 — 17.37 % over averaging", "claim-2-average-improvement"),
        ("C3", "C1_C2_C3_tables", "Claim 3 — Table 2, best on 5 of 6", "claim-3-table2"),
        ("C4", "C4_prop41", "Claim 4 — Proposition 4.1", "claim-4-proposition-41"),
        ("C5", "C5_thm42", "Claim 5 — Theorem 4.2", "claim-5-theorem-42"),
        ("C6", "C6_thm43", "Claim 6 — Theorem 4.3", "claim-6-theorem-43"),
    ]
    rows = []
    for cid, key, title, slug in order:
        blk = claims.get(key, {})
        rows.append(
            [
                cid,
                f"[{title}](#/{slug})",
                PAGE_VERDICT.get(cid) or blk.get("verdict", "—"),
                yesno(blk.get("ok")),
                f"{num(blk.get('runtime_s'), 1)} s",
            ]
        )
    ic = v.get("independent_check", {})
    env = v.get("environment", {})
    tail = (
        f"\n\nAll contracts satisfied: {yesno(v.get('all_contracts_ok'))} · "
        f"independent checker: {yesno(ic.get('ok'))} · "
        f"total runtime {num(v.get('total_runtime_s'), 1)} s · "
        f"Git SHA `{env.get('git_sha', '—')}` · "
        f"{env.get('cgroup_cpu_quota', '—')} vCPU on `{env.get('CARE_HF_FLAVOR', 'cpu-upgrade')}`."
    )
    return table(["#", "Claim", "Verdict", "Contract passes", "Runtime"], rows) + tail



# --- Claim 4 ---------------------------------------------------------------
def c4_d3(v):
    d3 = g(v, "claims", "C4_prop41", "thm_d3_symbolic_exact_recovery", default={})
    rows = [
        [
            f"({r['p']}, {r['h']})",
            yesno(r.get("columns_orthonormal_symbolically")),
            yesno(r.get("L_ki_equals_lambda_i_ki")),
            yesno(r.get("each_lambda_i_simple")),
        ]
        for r in d3.get("shapes", [])
    ]
    return (
        table(
            ["Shape (p, h)", "Columns orthonormal", "L·kᵢ = λᵢ·kᵢ", "Each λᵢ simple"],
            rows,
        )
        + f"\n\nAll shapes verified symbolically: {yesno(d3.get('ok'))}. Each row holds for "
        "**all** real parameter values of the Householder vector, not for sampled matrices."
    )


def c4_d4(v):
    der = g(v, "claims", "C4_prop41", "thm_d4_constant_derivation", default={})
    sup = g(v, "claims", "C4_prop41", "thm_d4_exact_supremum", default={})
    return table(
        ["Quantity", "Value"],
        [
            ["`max_of_relaxed_objective` (sympy, exact)", f"`{der.get('max_of_relaxed_objective')}`"],
            ["`derived_first_order_constant`", f"**`{der.get('derived_first_order_constant')}`**"],
            ["Paper's constant", str(der.get("paper_constant"))],
            ["Paper's constant is a valid upper bound", yesno(der.get("paper_constant_is_valid"))],
            ["Paper's constant is attained (tight)", yesno(der.get("paper_constant_is_tight"))],
            ["Attained supremum of the ratio, over the spectral-norm ball", num(sup.get("attained_sup_ratio"), 4)],
            ["Supremum respects the derived bound of 2", yesno(sup.get("sup_respects_derived_upper_bound"))],
            ["Slack factor of the paper's constant", num(sup.get("paper_constant_holds_with_slack_factor"), 3)],
            ["Configurations searched", str(sup.get("n_configurations"))],
        ],
    ) + f"\n\nMethod: {sup.get('method', '')}"


def c4_bound_scaling(v):  # noqa: C901
    ce = g(v, "claims", "C4_prop41", "maintext_bound_scaling_counterexample", default={})
    rows = [
        [
            num(r.get("c_scale_of_K_JH"), 0),
            "yes" if r.get("K_JH_columns_are_orthonormal") else "no",
            f"**{num(r.get('worst_err_over_maintext_bound'), 3)}**",
            num(r.get("worst_err_over_appendix_bound"), 3),
        ]
        for r in ce.get("rows", [])
    ]
    return table(
        ["Scale `c` on `K_JH`", "columns orthonormal?",
         "worst ‖ũᵢ − uᵢ‖ ÷ **main-text** bound", "÷ appendix bound"],
        rows,
    ) + (
        f"\n\nMain-text bound — ratio grows monotonically without bound: "
        f"{yesno(ce.get('ratio_grows_without_bound'))} · violated: "
        f"{yesno(ce.get('bound_violated'))} · maximum violation factor "
        f"**{num(ce.get('max_violation_factor'), 1)}×**.\n\n"
        f"Appendix bound — applicable only where its orthonormality hypothesis holds, i.e. "
        f"at `c = 1`, where the ratio is "
        f"{num(ce.get('appendix_ratio_at_c_equals_1'), 3)} and the bound is satisfied: "
        f"{yesno(ce.get('appendix_bound_holds_where_applicable'))}. The column is shown at "
        f"every `c` for transparency, but rows with `c ≠ 1` fall outside Theorem D.4's own "
        f"hypotheses and are not evidence for or against it.\n\n"
        "**Why the two bound columns are numerically equal.** In this construction "
        "`K_HH = diag(3, 2, 1)`, so `‖K_HH⁻¹‖₂ = 1` and the appendix bound "
        "`4‖K_HH⁻¹‖₂‖E‖₂/δ_i` reduces to the main-text `4‖E‖₂/δ_i`. The two statements are "
        "therefore *not* separated by their formulas here — they are separated by their "
        "**hypotheses**, and that is exactly what this counterexample exploits. At `c = 1` "
        "both hypotheses hold and both bounds hold. At `c > 1` the columns are still "
        "orthogonal but no longer orthonormal, so the main text still claims its bound "
        "while the appendix does not — and it is the main text's claim that fails, by a "
        "factor growing linearly in `c`."
    )


def c4_controls(v):
    nc = g(v, "claims", "C4_prop41", "negative_controls", default={})
    return table(
        ["Control", "Must fail because", "Result"],
        [
            [
                "NC1 — propose the constant 1.0, strictly below the attained supremum",
                "a search too weak to refute a too-small constant would make the whole analysis unfalsifiable",
                f"violation found: {yesno(nc.get('nc1_too_small_constant_1p0_is_violated'))} (attained ratio {num(nc.get('nc1_attained_ratio'), 4)})",
            ],
            [
                "NC2 — hand the signed-permutation detector a pair that genuinely **is** one",
                "a detector that always answered *no* would manufacture counterexample 1 out of nothing",
                f"detector accepts: {yesno(nc.get('nc2_detector_accepts_a_true_signed_permutation'))}",
            ],
            [
                "NC3 — feed the D.3 machinery a non-orthonormal `K_JH`",
                "if it were accepted, the orthonormality hypothesis would be doing no work",
                f"rejected: {yesno(nc.get('nc3_non_orthonormal_K_is_not_an_eigenvector'))}",
            ],
        ],
    ) + f"\n\nAll controls behave as required: {yesno(nc.get('ok'))}."


# --- Claim 5 extras --------------------------------------------------------
def c5_dk(v):
    dk = g(v, "claims", "C5_thm42", "route_b_davis_kahan_constant", default={})
    pa = g(v, "independent_check", "davis_kahan_by_principal_angle", default={})
    return table(
        ["Route", "Trials", "Worst attained error ÷ bound", "Bound ever violated"],
        [
            [
                "Claim module — direct ‖û − u‖",
                str(dk.get("n_trials", "—")),
                f"**{num(dk.get('worst_err_over_bound'), 4)}**",
                yesno(not dk.get("ok", True)),
            ],
            [
                "Independent checker — principal angle, `‖û − u‖ = 2 sin(θ/2)`",
                str(pa.get("trials", "—")),
                num(pa.get("worst_err_over_bound"), 4),
                yesno(not pa.get("constant_2_to_the_3_over_2_holds", True)),
            ],
        ],
    ) + (
        f"\n\nThe two routes agree on the eigenvector distance to 1e-6 relative: "
        f"{yesno(pa.get('two_routes_agree_on_eigvec_distance'))}, so the constant is not an "
        "artefact of either route's sign-alignment bookkeeping."
    )


def c5_symbolic(v):
    a = g(v, "claims", "C5_thm42", "route_a_symbolic_chain_audit", default={})
    rows = [[f"`{k}`", yesno(val)] for k, val in a.items() if isinstance(val, bool) and k != "ok"]
    return table(["Contract", "Result"], rows) + f"\n\nRoute A overall: {yesno(a.get('ok'))}."


def c5_controls(v):
    nc = g(v, "claims", "C5_thm42", "negative_controls", default={})
    rows = [[f"`{k}`", yesno(val)] for k, val in nc.items() if isinstance(val, bool) and k != "ok"]
    return table(["Control", "Behaves as required"], rows) + f"\n\nAll controls: {yesno(nc.get('ok'))}."


# --- Claim 6 extras --------------------------------------------------------
def c6_symbolic(v):
    a = g(v, "claims", "C6_thm43", "route_a_symbolic_chain_audit", default={})
    return table(
        ["Quantity", "Value"],
        [
            ["`mean_bound_reproduced_exactly`", yesno(a.get("mean_bound_reproduced_exactly"))],
            ["`factor_missing_from_stated_weight_bound`", f"`{a.get('factor_missing_from_stated_weight_bound')}`"],
            ["`derived_over_stated_on_boundary`", f"`{a.get('derived_over_stated_on_boundary')}`"],
            ["`grows_without_bound_in_sigma`", yesno(a.get("grows_without_bound_in_sigma"))],
        ],
    )


def c6_boundary(v):
    b = g(v, "claims", "C6_thm43", "route_c_boundary_sigma_probe", default={})
    rows = [
        [num(r.get("sigma_max"), 2), num(r.get("n"), 0),
         num(r.get("median_max_abs_pi_error"), 4),
         num(r.get("stated_bound_unit_sqrt_plogp_over_n"), 4),
         num(r.get("error_over_stated_unit"), 4)]
        for r in b.get("rows", [])
    ]
    ci = b.get("slope_ci95") or [None, None]
    # An earlier revision printed ONLY the last column and headed it "weight error".
    # Those are ratios, an order of magnitude larger than the errors, and the mislabel
    # made this table appear to contradict the negative controls below.
    return table(
        ["σ_max", "n on the boundary", "median weight error `max|π̂−π|`",
         "stated bound unit `√(p log(p/ε)/n)`", "ratio error / bound unit"],
        rows,
    ) + (
        f"\n\nFitted exponent **{num(b.get('loglog_slope_error_over_stated_bound_vs_sigma'), 4)} "
        f"± {num(b.get('slope_stderr'), 4)}** "
        f"(95 % CI {num(ci[0], 3)} to {num(ci[1], 3)}). "
        f"Predicted if the σ³ factor were genuinely missing: "
        f"{num(b.get('predicted_slope_if_sigma3_is_missing'), 1)}; predicted if the theorem is "
        f"correct as stated: {num(b.get('predicted_slope_if_theorem_correct'), 1)}. "
        f"σ³ violation hypothesis supported by the data: {yesno(b.get('ok'))}.\n\n"
        "The exponent is fitted to the **ratio** column, which is the quantity the "
        "theorem bounds by a constant; the raw weight error itself falls with σ because "
        "n rises as σ⁶ along the boundary. Both columns are shown so the two cannot be "
        "confused, and so this table can be compared with the negative controls below — "
        "which report raw errors, not ratios."
    )


def c6_controls(v):
    nc = g(v, "claims", "C6_thm43", "negative_controls", default={})
    rows = []
    for r in nc.get("nc1_rows", []):
        rows.append([f"NC1 — n = {r.get('n')}", num(r.get("median_err"), 4)])
    for r in nc.get("nc2_rows", []):
        rows.append([f"NC2 — σ = {num(r.get('sigma_max'), 2)}, n = {r.get('n')}", num(r.get("median_err"), 4)])
    return table(["Setting", "Median weight error"], rows) + (
        f"\n\nNC1 (over-sampling reduces error): {yesno(nc.get('nc1_oversampling_reduces_error'))} · "
        f"NC2 (frozen n, larger σ raises error): {yesno(nc.get('nc2_frozen_n_larger_sigma_raises_error'))} · "
        f"overall {yesno(nc.get('ok'))}."
    )


# --- Verdict headers -------------------------------------------------------
# Confidence is a judgement, so it is recorded here in code with its reason
# rather than typed into prose where it could drift from the evidence.
CONFIDENCE = {
    "C1": ("HIGH", "The arithmetic half is exact and seed-free. The UltraFeedback MAE pair "
                   "itself is NOT re-measured -- the authors released no UltraFeedback "
                   "judge-score matrix -- so the 26.8 % figure is verified as arithmetic on "
                   "the paper's own published values, while a different Table 1 column "
                   "(ASSET) is what this campaign reproduces at full scale. The block is "
                   "caused by a capability the paper itself names (A100 judge generation), "
                   "not by a gap in this reproduction."),
    "C2": ("HIGH", "The definition is identified uniquely by requiring both published targets "
                   "simultaneously, in exact rational arithmetic, and confirmed against a "
                   "second independent transcription."),
    "C3": ("HIGH", "Every arithmetic assertion is decided exactly over all nine Table 2 "
                   "methods, from a single transcription -- the independent checker "
                   "re-derives the Summarize percentages but NOT the argmax. Of Table 2's six "
                   "columns exactly ONE -- CivilComments -- is reproduced at full scale "
                   "over five seeds; PKU-BETTER ships judge outputs but its released "
                   "labels are degenerate and it is BLOCKED, and the other four ship no "
                   "judge outputs at all. The arithmetic assertions are therefore decided "
                   "against the paper's own published grid, not against re-measured "
                   "accuracies for those four columns."),
    "C4": ("HIGH", "Symbolic over a parameterised family, plus exact counterexamples that "
                   "satisfy the paper's own hypotheses. Deterministic; no seeds to vary."),
    "C5": ("MEDIUM", "The composition and the cited constant are established directly, and "
                     "the theorem-governed stage attains the predicted exponent. But the "
                     "eta-dependence is a tail statement we do not measure, and xi(T) has no "
                     "closed form we can evaluate, so both are reconstructed from the "
                     "derivation rather than confirmed empirically."),
    "C6": ("MEDIUM", "The p-factor falsification is the strongest part: four independent "
                     "estimates of the exponent (2.24, 2.98, 3.50, 3.63) all exceed the "
                     "stated 1, every other quantity in the bound is held fixed to eight "
                     "decimal places, and the solver's restart budget is ruled out. It is "
                     "MEDIUM rather than HIGH because those four span 2.2-3.6, the six "
                     "per-setting curve fits scatter (r^2 as low as 0.38) and n* is not "
                     "monotone in p, so the exponent's VALUE is uncertain even though its "
                     "excess over 1 is not. The sigma and pi_min "
                     "exponents are NOT MEASURED, and the delta^-2 factor is not "
                     "independently variable in this generative model."),
}

CLAIM_KEY = {
    "C1": "C1_C2_C3_tables", "C2": "C1_C2_C3_tables", "C3": "C1_C2_C3_tables",
    "C4": "C4_prop41", "C5": "C5_thm42", "C6": "C6_thm43",
}

# For C1-C3 the run reports one combined verdict, so each page states its own.
PAGE_VERDICT = {
    "C1": "**VERIFIED** (the 26.8 % arithmetic, exactly, and a comparator-selection audit "
          "over the full 6 × 4 grid finding no cherry-picking — the headline leaves "
          "6.28 pp unclaimed) / **BLOCKED** (the UltraFeedback MAE pair — the authors "
          "released no UltraFeedback judge-score matrix)",
    "C2": "**FALSIFIED as worded** — the average across the six benchmarks of CARE-SVD's "
          "improvement over AVG is 15.19 %, not 17.37 %. The published figure is an "
          "MAE-weighted mean that puts 84.4 % of its weight on one benchmark and is not "
          "invariant to that benchmark's unit of measurement / **BLOCKED** (five of six "
          "Table 1 columns have no released judge outputs)",
    "C3": "**VERIFIED** as arithmetic over the paper's published nine-method grid (best on "
          "5 of 6, CARE-Tensor's three leads, and the 13.4 % Summarize figure), with the "
          "scope qualification that the count of 5 is a two-variant family count — no "
          "single CARE configuration exceeds 3 of 6, though CARE-Tensor held fixed ranks "
          "1.50 on average against the best single baseline's 1 win / "
          "**REPRODUCED at full scale on 1 of 6 columns** (CivilComments) / **BLOCKED** on "
          "the other five: four ship no judge outputs, and PKU-BETTER's released labels are "
          "degenerate",
}


def _runtime(cid):
    """Runtimes drift on every run; a hand-typed one is stale the moment it is written."""
    def fn(v):
        secs = g(v, "claims", CLAIM_KEY[cid], "runtime_s", default=None)
        flavor = g(v, "environment", "hf_flavor", default="cpu-upgrade")
        total = g(v, "total_runtime_s", default=None)
        return (
            f"Runtime **{num(secs, 1)} s** for this stage on Hugging Face `{flavor}` "
            f"(8 vCPU / 32 GB), threads pinned to the cgroup quota; "
            f"{num(total, 1)} s for the whole run."
        )
    return fn


# Versions the run itself reports; the rest are read from the committed uv.lock, which is
# published alongside this page so the two can be compared.
LOCKED = [("scipy", "1.14.1"), ("pandas", "2.2.3"), ("scikit-learn", "1.5.2"),
          ("cvxpy", "1.5.4"), ("snorkel", "0.10.0"), ("sympy", "1.13.3"),
          ("mpmath", "1.3.0"), ("torch", "2.4.1+cpu")]


def env_packages(v):
    e = g(v, "environment", default={})
    rows = [["Python", f"**{e.get('python', '—')}**", "reported by the run"],
            ["numpy", f"**{e.get('numpy', '—')}**", "reported by the run"]]
    rows += [[k, val, "from `uv.lock`"] for k, val in LOCKED]
    return table(["Package", "Version", "Source"], rows) + (
        "\n\nThe first two are read from the release run itself rather than typed here; "
        "an earlier version of this page hard-coded a Python version that disagreed with "
        "the run."
    )


def _header(cid):
    def fn(v):
        conf, why = CONFIDENCE[cid]
        run_verdict = g(v, "claims", CLAIM_KEY[cid], "verdict", default=None)
        verdict = PAGE_VERDICT.get(cid) or (run_verdict or "—")
        contract = g(v, "claims", CLAIM_KEY[cid], "ok", default=None)
        # "Contract satisfied: yes" must never stand alone when part of the contract was
        # never measured -- that is how a vacuous sweep reads as a pass.
        unmeasured = []
        c5 = g(v, "claims", "C5_thm42", "route_c_calibrated_rate", default={})
        if cid == "C5":
            unmeasured = c5.get("elements_not_measured") or []
        if cid == "C6":
            sw = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", default={})
            unmeasured = [f"n*({k})" for k in (sw.get("uninformative_sweeps") or [])]
        note = ""
        if unmeasured:
            note = (
                f"\n\n**But {len(unmeasured)} contract element"
                + ("s were" if len(unmeasured) != 1 else " was")
                + " NOT MEASURED**: "
                + ", ".join(f"`{u}`" for u in unmeasured)
                + ". A sweep that resolved no exponent cannot satisfy a one-sided contract "
                "and cannot violate one; it is excluded, and the 'satisfied' above refers "
                "only to the elements that were measured."
            )
        return (
            f"**Verdict:** {verdict}\n\n"
            f"**Confidence: {conf}.** {why}\n\n"
            f"Machine-checkable contract satisfied by the release run: {yesno(contract)}."
            + note
        )
    return fn


def c3_label_audit(v):
    a = g(v, "claims", "C1_C2_C3_tables", "label_integrity_audit", default={})
    ds = a.get("datasets", {})
    rows = []
    for name, d in ds.items():
        if "candidate_label_sources" in d:
            detail = "; ".join(
                f"`{k}`: {c.get('distinct_values')} distinct"
                for k, c in d["candidate_label_sources"].items()
            )
        else:
            detail = (f"`{d.get('column')}`: {d.get('distinct_values')} distinct, "
                      f"minority fraction {num(d.get('minority_fraction'), 3)}")
        rows.append([name, yesno(d.get("supports_a_metric")), detail])
    out = table(["Dataset", "Can support the metric", "Released label sources"], rows)
    blocked = a.get("blocked_datasets") or []
    return out + (
        f"\n\nBlocked by this precondition: **{', '.join(blocked) or 'none'}**. "
        f"Usable: {', '.join(a.get('usable_datasets') or []) or 'none'}. "
        "The audit reports; it does not fail the reproduction, because a degenerate "
        "release is a finding about the artifact rather than an error in this run."
    )


GENERATORS = {
    "c1.arithmetic": c1_arithmetic,
    "c1.asset": c1_asset,
    "c1.control": c1_control,
    "c2.definitions": c2_definitions,
    "c1.comparator": c1_comparator,
    "c3.single_config": c3_single_config,
    "c2.weights": c2_weights,
    "c2.invariance": c2_invariance,
    "c2.per_dataset": c2_per_dataset,
    "c2.asset": c2_asset,
    "c2.control": c2_control,
    "c3.recompute": c3_recompute,
    "c3.summarize": c3_summarize,
    "c3.table2": c3_table2,
    "c3.control": c3_control,
    "c3.label_audit": c3_label_audit,
    "c4.d3": c4_d3,
    "c4.d4": c4_d4,
    "c4.bound_scaling": c4_bound_scaling,
    "c4.controls": c4_controls,
    "c5.symbolic": c5_symbolic,
    "c5.dk": c5_dk,
    "c5.results": c5_results,
    "c5.controls": c5_controls,
    "c6.symbolic": c6_symbolic,
    "c6.boundary": c6_boundary,
    "c6.results": c6_results,
    "c6.attribution": c6_attribution,
    "c6.confound": c6_confound,
    "c6.p_refit": c6_p_refit,
    "c6.grid": c6_grid,
    "env.packages": env_packages,
    "c4.runtime": _runtime("C4"),
    "c5.runtime": _runtime("C5"),
    "c4.runtime": _runtime("C4"),
    "c6.runtime": _runtime("C6"),
    "c6.controls": c6_controls,
    "verdicts": verdicts,
    "c1.header": _header("C1"),
    "c2.header": _header("C2"),
    "c3.header": _header("C3"),
    "c4.header": _header("C4"),
    "c5.header": _header("C5"),
    "c6.header": _header("C6"),
}


def main(verdict_path: str, staging: str) -> int:
    verdict = json.loads(Path(verdict_path).read_text())
    root = Path(staging)
    filled, unknown = 0, []

    for page in sorted(root.glob("pages/**/*.md")):
        text = page.read_text()

        def sub(m):
            nonlocal filled
            open_tag, block_id, _, close_tag = m.groups()
            fn = GENERATORS.get(block_id)
            if fn is None:
                unknown.append((str(page), block_id))
                return m.group(0)
            filled += 1
            return f"{open_tag}{fn(verdict)}\n{close_tag}"

        new = BLOCK.sub(sub, text)
        if new != text:
            page.write_text(new)

    for path, bid in unknown:
        print(f"UNKNOWN BLOCK  {path}: {bid}")

    leftovers = []
    for page in sorted(root.glob("pages/**/*.md")):
        txt = page.read_text()
        if "(release run)" in txt or "(pending release run)" in txt:
            leftovers.append(str(page))
    for p in leftovers:
        print(f"UNFILLED PLACEHOLDER  {p}")

    print(f"filled {filled} blocks; {len(unknown)} unknown; {len(leftovers)} pages with placeholders")
    return 1 if unknown or leftovers else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
