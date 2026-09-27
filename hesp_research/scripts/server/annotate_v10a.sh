#!/bin/bash
# v1.0 part A, steps 2-3 on the RTX PRO 6000D: annotate the sampled Sigma rules with phi-4 (bf16,
# temperature 0, JSON-schema constrained), then count the per-rule tables. Usage:
#   nohup scripts/server/annotate_v10a.sh > logs/annotate_v10a.log 2>&1 &
set -uo pipefail
ROOT=${HESP_ROOT:-/root/autodl-tmp/hesp}
CODE=$ROOT/HESP/hesp_research
PORT=${PORT:-8000}
. "$ROOT/venv/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
[ -f "$ROOT/models/phi-4/.fetch_complete" ] || { echo "phi-4 weights missing"; exit 1; }
vllm serve "$ROOT/models/phi-4" --served-model-name phi-4 --host 127.0.0.1 --port "$PORT"   --max-model-len 8192 --gpu-memory-utilization 0.90 --seed 0 > "$ROOT/logs/vllm_phi4.log" 2>&1 &
VLLM_PID=$!
for _ in $(seq 1 360); do
  curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && break
  kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_phi4.log"; exit 1; }
  sleep 5
done
python -u scripts/v10a_annotate.py --pool results/v10a/rule_pool.json --out results/v10a --model phi-4   --base-url "http://127.0.0.1:$PORT/v1"
echo "annotate exit $?"
kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
for pid in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2> /dev/null); do kill "$pid" 2> /dev/null; done
python -u scripts/v10a_tables.py --specs results/v10a/specs --k 20 --out results/v10a/tables
echo "=== $(date -Is) ANNOTATE_DONE"
