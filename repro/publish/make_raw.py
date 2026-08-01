"""Mechanical extraction of the per-claim CSVs from verdict.json.

    python repro/publish/make_raw.py <verdict.json> <staging_dir>

Writes staging_dir/raw/. Nothing here computes anything: every row is copied out of
the verdict JSON, so a CSV cannot disagree with the run that produced it.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

# Each CSV collects every list-of-dicts found under these subtrees, tagged by the
# path it came from, so a renamed inner key changes a tag rather than losing a row.
TARGETS = {
    "table1_asset.csv": ["claims.C1_C2_C3_tables.table1_asset"],
    "table2.csv": ["claims.C1_C2_C3_tables.table2"],
    "c4_constant_search.csv": [
        "claims.C4_prop41.thm_d4_exact_supremum",
        "claims.C4_prop41.thm_d4_finite_perturbation",
        "claims.C4_prop41.maintext_bound_scaling_counterexample",
    ],
    "c5_rate.csv": [
        "claims.C5_thm42.route_c_calibrated_rate",
        "claims.C5_thm42.route_b_davis_kahan_constant",
    ],
    "c6_sigma_sweep.csv": [
        "claims.C6_thm43.route_b_calibrated_sample_complexity",
        "claims.C6_thm43.route_c_boundary_sigma_probe",
    ],
}


def dig(obj, dotted: str):
    for part in dotted.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def tables(node, prefix: str):
    """Yield (tag, rows) for every list-of-dicts reachable under node."""
    if isinstance(node, list) and node and all(isinstance(x, dict) for x in node):
        yield prefix, node
        return
    if isinstance(node, dict):
        for k, v in node.items():
            yield from tables(v, f"{prefix}.{k}" if prefix else k)


def scalars(node, prefix: str, out: dict):
    if isinstance(node, dict):
        for k, v in node.items():
            scalars(v, f"{prefix}.{k}" if prefix else k, out)
    elif isinstance(node, (int, float, bool, str)) or node is None:
        out[prefix] = node


def write_csv(path: Path, rows: list[dict]) -> None:
    fields, seen = [], set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                fields.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})
    print(f"  {path.name}: {len(rows)} rows x {len(fields)} cols")


def main(verdict_path: str, staging: str) -> int:
    verdict = json.loads(Path(verdict_path).read_text())
    raw = Path(staging) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "verdict.json").write_text(json.dumps(verdict, indent=2, default=str))
    print(f"raw/verdict.json written ({(raw / 'verdict.json').stat().st_size} bytes)")

    for name, paths in TARGETS.items():
        rows = []
        for dotted in paths:
            node = dig(verdict, dotted)
            if node is None:
                print(f"  ! {name}: {dotted} absent")
                continue
            found = list(tables(node, dotted))
            for tag, block in found:
                for r in block:
                    rows.append({"source": tag, **{k: v for k, v in r.items()}})
            if not found:
                flat = {}
                scalars(node, dotted, flat)
                if flat:
                    rows.append({"source": dotted, **flat})
        if not rows:
            print(f"  ! {name}: nothing extracted, not written")
            continue
        write_csv(raw / name, rows)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
