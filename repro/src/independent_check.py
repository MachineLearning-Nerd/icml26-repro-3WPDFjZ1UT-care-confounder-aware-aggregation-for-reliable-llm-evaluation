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
        "summarize_13_4_from_0p814_over_0p705": abs(
            float((Fraction("0.814") - Fraction("0.705")) / Fraction("0.705") * 100) - 13.4
        )
        < 0.1,
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
        .get("route_b_sigma_sweep_on_sample_complexity_boundary", {})
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
        "least_squares_slope": verdict["claims"]["C6_thm43"][
            "route_b_sigma_sweep_on_sample_complexity_boundary"
        ]["loglog_slope_error_over_stated_bound_vs_sigma"],
        "agrees_that_slope_is_positive": bool(slope > 0.5),
    }


def run(verdict: dict | None = None) -> dict:
    out = {
        "table_percentages_exact_rational": table_percentages_exact(),
        "prop41_counterexample_mpmath": prop41_counterexample_mpmath(),
        "first_order_formula_vs_finite_difference": first_order_by_finite_difference(),
    }
    if verdict is not None:
        out["c6_slope_recheck"] = recheck_c6_slope(verdict)

        # Cross-check that the claim module and this checker agree on the tables.
        arith = verdict["claims"]["C1_C2_C3_tables"]["table_arithmetic"]
        pooled = arith["candidate_definitions"]["pooled_mean_MAE_ratio"]
        out["agreement_with_claim_module"] = {
            "pooled_vs_AVG": abs(pooled["vs_AVG"] - out["table_percentages_exact_rational"]["pooled_vs_AVG_pct"]) < 1e-6,
            "pooled_vs_MV": abs(pooled["vs_MV"] - out["table_percentages_exact_rational"]["pooled_vs_MV_pct"]) < 1e-6,
        }

    t = out["table_percentages_exact_rational"]
    out["ok"] = bool(
        t["pooled_matches_17_37"]
        and t["pooled_matches_12_75"]
        and t["ultrafeedback_matches_26_8"]
        and t["summarize_13_4_from_0p814_over_0p705"]
        and out["prop41_counterexample_mpmath"]["counterexample_holds"]
        and out["first_order_formula_vs_finite_difference"]["analytic_formula_confirmed"]
    )
    return out


if __name__ == "__main__":
    import json
    import sys

    v = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    res = run(v)
    print(json.dumps(res, indent=2, default=str))
    raise SystemExit(0 if res["ok"] else 1)
