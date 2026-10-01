"""Explain the HESP controller on one real episode: run the LLM-free controller (EIG/cost selection, controller stop
at 0.8, designer tables) on one sec-triage case and print, for every step, the posterior, the probe ranking, what the
planner proposed, the probe the controller executed, the raw response, its classified outcome, and the update.
For explanation only; not a study.

    python scripts/demo_controller_trace.py --cause dns_c2
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.controller import Budget, run  # noqa: E402
from hesp.planner import NeverFinishPlanner  # noqa: E402
from hesp.secapp import make_sec_env  # noqa: E402


def top(scores, n=4):
    return ", ".join(f"{h} {p:.3f}" for h, p in sorted(scores.items(), key=lambda kv: -kv[1])[:n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cause", default="dns_c2")
    ap.add_argument("--variant", default="base")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    env = make_sec_env({"cause": args.cause, "variant": args.variant}, seed=args.seed)
    out = Path(tempfile.mkdtemp()) / "run"
    run(env, NeverFinishPlanner(), "hesp", out,
        budget=Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60), auto_finish=0.8)
    print(f"hidden cause: {args.cause} ({args.variant}); 9 hypotheses, uniform prior 1/9 = 0.111")
    step = 0
    for line in open(out / "events.jsonl", encoding="utf-8"):
        e = json.loads(line)
        k = e["kind"]
        if k == "planner_request":
            step += 1
            print(f"\n--- step {step} ---")
            for a in (e["request"].get("action_rankings") or [])[:4]:
                print(f"  rank: {a['action_id']:<18} EIG {a['expected_information_gain_bits']:.3f} bits / cost "
                      f"{a['cost']} = {a['score']:.3f}")
        elif k == "planner_decision":
            print(f"  planner proposes: {e['decision'].get('action_id', e['decision']['kind'])}")
        elif k == "evidence_update":
            ev = e["evidence"]
            print(f"  controller executes: {ev['action_id']}")
            print(f"  raw response: {ev['raw']}")
            print(f"  classified outcome: {ev['outcome']}")
            print(f"  posterior before: {top(ev['before'])}")
            print(f"  posterior after : {top(ev['after'])}")
        elif k == "controller_finish":
            print(f"\ncontroller stop: {e['hypothesis']} with posterior {e['scores'][e['hypothesis']]:.3f} >= "
                  f"{e['threshold']}, citing {e['evidence_ids']}")
        elif k == "independent_verification":
            print(f"verifier (knows the hidden cause): passed = {e['passed']}")


if __name__ == "__main__":
    main()
