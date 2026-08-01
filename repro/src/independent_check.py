"""Independent checker.

Deliberately re-derives the load-bearing numbers by *different* routes from the
claim modules, so that a bug in one implementation cannot pass unnoticed:

  * Table 1/2 percentages: exact rational arithmetic on a second, hand-typed copy
    of the table, not the one in paper_source.py.
  * Table 2's full nine-method grid: typed a second time and compared cell by cell, so
    Claim 3's argmax over 54 cells does not rest on one transcription.
  * Proposition 4.1 counterexample: 60-digit mpmath, not sympy.
  * The first-order eigenvector perturbation used for Theorem D.4's constant:
    central finite differences on the true eigenvector, not the analytic formula.
  * Theorem 4.3's sigma sweep slope: Theil-Sen, not least squares.

Run standalone or import `run(verdict)` to cross-check a verdict JSON.
"""

from __future__ import annotations

import itertools
from fractions import Fraction

import math

import mpmath as mp

import numpy as np


# --- 1. table arithmetic, exact rationals, second transcription -------------
_T1_AVG = ["33.663", "0.830", "2.274", "1.394", "0.686", "1.037"]
_T1_MV = ["31.153", "0.822", "2.608", "1.417", "0.851", "0.923"]
_T1_CARE = ["27.629", "0.730", "1.957", "1.325", "0.623", "0.694"]
# Second, hand-typed copy of Appendix E.8 Table 7's "1st Factor" row (mean, std).
_T7_FIRST = ["27.148", "0.753", "1.950", "1.325", "0.622", "0.694"]
_T7_FIRST_STD = ["0.133", "0.003", "0.006", "0.003", "0.006", "0.005"]
_T1_CARE_STD = ["0.156", "0.002", "0.018", "0.004", "0.006", "0.004"]


# Second, hand-typed copy of Table 2 -- nine methods x six datasets -- typed from the
# paper independently of paper_source.py. Without this the whole "best on 5 of 6" verdict
# rested on ONE transcription of a 54-cell grid, in which a single wrong digit could flip
# a column winner and nothing would catch it. Bold cells are typed separately too, so the
# recomputed argmax can be checked against what the paper actually typesets.
_T2_DATASETS = ["Chatbot-Arena", "CivilComments", "PKU-BETTER", "PKU-SAFER", "SHP", "Summarize"]
_T2 = {
    "MV":          ["0.517", "0.691", "0.701", "0.698", "0.626", "0.600"],
    "AVG":         ["0.551", "0.690", "0.726", "0.717", "0.634", "0.683"],
    "WS":          ["0.543", "0.739", "0.575", "0.570", "0.619", "0.705"],
    "UWS":         ["0.507", "0.713", "0.703", "0.701", "0.629", "0.713"],
    "Dawid-Skene": ["0.546", "0.735", "0.551", "0.548", "0.612", "0.705"],
    "GLAD":        ["0.510", "0.695", "0.697", "0.671", "0.644", "0.718"],
    "MACE":        ["0.550", "0.732", "0.734", "0.735", "0.580", "0.706"],
    "CARE-SVD":    ["0.580", "0.778", "0.691", "0.690", "0.543", "0.695"],
    "CARE-Tensor": ["0.564", "0.749", "0.779", "0.731", "0.695", "0.814"],
}
_T2_BOLD = ["CARE-SVD", "CARE-SVD", "CARE-Tensor", "MACE", "CARE-Tensor", "CARE-Tensor"]
_T2_CARE = ("CARE-SVD", "CARE-Tensor")


