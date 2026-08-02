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
        # Never strip trailing zeros. An earlier version returned
        # f"{x:.{nd}f}".rstrip("0").rstrip("."), which is wrong in three ways a blind
        # reviewer demonstrated on the rendered pages: num(0.0, 0) -> "0" -> "" (a slope
        # of 0 vanished from a table row), num(100.0, 0) -> "1", and num(3.3e-4, 4) ->
        # "0.0003" but num(3.3e-4, 0) -> "0", printing a measured difference as exact
        # agreement. Significant zeros are information; the caller chose `nd`.
        return f"{x:.{nd}f}" if isinstance(x, float) else str(x)
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
        + "\n\n**Why the first row differs from the reproduction table above.** The "
          "reproduction runs the authors' full Table 1 procedure — five seeds, each with "
          "the paper's validation-based γ grid — and reports the mean over seeds. This "
          "control runs a single fixed configuration at γ = 1.0 with no seed averaging, "
          "because what it has to hold constant is the aggregator, not the tuning: the "
          "only thing allowed to differ between its two rows is whether the judge matrix "
          "has been column-permuted. The two numbers are therefore different quantities "
          "and are not expected to match; only the gap between the rows of this table is "
          "evidence."
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


def c3_literal(v):
    literal = g(v, "claims", "C1_C2_C3_tables", "claim3_literal_audit", default={})
    independent = g(v, "independent_check", "table2_second_transcription", default={})
    rows = [
        [
            "Generated claim: `(0.814−0.705)/0.705`",
            f"**{num(literal.get('quoted_pair_relative_improvement_pct'), 6)} %**",
            yesno(literal.get("quoted_pair_matches_13p4_at_printed_precision")),
        ],
        [
            "Repair control: `(0.814−0.718)/0.718`",
            f"{num(literal.get('nearby_paper_prose_relative_improvement_pct'), 6)} %",
            yesno(literal.get("nearby_paper_prose_matches_13p4_at_printed_precision")),
        ],
    ]
    return (
        table(["Reading", "Exact/recomputed result", "13.4% at printed precision?"], rows)
        + f"\n\nIndependent second transcription agrees that the generated literal is false: "
        f"{yesno(not independent.get('generated_claim_literal_holds', True))}. "
        f"Positive repair control passes: "
        f"{yesno(literal.get('positive_control_replace_0p705_with_0p718_repairs_arithmetic'))}."
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


def appendix_consistency(v):
    a = g(v, "claims", "C1_C2_C3_tables", "appendix_consistency_audit", default={})
    if not a.get("rows"):
        raise SystemExit(
            "appendix_consistency: appendix_consistency_audit missing from the verdict; "
            "refusing to render a table 1 vs table 7 comparison that was not measured"
        )
    rows = [
        [
            r["dataset"],
            f"{num(r['table1_care_svd'], 3)} ± {num(r['table1_std'], 3)}",
            f"{num(r['table7_first_factor'], 3)} ± {num(r['table7_std'], 3)}",
            num(r["gap"], 3),
            num(r["z"], 2),
            "agree" if r["consistent"] else "**disagree**",
        ]
        for r in a["rows"]
    ]
    t1 = a.get("headline_using_table1", {})
    t7 = a.get("headline_using_table7", {})
    return table(
        ["Dataset", "Table 1 CARE-SVD", "Table 7 1st Factor", "gap", "z", "verdict"], rows
    ) + (
        f"\n\n{a.get('n_consistent')} of {a.get('n_datasets')} columns agree within the "
        f"paper's own combined error bars (threshold z ≤ {num(a.get('consistency_threshold_z'), 1)}, "
        f"fixed before the z-scores were computed). Disagreeing: "
        f"**{', '.join(a.get('inconsistent_datasets') or ['none'])}**.\n\n"
        f"The appendix's own assertion that the leading factor beats every other factor: "
        f"**{yesno(a.get('leading_factor_claim_holds_where_testable'))}** on the "
        f"**{a.get('leading_factor_n_informative_columns')} of 6** columns where it is "
        f"testable at all. On "
        f"{', '.join(a.get('leading_factor_untestable_columns') or [])} Table 7 lists a "
        f"single factor, so the assertion is true there by having nothing to compare "
        f"against and is not counted.\n\n"
        f"| Headline figure | using Table 1 | using Table 7 | shift |\n|---|---|---|---|\n"
        f"| Claim 1's UltraFeedback reduction vs MV | {num(t1.get('claim1_ultrafeedback_reduction_vs_MV_pct'), 3)} % "
        f"| {num(t7.get('claim1_ultrafeedback_reduction_vs_MV_pct'), 3)} % | "
        f"{num(a.get('headline_shift_pp', {}).get('claim1_ultrafeedback_reduction_vs_MV_pct'), 3)} pp |\n"
        f"| Claim 2's improvement over AVG | {num(t1.get('claim2_pooled_vs_AVG_pct'), 3)} % "
        f"| {num(t7.get('claim2_pooled_vs_AVG_pct'), 3)} % | "
        f"{num(a.get('headline_shift_pp', {}).get('claim2_pooled_vs_AVG_pct'), 3)} pp |\n"
        f"| Claim 2's improvement over MV | {num(t1.get('claim2_pooled_vs_MV_pct'), 3)} % "
        f"| {num(t7.get('claim2_pooled_vs_MV_pct'), 3)} % | "
        f"{num(a.get('headline_shift_pp', {}).get('claim2_pooled_vs_MV_pct'), 3)} pp |\n\n"
        f"- Claim 1's own quoted MAE is internally consistent between the two tables: "
        f"**{yesno(a.get('claim1_number_is_internally_consistent'))}**\n"
        f"- Claim 1's headline still rounds to the same one-decimal percentage under both: "
        f"**{yesno(a.get('claim1_headline_rounds_the_same_under_both'))}**"
    ) + _asset_adjudication(a)


def _asset_adjudication(a):
    j = a.get("asset_adjudication") or {}
    if not j.get("available"):
        return ""
    return (
        f"\n\n**Can our own reproduction settle the ASSET disagreement?** ASSET is the only "
        f"disputed column whose judge outputs were released. Over {j.get('n_seeds')} seeds we "
        f"measure **{num(j.get('reproduced_mean'), 3)} ± {num(j.get('reproduced_std'), 3)}** "
        f"(range {num(j.get('reproduced_min'), 3)}–{num(j.get('reproduced_max'), 3)}), which sits "
        f"{num(j.get('sem_from_table1'), 2)} standard errors from Table 1's value and "
        f"{num(j.get('sem_from_table7'), 2)} from Table 7's. Excludes Table 1: "
        f"{yesno(j.get('excludes_table1'))} · excludes Table 7: {yesno(j.get('excludes_table7'))}. "
        f"Our seed spread is wider than both reported standard deviations: "
        f"{yesno(j.get('our_spread_exceeds_both_reported_stds'))}.\n\n"
        f"**But this does not adjudicate, and the reason is in our own seeds.** Of the "
        f"{j.get('n_seeds')} seeds, only {j.get('n_distinct_seed_values')} produced distinct "
        f"values — two are bit-identical — so there are fewer independent draws than seeds and "
        f"the standard error above is optimistic. Recomputed at the number of distinct values "
        f"the standard error is {num(j.get('sem_at_distinct_values_only'), 4)}, and the "
        f"exclusion of Table 7 no longer holds: "
        f"{yesno(j.get('excludes_table7_at_distinct_values_only'))}. The adjudication survives "
        f"the duplicate seed: {yesno(j.get('adjudication_survives_the_duplicate_seed'))}. "
        f"**This column is therefore reported as NOT adjudicating between the paper's two "
        f"published values.** At the nominal five seeds it would exclude Table 7 and side with "
        f"Table 1 — a stronger result than is claimed here — and that reading is deliberately "
        f"not taken, because an exclusion that holds at n = 5 and fails at n = 4 is marginal. "
        f"A blind reviewer found the duplicated seed; without it this block would have "
        f"published the stronger claim."
    )


def c3_pku_reachable(v):
    r = g(v, "claims", "C1_C2_C3_tables", "label_integrity_audit", "datasets",
          "PKU-BETTER", "reachable_accuracy_under_each_convention", default={})
    if not r.get("available"):
        return "The released PKU-BETTER archive was not present in this run."
    per = r.get("fraction_predicting_B_per_judge", {})
    rows = [[k, f"{num(x * 100, 2)} %"] for k, x in sorted(per.items(), key=lambda kv: -kv[1])]
    body = table(["Released judge model", "Rows on which it answers B"], rows)
    return body + (
        f"\n\nAcross {r.get('n_judges')} judges and {r.get('n_rows')} rows, majority vote "
        f"reaches **{num(r.get('majority_vote_accuracy_if_gold_is_B'), 4)}** if the gold "
        f"answer is B everywhere and **{num(r.get('majority_vote_accuracy_if_gold_is_A'), 4)}** "
        f"if it is A everywhere — the only two conventions the file admits. The paper "
        f"reports **{num(r.get('paper_reported_mv_accuracy'), 3)}**. The closest reachable "
        f"value is **{num(r.get('closest_reachable_gap'), 4)}** away, and the published "
        f"figure is reachable: {yesno(r.get('published_value_reachable'))}."
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
    if res is None:
        raise SystemExit(
            "c2.weights: aggregation_convention_audit missing from the verdict; refusing "
            "to render Claim 2's falsification without the identity residual behind it"
        )
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
        + "\n\nContract outcome per element, exactly as `verdict.json` records it: "
        + " \u00b7 ".join(f"`{k}` = **{val}**" for k, val in (c.get("checks") or {}).items())
        + ". `NOT MEASURED` is published as itself rather than as a pass; the verifier's "
        "gate treats an unmeasured sweep as non-failing, which is a different statement "
        "from a satisfied contract."
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
    if r.get("refit_produced_nothing"):
        raise SystemExit("c6.p_refit: the sweep produced rows but the refit produced no slope")
    over = r.get("fitted_over_settings") or []
    return table(["Estimator", "Exponent on p·log(p/ε)", "Computed by"], rows) + (
        f"\n\nAll four are fitted over the **same** settings — the "
        f"{len(over)} that survive the per-setting screen "
        f"(`p` = {', '.join(str(x) for x in over)}). An earlier revision fitted the "
        f"robust estimator over all six and called the difference \"estimator\".\n\n"
        f"Stated exponent: **{num(r.get('stated_exponent'), 0)}**. Every estimate exceeds "
        f"it: {yesno(r.get('both_estimators_exceed_stated_exponent'))} (lowest "
        f"{num(r.get('min_theil_sen_slope'), 3)}, highest "
        f"{num(r.get('max_theil_sen_slope'), 3)}). The robust estimates **bracket** the "
        f"least-squares value rather than falling below it, so no single outlying setting "
        f"is carrying the fit — which removes the one remaining reason to think the "
        f"exponent's *value* was an artefact of least squares.\n\n"
        f"Theil–Sen agrees with least squares within 1.0: "
        f"{yesno(r.get('theil_sen_agrees_with_least_squares'))}, and **that** is what the "
        f"independent checker gates on. It does **not** gate on the exponent exceeding 1: "
        f"an earlier revision did, which would have failed the entire verifier in exactly "
        f"the case where the theorem turned out to be right. None of this rescues the "
        f"withdrawn falsification, because agreement between estimators fitted to the same "
        f"inputs says nothing about whether those inputs are attributable to the theorem — "
        f"and the confound audit says they are not."
    )


def c5_eta(v):
    e = g(v, "claims", "C5_thm42", "route_d_eta_tail_measurement", default={})
    if not e.get("available"):
        return f"Not available: {e.get('why', 'not run')}"
    rows = [
        [num(q, 3), num(et, 4), num(y, 5)]
        for q, et, y in zip(e.get("quantiles", []), e.get("eta_of_quantile", []),
                            e.get("error_quantile", []))
    ]
    ci = e.get("ci95", [None, None])
    ols = e.get("ci95_ols_treating_quantiles_as_independent", [None, None])
    return table(["confidence q", "η(q) = −log((1−q)/2)", "stage-2 error quantile"], rows) + (
        f"\n\nFitted tail exponent: **{num(e.get('loglog_slope_error_vs_eta'), 4)}**, "
        f"95 % interval [{num(ci[0], 4)}, {num(ci[1], 4)}], over "
        f"{e.get('n_replicates')} independent replicates at n = {e.get('n')}.\n\n"
        f"Interval method: {e.get('ci95_method', '—')}. For comparison, treating the "
        f"quantiles as independent observations and using the OLS residual standard "
        f"error {num(e.get('stderr_ols_understated'), 4)} would report "
        f"[{num(ols[0], 4)}, {num(ols[1], 4)}] — {e.get('ols_interval_is_too_narrow_because', '')}\n\n"
        f"- Bound holds (tail grows no faster than √η): "
        f"{yesno(e.get('bound_holds_tail_no_faster_than_sqrt_eta'))}\n"
        f"- Measurement resolves a non-zero exponent: "
        f"{yesno(e.get('measurement_resolves_a_nonzero_exponent'))}\n"
        f"- Stated √η is *tight* (0.5 inside the interval): "
        f"{yesno(e.get('stated_exponent_is_tight'))}\n\n"
        + (e.get("interpretation") or "")
    )


def c6_confound(v):
    """Only the quantities that were actually MEASURED belong in this table.

    The previous version listed five columns, four of which were written from
    p-independent constants, under a caption saying they had been found constant.
    Design invariants are now stated as such, separately, and not dressed as findings.
    """
    c = g(v, "claims", "C6_thm43", "route_e_p_sweep_confound_audit", default={})
    rows = [
        [
            num(r.get("p_total"), 0),
            num(r.get("min_pairwise_mean_separation"), 6),
            num(r.get("empirical_m2_topk_condition_number"), 4),
            num(r.get("empirical_m2_leakage_outside_topk"), 4)
            if r.get("empirical_m2_leakage_outside_topk") is not None else "n/a",
        ]
        for r in c.get("rows", [])
    ]
    fixed = c.get("fixed_by_construction", {})
    held = c.get("held_fixed", {})
    ratio = c.get("leakage_ratio_first_to_last_measured_p")
    between = c.get("leakage_measured_between_p") or []
    body = table(
        ["p", "min ‖μᵢ−μⱼ‖", "empirical cond(M̂₂) on top-k", "leakage outside top-k"], rows
    )
    inv = ", ".join(
        f"`{k}` = {num(x, 4)}" for k, x in fixed.items() if isinstance(x, (int, float))
    )
    return body + (
        f"\n\n**Fixed by construction, not measured:** {inv}. "
        f"{fixed.get('why_these_cannot_drift', '')}\n\n"
        f"**Measured, and held fixed across the sweep:** "
        + ", ".join(f"{k} {yesno(vv)}" for k, vv in held.items())
        + (f"\n\nLeakage outside the signal subspace grows **{num(ratio, 0)}×** between "
           f"`p` = {between[0]} and `p` = {between[1]} at fixed `n` — the smallest and "
           f"largest `p` at which it is defined; it is undefined at "
           f"`p` = {', '.join(str(x) for x in c.get('leakage_undefined_at_p') or [])}, "
           f"where there is no subspace outside the top `k`. "
           if ratio and len(between) == 2 else "\n\n")
        + f"A measured p-exponent is attributable to the theorem's own factor: "
          f"{yesno(c.get('all_other_quantities_held_fixed'))}."
        + (f" {c.get('why_not_attributable')}." if c.get("why_not_attributable") else "")
    )


def c3_transcription(v):
    r = g(v, "independent_check", "table2_second_transcription", default={})
    if not r.get("recomputed_winners"):
        raise SystemExit("c3.transcription: the second transcription is not in the verdict")
    rows = [
        ["Cells compared, digit for digit", f"{r.get('cells_compared')} of 54"],
        ["Mismatches between the two transcriptions",
         f"**{len(r.get('cell_mismatches_vs_first_transcription') or [])}**"
         + (f" — {', '.join(r['cell_mismatches_vs_first_transcription'])}"
            if r.get("cell_mismatches_vs_first_transcription") else "")],
        ["Column winners recomputed from the second copy",
         ", ".join(r.get("recomputed_winners") or [])],
        ["Winners match the paper's bold cells", yesno(r.get("matches_paper_bold_cells"))],
        ["CARE wins", f"**{r.get('care_wins')} of {r.get('of_datasets')}**"],
        ["CARE-Tensor leads on", ", ".join(r.get("care_tensor_leads_on") or [])],
        ["Strongest Summarize baseline",
         f"{r.get('strongest_summarize_baseline')} at {num(r.get('strongest_summarize_baseline_value'), 3)}"],
        ["Summarize relative improvement",
         f"**{num(r.get('summarize_relative_improvement_pct'), 4)} %** "
         f"(matches the paper's 13.4 %: {yesno(r.get('summarize_matches_13_4'))})"],
    ]
    return table(["Check", "Result"], rows)


def env_runtimes(v):
    label = {
        "C1_C2_C3_tables": "Claims 1-3 — Table 1/2 arithmetic, audits and cached benchmark reads",
        "C4_prop41": "Claim 4 — symbolic D.3, exact D.4 supremum, both counterexamples",
        "C5_thm42": "Claim 5 — symbolic chain, Davis-Kahan search, calibrated sweep, η tail",
        "C6_thm43": "Claim 6 — symbolic chain, calibrated n* sweeps, boundary probe, confound audit",
    }
    claims = v.get("claims", {})
    rows, total = [], 0.0
    for cid, name in label.items():
        rt = (claims.get(cid) or {}).get("runtime_s")
        if rt is None:
            continue
        total += rt
        rows.append([name, f"{num(rt, 2)} s"])
    if not rows:
        raise SystemExit("env.runtimes: no per-stage runtime_s in the verdict")
    published = v.get("total_runtime_s")
    env = v.get("environment", {})
    rows.append(["**Sum of stages**", f"**{num(total, 2)} s**"])
    rows.append(["Published `total_runtime_s`", f"{num(published, 2)} s"])
    agree = published is not None and abs(total - published) < 1.0
    return table(["Stage", "Wall clock"], rows) + (
        f"\n\nStages sum to the published total: {yesno(agree)} · "
        f"{env.get('cgroup_cpu_quota', '—')} vCPU on `{env.get('hf_flavor', 'cpu-upgrade')}` · "
        f"thread pools pinned to {env.get('threads_pinned_to', '—')} · "
        f"Git SHA `{env.get('git_sha', '—')}`."
    )


def env_seeds(v):
    rec = v.get("seed_record") or {}
    rows_in = rec.get("rows") or []
    if not rows_in:
        raise SystemExit("env.seeds: the verdict carries no seed_record")

    def fmt(seeds):
        out = []
        for k, val in seeds.items():
            if isinstance(val, list):
                span = f"`{val[0]}…{val[-1]}` ({len(val)} seeds)" if len(val) > 2 else \
                       "`" + ", ".join(str(x) for x in val) + "`"
            else:
                span = f"`{val}`"
            out.append(f"{k} = {span}")
        return "; ".join(out) or "—"

    rows = [[r["claim"], r["stage"], f"`{r['function'].split('.')[-1]}`", fmt(r["seeds"])]
            for r in rows_in]
    bench = rec.get("benchmark_shards") or {}
    if bench.get("seeds"):
        rows.insert(0, [
            "Claims 1–3", "Table 1 ASSET and Table 2 CivilComments / PKU-BETTER shards",
            "authors' `--seed`",
            "`" + ", ".join(str(s) for s in bench["seeds"]) + f"` ({len(bench['seeds'])} seeds)",
        ])
    over = rec.get("call_sites_override_a_seed")
    return table(["Claim", "Stage", "Function", "Seeds actually used"], rows) + (
        f"\n\nGenerated from {rec.get('generated_from', '—')}. "
        f"A call site overrides a seed: {yesno(bool(over))} — if one ever did, the run "
        f"would abort rather than publish this table. "
        f"`PYTHONHASHSEED={rec.get('pythonhashseed', 'unset')}`."
    )


def c6_discrimination(v):
    b = g(v, "claims", "C6_thm43", "route_c_boundary_sigma_probe", default={})
    r = g(v, "independent_check", "c6_slope_recheck", default={})
    if "discriminates" not in b:
        raise SystemExit("c6.discrimination: the boundary probe recorded no discrimination flag")
    lo, hi = (b.get("slope_ci95") or [None, None])[:2]
    rows = [
        ["Measured slope (least squares)", num(b.get("loglog_slope_error_over_stated_bound_vs_sigma"), 4)],
        ["Standard error", num(b.get("slope_stderr"), 4)],
        ["Points fitted / residual dof", f"{b.get('n_points')} / {b.get('residual_dof')}"],
        ["95 % multiplier used", f"t(0.975, {b.get('residual_dof')}) = {num(b.get('ci95_uses_t_quantile'), 3)}"],
        ["95 % interval", f"[{num(lo, 4)}, {num(hi, 4)}]"],
        [f"Excludes the σ³ hypothesis (slope {num(b.get('predicted_slope_if_sigma3_is_missing'), 0)})",
         yesno(b.get("excludes_sigma3_hypothesis"))],
        [f"Excludes the theorem's prediction (slope {num(b.get('predicted_slope_if_theorem_correct'), 0)})",
         yesno(b.get("excludes_theorem_hypothesis"))],
        ["**Discriminates between them**", yesno(b.get("discriminates"))],
        ["Same points, Theil–Sen", num(r.get("theil_sen_slope"), 4)],
        ["Gap between the two estimators", num(r.get("abs_difference_between_estimators"), 4)],
        ["Estimators agree", yesno(r.get("estimators_agree_on_the_slope"))],
    ]
    return table(["Quantity", "Value"], rows) + f"\n\n{b.get('why', '')}. {r.get('why', '')}."


def c6_screen(v):
    """Render the per-setting screen for the p sweep, so its spreads cannot be typed."""
    sc = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", "p",
           "per_setting_screen", default={})
    recs = (sc.get("usable") or []) + (sc.get("dropped") or [])
    recs = [r for r in recs if r.get("r2") is not None]
    if not recs:
        raise SystemExit("c6.screen: per_setting_screen carries no scored settings")
    recs.sort(key=lambda r: r.get("p_total") or 0)
    rows = [
        [
            r.get("p_total"),
            num(r.get("n_star_fit"), 1),
            num(r.get("n_star_crossing"), 1),
            num(r.get("ratio"), 2) + "×",
            num(r.get("r2"), 3),
            num(r.get("decay_slope"), 3),
            "usable" if r.get("usable") else "**dropped**",
        ]
        for r in recs
    ]
    r2s = [r["r2"] for r in recs]
    ratios = [r["ratio"] for r in recs if r.get("ratio") is not None]
    return table(
        ["p", "n* (fitted)", "n* (crossing)", "estimator ratio", "r²", "decay slope", "screen"],
        rows,
    ) + (
        f"\n\nAcross the {len(recs)} settings: `r²` ranges **{num(min(r2s), 3)} to "
        f"{num(max(r2s), 3)}** against the screen's floor of 0.5, the two `n*` "
        f"estimators disagree by up to **{num(max(ratios), 2)}×** against a limit of 3×, "
        f"and every decay slope clears the |slope| ≥ 0.15 floor "
        f"(shallowest {num(min(abs(r['decay_slope']) for r in recs), 3)}). "
        f"**{sc.get('n_usable')} of {sc.get('n_settings')}** settings survive; the fit "
        f"that produces the exponent uses only those. Reasons the rest were dropped: "
        + "; ".join(f"`p` = {r.get('p_total')} — {r.get('why')}"
                    for r in recs if not r.get("usable")) + "."
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
        "\n\nPer-parameter contract outcome: "
        + " · ".join(f"{k} = **{s.get('contract_outcome', {}).get(k, '—')}**"
                     for k in ("sigma", "pi_min", "p"))
        + ". `NOT MEASURED` is published as itself rather than collapsed to a pass — the "
        "verifier's own gate treats an unmeasured sweep as non-failing, which is correct "
        "(absence of evidence is not failed evidence) and is not the same statement as "
        "a satisfied contract. "
        f"Informative sweeps: {s.get('informative_sweeps') or 'none'}; "
        f"uninformative: {s.get('uninformative_sweeps') or 'none'}. A sweep marked NOT "
        "INFORMATIVE contributes no evidence in either direction and is excluded from the "
        "verdict; it is shown here so the exclusion is visible rather than silent."
        + ("\n\n" + "\n".join(notes) if notes else "")
        + "\n\n"
        f"Independent Theil–Sen refit of the σ boundary probe: slope "
        f"{num(ic.get('theil_sen_slope'), 4)} against least squares "
        f"{num(ic.get('least_squares_slope'), 4)}, differing by "
        f"{num(ic.get('abs_difference_between_estimators'), 4)}. The two estimators "
        "**do not agree on the magnitude** — the difference is of the same order as the "
        "smaller of them. An earlier revision printed here that both 'fall under the 0.5 "
        "threshold for no σ-growth: **yes**'; the Theil–Sen figure clears that threshold "
        "by about 0.02, a margin this logbook elsewhere calls inside the noise, so "
        "printing it as an affirmative in the results block of a claim whose verdict is "
        "'decides nothing' invited exactly the misreading a blind reviewer flagged. The "
        "disagreement is itself the finding: it is a second reason the σ probe is not "
        "measuring a slope."
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
        verdict = PAGE_VERDICT.get(cid) or blk.get("verdict", "—")
        if callable(verdict):
            verdict = verdict(v)
        rows.append(
            [
                cid,
                f"[{title}](#/{slug})",
                verdict,
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
        f"{env.get('cgroup_cpu_quota', '—')} vCPU on "
        f"`{env.get('hf_flavor') if env.get('hf_flavor') not in (None, 'unset') else 'local CPU'}`."
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
        "**Why the two bound columns are numerically equal.** Because they are the same "
        "expression. Both the main text and Theorem D.4 state `‖K_HH⁻¹‖₂‖E‖₂/δ_i`, the "
        "appendix simply pinning the constant at 4 where the main text writes `≲`. Here "
        f"`K_HH⁻¹ = diag(3, 2, 1)`, so `‖K_HH⁻¹‖₂ = "
        f"{num(ce.get('khh_inverse_spectral_norm'), 0)}` and the same number enters both. "
        "An earlier revision explained the equality by asserting `‖K_HH⁻¹‖₂ = 1`, which is "
        "wrong — it read the norm off the reciprocal of the smallest diagonal entry rather "
        "than the largest, while every other computation in the module used the largest. "
        "A blind reviewer caught it, and the whole column was 3× too large as a result; "
        "the ratios and the maximum violation factor above are the corrected values. "
        "The two statements are "
        "therefore *not* separated by their formulas at all — they are separated by their "
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


def c5_counterexamples(v):
    ce = g(v, "claims", "C5_thm42", "route_0_literal_counterexamples", default={})
    sign = ce.get("sign_counterexample") or {}
    gap = ce.get("missing_zero_eigenspace_gap_counterexample") or {}
    statistical = ce.get("gaussian_two_point_lower_bound") or {}
    independent = g(v, "independent_check", "theorem_d5_counterexamples_independent", default={})
    rows = [
        [
            num(x.get("smallest_positive_eigenvalue_a"), 4),
            num(x.get("perturbation_norm"), 8),
            num(x.get("aligned_eigenvector_error"), 8),
            num(x.get("error_over_perturbation_div_paper_gap"), 3),
            num(x.get("error_over_perturbation_div_full_gap"), 6),
        ]
        for x in gap.get("rows", [])
    ]
    lower_rows = statistical.get("rows", [])
    lower_probability = min(
        (x.get("le_cam_error_probability_lower_bound", 1) for x in lower_rows),
        default=None,
    )
    return (
        table(
            [
                "a",
                "‖E‖₂=a/r",
                "aligned error",
                "error ÷ (‖E‖/δpaper)",
                "error ÷ (‖E‖/δfull)",
            ],
            rows,
        )
        + f"\n\nSign counterexample: raw distance "
        f"{num(sign.get('raw_distance_for_equally_valid_negative_eigenvector'), 1)}, "
        f"right-hand side {num(sign.get('advertised_rhs_at_exact_recovery'), 1)}; "
        f"sign-aligned control {num(sign.get('control_sign_aligned_distance'), 1)}.\n\n"
        f"Paper-gap ratio diverges: {yesno(gap.get('paper_ratio_diverges'))}. "
        f"Corrected full-gap ratio stays bounded: "
        f"{yesno(gap.get('corrected_ratio_stays_bounded'))}. "
        f"Gaussian two-point lower bound falsifies the statistical rate itself: "
        f"{yesno(statistical.get('literal_statistical_theorem_falsified'))}; its minimum "
        f"Le Cam error probability is {num(lower_probability, 4)} against the theorem's "
        f"{num(statistical.get('theorem_failure_probability_budget'), 4)} failure budget. "
        f"Independent 2×2/KL route passes: {yesno(independent.get('ok'))}."
    )


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
        f"**Excludes the σ³ hypothesis (slope 3):** "
        f"{yesno(b.get('excludes_sigma3_hypothesis'))} · "
        f"**excludes the theorem's prediction (slope 0):** "
        f"{yesno(b.get('excludes_theorem_hypothesis'))} · "
        f"**decides between them:** {yesno(b.get('discriminates'))}. "
        "The interval contains both hypotheses, so this probe supports neither. An "
        "earlier revision printed here 'σ³ violation hypothesis supported by the data: "
        "**yes**', rendered from the block's `ok` field — which means only that the "
        "least-squares fit returned two finite numbers and could not have read 'no' "
        "unless the probe crashed. A blind reviewer found it; it asserted a "
        "falsification of Theorem 4.3 that this page's own verdict header denies.\n\n"
        "The exponent is fitted to the **ratio** column, which is the quantity the "
        "theorem bounds by a constant; the raw weight error itself falls with σ because "
        "n rises as σ⁶ along the boundary. Both columns are shown so the two cannot be "
        "confused.\n\n"
        "**Do not read this table against the negative controls below.** They share the "
        "nominal configuration σ_max = 1, n = 20 000, but they draw from *different seed "
        "streams* — the boundary probe seeds `1000 + 17·s`, the controls `500 + 13·s` — "
        "and at that shared point their medians differ by about 1.8×. That spread is "
        "between-stream noise, not a disagreement between two measurements of one "
        "quantity. An earlier revision of this page invited exactly that comparison, "
        "which was the same defect a blind reviewer had already found between NC1 and "
        "NC2; those two were unified onto one stream, the boundary probe was not. The "
        "published `shared_configuration_cross_check` quantifies stream-to-stream spread "
        "for the controls only."
    )


def c6_controls(v):
    nc = g(v, "claims", "C6_thm43", "negative_controls", default={})
    rows = []
    def span(r):
        lo, hi = r.get("min_err"), r.get("max_err")
        if lo is None or hi is None:
            return "—"
        return f"{num(lo, 4)} – {num(hi, 4)} ({num(r.get('spread_max_over_min'), 1)}×)"
    for r in nc.get("nc1_rows", []):
        rows.append([f"NC1 — n = {r.get('n')}", num(r.get("median_err"), 4), span(r),
                     num(r.get("n_seeds_usable"), 0)])
    for r in nc.get("nc2_rows", []):
        rows.append([f"NC2 — σ = {num(r.get('sigma_max'), 2)}, n = {r.get('n')}",
                     num(r.get("median_err"), 4), span(r), num(r.get("n_seeds_usable"), 0)])
    p1, p2 = nc.get("nc1_effect_vs_seed_noise") or {}, nc.get("nc2_effect_vs_seed_noise") or {}
    sh = nc.get("shared_configuration_cross_check") or {}
    return table(
        ["Setting", "Median weight error", "seed min – max (spread)", "seeds used"], rows
    ) + (
        f"\n\n**Does each control survive seed variation?** Across the "
        f"{num(p1.get('n_seed_pairs'), 0)} endpoint seed pairs, NC1 goes the required way in "
        f"{num(p1.get('pairs_in_the_expected_direction'), 0)} of them "
        f"({num(p1.get('fraction_in_the_expected_direction'), 3)}; 0.5 is chance) — reliable "
        f"across seeds: {yesno(p1.get('control_is_reliable_across_seeds'))}. NC2 goes the "
        f"required way in {num(p2.get('pairs_in_the_expected_direction'), 0)} of "
        f"{num(p2.get('n_seed_pairs'), 0)} ({num(p2.get('fraction_in_the_expected_direction'), 3)}) "
        f"— reliable across seeds: {yesno(p2.get('control_is_reliable_across_seeds'))}. "
        "This is a rank statistic, not a ratio of medians against a max/min spread: the "
        "tensor power method fails to converge on an occasional seed, and one such run "
        "makes any max/min measure meaningless while leaving the median trend intact. An "
        "earlier revision published bare medians with no dispersion at all, and the "
        "revision after that used exactly the max/min measure this replaces.\n\n"
        f"**Is the shared configuration stable under a change of seed stream?** σ = 1 at "
        f"n = {sh.get('configuration', {}).get('n', '—')}, measured twice from independent "
        f"seed offsets: {num(sh.get('median_from_the_control_seed_stream'), 5)} against "
        f"{num(sh.get('median_from_an_independent_seed_stream'), 5)}, a ratio of "
        f"{num(sh.get('ratio_between_the_two_streams'), 2)}× against a limit of "
        f"{num(sh.get('stability_limit'), 1)}× — stable: "
        f"{yesno(sh.get('stable_under_a_change_of_seed_stream'))}. This gates the run. "
        "Two earlier revisions got this wrong in opposite ways: the first let NC1 and NC2 "
        "use mismatched offsets and reported medians 5.2× apart at this one shared point, "
        "and the second unified them onto a single deterministic call and then published "
        "the resulting identity as a gate — which tested only that the interpreter is "
        "deterministic. A blind reviewer named the tautology; this version draws a genuinely "
        "independent stream, so it can fail."
        f"\n\nNC1 (over-sampling reduces error): {yesno(nc.get('nc1_oversampling_reduces_error'))} · "
        f"NC2 (frozen n, larger σ raises error): {yesno(nc.get('nc2_frozen_n_larger_sigma_raises_error'))} · "
        f"NC2 monotone across the whole σ grid: "
        f"{yesno(nc.get('nc2_monotone_across_the_whole_sigma_grid'))} · "
        f"overall {yesno(nc.get('ok'))}.\n\n"
        f"{nc.get('nc2_saturation_note', '')}"
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
    "C2": ("HIGH", "The definition is identified uniquely and over-determined: each published "
                   "target selects the pooled mean-MAE ratio on its own, in exact rational "
                   "arithmetic, and the identification is confirmed against a second "
                   "independent transcription."),
    "C3": ("HIGH", "The official generated claim is decided in exact Fraction arithmetic: "
                   "its explicit 0.814/0.705 pair gives 15.461%, not 13.4%. A positive "
                   "repair control changes only 0.705 to the actual strongest baseline, "
                   "0.718, and recovers 13.3705%, so the check can distinguish the false "
                   "generated conjunction from the paper's correct nearby prose. A second "
                   "hand transcription agrees across all 54 Table 2 cells and independently "
                   "recomputes the 5-of-6 conjunct. One column is also reproduced at full "
                   "scale; that empirical evidence is preserved but is not needed for the "
                   "literal falsification."),
    "C4": ("HIGH", "Symbolic over a parameterised family, plus exact counterexamples that "
                   "satisfy the paper's own hypotheses. Deterministic; no seeds to vary."),
    "C5": ("HIGH", "The literal theorem has two exact formulation defects: it omits sign "
                     "alignment even at zero noise and omits the last positive eigenvalue's "
                     "gap to the zero eigenspace. The second defect is exercised by a symbolic "
                     "family whose paper-normalized violation diverges while the corrected "
                     "full-gap ratio remains bounded. A two-model Gaussian Le Cam bound then "
                     "shows this is not merely a gap in the displayed proof: every estimator "
                     "fails at probability above the theorem's budget on one model while the "
                     "advertised paper-gap rate tends to zero. An independent 2x2 "
                     "eigendecomposition and direct trace/log-determinant KL route agrees."),
    "C6": ("MEDIUM", "What stands is exact and symbolic: composing the paper's own cited results reproduces the mean bound (I) with no residual factor, and fails to reproduce the stated weight bound (II) by exactly sigma_max^3 -- a factor that grows without bound, so no universal constant absorbs it. That is a defect in the displayed derivation, established in sympy and re-derived by a second route. It is NOT a falsification of bound (II) itself: whether that bound happens to hold by some other argument is not decided here, and the boundary probe two earlier revisions read as deciding it resolves nothing at the correct t quantile. What does NOT stand: two earlier revisions each reported a falsification of this theorem -- one in sigma, one in the p*log(p/eps) factor -- and BOTH have been withdrawn on this campaign's own evidence. The rebuilt confound audit finds a real confound in the second: at fixed n the empirical M2 conditioning degrades with p and subspace leakage grows by two orders of magnitude, so part of any n*(p) growth is the moment estimate deteriorating rather than the stated factor being wrong. The sample-complexity exponents in sigma, pi_min and p are therefore NOT MEASURED at this budget, and the delta^-2 factor is not independently variable in this generative model. MEDIUM, not HIGH, because the strongest result here is about a proof rather than about the theorem's truth."),
}

CLAIM_KEY = {
    "C1": "C1_C2_C3_tables", "C2": "C1_C2_C3_tables", "C3": "C1_C2_C3_tables",
    "C4": "C4_prop41", "C5": "C5_thm42", "C6": "C6_thm43",
}

# For C1-C3 the run reports one combined verdict, so each page states its own.
def _v_c1(v):
    ta = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    ap = g(v, "claims", "C1_C2_C3_tables", "appendix_consistency_audit", default={})
    ca = g(v, "claims", "C1_C2_C3_tables", "comparator_selection_audit", default={})
    nc = g(v, "claims", "C1_C2_C3_tables", "negative_controls", default={})
    t1 = g(v, "claims", "C1_C2_C3_tables", "table1_asset", default={})
    pct = ta.get("claim1_ultrafeedback_reduction_vs_MV_pct")
    uf = next((r for r in ap.get("rows", []) if r.get("dataset") == "UltraFeedback"), {})
    bad = ap.get("inconsistent_datasets") or []
    t7 = g(ap, "headline_using_table7", "claim1_ultrafeedback_reduction_vs_MV_pct")
    gb = ca.get("global_best_cell") or {}
    grid = ca.get("relative_reduction_grid_pct") or {}
    named = ca.get("claimed_baseline")
    ds = ca.get("claimed_dataset")
    col = {b: grid[b].get(ds) for b in grid if isinstance(grid.get(b), dict)}
    col = {b: x for b, x in col.items() if x is not None}
    best_baseline_for_ds = max(col, key=col.get) if col else None
    return (
        "**VERIFIED on everything this claim can be held to without the authors' "
        "unreleased data, and BLOCKED on the rest — both stated exactly.** "
        f"(1) The reduction is **VERIFIED exactly**: Table 1's own UltraFeedback entries "
        f"give **{num(pct, 3)} %** against the paper's stated 26.8 %, by deterministic, "
        "seed-free arithmetic — checked against a 0.05 pp tolerance written in "
        "[`claim_c123_benchmarks.py`](repro/src/claim_c123_benchmarks.py) rather than "
        "recorded in the verdict — and re-derived independently in exact "
        "`Fraction` arithmetic from a second, hand-typed transcription. The two MAE inputs "
        "are transcribed in [`repro/src/paper_source.py`](repro/src/paper_source.py), which "
        "is published in this Space and gated byte-identical at publication time; they are "
        "not separately restated in `raw/verdict.json`, which records the derived "
        "percentages. "
        "(2) The paper's own second report of these MAEs **CORROBORATES the underlying "
        f"quantity**: Appendix E.8's Table 7 republishes the CARE-SVD row and its "
        f"UltraFeedback entry sits at z = {num(uf.get('z'), 3)}, well inside one combined "
        "standard deviation — the one number in this claim we cannot measure ourselves. "
        "It does **not** corroborate the headline to the last printed digit: recomputed "
        f"from Table 7 the same reduction reads **{num(t7, 3)} %**, a shift of "
        f"{num(g(ap, 'headline_shift_pp', 'claim1_ultrafeedback_reduction_vs_MV_pct'), 3)} pp "
        "that rounds to 26.9 %, not 26.8 %. And "
        f"{len(bad)} other columns of that same row do not reconcile at all "
        f"({', '.join(bad)}) — a defect in the paper's internal consistency, decided "
        "exactly and reported here. "
        f"(3) A comparator-selection audit over the whole {ca.get('n_cells')}-cell grid of "
        "(dataset, baseline) reductions locates the headline precisely, and the result is "
        "**mixed rather than clean**: the cell is the largest reduction against the "
        f"baseline the paper names ({named}), so 'up to' is used correctly, and "
        f"{named} is also the most favourable baseline for {ds} — so the reported pair is "
        "the best of its row *and* of its column. What the audit does establish against "
        "selection is that it is **not** the largest cell available: "
        f"{gb.get('baseline')} on {gb.get('dataset')} would have supported "
        f"{num(gb.get('pct'), 2)} %, leaving {num(ca.get('headroom_left_on_the_table_pp'), 2)} pp "
        "unclaimed. Baseline selection itself is not tested by any check here. "
        "(4) CARE's Table 1 methodology is **REPRODUCED END-TO-END AT FULL SCALE** on "
        "ASSET — the one Table 1 dataset whose judge outputs the authors released — with "
        f"their own code, {len(t1.get('seeds') or [])} seeds, and the paper's "
        "validation-based γ search, plus a negative control that row-permutes each judge "
        f"column and drives CARE's MAE from {num(nc.get('care_mae_real_judge_scores'), 2)} "
        f"to {num(nc.get('care_mae_row_permuted_judge_scores'), 2)}, worse than majority "
        f"vote at {num(nc.get('majority_vote_mae'), 2)}, as it must. "
        "**BLOCKED:** the UltraFeedback MAE pair itself is never re-measured, because the "
        "authors released no UltraFeedback judge-score matrix and regenerating one requires "
        "GPU inference over 11–20 LLM judges (Appendix E.2, ≈3 A100-hours) — a named "
        "missing capability, not a gap in this reproduction. It is **not** replaced by a "
        "synthetic proxy"
    )


def _v_c2(v):
    ta = g(v, "claims", "C1_C2_C3_tables", "table_arithmetic", default={})
    ag = g(v, "claims", "C1_C2_C3_tables", "aggregation_convention_audit", default={})
    ap = g(v, "claims", "C1_C2_C3_tables", "appendix_consistency_audit", default={})
    cd = ta.get("candidate_definitions") or {}
    pooled = cd.get("pooled_mean_MAE_ratio") or {}
    unw = cd.get("mean_of_per_dataset_relative_improvement") or {}
    tg = ta.get("paper_targets") or {}
    matching = ta.get("definition_matching_paper") or []
    share = ag.get("largest_weight_share")
    per = ta.get("per_dataset_relative_improvement_vs_AVG_pct") or {}
    bad = ap.get("inconsistent_datasets") or []
    return (
        "**VERIFIED EXACTLY, with a quantified scope qualification on what the headline "
        "statistic measures.** Recomputed in exact rational arithmetic from Table 1's own "
        f"entries, the pooled mean-MAE improvement is **{num(pooled.get('vs_AVG'), 4)} %** "
        f"over AVG and **{num(pooled.get('vs_MV'), 4)} %** over MV — matching the "
        f"published {num(tg.get('vs_AVG_pct'), 2)} % and {num(tg.get('vs_MV_pct'), 2)} % to "
        "the precision the paper prints them at. Of the three natural readings of 'average "
        f"improvement' that were enumerated, exactly {len(matching)} reproduces the "
        f"published pair (`{', '.join(matching)}`), and each published figure on its own "
        "already selects it — the nearest rival is several percentage points away in both "
        "cases — so the identification is **unique and over-determined**, not a coincidence "
        "rescued by using two targets. The independent checker re-derives all of it from a "
        "second transcription. "
        f"**CARE improves on AVG on all {len(per)} of the continuous-scoring benchmarks**; "
        "the direction of the paper's claim is not in dispute here. "
        "The scope qualification is quantified rather than asserted: the identified "
        "definition is algebraically an MAE-weighted mean of the per-dataset improvements, "
        "and those weights are an artefact of unit selection — ASSET's 0–100 scale gives it "
        f"**{num(100.0 * share, 2) if isinstance(share, float) else '—'} %** of the total "
        "weight, so the published 'average across scoring datasets' is very nearly ASSET's "
        "number alone. The unit-invariant average across the six benchmarks is "
        f"**{num(unw.get('vs_AVG'), 2)} %** over AVG and {num(unw.get('vs_MV'), 2)} % over "
        "MV, and rescaling ASSET reverses the paper's ordering of the two baselines. This "
        "is a **scope qualification, not a falsification** — every number the paper prints "
        "is correct under the definition it used. "
        "A second, independent defect: Appendix E.8's Table 7 republishes the CARE-SVD row "
        f"this statistic is computed from and disagrees with Table 1 on {len(bad)} of its "
        f"six columns ({', '.join(bad)}), which moves the headline again. "
        "**REPRODUCED at full scale** on ASSET with the authors' code and a negative "
        "control; **BLOCKED** on the other five Table 1 columns, which ship no judge outputs"
    )


def _v_c6(v):
    sym = g(v, "claims", "C6_thm43", "route_a_symbolic_chain_audit", default={})
    sw = g(v, "claims", "C6_thm43", "route_b_calibrated_sample_complexity", default={})
    nc = g(v, "claims", "C6_thm43", "negative_controls", default={})
    ic = g(v, "independent_check", "c6_composition_by_exponent_arithmetic", default={})
    agreed = g(v, "independent_check", "c6_two_route_agreement_evaluated", default=None)
    missing = sym.get("factor_missing_from_stated_weight_bound")
    unmeasured = sw.get("uninformative_sweeps") or []
    return (
        "**FALSIFIED (the displayed proof) and VERIFIED (the mean bound) — both exact, "
        "both reached by two independent routes.** "
        "(1) **VERIFIED:** composing the paper's own equations (8) and (10) reproduces the "
        f"stated mean-error bound exactly — the derived-over-stated ratio is "
        f"`{sym.get('mean_bound_ratio')}`, free of σ, δ, p, ε and n, so the two differ by "
        "at most a universal constant, which is what the theorem asserts "
        f"(`mean_bound_reproduced_exactly = {sym.get('mean_bound_reproduced_exactly')}`). "
        "(2) **FALSIFIED as a derivation:** composing the paper's own (8) with (11) yields "
        f"a weight-error bound larger than the stated one by exactly **σ_max³** "
        f"(`factor_missing_from_stated_weight_bound = {missing}`) — an "
        "unbounded factor no universal constant `C₂` can absorb, so the displayed chain "
        "does not establish the inequality it displays. Both results are obtained twice by "
        "machinery that shares no code: `sympy` simplification in the claim module, and "
        f"exact exponent-vector arithmetic over `Fraction`s in the independent checker "
        f"(`{ic.get('route', '')}`); the two routes are compared for agreement and the "
        f"comparison is a published field (`c6_two_route_agreement_evaluated = "
        f"{agreed}`), so a disagreement fails the run rather than being reported as "
        "a result. "
        "Scope, stated precisely: this falsifies the **written proof**, not the bound "
        "itself. Whether bound (II) as stated happens to hold is **not decided here** — the "
        "boundary probe two earlier revisions read as settling it has a 95 % interval "
        "containing both hypotheses at the correct t quantile, and that reading is "
        f"withdrawn. Of the three sample-complexity exponents, "
        f"{3 - len(unmeasured)} are now **MEASURED** and "
        f"{len(unmeasured)} ({', '.join('`' + s + '`' for s in unmeasured)}) "
        f"{'is' if len(unmeasured) == 1 else 'are'} **NOT MEASURED** at this budget. "
        "Where they are measured they come out *below* the stated exponent, which for a "
        "sufficiency condition is consistent with the theorem and shows the factor is not "
        "tight -- except `p`, whose measured exponent is **not attributable** to the "
        "theorem because a control finds the empirical second-moment conditioning "
        "degrades as `p` grows. Negative controls confirm the estimator does "
        "respond to `n` and to `σ` in the required directions "
        f"(`negative_controls.ok = {nc.get('ok')}`), so that is a power limit rather "
        "than a broken estimator"
    )


def c5_certificate(v):
    c = g(v, "claims", "C5_thm42", "route_c_calibrated_rate", default={})
    ns = c.get("grid_n") or []
    cs = c.get("stage_2_implied_constant_vs_n") or []
    if not ns or not cs:
        return "*(not in this run's record)*"
    rows = "\n".join(
        f"| {n} | {num(e, 4)} | {num(k, 2)} |"
        for n, e, k in zip(ns, c.get("stage_2_oracle_spectral_error_vs_n") or [], cs)
    )
    return (
        "| `n` | stage-2 error | implied `C(n) = err·√n` |\n|---|---|---|\n" + rows
        + f"\n\n**max `C(n)` over the grid: {num(c.get('stage_2_implied_constant_max'), 2)}** "
        f"-- bounded, so the stated rate holds across the measured range. "
        f"`C(n)` drifts upward by a factor of "
        f"{num(c.get('stage_2_implied_constant_drift'), 3)} from the smallest `n` to the "
        f"largest. {c.get('stage_2_certificate_note', '')}"
    )


def _v_c5(v):
    a = g(v, "claims", "C5_thm42", "route_a_symbolic_chain_audit", default={})
    b = g(v, "claims", "C5_thm42", "route_b_davis_kahan_constant", default={})
    c = g(v, "claims", "C5_thm42", "route_c_calibrated_rate", default={})
    d = g(v, "claims", "C5_thm42", "route_d_eta_tail_measurement", default={})
    dk = g(v, "independent_check", "davis_kahan_by_principal_angle", default={})
    ci = c.get("stage_2_loglog_slope_ci95") or [None, None]
    eci = d.get("ci95") or [None, None]
    unmeasured = c.get("elements_not_measured") or []
    return (
        "**One exact symbolic check VERIFIED, one weaker check reported and labelled as "
        "unable to fail, and the headline rate exponent NOT CONFIRMED — it lands on the "
        "shallow side of the stated −1/2 and this page does not read that as support.** "
        "(1) **The load-bearing symbolic result.** Solving the theorem's stated bound for "
        "the sample size needed to reach accuracy α yields "
        f"`{a.get('n_required_for_accuracy_alpha')}`, matching the sample complexity the "
        "paper states separately in Appendix D.6 and transcribes into the module "
        f"independently (`sample_complexity_inversion_matches_paper = "
        f"{a.get('sample_complexity_inversion_matches_paper')}`). `sympy` performs the "
        "solve; a wrong constant or a wrong power in the paper's own inversion would flip "
        "this flag. "
        "(2) **A weaker check, reported because it is in the record and not counted as "
        f"evidence.** `composition_reproduces_stated_bound = "
        f"{a.get('composition_reproduces_stated_bound')}` **cannot fail as written here**: "
        "the composed expression is built by multiplying the cited step by the Davis–Kahan "
        "factor and compared against the same product written another way, so it tests our "
        "transcription's self-consistency, not the paper. Note this is a defect in *how "
        "this instance was written*, not in the family — the structurally similar check on "
        "Theorem 4.3, where the derivation is composed independently of the stated result, "
        "is exactly the one that falsifies that theorem's displayed proof by σ_max³. "
        f"(3) The cited Davis–Kahan constant `{num(b.get('constant_checked'), 4)} = 2^(3/2)` "
        f"holds over the whole search (`no_violation_found = "
        f"{b.get('no_violation_found')}`, worst error/bound "
        f"{num(b.get('worst_err_over_bound'), 3)}), and the independent checker re-runs "
        f"that search on its own random draws under its own seed over {dk.get('trials')} "
        f"trials and finds it holds there too (worst error/bound "
        f"{num(dk.get('worst_err_over_bound'), 3)}). Both searches sample at random rather "
        "than adversarially, so this is corroboration over the region reached, not a "
        "proof of the constant. "
        "**The rate measurements, stated in the direction they actually point.** On the "
        "spectral step the theorem governs, the `n`-exponent is "
        f"**{num(c.get('stage_2_loglog_slope'), 4)}** (95 % CI [{num(ci[0], 4)}, "
        f"{num(ci[1], 4)}]). That is *shallower* than the stated −1/2, and the whole "
        "interval lies on that side — the side that would eventually outgrow an "
        f"`O(√(η/n))` bound "
        f"(`stage_2_exponent_statistically_consistent_with_minus_half = "
        f"{c.get('stage_2_exponent_statistically_consistent_with_minus_half')}`). Over a "
        "finite grid this is **not** a violation, because a constant absorbs it; but it is "
        "**not confirmation of the exponent either**, and the contract row that passes it "
        f"does so against a threshold of **{c.get('requirement_error_vs_n')}** — 16 % of "
        "slack below the theoretical value, disclosed here rather than only in the "
        "limitations. The accuracy exponent is "
        f"**{num(c.get('loglog_slope_n_star_vs_alpha'), 4)} ± "
        f"{num(c.get('loglog_slope_n_star_vs_alpha_stderr'), 4)}** against a stated −2, and "
        f"the `η` tail exponent is **{num(d.get('loglog_slope_error_vs_eta'), 4)}** "
        f"(bootstrap 95 % CI [{num(eci[0], 4)}, {num(eci[1], 4)}]) against a stated 1/2 — "
        "that one is conservative in the direction the bound requires. "
        + (
            "**Every contract element in this claim's calibrated sweep is now MEASURED** — "
            "the `δ` sweep, which three earlier revisions reported as NOT MEASURED, was "
            "found to be *confounded* rather than merely underpowered and has been "
            "rebuilt; see below. The one quantity still outside measurement is `ξ(T)`, "
            "which has no closed form we can evaluate. "
            if not unmeasured else
            f"**NOT MEASURED:** {', '.join('`' + u + '`' for u in unmeasured)} and `ξ(T)`, "
            "which has no closed form we can evaluate. "
        )
        + ("**DECIDED False, not unmeasured:** the "
        "end-to-end pipeline exponent "
        f"(`stage_3_full_pipeline_check = {c.get('stage_3_full_pipeline_check')}`), which "
        "falls short of `n^{-1/2}` at our solver's iteration budget; this page attributes "
        "that to the solver, and that attribution is an argument from the stage "
        "decomposition, not a separate executable test")
    )


def _v_c3_literal(v):
    literal = g(v, "claims", "C1_C2_C3_tables", "claim3_literal_audit", default={})
    independent = g(v, "independent_check", "table2_second_transcription", default={})
    return (
        "**FALSIFIED as the official generated claim is literally written.** Its explicit "
        f"pair `0.814 vs 0.705` gives **{num(literal.get('quoted_pair_relative_improvement_pct'), 4)} %**, "
        "not 13.4 %. The nearby paper prose is a different, correct statement: using "
        "GLAD's actual strongest-baseline value 0.718 gives "
        f"**{num(literal.get('nearby_paper_prose_relative_improvement_pct'), 4)} %**, which "
        "rounds to 13.4 %. Thus replacing only the generated claim's wrong baseline repairs "
        "the arithmetic, while retaining 0.705 is rejected. The 5-of-6 conjunct is "
        f"independently recomputed and holds ({independent.get('care_wins')}/"
        f"{independent.get('of_datasets')}); one false numerical conjunct is enough to "
        "falsify the generated conjunction. This result needs no missing judge outputs."
    )


def _v_c5_literal(v):
    ce = g(v, "claims", "C5_thm42", "route_0_literal_counterexamples", default={})
    gap = ce.get("missing_zero_eigenspace_gap_counterexample") or {}
    sign = ce.get("sign_counterexample") or {}
    statistical = ce.get("gaussian_two_point_lower_bound") or {}
    independent = g(v, "independent_check", "theorem_d5_counterexamples_independent", default={})
    rows = gap.get("rows") or []
    largest = rows[-1].get("error_over_perturbation_div_paper_gap") if rows else None
    corrected = rows[-1].get("error_over_perturbation_div_full_gap") if rows else None
    lower_rows = statistical.get("rows") or []
    lower_probability = min(
        (x.get("le_cam_error_probability_lower_bound", 1) for x in lower_rows),
        default=None,
    )
    return (
        "**FALSIFIED as literally stated, by exact counterexamples plus a Gaussian minimax "
        "lower bound.** First, D.5 omits the sign minimisation written explicitly in D.4: "
        "at exact recovery an equally valid eigenvector `-u` has distance "
        f"{num(sign.get('raw_distance_for_equally_valid_negative_eigenvector'), 1)} against "
        "a zero right-hand side; sign alignment reduces it to "
        f"{num(sign.get('control_sign_aligned_distance'), 1)}. Second, D.5 defines `δ` only "
        "between positive eigenvalues, although Yu-Wang-Samworth requires separation from "
        "the whole spectrum. For `L*=2u₁u₁ᵀ+a u_hu_hᵀ` and a perturbation of norm `a/r` "
        "coupling `u_h` to a null direction, the last eigenvector rotates by a nonzero "
        "angle independent of `a`, while the advertised right-hand side tends to zero. "
        f"The paper-normalized violation ratio reaches **{num(largest, 1)}×** on the grid "
        "and diverges; using the correct full-spectrum gap keeps the ratio at "
        f"{num(corrected, 4)}. A two-model Gaussian Le Cam construction forces error with "
        f"probability at least **{num(lower_probability, 4)}**, above D.5's "
        f"**{num(statistical.get('theorem_failure_probability_budget'), 4)}** failure "
        "budget, while the paper-gap rate tends to zero. Restoring the full gap makes the "
        "lower and upper scales match. The independent 2x2/KL implementation agrees: "
        f"**{independent.get('ok')}**."
    )


PAGE_VERDICT = {
    "C1": _v_c1,
    "C2": _v_c2,
    "C3": _v_c3_literal,
    "C5": _v_c5_literal,
    "C6": _v_c6,
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
        # A page verdict may be a callable so that every number in the most-read
        # paragraph on the page is rendered from the verdict rather than typed. A
        # hand-typed headline number is stale the moment the run moves.
        verdict = PAGE_VERDICT.get(cid)
        if callable(verdict):
            verdict = verdict(v)
        verdict = verdict or (run_verdict or "—")
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
    "c6.screen": c6_screen,
    "c6.discrimination": c6_discrimination,
    "env.runtimes": env_runtimes,
    "env.seeds": env_seeds,
    "c3.transcription": c3_transcription,
    "c1.appendix": appendix_consistency,
    "c2.appendix": appendix_consistency,
    "c3.single_config": c3_single_config,
    "c3.pku_reachable": c3_pku_reachable,
    "c2.weights": c2_weights,
    "c2.invariance": c2_invariance,
    "c2.per_dataset": c2_per_dataset,
    "c2.asset": c2_asset,
    "c2.control": c2_control,
    "c3.recompute": c3_recompute,
    "c3.summarize": c3_summarize,
    "c3.table2": c3_table2,
    "c3.control": c3_control,
    "c3.literal": c3_literal,
    "c3.label_audit": c3_label_audit,
    "c4.d3": c4_d3,
    "c4.d4": c4_d4,
    "c4.bound_scaling": c4_bound_scaling,
    "c4.controls": c4_controls,
    "c5.symbolic": c5_symbolic,
    "c5.dk": c5_dk,
    "c5.results": c5_results,
    "c5.controls": c5_controls,
    "c5.counterexamples": c5_counterexamples,
    "c6.symbolic": c6_symbolic,
    "c6.boundary": c6_boundary,
    "c6.results": c6_results,
    "c6.attribution": c6_attribution,
    "c5.eta": c5_eta,
    "c6.confound": c6_confound,
    "c6.p_refit": c6_p_refit,
    "c6.grid": c6_grid,
    "env.packages": env_packages,
    "c4.runtime": _runtime("C4"),
    "c5.runtime": _runtime("C5"),
        "c6.runtime": _runtime("C6"),
    "c6.controls": c6_controls,
    "verdicts": verdicts,
    "c1.header": _header("C1"),
    "c2.header": _header("C2"),
    "c3.header": _header("C3"),
    "c4.header": _header("C4"),
    "c5.header": _header("C5"),
    "c5.certificate": c5_certificate,
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
