"""v1.1 part F, replay diagnosis of "never concludes" (PROTOCOL.md v1.1).

Selection rule (fixed before any call): from the v0.9 archived journals of the given model, every
planner request in the memory_only and hesp_eigc_blind arms in which the leading hypothesis has a
current score of at least 0.99 or no legal probe is left; sorted by (run directory, sequence number);
the first 60 are used. Each request is re-rendered exactly as the model saw it and sent once per
system-prompt variant (v1, finish_example, explicit_rule) with temperature 0.2 and a fixed seed.
Recorded: the decision kind, JSON validity, the server's finish_reason, and completion tokens.
The script also records the model directory's chat template and generation config hashes.

    python scripts/v11_replay.py --archive results/v09_llama8b/runs_archive.tar.gz \
        --model llama-3.1-8b-instruct --model-dir /root/autodl-tmp/hesp/models/Llama-3.1-8B-Instruct \
        --out results/v11f_replay_llama8b.json
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.llm import PROMPT_VARIANTS, SYSTEM, OpenAICompatClient, render_request

N = 60


def select(archive):
    picked = []
    with tarfile.open(archive) as tar:
        names = sorted(n for n in tar.getnames() if n.endswith("/events.jsonl")
                       and ("_memory_only/" in n or "_hesp_eigc_blind/" in n))
        for name in names:
            for line in tar.extractfile(name).read().decode("utf-8").splitlines():
                e = json.loads(line)
                if e["kind"] != "planner_request":
                    continue
                req = e["request"]
                top = max(h["score"] for h in req["investigation"]["hypotheses"])
                if top >= 0.99 or req.get("no_legal_probe_left"):
                    picked.append((name, e["seq"], req))
    return picked[:N]


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    client = OpenAICompatClient(args.model, args.base_url)
    requests = select(args.archive)
    tok_cfg = Path(args.model_dir) / "tokenizer_config.json"
    template = json.loads(tok_cfg.read_text(encoding="utf-8")).get("chat_template") if tok_cfg.exists() else None
    rows = []
    for i, (name, seq, req) in enumerate(requests):
        for variant in PROMPT_VARIANTS:
            messages = [{"role": "system", "content": SYSTEM + PROMPT_VARIANTS[variant]},
                        {"role": "user", "content": render_request(req)}]
            reply = client.chat(messages, seed=1000 + i, temperature=0.2, num_predict=400)
            try:
                decision = json.loads(reply["content"])
                kind = decision.get("kind") if isinstance(decision, dict) else None
            except ValueError:
                kind = None
            rows.append({"run": name.split("/")[0], "seq": seq, "variant": variant, "kind": kind,
                         "valid_json": kind is not None, "finish_reason": reply["finish_reason"],
                         "completion_tokens": (reply["usage"] or {}).get("output_tokens"),
                         "top_score": max(h["score"] for h in req["investigation"]["hypotheses"]),
                         "no_legal_probe_left": bool(req.get("no_legal_probe_left"))})
    summary = {}
    for variant in PROMPT_VARIANTS:
        rs = [r for r in rows if r["variant"] == variant]
        summary[variant] = {"requests": len(rs), **{k: sum(r["kind"] == k for r in rs) for k in ("action", "finish", "stop")},
                            "invalid": sum(not r["valid_json"] for r in rs),
                            "truncated": sum(r["finish_reason"] == "length" for r in rs)}
    record = {"schema": "hesp.v11f.replay.v1", "model": client.info(), "selection": f"first {N}, rule in docstring",
              "archive_sha256": file_hash(args.archive),
              "chat_template_sha256": hashlib.sha256(template.encode()).hexdigest() if template else None,
              "chat_template_has_llama3_headers": bool(template and "<|start_header_id|>" in template),
              "generation_config_sha256": file_hash(Path(args.model_dir) / "generation_config.json"),
              "tokenizer_config_sha256": file_hash(tok_cfg), "summary": summary, "rows": rows}
    Path(args.out).write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
