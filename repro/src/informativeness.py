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


def estimators_agree(a_slope, a_se, b_slope, b_se) -> dict:
    """Do two independent estimators of the same exponent overlap at 95%?

    n* can be read as the crossing of the decay curve with the target, or by fitting
    the whole curve and solving. Both are estimates of the same quantity, so a real
    exponent must survive either. Where they disagree, the number being reported is a
    property of the estimator rather than of the system, and it cannot decide a claim.
    """
    vals = (a_slope, a_se, b_slope, b_se)
    if not all(isinstance(v, float) and math.isfinite(v) for v in vals):
        return {"agree": False, "why": "an estimator produced no finite exponent"}
    lo_a, hi_a = a_slope - 1.96 * a_se, a_slope + 1.96 * a_se
    lo_b, hi_b = b_slope - 1.96 * b_se, b_slope + 1.96 * b_se
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


def informativeness(ys, slope, stderr, grid, agreement=None) -> dict:
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
    elif isinstance(stderr, float) and math.isfinite(stderr) and abs(slope) <= 2 * stderr:
        why.append(
            f"the fitted trend {slope:.4f} +/- {stderr:.4f} has a 95% interval "
            f"[{slope - 1.96 * stderr:.4f}, {slope + 1.96 * stderr:.4f}] covering zero; "
            "no exponent was resolved"
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
