"""Policy interface: offline smoke policy, or user-authorized JSON subprocess."""

import json
import subprocess


class ScriptedPlanner:
    name = "scripted_smoke_not_llm"

    def decide(self, request):
        # Same policy for A/B/C. It is intentionally not a research baseline.
        for row in reversed(request["history"]):
            if row["outcome"] == "matched" and row["state_version"] == request["state_version"]:
                tools = {a["id"]: a for a in request["tools"]}
                cause = tools[row["action_id"]]["purpose"].removeprefix("diagnose_")
                return {"kind": "finish", "hypothesis": cause,
                        "evidence_ids": [row["id"]], "reason": "Fixture has a matching diagnostic signal",
                        "usage": {"input_tokens": 0, "output_tokens": 0}}
        seen = {(row["action_id"], row["state_version"]) for row in request["history"]}
        version = request["state_version"]
        options = [a for a in request["tools"] if (a["id"], version) not in seen]
        if not options:
            return {"kind": "stop", "reason": "No unused fixture action",
                    "usage": {"input_tokens": 0, "output_tokens": 0}}
        return {"kind": "action", "action_id": options[0]["id"],
                "reason": "Fixed fixture order for software testing only",
                "usage": {"input_tokens": 0, "output_tokens": 0}}


class SubprocessPlanner:
    """User-supplied executable reads one JSON request and prints one JSON reply.

    No shell evaluation. This is not a sandbox: execute only trusted adapters.
    The adapter owns provider credentials; none are copied into request/logs.
    """
    name = "external_json_process"

    def __init__(self, command, timeout=30):
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            raise ValueError("Adapter command must be a nonempty JSON array of strings")
        self.command = command
        self.timeout = timeout

    def decide(self, request):
        try:
            proc = subprocess.run(
                self.command, input=json.dumps(request, ensure_ascii=False),
                capture_output=True, text=True, encoding="utf-8", timeout=self.timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise RuntimeError("Planner adapter unavailable or timed out") from None
        if proc.returncode != 0:
            # Do not log provider stderr, which can contain secrets.
            raise RuntimeError("Planner adapter returned a nonzero exit code")
        if len(proc.stdout) > 1_000_000:
            raise ValueError("Adapter output exceeds protocol limit")
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise ValueError("Planner adapter must return exactly one JSON object") from None
        if not isinstance(result, dict):
            raise ValueError("Planner adapter response must be an object")
        return result


class PosteriorPlanner:
    """Deterministic, model-free policy for selector ablations (not an LLM, not a baseline claim).

    Finishes when the current-state posterior of one hypothesis reaches ``threshold`` and at
    least one used, supporting observation from the current state exists; otherwise proposes
    the next untried probe in catalogue order (the naive "sequential" strategy). In the HESP
    arm the controller overrides the proposed probe. Requires the structured ledger.
    """

    def __init__(self, threshold=0.9):
        self.threshold = threshold
        self.name = f"posterior_threshold_script@{threshold}"

    def decide(self, request):
        zero = {"input_tokens": 0, "output_tokens": 0}
        inv = request.get("investigation")
        if inv is None:
            raise ValueError("PosteriorPlanner requires the structured ledger (memory_only/hesp)")
        version = request["state_version"]
        scores = {h["id"]: h["score"] for h in inv["hypotheses"]}
        top = max(sorted(scores), key=lambda h: scores[h])
        if scores[top] >= self.threshold:
            support = [e["observation_id"] for e in reversed(inv["evidence"])
                       if e["used"] and e["state_version"] == version and e["relations"].get(top) == "support"][:3]
            if support:
                return {"kind": "finish", "hypothesis": top, "evidence_ids": support,
                        "reason": f"posterior {scores[top]:.3f} >= {self.threshold}", "usage": zero}
        tried = {(o["action_id"], o["state_version"]) for o in request["history"] if o.get("valid", True)}
        options = [t for t in request["tools"]
                   if (t["id"], version) not in tried and t["cost"] <= request["remaining_tool_cost"]]
        if not options or request["remaining_tool_calls"] <= 0:
            return {"kind": "stop", "reason": "No affordable untried probe", "usage": zero}
        return {"kind": "action", "action_id": options[0]["id"], "reason": "Next probe in catalogue order",
                "usage": zero}
