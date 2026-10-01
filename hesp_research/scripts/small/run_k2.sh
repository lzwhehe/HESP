#!/bin/bash
# K2-capability runs on the GPU host (docs/PROTOCOL_SMALL.md, section K2-能力). Resumable: k1_run.py skips done items.
set -x
cd ~/k0
serve() {  # served-name model-path max-model-len
  (nohup ~/hesp-venv/bin/vllm serve "$2" --served-model-name "$1" --host 127.0.0.1 --port 8000 --quantization fp8 \
      --max-model-len "$3" --gpu-memory-utilization 0.85 --max-num-seqs 16 --seed 0 > "k2/vllm_$1.log" 2>&1 < /dev/null &)
  until grep -q "Application startup complete\|Engine core initialization failed" "k2/vllm_$1.log"; do sleep 5; done
  grep -q "Application startup complete" "k2/vllm_$1.log" || { echo "SERVEFAIL $1"; return 1; }
}
stopserve() {
  pids=$(ps -eo pid,args | grep "[v]llm serve" | awk '{print $1}')
  [ -n "$pids" ] && kill $pids
  while ps -eo args | grep -q "[v]llm serve"; do sleep 2; done
  sleep 10
}
python3 k1_run.py --cond C4 --questions k2_questions.json --db ~/k0/db --out k2/C4.jsonl
for spec in "qwen2.5-7b-instruct /home/ubuntu/models/Qwen2.5-7B-Instruct 32768" \
            "llama-3.1-8b-instruct /home/ubuntu/models/Llama-3.1-8B-Instruct 32768" \
            "phi-4 /home/ubuntu/models/phi-4 16384"; do
  set -- $spec
  if ! ps -eo args | grep -q "[v]llm serve.*--served-model-name $1 "; then
    stopserve
    serve "$1" "$2" "$3" || continue
  else  # already starting or running (resume): wait until ready
    until grep -q "Application startup complete" "k2/vllm_$1.log"; do sleep 5; done
  fi
  for c in C1 C2 C3; do
    python3 k1_run.py --cond "$c" --questions k2_questions.json --db ~/k0/db --out "k2/${1}_$c.jsonl" --model "$1" --workers 12
  done
done
stopserve
echo ALLDONE
