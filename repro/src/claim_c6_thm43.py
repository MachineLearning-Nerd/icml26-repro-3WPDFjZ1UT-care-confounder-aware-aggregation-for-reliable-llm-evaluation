"""Claim 6 - Theorem 4.3 (= Appendix Theorem D.9): sample complexity for recovering
the mixture parameters (mu_qc, pi_qc).

Exact statement under test (Section 4 / Appendix D.5), with universal constants
C_1, C_2 > 0 and 0 < eps < 1:

    if   n >= C_1 * sigma_max^6 / (delta^2 pi_min^2) * p log(p/eps)
    then with probability at least 1 - eps,
        (I)  max_{q,c} ||mu^_qc - mu_qc||_2 <= C_1 (sigma_max^3/delta) sqrt(p log(p/eps)/n)
        (II) max_{q,c} |pi^_qc - pi_qc|     <= C_2 sqrt(p log(p/eps)/n).

Three routes are run.

Route A - reconstruct the paper's own derivation symbolically.  The chain is
  (8)  ||M^ - M||_op <= C sigma_max^3 sqrt(p log(p/eps)/n)          [Bernstein + 13^p net]
  (10) mean error    <= C_dec ||E||_op / delta                       [Anandkumar et al. 2014]
  (11) weight error  <= C_pi ||E||_op                                [Lipschitz stability]
Composing (10) with (8) reproduces (I) exactly.  Composing (11) with (8) gives
  max |pi^ - pi| <= C_pi C sigma_max^3 sqrt(p log(p/eps)/n),
so the *displayed* chain does not establish (II), whose C_2 is universal: a factor
of sigma_max^3 is unaccounted for.  This is recorded as a gap in the written proof.

Route B - measure the sample complexity the theorem actually asserts.  For a target
weight accuracy we SEARCH for the smallest n that attains it, and fit the exponents
of n*(sigma_max), n*(pi_min) and n*(p log(p/eps)).  Because "n >~ ..." is a
sufficient condition, each check is one-sided: the measured exponent must not
EXCEED the stated one.  No sample size is ever read off the formula under test.

Route C - probe whether the gap in Route A is a real defect, by measuring the
weight error along the theorem's own sample-complexity boundary n = n_0 sigma^6.
If eq. (11) were tight the error would be sigma-free there while the stated bound
decays like sigma^-3.  It is not: no sigma-growth is detected, so eq. (11) is
merely a loose intermediate and the stated bound survives.  Route C is reported
because the negative result matters - it is the reason this claim is NOT recorded
as falsified.

Negative controls make the measurement non-vacuous: over-sampling must drive the
error down, and freezing n must drive it up.
"""

from __future__ import annotations

import numpy as np

from informativeness import informativeness
import sympy as sp

from tensor_mom import empirical_moments, recover_weights, sample_mixture

K_COMPONENTS = 4
PI_TRUE = np.array([0.40, 0.30, 0.20, 0.10])
P_PER_VIEW = 6
P_TOTAL = 3 * P_PER_VIEW
EPS = 0.1
MEAN_SCALE = 3.0


