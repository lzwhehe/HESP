"""Task family ``comp-triage`` (v1.2): composite evidence, overlapping outcomes, and paired attack/admin causes.

Written in response to review (2026-09-29): in sec-triage and sigma-triage every cause has an observation that
only it produces, and outcomes are (nearly) deterministic. Here each scenario pairs an attack with legitimate
activity that uses the same tools, outcomes are probabilistic, and several causes have NO single-observation
signature: only a combination of observations separates them. The probe catalogue and outcome vocabulary are
those of sigma-triage (generic SOC questions); the outcome distributions below were written by the authors
before any v1.2 episode ran and are frozen with the v1.2 protocol.

Variants: base (no transient failures) and noise (15 % transient HTTP 503).
"""

from .sandbox import LoopbackSandbox
from .sigmaapp import NOTES, PATH, PROBES, VOCAB

# scenario -> cause -> probe -> {outcome: probability}; causes starting with "attack" require action.
SCENARIOS = {
    "remote_exec": {
        "title": "Remote service creation with an administration tool on a server",
        "causes": {
            "attack_lateral": "An intruder moving laterally with a remote-execution tool and stolen administrator credentials.",
            "admin_maintenance": "An IT administrator using the same remote-execution tool for maintenance.",
            "authorized_pentest": "An authorized penetration test using the same tool.",
            "deployment_agent": "The software-deployment agent installing a package.",
        },
        "outcomes": {
            "attack_lateral": {
                "actor_account": {"admin_user": 0.7, "standard_user": 0.3},
                "logon_origin": {"unusual_host": 0.8, "managed_admin_host": 0.2},
                "change_record": {"none": 0.95, "approved_change": 0.05},
                "software_approval": {"approved": 0.6, "not_approved": 0.4},
                "binary_reputation": {"signed_known_vendor": 0.9, "unsigned_or_renamed": 0.1},
                "prevalence": {"rare_first_seen": 0.7, "fleet_wide_routine": 0.3},
                "parent_process": {"interactive_shell": 0.9, "system_service": 0.1},
                "time_context": {"off_hours": 0.6, "business_hours": 0.4},
                "follow_on": {"lateral_movement": 0.5, "credential_access": 0.3, "none": 0.2},
                "threat_intel": {"malicious": 0.3, "clean": 0.7},
            },
            "admin_maintenance": {
                "actor_account": {"admin_user": 1.0},
                "logon_origin": {"managed_admin_host": 0.9, "unusual_host": 0.1},
                "change_record": {"approved_change": 0.7, "none": 0.3},
                "software_approval": {"approved": 1.0},
                "binary_reputation": {"signed_known_vendor": 1.0},
                "prevalence": {"fleet_wide_routine": 0.6, "rare_first_seen": 0.4},
                "parent_process": {"interactive_shell": 1.0},
                "time_context": {"maintenance_window": 0.5, "business_hours": 0.4, "off_hours": 0.1},
                "follow_on": {"none": 0.9, "lateral_movement": 0.1},
                "threat_intel": {"clean": 1.0},
            },
            "authorized_pentest": {
                "actor_account": {"admin_user": 0.5, "standard_user": 0.5},
                "logon_origin": {"unusual_host": 0.9, "managed_admin_host": 0.1},
                "change_record": {"approved_change": 0.9, "none": 0.1},
                "software_approval": {"not_approved": 0.6, "approved": 0.4},
                "binary_reputation": {"signed_known_vendor": 0.6, "unsigned_or_renamed": 0.4},
                "prevalence": {"rare_first_seen": 0.9, "fleet_wide_routine": 0.1},
                "parent_process": {"interactive_shell": 1.0},
                "time_context": {"business_hours": 0.8, "off_hours": 0.2},
                "follow_on": {"lateral_movement": 0.5, "credential_access": 0.4, "none": 0.1},
                "threat_intel": {"clean": 0.9, "malicious": 0.1},
            },
            "deployment_agent": {
                "actor_account": {"system_or_service": 1.0},
                "logon_origin": {"no_logon": 1.0},
                "change_record": {"approved_change": 0.6, "none": 0.4},
                "software_approval": {"approved": 1.0},
                "binary_reputation": {"signed_known_vendor": 1.0},
                "prevalence": {"fleet_wide_routine": 1.0},
                "parent_process": {"management_agent": 1.0},
                "time_context": {"maintenance_window": 0.7, "business_hours": 0.3},
                "follow_on": {"none": 1.0},
                "threat_intel": {"clean": 1.0},
            },
        },
    },
    "scheduled_task": {
        "title": "A scheduled task created by a user account on a workstation",
        "causes": {
            "attack_persistence": "An intruder creating a scheduled task for persistence.",
            "it_automation": "An IT automation script creating a scheduled maintenance task.",
            "software_updater": "A legitimate application's updater registering its update task.",
            "helpdesk_remote": "A helpdesk technician creating the task during a remote-assistance session.",
        },
        "outcomes": {
            "attack_persistence": {
                "actor_account": {"standard_user": 0.6, "admin_user": 0.4},
                "logon_origin": {"unusual_host": 0.6, "local_console": 0.4},
                "change_record": {"none": 1.0},
                "software_approval": {"not_approved": 0.7, "approved": 0.3},
                "binary_reputation": {"unsigned_or_renamed": 0.7, "signed_known_vendor": 0.3},
                "prevalence": {"rare_first_seen": 1.0},
                "parent_process": {"interactive_shell": 0.6, "office_or_browser": 0.4},
                "time_context": {"off_hours": 0.5, "business_hours": 0.5},
                "follow_on": {"persistence": 0.5, "credential_access": 0.3, "none": 0.2},
                "threat_intel": {"malicious": 0.4, "clean": 0.6},
            },
            "it_automation": {
                "actor_account": {"admin_user": 0.6, "system_or_service": 0.4},
                "logon_origin": {"managed_admin_host": 0.7, "no_logon": 0.3},
                "change_record": {"approved_change": 0.8, "none": 0.2},
                "software_approval": {"approved": 1.0},
                "binary_reputation": {"signed_known_vendor": 0.8, "unsigned_or_renamed": 0.2},
                "prevalence": {"fleet_wide_routine": 0.8, "rare_first_seen": 0.2},
                "parent_process": {"interactive_shell": 0.5, "management_agent": 0.5},
                "time_context": {"maintenance_window": 0.6, "business_hours": 0.4},
                "follow_on": {"none": 1.0},
                "threat_intel": {"clean": 1.0},
            },
            "software_updater": {
                "actor_account": {"standard_user": 0.7, "system_or_service": 0.3},
                "logon_origin": {"local_console": 0.7, "no_logon": 0.3},
                "change_record": {"none": 1.0},
                "software_approval": {"approved": 0.9, "not_approved": 0.1},
                "binary_reputation": {"signed_known_vendor": 1.0},
                "prevalence": {"fleet_wide_routine": 0.9, "rare_first_seen": 0.1},
                "parent_process": {"office_or_browser": 0.6, "system_service": 0.4},
                "time_context": {"business_hours": 0.8, "off_hours": 0.2},
                "follow_on": {"none": 1.0},
                "threat_intel": {"clean": 1.0},
            },
            "helpdesk_remote": {
                "actor_account": {"admin_user": 0.8, "standard_user": 0.2},
                "logon_origin": {"unusual_host": 0.5, "managed_admin_host": 0.5},
                "change_record": {"none": 0.6, "approved_change": 0.4},
                "software_approval": {"approved": 0.8, "not_approved": 0.2},
                "binary_reputation": {"signed_known_vendor": 0.9, "unsigned_or_renamed": 0.1},
                "prevalence": {"rare_first_seen": 0.6, "fleet_wide_routine": 0.4},
                "parent_process": {"interactive_shell": 1.0},
                "time_context": {"business_hours": 1.0},
                "follow_on": {"none": 0.9, "persistence": 0.1},
                "threat_intel": {"clean": 1.0},
            },
        },
    },
    "outbound_transfer": {
        "title": "A large outbound data transfer from a file server",
        "causes": {
            "attack_exfil": "An intruder staging and exfiltrating data.",
            "backup_job": "The scheduled off-site backup job.",
            "cloud_sync": "A user's approved cloud-storage client synchronizing a folder.",
            "authorized_migration": "An approved data migration to a new provider.",
        },
        "outcomes": {
            "attack_exfil": {
                "actor_account": {"standard_user": 0.5, "admin_user": 0.5},
                "logon_origin": {"unusual_host": 0.7, "local_console": 0.3},
                "change_record": {"none": 1.0},
                "software_approval": {"not_approved": 0.5, "approved": 0.5},
                "binary_reputation": {"signed_known_vendor": 0.5, "unsigned_or_renamed": 0.5},
                "prevalence": {"rare_first_seen": 0.9, "fleet_wide_routine": 0.1},
                "parent_process": {"interactive_shell": 0.8, "office_or_browser": 0.2},
                "time_context": {"off_hours": 0.7, "business_hours": 0.3},
                "follow_on": {"data_staging": 0.6, "none": 0.4},
                "threat_intel": {"malicious": 0.4, "clean": 0.6},
            },
            "backup_job": {
                "actor_account": {"system_or_service": 1.0},
                "logon_origin": {"no_logon": 1.0},
                "change_record": {"none": 0.7, "approved_change": 0.3},
                "software_approval": {"approved": 1.0},
                "binary_reputation": {"signed_known_vendor": 1.0},
                "prevalence": {"fleet_wide_routine": 1.0},
                "parent_process": {"system_service": 1.0},
                "time_context": {"off_hours": 0.6, "maintenance_window": 0.4},
                "follow_on": {"none": 1.0},
                "threat_intel": {"clean": 1.0},
            },
            "cloud_sync": {
                "actor_account": {"standard_user": 1.0},
                "logon_origin": {"local_console": 0.9, "unusual_host": 0.1},
                "change_record": {"none": 1.0},
                "software_approval": {"approved": 0.9, "not_approved": 0.1},
                "binary_reputation": {"signed_known_vendor": 1.0},
                "prevalence": {"fleet_wide_routine": 0.7, "rare_first_seen": 0.3},
                "parent_process": {"office_or_browser": 0.5, "system_service": 0.5},
                "time_context": {"business_hours": 0.8, "off_hours": 0.2},
                "follow_on": {"none": 0.8, "data_staging": 0.2},
                "threat_intel": {"clean": 1.0},
            },
            "authorized_migration": {
                "actor_account": {"admin_user": 1.0},
                "logon_origin": {"managed_admin_host": 0.6, "unusual_host": 0.4},
                "change_record": {"approved_change": 0.9, "none": 0.1},
                "software_approval": {"approved": 0.7, "not_approved": 0.3},
                "binary_reputation": {"signed_known_vendor": 0.8, "unsigned_or_renamed": 0.2},
                "prevalence": {"rare_first_seen": 0.8, "fleet_wide_routine": 0.2},
                "parent_process": {"interactive_shell": 1.0},
                "time_context": {"maintenance_window": 0.5, "off_hours": 0.5},
                "follow_on": {"data_staging": 0.7, "none": 0.3},
                "threat_intel": {"clean": 0.9, "malicious": 0.1},
            },
        },
    },
}
VARIANTS = {"base": {"lag": 0.0, "transient": 0.0, "drift_after": None},
            "noise": {"lag": 0.0, "transient": 0.15, "drift_after": None}}


