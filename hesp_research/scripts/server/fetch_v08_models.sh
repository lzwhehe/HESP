#!/bin/bash
# Download the two Llama 3.1 checkpoints used by v0.8 into $ROOT/models (non-gated mirrors;
# use is governed by the Llama 3.1 Community License). Set HF_ENDPOINT to a mirror if the
# server cannot reach huggingface.co directly. Usage:
#   nohup scripts/server/fetch_v08_models.sh > logs/fetch_v08.log 2>&1 &
# Run it alongside run_v08_all.sh: the Qwen models (already on disk) go first, so the download
# overlaps with GPU work; each finished model gets a .fetch_complete marker.
set -euo pipefail
ROOT=${HESP_ROOT:-/root/autodl-tmp/hesp}
. "$ROOT/venv/bin/activate"
export HF_HOME=${HF_HOME:-$ROOT/hf_cache}
# The provider's no-GPU mode caps the container at 2 GB of RAM; the Xet backend's parallel
# buffers got the downloader killed there. Plain HTTP streaming with few workers stays small.
export HF_HUB_DISABLE_XET=1
WORKERS=${FETCH_WORKERS:-2}
mkdir -p "$ROOT/models"
fetch() {  # $1 = repo id, $2 = local directory name
  echo "=== $(date -Is) $1"
  if command -v hf > /dev/null; then
    hf download "$1" --local-dir "$ROOT/models/$2" --exclude "original/*" --exclude "*.pth" --max-workers "$WORKERS"
  else
    huggingface-cli download "$1" --local-dir "$ROOT/models/$2" --exclude "original/*" "*.pth" --max-workers "$WORKERS"
  fi
  du -sh "$ROOT/models/$2"
  touch "$ROOT/models/$2/.fetch_complete"   # run_v08_all.sh waits for this before serving
}
fetch unsloth/Llama-3.1-8B-Instruct Llama-3.1-8B-Instruct
fetch hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4 Meta-Llama-3.1-70B-Instruct-AWQ-INT4
echo "=== $(date -Is) FETCH_DONE"
