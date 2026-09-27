"""v1.0 part A, step 1: the eligible Sigma rule pool, in a fixed random order (PROTOCOL.md v1.0).

Mechanical eligibility (fixed before sampling): a rule under ``rules/`` (not ``deprecated``,
``unsupported`` or the other rule collections); status stable or test; level medium, high or
critical; at least one ``attack.t####`` tag; at least two ``falsepositives`` entries left after
dropping generic ones (an entry that is only "unknown", "unlikely", "none" or "n/a", or is shorter
than 12 characters). The eligible rules, sorted by id, are shuffled with seed 2028. The first 12
in that order are the sample; the rest are the replacement order for rules whose annotation fails
the identifiability check. Nothing about any outcome is looked at here.

Needs PyYAML (present in the vLLM environment).

    python scripts/v10a_select_rules.py --sigma ~/sigma --out results/v10a/rule_pool.json
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess

import yaml

SEED = 2028
MAX_BENIGN = 4
GENERIC = re.compile(r"\W*(unknown|unlikely|none|n/?a)\W*", re.IGNORECASE)
TECHNIQUE = re.compile(r"attack\.t\d{4}(\.\d{3})?$", re.IGNORECASE)


def usable_fp(entries):
    out = []
    for e in entries or []:
        if not isinstance(e, str):
            continue
        e = " ".join(e.split())
        if GENERIC.fullmatch(e) or len(e) < 12:
            continue
        out.append(e)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sigma", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    root = Path(args.sigma).expanduser()
    commit = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H"], capture_output=True,
                            text=True, check=True).stdout.strip()
    eligible, seen, parse_errors = [], set(), 0
    for path in sorted((root / "rules").rglob("*.yml")):
        try:
            rule = next(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except Exception:
            parse_errors += 1
            continue
        if not isinstance(rule, dict):
            continue
        tags = [t for t in rule.get("tags") or [] if isinstance(t, str)]
        techniques = sorted({t.split(".", 1)[1].upper() for t in tags if TECHNIQUE.match(t)})
        fps = usable_fp(rule.get("falsepositives"))
        if (rule.get("status") in ("stable", "test") and rule.get("level") in ("medium", "high", "critical")
                and techniques and len(fps) >= 2 and rule.get("id") and rule["id"] not in seen):
            seen.add(rule["id"])
            eligible.append({"rule_id": rule["id"], "path": str(path.relative_to(root)).replace("\\", "/"),
                             "title": " ".join(str(rule.get("title", "")).split()),
                             "description": " ".join(str(rule.get("description", "")).split()),
                             "techniques": techniques, "logsource": rule.get("logsource") or {},
                             "level": rule["level"], "status": rule["status"],
                             "falsepositives": fps[:MAX_BENIGN]})
    eligible.sort(key=lambda r: r["rule_id"])
    random.Random(SEED).shuffle(eligible)
    record = {"schema": "hesp.v10a.rule_pool.v1", "sigma_commit": commit, "seed": SEED,
              "eligible": len(eligible), "parse_errors": parse_errors, "sample_size": 12,
              "license": "Detection Rule License (DRL) 1.1, https://github.com/SigmaHQ/Detection-Rule-License",
              "order": eligible}
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"{len(eligible)} eligible rules (commit {commit[:8]}), sha256 {hashlib.sha256(out.read_bytes()).hexdigest()[:12]}")
    for r in eligible[:12]:
        print(f"  {r['rule_id'][:8]} {r['title']}  ({len(r['falsepositives'])} benign)")


if __name__ == "__main__":
    main()
