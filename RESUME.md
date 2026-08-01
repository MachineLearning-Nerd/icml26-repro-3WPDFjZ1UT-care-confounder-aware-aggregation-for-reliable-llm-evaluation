# Resume state — 3WPDFjZ1UT (CARE)

**Blocked on Hugging Face pre-paid credits.** All jobs on the `DineshAI` account were
cancelled by the platform (90 CANCELED) and new job submissions return
`402 Payment Required: Pre-paid credit balance is insufficient`. No research compute can
run until credits are restored. Local execution is not a substitute — this campaign is
authorised to run research compute only on Hugging Face `cpu-upgrade`.

Nothing has been published. The live Space `DineshAI/3WPDFjZ1UT` is untouched at its
judged revision `2a647ca068d0943b4c3a54d2f7940594fac5287f` (5/12).

## To resume, in order

1. Relaunch the canonical run (12 h timeout; Table 2 costs ~112 min/seed × 5 seeds):

   ```
   SHA=$(git rev-parse HEAD)
   hf jobs run --flavor cpu-upgrade --timeout 12h -e CARE_HF_FLAVOR=cpu-upgrade --detach \
     ghcr.io/astral-sh/uv:python3.11-bookworm bash -c "set -eo pipefail
   apt-get update -qq && apt-get install -y -qq git
   curl -fsSL https://raw.githubusercontent.com/MachineLearning-Nerd/icml26-repro-3WPDFjZ1UT-care-confounder-aware-aggregation-for-reliable-llm-evaluation/$SHA/repro/orx/run_hf_job.sh -o /tmp/run_hf_job.sh
   BRANCH=main bash /tmp/run_hf_job.sh"
   ```

2. Capture the JSON printed between `===CARE_VERDICT_BEGIN===` and
   `===CARE_VERDICT_END===` into `verdict.json` (job filesystems are discarded, which is
   why the verdict is printed to stdout).

3. Stage and gate:

   ```
   python repro/publish/publish_space.py stage    <staging>   # seeds from the LIVE Space
   rsync -a repro/pages/ <staging>/pages/                     # overlay new pages
   python repro/publish/make_raw.py     verdict.json <staging>
   python repro/publish/fill_results.py verdict.json <staging>
   python repro/publish/check_links.py  <staging>
   python repro/publish/visibility_matrix.py <staging> redteam.json
   python repro/publish/publish_space.py check    <staging>
   ```

4. Run the evaluator-blind red team on the staged copy, write its per-claim verdicts to
   `redteam.json`, re-run the visibility gate, then
   `python repro/publish/publish_space.py upload <staging>`.

5. Mirror to GitHub `main`/`master`, confirm with `git ls-remote`, and mark the Space as
   awaiting judge. Do not state a score until the live judge evaluates the new revision.

## What is already done

* Claims 4-6 verifiers all pass their contracts on this SHA (measured on
  `cpu-upgrade`: C4 53.0 s, C5 111.8 s, C6 331.3 s).
* Table 1 (ASSET) reproduces end-to-end with the authors' code at `72f5b29`, ~50 s per
  seed after the first. Table 2 had completed one full seed (6733.5 s) before the
  cancellation; no seed results survived, because job filesystems are discarded.
* All 19 candidate pages are written and reachable from the entrypoint; every measured
  number is spliced from `verdict.json` by `repro/publish/fill_results.py` (30 blocks),
  so no figure is hand-transcribed.
* All release gates are implemented and each was tested against a deliberately broken
  copy to confirm it fails when it should.

## Known issues fixed on this branch, do not reintroduce

* `independent_check` asserted the Summarize 13.4 % against the claim string's 0.705,
  which yields 15.46 % and made the checker fail unconditionally. It is now asserted
  against the strongest Table 2 baseline (GLAD, 0.718), with a second assertion that
  0.705 does *not* reproduce 13.4 %.
* `recheck_c6_slope` read a key C6 no longer emits, so it silently returned
  `{"available": False}` while the Claim 6 page advertised the check.
