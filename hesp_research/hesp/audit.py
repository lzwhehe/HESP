"""Validate durable prediction/observation ordering and run consistency."""

import json
from pathlib import Path


def audit_run(directory):
    directory = Path(directory)
    events = [json.loads(line) for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    result = json.loads((directory / "result.json").read_text(encoding="utf-8"))
    config = json.loads((directory / "config.json").read_text(encoding="utf-8"))
    errors = []
    if [e.get("seq") for e in events] != list(range(1, len(events) + 1)):
        errors.append("Noncontiguous event sequence")
    if not events or events[0].get("kind") != "run_started":
        errors.append("Missing run start")
    if not events or events[-1].get("kind") != "run_finished" or events[-1].get("result") != result:
        errors.append("Missing or inconsistent final result")
    pending = None
    observations = set()
    predictions = decisions = cost = 0
    verification = False
    for event in events:
        kind = event.get("kind")
        if kind == "planner_request":
            decisions += 1
        elif kind == "prediction_registered":
            if pending is not None:
                errors.append("Prediction has no matching observation or execution error")
            pending = (event["action"]["id"], event["state_version"])
            predictions += 1
            cost += event["action"]["cost"]
        elif kind == "observation":
            obs = event["observation"]
            if pending is None or pending[0] != obs["action_id"]:
                errors.append("Observation without preceding matching prediction")
            if obs["id"] in observations:
                errors.append("Duplicate observation ID")
            observations.add(obs["id"])
            pending = None
        elif kind == "execution_error":
            if pending is None or pending[0] != event["action_id"]:
                errors.append("Execution error without matching prediction")
            pending = None
        elif kind == "evidence_update":
            if event["evidence"]["observation_id"] not in observations:
                errors.append("Evidence refers to an unseen observation")
        elif kind == "independent_verification":
            verification = event["passed"] is True
            if verification and (not event["evidence_ids"] or not set(event["evidence_ids"]) <= observations):
                errors.append("Verification cites absent evidence")
    if pending is not None:
        errors.append("Unfinished execution")
    if (predictions, cost, decisions) != (result["tool_calls"], result["tool_cost_units"], result["planner_calls"]):
        errors.append("Result counters differ from journal")
    if verification != result["verified_simulation"]:
        errors.append("Verification result differs from journal")
    if result["source_sha256"] != config["source_sha256"]:
        errors.append("Source hashes differ")
    for actual, limit in ((predictions, "max_tool_calls"), (cost, "max_tool_cost"), (decisions, "max_decisions")):
        if actual > config["budget"][limit]:
            errors.append("Budget exceeded: " + limit)
    return {"passed": not errors, "errors": errors, "events": len(events),
            "scope": "Journal consistency only; not authenticity or real-world success verification"}
