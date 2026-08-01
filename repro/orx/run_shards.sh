#!/usr/bin/env bash
# Launch every benchmark shard as its own Hugging Face job, each capped at one hour.
#
#   bash repro/orx/run_shards.sh launch          # submit all shards
#   bash repro/orx/run_shards.sh collect <dir>   # pull results into repro/cache/bench/
#
# Why sharded: the whole Table 2 reproduction costs ~112 min per seed, above this
# campaign's one-hour cap on any single job. Each shard here is roughly half an hour.
# Sharding changes where the work runs, not what is computed -- see repro/src/bench_shard.py.
set -eo pipefail

SHA="$(git rev-parse HEAD)"
RAW="https://raw.githubusercontent.com/MachineLearning-Nerd/icml26-repro-3WPDFjZ1UT-care-confounder-aware-aggregation-for-reliable-llm-evaluation/${SHA}"
SEEDS=(2024 2025 2026 2027 2028)
DATASETS=(civilcomments pku_better)
IMAGE="ghcr.io/astral-sh/uv:python3.11-bookworm"
IDFILE="${IDFILE:-shard_ids.txt}"

shard_cmd() {   # $* = arguments to bench_shard.py
  cat <<EOS
set -eo pipefail
apt-get update -qq && apt-get install -y -qq git
curl -fsSL ${RAW}/repro/orx/run_hf_job.sh -o /tmp/boot.sh
export CARE_SHARD_ARGS="$*"
BRANCH=main CARE_ENTRY="repro/src/bench_shard.py \$CARE_SHARD_ARGS" bash /tmp/boot.sh
EOS
}

launch() {
  : > "$IDFILE"
  submit() {  # $1 = label, rest = shard args
    local label="$1"; shift
    local id
    id="$(hf jobs run --flavor cpu-upgrade --timeout 1h -e CARE_HF_FLAVOR=cpu-upgrade \
            --detach "$IMAGE" bash -c "$(shard_cmd "$@")" 2>&1 | grep -oE '^id=[a-z0-9]+' | cut -d= -f2)"
    [ -n "$id" ] || { echo "FAILED to submit $label" >&2; return 1; }
    hf jobs labels "$id" --name "care-$label" >/dev/null 2>&1 || true
    printf '%s\t%s\t%s\n' "$id" "$label" "$*" >> "$IDFILE"
    echo "submitted $label -> $id"
  }

  for s in "${SEEDS[@]}"; do
    submit "t1-$s" t1 "$s"
  done
  for ds in "${DATASETS[@]}"; do
    for s in "${SEEDS[@]}"; do
      for part in main baselines; do
        submit "t2-$ds-$s-$part" t2 "$ds" "$s" "$part"
      done
    done
  done
  echo "shard ids in $IDFILE (timeout 1h each, so none can exceed the cap)"
}

collect() {
  local dest="${1:-repro/cache/bench}"
  mkdir -p "$dest"
  local ok=0 bad=0
  while IFS=$'\t' read -r id label _; do
    [ -n "$id" ] || continue
    if hf jobs logs "DineshAI/$id" 2>/dev/null \
       | awk '/===CARE_SHARD_BEGIN===/{f=1;next} /===CARE_SHARD_END===/{f=0} f' \
       > "$dest/$label.json" && [ -s "$dest/$label.json" ]; then
      python3 - "$dest/$label.json" "$id" "$SHA" <<'PY'
import json, sys
p, job, sha = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(p))
d["hf_job_id"], d["git_sha"] = job, sha
json.dump(d, open(p, "w"), indent=2)
PY
      ok=$((ok+1))
    else
      rm -f "$dest/$label.json"; bad=$((bad+1)); echo "no result yet: $label ($id)"
    fi
  done < "$IDFILE"
  echo "collected $ok shards into $dest; $bad still missing"
}

case "${1:-}" in
  launch)  launch ;;
  collect) shift; collect "$@" ;;
  *) echo "usage: $0 launch | collect [dest]"; exit 2 ;;
esac
