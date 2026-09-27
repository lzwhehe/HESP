"""Figure 1 (motivating example): one alert, one model, four ways to split the investigation.

Same task (sec-base-02, true cause: exposed admin panel), same planner (Llama-3.1-8B), same
seed, from the stopping study's archived journal. One row per configuration (who picks probes x
who may stop); probes sit on a common step grid so the decisive observation (red) lines up.

    python paper/figures/make_fig_motivating.py
"""
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "hesp_research" / "results" / "v09_llama8b" / "runs_archive.tar.gz"
TECTONIC = Path("E:/tools/tectonic/tectonic.exe")
ROWS = [("llm", "llm", "run0061_sec-base-02_0_memory_only"),
        ("ctl", "llm", "run0136_sec-base-02_0_hesp_eigc_blind"),
        ("llm", "ctl", "run0316_sec-base-02_0_memory_only_autostop"),
        ("ctl", "ctl", "run0087_sec-base-02_0_hesp_eigc_blind_autostop")]
SHORT = {"auth_log": "auth", "access_pattern": "HTTP", "source_ips": "IPs", "admin_exposure": "admin",
         "user_activity": "egress", "change_ticket": "ticket", "dns_logs": "DNS", "component_versions": "inv.",
         "threat_intel": "TI", "runbook": "runbook"}
DECISIVE = ("admin_exposure", "exposed_no_auth")
X0, SLOT, CHIP = 4.35, 0.98, 0.88


def trace(run):
    with tarfile.open(ARCHIVE) as tf:
        ev = [json.loads(x) for x in tf.extractfile(f"{run}/events.jsonl").read().decode("utf-8").splitlines()]
    steps = []
    for e in ev:
        if e["kind"] == "observation":
            o = e["observation"]
            steps.append(("obs", o["action_id"], (o["action_id"], o["outcome"]) == DECISIVE))
        elif e["kind"] == "action_blocked":
            steps.append(("blocked", e["action_id"], False))
    return steps, next(e["result"] for e in ev if e["kind"] == "run_finished")


def tag(who, what, x, y):
    colour = "llm" if who == "llm" else "hesp"
    name = "LLM" if who == "llm" else "HESP"
    return (rf"\node[anchor=west, draw={colour}, fill={colour}!12, rounded corners=2pt, inner sep=1.6pt, "
            rf"font=\scriptsize] at ({x:.2f},{y:.2f}) {{{what}: \textbf{{{name}}}}};")


def row(probes, stops, run, y):
    steps, res = trace(run)
    out = [tag(probes, "probes", 0.0, y), tag(stops, "stop", 2.05, y)]
    for i, (kind, probe, decisive) in enumerate(steps):
        cx = X0 + i * SLOT + CHIP / 2
        label = SHORT[probe]
        if kind == "blocked":
            out.append(rf"\node[chip, draw=black!35, dashed, text=black!40] at ({cx:.2f},{y:.2f}) {{{label}}};")
            out.append(rf"\draw[black!45] ({cx - 0.3:.2f},{y - 0.13:.2f}) -- ({cx + 0.3:.2f},{y + 0.13:.2f});")
        elif decisive:
            out.append(rf"\node[chip, draw=red!75!black, fill=red!8, text=red!75!black, font=\scriptsize\bfseries] "
                       rf"at ({cx:.2f},{y:.2f}) {{{label}}};")
        else:
            out.append(rf"\node[chip] at ({cx:.2f},{y:.2f}) {{{label}}};")
    xe = X0 + len(steps) * SLOT + 0.1
    if res["verified_simulation"]:
        out.append(rf"\node[anchor=west, font=\scriptsize\bfseries, text=ver] at ({xe:.2f},{y:.2f}) "
                   rf"{{\ding{{51}} verdict: exposed admin panel \ (cost {res['tool_cost_units']})}};")
    else:
        out.append(rf"\node[anchor=west, font=\scriptsize\bfseries, text=red!75!black] at ({xe:.2f},{y:.2f}) "
                   rf"{{\ding{{55}} no verdict \ (budget {res['tool_cost_units']}/10 spent)}};")
    return "\n".join(out)


def main():
    body, ys = [], [2.1, 1.45, 0.65, 0.0]
    for (probes, stops, run), y in zip(ROWS, ys):
        body.append(row(probes, stops, run, y))
    header = "\n".join(rf"\node[font=\scriptsize, text=black!55] at ({X0 + i * SLOT + CHIP / 2:.2f},2.62) {{{i + 1}}};"
                       for i in range(9))
    tex = r"""\documentclass[border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{pifont}
\usepackage{tikz}
\definecolor{hesp}{HTML}{4C72B0}
\definecolor{llm}{HTML}{DD8452}
\definecolor{ver}{HTML}{55A868}
\begin{document}
\begin{tikzpicture}[font=\scriptsize,
  chip/.style={draw=black!45, fill=hesp!8, rounded corners=2pt, minimum height=0.42cm, minimum width=0.88cm,
               inner sep=0.5pt, font=\scriptsize}]
\node[anchor=west, font=\scriptsize, text=black!55] at (0.0,2.62) {who decides};
\node[anchor=east, font=\scriptsize, text=black!55] at (4.25,2.62) {step};
""" + header + "\n" + "\n".join(body) + r"""
\draw[black!25, dashed] (0.0,1.05) -- (17.6,1.05);
\node[anchor=east, font=\scriptsize\itshape, text=black!55] at (17.6,1.2) {the model never concludes on its own};
\node[anchor=east, font=\scriptsize\itshape, text=black!55] at (17.6,-0.4) {a controller-side stop concludes; EIG/cost gets there in 3 probes};
\end{tikzpicture}
\end{document}
"""
    path = HERE / "fig_motivating.tex"
    path.write_text(tex, encoding="utf-8")
    subprocess.run([str(TECTONIC), "-X", "compile", str(path), "--outdir", str(HERE)], check=True)


if __name__ == "__main__":
    main()