def table2_second_transcription(verdict: dict | None = None) -> dict:
    """Recompute Claim 3's structure from an independent copy of the nine-method grid.

    Exact rationals throughout: an accuracy typed to three decimals is a rational, and
    an argmax over rationals has no tolerance to tune.
    """
    grid = {m: [Fraction(x) for x in row] for m, row in _T2.items()}
    winners, care_wins, tensor_leads = [], 0, []
    for j in range(len(_T2_DATASETS)):
        col = {m: v[j] for m, v in grid.items()}
        w = max(col, key=col.get)
        winners.append(w)
        if w in _T2_CARE:
            care_wins += 1
        if w == "CARE-Tensor":
            tensor_leads.append(_T2_DATASETS[j])

    j = _T2_DATASETS.index("Summarize")
    baselines = {m: grid[m][j] for m in grid if m not in _T2_CARE}
    strongest = max(baselines, key=baselines.get)
    rel = (grid["CARE-Tensor"][j] - baselines[strongest]) / baselines[strongest] * 100

    out = {
        "recomputed_winners": winners,
        "matches_paper_bold_cells": winners == _T2_BOLD,
        "care_wins": care_wins,
        "of_datasets": len(_T2_DATASETS),
        "care_best_on_5_of_6": care_wins == 5,
        "care_tensor_leads_on": tensor_leads,
        "strongest_summarize_baseline": strongest,
        "strongest_summarize_baseline_value": float(baselines[strongest]),
        "summarize_relative_improvement_pct": float(rel),
        "summarize_matches_13_4": abs(float(rel) - 13.4) < 0.1,
    }
    if verdict:
        # Cell-by-cell against the first transcription: this is the check that a wrong
        # digit cannot survive, and it is stricter than agreeing on the argmax.
        from paper_source import TABLE2_ACC
        mismatch = [
            f"{m}[{_T2_DATASETS[j]}]"
            for m, row in _T2.items()
            for j, x in enumerate(row)
            if m in TABLE2_ACC and abs(float(Fraction(x)) - TABLE2_ACC[m][j]) > 1e-12
        ]
        out["cells_compared"] = sum(len(r) for r in _T2.values())
        out["cell_mismatches_vs_first_transcription"] = mismatch
        out["two_transcriptions_agree_cell_by_cell"] = not mismatch
    return out


def c6_composition_by_exponent_arithmetic() -> dict:
    """Re-derive Theorem 4.3's two bounds WITHOUT sympy, from exponents alone.

    The claim module composes the paper's chain in sympy. That is one implementation, and
    four pages of this logbook claimed the composition was "re-derived by a second route"
    when no such route existed -- a blind reviewer found the phrase describing work that
    was never written. This is that route, written.

    It uses no symbolic algebra at all. Each factor is a monomial in
    (sigma, delta, p_log, n), so a bound is just an exponent vector, composition is vector
    addition, and "what is missing" is a vector difference in exact `Fraction`s. The
    equations are typed here from the paper independently of claim_c6_thm43.py.

        (8)   ||M^ - M||_op  ~  sigma^3 (p_log/n)^(1/2)
        (10)  mean error     ~  ||E||_op / delta
        (11)  weight error   ~  ||E||_op
        (I)   stated mean    ~  sigma^3 delta^-1 (p_log/n)^(1/2)
        (II)  stated weight  ~  (p_log/n)^(1/2)
    """
    F = Fraction
    # exponents of (sigma, delta, p_log, n)
    eq8 = (F(3), F(0), F(1, 2), F(-1, 2))
    eq10_over_eq8 = (F(0), F(-1), F(0), F(0))     # divide by delta
    eq11_over_eq8 = (F(0), F(0), F(0), F(0))      # identity
    stated_I = (F(3), F(-1), F(1, 2), F(-1, 2))
    stated_II = (F(0), F(0), F(1, 2), F(-1, 2))

    def add(a, b):
        return tuple(x + y for x, y in zip(a, b))

    def sub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    derived_I = add(eq8, eq10_over_eq8)
    derived_II = add(eq8, eq11_over_eq8)
    resid_I = sub(derived_I, stated_I)
    resid_II = sub(derived_II, stated_II)
    names = ("sigma", "delta", "p_log", "n")

    def show(v):
        return {k: str(x) for k, x in zip(names, v)}

    return {
        "route": "exponent-vector arithmetic in exact Fractions; no symbolic algebra",
        "derived_mean_bound_exponents": show(derived_I),
        "stated_mean_bound_exponents": show(stated_I),
        "mean_bound_residual_exponents": show(resid_I),
        "mean_bound_reproduced_exactly": all(x == 0 for x in resid_I),
        "derived_weight_bound_exponents": show(derived_II),
        "stated_weight_bound_exponents": show(stated_II),
        "weight_bound_residual_exponents": show(resid_II),
        "weight_bound_reproduced_exactly": all(x == 0 for x in resid_II),
        "missing_factor_is_sigma_cubed": (
            resid_II[0] == 3 and all(x == 0 for x in resid_II[1:])
        ),
        "why": (
            "composing the paper's own cited results reproduces bound (I) with a zero "
            "residual and bound (II) with a residual of exactly sigma^3; because the "
            "residual is a positive power of sigma it is unbounded, so no universal "
            "constant C_2 can absorb it"
        ),
    }


