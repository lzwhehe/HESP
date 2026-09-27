#!/bin/bash
# v0.8 on a single GPU server: for each model, serve it with vLLM on 127.0.0.1 only, run the
# pre-registered study (resumable), audit and ARCHIVE the per-episode journals, then stop the
# server and wait until the GPU is really free. Usage:
#   nohup scripts/server/run_v08_all.sh [MODEL_KEY ...] > logs/v08_all.log 2>&1 &
# MODEL_KEY in: qwen7b qwen32b qwen72b llama8b llama70b (default: all five, as pre-registered).
# Start scripts/server/fetch_v08_models.sh alongside; Llama runs wait for its completion markers.
set -uo pipefail
ROOT=${HESP_ROOT:-/root/autodl-tmp/hesp}
CODE=$ROOT/HESP/hesp_research
PORT=${PORT:-8000}
WORKERS=${WORKERS:-32}
REPEATS=${REPEATS:-3}
. "$ROOT/venv/bin/activate"
# System nvcc is 12.8; FlashInfer JIT needs >= 12.9 for sm_120, so use the PyTorch sampler.
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
mkdir -p "$ROOT/logs" results

declare -A DIR=([qwen7b]=Qwen2.5-7B-Instruct [qwen32b]=Qwen2.5-32B-Instruct-AWQ [qwen72b]=Qwen2.5-72B-Instruct-AWQ
                [llama8b]=Llama-3.1-8B-Instruct [llama70b]=Meta-Llama-3.1-70B-Instruct-AWQ-INT4)
declare -A NAME=([qwen7b]=qwen2.5-7b-instruct [qwen32b]=qwen2.5-32b-instruct-awq [qwen72b]=qwen2.5-72b-instruct-awq
                 [llama8b]=llama-3.1-8b-instruct [llama70b]=llama-3.1-70b-instruct-awq)

gpu_free() {  # kill every compute process on the GPU and wait until memory is released
  # Killing only the launcher PID leaves vLLM's EngineCore child holding the GPU (v0.5). Never use
  # `pkill -f "vllm serve"`: it matches the invoking SSH shell's own command line and kills it.
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null); do
    kill "$pid" 2> /dev/null
  done
  for _ in $(seq 1 60); do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    [ "${used:-99999}" -lt 2000 ] && return 0
    sleep 5
  done
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null); do
    kill -9 "$pid" 2> /dev/null
  done
  sleep 10
}

wait_weights() {  # $1 = model key. Llama weights may still be downloading (fetch_v08_models.sh).
  local d="$ROOT/models/${DIR[$1]}"
  case "$1" in llama*) ;; *) [ -d "$d" ]; return;; esac
  for _ in $(seq 1 720); do   # up to 2 h
    [ -f "$d/.fetch_complete" ] && return 0
    sleep 10
  done
  echo "weights not complete after 2 h: $d"; return 1
}

serve() {  # $1 = model key
  wait_weights "$1" || { echo "missing weights: $ROOT/models/${DIR[$1]}"; return 1; }
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.90 \
    --enable-prefix-caching --max-num-seqs 64 --seed 0 \
    > "$ROOT/logs/vllm_v08_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 360); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_v08_$1.log"; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; return 1
}

archive() {  # $1 = results dir. Pre-registered rule (errata E-2): archive before releasing compute.
  local d=$1
  ( cd "$d" || exit 1
    shopt -s nullglob
    runs=(run0* _aborted_*)   # interrupted attempts are kept for the audit trail
    [ ${#runs[@]} -gt 0 ] || { echo "no run directories in $d"; exit 1; }
    tar -czf runs_archive.tar.gz "${runs[@]}" ) \
    && sha256sum "$d/runs_archive.tar.gz" | tee "$d/runs_archive.sha256"
}

gpu_free
for key in ${@:-qwen7b qwen32b qwen72b llama8b llama70b}; do   # Qwen first: its weights are on disk
  echo "=== $(date -Is) model $key"
  serve "$key" || { gpu_free; continue; }
  python -u scripts/run_v08_study.py --output "results/v08_$key" --model "${NAME[$key]}" \
    --backend vllm --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" \
    --repeats "$REPEATS" --resume \
    > "$ROOT/logs/study_v08_$key.log" 2>&1
  echo "study exit $? for $key"
  python -u -c "
import json, sys; sys.path.insert(0, '.')
from pathlib import Path
from hesp.audit import audit_run
d = Path('results/v08_$key')
rows = [json.loads(l) for l in open(d / 'outcomes.jsonl', encoding='utf-8')]
bad = [r['run_directory'] for r in rows if not audit_run(d / r['run_directory'])['passed']]
hashes = sorted({r['source_sha256'][:8] for r in rows})
print(f'audit: {len(rows) - len(bad)}/{len(rows)} passed; source hashes {hashes}')
for b in bad: print('  FAILED', b)
" 2>&1 | tee "$ROOT/logs/audit_v08_$key.log"
  archive "results/v08_$key"
  kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
  gpu_free
done
echo "=== $(date -Is) ALL_DONE"
