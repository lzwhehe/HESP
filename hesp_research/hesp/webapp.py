"""Local, authorized web diagnosis sandbox (v0.3).

A tiny document-management app is served by the standard library on 127.0.0.1 with an
ephemeral port, one fresh instance per episode. One hidden *fault* makes
``POST /documents/42/save`` fail. The agent may only send the fixed read-only probes
below; each probe returns a real HTTP response that a per-probe classifier maps to a
finite outcome class. An independent verifier, not reachable through the planner
API, checks the final diagnosis.

Safety scope: loopback only, fixed path allowlist, redirects refused, short timeouts,
no payloads, no credentials, no external network. This is a *diagnosis* task, not an
attack benchmark.

Variants
  base   deterministic responses; the audit log lags with probability 0.10
  noise  15% transient HTTP 503 on any probe (invalid observation, retry allowed);
         audit lag 0.30
  drift  like base, but after the second tool call another user changes the document,
         the business-state version advances and the hidden fault switches.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import random
import threading
import urllib.error
import urllib.parse
import urllib.request

from .core import Action, Observation

LABEL = "local_web_sandbox"
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
    "base": {"audit_lag": 0.10, "transient": 0.0, "drift_after": None},
    "noise": {"audit_lag": 0.30, "transient": 0.15, "drift_after": None},
    "drift": {"audit_lag": 0.10, "transient": 0.0, "drift_after": 2},
}
# Designer's predictive model assumes one lag rate for every variant (it is not told the variant).
TABLE_AUDIT_LAG = 0.15
EPS = 0.01


# ------------------------------------------------------------------ probe catalogue
def _probe(pid, method, path, cost, description, notes):
    return {"id": pid, "method": method, "path": path, "cost": cost,
            "description": description, "outcome_notes": notes}


PROBES = [
    _probe("whoami", "GET", "/whoami", 1, "Show the authenticated user and current role.",
           {"editor": "200, role=editor", "viewer": "200, role=viewer", "unauthorized": "401"}),
    _probe("doc_meta", "GET", "/documents/42", 1, "Read document #42 metadata (owner, status).",
           {"own_active": "200, owned by the user, status active", "owner_other": "200, owned by another user",
            "archived": "200, status archived", "unauthorized": "401"}),
    _probe("workflow", "GET", "/workflow/42", 1, "Read the approval-workflow state of document #42.",
           {"open": "200, no lock", "locked": "200, lock held by another user", "unauthorized": "401"}),
    _probe("quota", "GET", "/quota", 1, "Read the user's storage quota.",
           {"ok": "200, usage below limit", "exceeded": "200, usage at limit", "unauthorized": "401"}),
    _probe("features", "GET", "/features", 1, "Read workspace feature flags.",
           {"editing_on": "200, doc_editing=true", "editing_off": "200, doc_editing=false",
            "unauthorized": "401"}),
    _probe("versions", "GET", "/documents/42/versions", 1, "Compare the user's base revision with the head.",
           {"consistent": "200, base equals head", "concurrent_edit": "200, head is ahead of base",
            "unauthorized": "401"}),
    _probe("save_dry_run", "POST", "/documents/42/save?dry_run=1", 1,
           "Replay the failing save in dry-run mode (no write).",
           {"forbidden": "403 generic 'operation not permitted'", "conflict": "409",
            "unauthorized": "401"}),
    _probe("audit", "GET", "/audit?doc=42", 3, "Read the security audit log for document #42 (slow).",
           {**{"deny:" + c: f"200, last denial reason {AUDIT_CODES[c]}" for c in AUDIT_CODES},
            "no_entry": "200, no entry yet (log may lag)", "unauthorized": "401"}),
    _probe("help", "GET", "/help", 1, "Read the generic help page.", {"generic": "200, generic advice"}),
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


def likelihood_table(probe_id, audit_lag=TABLE_AUDIT_LAG, eps=EPS):
    """P(o | h, a) over the full outcome vocabulary with epsilon smoothing."""
    vocab = list(PROBE_BY_ID[probe_id]["outcome_notes"])
    table = {}
    for h in HYPOTHESES:
        dist = true_outcome_distribution(probe_id, h, audit_lag)
        row = {o: dist.get(o, 0.0) * (1 - eps) + eps / len(vocab) for o in vocab}
        total = sum(row.values())
        table[h] = {o: v / total for o, v in row.items()}
    return table


def catalog(audit_lag=TABLE_AUDIT_LAG):
    return [Action(p["id"], TARGET, f'{p["method"]} {p["path"]}', p["cost"], likelihood_table(p["id"], audit_lag),
                   prediction_source="designer_table_eps0.01", description=p["description"],
                   outcome_notes=dict(p["outcome_notes"]))
            for p in PROBES]


# ------------------------------------------------------------------ HTTP application
class _App:
    def __init__(self, cause, variant, seed):
        self.cause = cause
        self.variant = VARIANTS[variant]
        self.rng = random.Random(seed)
        self.lock = threading.Lock()

    def respond(self, method, path):
        with self.lock:
            cause, rng, v = self.cause, self.rng, self.variant
            if v["transient"] and path != "/help" and rng.random() < v["transient"]:
                return 503, {"error": "service temporarily unavailable"}
            if (method, path) not in ALLOWED:
                return 404, {"error": "not found"}
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
                    return 200, {"entries": [{"event": "save_denied", "user": "alice",
                                              "reason": AUDIT_CODES[cause]}]}
                return 200, {"entries": []}
            return 404, {"error": "not found"}


def _handler(app):
    class Handler(BaseHTTPRequestHandler):
        def _serve(self, method):
            status, body = app.respond(method, self.path)
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._serve("GET")

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                self.rfile.read(min(length, 4096))
            self._serve("POST")

        def log_message(self, *args):
            pass
    return Handler


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


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


class WebDiagEnvironment:
    """One episode of the local web diagnosis task. Use as a context manager."""
    label = LABEL
    family = "web-diag"
    hypotheses = HYPOTHESES
    max_citations = 3

    def __init__(self, cause="owner_policy", variant="base", seed=0, drift_to=None, timeout=5.0):
        if cause not in CAUSES or variant not in VARIANTS:
            raise ValueError("Unknown web fixture")
        if VARIANTS[variant]["drift_after"] and (drift_to not in CAUSES or drift_to == cause):
            raise ValueError("Drift variant needs a different drift_to cause")
        self.variant = variant
        self._drift_to = drift_to
        self._app = _App(cause, variant, seed)
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(self._app))
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._base = f"http://127.0.0.1:{self._server.server_address[1]}"
        self._opener = urllib.request.build_opener(_NoRedirect)
        self._timeout = timeout
        self._version = 0
        self._calls = 0
        self._counter = 0
        self._observations = {}
        self._catalog = {a.id: a for a in catalog()}

    # -- lifecycle
    def close(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- public interface
    def catalog(self):
        return list(self._catalog.values())

    def describe(self):
        return {
            "objective": "Diagnose why user alice cannot save document #42 in a local test application",
            "initial_observation": "POST /documents/42/save returned an error page: 'Save failed'",
            "environment": LABEL,
            "allowed_targets": [TARGET],
            "answer_options": dict(DESCRIPTIONS),
            "finish_rule": ("Cite 1-3 observation IDs from the current state version whose response "
                            "directly shows the cause."),
        }

    def state(self):
        return {"user": "alice", "page": "document/42", "version": self._version}

    def _request(self, method, path):
        if (method, path) not in ALLOWED:
            raise ValueError("Path not in sandbox allowlist")
        url = self._base + path
        parsed = urllib.parse.urlsplit(url)
        if parsed.hostname != "127.0.0.1":
            raise ValueError("Sandbox is loopback-only")
        req = urllib.request.Request(url, method=method, data=b"{}" if method == "POST" else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with self._opener.open(req, timeout=self._timeout) as resp:
                status, raw = resp.status, resp.read(4096)
        except urllib.error.HTTPError as err:
            status, raw = err.code, err.read(4096)
        except (urllib.error.URLError, TimeoutError, OSError):
            raise RuntimeError("Sandbox request failed") from None
        try:
            body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            body = None
        return status, body, raw.decode("utf-8", "replace")

    def execute(self, action):
        known = self._catalog.get(action.id)
        if known is None or (known.target, known.purpose, known.cost) != (action.target, action.purpose, action.cost):
            raise ValueError("Only catalogued sandbox probes are allowed")
        probe = PROBE_BY_ID[action.id]
        status, body, raw = self._request(probe["method"], probe["path"])
        self._counter += 1
        outcome = classify(action.id, status, body)
        valid = status != 503
        observation = Observation(
            f"o{self._counter:04d}", action.id, self._version,
            outcome if outcome is not None else ("transient_error" if not valid else "unclassified"),
            {"http_status": status}, f"{probe['method']} {probe['path']} -> HTTP {status} {raw}", valid)
        self._observations[observation.id] = observation
        self._calls += 1
        drift_after = VARIANTS[self.variant]["drift_after"]
        if drift_after and self._calls == drift_after:
            # Another user changes the document: state version advances and the fault changes.
            with self._app.lock:
                self._app.cause = self._drift_to
            self._version += 1
        return observation

    def verify(self, hypothesis, evidence_ids):
        """Independent oracle; inaccessible through the planner API."""
        cause = self._app.cause
        if hypothesis != cause or not evidence_ids or len(evidence_ids) > self.max_citations:
            return False
        cited = [self._observations.get(i) for i in evidence_ids]
        if any(o is None for o in cited):
            return False
        return any(o.state_version == self._version and (o.action_id, o.outcome) in SIGNATURES[cause]
                   for o in cited)


def web_suite(variants=("base", "drift", "noise")):
    """24 task specs (8 causes x 3 variants). Hidden causes live only in these specs."""
    tasks = []
    for variant in variants:
        for i, cause in enumerate(CAUSES):
            drift_to = CAUSES[(i + 3) % len(CAUSES)] if variant == "drift" else None
            tasks.append({"task_id": f"web-{variant}-{i:02d}", "family": "web-diag", "variant": variant,
                          "cause": cause, "drift_to": drift_to})
    return tasks


def make_web_env(task, seed):
    return WebDiagEnvironment(task["cause"], task["variant"], seed, task.get("drift_to"))
