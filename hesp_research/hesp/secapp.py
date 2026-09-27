"""Task family ``sec-triage`` (v0.5): a blue-team analyst triages one security alert.

A SOC/security-maintenance analyst is paged about anomalous activity on a web service
(case INC-4271) and must determine its TRUE nature among competing verdicts -- a real
attack of some type, a misconfiguration, an authorized activity, or a false positive --
using read-only investigation probes, each of which costs analyst time. This is a
*diagnosis* task (defensive), not exploitation: the agent never sends attack payloads,
only queries SIEM/config/inventory/threat-intel views.

Design notes (mirrors upload-diag, structurally different from it):
- Threat-intel enrichment (cost 3) tells you *whether* the top indicator is malicious,
  but three different real attacks all enrich to "malicious_campaign", so TI alone never
  identifies which attack -- you still need the specific per-cause signal. Elimination or
  a bare "it's malicious" does not pass the verifier.
- Every outcome that a single cause produces uniquely is a valid confirmation of it; only
  the shared outcomes (a malicious TI verdict, or the many benign/"normal" branches) are
  suggestive-but-not-confirmatory. Several causes have more than one confirming signal
  (e.g. an authorized scan shows both a scanner ASN and a change ticket).

Variants
  base   deterministic; the threat-intel feed is not yet enriched with prob 0.10
  noise  15% transient HTTP 503 on any SIEM query except the runbook; TI lag 0.30
  drift  after the second probe the incident is superseded: the state version advances
         and the true dominant cause switches.
"""

from .sandbox import LoopbackSandbox, probe, suite

TARGET = "sandbox://soc-console"
CAUSES = ("credential_stuffing", "sqli_probe", "misconfig_exposed_admin", "authorized_scan",
          "false_positive_monitor", "insider_exfil", "vuln_component", "dns_c2")
HYPOTHESES = CAUSES + ("other",)
DESCRIPTIONS = {
    "credential_stuffing": "A real credential-stuffing attack: distributed failed logins across many accounts from many source IPs.",
    "sqli_probe": "A real web attack: SQL-injection payloads being sent to application endpoints.",
    "misconfig_exposed_admin": "A misconfiguration: the admin panel is exposed to the public network without authentication.",
    "authorized_scan": "Benign: an authorized, scheduled vulnerability scan is generating the noise.",
    "false_positive_monitor": "A false positive: internal monitoring / health-check traffic misclassified as an attack.",
    "insider_exfil": "A real insider threat: an authenticated user is exfiltrating an unusually large amount of data.",
    "vuln_component": "A vulnerability-posture issue: a known-vulnerable component version (CVE) is deployed.",
    "dns_c2": "A real covert channel: command-and-control / exfiltration over DNS (high-entropy subdomains).",
    "other": "Some cause not listed here.",
}
VARIANTS = {
    "base": {"lag": 0.10, "transient": 0.0, "drift_after": None},
    "noise": {"lag": 0.30, "transient": 0.15, "drift_after": None},
    "drift": {"lag": 0.10, "transient": 0.0, "drift_after": 2},
}
TABLE_LAG = 0.15
MALICIOUS = frozenset({"credential_stuffing", "sqli_probe", "dns_c2"})

PROBES = [
    probe("auth_log", "GET", "/siem/auth?window=1h", 1, "Read the authentication-failure pattern in the last hour.",
          {"distributed_failures": "200, many accounts failing from many source IPs", "none": "200, baseline auth failures"}),
    probe("access_pattern", "GET", "/siem/http?window=1h", 1, "Read the dominant HTTP request pattern.",
          {"sqli_payloads": "200, SQL-injection payloads seen", "path_scanning": "200, systematic path enumeration",
           "large_response": "200, unusually large responses", "normal": "200, nothing unusual"}),
    probe("source_ips", "GET", "/siem/sources?window=1h", 1, "Read the reputation of the top traffic sources.",
          {"many_residential": "200, many residential/botnet IPs", "known_scanner_asn": "200, a known scanner ASN",
           "monitoring_range": "200, the internal monitoring range", "internal_host": "200, a single internal host",
           "normal": "200, mixed normal traffic"}),
    probe("admin_exposure", "GET", "/config/admin", 1, "Read the admin panel's exposure configuration.",
          {"protected": "200, auth required and VPN-only", "exposed_no_auth": "200, public with no auth"}),
    probe("user_activity", "GET", "/siem/egress?window=24h", 2, "Read per-user data egress over 24h (slower query).",
          {"normal": "200, egress within baseline", "one_user_spike": "200, one user far above baseline"}),
    probe("dns_logs", "GET", "/siem/dns?window=1h", 2, "Read DNS query characteristics (slower query).",
          {"normal": "200, low-entropy DNS", "high_entropy": "200, high-entropy subdomains, high NXDOMAIN"}),
    probe("component_versions", "GET", "/inventory/components", 1, "Read the deployed component versions.",
          {"up_to_date": "200, no known CVE", "known_cve": "200, a version with a known CVE"}),
    probe("change_ticket", "GET", "/itsm/changes?window=24h", 1, "Check for an authorized change/maintenance window.",
          {"authorized_window": "200, an active authorized scan ticket", "none": "200, no relevant change ticket"}),
    probe("threat_intel", "GET", "/ti/enrich", 3, "Enrich the top indicator against threat intelligence (slow).",
          {"malicious_campaign": "200, matches a known malicious campaign", "benign_scanner": "200, a known benign scanner",
           "clean": "200, no reputation hit", "inconclusive": "200, not enriched yet"}),
    probe("runbook", "GET", "/runbook", 1, "Read the generic triage runbook.", {"generic": "200, generic guidance"}),
]


