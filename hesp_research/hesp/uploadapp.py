"""Task family ``upload-diag`` (v0.4, held-out): why does bob's file upload fail?

Designed and frozen before any v0.4 result, and structurally different from
``web-diag``: a medium-cost dry-run probe (cost 2) splits the causes into six groups,
the decisive trace probe costs 4, several causes are indistinguishable by the dry run
(generic 403), and authentication failure is *not* global (reads use the browser
session, only uploads use the API token).

Variants
  base   deterministic; the support trace is not yet indexed with probability 0.10
  noise  15% transient HTTP 503 on any probe except the FAQ; trace lag 0.30
  drift  after the second tool call a colleague changes the folder: the state version
         advances and the hidden cause switches.
"""

from .sandbox import LoopbackSandbox, probe, suite

TARGET = "sandbox://files-app"
CAUSES = ("file_too_large", "type_blocked", "folder_readonly", "storage_full",
          "name_locked", "scanner_down", "token_revoked", "region_mismatch")
HYPOTHESES = CAUSES + ("other",)
DESCRIPTIONS = {
    "file_too_large": "The file exceeds the per-file upload size limit of the workspace.",
    "type_blocked": "The file type (PDF) is not on the workspace's allowed upload types.",
    "folder_readonly": "The user only has read permission on the target folder.",
    "storage_full": "The team's shared storage allocation is full.",
    "name_locked": "A file with the same name exists and is locked (checked out) by another user.",
    "scanner_down": "The malware-scanning service is down, so uploads are rejected until it recovers.",
    "token_revoked": "The user's API upload token was revoked; browsing still works with the session cookie.",
    "region_mismatch": "The folder is pinned to another data region and cross-region writes are refused.",
    "other": "Some cause not listed here.",
}
TRACE_CODES = {"file_too_large": "E_SIZE", "type_blocked": "E_MIME", "folder_readonly": "E_ACL",
               "storage_full": "E_QUOTA", "name_locked": "E_LOCK", "scanner_down": "E_AV_UNAVAILABLE",
               "token_revoked": "E_TOKEN", "region_mismatch": "E_REGION"}
CODE_TO_CAUSE = {v: k for k, v in TRACE_CODES.items()}
VARIANTS = {
    "base": {"lag": 0.10, "transient": 0.0, "drift_after": None},
    "noise": {"lag": 0.30, "transient": 0.15, "drift_after": None},
    "drift": {"lag": 0.10, "transient": 0.0, "drift_after": 2},
}
TABLE_LAG = 0.15
DRY_RUN = {"file_too_large": (413, "too_large"), "type_blocked": (415, "unsupported_type"),
           "name_locked": (409, "conflict"), "storage_full": (507, "insufficient_storage"),
           "scanner_down": (424, "dependency_failed"), "folder_readonly": (403, "forbidden"),
           "token_revoked": (403, "forbidden"), "region_mismatch": (403, "forbidden")}

PROBES = [
    probe("limits", "GET", "/upload/limits", 1, "Read workspace upload limits (max size, allowed types).",
          {"ok": "200, file within limits", "size_exceeded": "200, 18 MB above max_mb",
           "type_not_allowed": "200, pdf missing from allowed_types"}),
    probe("folder_acl", "GET", "/folders/finance/acl", 1, "Read bob's permission on folder 'finance'.",
          {"write": "200, permission=write", "read_only": "200, permission=read"}),
    probe("storage", "GET", "/teams/finance/storage", 1, "Read the team's storage usage.",
          {"ok": "200, used below allocation", "full": "200, used equals allocation"}),
    probe("listing", "GET", "/folders/finance/files?name=report.pdf", 1,
          "Look for an existing file with the same name.",
          {"absent": "200, no such file", "locked_by_other": "200, exists and locked by another user"}),
    probe("health", "GET", "/services/health", 1, "Read platform service health.",
          {"all_up": "200, all services up", "scanner_down": "200, av-scanner down"}),
    probe("token", "GET", "/auth/token", 1, "Inspect the API upload token.",
          {"valid": "200, token active", "revoked": "200, token revoked"}),
    probe("folder_meta", "GET", "/folders/finance", 1, "Read folder metadata (data region).",
          {"same_region": "200, region matches client", "cross_region": "200, region differs from client"}),
    probe("dry_run", "POST", "/upload/dry-run", 2, "Validate the upload without storing it (slower).",
          {"too_large": "413", "unsupported_type": "415", "conflict": "409", "insufficient_storage": "507",
           "dependency_failed": "424", "forbidden": "403 generic", "server_error": "500 generic"}),
    probe("trace", "GET", "/support/trace?upload=last", 4, "Fetch the support trace of the last upload (slow).",
          {**{"code:" + c: f"200, error code {TRACE_CODES[c]}" for c in TRACE_CODES},
           "not_indexed": "200, trace not indexed yet"}),
    probe("faq", "GET", "/help/upload", 1, "Read the generic upload FAQ.", {"generic": "200, generic advice"}),
]


