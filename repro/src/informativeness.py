"""Did a calibrated sweep measure an exponent, or merely fail to disagree?

Theorems 4.2 and 4.3 state sufficient conditions, so their contracts are one-sided:
the measured exponent must be no larger (4.3) or no smaller (4.2) than the stated one.
A one-sided contract is satisfied by a sweep that measured nothing at all, which is the
failure mode this module exists to catch. Three ways it happens, each of which must
disqualify the sweep rather than pass it:

  * fewer than three usable points, so no exponent is identifiable;
  * every n* pinned to an endpoint of the search grid, so the search was censored and
    the reported exponent is a property of the grid rather than of the estimator;
  * two independent n* estimators (curve-crossing and curve-fitting) whose 95%
    intervals for the exponent do not overlap, so the number is a property of the
    estimator rather than of the system;
  * a fitted trend whose 95% interval covers zero, so no exponent was resolved. The
    threshold is 2 standard errors rather than 1: a slope of 0.60 +/- 0.56 has a 95%
    interval of [-0.50, +1.71], and a sweep that cannot distinguish its exponent from
    zero has not measured one, however comfortably it clears a one-sided contract.

A sweep that fails any of these is reported NOT INFORMATIVE and excluded from `ok`.
"""

from __future__ import annotations

import math


def usable_setting(n_star_fit: dict | None, n_star_crossing, max_ratio=3.0,
                   min_r2=0.5, min_abs_slope=0.15) -> dict:
    """Is a single sweep setting's n* trustworthy enough to enter an exponent fit?

    Aggregate-slope agreement is too weak a test. Two estimators can produce
    overlapping *slope* intervals while disagreeing by an order of magnitude at every
    individual point, in opposite directions -- which is agreement between two fits
    through noise, not corroboration.

    Each setting must therefore pass on its own before it may contribute:

      * the two n* estimators agree within `max_ratio`;
      * the decay fit that produces n* actually describes the curve (r2 >= min_r2);
      * the decay is steep enough that extrapolating to the target is stable. n* is
        exp((log target - a)/b), so d log n* / d log err = -1/b: at b = -0.076 a 10%
        error wobble moves n* by ~3.5x, and the reported n* is then a property of the
        noise. Requiring |b| >= 0.15 caps that amplification at ~7x per e-fold.

    A setting failing any of these is dropped and named, rather than silently averaged
    into an exponent that then carries a standard error computed as if n* were exact.
    """
    if not isinstance(n_star_fit, dict) or n_star_fit.get("n_star") is None:
        return {"usable": False, "why": "curve-fitting produced no n*"}
    nf, nc = n_star_fit.get("n_star"), n_star_crossing
    r2, slope = n_star_fit.get("r2"), n_star_fit.get("decay_slope")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (nf, nc, r2, slope)):
        return {"usable": False, "why": "an estimator produced no finite value"}
    if nf <= 0 or nc <= 0:
        return {"usable": False, "why": "a non-positive n* cannot enter a log fit"}
    ratio = max(nf, nc) / min(nf, nc)
    why = []
    if ratio > max_ratio:
        why.append(f"the two n* estimators disagree by {ratio:.1f}x (limit {max_ratio}x)")
    if r2 < min_r2:
        why.append(f"the decay fit explains little of the curve (r2={r2:.2f} < {min_r2})")
    if abs(slope) < min_abs_slope:
        why.append(
            f"the decay is too shallow to extrapolate (slope={slope:.3f}, "
            f"|slope| < {min_abs_slope}); n* amplifies noise by ~{1/max(abs(slope),1e-9):.0f}x"
        )
    return {
        "usable": not why,
        "n_star_fit": nf,
        "n_star_crossing": nc,
        "ratio": ratio,
        "r2": r2,
        "decay_slope": slope,
        "why": "; ".join(why),
    }


def screen_settings(rows, key) -> dict:
    """Apply `usable_setting` across a sweep and report what survives."""
    kept, dropped = [], []
    for r in rows:
        u = usable_setting(r.get("n_star_fit"), r.get("n_star_crossing"))
        rec = {key: r.get(key), **u}
        (kept if u["usable"] else dropped).append(rec)
    return {
        "n_settings": len(rows),
        "n_usable": len(kept),
        "usable": kept,
        "dropped": dropped,
        "enough_usable_settings": len(kept) >= 3,
    }


def t_crit(n_points: int, n_params: int = 2) -> float:
    """Two-sided 95% critical value for a fit with `n_points - n_params` residual df.

    Every interval in this campaign comes from a log-log least-squares fit over a handful
    of settings, and a handful of settings is not the normal limit. A 5-point, 2-parameter
    fit has 3 residual degrees of freedom, where t(0.975, 3) = 3.182 -- using 1.96 there
    reports an interval 38% narrower than it is.

    That is not a presentational detail. A blind reviewer showed that Claim 6's boundary
    probe was published as EXCLUDING the slope of 3 that a missing sigma^3 factor predicts;
    at the correct width its interval INCLUDES 3, so the probe discriminates nothing and
    the conclusion drawn from it had to be withdrawn. Anything that reports a 95% interval
    must call this.
    """
    df = max(int(n_points) - int(n_params), 1)
    from scipy import stats
    return float(stats.t.ppf(0.975, df))


def ci95(slope: float, stderr: float, n_points: int, n_params: int = 2) -> list:
    k = t_crit(n_points, n_params)
    return [float(slope - k * stderr), float(slope + k * stderr)]