def appendix_consistency_exact() -> dict:
    """Re-decide the Table 1 vs Table 7 comparison from a second transcription.

    The finding is that two of the paper's tables report the same quantity with
    incompatible values, so it is exactly the kind of finding a single transcription
    could manufacture: one mistyped digit and the tables "disagree". This route types
    both rows again, independently of paper_source.py, and does the arithmetic in exact
    rationals. Only the z-scores need floating point, and they need it only for a square
    root; the gaps themselves are exact.
    """
    datasets = ["ASSET", "FeedbackQA", "Review-5K", "Summarize", "UltraFeedback", "Yelp"]
    care = [Fraction(x) for x in _T1_CARE]
    first = [Fraction(x) for x in _T7_FIRST]
    s1 = [Fraction(x) for x in _T1_CARE_STD]
    s7 = [Fraction(x) for x in _T7_FIRST_STD]
    avg = [Fraction(x) for x in _T1_AVG]
    mv = [Fraction(x) for x in _T1_MV]

    rows = []
    for i, ds in enumerate(datasets):
        gap = care[i] - first[i]
        pooled = math.hypot(float(s1[i]), float(s7[i]))
        z = abs(float(gap)) / pooled if pooled > 0 else (float("inf") if gap else 0.0)
        rows.append({
            "dataset": ds,
            "gap_exact": str(gap),
            "gap_is_zero": gap == 0,
            "z": round(z, 3),
            "consistent": bool(z <= 2.0),
        })

    def pooled_pct(base, care_row):
        return float((sum(base) - sum(care_row)) / sum(base) * 100)

    i_uf = datasets.index("UltraFeedback")
    return {
        "rows": rows,
        "n_consistent": sum(r["consistent"] for r in rows),
        "inconsistent_datasets": [r["dataset"] for r in rows if not r["consistent"]],
        "claim1_pct_using_table1": float((mv[i_uf] - care[i_uf]) / mv[i_uf] * 100),
        "claim1_pct_using_table7": float((mv[i_uf] - first[i_uf]) / mv[i_uf] * 100),
        "claim2_pooled_vs_AVG_using_table1": pooled_pct(avg, care),
        "claim2_pooled_vs_AVG_using_table7": pooled_pct(avg, first),
        "claim2_pooled_vs_MV_using_table1": pooled_pct(mv, care),
        "claim2_pooled_vs_MV_using_table7": pooled_pct(mv, first),
    }


def table_percentages_exact() -> dict:
    def frac(xs):
        return [Fraction(x) for x in xs]

    avg, mv, care = frac(_T1_AVG), frac(_T1_MV), frac(_T1_CARE)
    n = len(avg)
    pooled_avg = (sum(avg) / n - sum(care) / n) / (sum(avg) / n) * 100
    pooled_mv = (sum(mv) / n - sum(care) / n) / (sum(mv) / n) * 100
    mean_rel_avg = sum((a - c) / a for a, c in zip(avg, care)) / n * 100
    mean_rel_mv = sum((m - c) / m for m, c in zip(mv, care)) / n * 100
    uf = (mv[4] - care[4]) / mv[4] * 100
    return {
        "pooled_vs_AVG_pct": float(pooled_avg),
        "pooled_vs_MV_pct": float(pooled_mv),
        "mean_relative_vs_AVG_pct": float(mean_rel_avg),
        "mean_relative_vs_MV_pct": float(mean_rel_mv),
        "ultrafeedback_vs_MV_pct": float(uf),
        "pooled_matches_17_37": abs(float(pooled_avg) - 17.37) < 0.005,
        "pooled_matches_12_75": abs(float(pooled_mv) - 12.75) < 0.005,
        "ultrafeedback_matches_26_8": abs(float(uf) - 26.8) < 0.05,
        # The paper's 13.4% is measured against the STRONGEST Table 2 baseline on
        # Summarize, which is GLAD at 0.718 -- not the 0.705 (WS / Dawid-Skene) that
        # the circulated claim string quotes. Both readings are reported; only the
        # first is asserted, because only the first is what the paper states.
        "summarize_pct_vs_strongest_baseline_0p718": float(
            (Fraction("0.814") - Fraction("0.718")) / Fraction("0.718") * 100
        ),
        "summarize_pct_vs_claimstring_0p705": float(
            (Fraction("0.814") - Fraction("0.705")) / Fraction("0.705") * 100
        ),
        "summarize_13_4_from_0p814_over_0p718": abs(
            float((Fraction("0.814") - Fraction("0.718")) / Fraction("0.718") * 100) - 13.4
        )
        < 0.1,
        "claimstring_0p705_does_not_reproduce_13_4": abs(
            float((Fraction("0.814") - Fraction("0.705")) / Fraction("0.705") * 100) - 13.4
        )
        >= 0.1,
    }


