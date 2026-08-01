"""Text-only publication to the existing Hugging Face Space DineshAI/3WPDFjZ1UT.

Never creates a second Space. Never uploads binaries. Before uploading it proves
that the judged revision's file set is a subset of the candidate's, so no existing
page or evidence file can be dropped.

    python repro/publish/publish_space.py stage   <staging_dir>   # build candidate
    python repro/publish/publish_space.py check    <staging_dir>   # subset + manifest
    python repro/publish/publish_space.py upload   <staging_dir>   # commit + verify
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi, get_token, hf_hub_download, snapshot_download

REPO = "DineshAI/3WPDFjZ1UT"
JUDGED_REV = "2a647ca068d0943b4c3a54d2f7940594fac5287f"

# Every path we are allowed to write. Text only.
ALLOWLIST = [
    "logbook.json",
    "pages/index.md",
    "pages/overview/page.md",
    "pages/claims/page.md",
    "pages/conclusion/page.md",
    "pages/current-verification/page.md",
    "pages/claim-1-ultrafeedback/page.md",
    "pages/claim-2-average-improvement/page.md",
    "pages/claim-3-table2/page.md",
    "pages/claim-4-proposition-41/page.md",
    "pages/claim-5-theorem-42/page.md",
    "pages/claim-6-theorem-43/page.md",
    "pages/source-audit/page.md",
    "pages/environment-and-command/page.md",
    "pages/raw-data/page.md",
    "pages/visibility-matrix/page.md",
    "pages/limitations/page.md",
    "pages/historical-2026-07-30/page.md",
    "repro/src/run_all.py",
    "repro/src/threads.py",
    "repro/src/paper_source.py",
    "repro/src/tensor_mom.py",
    "repro/src/independent_check.py",
    "repro/src/claim_c123_benchmarks.py",
    "repro/src/claim_c4_prop41.py",
    "repro/src/claim_c5_thm42.py",
    "repro/src/claim_c6_thm43.py",
    "repro/orx/run_hf_job.sh",
    "repro/env/pyproject.toml",
    "repro/env/uv.lock",
    "raw/verdict.json",
    "raw/claim_contract.json",
    "raw/source_audit.md",
    "raw/method.md",
    "raw/table1_asset.csv",
    "raw/table2.csv",
    "raw/c5_rate.csv",
    "raw/c6_sigma_sweep.csv",
    "raw/c4_constant_search.csv",
]

PAGE_TREE = [
    ("current-verification", "Current verification (2026-08-01)"),
    ("claim-1-ultrafeedback", "Claim 1 - UltraFeedback MAE"),
    ("claim-2-average-improvement", "Claim 2 - 17.37% over averaging"),
    ("claim-3-table2", "Claim 3 - Table 2, best on 5 of 6"),
    ("claim-4-proposition-41", "Claim 4 - Proposition 4.1"),
    ("claim-5-theorem-42", "Claim 5 - Theorem 4.2"),
    ("claim-6-theorem-43", "Claim 6 - Theorem 4.3"),
    ("source-audit", "Source audit and exact quantifiers"),
    ("environment-and-command", "Fixed command, environment, seeds, runtime"),
    ("raw-data", "Raw data downloads"),
    ("visibility-matrix", "Visibility matrix"),
    ("limitations", "Limitations and deviations"),
    ("overview", "Overview"),
    ("claims", "Claims"),
    ("conclusion", "Conclusion"),
    ("historical-2026-07-30", "Historical rejected baseline - narrative (2026-07-30)"),
    ("evidence", "Historical rejected baseline - evidence (2026-07-30)"),
    ("verification-run", "Historical rejected baseline - verifier (2026-07-30)"),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stage(work: Path) -> None:
    """Seed the staging directory from the LIVE Space, never from a local guess."""
    token = get_token()
    work.mkdir(parents=True, exist_ok=True)
    snapshot_download(REPO, repo_type="space", local_dir=str(work), token=token)
    print(f"seeded {work} from live {REPO}")


def build_logbook(work: Path) -> None:
    lb = json.loads((work / "logbook.json").read_text())
    children = []
    for slug, title in PAGE_TREE:
        f = f"pages/{slug}/page.md"
        if not (work / f).exists():
            print(f"  ! missing {f}, skipping node")
            continue
        children.append({"slug": slug, "title": title, "file": f, "children": []})
    lb["root"]["children"] = children
    lb["updated_at"] = "2026-08-01T00:00:00+00:00"
    (work / "logbook.json").write_text(json.dumps(lb, indent=1, ensure_ascii=False) + "\n")
    print(f"logbook.json rebuilt with {len(children)} nodes")


def check(work: Path) -> int:
    token = get_token()
    judged = work.parent / "judged_ref"
    if not judged.exists():
        snapshot_download(
            REPO, repo_type="space", revision=JUDGED_REV, local_dir=str(judged), token=token
        )

    def files(root: Path):
        return {
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and ".cache" not in p.parts and ".git" not in p.parts
        }

    old, new = files(judged), files(work)
    missing = sorted(old - new)
    print(f"judged files: {len(old)}  candidate files: {len(new)}")
    if missing:
        print("SUBSET CHECK FAILED, these judged files are absent from the candidate:")
        for m in missing:
            print("   ", m)
        return 1
    print("SUBSET CHECK PASSED: judged file set is a subset of the candidate file set")

    # Historical evidence files must be byte-identical.
    frozen = ["pages/evidence/page.md", "pages/verification-run/page.md"]
    for f in frozen:
        a, b = judged / f, work / f
        if sha256(a) != sha256(b):
            print(f"FROZEN FILE MODIFIED: {f}")
            return 1
    print("frozen historical evidence files are byte-identical")

    json.loads((work / "logbook.json").read_text())
    print("logbook.json parses")

    manifest = {}
    for rel in ALLOWLIST:
        p = work / rel
        if p.exists():
            manifest[rel] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    (work.parent / "upload_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"manifest written for {len(manifest)} paths -> {work.parent/'upload_manifest.json'}")

    # No secrets.
    bad = []
    for rel in manifest:
        txt = (work / rel).read_text(errors="ignore")
        for needle in ("hf_", "HF_TOKEN=", "github_pat", "ghp_", "sk-"):
            if needle in txt and rel.endswith((".md", ".json", ".sh")):
                bad.append((rel, needle))
    if bad:
        print("POSSIBLE SECRET MATERIAL:", bad)
        return 1
    print("no secret-shaped strings in the allowlisted text")
    return 0


def upload(work: Path) -> int:
    token = get_token()
    api = HfApi(token=token)
    who = api.whoami(token=token)
    print("authenticated as", who.get("name"))
    present = [p for p in ALLOWLIST if (work / p).exists()]
    api.upload_folder(
        repo_id=REPO,
        repo_type="space",
        folder_path=str(work),
        allow_patterns=present,
        token=token,
        commit_message="Full-scale benchmark reproduction and machine-checked theory verdicts for CARE",
    )
    sha = api.repo_info(REPO, repo_type="space", token=token).sha
    print("new revision:", sha)

    manifest = json.loads((work.parent / "upload_manifest.json").read_text())
    bad = []
    for rel, meta in manifest.items():
        got = hf_hub_download(
            REPO, rel, repo_type="space", revision=sha, force_download=True, token=token
        )
        if sha256(Path(got)) != meta["sha256"]:
            bad.append(rel)
    if bad:
        print("HASH MISMATCH after upload:", bad)
        return 1
    print(f"all {len(manifest)} uploaded paths verified byte-identical at {sha}")
    (work.parent / "published_revision.txt").write_text(sha + "\n")
    return 0


if __name__ == "__main__":
    cmd, target = sys.argv[1], Path(sys.argv[2])
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    if cmd == "stage":
        stage(target)
    elif cmd == "logbook":
        build_logbook(target)
    elif cmd == "check":
        raise SystemExit(check(target))
    elif cmd == "upload":
        raise SystemExit(upload(target))
    else:
        raise SystemExit(f"unknown command {cmd}")
