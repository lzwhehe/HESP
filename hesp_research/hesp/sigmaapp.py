"""Task family ``sigma-triage`` (v1.0 part A): alerts and candidate causes taken from SigmaHQ rules.

Each task is one Sigma detection rule firing. The candidate causes are NOT written by us: the
attack explanation is the rule's own title and ATT&CK technique, and the benign explanations are
the rule author's ``falsepositives`` entries, verbatim. The probe catalogue below is a fixed set of
generic SOC investigation questions, written before any rule was sampled and shared by all rules.
Which outcome each probe returns under each cause comes from a frozen annotation (one JSON spec per
rule, see scripts/v10a_*.py), never from the controller or the planner.

A spec (validated by ``validate_spec``)::

    {"rule_id", "slug", "title", "description", "technique", "logsource",
     "causes": {"attack": text, "benign_1": text, ...},
     "outcomes": {cause: {probe_id: outcome}}}

Variants: base (threat-intel lag 0.10) and noise (15 % transient 503 on every probe, lag 0.30).
A threat-intel answer of "malicious" is replaced by "inconclusive" with the lag probability.
"""

from .sandbox import LoopbackSandbox, probe

PROBES = [
    probe("actor_account", "GET", "/edr/actor", 1, "Which account performed the activity.",
          {"system_or_service": "200, SYSTEM, a machine account or a service account",
           "admin_user": "200, a named administrator account", "standard_user": "200, a standard user account",
           "unattributed": "200, no attributable account"}),
    probe("logon_origin", "GET", "/edr/logon", 1, "Origin of the logon session that performed the activity.",
          {"local_console": "200, a local interactive session", "managed_admin_host": "200, a network logon from a managed administration host",
           "unusual_host": "200, a network logon from an unusual or external host", "no_logon": "200, no user logon (service or scheduled context)"}),
    probe("change_record", "GET", "/itsm/changes", 1, "Look for an approved change or maintenance ticket covering the activity.",
          {"approved_change": "200, an approved change ticket covers it", "none": "200, no matching ticket"}),
    probe("software_approval", "GET", "/inventory/software", 1, "Check whether the tool involved is on the approved-software list or deployed by IT.",
          {"approved": "200, approved or deployed by IT", "not_approved": "200, not approved and not deployed by IT"}),
    probe("binary_reputation", "GET", "/edr/binary", 2, "Check the signature and name of the executable involved (slower query).",
          {"signed_known_vendor": "200, signed by a known vendor, expected name and path", "unsigned_or_renamed": "200, unsigned, renamed or in an unusual path"}),
    probe("prevalence", "GET", "/edr/prevalence", 2, "How common this exact activity is across the fleet (slower query).",
          {"fleet_wide_routine": "200, seen routinely on many hosts", "rare_first_seen": "200, first seen or seen on this host only"}),
    probe("parent_process", "GET", "/edr/parent", 1, "The process that launched the activity.",
          {"management_agent": "200, a deployment, update or management agent", "interactive_shell": "200, a user shell or script host",
           "office_or_browser": "200, an office application or web browser", "system_service": "200, an operating-system service"}),
    probe("time_context", "GET", "/edr/time", 1, "When the activity happened relative to schedules.",
          {"maintenance_window": "200, inside a maintenance window", "business_hours": "200, normal business hours",
           "off_hours": "200, outside business hours and maintenance windows"}),
    probe("follow_on", "GET", "/edr/follow_on", 2, "Activity by the same actor in the following hour (slower query).",
          {"none": "200, nothing notable", "credential_access": "200, credential access", "lateral_movement": "200, lateral movement",
           "data_staging": "200, data collection or staging", "persistence": "200, a persistence mechanism created"}),
    probe("threat_intel", "GET", "/ti/enrich", 3, "Enrich the artifacts against threat intelligence (slow).",
          {"malicious": "200, matches known malicious infrastructure or malware", "clean": "200, no reputation hit",
           "inconclusive": "200, not enriched yet"}),
]
PROBE_IDS = [p["id"] for p in PROBES]
VOCAB = {p["id"]: list(p["outcome_notes"]) for p in PROBES}
NOTES = {p["id"]: dict(p["outcome_notes"]) for p in PROBES}
PATH = {p["path"]: p["id"] for p in PROBES}
VARIANTS = {"base": {"lag": 0.10, "transient": 0.0, "drift_after": None},
            "noise": {"lag": 0.30, "transient": 0.15, "drift_after": None}}
MAX_BENIGN = 4


def signatures(spec):
    """(probe, outcome) pairs that exactly one named cause produces, per cause."""
    out = spec["outcomes"]
    sig = {c: set() for c in out}
    for a in PROBE_IDS:
        for c in out:
            if all(out[c][a] != out[d][a] for d in out if d != c):
                sig[c].add((a, out[c][a]))
    return sig