def true_outcome_distribution(probe_id, cause, lag):
    if cause == "other":
        cause = None
    if probe_id == "faq":
        return {"generic": 1.0}
    if probe_id == "limits":
        return {"size_exceeded": 1.0} if cause == "file_too_large" else (
            {"type_not_allowed": 1.0} if cause == "type_blocked" else {"ok": 1.0})
    if probe_id == "folder_acl":
        return {"read_only": 1.0} if cause == "folder_readonly" else {"write": 1.0}
    if probe_id == "storage":
        return {"full": 1.0} if cause == "storage_full" else {"ok": 1.0}
    if probe_id == "listing":
        return {"locked_by_other": 1.0} if cause == "name_locked" else {"absent": 1.0}
    if probe_id == "health":
        return {"scanner_down": 1.0} if cause == "scanner_down" else {"all_up": 1.0}
    if probe_id == "token":
        return {"revoked": 1.0} if cause == "token_revoked" else {"valid": 1.0}
    if probe_id == "folder_meta":
        return {"cross_region": 1.0} if cause == "region_mismatch" else {"same_region": 1.0}
    if probe_id == "dry_run":
        return {DRY_RUN[cause][1]: 1.0} if cause else {"server_error": 1.0}
    if probe_id == "trace":
        if cause is None:
            return {"not_indexed": 1.0}
        return {"code:" + cause: 1.0 - lag, "not_indexed": lag}
    raise ValueError("unknown probe")


def respond(cause, method, path, rng, v):
    if path == "/help/upload":
        return 200, {"text": "Uploads can fail for many reasons. Check limits, permissions and storage."}
    if path == "/upload/limits":
        return 200, {"max_mb": 10 if cause == "file_too_large" else 100, "file_mb": 18,
                     "allowed_types": ["docx", "xlsx"] if cause == "type_blocked" else ["docx", "xlsx", "pdf"],
                     "file_type": "pdf"}
    if path == "/folders/finance/acl":
        return 200, {"user": "bob", "permission": "read" if cause == "folder_readonly" else "write"}
    if path == "/teams/finance/storage":
        return 200, {"used_gb": 500 if cause == "storage_full" else 211, "allocation_gb": 500}
    if path == "/folders/finance/files?name=report.pdf":
        if cause == "name_locked":
            return 200, {"files": [{"name": "report.pdf", "locked_by": "dana"}]}
        return 200, {"files": []}
    if path == "/services/health":
        return 200, {"api": "up", "storage": "up", "av_scanner": "down" if cause == "scanner_down" else "up"}
    if path == "/auth/token":
        return 200, {"token": "upl_****", "status": "revoked" if cause == "token_revoked" else "active"}
    if path == "/folders/finance":
        return 200, {"name": "finance", "region": "eu-west" if cause == "region_mismatch" else "ap-east",
                     "client_region": "ap-east"}
    if path == "/upload/dry-run":
        if cause is None or cause not in DRY_RUN:
            return 500, {"error": "internal error"}
        status, _ = DRY_RUN[cause]
        return status, {"error": {403: "forbidden", 409: "conflict", 413: "payload too large",
                                  415: "unsupported media type", 424: "failed dependency",
                                  507: "insufficient storage"}[status]}
    if path == "/support/trace?upload=last":
        if cause in TRACE_CODES and rng.random() >= v["lag"]:
            return 200, {"trace": {"upload": "report.pdf", "error_code": TRACE_CODES[cause]}}
        return 200, {"trace": None}
    return 404, {"error": "not found"}


