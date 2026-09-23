import argparse
import json
import sys

from .controller import Budget, MODES, run
from .environment import CAUSES, SimulatedEnvironment
from .planner import PosteriorPlanner, ScriptedPlanner, SubprocessPlanner
from .selectors import SELECTORS, Selector
from . import webapp


def main():
    parser = argparse.ArgumentParser(description="HESP prototype: one auditable local episode")
    parser.add_argument("--env", choices=("fixture", "web"), default="fixture",
                        help="in-process fixture (v0.1) or the loopback web sandbox (v0.3)")
    parser.add_argument("--mode", choices=MODES, default="hesp")
    parser.add_argument("--case", choices=sorted(set(CAUSES) | set(webapp.CAUSES)), default="owner_policy")
    parser.add_argument("--variant", choices=sorted(webapp.VARIANTS), default="base")
    parser.add_argument("--drift-to", choices=webapp.CAUSES, default="workflow_locked")
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
            env = webapp.WebDiagEnvironment(args.case, args.variant, args.seed,
                                            args.drift_to if args.variant == "drift" else None)
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