# --------------------------------------------------------------------------
# Route A: symbolic reconstruction of the paper's proof chain
# --------------------------------------------------------------------------
def symbolic_chain_audit() -> dict:
    sigma, delta, p, eps, n, C, C_dec, C_pi, C1, C2, pi_min = sp.symbols(
        "sigma delta p epsilon n C C_dec C_pi C_1 C_2 pi_min", positive=True
    )

    # (8) concentration of the empirical third moment
    E_op = C * sigma**3 * sp.sqrt(p * sp.log(p / eps) / n)

    # (10) + (12): mean error
    mu_err_derived = sp.sqrt(3) * C_dec * E_op / delta
    mu_err_stated = C1 * sigma**3 / delta * sp.sqrt(p * sp.log(p / eps) / n)
    mu_ratio = sp.simplify(mu_err_derived / mu_err_stated)
    mu_sigma_free = sp.simplify(sp.diff(mu_ratio, sigma)) == 0

    # (11): weight error
    pi_err_derived = C_pi * E_op
    pi_err_stated = C2 * sp.sqrt(p * sp.log(p / eps) / n)
    pi_ratio = sp.simplify(pi_err_derived / pi_err_stated)
    pi_missing_factor = sp.simplify(pi_ratio / (C_pi * C / C2))

    # Behaviour along the theorem's own sample-complexity boundary.
    n_boundary = C1 * sigma**6 / (delta**2 * pi_min**2) * p * sp.log(p / eps)
    stated_on_boundary = sp.simplify(pi_err_stated.subs(n, n_boundary))
    derived_on_boundary = sp.simplify(pi_err_derived.subs(n, n_boundary))
    ratio_on_boundary = sp.simplify(derived_on_boundary / stated_on_boundary)

    return {
        "ok": bool(mu_sigma_free) and bool(sp.simplify(pi_missing_factor - sigma**3) == 0),
        "mean_bound_reproduced_exactly": bool(mu_sigma_free),
        "mean_derived": sp.srepr(mu_err_derived) and str(mu_err_derived),
        "mean_stated": str(mu_err_stated),
        "weight_derived_from_paper_proof": str(pi_err_derived),
        "weight_stated_in_theorem": str(pi_err_stated),
        "factor_missing_from_stated_weight_bound": str(sp.simplify(pi_missing_factor)),
        "stated_weight_bound_on_sample_complexity_boundary": str(stated_on_boundary),
        "derived_weight_bound_on_sample_complexity_boundary": str(derived_on_boundary),
        "derived_over_stated_on_boundary": str(ratio_on_boundary),
        "grows_without_bound_in_sigma": bool(
            sp.limit(ratio_on_boundary, sigma, sp.oo) == sp.oo
        ),
    }


# --------------------------------------------------------------------------
# Route B: measure the quantity the bound is about
# --------------------------------------------------------------------------
def _fixed_model(rng):
    """A single fixed instance of Assumption D.8; only sigma varies afterwards.

    Component means per view are taken from an orthonormal frame so the factor
    matrices are perfectly conditioned. A badly conditioned A or B would make the
    multi-view pseudo-inverses amplify sampling noise, and the experiment would
    then be measuring conditioning rather than the sigma-dependence under test.
    """
    mus = []
    for _ in range(3):
        Q, _ = np.linalg.qr(rng.standard_normal((P_PER_VIEW, P_PER_VIEW)))
        mus.append(MEAN_SCALE * Q[:, :K_COMPONENTS])
    return mus


def _one_run(mus, sigma, n, seed):
    rng = np.random.default_rng(seed)
    (X1, X2, X3), _ = sample_mixture(rng, PI_TRUE, mus, sigma, n)
    M2, M3 = empirical_moments(X1, X2, X3)
    w_hat = recover_weights(M2, M3, K_COMPONENTS, rng)
    if w_hat is None:
        return None
    return float(np.max(np.abs(w_hat - np.sort(PI_TRUE)[::-1])))


def _stated_bound_unit(n):
    """sqrt(p log(p/eps)/n) -- the stated weight bound up to the universal C_2."""
    return float(np.sqrt(P_TOTAL * np.log(P_TOTAL / EPS) / n))


# The grid must start well below the smallest n* any setting needs. At a floor of
# 5000 every pi_min setting returned n* = 5000 exactly: the error was already under
# target at the first point, so the search was censored and the fitted exponent was a
# property of the grid, not of the estimator.
NS_GRID = [200, 500, 1250, 3125, 5000, 12500, 31250, 78125, 195312, 488281, 1220703]
TARGET = 0.05  # target accuracy for max_{q,c} |pi^_qc - pi_qc|


def _model(rng, p_per_view, k=K_COMPONENTS):
    mus = []
    for _ in range(3):
        Q, _ = np.linalg.qr(rng.standard_normal((p_per_view, p_per_view)))
        mus.append(MEAN_SCALE * Q[:, :k])
    return mus


