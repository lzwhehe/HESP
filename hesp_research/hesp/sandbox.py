"""Generic loopback diagnosis sandbox shared by all task families.

A family subclass supplies: hypotheses and their descriptions, the probe catalogue
(method, path, cost, outcome vocabulary), the HTTP behaviour of the application under
each hidden cause (``respond``), the response classifier (``classify``), the exact
generative outcome model (``true_outcome_distribution``), cause signatures for the
independent verifier, and the public task text.

Shared guarantees: one fresh ``ThreadingHTTPServer`` on 127.0.0.1 per episode, fixed
(method, path) allowlist, redirects refused, short timeouts, transient-error noise that
is marked invalid, optional mid-episode drift (state version advances and the hidden
cause changes), and a verifier that is unreachable through the planner API.
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
EPS = 0.01
TRANSIENT = "transient_error"


def probe(pid, method, path, cost, description, notes):
    return {"id": pid, "method": method, "path": path, "cost": cost,
            "description": description, "outcome_notes": notes}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class _App:
    """Mutable server-side state; ``respond`` is the family's pure behaviour function."""

    def __init__(self, family, cause, variant, seed):
        self.family, self.cause = family, cause
        self.variant = family.VARIANTS[variant]
        self.rng = random.Random(seed)
        self.lock = threading.Lock()

    def respond(self, method, path):
        with self.lock:
            v = self.variant
            if (method, path) not in self.family.allowed():
                return 404, {"error": "not found"}
            if v["transient"] and path not in self.family.NOISE_EXEMPT and self.rng.random() < v["transient"]:
                return 503, {"error": "service temporarily unavailable"}
            return self.family.respond(self.cause, method, path, self.rng, v)


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


class LoopbackSandbox:
    """Base environment. Subclasses define the family-specific class attributes/methods."""
    label = LABEL
    family = None
    TARGET = None
    CAUSES = ()
    DESCRIPTIONS = {}
    PROBES = []
    VARIANTS = {}
    TABLE_LAG = 0.15
    NOISE_EXEMPT = frozenset()
    SIGNATURES = {}
    STATE_FIELDS = {}
    max_citations = 3

    # ---- family hooks -------------------------------------------------------------
    @classmethod
    def hypotheses_(cls):
        return tuple(cls.CAUSES) + ("other",)

    @classmethod
    def allowed(cls):
        return {(p["method"], p["path"]) for p in cls.PROBES}

    @classmethod
    def probe_by_id(cls):
        return {p["id"]: p for p in cls.PROBES}

    @staticmethod
    def respond(cause, method, path, rng, variant):
        raise NotImplementedError

    @staticmethod
    def classify(probe_id, status, body):
        raise NotImplementedError

    @staticmethod
    def true_outcome_distribution(probe_id, cause, lag):
        raise NotImplementedError

    @classmethod
    def public_task(cls):
        raise NotImplementedError

    # ---- predictive tables ---------------------------------------------------------
    @classmethod
    def likelihood_table(cls, probe_id, lag=None, eps=EPS):
        lag = cls.TABLE_LAG if lag is None else lag
        vocab = list(cls.probe_by_id()[probe_id]["outcome_notes"])
        table = {}
        for h in cls.hypotheses_():
            dist = cls.true_outcome_distribution(probe_id, h, lag)
            row = {o: dist.get(o, 0.0) * (1 - eps) + eps / len(vocab) for o in vocab}
            total = sum(row.values())
            table[h] = {o: v / total for o, v in row.items()}
        return table

    @classmethod
    def uniform_table(cls, probe_id):
        """An uninformed table: every outcome equally likely under every hypothesis."""
        vocab = list(cls.probe_by_id()[probe_id]["outcome_notes"])
        return {h: {o: 1.0 / len(vocab) for o in vocab} for h in cls.hypotheses_()}

    @classmethod
    def build_catalog(cls, lag=None, oracle=True):
        """Probe catalogue. ``oracle=False`` never calls ``true_outcome_distribution``: it
        attaches uninformed tables instead, so code that must not see the generative model
        (the v0.6 empirical estimator) cannot reach it even by accident. Execution only
        checks an action's identity, so probing behaves identically either way."""
        table = (lambda pid: cls.likelihood_table(pid, lag)) if oracle else cls.uniform_table
        source = "designer_table_eps0.01" if oracle else "uninformed_uniform"
        return [Action(p["id"], cls.TARGET, f'{p["method"]} {p["path"]}', p["cost"], table(p["id"]),
                       prediction_source=source, description=p["description"],
                       outcome_notes=dict(p["outcome_notes"]))
                for p in cls.PROBES]

    # ---- episode ----------------------------------------------------------------------
    def __init__(self, cause, variant="base", seed=0, drift_to=None, timeout=5.0, oracle=True):
        if cause not in self.CAUSES or variant not in self.VARIANTS:
            raise ValueError("Unknown sandbox fixture")
        if self.VARIANTS[variant]["drift_after"] and (drift_to not in self.CAUSES or drift_to == cause):
            raise ValueError("Drift variant needs a different drift_to cause")
        self.hypotheses = self.hypotheses_()
        self.variant = variant
        self._drift_to = drift_to
        self._app = _App(type(self), cause, variant, seed)
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
        self._catalog = {a.id: a for a in self.build_catalog(oracle=oracle)}

    def close(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def catalog(self):
        return list(self._catalog.values())

    def describe(self):
        return {**self.public_task(), "environment": LABEL, "allowed_targets": [self.TARGET],
                "answer_options": dict(self.DESCRIPTIONS),
                "finish_rule": ("Cite 1-3 observation IDs from the current state version whose response "
                                "directly shows the cause.")}

    def state(self):
        return {**self.STATE_FIELDS, "version": self._version}

    def _request(self, method, path):
        if (method, path) not in self.allowed():
            raise ValueError("Path not in sandbox allowlist")
        url = self._base + path
        if urllib.parse.urlsplit(url).hostname != "127.0.0.1":
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
        p = self.probe_by_id()[action.id]
        status, body, raw = self._request(p["method"], p["path"])
        self._counter += 1
        valid = status != 503
        outcome = self.classify(action.id, status, body) if valid else None
        observation = Observation(
            f"o{self._counter:04d}", action.id, self._version,
            outcome if outcome is not None else (TRANSIENT if not valid else "unclassified"),
            {"http_status": status}, f"{p['method']} {p['path']} -> HTTP {status} {raw}", valid)
        self._observations[observation.id] = observation
        self._calls += 1
        drift_after = self.VARIANTS[self.variant]["drift_after"]
        if drift_after and self._calls == drift_after:
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
        return any(o.state_version == self._version and (o.action_id, o.outcome) in self.SIGNATURES[cause]
                   for o in cited)


def suite(env_cls, prefix, variants=("base", "drift", "noise")):
    """8 causes x variants task specs; drift pairs cause i with cause i+3."""
    tasks = []
    causes = env_cls.CAUSES
    for variant in variants:
        for i, cause in enumerate(causes):
            drift_to = causes[(i + 3) % len(causes)] if variant == "drift" else None
            tasks.append({"task_id": f"{prefix}-{variant}-{i:02d}", "family": env_cls.family, "variant": variant,
                          "cause": cause, "drift_to": drift_to})
    return tasks
