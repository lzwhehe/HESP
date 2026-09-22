"""Integration smoke suite, deliberately not named a benchmark."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hesp.controller import MODES, run
from hesp.environment import CAUSES, SimulatedEnvironment
from hesp.planner import ScriptedPlanner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for i, cause in enumerate(CAUSES):
        for mode in MODES:
            # Task ID and cause stay out of the Planner request.
            result = run(SimulatedEnvironment(cause), ScriptedPlanner(), mode, output / f"task{i:02d}_{mode}")
            rows.append({"fixture_cause": cause, **result})
    passed = sum(row["verified_simulation"] for row in rows)
    summary = {
        "purpose": "software_integration_smoke_test_only",
        "cases": len(CAUSES), "modes": list(MODES), "runs": len(rows),
        "verified_fixture_runs": passed, "research_claim_allowed": False,
        "warning": "Handwritten tasks, predictions, and policy; no LLM, no Web CTF, no significance claim",
        "results": rows,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Software smoke checks: {passed}/{len(rows)}. NOT research task success rate.")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
