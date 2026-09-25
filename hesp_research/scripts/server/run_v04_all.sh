#!/bin/bash
# v0.4 on a single GPU server: for each model, serve it with vLLM on 127.0.0.1 only,
# run the paired study (resumable), then stop the server. Usage:
#   nohup scripts/server/run_v04_all.sh [MODEL_KEY ...] > logs/v04_all.log 2>&1 &
# MODEL_KEY in: 7b 32b 72b (default: all three, smallest first).
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

declare -A DIR=([7b]=Qwen2.5-7B-Instruct [32b]=Qwen2.5-32B-Instruct-AWQ [72b]=Qwen2.5-72B-Instruct-AWQ)
declare -A NAME=([7b]=qwen2.5-7b-instruct [32b]=qwen2.5-32b-instruct-awq [72b]=qwen2.5-72b-instruct-awq)

serve() {  # $1 = model key
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.90 \
    --enable-prefix-caching --max-num-seqs 64 --seed 0 \
    > "$ROOT/logs/vllm_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 240); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_$1.log"; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; return 1
}

for key in "${@:-7b 32b 72b}"; do
  for k in $key; do
    echo "=== $(date -Is) model $k"
    [ -f "$ROOT/logs/setup.log" ] && until grep -q "^Qwen/${DIR[$k]} " "$ROOT/logs/setup.log"; do sleep 30; done
    serve "$k" || { kill $VLLM_PID 2> /dev/null; continue; }
    python -u scripts/run_v04_study.py --output "results/v04_$k" --model "${NAME[$k]}" \
      --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" --repeats "$REPEATS" --resume \
      > "$ROOT/logs/study_$k.log" 2>&1
    echo "study exit $? for $k"
    kill $VLLM_PID; wait $VLLM_PID 2> /dev/null
  done
done
echo "=== $(date -Is) ALL_DONE"
