"""Figure 1, pipeline version in the style of security-venue overviews: dashed stage panels,
numbered stages, concrete artifacts (a posterior table, a probe ranking, JSON decisions, journal
events), and the key output in red. Every value is one real episode from the stopping study's
archived journal (sec-base-02, Llama-3.1-8B planner, controller selects and stops).

    python paper/figures/make_fig_pipeline.py       # writes fig_pipeline.tex and compiles it
"""
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "hesp_research" / "results" / "v09_llama8b" / "runs_archive.tar.gz"
RUN = "run0087_sec-base-02_0_hesp_eigc_blind_autostop"
TECTONIC = Path("E:/tools/tectonic/tectonic.exe")
CAUSES = [("credential_stuffing", "credential stuffing"), ("sqli_probe", "SQL injection"),
          ("misconfig_exposed_admin", "exposed admin panel"), ("authorized_scan", "authorized scan"),
          ("false_positive_monitor", "monitoring FP"), ("insider_exfil", "insider exfiltration"),
          ("vuln_component", "vulnerable component"), ("dns_c2", "DNS C2"), ("other", "other")]


def episode():
    with tarfile.open(ARCHIVE) as tf:
        ev = [json.loads(x) for x in tf.extractfile(f"{RUN}/events.jsonl").read().decode("utf-8").splitlines()]
    first = next(e for e in ev if e["kind"] == "evidence_update")
    posts = [first["evidence"]["before"]] + [e["evidence"]["after"] for e in ev if e["kind"] == "evidence_update"]
    preds = [e for e in ev if e["kind"] == "prediction_registered"]
    obs = [e["observation"] for e in ev if e["kind"] == "observation"]
    decisions = [e["decision"] for e in ev if e["kind"] == "planner_decision"]
    verdict = next(e for e in ev if e["kind"] == "independent_verification")
    return posts, preds, obs, decisions, verdict


def tt(s):
    return r"\texttt{" + s.replace("_", r"\_") + "}"


def ledger_table(posts, winner, x0, y0):
    """Posterior table: rows are causes, columns are steps; cell shade is belief."""
    out, cw, rh = [], 0.66, 0.38
    for j, lab in enumerate(["prior", "IPs", "HTTP", "admin"]):
        out.append(rf"\node[lab] at ({x0 + (j + 0.5) * cw:.2f},{y0 + 0.28:.2f}) {{{lab}}};")
    for i, (key, name) in enumerate(CAUSES):
        y = y0 - (i + 0.5) * rh
        win = key == winner
        style = r", text=red!75!black, font=\scriptsize\bfseries" if win else ""
        out.append(rf"\node[lab, anchor=east{style}] at ({x0 - 0.06:.2f},{y:.2f}) {{{name}}};")
        for j, post in enumerate(posts):
            v = post[key]
            shade = int(round(min(1.0, v) * 85))
            cell = f"hesp!{shade}" if v >= 0.0015 else "white"
            txt = "0" if v < 0.005 else f".{int(round(v * 100)):02d}"
            col = "white" if shade > 45 else "black!75"
            border = "red!80!black, line width=0.9pt" if (win and j == len(posts) - 1) else "black!25"
            out.append(rf"\draw[draw={border}, fill={cell}] ({x0 + j * cw:.2f},{y - rh / 2:.2f}) rectangle "
                       rf"({x0 + (j + 1) * cw:.2f},{y + rh / 2:.2f});")
            out.append(rf"\node[lab, text={col}] at ({x0 + (j + 0.5) * cw:.2f},{y:.2f}) {{{txt}}};")
    return "\n".join(out)


def ranking(pred, x0, y0, proposed):
    """First-step EIG/cost ranking as bars; the probe run is red, the LLM's proposal is marked."""
    rows, out, rh, bmax = pred["modeled_rankings"][:5], [], 0.42, 1.45
    top = max(r["score"] for r in rows)
    for i, r in enumerate(rows):
        y = y0 - (i + 0.5) * rh
        run = r["action_id"] == pred["action"]["id"]
        colour = "red!75!black" if run else "black!40"
        out.append(rf"\node[lab, anchor=east] at ({x0:.2f},{y:.2f}) {{{tt(r['action_id'])}}};")
        out.append(rf"\fill[{colour}] ({x0 + 0.08:.2f},{y - 0.12:.2f}) rectangle "
                   rf"({x0 + 0.08 + bmax * r['score'] / top:.2f},{y + 0.12:.2f});")
        tag = r" $\leftarrow$ run" if run else ""
        out.append(rf"\node[lab, anchor=west] at ({x0 + 0.12 + bmax * r['score'] / top:.2f},{y:.2f}) "
                   rf"{{{r['score']:.2f}{tag}}};")
        if r["action_id"] == proposed:
            out.append(rf"\node[lab, anchor=west, text=llm!90!black] (prop) at ({x0 + 1.2:.2f},{y:.2f}) "
                       r"{$\leftarrow$ \textit{LLM's pick}};")
    return "\n".join(out)


