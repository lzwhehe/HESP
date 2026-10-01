"""Shortcut audit of the SIABench alert-triage subset (no LLM, no PCAP). Descriptive; see docs/PROTOCOL_AUDIT.md.

Each of the 35 alerts asks: given the IDS alert and its PCAP, is the alert a true or a false positive? The rules below
read only the `scenario` text, which the benchmark gives to the model (it embeds the raw Snort alert).
  majority  : answer "false positive" for every alert.
  attacker  : answer "true positive" iff the alert involves 172.16.0.1, the address through which the CIC-IDS2017
              attack network reaches the victim network (dataset documentation). Found after reading the data (post hoc).
Reported accuracies of models are copied from the SIABench paper (alert-triage table) into the output for comparison.

    python scripts/audit/siabench_shortcut.py --out results/audit/siabench.json
"""
import argparse
import glob
import json
import os
import re

ROOT = os.environ.get("SIABENCH_ROOT", r"E:\HESP\external\siabench")
ATTACKER = "172.16.0.1"
REPORTED = {"GPT-5": 0.971, "Claude-4.5-Sonnet": 0.8857, "DeepSeek-Reasoner": 0.857, "GPT-4o-mini": 0.514}


def label(answer):
    a = answer.lower()
    if "true" in a:
        return "true positive"
    if "false" in a:
        return "false positive"
    return a.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = []
    files = sorted(glob.glob(os.path.join(ROOT, "Alert_Triaging_Dataset", "alert_*.json")),
                   key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
    for f in files:
        d = json.load(open(f, encoding="utf-8"))["scenarios"]
        comp = d[1]["sia_components"]
        gold = label(comp["questions"][0]["answer"])
        text = comp["scenario"]
        ips = re.findall(r"\d+\.\d+\.\d+\.\d+", comp["alert"])
        rule = "true positive" if re.search(r"(?<![\d.])" + re.escape(ATTACKER) + r"(?![\d.])", text) else "false positive"
        rows.append({"alert": os.path.basename(f)[:-5], "gold": gold, "ips": ips, "attacker_rule": rule,
                     "attacker_correct": rule == gold, "majority_correct": gold == "false positive"})
    n = len(rows)
    summary = {"alerts": n, "true_positive": sum(r["gold"] == "true positive" for r in rows),
               "attacker_rule_correct": sum(r["attacker_correct"] for r in rows),
               "majority_correct": sum(r["majority_correct"] for r in rows),
               "reported_accuracy": REPORTED,
               "reported_source": "SIABench (arXiv:2603.06422), alert-triage results table"}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({"summary": summary, "rows": rows}, open(args.out, "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
