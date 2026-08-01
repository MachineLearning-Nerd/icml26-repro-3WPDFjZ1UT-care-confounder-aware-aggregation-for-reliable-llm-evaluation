"""Machine-check the evaluator-visibility matrix against the staged candidate.

    python repro/publish/visibility_matrix.py <staging_dir> [redteam.json]

Every column is *checked*, not asserted: the script opens each claim page in the
staging directory and verifies that the required artifact is actually reachable from
it. It rewrites the table on pages/visibility-matrix/page.md and exits nonzero if any
cell fails, so publication is blocked while a claim is undiscoverable.

The "Reviewer verdict" column is supplied by the evaluator-blind red team via an
optional JSON file mapping claim id -> verdict string; without it the column reads
"pending" and the gate fails, because an unreviewed matrix is not a passed matrix.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# A "Control" cell used to be a presence check: does the page have a negative-control
# block? Presence is not discrimination. A control that runs the method on corrupted
# input can fail; an arithmetic non-equality between two fixed rationals cannot, however
# correctly it is reported. The distinction is declared per claim here and rendered, so
# the column a judge scans cannot read the same for both.
CONTROL_IS_DISCRIMINATING = {
    "C1": True,   # CARE re-run on column-permuted ASSET judge scores
    "C2": True,   # same permutation control
    "C3": False,  # arithmetic only: 0.705 must not reproduce 13.4%. See Limitations 18.
    "C4": True,   # exact counterexamples; the appendix form is checked and survives
    "C5": True,   # stage decomposition + oracle-sparse control, either could fail
    "C6": True,   # NC1 over-sampling and NC2 frozen-n, both re-run the estimator
}

# A "Checker" cell used to be `a link to independent_check.py` plus the substring
# "ndependent check" somewhere on the page. That passes for a claim the checker never
# looks at, and it is how C3's cell read green while the page's own header said the
# checker did not recompute the argmax. The cell now additionally requires that the
# staged run's `independent_check` actually produced the named outputs for this claim,
# and that each one carries a boolean-valued key -- i.e. it decided something.
CHECKER_KEYS = {
    "C1": ["table_percentages_exact_rational", "appendix_consistency_exact"],
    "C2": ["c2_unit_invariance_exact", "agreement_with_claim_module"],
    "C3": ["table2_second_transcription", "table_percentages_exact_rational"],
    "C4": ["prop41_counterexample_mpmath", "first_order_formula_vs_finite_difference"],
    "C5": ["davis_kahan_by_principal_angle", "c5_stage_slope_recheck"],
    "C6": ["c6_p_exponent_recheck", "c6_slope_recheck"],
}

CLAIMS = [
    ("C1", "claim-1-ultrafeedback", "claim_c123_benchmarks.py"),
    ("C2", "claim-2-average-improvement", "claim_c123_benchmarks.py"),
    ("C3", "claim-3-table2", "claim_c123_benchmarks.py"),
    ("C4", "claim-4-proposition-41", "claim_c4_prop41.py"),
    ("C5", "claim-5-theorem-42", "claim_c5_thm42.py"),
    ("C6", "claim-6-theorem-43", "claim_c6_thm43.py"),
]

LINK = re.compile(r"\]\(([^)]+)\)")
TABLE_ROW = re.compile(r"^\|.*\d.*\|", re.M)
FILLED = re.compile(r"<!-- FILL:([a-z0-9_.]+) -->\n(.*?)<!-- /FILL -->", re.S)


def links(text):
    return set(LINK.findall(text))


def checker_ran_for(root: Path, cid: str) -> bool:
    """Did the independent checker produce a decided output for THIS claim?"""
    vf = root / "raw" / "verdict.json"
    if not vf.exists():
        return False
    chk = (json.loads(vf.read_text()).get("independent_check") or {})
    for key in CHECKER_KEYS[cid]:
        block = chk.get(key)
        if not isinstance(block, dict):
            return False
        if not _decided_something(block):
            return False
    return True


def _decided_something(o) -> bool:
    """Does this checker output contain a decision anywhere, at any depth?

    Some blocks decide at the top level (`agree: false`), others per row inside a list
    (`consistent: true` for each of six datasets). A shallow scan would call the second
    kind undecided, so this walks the whole structure.
    """
    if isinstance(o, bool):
        return True
    if isinstance(o, dict):
        return any(_decided_something(v) for v in o.values())
    if isinstance(o, list):
        return any(_decided_something(v) for v in o)
    return False


def check_page(root: Path, slug: str, src_name: str, cid: str):
    page = root / "pages" / slug / "page.md"
    if not page.exists():
        return None, {"missing page": False}
    text = page.read_text()
    ls = links(text)
    blocks = dict(FILLED.findall(text))

    def linked(pred):
        return any(pred(t) and (root / t).exists() for t in ls)

    # Data inline: at least one FILL block that actually rendered a numeric table.
    inline = any(TABLE_ROW.search(b) for b in blocks.values())
    unrendered = [bid for bid, b in blocks.items() if "pending release run" in b]

    checks = {
        "Code visible": linked(lambda t: t.endswith(f"src/{src_name}")),
        "Data inline": bool(inline) and not unrendered,
        # Both, deliberately: the whole verdict AND this claim's own extract. An "any"
        # here would let a claim-specific CSV vanish while verdict.json kept the cell green.
        "Raw link": linked(lambda t: t == "raw/verdict.json")
        and linked(lambda t: t.startswith("raw/") and t.endswith(".csv")),
        "Checker": (linked(lambda t: t.endswith("independent_check.py"))
                    and "ndependent check" in text
                    and checker_ran_for(root, cid)),
        "Control": "egative control" in text and any(
            bid.endswith(("control", "controls")) for bid in blocks
        ),
        "Exact claim tested": bool(re.search(r"^> .+", text, re.M)) and "raw/claim_contract.json" in text,
    }
    return checks, unrendered


def main(staging: str, redteam: str | None) -> int:
    root = Path(staging)
    verdicts = json.loads(Path(redteam).read_text()) if redteam else {}

    cols = ["Code visible", "Data inline", "Raw link", "Checker", "Control", "Exact claim tested"]
    rows, failures = [], []
    for cid, slug, src in CLAIMS:
        checks, unrendered = check_page(root, slug, src, cid)
        if checks is None:
            failures.append(f"{cid}: pages/{slug}/page.md missing")
            continue
        for name, ok in checks.items():
            if not ok:
                failures.append(f"{cid}: {name}")
        for bid in unrendered:
            failures.append(f"{cid}: block {bid} never rendered")
        verdict = verdicts.get(cid, "pending")
        if verdict == "pending":
            failures.append(f"{cid}: reviewer verdict pending")
        rows.append(
            "| "
            + " | ".join(
                [cid, f"[{slug}](#/{slug})"]
                + [("✗" if not checks[c] else
                    "✓" if c != "Control" or CONTROL_IS_DISCRIMINATING[cid] else
                    "◐ arithmetic only")
                   for c in cols]
                + [verdict]
            )
            + " |"
        )

    header = "| Claim | Canonical page | " + " | ".join(cols) + " | Reviewer verdict |"
    sep = "|" + "---|" * (len(cols) + 3)
    matrix = "\n".join([header, sep] + rows)

    page = root / "pages" / "visibility-matrix" / "page.md"
    text = page.read_text()
    new, n = re.subn(
        r"(<!-- MATRIX -->\n).*?(<!-- /MATRIX -->)",
        lambda m: m.group(1) + matrix + "\n" + m.group(2),
        text,
        flags=re.S,
    )
    if n:
        page.write_text(new)
        print(f"visibility matrix written ({len(rows)} rows)")
    else:
        print("! pages/visibility-matrix/page.md has no <!-- MATRIX --> block; not rewritten")
        failures.append("matrix block missing")

    for f in failures:
        print(f"VISIBILITY FAIL  {f}")
    print(f"{len(failures)} failing cells")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None))