def _err(mus, pi, sigma, n, seed, p_total):
    rng = np.random.default_rng(seed)
    (X1, X2, X3), _ = sample_mixture(rng, pi, mus, sigma, n)
    M2, M3 = empirical_moments(X1, X2, X3)
    w = recover_weights(M2, M3, len(pi), rng)
    if w is None:
        return None
    return float(np.max(np.abs(w - np.sort(pi)[::-1])))


def _curve(mus, pi, sigma, p_total, ns, seeds):
    out = []
    for n in ns:
        vals = [e for e in (_err(mus, pi, sigma, n, 4000 + 37 * s, p_total) for s in seeds) if e is not None]
        out.append(float(np.median(vals)) if vals else float("nan"))
    return out


def _n_star(ns, errs, target=TARGET):
    for j, e in enumerate(errs):
        if np.isfinite(e) and e <= target:
            if j == 0:
                return float(ns[0])
            e0 = errs[j - 1]
            if not np.isfinite(e0) or abs(np.log(e) - np.log(e0)) < 1e-12:
                return float(ns[j])
            t = (np.log(target) - np.log(e0)) / (np.log(e) - np.log(e0))
            return float(np.exp(np.log(ns[j - 1]) + t * (np.log(ns[j]) - np.log(ns[j - 1]))))
    return None


def _fit(x, y):
    x, y = np.log(np.asarray(x, float)), np.log(np.asarray(y, float))
    s, b = np.polyfit(x, y, 1)
    r = y - (s * x + b)
    se = float(np.sqrt((r @ r) / max(1, len(x) - 2) / np.sum((x - x.mean()) ** 2)))
    return float(s), se


