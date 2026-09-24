import argparse
import json
import sys

from .controller import Budget, MODES, run
from .environment import CAUSES, SimulatedEnvironment
from .planner import PosteriorPlanner, ScriptedPlanner, SubprocessPlanner
from .selectors import SELECTORS, Selector
from . import secapp, uploadapp, webapp

FAMILIES = {"web": webapp, "upload": uploadapp, "sec": secapp}


def main():
    parser = argparse.ArgumentParser(description="HESP prototype: one auditable local episode")
    parser.add_argument("--env", choices=("fixture", "web", "upload", "sec"), default="fixture",
                        help="fixture (v0.1), or a loopback sandbox family: web/upload (v0.3-4) or sec (v0.5)")
    parser.add_argument("--mode", choices=MODES, default="hesp")
    all_causes = set(CAUSES).union(*(m.CAUSES for m in FAMILIES.values()))
    parser.add_argument("--case", default="owner_policy",
                        help="hidden cause; valid values depend on --env (see each family's CAUSES)")
    parser.add_argument("--variant", choices=("base", "drift", "noise"), default="base")
    parser.add_argument("--drift-to", default=None, help="cause after drift (drift variant only)")
    parser.add_argument("--selector", choices=SELECTORS, default="eig_cost")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", required=True, help="New run directory; never overwrite")
    parser.add_argument("--max-tool-calls", type=int, default=8)
    parser.add_argument("--max-decisions", type=int, default=12)
    parser.add_argument("--max-tool-cost", type=int, default=8)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    planners = parser.add_mutually_exclusive_group()
    planners.add_argument("--planner-command-json", help="Trusted adapter argv as JSON array; no shell")
    planners.add_argument("--llm", metavar="MODEL", help="Use a local Ollama model, e.g. qwen2.5:7b-instruct")
    args = parser.parse_args()
    env = None
    try:
        if args.llm:
            from .llm import LLMPlanner, OllamaClient
            planner = LLMPlanner(OllamaClient(args.llm), seed=args.seed)
        elif args.planner_command_json:
            planner = SubprocessPlanner(json.loads(args.planner_command_json))
        else:
            planner = ScriptedPlanner() if args.env == "fixture" else PosteriorPlanner()
        if args.env == "fixture":
            env = SimulatedEnvironment(args.case)
        else:
            family = FAMILIES[args.env]
            env_cls = next(v for k, v in vars(family).items() if isinstance(v, type)
                           and getattr(v, "family", None) == {"web": "web-diag", "upload": "upload-diag",
                                                              "sec": "sec-triage"}[args.env])
            case = args.case if args.case in family.CAUSES else family.CAUSES[0]
            drift_to = args.drift_to if (args.variant == "drift") else None
            if args.variant == "drift" and drift_to not in family.CAUSES:
                drift_to = family.CAUSES[(family.CAUSES.index(case) + 3) % len(family.CAUSES)]
            env = env_cls(case, args.variant, args.seed, drift_to)
        result = run(env, planner, args.mode, args.output,
                     Budget(args.max_tool_calls, args.max_decisions, args.max_tool_cost, args.max_seconds),
                     selector=Selector(args.selector, args.seed))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Cannot start run: {exc}", file=sys.stderr)
        return 2
    finally:
        if env is not None:
            env.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verified_simulation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
