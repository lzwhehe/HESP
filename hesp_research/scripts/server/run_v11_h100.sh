#!/bin/bash
# v1.1 on the H100 vGPU (20 GB; vLLM 0.11.0; small models only). Same procedure as run_v11_all.sh.
# --enforce-eager: the machine lacks Python headers, so torch.compile cannot build its kernels; eager
# execution changes speed, not the sampling procedure. For each model: serve it with
# vLLM on 127.0.0.1 only, run parts e2 (sec, sigma) and e4, plus part f and the replay diagnosis for
# the two small models; audit and ARCHIVE every run directory, then stop the server. Usage:
#   nohup scripts/server/run_v11_h100.sh [MODEL_KEY ...] > logs/v11_all.log 2>&1 &
set -uo pipefail
ROOT=${HESP_ROOT:-$HOME}
CODE=$HOME/hesp11/hesp_research
PORT=${PORT:-8000}
WORKERS=${WORKERS:-16}
. "$HOME/hesp-venv/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
mkdir -p "$ROOT/logs" results

declare -A DIR=([qwen7b]=Qwen2.5-7B-Instruct [qwen32b]=Qwen2.5-32B-Instruct-AWQ [qwen72b]=Qwen2.5-72B-Instruct-AWQ
                [llama8b]=Llama-3.1-8B-Instruct [llama70b]=Meta-Llama-3.1-70B-Instruct-AWQ-INT4)
declare -A NAME=([qwen7b]=qwen2.5-7b-instruct [qwen32b]=qwen2.5-32b-instruct-awq [qwen72b]=qwen2.5-72b-instruct-awq
                 [llama8b]=llama-3.1-8b-instruct [llama70b]=llama-3.1-70b-instruct-awq)

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
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.92 \
    --enable-prefix-caching --max-num-seqs 16 --seed 0 --enforce-eager > "$ROOT/logs/vllm_v11_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 360); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_v11_$1.log"; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; return 1
}

audit_archive() {  # $1 = results dir
  local d=$1
  python -u -c "
import json, sys; sys.path.insert(0, '.')
from pathlib import Path
from hesp.audit import audit_run
d = Path('$d')
rows = [json.loads(l) for l in open(d / 'outcomes.jsonl', encoding='utf-8')]
bad = [r['run_directory'] for r in rows if not audit_run(d / r['run_directory'])['passed']]
print(f'audit $d: {len(rows) - len(bad)}/{len(rows)} passed; source hashes', sorted({r['source_sha256'][:8] for r in rows}))
for b in bad: print('  FAILED', b)
"
  ( cd "$d" && shopt -s nullglob && runs=(run0* _aborted_*) && tar -czf runs_archive.tar.gz "${runs[@]}" ) \
    && sha256sum "$d/runs_archive.tar.gz" | tee "$d/runs_archive.sha256"
}

study() {  # $1 = key, $2 = part, $3 = family
  local out="results/v11${2}_${3}_$1"
  python -u scripts/run_v11_study.py --part "$2" --family "$3" --output "$out" --model "${NAME[$1]}" \
    --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" --resume > "$ROOT/logs/study_v11${2}_${3}_$1.log" 2>&1
  echo "study $2/$3 exit $? for $1"
  audit_archive "$out"
}

gpu_free
for key in ${@:-qwen7b llama8b}; do
  echo "=== $(date -Is) model $key"
  serve "$key" || { gpu_free; continue; }
  study "$key" e2 sec
  study "$key" e2 sigma
  study "$key" e4 sec
  if [ "$key" = qwen7b ] || [ "$key" = llama8b ]; then
    study "$key" f sec
    python -u scripts/v11_replay.py --archive "results/v09_$key/runs_archive.tar.gz" --model "${NAME[$key]}" \
      --model-dir "$ROOT/models/${DIR[$key]}" --base-url "http://127.0.0.1:$PORT/v1" \
      --out "results/v11f_replay_$key.json" > "$ROOT/logs/replay_v11_$key.log" 2>&1
    echo "replay exit $? for $key"
  fi
  kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
  gpu_free
done
echo "=== $(date -Is) ALL_DONE"
