"""Feasibility audit of OTRF Security-Datasets as a HESP triage source (no LLM, no GPU).

Question: if a service-install or scheduled-task event is raised as an alert, does the alert
text alone already tell attack from benign (the ExCyTIn failure), or is investigation needed?

Event-level ground truth: an alert is "attack" when its service/task name occurs as a word in
the metadata of the recording it came from (the emulation's own adversary_view / description);
otherwise it is background activity of the lab hosts. Names are matched per recording, so the
contributor handle that appears in every metadata file does not count by itself.

Usage: python otrf_alert_audit.py   (reads external/otrf/, written by the download step)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from otrf_load import ROOT, events, manifest  # noqa: E402

MS_TASK = re.compile(r"^\\(Microsoft\\Windows\\|OneDrive Standalone Update Task)", re.I)
MS_BINARY = re.compile(r"svchost\.exe -k |\\Windows Defender\\|CredentialEnrollmentManager\.exe", re.I)


def alerts(recording):
    for e in events(ROOT / "host" / recording["file"]):
        channel = str(e.get("Channel") or "").lower()
        eid = int(e.get("EventID") or 0)
        if ("security" in channel and eid == 4697) or (channel == "system" and eid == 7045):
            yield {"kind": "service", "name": e.get("ServiceName") or "",
                   "detail": str(e.get("ServiceFileName") or e.get("ImagePath") or ""),
                   "creator": str(e.get("SubjectUserName") or e.get("AccountName") or "")}
        elif "security" in channel and eid in (4698, 4702):
            yield {"kind": "task", "name": e.get("TaskName") or "", "detail": "",
                   "creator": str(e.get("SubjectUserName") or "")}


def is_attack(alert, metadata_text):
    leaf = alert["name"].rsplit("\\", 1)[-1]
    return bool(leaf) and re.search(rf"\b{re.escape(leaf)}\b", metadata_text) is not None


def looks_benign(alert):
    """The one-glance rule an analyst applies to the alert text alone."""
    if alert["kind"] == "task":
        return bool(MS_TASK.match(alert["name"]))
    return bool(MS_BINARY.search(alert["detail"]))


def main():
    rows, seen = [], set()
    for rec in manifest():
        meta = (ROOT / "metadata" / f"{rec['id']}.yaml").read_text(encoding="utf-8", errors="replace")
        for a in alerts(rec):
            key = (rec["file"], a["kind"], a["name"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({**a, "recording": rec["file"], "attack": is_attack(a, meta),
                         "rule_benign": looks_benign(a)})
    attack = [r for r in rows if r["attack"]]
    benign = [r for r in rows if not r["attack"]]
    leaked = [r for r in attack if not r["rule_benign"]]
    disguised = [r for r in attack if r["rule_benign"]]
    benign_flagged = [r for r in benign if not r["rule_benign"]]
    summary = {
        "recordings": len(manifest()), "distinct_alerts": len(rows),
        "attack_alerts": len(attack), "benign_alerts": len(benign),
        "attack_named_by_alert_text": len(leaked), "attack_disguised_as_benign": len(disguised),
        "benign_flagged_by_rule": len(benign_flagged),
        "rule_accuracy": round(sum(r["attack"] != r["rule_benign"] for r in rows) / len(rows), 3),
        "disguised": [{k: r[k] for k in ("recording", "kind", "name", "creator")} for r in disguised],
        "leaked": [{k: r[k] for k in ("recording", "kind", "name")} for r in leaked],
        "benign_flagged": [{k: r[k] for k in ("recording", "kind", "name")} for r in benign_flagged],
        "benign_creators": sorted({r["creator"] for r in benign if r["kind"] == "task"}),
    }
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