def true_outcome_distribution(probe_id, cause, lag):
    if cause == "other":
        cause = None
    if probe_id == "runbook":
        return {"generic": 1.0}
    if probe_id == "auth_log":
        return {"distributed_failures": 1.0} if cause == "credential_stuffing" else {"none": 1.0}
    if probe_id == "access_pattern":
        return {"sqli_payloads": 1.0} if cause == "sqli_probe" else (
            {"path_scanning": 1.0} if cause == "authorized_scan" else (
                {"large_response": 1.0} if cause == "insider_exfil" else {"normal": 1.0}))
    if probe_id == "source_ips":
        rep = {"credential_stuffing": "many_residential", "authorized_scan": "known_scanner_asn",
               "false_positive_monitor": "monitoring_range", "insider_exfil": "internal_host"}.get(cause, "normal")
        return {rep: 1.0}
    if probe_id == "admin_exposure":
        return {"exposed_no_auth": 1.0} if cause == "misconfig_exposed_admin" else {"protected": 1.0}
    if probe_id == "user_activity":
        return {"one_user_spike": 1.0} if cause == "insider_exfil" else {"normal": 1.0}
    if probe_id == "dns_logs":
        return {"high_entropy": 1.0} if cause == "dns_c2" else {"normal": 1.0}
    if probe_id == "component_versions":
        return {"known_cve": 1.0} if cause == "vuln_component" else {"up_to_date": 1.0}
    if probe_id == "change_ticket":
        return {"authorized_window": 1.0} if cause == "authorized_scan" else {"none": 1.0}
    if probe_id == "threat_intel":
        if cause in MALICIOUS:
            return {"malicious_campaign": 1.0 - lag, "inconclusive": lag}
        if cause == "authorized_scan":
            return {"benign_scanner": 1.0 - lag, "inconclusive": lag}
        return {"clean": 1.0}
    raise ValueError("unknown probe")


def respond(cause, method, path, rng, v):
    if path == "/runbook":
        return 200, {"text": "Correlate auth, http and source signals; enrich the top indicator; check change tickets."}
    if path == "/siem/auth?window=1h":
        if cause == "credential_stuffing":
            return 200, {"failed_logins": 4210, "distinct_accounts": 900, "distinct_source_ips": 780, "pattern": "distributed"}
        return 200, {"failed_logins": 3, "distinct_accounts": 2, "distinct_source_ips": 1, "pattern": "baseline"}
    if path == "/siem/http?window=1h":
        pat = {"sqli_probe": "sqli_payloads", "authorized_scan": "path_scanning",
               "insider_exfil": "large_response"}.get(cause, "normal")
        return 200, {"top_pattern": pat, "requests": 5200}
    if path == "/siem/sources?window=1h":
        rep = {"credential_stuffing": "residential_botnet", "authorized_scan": "known_scanner_asn",
               "false_positive_monitor": "monitoring_range", "insider_exfil": "internal_host"}.get(cause, "mixed_normal")
        return 200, {"reputation": rep}
    if path == "/config/admin":
        exposed = cause == "misconfig_exposed_admin"
        return 200, {"path": "/admin", "auth_required": not exposed, "network": "public" if exposed else "vpn_only"}
    if path == "/siem/egress?window=24h":
        if cause == "insider_exfil":
            return 200, {"top_user": "j.doe", "egress_mb": 41200, "baseline_mb": 300}
        return 200, {"top_user": "s.admin", "egress_mb": 280, "baseline_mb": 300}
    if path == "/siem/dns?window=1h":
        if cause == "dns_c2":
            return 200, {"max_subdomain_entropy": 4.7, "nxdomain_ratio": 0.62}
        return 200, {"max_subdomain_entropy": 2.1, "nxdomain_ratio": 0.03}
    if path == "/inventory/components":
        if cause == "vuln_component":
            return 200, {"component": "libweb", "version": "1.2.3", "known_cve": "CVE-2025-9999"}
        return 200, {"component": "libweb", "version": "1.4.0", "known_cve": None}
    if path == "/itsm/changes?window=24h":
        if cause == "authorized_scan":
            return 200, {"changes": [{"id": "CHG-88", "type": "authorized_vuln_scan", "active": True}]}
        return 200, {"changes": []}
    if path == "/ti/enrich":
        if cause in MALICIOUS and rng.random() >= v["lag"]:
            return 200, {"verdict": "malicious_campaign", "indicator": "top_source"}
        if cause == "authorized_scan" and rng.random() >= v["lag"]:
            return 200, {"verdict": "benign_scanner", "indicator": "top_source"}
        if cause in MALICIOUS or cause == "authorized_scan":
            return 200, {"verdict": "inconclusive", "indicator": "top_source"}
        return 200, {"verdict": "clean", "indicator": "top_source"}
    return 404, {"error": "not found"}