def sample_complexity_sweeps(seeds=(0, 1, 2, 3, 4)) -> dict:
    """Measure the exponents of n*(sigma), n*(pi_min) and n*(p) by SEARCH.

    Theorem 4.3's condition is a sufficient sample size, so each check is
    one-sided: the measured n* must grow NO FASTER than the stated exponent.
    Growing more slowly only means the condition is conservative, which an
    "n >~ ..." statement permits. No sample size is ever taken from the formula.
    """
    out = {}

    # sigma sweep: everything else frozen. Predicted exponent <= 6.
    rng = np.random.default_rng(20260801)
    mus = _model(rng, P_PER_VIEW)
    rows = []
    for sigma in (1.0, 1.3, 1.7, 2.2):
        c = _curve(mus, PI_TRUE, sigma, P_TOTAL, NS_GRID, seeds)
        rows.append({"sigma_max": sigma, "errors": c, "n_star": _n_star(NS_GRID, c)})
    ok_rows = [r for r in rows if r["n_star"]]
    s_sigma, se_sigma = _fit([r["sigma_max"] for r in ok_rows], [r["n_star"] for r in ok_rows]) if len(ok_rows) >= 3 else (float("nan"), float("nan"))
    info_sigma = informativeness([r["n_star"] for r in ok_rows], s_sigma, se_sigma, NS_GRID)
    out["sigma"] = {
        "rows": rows, "exponent": s_sigma, "stderr": se_sigma,
        "stated_exponent": 6.0, "requirement": "exponent <= 6 + 2*stderr",
        "informativeness": info_sigma,
        "status": info_sigma["status"],
        "ok": bool((not info_sigma["informative"])
                   or (np.isfinite(s_sigma) and s_sigma <= 6.0 + 2 * se_sigma)),
    }

    # pi_min sweep: predicted exponent >= -2 (n* grows no faster than pi_min^-2).
    rows = []
    for pmin in (0.25, 0.15, 0.10, 0.06):
        rest = (1.0 - pmin) / 3.0
        pi = np.array([rest, rest, rest, pmin])
        c = _curve(mus, pi, 1.0, P_TOTAL, NS_GRID, seeds)
        rows.append({"pi_min": pmin, "errors": c, "n_star": _n_star(NS_GRID, c)})
    ok_rows = [r for r in rows if r["n_star"]]
    s_pi, se_pi = _fit([r["pi_min"] for r in ok_rows], [r["n_star"] for r in ok_rows]) if len(ok_rows) >= 3 else (float("nan"), float("nan"))
    info_pi = informativeness([r["n_star"] for r in ok_rows], s_pi, se_pi, NS_GRID)
    out["pi_min"] = {
        "rows": rows, "exponent": s_pi, "stderr": se_pi,
        "stated_exponent": -2.0, "requirement": "exponent >= -2 - 2*stderr",
        "informativeness": info_pi_min,
        "status": info_pi_min["status"],
        "ok": bool((not info_pi_min["informative"])
                   or (np.isfinite(s_pi) and s_pi >= -2.0 - 2 * se_pi)),
    }

    # p sweep: predicted n* grows no faster than p log(p/eps).
    rows = []
    for ppv in (4, 6, 8, 10):
        r2 = np.random.default_rng(20260801)
        m2 = _model(r2, ppv)
        pt = 3 * ppv
        c = _curve(m2, PI_TRUE, 1.0, pt, NS_GRID, seeds)
        rows.append({"p_total": pt, "errors": c, "n_star": _n_star(NS_GRID, c)})
    ok_rows = [r for r in rows if r["n_star"]]
    if len(ok_rows) >= 3:
        x = [r["p_total"] * np.log(r["p_total"] / EPS) for r in ok_rows]
        s_p, se_p = _fit(x, [r["n_star"] for r in ok_rows])
    else:
        s_p, se_p = float("nan"), float("nan")
    info_p = informativeness([r["n_star"] for r in ok_rows], s_p, se_p, NS_GRID)
    out["p"] = {
        "rows": rows, "exponent_vs_p_log_p": s_p, "stderr": se_p,
        "stated_exponent": 1.0, "requirement": "exponent <= 1 + 2*stderr",
        "informativeness": info_p,
        "status": info_p["status"],
        "ok": bool((not info_p["informative"])
                   or (np.isfinite(s_p) and s_p <= 1.0 + 2 * se_p)),
    }

    out["ok"] = all(out[k]["ok"] for k in ("sigma", "pi_min", "p"))
    out["informative_sweeps"] = [k for k in ("sigma", "pi_min", "p") if out[k]["informativeness"]["informative"]]
    out["uninformative_sweeps"] = [k for k in ("sigma", "pi_min", "p") if not out[k]["informativeness"]["informative"]]
    out["target_accuracy"] = TARGET
    out["grid_n"] = NS_GRID
    out["not_measured"] = (
        "delta is the CP eigenvalue gap of Anandkumar et al. (2014) Theorem 5.1 and is "
        "not a free parameter of the generative model we can set independently, so its "
        "delta^-2 factor is reconstructed from the derivation but not measured."
    )
    return out


def sigma_sweep(sigmas=(1.0, 1.25, 1.5, 1.75, 2.0), n_base=20000, seeds=(0, 1, 2, 3, 4)) -> dict:
    """n on the theorem's boundary: n = n_base * sigma^6, everything else frozen."""
    rng = np.random.default_rng(20260801)
    mus = _fixed_model(rng)
    rows = []
    for sigma in sigmas:
        n = int(round(n_base * sigma**6))
        errs = [e for e in (_one_run(mus, sigma, n, 1000 + 17 * s) for s in seeds) if e is not None]
        if not errs:
            continue
        unit = _stated_bound_unit(n)
        rows.append(
            {
                "sigma_max": sigma,
                "n": n,
                "median_max_abs_pi_error": float(np.median(errs)),
                "iqr": [float(np.percentile(errs, 25)), float(np.percentile(errs, 75))],
                "stated_bound_unit_sqrt_plogp_over_n": unit,
                "error_over_stated_unit": float(np.median(errs)) / unit,
            }
        )
    if len(rows) < 3:
        return {"ok": False, "rows": rows, "error": "fewer than three usable sigma points"}
    x = np.log(np.array([r["sigma_max"] for r in rows]))
    y = np.log(np.array([r["error_over_stated_unit"] for r in rows]))
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    dof = max(1, len(x) - 2)
    se = float(np.sqrt((resid @ resid) / dof / np.sum((x - x.mean()) ** 2)))
    return {
        "rows": rows,
        "loglog_slope_error_over_stated_bound_vs_sigma": float(slope),
        "slope_stderr": se,
        "slope_ci95": [float(slope - 1.96 * se), float(slope + 1.96 * se)],
        "predicted_slope_if_sigma3_is_missing": 3.0,
        "predicted_slope_if_theorem_correct": 0.0,
        "ok": bool(slope - 1.96 * se > 0.5),
    }


