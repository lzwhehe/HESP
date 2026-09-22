import argparse
import json
import sys

from .controller import Budget, MODES, run
from .environment import CAUSES, SimulatedEnvironment
from .planner import ScriptedPlanner, SubprocessPlanner


def main():
    parser = argparse.ArgumentParser(description="HESP simulation-only prototype")
    parser.add_argument("--mode", choices=MODES, default="hesp")
    parser.add_argument("--case", choices=CAUSES, default="owner_policy")
    parser.add_argument("--output", required=True, help="New run directory; never overwrite")
    parser.add_argument("--max-tool-calls", type=int, default=8)
    parser.add_argument("--max-decisions", type=int, default=12)
    parser.add_argument("--max-tool-cost", type=int, default=8)
    parser.add_argument("--max-seconds", type=float, default=60.0)
    parser.add_argument("--planner-command-json", help="Trusted adapter argv as JSON array; no shell")
    args = parser.parse_args()
    try:
        planner = SubprocessPlanner(json.loads(args.planner_command_json)) if args.planner_command_json else ScriptedPlanner()
        result = run(
            SimulatedEnvironment(args.case), planner, args.mode, args.output,
            Budget(args.max_tool_calls, args.max_decisions, args.max_tool_cost, args.max_seconds),
        )
    except (ValueError, OSError) as exc:
        print(f"Cannot start run: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verified_simulation"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
