"""Evaluator-blind traversal: every link reachable from the entrypoint must resolve.

    python repro/publish/check_links.py <staging_dir>

Starts at pages/index.md and follows only links, exactly as an evaluator would. Exits
nonzero if any target is missing, or if a page is unreachable from the entrypoint —
an unreachable page earns no credit however good its evidence is.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINK = re.compile(r"\]\(([^)]+)\)")


def page_for(root: Path, slug: str) -> Path:
    return root / "pages" / "index.md" if slug == "index" else root / "pages" / slug / "page.md"


def main(staging: str) -> int:
    root = Path(staging)
    start = root / "pages" / "index.md"
    if not start.exists():
        print(f"no entrypoint at {start}")
        return 1

    seen, queue, broken = {"index"}, ["index"], []
    while queue:
        slug = queue.pop()
        src = page_for(root, slug)
        for target in LINK.findall(src.read_text()):
            if target.startswith("http"):
                continue
            if target.startswith("#/"):
                nxt = target[2:]
                if not page_for(root, nxt).exists():
                    broken.append((slug, target))
                elif nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
            elif not (root / target).exists():
                broken.append((slug, target))

    all_pages = {"index"} | {p.parent.name for p in root.glob("pages/*/page.md")}
    orphans = sorted(all_pages - seen)

    for slug, target in broken:
        print(f"BROKEN  {slug} -> {target}")
    for o in orphans:
        print(f"ORPHAN  pages/{o}/page.md is not reachable from the entrypoint")
    print(f"reachable pages: {len(seen)}/{len(all_pages)}  broken links: {len(broken)}")
    return 1 if broken or orphans else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