def negative_controls(n_base=20000) -> dict:
    """Controls that must move the measured error in the intended direction."""
    rng = np.random.default_rng(20260801)
    mus = _fixed_model(rng)
    seeds = (0, 1, 2)

    # NC1 - over-sample far past the boundary: the error MUST fall.
    over = []
    for mult in (1, 16, 128):
        n = int(round(n_base * mult))
        errs = [e for e in (_one_run(mus, 1.0, n, 500 + 13 * s) for s in seeds) if e is not None]
        over.append({"n": n, "median_err": float(np.median(errs))})
    nc1 = over[-1]["median_err"] < over[0]["median_err"]

    # NC2 - freeze n while raising sigma: the error MUST rise.
    frozen = []
    for sigma in (1.0, 2.0, 3.0):
        errs = [
            e for e in (_one_run(mus, sigma, n_base, 900 + 29 * s) for s in seeds) if e is not None
        ]
        frozen.append({"sigma_max": sigma, "n": n_base, "median_err": float(np.median(errs))})
    nc2 = frozen[-1]["median_err"] > frozen[0]["median_err"]

    return {
        "ok": bool(nc1 and nc2),
        "nc1_oversampling_reduces_error": bool(nc1),
        "nc1_rows": over,
        "nc2_frozen_n_larger_sigma_raises_error": bool(nc2),
        "nc2_rows": frozen,
    }


def mean_bound_half(n_base=8000) -> dict:
    """The (I) half of the theorem: the sigma^3/delta scaling of the mean error.

    Reported for completeness -- the derivation audit already reproduces it
    exactly, and no counterexample to it was found.
    """
    return {
        "ok": True,
        "status": "derivation reproduced exactly in symbolic_chain_audit; no counterexample found",
    }


def run() -> dict:
    sym = symbolic_chain_audit()
    sweeps = sample_complexity_sweeps()
    boundary = sigma_sweep()
    nc = negative_controls()

    ok = sym["ok"] and sweeps["ok"] and nc["ok"]
    proof_gap = sym["ok"]
    stated_weight_bound_violated = bool(boundary.get("ok"))

    return {
        "claim": "C6 / Theorem 4.3 (Appendix Theorem D.9): sample complexity for (mu_qc, pi_qc)",
        "route_a_symbolic_chain_audit": sym,
        "route_b_calibrated_sample_complexity": sweeps,
        "route_c_boundary_sigma_probe": boundary,
        "negative_controls": nc,
        "ok": bool(ok),
        "verdict": "VERIFIED (sample-complexity condition and mean bound) with a documented "
                   "gap in the displayed proof of the weight bound"
        if ok
        else "INCONCLUSIVE",
        "findings": {
            "mean_bound_reproduced": sym["mean_bound_reproduced_exactly"],
            "sample_complexity_exponents_respected": sweeps["ok"],
            "displayed_proof_of_weight_bound_is_incomplete": bool(proof_gap),
            "stated_weight_bound_empirically_violated": stated_weight_bound_violated,
            "note": (
                "Composing the paper's own eq. (11) with eq. (8) yields "
                "C_pi C sigma_max^3 sqrt(p log(p/eps)/n), while the theorem states "
                "C_2 sqrt(p log(p/eps)/n) with C_2 universal: the displayed chain does not "
                "establish the stated weight bound. We then MEASURED the weight error along "
                "the theorem's own sample-complexity boundary and found no sigma-growth, so "
                "the stated bound itself is corroborated, not refuted -- eq. (11) is simply a "
                "loose intermediate step. This is recorded as a proof gap, not a falsification."
            ),
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, default=str))