def validate_spec(spec):
    """Reasons a spec is unusable (empty list if usable): schema, vocabulary, identifiability."""
    errors = []
    causes = spec.get("causes") or {}
    if "attack" not in causes or not 1 <= len(causes) - 1 <= MAX_BENIGN:
        errors.append("needs one attack cause and 1-4 benign causes")
    if set(causes) != {"attack", *[f"benign_{i}" for i in range(1, len(causes))]}:
        errors.append("cause ids must be attack, benign_1..benign_n")
    out = spec.get("outcomes") or {}
    if set(out) != set(causes):
        errors.append("outcomes must cover exactly the causes")
        return errors
    for c, row in out.items():
        for a in PROBE_IDS:
            if row.get(a) not in VOCAB[a]:
                errors.append(f"{c}/{a}: outcome {row.get(a)!r} not in vocabulary")
    if errors:
        return errors
    vectors = [tuple(out[c][a] for a in PROBE_IDS) for c in out]
    if len(set(vectors)) != len(vectors):
        errors.append("two causes have identical outcome vectors")
    for c, s in signatures(spec).items():
        if not s:
            errors.append(f"{c} has no signature (no outcome unique to it)")
    return errors


def make_family(spec):
    """Environment class for one rule's spec (validated)."""
    errors = validate_spec(spec)
    if errors:
        raise ValueError("; ".join(errors))
    out = spec["outcomes"]
    target = f"sandbox://sigma/{spec['slug']}"

    def true_outcome_distribution(probe_id, cause, lag):
        if cause == "other":
            return {o: 1.0 / len(VOCAB[probe_id]) for o in VOCAB[probe_id]}
        o = out[cause][probe_id]
        if probe_id == "threat_intel" and o == "malicious":
            return {"malicious": 1.0 - lag, "inconclusive": lag}
        return {o: 1.0}

    def respond(cause, method, path, rng, v):
        pid = PATH.get(path)
        if pid is None:
            return 404, {"error": "not found"}
        o = out[cause][pid]
        if pid == "threat_intel" and o == "malicious" and rng.random() < v["lag"]:
            o = "inconclusive"
        return 200, {"probe": pid, "finding": o, "detail": NOTES[pid][o]}

    def classify(probe_id, status, body):
        if status != 200 or not isinstance(body, dict):
            return None
        return body.get("finding") if body.get("finding") in VOCAB[probe_id] else None

    task = {"objective": (f"Triage the alert raised by the detection rule \"{spec['title']}\": determine whether it is "
                          "the attack the rule targets or one of the benign explanations listed below."),
            "initial_observation": f"Alert: {spec['title']}. {spec['description']}".strip()}
    return type(f"Sigma_{spec['slug']}", (LoopbackSandbox,), {
        "family": "sigma-triage", "TARGET": target, "CAUSES": tuple(spec["causes"]),
        "DESCRIPTIONS": {**spec["causes"], "other": "Some cause not listed here."},
        "PROBES": [{**p} for p in PROBES], "VARIANTS": VARIANTS, "TABLE_LAG": 0.15,
        "NOISE_EXEMPT": frozenset(), "SIGNATURES": signatures(spec),
        "BENIGN": frozenset(c for c in spec["causes"] if c != "attack"),
        "STATE_FIELDS": {"analyst": "on-call", "rule": spec["rule_id"]},
        "respond": staticmethod(respond), "classify": staticmethod(classify),
        "true_outcome_distribution": staticmethod(true_outcome_distribution),
        "public_task": classmethod(lambda cls: dict(task)),
    })


def sigma_suite(specs, variants=("base", "noise")):
    """Tasks: every (rule, cause, variant). ``specs`` is an ordered list of validated specs."""
    tasks = []
    for r, spec in enumerate(specs):
        for variant in variants:
            for c, cause in enumerate(spec["causes"]):
                tasks.append({"task_id": f"sig{r:02d}-{variant}-{c}", "family": "sigma-triage", "rule": spec["slug"],
                              "variant": variant, "cause": cause, "drift_to": None})
    return tasks


class SigmaEnvironments:
    """Factory: one environment class per rule, built once from the frozen specs."""

    def __init__(self, specs):
        self.classes = {s["slug"]: make_family(s) for s in specs}

    def __call__(self, task, seed):
        return self.classes[task["rule"]](task["cause"], task["variant"], seed)


class RuleTablePredictor:
    """Per-rule frozen tables, selected by the action's (rule-specific) target."""

    def __init__(self, tables_by_slug, source):
        self.tables, self.source = tables_by_slug, source

    def likelihoods(self, action, hypotheses):
        return self.tables[action.target.rsplit("/", 1)[1]][action.id]