def classify(probe_id, status, body):
    if probe_id == "dry_run":
        return {413: "too_large", 415: "unsupported_type", 409: "conflict", 507: "insufficient_storage",
                424: "dependency_failed", 403: "forbidden", 500: "server_error"}.get(status)
    if status != 200 or not isinstance(body, dict):
        return None
    if probe_id == "faq":
        return "generic"
    if probe_id == "limits":
        if body.get("file_mb", 0) > body.get("max_mb", 0):
            return "size_exceeded"
        return "ok" if body.get("file_type") in (body.get("allowed_types") or []) else "type_not_allowed"
    if probe_id == "folder_acl":
        return {"write": "write", "read": "read_only"}.get(body.get("permission"))
    if probe_id == "storage":
        return "full" if body.get("used_gb", 0) >= body.get("allocation_gb", 1) else "ok"
    if probe_id == "listing":
        files = body.get("files") or []
        return "locked_by_other" if any(f.get("locked_by") not in (None, "bob") for f in files) else "absent"
    if probe_id == "health":
        return "scanner_down" if body.get("av_scanner") == "down" else "all_up"
    if probe_id == "token":
        return {"active": "valid", "revoked": "revoked"}.get(body.get("status"))
    if probe_id == "folder_meta":
        return "same_region" if body.get("region") == body.get("client_region") else "cross_region"
    if probe_id == "trace":
        trace = body.get("trace")
        if not trace:
            return "not_indexed"
        cause = CODE_TO_CAUSE.get(trace.get("error_code"))
        return "code:" + cause if cause else None
    return None


SIGNATURES = {
    "file_too_large": {("limits", "size_exceeded"), ("dry_run", "too_large")},
    "type_blocked": {("limits", "type_not_allowed"), ("dry_run", "unsupported_type")},
    "folder_readonly": {("folder_acl", "read_only")},
    "storage_full": {("storage", "full"), ("dry_run", "insufficient_storage")},
    "name_locked": {("listing", "locked_by_other"), ("dry_run", "conflict")},
    "scanner_down": {("health", "scanner_down"), ("dry_run", "dependency_failed")},
    "token_revoked": {("token", "revoked")},
    "region_mismatch": {("folder_meta", "cross_region")},
}
for _c in TRACE_CODES:
    SIGNATURES[_c].add(("trace", "code:" + _c))


class UploadDiagEnvironment(LoopbackSandbox):
    family = "upload-diag"
    TARGET = TARGET
    CAUSES = CAUSES
    DESCRIPTIONS = DESCRIPTIONS
    PROBES = PROBES
    VARIANTS = VARIANTS
    TABLE_LAG = TABLE_LAG
    NOISE_EXEMPT = frozenset({"/help/upload"})
    SIGNATURES = SIGNATURES
    STATE_FIELDS = {"user": "bob", "page": "folder/finance"}
    respond = staticmethod(respond)
    classify = staticmethod(classify)
    true_outcome_distribution = staticmethod(true_outcome_distribution)

    @classmethod
    def public_task(cls):
        return {"objective": "Diagnose why user bob cannot upload report.pdf (18 MB) to the shared "
                             "folder 'finance' in a local test application",
                "initial_observation": "The upload dialog shows 'Upload failed' after the progress bar completes"}


def upload_suite(variants=("base", "drift", "noise")):
    return suite(UploadDiagEnvironment, "upl", variants)


def make_upload_env(task, seed):
    return UploadDiagEnvironment(task["cause"], task["variant"], seed, task.get("drift_to"))
