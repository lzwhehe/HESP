"""Task family ``web-diag`` (v0.3): why can't alice save document #42?

A tiny document-management app on the shared loopback sandbox (``hesp/sandbox.py``).
One hidden fault makes ``POST /documents/42/save`` fail; the agent may only send the
fixed read-only probes below. This family was used during v0.3 development and serves
as the *development* family from v0.4 on.

Variants
  base   deterministic responses; the audit log lags with probability 0.10
  noise  15% transient HTTP 503 on any probe (invalid observation, retry allowed);
         audit lag 0.30
  drift  like base, but after the second tool call another user changes the document,
         the business-state version advances and the hidden fault switches.
"""

from .sandbox import EPS, LABEL, LoopbackSandbox, probe, suite

TARGET = "sandbox://docs-app"
CAUSES = ("session_expired", "role_readonly", "owner_policy", "document_archived",
          "workflow_locked", "quota_exceeded", "edit_conflict", "feature_disabled")
HYPOTHESES = CAUSES + ("other",)
DESCRIPTIONS = {
    "session_expired": "The user's session token has expired; the server no longer authenticates the request.",
    "role_readonly": "The user is authenticated but currently holds a read-only (viewer) role.",
    "owner_policy": "An ownership/ACL policy forbids this user from writing a document owned by someone else.",
    "document_archived": "The document is archived and therefore immutable.",
    "workflow_locked": "The document is locked by an approval workflow held by another user.",
    "quota_exceeded": "The user's storage quota is exhausted, so new revisions are refused.",
    "edit_conflict": "The user's local copy is based on a stale revision; saving would overwrite a concurrent edit.",
    "feature_disabled": "Document editing is switched off by a feature flag for this workspace.",
    "other": "Some cause not listed here.",
}
AUDIT_CODES = {
    "role_readonly": "ROLE_READONLY", "owner_policy": "ACL_OWNER_MISMATCH",
    "document_archived": "DOC_ARCHIVED", "workflow_locked": "WF_LOCK_HELD",
    "quota_exceeded": "QUOTA_LIMIT", "edit_conflict": "BASE_REV_STALE",
    "feature_disabled": "FEATURE_OFF",
}
CODE_TO_CAUSE = {v: k for k, v in AUDIT_CODES.items()}
VARIANTS = {
    "base": {"audit_lag": 0.10, "lag": 0.10, "transient": 0.0, "drift_after": None},
    "noise": {"audit_lag": 0.30, "lag": 0.30, "transient": 0.15, "drift_after": None},
    "drift": {"audit_lag": 0.10, "lag": 0.10, "transient": 0.0, "drift_after": 2},
}
# Designer's predictive model assumes one lag rate for every variant (it is not told the variant).
TABLE_AUDIT_LAG = 0.15

PROBES = [
    probe("whoami", "GET", "/whoami", 1, "Show the authenticated user and current role.",
          {"editor": "200, role=editor", "viewer": "200, role=viewer", "unauthorized": "401"}),
    probe("doc_meta", "GET", "/documents/42", 1, "Read document #42 metadata (owner, status).",
          {"own_active": "200, owned by the user, status active", "owner_other": "200, owned by another user",
           "archived": "200, status archived", "unauthorized": "401"}),
    probe("workflow", "GET", "/workflow/42", 1, "Read the approval-workflow state of document #42.",
          {"open": "200, no lock", "locked": "200, lock held by another user", "unauthorized": "401"}),
    probe("quota", "GET", "/quota", 1, "Read the user's storage quota.",
          {"ok": "200, usage below limit", "exceeded": "200, usage at limit", "unauthorized": "401"}),
    probe("features", "GET", "/features", 1, "Read workspace feature flags.",
          {"editing_on": "200, doc_editing=true", "editing_off": "200, doc_editing=false",
           "unauthorized": "401"}),
    probe("versions", "GET", "/documents/42/versions", 1, "Compare the user's base revision with the head.",
          {"consistent": "200, base equals head", "concurrent_edit": "200, head is ahead of base",
           "unauthorized": "401"}),
    probe("save_dry_run", "POST", "/documents/42/save?dry_run=1", 1,
          "Replay the failing save in dry-run mode (no write).",
          {"forbidden": "403 generic 'operation not permitted'", "conflict": "409",
           "unauthorized": "401"}),
    probe("audit", "GET", "/audit?doc=42", 3, "Read the security audit log for document #42 (slow).",
          {**{"deny:" + c: f"200, last denial reason {AUDIT_CODES[c]}" for c in AUDIT_CODES},
           "no_entry": "200, no entry yet (log may lag)", "unauthorized": "401"}),
    probe("help", "GET", "/help", 1, "Read the generic help page.", {"generic": "200, generic advice"}),
]
PROBE_BY_ID = {p["id"]: p for p in PROBES}
ALLOWED = {(p["method"], p["path"]) for p in PROBES}