def c2_unit_invariance_exact() -> dict:
    """Re-decide Claim 2's falsification in exact rationals, independently of numpy.

    The claim module reaches its verdict in floating point. Because the verdict turns
    on one statistic being *exactly* invariant and another not, a float implementation
    is exactly the wrong tool to confirm it with: `unweighted_spread == 0.0` could be
    rounding. Fractions make the invariance exact rather than approximate.
    """

    def frac(xs):
        return [Fraction(x) for x in xs]

    avg, mv, care = frac(_T1_AVG), frac(_T1_MV), frac(_T1_CARE)
    n = len(avg)

    def scaled(xs, c, i=0):
        out = list(xs)
        out[i] = out[i] * c
        return out

    def pooled(base, care_, c, i=0):
        b, k = scaled(base, c, i), scaled(care_, c, i)
        return (sum(b) / n - sum(k) / n) / (sum(b) / n) * 100

    def unweighted(base, care_, c, i=0):
        b, k = scaled(base, c, i), scaled(care_, c, i)
        return sum((x - y) / x for x, y in zip(b, k)) / n * 100

    factors = [Fraction(1, 100), Fraction(1, 10), Fraction(1, 4), Fraction(1), Fraction(10)]
    pooled_avg = [pooled(avg, care, c) for c in factors]
    pooled_mv = [pooled(mv, care, c) for c in factors]
    unw_avg = [unweighted(avg, care, c) for c in factors]
    unw_mv = [unweighted(mv, care, c) for c in factors]

    # Exact equality, not a tolerance: every rescaling must give the identical rational.
    unweighted_exactly_invariant = len(set(unw_avg)) == 1 and len(set(unw_mv)) == 1
    pooled_spread = float(max(pooled_avg) - min(pooled_avg))
    orderings = {a > m for a, m in zip(pooled_avg, pooled_mv)}

    # The weighted-mean identity, in exact arithmetic.
    w = [a / sum(avg) for a in avg]
    r = [(a - c) / a for a, c in zip(avg, care)]
    identity_exact = sum(wi * ri for wi, ri in zip(w, r)) * 100 == pooled(avg, care, Fraction(1))

    return {
        "unweighted_across_benchmark_avg_vs_AVG_pct": float(unw_avg[0]),
        "unweighted_across_benchmark_avg_vs_MV_pct": float(unw_mv[0]),
        "unweighted_exactly_invariant_under_unit_change": bool(unweighted_exactly_invariant),
        "pooled_spread_across_unit_changes_pct": pooled_spread,
        "pooled_ordering_flips": bool(len(orderings) > 1),
        "weighted_mean_identity_exact": bool(identity_exact),
        "asset_weight_share": float(w[0]),
        "paper_headline_pct": 17.37,
        "discrepancy_pp": abs(float(unw_avg[0]) - 17.37),
        "scope_qualification_established": bool(
            unweighted_exactly_invariant
            and identity_exact
            and pooled_spread > 1.0
            and len(orderings) > 1
            and abs(float(unw_avg[0]) - 17.37) > 1.0
        ),
    }


# --- 2. Proposition 4.1 counterexample in 60-digit arithmetic ---------------
def prop41_counterexample_mpmath(dps: int = 60) -> dict:
    mp.mp.dps = dps
    r2 = mp.sqrt(2)
    K = mp.matrix([[r2, 0], [0, 1]])
    Kp = mp.matrix([[r2 / r2, 1 / r2], [r2 / r2, -1 / r2]])  # [sqrt(2)*f1, f2]
    KHHinv = mp.matrix([[mp.mpf(1) / 2, 0], [0, 1]])

    def low_rank(M):
        return M * KHHinv * M.T

    L, Lp = low_rank(K), low_rank(Kp)
    diff = max(abs(L[i, j] - Lp[i, j]) for i in range(2) for j in range(2))

    def cols(M):
        return [mp.matrix([M[0, j], M[1, j]]) for j in range(2)]

    a, b = cols(K), cols(Kp)
    is_signed_perm = False
    for perm in itertools.permutations(range(2)):
        for signs in itertools.product([1, -1], repeat=2):
            if all(
                max(abs(a[j][i] - signs[j] * b[perm[j]][i]) for i in range(2)) < mp.mpf(10) ** (-dps + 10)
                for j in range(2)
            ):
                is_signed_perm = True
    orth = abs(K[0, 0] * K[0, 1] + K[1, 0] * K[1, 1]) < mp.mpf(10) ** (-dps + 10)
    orth_p = abs(Kp[0, 0] * Kp[0, 1] + Kp[1, 0] * Kp[1, 1]) < mp.mpf(10) ** (-dps + 10)
    return {
        "dps": dps,
        "max_abs_L_minus_Lprime": float(diff),
        "same_L_to_full_precision": bool(diff < mp.mpf(10) ** (-dps + 10)),
        "both_have_orthogonal_columns": bool(orth and orth_p),
        "columns_are_signed_permutation": bool(is_signed_perm),
        "counterexample_holds": bool(diff < mp.mpf(10) ** (-dps + 10) and orth and orth_p and not is_signed_perm),
    }