def estimators_agree(a_slope, a_se, b_slope, b_se, a_n=None, b_n=None) -> dict:
    """Do two independent estimators of the same exponent overlap at 95%?

    n* can be read as the crossing of the decay curve with the target, or by fitting
    the whole curve and solving. Both are estimates of the same quantity, so a real
    exponent must survive either. Where they disagree, the number being reported is a
    property of the estimator rather than of the system, and it cannot decide a claim.
    """
    vals = (a_slope, a_se, b_slope, b_se)
    if not all(isinstance(v, float) and math.isfinite(v) for v in vals):
        return {"agree": False, "why": "an estimator produced no finite exponent"}
    ka = t_crit(a_n) if a_n else 1.96
    kb = t_crit(b_n) if b_n else 1.96
    lo_a, hi_a = a_slope - ka * a_se, a_slope + ka * a_se
    lo_b, hi_b = b_slope - kb * b_se, b_slope + kb * b_se
    overlap = max(lo_a, lo_b) <= min(hi_a, hi_b)
    # Both must individually resolve an exponent first. Otherwise a garbage estimator
    # with a very wide interval "agrees" with everything, and agreement becomes another
    # way of passing without measuring.
    a_resolved, b_resolved = lo_a * hi_a > 0, lo_b * hi_b > 0
    if not (a_resolved and b_resolved):
        which = "curve-fitting" if not a_resolved else "curve-crossing"
        return {
            "agree": False,
            "fitted_ci95": [lo_a, hi_a],
            "crossing_ci95": [lo_b, hi_b],
            "why": f"the {which} estimator's own 95% interval covers zero, so it "
                   "resolved no exponent; agreement with an unresolved estimator is "
                   "not evidence",
        }
    return {
        "agree": bool(overlap),
        "fitted_ci95": [lo_a, hi_a],
        "crossing_ci95": [lo_b, hi_b],
        "why": "" if overlap else
               f"the two estimators' 95% intervals [{lo_a:.3f}, {hi_a:.3f}] and "
               f"[{lo_b:.3f}, {hi_b:.3f}] do not overlap; the exponent is a property "
               "of the estimator, not of the system",
    }


def informativeness(ys, slope, stderr, grid, agreement=None, n_points=None) -> dict:
    ys = [y for y in ys if y is not None and math.isfinite(y)]
    why = []
    if len(ys) < 3:
        why.append(f"only {len(ys)} usable points; three are needed to identify an exponent")
    if len(set(ys)) < 3:
        why.append(f"only {len(set(ys))} distinct n* value(s); the sweep does not discriminate")
    if ys and grid and (all(y <= min(grid) for y in ys) or all(y >= max(grid) for y in ys)):
        why.append(
            "every n* sits at an endpoint of the search grid "
            f"[{min(grid)}, {max(grid)}]; the search was censored, so the exponent is a "
            "property of the grid rather than of the estimator"
        )
    if not (isinstance(slope, float) and math.isfinite(slope)):
        why.append("no finite slope")
    elif isinstance(stderr, float) and math.isfinite(stderr):
        k = t_crit(n_points) if n_points else 1.96
        lo, hi = slope - k * stderr, slope + k * stderr
        if lo * hi <= 0:
            why.append(
                f"the fitted trend {slope:.4f} +/- {stderr:.4f} has a 95% interval "
                f"[{lo:.4f}, {hi:.4f}] covering zero; no exponent was resolved "
                f"(interval width uses t(0.975, {max((n_points or 4) - 2, 1)}) = {k:.3f}, "
                "not the normal 1.96)"
            )
    if agreement is not None and not agreement.get("agree"):
        why.append(agreement.get("why") or "the two n* estimators disagree")
    return {
        "informative": not why,
        "estimator_agreement": agreement,
        "status": "MEASURED" if not why else "NOT INFORMATIVE",
        "not_informative_because": why,
        "n_usable_points": len(ys),
        "n_distinct_n_star": len(set(ys)),
    }


def tristate(informative: bool, passed: bool):
    """Publish a contract's outcome as True / False / "NOT MEASURED".

    A one-sided contract evaluated on a sweep that resolved no exponent is *satisfied*,
    and writing that satisfaction into the record as `true` is how a reader ends up
    believing an exponent was measured when the page next to it says NOT MEASURED. The
    verifier still treats such a sweep as non-failing -- absence of evidence is not
    failed evidence -- but the published value must say which of the two it is.
    """
    if not informative:
        return "NOT MEASURED"
    return bool(passed)


def with_screen(info: dict, screen: dict) -> dict:
    """Fold a per-setting screen into a sweep's informativeness verdict.

    A sweep whose usable settings have fallen below three has not measured an
    exponent, however well the surviving points happen to line up.
    """
    info = dict(info)
    info["per_setting_screen"] = {
        "n_settings": screen["n_settings"],
        "n_usable": screen["n_usable"],
        "dropped": [{k: v for k, v in d.items() if k in ("why",) or not isinstance(v, dict)}
                    for d in screen["dropped"]],
    }
    if not screen["enough_usable_settings"]:
        info["informative"] = False
        info["status"] = "NOT INFORMATIVE"
        why = (f"only {screen['n_usable']} of {screen['n_settings']} settings survived "
               "the per-setting screen; fewer than three usable n* values")
        info["why"] = (info.get("why") + "; " + why) if info.get("why") else why
    return info
