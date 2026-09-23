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


# --------------------------------------------------------------------------- v0.3 suites
def cell_seed(seed, task_id, repeat):
    """Environment/selector seed shared by all arms of one (task, repeat) pair."""
    return int(hashlib.sha256(f"{seed}|{task_id}|{repeat}".encode()).hexdigest()[:8], 16)


def run_suite(output, tasks, arms, env_factory, repeats=1, seed=42, budget=None, comparisons=None,
              extra_manifest=None, resume=False, progress=None, purpose="scripted_ablation"):
    """Paired, shuffled, resumable study over arbitrary arms.

    tasks: list of dicts with a unique ``task_id`` (hidden fields stay out of planner requests).
    arms:  {name: {"mode", "planner": callable(seed)->planner, "selector": str,
                   "predictor": object | None}}
    env_factory: callable(task, seed) -> environment (context manager or with close()).
    """
    from .selectors import Selector
    budget = budget or Budget()
    budget.validate()
    output = Path(output)
    schedule = [{"task_id": t["task_id"], "repeat": r, "arm": a}
                for t in tasks for r in range(repeats) for a in arms]
    random.Random(seed).shuffle(schedule)
    arm_specs = {name: {"mode": s["mode"], "selector": s.get("selector", "eig_cost"),
                        "prediction_source": getattr(s.get("predictor"), "source", "designer_table"),
                        "planner": s["planner"](0).name} for name, s in arms.items()}
    manifest = {
        "schema": "hesp.suite.v1", "source_sha256": source_hash(), "seed": seed, "repeats": repeats,
        "budget": asdict(budget), "arms": arm_specs, "tasks": tasks, "schedule": schedule,
        "purpose": purpose, "research_claim_allowed": False, **(extra_manifest or {}),
    }
    done = {}
    if resume and (output / "manifest.json").exists():
        old = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if {k: old.get(k) for k in ("schedule", "arms", "budget", "tasks")} != \
                {k: manifest[k] for k in ("schedule", "arms", "budget", "tasks")}:
            raise ValueError("Existing manifest differs; refusing to resume into it")
        if old.get("source_sha256") != manifest["source_sha256"]:
            raise ValueError("Source changed since the study started; refusing to mix versions")
        if (output / "outcomes.jsonl").exists():
            for line in (output / "outcomes.jsonl").read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                done[row["task_id"], row["repeat"], row["arm"]] = row
    else:
        output.mkdir(parents=True, exist_ok=False)
        manifest["created_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "manifest.json", manifest)
    manifest_hash = hashlib.sha256((output / "manifest.json").read_bytes()).hexdigest()
    task_map = {t["task_id"]: t for t in tasks}
    rows = []
    for index, cell in enumerate(schedule):
        key = (cell["task_id"], cell["repeat"], cell["arm"])
        folder = f"run{index:04d}_{cell['task_id']}_{cell['repeat']}_{cell['arm']}"
        if key in done:
            rows.append(done[key])
            continue
        if (output / folder).exists():
            # An interrupted attempt is kept for the audit trail, never silently reused.
            (output / folder).rename(output / f"_aborted_{datetime.now(timezone.utc):%Y%m%dT%H%M%S}_{folder}")
        spec = arms[cell["arm"]]
        s = cell_seed(seed, cell["task_id"], cell["repeat"])
        env = env_factory(task_map[cell["task_id"]], s)
        try:
            result = run(env, spec["planner"](s), spec["mode"], output / folder, budget,
                         predictor=spec.get("predictor"), selector=Selector(spec.get("selector", "eig_cost"), s),
                         arm=cell["arm"], metadata={"task_id": cell["task_id"], "repeat": cell["repeat"]})
        finally:
            env.close()
        row = {**{k: v for k, v in task_map[cell["task_id"]].items()}, **cell, **result, "run_directory": folder}
        rows.append(row)
        with (output / "outcomes.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        if progress:
            progress(index + 1, len(schedule), row)
    report = summarize(rows, seed=seed, arms=list(arms), comparisons=comparisons)
    report["purpose"] = purpose
    report["warning"] = ("Paired local-sandbox study. Intervals are over task clusters of a small, "
                         "hand-built suite; they do not generalize to real websites or Web CTF.")
    report["manifest_sha256"] = manifest_hash
    write_json(output / "analysis.json", report)
    return report, rows
