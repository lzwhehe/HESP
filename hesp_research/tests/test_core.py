from dataclasses import replace
import math
import unittest

from hesp.core import Action, Ledger, Observation, entropy, expected_information_gain, normalize


def binary_action():
    return Action("test", "fixture://documents", "distinguish", 1,
                  {"a": {"yes": .9, "no": .1}, "b": {"yes": .1, "no": .9}})


class InformationTests(unittest.TestCase):
    def test_entropy_uniform(self):
        self.assertAlmostEqual(entropy({"a": 1, "b": 1}), 1)

    def test_perfect_test_yields_one_bit(self):
        a = replace(binary_action(), likelihoods={"a": {"yes": 1., "no": 0.}, "b": {"yes": 0., "no": 1.}})
        self.assertAlmostEqual(expected_information_gain({"a": .5, "b": .5}, a), 1)

    def test_uninformative_test_yields_zero(self):
        a = replace(binary_action(), likelihoods={"a": {"yes": .5, "no": .5}, "b": {"yes": .5, "no": .5}})
        self.assertAlmostEqual(expected_information_gain({"a": .5, "b": .5}, a), 0)

    def test_information_bound(self):
        prior = {"a": .9, "b": .1}
        value = expected_information_gain(prior, binary_action())
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, entropy(prior))

    def test_invalid_probabilities_rejected(self):
        for p in ({}, {"a": 0}, {"a": -1}, {"a": math.nan}, {"a": math.inf}):
            with self.assertRaises(ValueError):
                normalize(p)

    def test_likelihood_must_sum_to_one(self):
        a = replace(binary_action(), likelihoods={"a": {"yes": .2}, "b": {"yes": .9}})
        with self.assertRaises(ValueError):
            expected_information_gain({"a": .5, "b": .5}, a)

    def test_prediction_must_cover_hypotheses(self):
        with self.assertRaises(ValueError):
            expected_information_gain({"a": .5, "c": .5}, binary_action())

    def test_reject_different_outcome_vocabularies(self):
        a = replace(binary_action(), likelihoods={"a": {"yes": 1}, "b": {"no": 1}})
        with self.assertRaises(ValueError):
            expected_information_gain({"a": .5, "b": .5}, a)

    def test_invalid_costs(self):
        for cost in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                replace(binary_action(), cost=cost).validate({"a", "b"})


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger({"a": .5, "b": .5})
        self.action = binary_action()
        self.obs = Observation("e1", "test", 0, "yes", {"signal": "yes"}, "raw")

    def test_updates_and_relations(self):
        result = self.ledger.ingest(self.action, self.obs)
        self.assertAlmostEqual(self.ledger.scores["a"], .9)
        self.assertEqual(result["relations"], {"a": "support", "b": "against"})
        self.assertTrue(result["used"])

    def test_duplicate_id_does_not_double_count(self):
        self.ledger.ingest(self.action, self.obs)
        result = self.ledger.ingest(self.action, self.obs)
        self.assertEqual(result["skip_reason"], "duplicate_observation")
        self.assertAlmostEqual(self.ledger.scores["a"], .9)

    def test_same_test_new_evidence_id_not_independent(self):
        self.ledger.ingest(self.action, self.obs)
        result = self.ledger.ingest(self.action, replace(self.obs, id="e2"))
        self.assertEqual(result["skip_reason"], "correlated_repeat")

    def test_renamed_action_same_purpose_not_independent(self):
        self.ledger.ingest(self.action, self.obs)
        result = self.ledger.ingest(replace(self.action, id="alias"), replace(self.obs, id="e2", action_id="alias"))
        self.assertEqual(result["skip_reason"], "correlated_repeat")

    def test_unknown_outcome_is_not_negative_evidence(self):
        result = self.ledger.ingest(self.action, replace(self.obs, outcome="timeout"))
        self.assertEqual(result["skip_reason"], "unmodeled_outcome")
        self.assertEqual(self.ledger.scores, {"a": .5, "b": .5})

    def test_invalid_observation_not_used(self):
        result = self.ledger.ingest(self.action, replace(self.obs, valid=False))
        self.assertEqual(result["skip_reason"], "invalid_observation")

    def test_old_state_evidence_not_used(self):
        self.ledger.set_state({"version": 1, "role": "tester"})
        result = self.ledger.ingest(self.action, self.obs)
        self.assertEqual(result["skip_reason"], "stale_state")

    def test_state_change_invalidates_old_scores_and_allows_retest(self):
        self.ledger.ingest(self.action, self.obs)
        self.assertTrue(self.ledger.set_state({"version": 1, "role": "new_tester"}))
        self.assertEqual(self.ledger.scores, {"a": .5, "b": .5})
        result = self.ledger.ingest(self.action, replace(self.obs, id="e2", state_version=1))
        self.assertTrue(result["used"])
        self.assertEqual(len(self.ledger.evidence), 2)

    def test_state_versions_cannot_go_backwards(self):
        with self.assertRaises(ValueError):
            self.ledger.set_state({"version": -1})

    def test_mismatched_action_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.ingest(self.action, replace(self.obs, action_id="wrong"))

    def test_impossible_result_keeps_uncertainty(self):
        action = replace(self.action, likelihoods={"a": {"yes": 0., "no": 1.}, "b": {"yes": 0., "no": 1.}})
        result = self.ledger.ingest(action, self.obs)
        self.assertEqual(result["skip_reason"], "predictive_model_conflict")
        self.assertEqual(self.ledger.scores, {"a": .5, "b": .5})

    def test_high_score_does_not_mean_confirmed(self):
        self.ledger.ingest(self.action, self.obs)
        self.assertTrue(all(h["status"] == "candidate" for h in self.ledger.public()["hypotheses"]))
