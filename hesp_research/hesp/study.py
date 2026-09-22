"""Frozen, randomized paired fixture studies with immutable run folders."""

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random

from .analysis import summarize
from .controller import Budget, MODES, run, source_hash
from .environment import CAUSES, SimulatedEnvironment
from .planner import ScriptedPlanner


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def make_schedule(repeats, seed):
    if isinstance(repeats, bool) or not isinstance(repeats, int) or repeats < 1:
        raise ValueError("repeats must be a positive integer")
    schedule = [{"task_id": f"task{i:02d}", "fixture_cause": cause, "repeat": repeat, "mode": mode}
                for i, cause in enumerate(CAUSES) for repeat in range(repeats) for mode in MODES]
    random.Random(seed).shuffle(schedule)
    return schedule


def run_study(output, repeats=3, seed=42, budget=None):
    schedule = make_schedule(repeats, seed)
    budget = budget or Budget()
    budget.validate()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "hesp.fixture-study.v1", "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_hash(), "seed": seed, "repeats": repeats,
        "budget": asdict(budget), "schedule": schedule,
        "authorization": "In-process synthetic fixtures; no network or external targets",
        "research_claim_allowed": False,
    }
    write_json(output / "manifest.json", manifest)
    manifest_hash = hashlib.sha256((output / "manifest.json").read_bytes()).hexdigest()
    rows = []
    for index, cell in enumerate(schedule):
        folder = f"run{index:04d}_{cell['task_id']}_{cell['repeat']}_{cell['mode']}"
        result = run(SimulatedEnvironment(cell["fixture_cause"]), ScriptedPlanner(),
                     cell["mode"], output / folder, budget)
        row = {**cell, **result, "run_directory": folder}
        rows.append(row)
        # Keep completed outcomes durable even if a later run is interrupted.
        with (output / "outcomes.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    report = summarize(rows, seed=seed)
    report["manifest_sha256"] = manifest_hash
    write_json(output / "analysis.json", report)
    write_json(output / "summary.json", {"manifest_sha256": manifest_hash, "results": rows,
                                        "research_claim_allowed": False})
    lines = ["# Paired fixture study", "", report["warning"], "",
             "| Mode | Runs | Verified | Mean tool calls |", "| --- | ---: | ---: | ---: |"]
    for mode, value in report["modes"].items():
        lines.append(f"| {mode} | {value['runs']} | {value['verified_fraction']:.3f} | "
                     f"{value['tool_calls']['mean_known']:.3f} |")
    lines.extend(["", "No real model calls, Web CTF results, or method superiority claims.",
                  "All failures remain in the denominator; see analysis.json for status counts."])
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
