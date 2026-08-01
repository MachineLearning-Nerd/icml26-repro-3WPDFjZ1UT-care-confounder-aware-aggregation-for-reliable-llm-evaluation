#!/usr/bin/env bash
# Bootstrap for a Hugging Face `cpu-upgrade` job.
#
#   BRANCH=<git branch> [CARE_ENTRY="repro/src/bench_shard.py t1 2024"] bash run_hf_job.sh
#
# Clones this repository and the authors' released code (pinned by SHA, so the
# judge-score matrices are byte-identical across runs), syncs the locked
# environment, and executes the one fixed run command.
set -eo pipefail

BRANCH="${BRANCH:-main}"
CARE_SHA="72f5b29a822d9934d31777c10a5c38369884c9dc"
REPO="https://github.com/MachineLearning-Nerd/icml26-repro-3WPDFjZ1UT-care-confounder-aware-aggregation-for-reliable-llm-evaluation.git"

command -v git >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq git)

git clone --depth 1 --branch "$BRANCH" "$REPO" repo
cd repo
echo "[job] repo branch=$BRANCH sha=$(git rev-parse HEAD)"

mkdir -p external
git clone --filter=blob:none https://github.com/SprocketLab/CARE.git external/CARE
git -C external/CARE checkout --quiet "$CARE_SHA"
echo "[job] official CARE sha=$(git -C external/CARE rev-parse HEAD)"

export CARE_OFFICIAL_DIR="$PWD/external/CARE"
export PYTHONHASHSEED=0
export CARE_HF_FLAVOR="${CARE_HF_FLAVOR:-cpu-upgrade}"

uv sync --frozen

# CARE_ENTRY lets a one-hour shard job reuse this identical bootstrap. Unset, the
# bootstrap runs the one fixed command that produces the canonical verdict.
uv run python ${CARE_ENTRY:-repro/src/run_all.py}