def signatures(outcomes):
    """(probe, outcome) pairs that only one named cause can produce (probability > 0 under exactly one)."""
    sig = {c: set() for c in outcomes}
    for c, rows in outcomes.items():
        for a, dist in rows.items():
            for o, p in dist.items():
                if p > 0 and all(outcomes[d][a].get(o, 0.0) == 0.0 for d in outcomes if d != c):
                    sig[c].add((a, o))
    return sig


def validate(scenario):
    errors = []
    for c, rows in scenario["outcomes"].items():
        if set(rows) != set(VOCAB):
            errors.append(f"{c}: probes must be exactly the sigma catalogue")
        for a, dist in rows.items():
            if abs(sum(dist.values()) - 1.0) > 1e-9 or any(o not in VOCAB[a] for o in dist):
                errors.append(f"{c}/{a}: not a distribution over the vocabulary")
    return errors


def make_family(name):
    scenario = SCENARIOS[name]
    errors = validate(scenario)
    if errors:
        raise ValueError("; ".join(errors))
    out = scenario["outcomes"]

    def true_outcome_distribution(probe_id, cause, lag):
        if cause == "other":
            return {o: 1.0 / len(VOCAB[probe_id]) for o in VOCAB[probe_id]}
        return dict(out[cause][probe_id])

    def respond(cause, method, path, rng, v):
        pid = PATH.get(path)
        if pid is None:
            return 404, {"error": "not found"}
        dist = out[cause][pid]
        r, acc, o = rng.random(), 0.0, None
        for outcome, p in sorted(dist.items()):
            acc += p
            if r < acc:
                o = outcome
                break
        o = o or sorted(dist)[-1]
        return 200, {"probe": pid, "finding": o, "detail": NOTES[pid][o]}

    def classify(probe_id, status, body):
        if status != 200 or not isinstance(body, dict):
            return None
        return body.get("finding") if body.get("finding") in VOCAB[probe_id] else None

    task = {"objective": (f"Triage the alert \"{scenario['title']}\": determine which of the explanations below "
                          "caused it."),
            "initial_observation": f"Alert: {scenario['title']}."}
    return type(f"Comp_{name}", (LoopbackSandbox,), {
        "family": "comp-triage", "TARGET": f"sandbox://comp/{name}", "CAUSES": tuple(scenario["causes"]),
        "DESCRIPTIONS": {**scenario["causes"], "other": "Some cause not listed here."},
        "PROBES": [{**p} for p in PROBES], "VARIANTS": VARIANTS, "TABLE_LAG": 0.0,
        "NOISE_EXEMPT": frozenset(), "SIGNATURES": signatures(out),
        "BENIGN": frozenset(c for c in scenario["causes"] if not c.startswith("attack")),
        "STATE_FIELDS": {"analyst": "on-call", "scenario": name},
        "respond": staticmethod(respond), "classify": staticmethod(classify),
        "true_outcome_distribution": staticmethod(true_outcome_distribution),
        "public_task": classmethod(lambda cls: dict(task)),
    })


def comp_suite(variants=("base", "noise")):
    tasks = []
    for s, name in enumerate(SCENARIOS):
        for variant in variants:
            for c, cause in enumerate(SCENARIOS[name]["causes"]):
                tasks.append({"task_id": f"cmp{s:02d}-{variant}-{c}", "family": "comp-triage", "scenario": name,
                              "variant": variant, "cause": cause, "drift_to": None})
    return tasks


class CompEnvironments:
    def __init__(self):
        self.classes = {name: make_family(name) for name in SCENARIOS}

    def __call__(self, task, seed):
        return self.classes[task["scenario"]](task["cause"], task["variant"], seed)
