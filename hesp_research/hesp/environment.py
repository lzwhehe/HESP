"""In-memory diagnostic fixture. No HTTP, payloads, credentials, or live targets."""

from .core import Action, Observation

CAUSES = ("session_expired", "owner_policy", "workflow_locked", "other")


def actions():
    result = [Action(
        "read_help", "fixture://documents", "read_general_help", 1,
        {h: {"generic_help": 1.0} for h in CAUSES},
    )]
    for cause, test_id in zip(CAUSES, ("inspect_session", "inspect_owner", "inspect_workflow", "inspect_other")):
        result.append(Action(
            test_id, "fixture://documents", "diagnose_" + cause, 1,
            {h: {"matched": 0.97 if h == cause else 0.01,
                 "not_matched": 0.03 if h == cause else 0.99} for h in CAUSES},
        ))
    return result


class SimulatedEnvironment:
    label = "synthetic_software_test_only"

    def __init__(self, cause="owner_policy"):
        if cause not in CAUSES:
            raise ValueError("Unknown fixture")
        self._cause = cause
        self._counter = 0
        self._observations = {}
        self._actions = {a.id: a for a in actions()}
        self._version = 0

    def describe(self):
        # Never expose the cause or choose a task ID encoding the cause here.
        return {
            "objective": "Diagnose why a document operation fails in a simulator",
            "initial_observation": "Document operation did not complete",
            "environment": self.label,
            "allowed_targets": ["fixture://documents"],
        }

    def state(self):
        return {"role": "tester", "page": "document", "version": self._version}

    def execute(self, action):
        if self._actions.get(action.id) != action:
            raise ValueError("Only exact fixture actions are allowed")
        self._counter += 1
        if action.id == "read_help":
            outcome = "generic_help"
        else:
            outcome = "matched" if action.purpose == "diagnose_" + self._cause else "not_matched"
        observation = Observation(
            f"o{self._counter:04d}", action.id, self._version, outcome,
            {"signal": outcome},
            f"SIMULATED tool={action.id} signal={outcome}",
        )
        self._observations[observation.id] = observation
        return observation

    def verify(self, hypothesis, evidence_ids):
        """Separate deterministic fixture oracle, inaccessible through Planner API."""
        if hypothesis != self._cause:
            return False
        for evidence_id in evidence_ids:
            obs = self._observations.get(evidence_id)
            if (obs and obs.state_version == self._version and obs.outcome == "matched"
                    and self._actions[obs.action_id].purpose == "diagnose_" + hypothesis):
                return True
        return False
