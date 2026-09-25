#!/bin/bash
# Download the two Llama 3.1 checkpoints used by v0.8 into $ROOT/models (non-gated mirrors;
# use is governed by the Llama 3.1 Community License). Set HF_ENDPOINT to a mirror if the
# server cannot reach huggingface.co directly. Usage:
#   nohup scripts/server/fetch_v08_models.sh > logs/fetch_v08.log 2>&1 &
set -euo pipefail
ROOT=${HESP_ROOT:-/root/autodl-tmp/hesp}
. "$ROOT/venv/bin/activate"
export HF_HOME=${HF_HOME:-$ROOT/hf_cache}
mkdir -p "$ROOT/models"
fetch() {  # $1 = repo id, $2 = local directory name
  echo "=== $(date -Is) $1"
  if command -v hf > /dev/null; then
    hf download "$1" --local-dir "$ROOT/models/$2" --exclude "original/*" "*.pth"
  else
    huggingface-cli download "$1" --local-dir "$ROOT/models/$2" --exclude "original/*" "*.pth"
  fi
  du -sh "$ROOT/models/$2"
}
fetch unsloth/Llama-3.1-8B-Instruct Llama-3.1-8B-Instruct
fetch hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4 Meta-Llama-3.1-70B-Instruct-AWQ-INT4
echo "=== $(date -Is) FETCH_DONE"
