"""GUIDE incident replay (PROTOCOL.md v0.7): real, analyst-graded Defender XDR incidents.

Each episode replays one incident's metadata. The hypotheses are the analyst grades
(TruePositive, BenignPositive, FalsePositive); a probe reveals one facet of the incident, already
discretised by ``scripts/external/guide_build_incidents.py``. Everything the controller models --
P(o | grade, probe), the detector's grading history, and the organisation prior -- is estimated
from the history split only (the GUIDE training split) by ``GuideModel``. Verification is
"the verdict equals the analyst's grade"; there is no signature requirement, because GUIDE
records a grade, not the evidence that justified it.

Both parts of the v0.7 study use this module, so the LLM-free confirmation (part A) and the LLM
episodes (part B) share one model.
"""
import collections
import json

from .core import Action, Observation

LABEL = "guide_replay"
GRADES = ("TruePositive", "BenignPositive", "FalsePositive")
TARGET = "guide://incident"
TOP_OUTCOMES = 60          # outcomes kept by name per probe; the rest -> "other"
PRIOR_ALPHA = 20           # pseudo-counts pulling an organisation's prior toward the global mix
DETECTOR_MIN, DETECTOR_PURE = 20, 0.6
COLD_MIN, COLD_PURE = 5, 0.8

PROBES = {   # id: (cost, planner-visible description)
    "category": (1, "MITRE tactic category of the incident's alerts (majority), e.g. InitialAccess, Exfiltration"),
    "technique": (1, "most common MITRE technique id on the alerts, or none"),
    "entity_types": (1, "the two most frequent evidence entity types, e.g. Ip+User, MailMessage+User"),
    "evidence_roles": (1, "whether evidence is mostly Impacted or mostly Related"),
    "scale": (1, "number of alerts and of evidence rows in the incident"),
    "detector": (2, "how past incidents from the same detector were graded (all organisations)"),
    "auto_verdict": (2, "automated-investigation verdict: Malicious / Suspicious / NoThreatsFound / none"),
    "roles": (1, "strongest entity role annotation: Compromised, Attacker, Suspicious, ... or none"),
    "threat_family": (1, "whether a malware / threat family is named"),
    "geography": (1, "number of distinct countries among the evidence"),
}
ANSWERS = {
    "TruePositive": "real malicious activity that needs response",
    "BenignPositive": "real activity that is expected or authorised (e.g. a test, an admin action); no response",
    "FalsePositive": "the detection itself was wrong; nothing of note happened",
}


def load_incidents(path):
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


class GuideModel:
    """Everything estimated from the history split. ``incidents`` keep their raw detector ids."""

    def __init__(self, history):
        self.global_prior = self._mix(collections.Counter(r["grade"] for r in history))
        self.org = collections.defaultdict(collections.Counter)
        self.org_detector = collections.defaultdict(collections.Counter)
        by_detector = collections.defaultdict(collections.Counter)
        for r in history:
            self.org[r["org"]][r["grade"]] += 1
            self.org_detector[(r["org"], r["o"]["detector"])][r["grade"]] += 1
            by_detector[r["o"]["detector"]][r["grade"]] += 1
        self.detector_history = {}
        for d, c in by_detector.items():
            n = sum(c.values())
            g, k = c.most_common(1)[0]
            self.detector_history[d] = ("little_history" if n < DETECTOR_MIN
                                        else f"mostly_{g}" if k / n >= DETECTOR_PURE else "mixed")
        counts = {p: collections.defaultdict(collections.Counter) for p in PROBES}
        for r in history:
            for p in PROBES:
                counts[p][self.facet(r, p)][r["grade"]] += 1
        self.tables = {}
        for p, by_o in counts.items():
            kept = sorted(by_o, key=lambda o: (-sum(by_o[o].values()), o))[:TOP_OUTCOMES]
            totals = {h: sum(by_o[o][h] for o in by_o) for h in GRADES}
            rows = {}
            for h in GRADES:
                row = {o: (by_o[o][h] + 1) / (totals[h] + len(kept) + 1) for o in kept}
                row["other"] = 1 - sum(row.values())
                rows[h] = row
            self.tables[p] = rows

    @staticmethod
    def _mix(counter):
        n = sum(counter[h] for h in GRADES)
        return {h: counter[h] / n for h in GRADES}

    def facet(self, incident, probe):
        """Raw facet value, with the detector id replaced by its grading history."""
        value = incident["o"][probe]
        if probe == "detector":
            return self.detector_history.get(value, "unseen_detector")
        return value

    def outcome(self, incident, probe):
        value = self.facet(incident, probe)
        return value if value in self.tables[probe][GRADES[0]] else "other"

    def org_prior(self, org):
        c = self.org.get(org)
        if not c:
            return dict(self.global_prior)
        n = sum(c.values())
        return {h: (c[h] + PRIOR_ALPHA * self.global_prior[h]) / (n + PRIOR_ALPHA) for h in GRADES}

    def cold_kind(self, incident):
        """'unseen' / 'mixed' for cold-start incidents, None when history decides it."""
        c = self.org_detector.get((incident["org"], incident["o"]["detector"]))
        if not c:
            return "unseen"
        n = sum(c.values())
        return "mixed" if n >= COLD_MIN and c.most_common(1)[0][1] / n < COLD_PURE else None

    def history_verdict(self, incident):
        c = self.org_detector.get((incident["org"], incident["o"]["detector"]))
        if c:
            return c.most_common(1)[0][0]
        prior = self.org_prior(incident["org"])
        return max(GRADES, key=lambda h: prior[h])

    def actions(self):
        return [Action(p, TARGET, f"reveal {p}", cost, self.tables[p], prediction_source="guide_history_counts",
                       description=desc) for p, (cost, desc) in PROBES.items()]


class GuideTriageEnvironment:
    """One incident. The grade is held here and only reaches the planner through ``verify``."""

    label = LABEL
    hypotheses = GRADES

    def __init__(self, incident, model):
        self._incident, self._model = incident, model
        self._catalog = {a.id: a for a in model.actions()}
        self._observations = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        pass

    def catalog(self):
        return list(self._catalog.values())

    def priors(self):
        return self._model.org_prior(self._incident["org"])

    def describe(self):
        return {
            "environment": LABEL,
            "objective": ("Triage one security incident from a real organisation's XDR queue: decide whether it is "
                          "a true positive, a benign positive, or a false positive."),
            "initial_observation": ("A new incident was raised by a detector this organisation has no consistent "
                                    "grading history for. The ledger's starting scores are this organisation's "
                                    "historical grade mix."),
            "allowed_targets": [TARGET],
            "answer_options": dict(ANSWERS),
            "finish_rule": "Cite 1-3 observation IDs whose facets support the grade.",
        }

    def state(self):
        return {"case": f"{self._incident['org']}/{self._incident['incident']}", "version": 0}

    def execute(self, action):
        known = self._catalog.get(action.id)
        if known is None or (known.target, known.purpose, known.cost) != (action.target, action.purpose, action.cost):
            raise ValueError("Only catalogued GUIDE probes are allowed")
        outcome = self._model.outcome(self._incident, action.id)
        obs = Observation(f"o{len(self._observations) + 1:04d}", action.id, 0, outcome,
                          {"probe": action.id}, f"{action.id} = {outcome}")
        self._observations[obs.id] = obs
        return obs

    def verify(self, hypothesis, evidence_ids):
        return hypothesis == self._incident["grade"]
