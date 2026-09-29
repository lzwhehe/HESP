#!/bin/bash
# v1.3 on the H100 vGPU (vLLM 0.11.0, prefix caching off, serving-fault rule as in v1.1): the served model as the
# base reader under every reader policy and log condition (scripts/run_v13_study.py --reader llm).
# Usage: nohup scripts/server/run_v13_h100.sh > ~/logs/v13.log 2>&1 &
#        STRIDE=8 scripts/server/run_v13_h100.sh smoke     (disclosed smoke test, results/v13_smoke_*)
set -uo pipefail
ROOT=${HESP_ROOT:-$HOME}
CODE=$HOME/hesp13/hesp_research
PORT=${PORT:-8000}
WORKERS=${WORKERS:-16}
. "$HOME/hesp-venv/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
mkdir -p "$ROOT/logs" results results/_aborted_fsm

declare -A DIR=([qwen7b]=Qwen2.5-7B-Instruct [llama8b]=Llama-3.1-8B-Instruct)
declare -A NAME=([qwen7b]=qwen2.5-7b-instruct [llama8b]=llama-3.1-8b-instruct)
FSM_ERR="Failed to advance FSM"

gpu_free() {
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null); do kill "$pid" 2> /dev/null; done
  for _ in $(seq 1 60); do
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    [ "${used:-99999}" -lt 2000 ] && return 0
    sleep 5
  done
  for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null); do kill -9 "$pid" 2> /dev/null; done
  sleep 10
}

serve() {
  echo "=== $(date -Is) serve $1" >> "$ROOT/logs/vllm_v13_$1.log"
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.92 \
    --no-enable-prefix-caching --max-num-seqs 16 --seed 0 >> "$ROOT/logs/vllm_v13_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 360); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_v13_$1.log"; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; return 1
}

restart() { kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null; gpu_free; serve "$1"; }
log_lines() { wc -l < "$ROOT/logs/vllm_v13_$1.log"; }
fsm_errors_since() { tail -n +"$(( $2 + 1 ))" "$ROOT/logs/vllm_v13_$1.log" | grep -c "$FSM_ERR"; }

archive() {  # $1 = results dir (audits are recorded per episode in outcomes.jsonl)
  ( cd "$1" && tar -czf runs_archive.tar.gz run0* ) && sha256sum "$1/runs_archive.tar.gz" | tee "$1/runs_archive.sha256"
}

v13() {  # $1 = key, $2 = mode (full|smoke)
  local out attempt start n extra=""
  if [ "$2" = smoke ]; then out="results/v13_smoke_$1"; extra="--task-stride ${STRIDE:-8}"; else out="results/v13_llm_$1"; fi
  for attempt in 1 2 3; do
    start=$(log_lines "$1")
    python -u scripts/run_v13_study.py --reader llm $extra --output "$out" --model "${NAME[$1]}" \
      --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" --resume >> "$ROOT/logs/study_v13_$1.log" 2>&1
    echo "v1.3 exit $? for $1 (attempt $attempt)"
    n=$(fsm_errors_since "$1" "$start")
    [ "$n" -eq 0 ] && break
    echo "SERVING FAULT: $n FSM errors for $1; discarding and restarting vLLM"
    mv "$out" "results/_aborted_fsm/$(basename "$out")_attempt$attempt"
    restart "$1" || return 1
  done
  archive "$out"
}

gpu_free
MODE=${1:-full}
for key in ${MODELS:-qwen7b llama8b}; do
  echo "=== $(date -Is) $MODE model $key"
  serve "$key" || { gpu_free; continue; }
  v13 "$key" "$MODE"
  kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
  gpu_free
done
echo "=== $(date -Is) ALL_DONE $MODE"