def tikz(posts, preds, obs, decisions, verdict):
    winner = verdict["hypothesis"]
    proposed = decisions[0]["action_id"]
    lead = posts[-1][winner]
    body = r"""
% ---------- planner band (top)
\node[card=llm, minimum width=17.2cm, minimum height=0.95cm] (planner) at (8.9,8.55) {};
\node[anchor=west, font=\footnotesize\bfseries] at (0.45,8.72) {Local LLM planner};
\node[anchor=west, lab] at (0.45,8.35) {Llama-3.1-8B, served locally};
\node[anchor=west, lab, font=\scriptsize\ttfamily, text=black!80] at (4.15,8.72)
  {\{"kind": "action", "action\_id": "PROPOSED"\} \ \ \textrm{(3 of 3 decisions)}};
\node[anchor=west, lab] at (4.15,8.35) {proposes probes but never issues a verdict; it sees no ranking};
\draw[flow=llm] (7.95,8.07) -- (7.95,7.45) node[midway, right, lab, text=llm!90!black] {propose};
\draw[flow=llm, dashed] (14.9,8.07) -- (14.9,7.45) node[midway, right, lab, text=llm!90!black] {finish (never used)};

% ---------- alert
\node[doc] (alert) at (0.75,4.9) {};
\draw[fill=red!75!black] (0.75,5.05) -- (0.97,4.68) -- (0.53,4.68) -- cycle;
\node[text=white, font=\tiny\bfseries] at (0.75,4.79) {!};
\node[lab, align=center] at (0.75,4.15) {alert\\sec-base-02};
\draw[flow=black!60] (1.2,4.9) -- (1.85,4.9);

% ---------- stage 1: ledger
\draw[stage] (1.9,1.55) rectangle (7.1,7.35);
\node[stagehead] at (2.0,7.12) {\stepnum{1} Hypothesis Ledger};
LEDGER
\node[lab, anchor=west, align=left] at (2.0,1.88) {\faLock\ $P(o\mid h,a)$ counted from LLM-free runs};

% ---------- stage 2: selection and probing
\draw[stage] (7.4,3.35) rectangle (12.35,7.35);
\node[stagehead] at (7.5,7.12) {\stepnum{2} EIG/cost Probe Selection};
\node[lab, anchor=west, text=black!65] at (7.5,6.42) {\textit{step 1 of 3: expected information gain per cost}};
RANKING
\node[card=env, minimum width=4.95cm, minimum height=1.6cm] (probe) at (9.87,2.35) {};
\node[anchor=west, font=\footnotesize\bfseries] at (7.55,2.9) {Read-only probes};
\foreach \y in {2.45,2.7,2.95} {\draw[draw=black!55, fill=black!8, rounded corners=1pt] (11.45,\y) rectangle (12.1,\y+0.2); \fill[ver] (11.56,\y+0.1) circle (0.04);}
\node[anchor=west, lab, align=left, font=\scriptsize] at (7.48,2.25) {OBS1\\OBS2\\OBS3};
\draw[flow=red!75!black] (9.3,3.35) -- (9.3,3.15);
\draw[flow=hesp, rounded corners=4pt] (7.4,2.35) -- (5.72,2.35) -- (5.72,2.74);
\node[lab, text=hesp, anchor=north] at (6.5,2.3) {Bayes update};
\draw[flow=hesp, rounded corners=6pt] (12.35,5.2) -- (12.6,5.2);
\node[font=\small\bfseries, text=hesp] at (9.95,3.6) {$\circlearrowleft$ \scriptsize 3 probes};

% ---------- stage 3: evidence rule and stop
\draw[stage] (12.65,1.55) rectangle (17.5,7.35);
\node[stagehead] at (12.75,7.12) {\stepnum{3} Evidence Rule \& Stop};
\node[card=hesp, minimum width=4.6cm, minimum height=1.1cm] at (15.07,5.88) {};
\node[anchor=west, lab, align=left] at (12.85,5.88)
  {leader $p = LEAD \ge 0.8$ \hfill {\color{ver}\ding{51}}\\ cites current evidence o3 \hfill {\color{ver}\ding{51}}};
\draw[flow=black!60] (15.07,5.4) -- (15.07,4.98);
\node[card=red!75!black, minimum width=4.6cm, minimum height=0.75cm, font=\footnotesize\bfseries, text=red!75!black]
  at (15.07,4.6) {Controller stop};
\draw[flow=black!60] (15.07,4.22) -- (15.07,3.84);
\node[card=black!50, minimum width=4.6cm, minimum height=0.95cm, align=center] at (15.07,3.35)
  {\footnotesize\bfseries\color{red!75!black} Verdict: exposed admin panel\\[-1pt] \scriptsize cites o3, o2, o1};
\draw[flow=black!60] (15.07,2.87) -- (15.07,2.47);
\node[card=ver, dashed, minimum width=4.6cm, minimum height=0.62cm, align=center, text=ver] at (15.07,2.12)
  {\footnotesize\bfseries Independent verifier {\ding{51}}\\[-2pt] \scriptsize\itshape offline evaluation only};

% ---------- journal band (bottom)
\draw[stage] (0.2,0.05) rectangle (17.5,1.25);
\node[stagehead] at (0.3,1.22) {Journal \& Audit};
JOURNAL
"""
    journal = []
    chips = ["request", "decision", "prediction", "observation", "update"]
    x = 0.45
    for k, c in enumerate(chips * 1):
        journal.append(rf"\node[chip] at ({x + 0.72:.2f},0.4) {{{c}}};")
        if k < len(chips) - 1:
            journal.append(rf"\draw[flow=black!50] ({x + 1.47:.2f},0.4) -- ({x + 1.63:.2f},0.4);")
        x += 1.62
    journal.append(r"\node[lab] at (8.95,0.4) {$\times 3$ \quad $\to$};")
    x = 9.6
    for c in ["stop", "verify"]:
        journal.append(rf"\node[chip] at ({x + 0.72:.2f},0.4) {{{c}}};")
        x += 1.62
    journal.append(r"\node[lab, anchor=west, align=left] at (12.95,0.5) "
                   r"{each prediction written \emph{before}\\ its observation; audit replays it \ {\color{ver}\ding{51}}};")
    body = (body.replace("LEDGER", ledger_table(posts, winner, 4.4, 6.18))
            .replace("RANKING", ranking(preds[0], 9.4, 6.12, proposed))
            .replace("PROPOSED", proposed.replace("_", r"\_"))
            .replace("LEAD", f"{lead:.2f}")
            .replace("JOURNAL", "\n".join(journal)))
    for k, o in enumerate(obs, 1):
        body = body.replace(f"OBS{k}", rf"o{k}: {tt(o['action_id'])} $\to$ {tt(o['outcome'])}")
    return r"""\documentclass[border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{pifont,fontawesome5}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shadows}
\definecolor{hesp}{HTML}{4C72B0}
\definecolor{llm}{HTML}{DD8452}
\definecolor{env}{HTML}{8C8C8C}
\definecolor{ver}{HTML}{55A868}
\newcommand{\stepnum}[1]{\tikz[baseline=-0.6ex]\node[circle, fill=black, text=white, font=\scriptsize\bfseries, inner sep=0.8pt, minimum size=10pt] {#1};}
\begin{document}
\begin{tikzpicture}[font=\scriptsize,
  lab/.style={font=\scriptsize, inner sep=1pt},
  stage/.style={draw=black!70, dashed, line width=0.8pt, rounded corners=6pt},
  stagehead/.style={anchor=north west, font=\footnotesize\bfseries\itshape},
  card/.style={draw=#1, line width=0.7pt, fill=white, rounded corners=3pt, drop shadow={opacity=0.15, shadow xshift=0.4pt, shadow yshift=-0.4pt}},
  chip/.style={draw=black!40, fill=hesp!10, rounded corners=2pt, minimum width=1.44cm, minimum height=0.42cm, font=\scriptsize},
  doc/.style={draw=black!60, fill=white, minimum width=0.72cm, minimum height=0.9cm, line width=0.6pt},
  server/.style={draw=black!55, fill=black!8, minimum width=0.7cm, minimum height=0.8cm, rounded corners=1pt},
  flow/.style={-{Stealth[length=5pt]}, line width=0.8pt, draw=#1}]
""" + body + r"""
\end{tikzpicture}
\end{document}
"""


def main():
    posts, preds, obs, decisions, verdict = episode()
    tex = HERE / "fig_pipeline.tex"
    tex.write_text(tikz(posts, preds, obs, decisions, verdict), encoding="utf-8")
    subprocess.run([str(TECTONIC), "-X", "compile", str(tex), "--outdir", str(HERE)], check=True)
    print(HERE / "fig_pipeline.pdf")


if __name__ == "__main__":
    main()