def classify(probe_id, status, body):
    if status != 200 or not isinstance(body, dict):
        return None
    if probe_id == "runbook":
        return "generic"
    if probe_id == "auth_log":
        return "distributed_failures" if body.get("pattern") == "distributed" else "none"
    if probe_id == "access_pattern":
        p = body.get("top_pattern")
        return p if p in {"sqli_payloads", "path_scanning", "large_response", "normal"} else None
    if probe_id == "source_ips":
        return {"residential_botnet": "many_residential", "known_scanner_asn": "known_scanner_asn",
                "monitoring_range": "monitoring_range", "internal_host": "internal_host",
                "mixed_normal": "normal"}.get(body.get("reputation"))
    if probe_id == "admin_exposure":
        return "protected" if body.get("auth_required") else "exposed_no_auth"
    if probe_id == "user_activity":
        return "one_user_spike" if body.get("egress_mb", 0) >= 5 * body.get("baseline_mb", 1) else "normal"
    if probe_id == "dns_logs":
        return "high_entropy" if body.get("max_subdomain_entropy", 0) >= 4.0 else "normal"
    if probe_id == "component_versions":
        return "known_cve" if body.get("known_cve") else "up_to_date"
    if probe_id == "change_ticket":
        changes = body.get("changes") or []
        return "authorized_window" if any(c.get("type") == "authorized_vuln_scan" and c.get("active")
                                          for c in changes) else "none"
    if probe_id == "threat_intel":
        return {"malicious_campaign": "malicious_campaign", "benign_scanner": "benign_scanner",
                "clean": "clean", "inconclusive": "inconclusive"}.get(body.get("verdict"))
    return None


# A bare "it's malicious" (shared by three attacks) is deliberately NOT a signature:
# the analyst must find the specific signal, not just confirm maliciousness. Every
# per-cause-unique outcome below IS a valid signature (see module docstring).
SIGNATURES = {
    "credential_stuffing": {("auth_log", "distributed_failures"), ("source_ips", "many_residential")},
    "sqli_probe": {("access_pattern", "sqli_payloads")},
    "misconfig_exposed_admin": {("admin_exposure", "exposed_no_auth")},
    "authorized_scan": {("change_ticket", "authorized_window"), ("threat_intel", "benign_scanner"),
                        ("access_pattern", "path_scanning"), ("source_ips", "known_scanner_asn")},
    "false_positive_monitor": {("source_ips", "monitoring_range")},
    "insider_exfil": {("user_activity", "one_user_spike"), ("access_pattern", "large_response"),
                      ("source_ips", "internal_host")},
    "vuln_component": {("component_versions", "known_cve")},
    "dns_c2": {("dns_logs", "high_entropy")},
}


class SecTriageEnvironment(LoopbackSandbox):
    """One episode of the security-alert-triage family. Use as a context manager."""
    family = "sec-triage"
    TARGET = TARGET
    CAUSES = CAUSES
    DESCRIPTIONS = DESCRIPTIONS
    PROBES = PROBES
    VARIANTS = VARIANTS
    TABLE_LAG = TABLE_LAG
    NOISE_EXEMPT = frozenset({"/runbook"})
    SIGNATURES = SIGNATURES
    STATE_FIELDS = {"analyst": "on-call", "case": "INC-4271"}
    respond = staticmethod(respond)
    classify = staticmethod(classify)
    true_outcome_distribution = staticmethod(true_outcome_distribution)

    @classmethod
    def public_task(cls):
        return {"objective": "Triage security alert INC-4271 on a local test web service: determine the true "
                             "nature of the anomalous activity (a specific attack, a misconfiguration, an "
                             "authorized activity, or a false positive)",
                "initial_observation": "Alert: spike in authentication failures and 4xx/5xx errors on the web "
                                       "tier over the last hour"}


def sec_suite(variants=("base", "drift", "noise")):
    return suite(SecTriageEnvironment, "sec", variants)


def make_sec_env(task, seed):
    return SecTriageEnvironment(task["cause"], task["variant"], seed, task.get("drift_to"))
