"""K0 kill test runner (docs/PROTOCOL_SMALL.md): baseline (B) vs external-structure (S) agent on ExCyTIn questions.

Runs on the GPU host against a vLLM OpenAI-compatible server. One SQLite database per incident (k0_build_db.py).

    python k0_run.py --arm B --questions qs.json --db ~/k0/db --out out_B.jsonl
"""
import argparse
import concurrent.futures as cf
import json
import re
import sqlite3
import threading
import time
import urllib.error
import urllib.request

MAX_STEPS = 25
MAX_STR = 100000          # official: beyond this many characters show only the first 15 rows
MAX_ROWS = 15
CAP = 6000                # K0: both arms, per observation
TIMEOUT_S = 30

# ---- official baseline prompt (secgym/agents/baseline_agent.py, O1_PROMPT) ----------------------------------------
O1_PROMPT = """You are a security analyst.
You need to answer a given security question by querying the database.
The logs are stored in a MySQL database, you can use SQL queries to retrieve entries as needed.
Note there are more than 20 tables in the database, so you may need to explore the schema or check example entries to understand the database structure.

Your response should always be a thought-action pair:
Thought: <your reasoning>
Action: <your action>

In Thought, you can analyse and reason about the current situation,
Action can be one of the following:
(1) execute[<your sql query>], which executes the SQL query. For example, execute[DESCRIBE table_name].
(2) submit[<your answer>], which is the final answer to the question

You should only give one thought-action per response. The action from your response will be executed and the result will be shown to you.
Follow the format "Thought: ....\\nAction: ...." exactly.
Do not include any other information in your response. Wait for the response from one action before giving the next thought-action pair. DO NOT make assumptions about the data that are not observed in the logs.
"""

S_PROMPT = """You are a security analyst investigating an incident. Answer the security question using the incident's logs.
The logs are in a MySQL database (more than 20 tables). Security alerts are in the table SecurityAlert; each alert has an
AlertName, a Description, a SystemAlertId, and an Entities field listing the hosts, accounts, IPs, files, processes, URLs
and mailboxes involved.

Your response should always be a thought-action pair:
Thought: <your reasoning>
Action: <your action>

Action can be one of the following:
(1) find_alerts[<keywords>]: list alerts whose name or description contains the keywords (id, name, time).
(2) alert_entities[<SystemAlertId>]: list the entities of one alert, one per line as "Type: field=value".
(3) related_alerts[<entity value>]: list alerts that involve an entity value (an IP, account, host, file, ...). Use it to
    move from one alert to related alerts.
(4) execute[<sql query>]: run any SQL query on the database.
(5) submit[<answer>]: give the final answer: a single value of the type the question asks for, copied exactly from the records.

A good investigation: find the alert the question starts from or refers to, read its entities, follow related alerts
through shared entities, and read the entity the question asks for. Give one thought-action per response.
The list "Evidence observed so far" is kept for you; use it instead of re-querying.
"""

LOCK = threading.Lock()


# ---- environment --------------------------------------------------------------------------------------------------
def _concat(*a):
    return None if any(x is None for x in a) else "".join(str(x) for x in a)


def _locate(sub, s, pos=1):
    if sub is None or s is None:
        return None
    return str(s).lower().find(str(sub).lower(), int(pos) - 1) + 1


def _substring_index(s, delim, count):
    if s is None:
        return None
    parts = str(s).split(str(delim))
    count = int(count)
    return str(delim).join(parts[:count]) if count >= 0 else str(delim).join(parts[count:])


def _regexp(pattern, s):
    try:
        return s is not None and re.search(pattern, str(s), re.I) is not None
    except re.error:
        return False


