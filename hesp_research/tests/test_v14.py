"""v1.4: a model that decides alone on raw logs. ``NullParser`` leaves every observation ``unparsed`` with the log
text; the planner prompt shows the text and no label; the verifier applies the structured standard (a signature in
the cited observation's true outcome)."""

import tempfile
import unittest
from pathlib import Path

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.llm import render_request
from hesp.rawlog import NullParser, make_raw_env_class

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)


class ScriptReader:
    """Probes ``source_ips``, then finishes with a fixed hypothesis citing that observation; records the prompts."""
    name = "script_reader"

    def __init__(self, hypothesis):
        self.hypothesis, self.prompts = hypothesis, []

    def decide(self, request):
        self.prompts.append(render_request(request))
        if not request["history"]:
            return {"kind": "action", "action_id": "source_ips", "reason": "read sources"}
        return {"kind": "finish", "hypothesis": self.hypothesis, "evidence_ids": [request["history"][0]["id"]],
                "reason": "read the log"}


def episode(hypothesis, condition="drifted", mode="react_style", presentation="unparsed"):
    planner = ScriptReader(hypothesis)
    with tempfile.TemporaryDirectory() as root:
        with make_raw_env_class(NullParser(presentation), condition)("credential_stuffing", "base", 5) as env:
            result = run(env, planner, mode, Path(root) / "r", BUDGET)
            log = list(env.parse_log)
        audit = audit_run(Path(root) / "r")
    return result, audit, log, planner.prompts


class TestModelAloneOnRawLogs(unittest.TestCase):
    def test_prompt_shows_text_not_label(self):
        for mode in ("react_style", "memory_only"):
            _, audit, log, prompts = episode("credential_stuffing", mode=mode)
            self.assertTrue(audit["passed"])
            self.assertEqual(log[0]["parsed"], None)
            self.assertEqual(log[0]["truth"], "many_residential")
            last = prompts[-1]
            self.assertIn("source_ips -> outcome=(not parsed; read the log text)", last)
            self.assertIn("consumer broadband ranges flagged as botnet", last)
            self.assertNotIn("outcome=many_residential", last)
            self.assertNotIn("=many_residential:", last)        # memory-only ledger line

    def test_documented_text_reaches_the_prompt(self):
        _, _, _, prompts = episode("credential_stuffing", condition="documented")
        self.assertIn("probe=source_ips reputation=residential_botnet", prompts[-1])

    def test_correct_reading_is_verified(self):
        result, _, _, _ = episode("credential_stuffing")
        self.assertEqual(result["status"], "VERIFIED_SIMULATION")

    def test_neutral_wording(self):
        result, _, _, prompts = episode("credential_stuffing", presentation="raw_text")
        self.assertIn("source_ips -> outcome=(raw log below)", prompts[-1])
        self.assertNotIn("not parsed", prompts[-1])
        self.assertEqual(result["status"], "VERIFIED_SIMULATION")

    def test_wrong_cause_is_not_verified(self):
        result, _, _, _ = episode("authorized_scan")
        self.assertNotEqual(result["status"], "VERIFIED_SIMULATION")


if __name__ == "__main__":
    unittest.main()
