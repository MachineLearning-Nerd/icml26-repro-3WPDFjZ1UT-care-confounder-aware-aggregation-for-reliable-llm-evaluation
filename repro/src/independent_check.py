"""Independent checker.

Deliberately re-derives the load-bearing numbers by *different* routes from the
claim modules, so that a bug in one implementation cannot pass unnoticed:

  * Table 1/2 percentages: exact rational arithmetic on a second, hand-typed copy
    of the table, not the one in paper_source.py.
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
        "falsified_as_worded": bool(
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
        # The sigma^3 hypothesis predicted a slope near 3 and would need at least 0.5
        # to be visible at all. Both estimators must agree that no such growth is there,
        # otherwise the claim module's null result rests on the choice of estimator.
        "theil_sen_agrees_no_sigma_growth": bool(slope < 0.5),
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
    out = {"available": False}
    for tag, key in (("fitted", "n_star"), ("crossing", "n_star_crossing")):
        pts = [(r["p_total"], r.get(key)) for r in rows if r.get(key)]
        if len(pts) < 3:
            out[f"{tag}_theil_sen_slope"] = None
            continue
        x = [math.log(p * math.log(p / eps)) for p, _ in pts]
        y = [math.log(n) for _, n in pts]
        out[f"{tag}_theil_sen_slope"] = theil_sen(x, y)
        out[f"{tag}_n_points"] = len(pts)
    slopes = [out.get("fitted_theil_sen_slope"), out.get("crossing_theil_sen_slope")]
    slopes = [v for v in slopes if v is not None]
    if slopes:
        out["available"] = True
        out["least_squares_slope_from_claim_module"] = sw.get("exponent_vs_p_log_p")
        out["stated_exponent"] = 1.0
        # The whole falsification is "the exponent exceeds 1". If a Theil-Sen refit does
        # not agree, the finding is an artefact of least squares and must not stand.
        out["both_estimators_exceed_stated_exponent"] = bool(min(slopes) > 1.0)
        out["min_theil_sen_slope"] = min(slopes)
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
    }


def run(verdict: dict | None = None) -> dict:
    out = {
        "table_percentages_exact_rational": table_percentages_exact(),
        "c2_unit_invariance_exact": c2_unit_invariance_exact(),
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
            out["agreement_with_claim_module"]["c2_falsified_as_worded"] = bool(
                conv["falsified_as_worded"] == e["falsified_as_worded"]
            )
            out["agreement_with_claim_module"]["c2_unweighted_average"] = bool(
                abs(conv["unweighted_across_benchmark_average_vs_AVG_pct"]
                    - e["unweighted_across_benchmark_avg_vs_AVG_pct"]) < 1e-6
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
    )
    # A cross-implementation agreement check that does not gate `ok` is decoration: the
    # two implementations could disagree about a published verdict and the run would
    # still exit 0. Any recorded disagreement fails the checker.
    agree = out.get("agreement_with_claim_module")
    if agree:
        out["ok"] = bool(out["ok"] and all(agree.values()))

    # If the p exponent was refit at all, the falsification it supports must survive the
    # refit; otherwise the finding is a property of least squares and this checker fails.
    pr = out.get("c6_p_exponent_recheck") or {}
    if pr.get("available"):
        out["ok"] = bool(out["ok"] and pr["both_estimators_exceed_stated_exponent"])
    return out


if __name__ == "__main__":
    import json
    import sys

    v = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    res = run(v)
    print(json.dumps(res, indent=2, default=str))
    raise SystemExit(0 if res["ok"] else 1)