class Env:
    def __init__(self, path):
        self.con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
        for name, n, fn in [("CONCAT", -1, _concat), ("JSON_UNQUOTE", 1, lambda x: None if x is None else str(x).strip('"')),
                            ("LOCATE", -1, _locate), ("SUBSTRING_INDEX", 3, _substring_index),
                            ("LCASE", 1, lambda x: None if x is None else str(x).lower()),
                            ("UCASE", 1, lambda x: None if x is None else str(x).upper()), ("REGEXP", 2, _regexp)]:
            self.con.create_function(name, n, fn)
        self.tables = [r[0] for r in self.con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

    def _translate(self, q):
        s = q.strip().rstrip(";").strip()
        if re.fullmatch(r"(?i)show\s+(full\s+)?tables(\s+from\s+\w+)?", s):
            return None, [(t,) for t in self.tables]
        if re.fullmatch(r"(?i)show\s+databases", s):
            return None, [("env_monitor_db",)]
        if re.fullmatch(r"(?i)use\s+\w+", s):
            return None, []
        m = re.fullmatch(r"(?i)(?:describe|desc|explain|show\s+(?:full\s+)?columns\s+from)\s+`?(\w+)`?", s)
        if m:
            t = m.group(1)
            match = [x for x in self.tables if x.lower() == t.lower()]
            if not match:
                raise sqlite3.OperationalError(f"Table 'env_monitor_db.{t}' doesn't exist")
            rows = self.con.execute(f'PRAGMA table_info("{match[0]}")').fetchall()
            return None, [(r[1], "text", "YES", "", None, "") for r in rows]
        return s, None

    def query(self, q):
        sql, direct = self._translate(q)
        if direct is not None:
            return direct
        start = time.time()
        self.con.set_progress_handler(lambda: 1 if time.time() - start > TIMEOUT_S else 0, 10000)
        try:
            return self.con.execute(sql).fetchall()
        finally:
            self.con.set_progress_handler(None, 0)

    def observe(self, q):
        try:
            rows = self.query(q)
            obs = str(rows)
            if len(obs) > MAX_STR and len(rows) > MAX_ROWS:
                obs = f"Retrieved {len(rows)} entries. Displaying first {MAX_ROWS} entries.\n{str(rows[:MAX_ROWS])}"
            ok = True
        except Exception as e:  # noqa: BLE001
            obs, ok = f"{e.__class__.__name__}: {e}", False
        return cap(obs), ok


def cap(obs):
    return obs if len(obs) <= CAP else obs[:CAP] + f"\n...[output truncated to {CAP} characters]"


# ---- structured tools (arm S) -------------------------------------------------------------------------------------
SKIP = {"$id", "$ref", "CreatedTimeUtc", "Asset", "IsDomainJoined", "IsValid", "Location", "LastExternalIpAddress",
        "LastIpAddress"}


def entity_lines(raw):
    try:
        ents = json.loads(raw) if raw else []
    except ValueError:
        return []
    out = []
    for e in ents if isinstance(ents, list) else []:
        if not isinstance(e, dict):
            continue
        t = e.get("Type", "?")
        fields = [f"{k}={v}" for k, v in e.items() if k not in SKIP and k != "Type" and isinstance(v, (str, int))
                  and str(v).strip() and len(str(v)) < 400]
        if fields:
            out.append(f"{t}: " + ", ".join(fields))
    return out


def find_alerts(env, arg):
    words = [w for w in re.findall(r"[A-Za-z0-9_.\-]+", arg) if len(w) > 2]
    if not words:
        return "No keywords given."
    rows = env.con.execute('SELECT SystemAlertId, AlertName, TimeGenerated, Description FROM "SecurityAlert"').fetchall()
    scored = {}
    for sid, name, t, desc in rows:
        text = f"{name} {desc}".lower()
        score = sum(1 for w in words if w.lower() in text)
        if score and (sid not in scored or scored[sid][0] < score):
            scored[sid] = (score, name, t)
    top = sorted(scored.items(), key=lambda kv: (-kv[1][0], kv[1][2]))[:10]
    if not top:
        return "No alert matches these keywords."
    return "\n".join(f"id={sid} | {name} | {t}" for sid, (_, name, t) in top)


def alert_entities(env, arg):
    sid = arg.strip().strip("'\"")
    row = env.con.execute('SELECT AlertName, TimeGenerated, Entities FROM "SecurityAlert" WHERE SystemAlertId = ? LIMIT 1',
                          (sid,)).fetchone()
    if row is None:
        row = env.con.execute('SELECT AlertName, TimeGenerated, Entities FROM "SecurityAlert" WHERE AlertName = ? LIMIT 1',
                              (sid,)).fetchone()
    if row is None:
        return "No alert with this SystemAlertId (use find_alerts to get ids)."
    lines = entity_lines(row[2])
    return f"Alert: {row[0]} | {row[1]}\n" + ("\n".join(lines) if lines else "(no entities)")


def related_alerts(env, arg):
    v = arg.strip().strip("'\"")
    if len(v) < 3:
        return "Give a longer entity value."
    rows = env.con.execute('SELECT SystemAlertId, AlertName, TimeGenerated FROM "SecurityAlert" WHERE Entities LIKE ? '
                           'ORDER BY TimeGenerated LIMIT 30', (f"%{v}%",)).fetchall()
    seen, out = set(), []
    for sid, name, t in rows:
        if sid in seen:
            continue
        seen.add(sid)
        out.append(f"id={sid} | {name} | {t}")
    return "\n".join(out[:15]) if out else "No alert involves this value."


PATTERNS = [("IP", r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), ("URL", r"https?://[^\s'\",\]\)]+"),
            ("Email/UPN", r"\b[\w.\-]+@[\w\-]+(?:\.[\w\-]+)+\b"), ("SID", r"\bS-\d-\d+(?:-\d+)+\b"),
            ("Hash", r"\b[a-fA-F0-9]{64}\b|\b[a-fA-F0-9]{40}\b"),
            ("File", r"\b[\w\-]+\.(?:exe|dll|ps1|bat|cmd|vbs|js|docm|docx|xlsm|zip|7z|lnk|hta|msi|sys)\b")]


def update_ledger(ledger, obs):
    for line in obs.splitlines():
        m = re.match(r"^(\w+): (.*)$", line)
        if m and "=" in m.group(2):
            for kv in m.group(2).split(", "):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    if k in ("Address", "HostName", "Name", "Sid", "AadUserId", "UserPrincipalName", "Url", "Value",
                             "CommandLine", "ProcessId", "MailboxPrimaryAddress", "Upn", "Directory", "DnsDomain",
                             "NTDomain", "AadDeviceId", "DisplayName"):
                        ledger.setdefault(f"{m.group(1)}.{k}: {v}", None)
    for t, p in PATTERNS:
        for v in re.findall(p, obs):
            ledger.setdefault(f"{t}: {v}", None)


def ledger_text(ledger):
    items = list(ledger)[-40:]
    return "Evidence observed so far:\n" + ("\n".join(f"- {x}" for x in items) if items else "(none)")


# ---- agent loop ---------------------------------------------------------------------------------------------------
def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().strip("`'\"").lower()


def correct(gold, pred):
    g, p = norm(gold), norm(pred)
    return bool(g) and bool(p) and (g == p or (g in p and len(p) <= max(3 * len(g), len(g) + 40)))


def parse(action):
    action = action.replace("`", "")
    for kind in ("submit", "find_alerts", "alert_entities", "related_alerts", "execute"):
        m = re.findall(kind + r"\[(.*)\]", action, re.DOTALL)
        if m:
            a = m[0]
            if kind == "execute" and ";" in a:
                a = a[:a.index(";")]
            return kind, a
    return "raw", action


class LLM:
    def __init__(self, url, model):
        self.url, self.model = url, model

    def __call__(self, messages):
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0, "max_tokens": 768}).encode()
        req = urllib.request.Request(self.url + "/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"] or ""