def true_outcome_distribution(probe_id, cause, audit_lag):
    """Exact generative model of one probe outcome (excluding transient 503s)."""
    if cause == "other":
        cause = None                     # 'other' behaves like a healthy account in every probe
    if probe_id == "help":
        return {"generic": 1.0}
    if cause == "session_expired":
        return {"unauthorized": 1.0}
    if probe_id == "whoami":
        return {"viewer": 1.0} if cause == "role_readonly" else {"editor": 1.0}
    if probe_id == "doc_meta":
        return {"owner_other": 1.0} if cause == "owner_policy" else (
            {"archived": 1.0} if cause == "document_archived" else {"own_active": 1.0})
    if probe_id == "workflow":
        return {"locked": 1.0} if cause == "workflow_locked" else {"open": 1.0}
    if probe_id == "quota":
        return {"exceeded": 1.0} if cause == "quota_exceeded" else {"ok": 1.0}
    if probe_id == "features":
        return {"editing_off": 1.0} if cause == "feature_disabled" else {"editing_on": 1.0}
    if probe_id == "versions":
        return {"concurrent_edit": 1.0} if cause == "edit_conflict" else {"consistent": 1.0}
    if probe_id == "save_dry_run":
        return {"conflict": 1.0} if cause == "edit_conflict" else {"forbidden": 1.0}
    if probe_id == "audit":
        if cause is None:
            return {"no_entry": 1.0}
        return {"deny:" + cause: 1.0 - audit_lag, "no_entry": audit_lag}
    raise ValueError("unknown probe")


def respond(cause, method, path, rng, v):
    if path == "/help":
        return 200, {"text": "If saving fails, check your permissions or contact support."}
    if cause == "session_expired":
        return 401, {"error": "unauthorized", "detail": "session token expired"}
    if path == "/whoami":
        return 200, {"user": "alice", "role": "viewer" if cause == "role_readonly" else "editor"}
    if path == "/documents/42":
        return 200, {"id": 42, "title": "Q3 plan", "owner": "bob" if cause == "owner_policy" else "alice",
                     "status": "archived" if cause == "document_archived" else "active"}
    if path == "/workflow/42":
        return 200, {"doc": 42, "stage": "review",
                     "lock": {"held_by": "carol"} if cause == "workflow_locked" else None}
    if path == "/quota":
        return 200, {"used_mb": 1024 if cause == "quota_exceeded" else 312, "limit_mb": 1024}
    if path == "/features":
        return 200, {"doc_editing": cause != "feature_disabled", "comments": True}
    if path == "/documents/42/versions":
        return 200, {"head": 17, "your_base": 16 if cause == "edit_conflict" else 17}
    if path == "/documents/42/save?dry_run=1":
        if cause == "edit_conflict":
            return 409, {"error": "conflict"}
        return 403, {"error": "operation not permitted"}
    if path == "/audit?doc=42":
        if cause in AUDIT_CODES and rng.random() >= v["audit_lag"]:
            return 200, {"entries": [{"event": "save_denied", "user": "alice", "reason": AUDIT_CODES[cause]}]}
        return 200, {"entries": []}
    return 404, {"error": "not found"}


