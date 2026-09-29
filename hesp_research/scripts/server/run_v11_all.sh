#!/bin/bash
# v1.1 on the RTX PRO 6000 server (vLLM 0.30.0, the v0.9/v1.0 serving stack; prefix caching ON as there).
# For each model: serve it with vLLM on 127.0.0.1 only, run parts e2 (sec, sigma) and e4, plus part f and
# the replay diagnosis for the two small models; audit and ARCHIVE every run directory, stop the server.
# Serving fault rule (PROTOCOL v1.1): if the server log shows "Failed to advance FSM" during a study, the
# study directory is moved to results/_aborted_fsm/, the server is restarted, and the study is rerun from
# scratch (at most 3 attempts). Qwen2.5-72B (primary endpoint PE1) runs first. Usage:
#   nohup scripts/server/run_v11_all.sh [MODEL_KEY ...] > logs/v11_all.log 2>&1 &
set -uo pipefail
ROOT=${HESP_ROOT:-/root/autodl-tmp/hesp}
CODE=$ROOT/HESP/hesp_research
PORT=${PORT:-8000}
WORKERS=${WORKERS:-32}
. "$ROOT/venv/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
cd "$CODE"
mkdir -p "$ROOT/logs" results results/_aborted_fsm

declare -A DIR=([qwen7b]=Qwen2.5-7B-Instruct [qwen32b]=Qwen2.5-32B-Instruct-AWQ [qwen72b]=Qwen2.5-72B-Instruct-AWQ
                [llama8b]=Llama-3.1-8B-Instruct [llama70b]=Meta-Llama-3.1-70B-Instruct-AWQ-INT4)
declare -A NAME=([qwen7b]=qwen2.5-7b-instruct [qwen32b]=qwen2.5-32b-instruct-awq [qwen72b]=qwen2.5-72b-instruct-awq
                 [llama8b]=llama-3.1-8b-instruct [llama70b]=llama-3.1-70b-instruct-awq)
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

serve() {  # $1 = key; appends to the model's vLLM log so that restarts keep the full record
  echo "=== $(date -Is) serve $1" >> "$ROOT/logs/vllm_v11_$1.log"
  vllm serve "$ROOT/models/${DIR[$1]}" --served-model-name "${NAME[$1]}" \
    --host 127.0.0.1 --port "$PORT" --max-model-len 8192 --gpu-memory-utilization 0.90 \
    --enable-prefix-caching --max-num-seqs 64 --seed 0 >> "$ROOT/logs/vllm_v11_$1.log" 2>&1 &
  VLLM_PID=$!
  for _ in $(seq 1 360); do
    curl -sf "http://127.0.0.1:$PORT/v1/models" > /dev/null && return 0
    kill -0 $VLLM_PID 2> /dev/null || { echo "vLLM exited early; see logs/vllm_v11_$1.log"; return 1; }
    sleep 5
  done
  echo "vLLM did not become ready"; return 1
}

restart() {  # $1 = key
  kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
  gpu_free
  serve "$1"
}

log_lines() { wc -l < "$ROOT/logs/vllm_v11_$1.log"; }
fsm_errors_since() { tail -n +"$(( $2 + 1 ))" "$ROOT/logs/vllm_v11_$1.log" | grep -c "$FSM_ERR"; }

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
  local out="results/v11${2}_${3}_$1" attempt start n
  for attempt in 1 2 3; do
    start=$(log_lines "$1")
    python -u scripts/run_v11_study.py --part "$2" --family "$3" --output "$out" --model "${NAME[$1]}" \
      --base-url "http://127.0.0.1:$PORT/v1" --workers "$WORKERS" --resume >> "$ROOT/logs/study_v11${2}_${3}_$1.log" 2>&1
    echo "study $2/$3 exit $? for $1 (attempt $attempt)"
    n=$(fsm_errors_since "$1" "$start")
    [ "$n" -eq 0 ] && break
    echo "SERVING FAULT: $n FSM errors during $2/$3 for $1; discarding the study and restarting vLLM"
    mv "$out" "results/_aborted_fsm/$(basename "$out")_attempt$attempt"
    restart "$1" || return 1
  done
  audit_archive "$out"
}

replay() {  # $1 = key
  local attempt start n out="results/v11f_replay_$1.json"
  for attempt in 1 2 3; do
    start=$(log_lines "$1")
    python -u scripts/v11_replay.py --archive "results/v09_$1/runs_archive.tar.gz" --model "${NAME[$1]}" \
      --model-dir "$ROOT/models/${DIR[$1]}" --base-url "http://127.0.0.1:$PORT/v1" \
      --out "$out" >> "$ROOT/logs/replay_v11_$1.log" 2>&1
    echo "replay exit $? for $1 (attempt $attempt)"
    n=$(fsm_errors_since "$1" "$start")
    [ "$n" -eq 0 ] && break
    echo "SERVING FAULT: $n FSM errors during the replay for $1; restarting vLLM"
    mv "$out" "results/_aborted_fsm/$(basename "$out" .json)_attempt$attempt.json"
    restart "$1" || return 1
  done
}

gpu_free
for key in ${@:-qwen72b qwen32b llama70b}; do
  echo "=== $(date -Is) model $key"
  serve "$key" || { gpu_free; continue; }
  study "$key" e2 sec
  study "$key" e2 sigma
  study "$key" e4 sec
  if [ "$key" = qwen7b ] || [ "$key" = llama8b ]; then
    study "$key" f sec
    replay "$key"
  fi
  kill $VLLM_PID 2> /dev/null; wait $VLLM_PID 2> /dev/null
  gpu_free
done
echo "=== $(date -Is) ALL_DONE"
