"""Did a calibrated sweep measure an exponent, or merely fail to disagree?

Theorems 4.2 and 4.3 state sufficient conditions, so their contracts are one-sided:
the measured exponent must be no larger (4.3) or no smaller (4.2) than the stated one.
A one-sided contract is satisfied by a sweep that measured nothing at all, which is the
failure mode this module exists to catch. Three ways it happens, each of which must
disqualify the sweep rather than pass it:

  * fewer than three usable points, so no exponent is identifiable;
  * every n* pinned to an endpoint of the search grid, so the search was censored and
    the reported exponent is a property of the grid rather than of the estimator;
  * a fitted trend no larger than its own standard error, so no exponent was resolved.

A sweep that fails any of these is reported NOT INFORMATIVE and excluded from `ok`.
"""

from __future__ import annotations

import math


def informativeness(ys, slope, stderr, grid) -> dict:
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
    elif isinstance(stderr, float) and math.isfinite(stderr) and abs(slope) <= stderr:
        why.append(
            f"the fitted trend {slope:.4f} is no larger than its standard error "
            f"{stderr:.4f}; no exponent was resolved"
        )
    return {
        "informative": not why,
        "status": "MEASURED" if not why else "NOT INFORMATIVE",
        "not_informative_because": why,
        "n_usable_points": len(ys),
        "n_distinct_n_star": len(set(ys)),
    }
