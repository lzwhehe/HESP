#!/bin/bash
# v1.4 on the H100 vGPU (vLLM 0.11.0, prefix caching off, serving-fault rule as in v1.1): the served model deciding
# alone on structured observations and on raw logs (scripts/run_v14_study.py).
# Only the vLLM process this script starts is ever stopped; if any other process holds the GPU, nothing starts.
# Usage: nohup scripts/server/run_v14_h100.sh > ~/logs/v14.log 2>&1 &
#        STRIDE=8 scripts/server/run_v14_h100.sh smoke     (disclosed smoke test, results/v14_smoke_*)
set -uo pipefail
ROOT=${HESP_ROOT:-$HOME}
CODE=$HOME/hesp14/hesp_research
PORT=${PORT:-8000}
WORKERS=${WORKERS:-16}
. "$HOME/hesp-venv/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
mkdir -p "$ROOT/logs" results results/_aborted_fsm

declare -A DIR=([qwen7b]=Qwen2.5-7B-Instruct [llama8b]=Llama-3.1-8B-Instruct)
declare -A NAME=([qwen7b]=qwen2.5-7b-instruct [llama8b]=llama-3.1-8b-instruct)
FSM_ERR="Failed to advance FSM"
VLLM_PID=""

gpu_idle() {  # true if no process holds the GPU
  [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null)" ]
}

stop_own() {  # stop only the vLLM this script started, then wait for its memory to be released
  [ -n "$VLLM_PID" ] || return 0
  kill "$VLLM_PID" 2> /dev/null; wait "$VLLM_PID" 2> /dev/null; VLLM_PID=""
  for _ in $(seq 1 60); do gpu_idle && return 0; sleep 5; done
  echo "GPU still busy after stopping our vLLM"
}

serve() {
  gpu_idle || { echo "GPU busy with another process; not starting"; return 1; }
  echo "=== $(date -Is) serve $1" >> "$ROOT/logs/vllm_v14_$1.log"
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.92 \
    --no-enable-prefix-caching --max-num-seqs 16 --seed 0 >> "$ROOT/logs/vllm_v14_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 360); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_v14_$1.log"; VLLM_PID=""; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; stop_own; return 1
}

log_lines() { wc -l < "$ROOT/logs/vllm_v14_$1.log"; }
fsm_errors_since() { tail -n +"$(( $2 + 1 ))" "$ROOT/logs/vllm_v14_$1.log" | grep -c "$FSM_ERR"; }

archive() {
  ( cd "$1" && tar -czf runs_archive.tar.gz run0* ) && sha256sum "$1/runs_archive.tar.gz" | tee "$1/runs_archive.sha256"
}

v14() {  # $1 = key, $2 = mode (full|smoke)
  local out attempt start n extra=""
  if [ "$2" = smoke ]; then out="results/v14_smoke_$1"; extra="--task-stride ${STRIDE:-8}"; else out="results/v14_alone_$1"; fi
  for attempt in 1 2 3; do
    start=$(log_lines "$1")
    python -u scripts/run_v14_study.py $extra --output "$out" --model "${NAME[$1]}" \
      --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" --resume >> "$ROOT/logs/study_v14_$1.log" 2>&1
    echo "v1.4 exit $? for $1 (attempt $attempt)"
    n=$(fsm_errors_since "$1" "$start")
    [ "$n" -eq 0 ] && break
    echo "SERVING FAULT: $n FSM errors for $1; discarding and restarting vLLM"
    mv "$out" "results/_aborted_fsm/$(basename "$out")_attempt$attempt"
    stop_own; serve "$1" || return 1
  done
  archive "$out"
}

trap stop_own EXIT
MODE=${1:-full}
for key in ${MODELS:-qwen7b llama8b}; do
  echo "=== $(date -Is) $MODE model $key"
  serve "$key" || continue
  v14 "$key" "$MODE"
  stop_own
done
echo "=== $(date -Is) ALL_DONE $MODE"