def classify(probe_id, status, body):
    """Map a raw HTTP response to the probe's outcome vocabulary (or None if unmodeled)."""
    if status == 401:
        return "unauthorized"
    if probe_id == "save_dry_run":
        return {403: "forbidden", 409: "conflict"}.get(status)
    if status != 200 or not isinstance(body, dict):
        return None
    if probe_id == "help":
        return "generic"
    if probe_id == "whoami":
        return {"editor": "editor", "viewer": "viewer"}.get(body.get("role"))
    if probe_id == "doc_meta":
        if body.get("status") == "archived":
            return "archived"
        return "own_active" if body.get("owner") == "alice" else "owner_other"
    if probe_id == "workflow":
        return "locked" if body.get("lock") else "open"
    if probe_id == "quota":
        return "exceeded" if body.get("used_mb", 0) >= body.get("limit_mb", 1) else "ok"
    if probe_id == "features":
        return "editing_on" if body.get("doc_editing") else "editing_off"
    if probe_id == "versions":
        return "consistent" if body.get("head") == body.get("your_base") else "concurrent_edit"
    if probe_id == "audit":
        entries = body.get("entries") or []
        if not entries:
            return "no_entry"
        cause = CODE_TO_CAUSE.get(entries[-1].get("reason"))
        return "deny:" + cause if cause else None
    return None


SIGNATURES = {
    "session_expired": {(p["id"], "unauthorized") for p in PROBES if p["id"] != "help"},
    "role_readonly": {("whoami", "viewer")}, "owner_policy": {("doc_meta", "owner_other")},
    "document_archived": {("doc_meta", "archived")}, "workflow_locked": {("workflow", "locked")},
    "quota_exceeded": {("quota", "exceeded")}, "edit_conflict": {("versions", "concurrent_edit"),
                                                                 ("save_dry_run", "conflict")},
    "feature_disabled": {("features", "editing_off")},
}
for _c in AUDIT_CODES:
    SIGNATURES[_c].add(("audit", "deny:" + _c))


class WebDiagEnvironment(LoopbackSandbox):
    """One episode of the web-diag family. Use as a context manager."""
    family = "web-diag"
    TARGET = TARGET
    CAUSES = CAUSES
    DESCRIPTIONS = DESCRIPTIONS
    PROBES = PROBES
    VARIANTS = VARIANTS
    TABLE_LAG = TABLE_AUDIT_LAG
    NOISE_EXEMPT = frozenset({"/help"})
    SIGNATURES = SIGNATURES
    STATE_FIELDS = {"user": "alice", "page": "document/42"}
    respond = staticmethod(respond)
    classify = staticmethod(classify)
    true_outcome_distribution = staticmethod(true_outcome_distribution)

    @classmethod
    def public_task(cls):
        return {"objective": "Diagnose why user alice cannot save document #42 in a local test application",
                "initial_observation": "POST /documents/42/save returned an error page: 'Save failed'"}


def likelihood_table(probe_id, audit_lag=TABLE_AUDIT_LAG, eps=EPS):
    return WebDiagEnvironment.likelihood_table(probe_id, audit_lag, eps)


def catalog(audit_lag=TABLE_AUDIT_LAG):
    return WebDiagEnvironment.build_catalog(audit_lag)


def web_suite(variants=("base", "drift", "noise")):
    """24 task specs (8 causes x 3 variants). Hidden causes live only in these specs."""
    return suite(WebDiagEnvironment, "web", variants)


def make_web_env(task, seed):
    return WebDiagEnvironment(task["cause"], task["variant"], seed, task.get("drift_to"))