def run_episode(llm, env, q, arm):
    question = f"{q.get('context', '')} {q['question']}".strip()
    msgs = [{"role": "system", "content": O1_PROMPT if arm == "B" else S_PROMPT}, {"role": "user", "content": question}]
    ledger, observations, traj = {}, [], []
    submitted, answer, rejected, overflow, steps = False, "", False, False, 0
    for steps in range(1, MAX_STEPS + 1):
        try:
            resp = llm(msgs)
            if "\nAction:" in resp:
                thought, action = resp.strip().split("\nAction:", 1)
                msgs.append({"role": "assistant", "content": resp.strip()})
            else:  # official retry: ask for the action given the thought
                thought = resp.strip()
                action = llm(msgs + [{"role": "user", "content": f"{thought}\nAction:"}]).strip()
                if "Thought" not in thought:
                    thought = f"Thought: {thought}"
                msgs.append({"role": "assistant", "content": f"{thought}\nAction:{action}"})
        except urllib.error.HTTPError as e:
            overflow = e.code == 400
            break
        kind, arg = parse(action)
        if kind == "submit":
            if arm == "S" and not rejected and not any(norm(arg) and norm(arg) in norm(o) for o in observations):
                rejected = True
                obs = (f"Check: your answer '{arg.strip()}' does not appear in any record you retrieved in this "
                       "investigation. Submit a value copied exactly from the records, or keep investigating.")
            else:
                submitted, answer = True, arg.strip()
                traj.append({"action": action[:500], "kind": kind})
                break
        elif arm == "S" and kind in ("find_alerts", "alert_entities", "related_alerts"):
            obs = cap({"find_alerts": find_alerts, "alert_entities": alert_entities,
                       "related_alerts": related_alerts}[kind](env, arg))
        else:
            obs, _ = env.observe(arg)
        observations.append(obs)
        traj.append({"action": action[:500], "kind": kind, "obs": obs[:300]})
        if arm == "S":
            update_ledger(ledger, obs)
            msgs.append({"role": "user", "content": obs + "\n\n" + ledger_text(ledger)})
        else:
            msgs.append({"role": "user", "content": obs})
    return {"submitted": submitted, "answer": answer, "steps": steps, "overflow": overflow, "rejected_once": rejected,
            "correct": submitted and correct(q["answer"], answer), "traj": traj}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("B", "S"), required=True)
    ap.add_argument("--questions", required=True, help="JSON list of {incident, index, question dict}")
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--model", default="qwen2.5-7b-instruct")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    items = json.load(open(args.questions, encoding="utf-8"))
    llm = LLM(args.url, args.model)
    local = threading.local()

    def job(it):
        envs = getattr(local, "envs", None)
        if envs is None:
            envs = local.envs = {}
        if it["incident"] not in envs:
            envs[it["incident"]] = Env(f"{args.db}/{it['incident']}.sqlite")
        t0 = time.time()
        r = run_episode(llm, envs[it["incident"]], it["q"], args.arm)
        r.update({"arm": args.arm, "incident": it["incident"], "index": it["index"], "resistant": it.get("resistant"),
                  "gold": it["q"]["answer"], "seconds": round(time.time() - t0, 1)})
        with LOCK:
            with open(args.out, "a", encoding="utf-8") as f:
                f.write(json.dumps(r) + "\n")
        return r

    done = set()
    try:
        for line in open(args.out, encoding="utf-8"):
            d = json.loads(line)
            done.add((d["incident"], d["index"]))
    except FileNotFoundError:
        pass
    todo = [it for it in items if (it["incident"], it["index"]) not in done]
    with cf.ThreadPoolExecutor(args.workers) as ex:
        for r in ex.map(job, todo):
            print(r["arm"], r["incident"], r["index"], "correct" if r["correct"] else "wrong", r["steps"], r["answer"][:60],
                  flush=True)


if __name__ == "__main__":
    main()
