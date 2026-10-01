"""K2-capability analysis (docs/PROTOCOL_SMALL.md, section K2-能力).

Per model: accuracy of C1-C3 and C4 on the 589 o1 test questions and on the 186 shortcut-resistant ones, paired
differences with incident-clustered bootstrap intervals (2,000 resamples, seed 2040), P1/P2 decisions for the two small
models, descriptive C3-C2 and model-size comparisons, and 15 random judgments per model for manual checking.

    python scripts/small/k2_analysis.py --dir results/small/k2
"""
import argparse
import json
import random
from pathlib import Path

from k1_analysis import acc, diff_ci

ROOT = Path(__file__).resolve().parents[2]
MODELS = [("qwen2.5-7b-instruct", "Qwen2.5-7B"), ("llama-3.1-8b-instruct", "Llama-3.1-8B"), ("phi-4", "phi-4 (14B)")]
SMALL = MODELS[:2]


def load(path):
    p = Path(path)
    return {(r["incident"], r["index"]): r for r in map(json.loads, open(p, encoding="utf-8"))} if p.exists() else {}


def summary(rows, keys, res):
    return {"accuracy": acc(rows, keys), "accuracy_resistant": acc(rows, res),
            "no_answer": sum(not rows[k]["submitted"] for k in keys), "overflow": sum(rows[k]["overflow"] for k in keys),
            "mean_steps": sum(rows[k]["steps"] for k in keys) / len(keys)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "results/small/k2"))
    args = ap.parse_args()
    d = Path(args.dir)
    c4 = load(d / "C4.jsonl")
    out = {"models": {}, "C4": None}
    keys_all = sorted(c4)
    res_all = [k for k in keys_all if c4[k]["resistant"] == 1]
    out["C4"] = summary(c4, keys_all, res_all)
    rng = random.Random(11)
    out["manual_check"] = []
    for mid, name in MODELS:
        R = {c: load(d / f"{mid}_{c}.jsonl") for c in ("C1", "C2", "C3")}
        if not all(len(R[c]) for c in R):
            continue
        keys = sorted(set(keys_all).intersection(*(set(R[c]) for c in R)))
        res = [k for k in keys if c4[k]["resistant"] == 1]
        m = {"name": name, "questions": len(keys), "resistant": len(res),
             "conditions": {c: summary(R[c], keys, res) for c in R},
             "contrasts": {"C2-C1": diff_ci(R["C2"], R["C1"], keys), "C2-C4": diff_ci(R["C2"], c4, keys),
                           "C2-C4 (resistant)": diff_ci(R["C2"], c4, res), "C3-C2": diff_ci(R["C3"], R["C2"], keys),
                           "C3-C1": diff_ci(R["C3"], R["C1"], keys)}}
        if (mid, name) in SMALL:
            p1 = m["contrasts"]["C2-C1"]["ci95"][0] > 0
            p2 = m["contrasts"]["C2-C4"]["ci95"][0] > 0
            m["decision"] = {"P1": p1, "P2": p2, "P2_resistant_ci_excludes_0": m["contrasts"]["C2-C4 (resistant)"]["ci95"][0] > 0}
        out["models"][mid] = m
        for c, k in [(c, rng.choice(keys)) for c in ("C1", "C2", "C3") for _ in range(5)]:
            out["manual_check"].append({"model": name, "cond": c, "incident": k[0], "index": k[1], "gold": R[c][k]["gold"],
                                        "answer": R[c][k]["answer"], "scored_correct": R[c][k]["correct"]})
    # model-size comparison on C2 (descriptive)
    if "phi-4" in out["models"]:
        R14 = load(d / "phi-4_C2.jsonl")
        for mid, name in SMALL:
            if mid in out["models"]:
                Rs = load(d / f"{mid}_C2.jsonl")
                keys = sorted(set(R14) & set(Rs))
                out["models"][mid]["C2_vs_phi4_C2"] = diff_ci(Rs, R14, keys)
    fr = ROOT / "results/small/k2_frontier.json"
    if fr.exists():
        out["frontier_reference"] = json.loads(fr.read_text(encoding="utf-8"))
    (d / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("C4:", {k: round(v, 3) if isinstance(v, float) else v for k, v in out["C4"].items()})
    for mid, m in out["models"].items():
        print(m["name"], {c: (round(v["accuracy"], 3), round(v["accuracy_resistant"], 3), v["no_answer"], v["overflow"])
                          for c, v in m["conditions"].items()})
        for n, v in m["contrasts"].items():
            print(f"   {n}: {v['diff']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] a-only {v['a_only']} b-only {v['b_only']}")
        if "decision" in m:
            print("   decision", m["decision"])
        if "C2_vs_phi4_C2" in m:
            v = m["C2_vs_phi4_C2"]
            print(f"   C2 vs phi-4 C2: {v['diff']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]")


if __name__ == "__main__":
    main()
