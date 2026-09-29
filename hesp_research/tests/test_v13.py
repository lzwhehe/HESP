"""v1.3: adaptive log injection, reader policies, and the ``benign_requires_trusted`` option. The option is off by
default; the defaults must reproduce v1.2 exactly."""

import json
from pathlib import Path
import random
import tempfile
import unittest

from hesp.audit import audit_run
from hesp.controller import Budget, run
from hesp.planner import NeverFinishPlanner
from hesp.predictors import FrozenPredictor
from hesp.rawlog import (CLAIMED_LABEL, CLAIMS, CONDITIONS, AdoptParser, RuleFirstParser, RuleParser, StripParser,
                         make_raw_env_class, render)
from hesp.secapp import CAUSES, VARIANTS, _respond, classify, make_sec_env, sec_suite
from hesp.selectors import Selector

BUDGET = Budget(max_tool_calls=10, max_decisions=12, max_tool_cost=10, max_seconds=60.0)
TABLE = json.loads((Path(__file__).resolve().parents[1] / "results/v06_tables/empirical_20.json")
                   .read_text(encoding="utf-8"))["tables"]
VOLATILE = {"wall_seconds", "source_sha256"}
PATHS = {"auth_log": "/siem/auth?window=1h", "access_pattern": "/siem/http?window=1h",
         "source_ips": "/siem/sources?window=1h", "admin_exposure": "/config/admin",
         "user_activity": "/siem/egress?window=24h", "dns_logs": "/siem/dns?window=1h",
         "component_versions": "/inventory/components", "change_ticket": "/itsm/changes?window=24h",
         "threat_intel": "/ti/enrich"}
ATTACKS = ("injected", "injected_all", "drifted_injected_all", "lineinjected_all")


def cases():
    for cause in CAUSES:
        for pid, path in PATHS.items():
            status, body = _respond(cause, "GET", path, random.Random(2), VARIANTS["base"])
            yield pid, body, classify(pid, status, body)


class TruthUntrusted:
    """Reads every format correctly but is not a trusted source (stands in for a model that is never fooled)."""
    name = source = "llm"

    def parse_with_source(self, probe_id, text, truth=None):
        return truth, "llm"


def recommended(env, root, seed=5, **kw):
    """The recommended configuration of the paper, LLM-free planning."""
    return run(env, NeverFinishPlanner(), "hesp", Path(root) / "r", BUDGET, selector=Selector("eig_cost", seed),
               show_rankings=False, auto_finish=0.8, stop_rule="confirm", corroborate_benign=2,
               corroborate_unit="source", finish_rejection_limit=2, predictor=FrozenPredictor(TABLE, "empirical_20"), **kw)


def raw_episode(cause, variant, parser, condition, seed=5, **kw):
    with tempfile.TemporaryDirectory() as root:
        with make_raw_env_class(parser, condition)(cause, variant, seed) as env:
            result = recommended(env, root, seed, **kw)
            log = list(env.parse_log)
        audit = audit_run(Path(root) / "r")
    return result, audit, log


class RenderAndParserTests(unittest.TestCase):
    def test_rule_parser_reads_the_first_record_under_every_documented_condition(self):
        rng, parser = random.Random(1), RuleParser()
        for pid, body, truth in cases():
            for condition in ("documented", "injected", "injected_all", "lineinjected_all"):
                with self.subTest(pid=pid, condition=condition):
                    self.assertEqual(parser.parse(pid, render(pid, body, condition, rng)), truth)
            for condition in ("drifted", "drifted_injected_all"):
                with self.subTest(pid=pid, condition=condition):
                    self.assertIsNone(parser.parse(pid, render(pid, body, condition, rng)))

    def test_adopter_takes_every_claim_it_can_see_and_reads_the_truth_otherwise(self):
        rng, adopt = random.Random(1), AdoptParser()
        for pid, body, truth in cases():
            for condition in CONDITIONS:
                label, source = adopt.parse_with_source(pid, render(pid, body, condition, rng), truth=truth)
                expected = CLAIMED_LABEL[pid] if pid in CLAIMS.get(condition, {}) else truth
                with self.subTest(pid=pid, condition=condition):
                    self.assertEqual((label, source), (expected, "adopt"))

    def test_strip_removes_field_claims_but_not_a_forged_log_line(self):
        rng, strip = random.Random(1), StripParser(AdoptParser())
        for pid, body, truth in cases():
            for condition in ("injected", "injected_all", "drifted_injected_all"):
                with self.subTest(pid=pid, condition=condition):
                    self.assertEqual(strip.parse_with_source(pid, render(pid, body, condition, rng), truth=truth)[0], truth)
            if pid in CLAIMED_LABEL:
                with self.subTest(pid=pid, condition="lineinjected_all"):
                    self.assertEqual(strip.parse_with_source(pid, render(pid, body, "lineinjected_all", rng), truth=truth)[0],
                                     CLAIMED_LABEL[pid])

    def test_rule_first_falls_back_only_when_the_rule_parser_reads_nothing(self):
        rng, parser = random.Random(1), RuleFirstParser(AdoptParser())
        pid, body, truth = next(cases())
        self.assertEqual(parser.parse_with_source(pid, render(pid, body, "injected_all", rng), truth=truth), (truth, "rule"))
        self.assertEqual(parser.parse_with_source(pid, render(pid, body, "drifted_injected_all", rng), truth=truth)[1], "adopt")

    def test_lineinjected_text_contains_two_records_and_the_claim_is_a_valid_documented_line(self):
        rng = random.Random(1)
        _, body = _respond("credential_stuffing", "GET", PATHS["source_ips"], random.Random(2), VARIANTS["base"])
        text = render("source_ips", body, "lineinjected_all", rng)
        records = [l for l in text.splitlines() if l.startswith("probe=source_ips ")]
        self.assertEqual(len(records), 2)
        self.assertEqual(RuleParser().parse("source_ips", records[1]), "known_scanner_asn")


