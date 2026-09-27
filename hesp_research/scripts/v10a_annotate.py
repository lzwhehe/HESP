"""v1.0 part A, step 2: annotate the outcome structure of the sampled Sigma rules (PROTOCOL.md v1.0).

For each rule in the pool order, one call to the annotator model (not one of the planners),
temperature 0, constrained by a JSON schema to the fixed probe vocabulary: for every candidate cause
and every probe, the one outcome an analyst would observe if that cause were true. A rule whose
annotation fails ``validate_spec`` (a cause without a unique outcome, or two identical causes) is
recorded and replaced by the next rule in the pool order, until 12 rules are accepted. Every prompt
and raw reply is kept. Specs are never edited after this step.

    python scripts/v10a_annotate.py --pool results/v10a/rule_pool.json --out results/v10a \
        --model phi-4 --base-url http://127.0.0.1:8000/v1
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.llm import OpenAICompatClient
from hesp.sigmaapp import MAX_BENIGN, PROBES, PROBE_IDS, VOCAB, validate_spec

N_RULES = 12
SYSTEM = ("You are an experienced security operations analyst. You describe, for a detection rule, what an "
          "investigation would find under each possible explanation of an alert. Answer with JSON only.")


def causes_of(rule):
    causes = {"attack": (f"The malicious activity the rule is written to detect: {rule['title']} "
                         f"(MITRE ATT&CK {', '.join(rule['techniques'])}).")}
    for i, fp in enumerate(rule["falsepositives"][:MAX_BENIGN], 1):
        causes[f"benign_{i}"] = f"Benign: {fp}"
    return causes


def prompt(rule, causes):
    lines = [f"Detection rule: {rule['title']}", f"Description: {rule['description']}",
             f"Log source: {json.dumps(rule['logsource'], sort_keys=True)}", "",
             "Candidate explanations of an alert from this rule:"]
    lines += [f"- {cid}: {text}" for cid, text in causes.items()]
    lines += ["", "Investigation probes and their possible findings:"]
    for p in PROBES:
        lines.append(f"- {p['id']}: {p['description']} Findings: " +
                     "; ".join(f"{o} = {note.split(', ', 1)[1]}" for o, note in p["outcome_notes"].items()))
    lines += ["", "For EACH explanation, choose for EACH probe the single finding an analyst would most likely "
              "observe if that explanation were the true one. Be realistic and specific to this rule; different "
              "explanations should differ wherever they really would.",
              'Reply as {"<explanation id>": {"<probe id>": "<finding>", ...}, ...}.']
    return "\n".join(lines)


def schema(causes):
    row = {"type": "object", "additionalProperties": False, "required": PROBE_IDS,
           "properties": {a: {"type": "string", "enum": VOCAB[a]} for a in PROBE_IDS}}
    return {"type": "object", "additionalProperties": False, "required": list(causes),
            "properties": {c: row for c in causes}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    args = ap.parse_args()
    pool = json.loads(Path(args.pool).read_text(encoding="utf-8"))
    client = OpenAICompatClient(args.model, args.base_url)
    out = Path(args.out)
    (out / "specs").mkdir(parents=True, exist_ok=False)
    log, accepted = [], []
    for position, rule in enumerate(pool["order"]):
        if len(accepted) == N_RULES:
            break
        causes = causes_of(rule)
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt(rule, causes)}]
        reply = client.chat(messages, seed=0, temperature=0.0, fmt=schema(causes), num_predict=3000)
        try:
            outcomes = json.loads(reply["content"])
        except ValueError:
            outcomes = None
        slug = re.sub(r"[^a-z0-9]+", "-", rule["title"].lower()).strip("-")[:48] + "-" + rule["rule_id"][:8]
        spec = {"rule_id": rule["rule_id"], "slug": slug, "path": rule["path"], "title": rule["title"],
                "description": rule["description"], "technique": rule["techniques"], "logsource": rule["logsource"],
                "causes": causes, "outcomes": outcomes}
        errors = ["unparseable annotation"] if not isinstance(outcomes, dict) else validate_spec(spec)
        log.append({"position": position, "rule_id": rule["rule_id"], "title": rule["title"],
                    "accepted": not errors, "errors": errors, "messages": messages, "raw_reply": reply["content"],
                    "finish_reason": reply["finish_reason"], "usage": reply["usage"]})
        if not errors:
            path = out / "specs" / f"{len(accepted):02d}_{slug}.json"
            path.write_bytes((json.dumps(spec, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            accepted.append({"file": path.name, "slug": slug, "rule_id": rule["rule_id"],
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        print(f"[{position}] {'ok ' if not errors else 'REJ'} {rule['title']}" + (f"  {errors}" if errors else ""),
              flush=True)
    index = {"schema": "hesp.v10a.specs.v1", "annotator": client.info(), "temperature": 0.0,
             "sigma_commit": pool["sigma_commit"],
             "pool_sha256": hashlib.sha256(Path(args.pool).read_bytes()).hexdigest(),
             "accepted": accepted, "examined": len(log)}
    (out / "annotation_log.json").write_bytes((json.dumps(log, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    (out / "specs" / "index.json").write_bytes((json.dumps(index, indent=2) + "\n").encode("utf-8"))
    print(f"accepted {len(accepted)} of {len(log)} examined")


if __name__ == "__main__":
    main()