# --- 3. first-order perturbation by finite differences ----------------------
def first_order_by_finite_difference(seed: int = 99, n_cases: int = 30) -> dict:
    """Cross-check claim_c4's analytic first-order formula against d/dt of the truth."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from claim_c4_prop41 import _first_order_error

    rng = np.random.default_rng(seed)
    worst_rel = 0.0
    for _ in range(n_cases):
        p, h = int(rng.integers(5, 12)), 3
        lam = np.sort(rng.uniform(0.6, 4.0, size=h))[::-1].copy()
        if np.min(np.abs(np.diff(lam))) < 0.05:
            continue
        Q, _ = np.linalg.qr(rng.standard_normal((p, p)))
        K = Q[:, :h]
        E = rng.standard_normal((p, h))
        E /= np.linalg.norm(E, 2)
        Lam = np.diag(lam)
        L = K @ Lam @ K.T
        w0, V0 = np.linalg.eigh(L)
        o0 = np.argsort(w0)[::-1]
        for i in range(h):
            t = 1e-7
            Lt = (K + t * E) @ Lam @ (K + t * E).T
            wt, Vt = np.linalg.eigh(Lt)
            ot = np.argsort(wt)[::-1]
            u, ut = V0[:, o0[i]], Vt[:, ot[i]]
            if float(u @ ut) < 0:
                ut = -ut
            numeric = float(np.linalg.norm(ut - u)) / t
            analytic = _first_order_error(K, lam, E, i)
            if analytic > 1e-9:
                worst_rel = max(worst_rel, abs(numeric - analytic) / analytic)
    return {
        "worst_relative_disagreement": worst_rel,
        "analytic_formula_confirmed": bool(worst_rel < 5e-3),
    }


# --- 4. robust slope for the Theorem 4.3 sweep ------------------------------
def theil_sen(x, y) -> float:
    x, y = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    slopes = [
        (y[j] - y[i]) / (x[j] - x[i])
        for i in range(len(x))
        for j in range(i + 1, len(x))
        if x[j] != x[i]
    ]
    return float(np.median(slopes))


def recheck_c6_slope(verdict: dict) -> dict:
    rows = (
        verdict.get("claims", {})
        .get("C6_thm43", {})
        .get("route_c_boundary_sigma_probe", {})
        .get("rows", [])
    )
    if len(rows) < 3:
        return {"available": False}
    slope = theil_sen(
        [r["sigma_max"] for r in rows], [r["error_over_stated_unit"] for r in rows]
    )
    return {
        "available": True,
        "theil_sen_slope": slope,
        "least_squares_slope": verdict["claims"]["C6_thm43"]["route_c_boundary_sigma_probe"][
            "loglog_slope_error_over_stated_bound_vs_sigma"
        ],
        # The sigma^3 hypothesis predicts a slope near 3, so a one-sided "slope < 0.5"
        # test looked like agreement -- Theil-Sen clears it by 0.02. But the two
        # estimators are 8x apart on the same five points, which is the real signal:
        # this probe's slope is a property of the estimator, not of the system. That is
        # reported rather than gated, because an uninformative measurement is absent
        # evidence, not failed evidence -- and the conclusion the probe used to carry has
        # been withdrawn for exactly this reason (see also the t-interval correction in
        # informativeness.t_crit).
        "theil_sen_agrees_no_sigma_growth": bool(slope < 0.5),
        "abs_difference_between_estimators": abs(
            float(slope) - float(verdict["claims"]["C6_thm43"]
                                 ["route_c_boundary_sigma_probe"]
                                 ["loglog_slope_error_over_stated_bound_vs_sigma"])
        ),
        "estimators_agree_on_the_slope": bool(
            abs(float(slope) - float(verdict["claims"]["C6_thm43"]
                                     ["route_c_boundary_sigma_probe"]
                                     ["loglog_slope_error_over_stated_bound_vs_sigma"])) <= 0.15
        ),
        "why": (
            "the two estimators disagree by far more than either one's own claimed "
            "precision, so the boundary probe resolves no slope and must not be read as "
            "evidence for or against the missing sigma^3 factor"
        ),
    }


def recheck_c6_p_exponent(verdict: dict) -> dict:
    """Refit the p exponent -- the sweep the falsification rests on -- independently.

    The claim module fits least squares to its own fitted-n* estimates. This refits with
    Theil-Sen, which a single outlying setting cannot carry, and does so for BOTH n*
    estimators. The falsification only stands if the exponent still exceeds the stated 1
    under an estimator the claim module never used.
    """
    sw = (verdict.get("claims", {}).get("C6_thm43", {})
          .get("route_b_calibrated_sample_complexity", {}).get("p", {}))
    rows = sw.get("rows", [])
    eps = 0.1
    # Two bugs lived here and both mattered.
    #
    # 1. `theil_sen` logs its own inputs. This call site passed values that were ALREADY
    #    logged, so the published figure was the median slope of log(log n) against
    #    log(log(p log(p/eps))) -- not an exponent at all, and systematically too small.
    # 2. The claim module fits over the settings its per-setting screen accepts; this
    #    refit read every row. A 3-point least-squares fit was being compared against a
    #    6-point Theil-Sen fit and the difference was labelled "estimator".
    #
    # Both are fixed: raw inputs, and the same screened settings.
    # `per_setting_screen.usable` is a list of RECORDS, not of p values. Reading it as a
    # set of keys silently matched nothing, both refits returned None, `available` stayed
    # False and the gate below never ran -- a check that quietly measures nothing, which
    # is the same failure this file exists to catch.
    screen = sw.get("per_setting_screen") or {}
    usable = {u["p_total"] for u in (screen.get("usable") or []) if "p_total" in u} or None
    out = {"available": False, "fitted_over_settings": sorted(usable) if usable else None}
    for tag, key in (("fitted", "n_star"), ("crossing", "n_star_crossing")):
        pts = [(r["p_total"], r.get(key)) for r in rows
               if r.get(key) and (usable is None or r["p_total"] in usable)]
        if len(pts) < 3:
            out[f"{tag}_theil_sen_slope"] = None
            continue
        x = [p * math.log(p / eps) for p, _ in pts]
        y = [n for _, n in pts]
        out[f"{tag}_theil_sen_slope"] = theil_sen(x, y)
        out[f"{tag}_n_points"] = len(pts)
    slopes = [out.get("fitted_theil_sen_slope"), out.get("crossing_theil_sen_slope")]
    slopes = [v for v in slopes if v is not None]
    # If the sweep produced rows at all, a refit that yields nothing is a broken check,
    # not an absent one, and must fail rather than disappear.
    out["refit_expected"] = bool(rows)
    out["refit_produced_nothing"] = bool(rows) and not slopes
    if slopes:
        out["available"] = True
        out["least_squares_slope_from_claim_module"] = sw.get("exponent_vs_p_log_p")
        out["stated_exponent"] = 1.0
        out["min_theil_sen_slope"] = min(slopes)
        out["max_theil_sen_slope"] = max(slopes)
        ls = sw.get("exponent_vs_p_log_p")
        # What this refit is for is estimator-robustness: does a median-of-slopes
        # estimator land where least squares did? It must NOT be a test of whether the
        # exponent exceeds the theorem's 1 -- gating on that would fail the whole run
        # whenever the paper looked correct, which is an inverted contract, not a check.
        out["theil_sen_agrees_with_least_squares"] = bool(
            ls and abs(min(slopes) - ls) <= 1.0 and abs(max(slopes) - ls) <= 1.0
        )
        out["both_estimators_exceed_stated_exponent"] = bool(min(slopes) > 1.0)
    return out


def davis_kahan_by_principal_angle(seed: int = 131, n_trials: int = 500) -> dict:
    """Re-validate the 2^{3/2} constant along a different route than the claim module.

    claim_c5_thm42 measures ||u_hat - u|| directly. Here we compute the principal
    angle between the two one-dimensional subspaces and use the identity
    ||u_hat - u|| = 2 sin(theta/2) after sign alignment, so an error in either
    route's eigenvector bookkeeping cannot cancel out between them.
    """
    rng = np.random.default_rng(seed)
    worst, agree = 0.0, True
    for _ in range(n_trials):
        p_dim = int(rng.integers(4, 12))
        A = rng.standard_normal((p_dim, p_dim))
        M = (A + A.T) / 2.0
        E = rng.standard_normal((p_dim, p_dim))
        E = (E + E.T) / 2.0
        E *= 10.0 ** rng.uniform(-4, -1) / max(np.linalg.norm(E, 2), 1e-300)

        w, V = np.linalg.eigh(M)
        wt, Vt = np.linalg.eigh(M + E)
        i = int(np.argmax(w))
        u, ut = V[:, i], Vt[:, int(np.argmax(wt))]
        if float(ut @ u) < 0:
            ut = -ut

        gaps = [abs(w[i] - w[j]) for j in range(p_dim) if j != i]
        delta = min(gaps)
        if delta < 1e-8:
            continue

        direct = float(np.linalg.norm(ut - u))
        cos = float(np.clip(abs(ut @ u), -1.0, 1.0))
        by_angle = 2.0 * math.sin(math.acos(cos) / 2.0)
        if abs(direct - by_angle) > 1e-6 * max(1.0, direct):
            agree = False

        bound = 2.0 ** 1.5 * float(np.linalg.norm(E, 2)) / delta
        worst = max(worst, direct / bound)

    return {
        "trials": n_trials,
        "two_routes_agree_on_eigvec_distance": bool(agree),
        "worst_err_over_bound": worst,
        "constant_2_to_the_3_over_2_holds": bool(worst <= 1.0),
    }


def recheck_c5_stage_slopes(verdict: dict) -> dict:
    """Refit the two theorem-governed C5 curves with Theil-Sen instead of least squares."""
    cal = verdict.get("claims", {}).get("C5_thm42", {}).get("route_c_calibrated_rate", {})
    ns = cal.get("grid_n", [])
    s1 = cal.get("stage_1_precision_error_vs_n", [])
    s2 = cal.get("stage_2_oracle_spectral_error_vs_n", [])
    if len(ns) < 4 or len(s1) != len(ns) or len(s2) != len(ns):
        return {"available": False}
    ts1, ts2 = theil_sen(ns, s1), theil_sen(ns, s2)
    return {
        "available": True,
        "stage_1_theil_sen_slope": ts1,
        "stage_1_least_squares_slope": cal.get("stage_1_loglog_slope"),
        "stage_2_theil_sen_slope": ts2,
        "stage_2_least_squares_slope": cal.get("stage_2_loglog_slope"),
        # One-sided, matching the claim module: the theorem is an O(.) upper bound.
        "stage_1_agrees_at_least_root_n": bool(ts1 <= -0.42),
        "stage_2_agrees_at_least_root_n": bool(ts2 <= -0.42),
        # A one-sided contract is not an agreement test -- both estimators could clear it
        # while disagreeing badly. This is the two-sided question, and it is what gates.
        "agrees_with_claim_module": bool(
            cal.get("stage_1_loglog_slope") is not None
            and cal.get("stage_2_loglog_slope") is not None
            and abs(ts1 - cal["stage_1_loglog_slope"]) <= 0.15
            and abs(ts2 - cal["stage_2_loglog_slope"]) <= 0.15
        ),
        "agreement_tolerance": 0.15,
    }


def run(verdict: dict | None = None) -> dict:
    out = {
        "table_percentages_exact_rational": table_percentages_exact(),
        "c2_unit_invariance_exact": c2_unit_invariance_exact(),
        "appendix_consistency_exact": appendix_consistency_exact(),
        "c6_composition_by_exponent_arithmetic": c6_composition_by_exponent_arithmetic(),
        "table2_second_transcription": table2_second_transcription(verdict),
        "prop41_counterexample_mpmath": prop41_counterexample_mpmath(),
        "first_order_formula_vs_finite_difference": first_order_by_finite_difference(),
        "davis_kahan_by_principal_angle": davis_kahan_by_principal_angle(),
    }
    if verdict is not None:
        out["c5_stage_slope_recheck"] = recheck_c5_stage_slopes(verdict)
        out["c6_slope_recheck"] = recheck_c6_slope(verdict)
        out["c6_p_exponent_recheck"] = recheck_c6_p_exponent(verdict)

        # Cross-check that the claim module and this checker agree on the tables.
        arith = verdict["claims"]["C1_C2_C3_tables"]["table_arithmetic"]
        pooled = arith["candidate_definitions"]["pooled_mean_MAE_ratio"]
        out["agreement_with_claim_module"] = {
            "pooled_vs_AVG": abs(pooled["vs_AVG"] - out["table_percentages_exact_rational"]["pooled_vs_AVG_pct"]) < 1e-6,
            "pooled_vs_MV": abs(pooled["vs_MV"] - out["table_percentages_exact_rational"]["pooled_vs_MV_pct"]) < 1e-6,
        }
        # The C2 verdict is only as good as the two implementations agreeing on it.
        conv = verdict["claims"]["C1_C2_C3_tables"].get("aggregation_convention_audit")
        if conv is not None:
            e = out["c2_unit_invariance_exact"]
            out["agreement_with_claim_module"]["c2_scope_qualification"] = bool(
                conv["scope_qualification_established"] == e["scope_qualification_established"]
            )
            out["agreement_with_claim_module"]["c2_unweighted_average"] = bool(
                abs(conv["unweighted_across_benchmark_average_vs_AVG_pct"]
                    - e["unweighted_across_benchmark_avg_vs_AVG_pct"]) < 1e-6
            )
        # The Table 1 vs Table 7 finding rests on a transcription, so the two
        # transcriptions must agree on WHICH datasets disagree, not merely on a summary.
        app = verdict["claims"]["C1_C2_C3_tables"].get("appendix_consistency_audit")
        if app is not None:
            a = out["appendix_consistency_exact"]
            out["agreement_with_claim_module"]["appendix_inconsistent_set"] = bool(
                sorted(app["inconsistent_datasets"]) == sorted(a["inconsistent_datasets"])
            )
            out["agreement_with_claim_module"]["appendix_headline_shift"] = bool(
                abs(app["headline_using_table7"]["claim2_pooled_vs_AVG_pct"]
                    - a["claim2_pooled_vs_AVG_using_table7"]) < 1e-3
            )

    t = out["table_percentages_exact_rational"]
    out["ok"] = bool(
        t["pooled_matches_17_37"]
        and t["pooled_matches_12_75"]
        and t["ultrafeedback_matches_26_8"]
        and t["summarize_13_4_from_0p814_over_0p718"]
        and t["claimstring_0p705_does_not_reproduce_13_4"]
        and out["prop41_counterexample_mpmath"]["counterexample_holds"]
        and out["first_order_formula_vs_finite_difference"]["analytic_formula_confirmed"]
        and out["davis_kahan_by_principal_angle"]["two_routes_agree_on_eigvec_distance"]
        and out["davis_kahan_by_principal_angle"]["constant_2_to_the_3_over_2_holds"]
        and out["c2_unit_invariance_exact"]["weighted_mean_identity_exact"]
        and out["c2_unit_invariance_exact"]["unweighted_exactly_invariant_under_unit_change"]
        # Claim 3's structural verdict is an argmax over a 54-cell grid. Two independent
        # transcriptions must agree cell by cell, and the recomputed winners must match
        # the cells the paper typesets bold.
        and out["table2_second_transcription"]["two_transcriptions_agree_cell_by_cell"]
        and out["table2_second_transcription"]["matches_paper_bold_cells"]
        and out["table2_second_transcription"]["summarize_matches_13_4"]
        # The second, non-symbolic derivation of Theorem 4.3's chain must reach the same
        # two conclusions as the sympy route. This is what makes the claim module's
        # symbolic audit falsifiable: on its own it divides three transcribed expressions
        # and can only confirm the transcription.
        and out["c6_composition_by_exponent_arithmetic"]["mean_bound_reproduced_exactly"]
        and out["c6_composition_by_exponent_arithmetic"]["missing_factor_is_sigma_cubed"]
    )
    # A cross-implementation agreement check that does not gate `ok` is decoration: the
    # two implementations could disagree about a published verdict and the run would
    # still exit 0. Any recorded disagreement fails the checker.
    agree = out.get("agreement_with_claim_module")
    if agree:
        out["ok"] = bool(out["ok"] and all(agree.values()))

    # The refit gates on the two estimators AGREEING, not on the exponent exceeding the
    # theorem's stated 1. An earlier revision gated on the latter, which meant the whole
    # verifier exited nonzero in exactly the case where the paper turned out to be right.
    pr = out.get("c6_p_exponent_recheck") or {}
    if pr.get("refit_produced_nothing"):
        out["ok"] = False
    elif pr.get("available"):
        out["ok"] = bool(out["ok"] and pr["theil_sen_agrees_with_least_squares"])

    # Two further cross-estimator rechecks were computed and then not wired to anything,
    # which is the "an agreement check that cannot fail is decoration" defect recurring
    # in the two places it was not fixed. Both now gate the run.
    sr = out.get("c5_stage_slope_recheck") or {}
    if sr.get("available"):
        out["ok"] = bool(out["ok"] and sr["agrees_with_claim_module"])
    # Deliberately NOT gated: the sigma boundary probe is reported as uninformative, and
    # failing the verifier on an uninformative measurement would confuse "we could not
    # measure this" with "the evidence failed". What IS required is that the recheck ran
    # and recorded both estimators, so the disagreement cannot vanish silently.
    cr = out.get("c6_slope_recheck") or {}
    if cr.get("available"):
        out["ok"] = bool(out["ok"] and "estimators_agree_on_the_slope" in cr)
    return out


if __name__ == "__main__":
    import json
    import sys

    v = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    res = run(v)
    print(json.dumps(res, indent=2, default=str))
    raise SystemExit(0 if res["ok"] else 1)