class TrustFactsTests(unittest.TestCase):
    def test_observations_record_parser_and_trust(self):
        for parser, trusted in ((RuleParser(), True), (TruthUntrusted(), False), (RuleFirstParser(TruthUntrusted()), True)):
            with make_raw_env_class(parser, "documented")("sqli_probe", "base", 3) as env:
                obs = env.execute(next(a for a in env.catalog() if a.id == "access_pattern"))
            with self.subTest(parser=parser.name):
                self.assertEqual(obs.facts["trusted"], trusted)
                self.assertEqual(env.parse_log[0]["source"], obs.facts["parser"])

    def test_rule_first_marks_fallback_observations_untrusted(self):
        with make_raw_env_class(RuleFirstParser(TruthUntrusted()), "drifted")("sqli_probe", "base", 3) as env:
            obs = env.execute(next(a for a in env.catalog() if a.id == "access_pattern"))
        self.assertEqual((obs.outcome, obs.facts["parser"], obs.facts["trusted"]), ("sqli_payloads", "llm", False))


class BenignRequiresTrustedTests(unittest.TestCase):
    def test_explicit_default_reproduces_v12(self):
        def structured(**kw):
            with tempfile.TemporaryDirectory() as root:
                with make_sec_env(next(t for t in sec_suite(("base",)) if t["cause"] == "authorized_scan"), 5) as env:
                    return recommended(env, root, **kw)
        a, b = structured(), structured(benign_requires_trusted=False)
        self.assertEqual({k: v for k, v in a.items() if k not in VOLATILE}, {k: v for k, v in b.items() if k not in VOLATILE})
        self.assertNotIn("benign_requires_trusted", json.dumps(a))

    def test_untrusted_readings_cannot_close_a_benign_case_but_can_confirm_an_attack(self):
        benign, audit, _ = raw_episode("authorized_scan", "base", TruthUntrusted(), "documented", benign_requires_trusted=True)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertIsNone(benign["claimed_hypothesis"])          # every reading was correct, none was trusted
        attack, audit, _ = raw_episode("sqli_probe", "base", TruthUntrusted(), "documented", benign_requires_trusted=True)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertTrue(attack["verified_simulation"])

    def test_trusted_readings_close_a_benign_case_under_the_option(self):
        benign, audit, _ = raw_episode("authorized_scan", "base", RuleParser(), "documented", benign_requires_trusted=True)
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertTrue(benign["verified_simulation"])

    def test_option_is_recorded_in_the_config(self):
        with tempfile.TemporaryDirectory() as root:
            with make_raw_env_class(RuleParser(), "documented")("sqli_probe", "base", 3) as env:
                recommended(env, root, benign_requires_trusted=True)
            config = json.loads((Path(root) / "r" / "config.json").read_text(encoding="utf-8"))
        self.assertTrue(config["benign_requires_trusted"])


class AdaptiveAttackTests(unittest.TestCase):
    """The pre-registered upper bound: under full adoption, a consistent story on every probe defeats source-group
    corroboration; the reader-trust rule removes the benign verdict."""

    def test_full_adoption_of_a_consistent_story_closes_an_attack_as_the_authorized_scan(self):
        for condition in ("injected_all", "lineinjected_all"):
            result, audit, log = raw_episode("credential_stuffing", "base", AdoptParser(), condition)
            with self.subTest(condition=condition):
                self.assertTrue(audit["passed"], audit["errors"])
                self.assertEqual(result["claimed_hypothesis"], "authorized_scan")
                self.assertFalse(result["verified_simulation"])

    def test_reader_trust_escalates_the_same_episodes(self):
        for condition in ("injected_all", "drifted_injected_all", "lineinjected_all"):
            result, audit, _ = raw_episode("credential_stuffing", "base", RuleFirstParser(AdoptParser()), condition,
                                           benign_requires_trusted=True)
            with self.subTest(condition=condition):
                self.assertTrue(audit["passed"], audit["errors"])
                self.assertNotIn(result["claimed_hypothesis"], ("authorized_scan", "false_positive_monitor"))

    def test_even_the_four_probe_injection_of_v12_closes_the_attack_under_full_adoption(self):
        """v1.2's safety came from partial adoption, not from the ledger: the four claimed probes span three source groups."""
        result, audit, _ = raw_episode("credential_stuffing", "base", AdoptParser(), "injected")
        self.assertTrue(audit["passed"], audit["errors"])
        self.assertEqual(result["claimed_hypothesis"], "authorized_scan")


if __name__ == "__main__":
    unittest.main()
