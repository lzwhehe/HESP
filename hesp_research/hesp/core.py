"""Small typed records and explicitly model-dependent Bayesian calculations."""

from dataclasses import dataclass, field
import hashlib
import json
import math


def normalize(values):
    if not values or any(not math.isfinite(v) or v < 0 for v in values.values()):
        raise ValueError("Scores must be nonnegative, finite, and nonempty")
    total = sum(values.values())
    if total <= 0:
        raise ValueError("Scores have zero mass")
    return {k: v / total for k, v in values.items()}


def entropy(scores):
    return -sum(p * math.log2(p) for p in normalize(scores).values() if p > 0)


@dataclass(frozen=True)
class Action:
    id: str
    target: str
    purpose: str
    cost: int
    likelihoods: dict[str, dict[str, float]]
    prediction_source: str = "handwritten_simulator_model"
    prerequisites: dict = field(default_factory=dict)
    # Public, planner-visible text. Not part of the fingerprint.
    description: str = ""
    outcome_notes: dict = field(default_factory=dict)

    def outcomes(self):
        return list(next(iter(self.likelihoods.values())))

    def validate(self, hypotheses):
        if isinstance(self.cost, bool) or not isinstance(self.cost, int) or self.cost <= 0:
            raise ValueError("Cost must be a positive integer")
        if set(self.likelihoods) != set(hypotheses):
            raise ValueError("Prediction must cover every local hypothesis")
        outcomes = None
        for row in self.likelihoods.values():
            normalize(row)
            if not math.isclose(sum(row.values()), 1.0, abs_tol=1e-8):
                raise ValueError("Each likelihood row must sum to one")
            if outcomes is not None and set(row) != outcomes:
                raise ValueError("All hypotheses must predict the same outcome vocabulary")
            outcomes = set(row)

    def fingerprint(self, version):
        value = [self.target, self.purpose, version, self.prerequisites]
        return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def expected_information_gain(scores, action):
    """Exact IG for a finite *supplied* predictive model, not an LLM truth score."""
    scores = normalize(scores)
    action.validate(scores)
    expected = 0.0
    for outcome in next(iter(action.likelihoods.values())):
        joint = {h: p * action.likelihoods[h][outcome] for h, p in scores.items()}
        mass = sum(joint.values())
        if mass > 0:
            expected += mass * entropy(joint)
    return max(0.0, entropy(scores) - expected)


@dataclass(frozen=True)
class Observation:
    id: str
    action_id: str
    state_version: int
    outcome: str
    facts: dict
    raw: str
    valid: bool = True


class Ledger:
    """Version-scoped evidence. High posterior alone never confirms a result."""

    def __init__(self, priors, initial_state=None):
        self.priors = normalize(priors)
        self.scores = dict(self.priors)
        self.state = dict(initial_state or {"role": "tester", "page": "document", "version": 0})
        self.evidence = []
        self.observation_ids = set()
        self.used_fingerprints = set()

    def set_state(self, state):
        version = state["version"]
        if version < self.state["version"]:
            raise ValueError("State versions must not go backwards")
        changed = version != self.state["version"]
        if changed:
            self.scores = dict(self.priors)
        self.state = dict(state)
        return changed

    def ingest(self, action, observation):
        action.validate(self.scores)
        if observation.action_id != action.id:
            raise ValueError("Observation must match executed action")
        fingerprint = action.fingerprint(observation.state_version)
        reason = None
        if observation.id in self.observation_ids:
            reason = "duplicate_observation"
        elif observation.state_version != self.state["version"]:
            reason = "stale_state"
        elif not observation.valid:
            reason = "invalid_observation"
        elif fingerprint in self.used_fingerprints:
            reason = "correlated_repeat"
        elif observation.outcome not in next(iter(action.likelihoods.values())):
            reason = "unmodeled_outcome"
        self.observation_ids.add(observation.id)
        before = dict(self.scores)
        if reason is None:
            unnormalized = {
                h: p * action.likelihoods[h][observation.outcome]
                for h, p in self.scores.items()
            }
            if sum(unnormalized.values()) == 0:
                reason = "predictive_model_conflict"
            else:
                self.scores = normalize(unnormalized)
                self.used_fingerprints.add(fingerprint)
        relations = {
            h: "support" if self.scores[h] > before[h] + 1e-9
            else "against" if self.scores[h] < before[h] - 1e-9 else "neutral"
            for h in before
        }
        entry = {
            "observation_id": observation.id,
            "action_id": action.id,
            "state_version": observation.state_version,
            "outcome": observation.outcome,
            "facts": observation.facts,
            "raw": observation.raw,
            "used": reason is None,
            "skip_reason": reason,
            "before": before,
            "after": dict(self.scores),
            "relations": relations,
            "interpretation": "relative_to_supplied_predictive_model",
        }
        self.evidence.append(entry)
        return entry

    def public(self):
        return {
            "business_state": dict(self.state),
            "hypotheses": [{"id": h, "score": p, "status": "candidate"}
                           for h, p in self.scores.items()],
            "evidence": list(self.evidence),
            "score_warning": "Model-dependent scores, not confirmed vulnerabilities",
        }
