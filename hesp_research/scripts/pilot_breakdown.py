"""Secondary breakdowns of a finished pilot: per variant, loop behaviour, token cost per success.

Reads outcomes.jsonl (and each run's events.jsonl for proposal-level behaviour); writes
breakdown.json and breakdown.md next to them. Descriptive only.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study")
    args = parser.parse_args()
    root = Path(args.study)
    rows = [json.loads(l) for l in (root / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    arms = list(dict.fromkeys(json.loads((root / "manifest.json").read_text(encoding="utf-8"))["arms"]))
    out = {"per_variant": {}, "behaviour": {}, "tokens": {}}
    for arm in arms:
        mine = [r for r in rows if r["arm"] == arm]
        out["per_variant"][arm] = {v: mean([float(r["verified_simulation"]) for r in mine if r["variant"] == v])
                                   for v in ("base", "drift", "noise")}
        repairs = llm_seconds = decisions = 0
        proposals = Counter()
        stale_finish = 0
        for r in mine:
            for line in (root / r["run_directory"] / "events.jsonl").read_text(encoding="utf-8").splitlines():
                e = json.loads(line)
                if e["kind"] == "planner_decision":
                    d = e["decision"]
                    decisions += 1
                    llm = d.get("llm") or {}
                    repairs += llm.get("attempts", 1) - 1
                    llm_seconds += llm.get("seconds", 0)
                    proposals[d["kind"]] += 1
        solved = [r for r in mine if r["verified_simulation"]]
        tokens = [(r["reported_input_tokens"] or 0) + (r["reported_output_tokens"] or 0) for r in mine
                  if r["reported_input_tokens"] is not None]
        out["behaviour"][arm] = {
            "episodes": len(mine), "decisions": decisions, "repair_attempts": repairs,
            "blocked_duplicate_proposals_per_episode": mean([r["blocked_duplicate_proposals"] for r in mine]),
            "episodes_with_any_blocked_duplicate": sum(r["blocked_duplicate_proposals"] > 0 for r in mine),
            "decision_kinds": dict(proposals), "statuses": dict(Counter(r["status"] for r in mine)),
            "llm_seconds_per_episode": llm_seconds / len(mine),
        }
        out["tokens"][arm] = {
            "mean_total_tokens_per_episode": mean(tokens),
            "total_tokens_per_verified_episode": (sum(tokens) / len(solved)) if solved else None,
            "mean_input_tokens": mean([r["reported_input_tokens"] for r in mine]),
            "mean_output_tokens": mean([r["reported_output_tokens"] for r in mine]),
            "unknown_usage_episodes": sum(r["reported_input_tokens"] is None for r in mine),
        }
    (root / "breakdown.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    f = lambda v, d=3: "n/a" if v is None else f"{v:.{d}f}"
    lines = ["# Pilot breakdown (descriptive)", "", "## Verified rate by variant", "",
             "| Arm | base | drift | noise |", "| --- | ---: | ---: | ---: |"]
    lines += [f"| {a} | " + " | ".join(f(out["per_variant"][a][v]) for v in ("base", "drift", "noise")) + " |"
              for a in arms]
    lines += ["", "## Planner behaviour", "",
              "| Arm | blocked dup. proposals / ep. | eps. with a blocked dup. | repair attempts | "
              "LLM s / ep. | tokens / ep. | tokens / verified ep. |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for a in arms:
        b, t = out["behaviour"][a], out["tokens"][a]
        lines.append(f"| {a} | {f(b['blocked_duplicate_proposals_per_episode'], 2)} | "
                     f"{b['episodes_with_any_blocked_duplicate']}/{b['episodes']} | {b['repair_attempts']} | "
                     f"{f(b['llm_seconds_per_episode'], 1)} | {f(t['mean_total_tokens_per_episode'], 0)} | "
                     f"{f(t['total_tokens_per_verified_episode'], 0)} |")
    lines += ["", "Tokens are server-reported by local Ollama (prompt incl. cached prefix + generated)."]
    (root / "breakdown.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
