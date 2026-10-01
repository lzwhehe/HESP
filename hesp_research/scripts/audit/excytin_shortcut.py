"""Shortcut audit of ExCyTIn-Bench (no LLM). Pre-registered in docs/PROTOCOL_AUDIT.md.

Two investigation-free baselines answer each question by reading the alert the question names:
  graph : rank the alert nodes of the incident graph by word overlap between the question and the alert name; among the
          top alert's neighbouring entities of the requested type, answer the first (lowest node id).
  table : the same, but using only the SecurityAlert table an agent can query (AlertName and its Entities field).
Metrics (exact match after normalization; stricter than the benchmark's LLM judge):
  named      : the question's end alert is ranked first by word overlap (graph only);
  adjacent   : the gold answer is a neighbour of the end alert (graph only; an upper bound of the shortcut);
  accuracy   : the baseline's single answer equals the gold answer.

    python scripts/audit/excytin_shortcut.py --split train --out results/audit/excytin_train.json
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.environ.get("EXCYTIN_ROOT", r"E:\HESP\external\excytin")
NS = "{http://graphml.graphdrawing.org/xmlns}"
SEP = "\u2756"
STOP = set("the a an of to for in on with by and or that this was were is are what which who whose from at as be its it "
           "related alert alerts associated activity involved during same also one name full value identify identified "
           "observed detected reported reporting about".split())
TYPE_WORDS = [
    ("ip", ["ip address", " ip "]), ("hash", ["sha256", "sha1", "hash"]), ("url", ["url", "domain", "link"]),
    ("mailbox", ["email", "mailbox", "upn", "user principal"]), ("account", ["account", "user", "sid", "aaduserid"]),
    ("file", ["file", "executable", "binary"]), ("process", ["process", "command line", "commandline"]),
    ("host", ["host", "device", "machine", "computer"]),
]
GRAPH_TYPES = {"ip": ["ip"], "hash": ["file", "hash"], "url": ["url", "dns", "domain"], "mailbox": ["mailbox", "mail"],
               "account": ["account", "user"], "file": ["file"], "process": ["process"], "host": ["host", "machine", "device"]}
# entity type in SecurityAlert.Entities -> fields that carry the value an analyst would report
TABLE_FIELDS = {
    "ip": ("ip", ["Address"]), "url": ("url", ["Url"]), "mailbox": ("mailbox", ["MailboxPrimaryAddress", "Upn"]),
    "account": ("account", ["Name", "Sid", "AadUserId", "UserPrincipalName"]), "file": ("file", ["Name"]),
    "hash": ("filehash", ["Value"]), "process": ("process", ["CommandLine", "ProcessId"]),
    "host": ("host", ["HostName"]),
}


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def qtype(q):
    ql = " " + q.lower() + " "
    for t, ws in TYPE_WORDS:
        if any(w in ql for w in ws):
            return t
    return None


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().strip("`'\"").lower()


def match(gold, value):
    return bool(gold) and bool(value) and (gold == value or gold in value)


def load_graph(path):
    root = ET.parse(path).getroot()
    keys = {k.get("id"): k.get("attr.name") for k in root.iter(NS + "key")}
    nodes, adj = {}, defaultdict(set)
    for n in root.iter(NS + "node"):
        nodes[n.get("id")] = {keys[x.get("key")]: (x.text or "") for x in n.iter(NS + "data")}
    for e in root.iter(NS + "edge"):
        adj[e.get("source")].add(e.get("target"))
        adj[e.get("target")].add(e.get("source"))
    return nodes, adj


def load_alert_table(incident):
    path = os.path.join(ROOT, "data_anonymized", "incidents", incident, "SecurityAlert.csv")
    text = open(path, encoding="utf-8-sig").read()
    header = text.split("\n", 1)[0].split(SEP)
    tenant = text.split("\n", 2)[1].split(SEP)[0]
    records = re.split(r"\n(?=" + re.escape(tenant) + SEP + ")", text)[1:]
    alerts = []
    for r in records:
        f = r.split(SEP)
        if len(f) < len(header):
            continue
        row = dict(zip(header, f))
        raw = row.get("Entities", "").strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1].replace('""', '"')
        try:
            ents = json.loads(raw) if raw else []
        except ValueError:
            ents = []
        alerts.append((row.get("AlertName", ""), row.get("TimeGenerated", ""), ents))
    return alerts


def graph_answer(q, nodes, adj, alerts):
    qw = words(q)
    ranked = sorted(alerts, key=lambda a: (-len(qw & words(nodes[a].get("name", ""))), int(a)))
    if not ranked:
        return None, None
    t = qtype(q)
    for m in sorted(adj.get(ranked[0], set()), key=int):
        d = nodes[m]
        nt = d.get("node_type", "").lower()
        if t is None or any(k in nt for k in GRAPH_TYPES.get(t, [])):
            v = norm(d.get("value", "") or d.get("name", ""))
            if v and v not in q.lower():
                return ranked[0], v
    return ranked[0], None


def table_answer(q, table):
    qw = words(q)
    if not table:
        return None
    best = max(len(qw & words(name)) for name, _, _ in table)
    top = sorted([a for a in table if len(qw & words(a[0])) == best], key=lambda a: a[1])
    t = qtype(q)
    for _, _, ents in top:
        for e in ents if isinstance(ents, list) else []:
            if not isinstance(e, dict):
                continue
            etype = str(e.get("Type", "")).lower()
            specs = [TABLE_FIELDS[t]] if t in TABLE_FIELDS else list(TABLE_FIELDS.values())
            for want, fields in specs:
                if etype != want:
                    continue
                for fld in fields:
                    v = norm(e.get(fld, ""))
                    if v and v not in q.lower():
                        return v
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", choices=("train", "test"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--qdir", help="question directory of another release, e.g. questions_old/o1/v0/test "
                    "(files incident_<i>_*.json); input path only, the rules are unchanged")
    args = ap.parse_args()
    rows = []
    for gf in sorted(glob.glob(os.path.join(ROOT, "graphs", "*.graphml"))):
        inc = os.path.basename(gf)[:-8]
        nodes, adj = load_graph(gf)
        galerts = [n for n, d in nodes.items() if d.get("type") == "alert"]
        table = load_alert_table(inc)
        qpath = (glob.glob(os.path.join(args.qdir, f"{inc}_*.json"))[0] if args.qdir
                 else os.path.join(ROOT, "questions", f"{inc}_{args.split}.json"))
        for k, item in enumerate(json.load(open(qpath, encoding="utf-8"))):
            q, gold = item["question"], norm(item["answer"])
            end = str(item.get("end_alert"))
            top, gans = graph_answer(q, nodes, adj, galerts)
            tans = table_answer(q, table)
            end_vals = [norm(nodes[m].get("value", "") or nodes[m].get("name", "")) for m in adj.get(end, set())]
            rows.append({"incident": inc, "index": k, "qtype": qtype(q), "named": top == end,
                         "adjacent": any(match(gold, v) for v in end_vals),
                         "graph_correct": match(gold, gans), "table_correct": match(gold, tans)})
    per = defaultdict(lambda: defaultdict(int))
    for r in rows:
        for key in ("named", "adjacent", "graph_correct", "table_correct"):
            per[r["incident"]][key] += r[key]
        per[r["incident"]]["n"] += 1
    n = len(rows)
    summary = {"split": args.split, "questions": n,
               **{key: sum(r[key] for r in rows) for key in ("named", "adjacent", "graph_correct", "table_correct")},
               "per_incident": {k: dict(v) for k, v in sorted(per.items())}}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({"summary": summary, "rows": rows}, open(args.out, "w", encoding="utf-8"), indent=1)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_incident"}))
    for key in ("named", "adjacent", "graph_correct", "table_correct"):
        print(f"{key}: {summary[key]}/{n} = {summary[key] / n:.3f}")


if __name__ == "__main__":
    main()
