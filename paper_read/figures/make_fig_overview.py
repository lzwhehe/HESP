"""Figure 1 (overview of HESP) as a standalone TikZ picture, drawn in the paper's own font.

Style: classic academic (flat, no decoration, grayscale-safe), colourblind-safe "deep" palette,
no text below 7 pt at final size (the picture is typeset at its printed width, never scaled).
The posterior strip inside the ledger is one real episode read from the stopping study's
archived journal (sec-base-02, controller selects and stops).

    python paper/figures/make_fig_overview.py          # writes fig_overview.tex and compiles it
    powershell -File paper/figures/pdf2png.ps1 paper/figures/fig_overview.pdf preview.png 3
"""
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "hesp_research" / "results" / "v09_llama8b" / "runs_archive.tar.gz"
RUN = "run0087_sec-base-02_0_hesp_eigc_blind_autostop"
ORDER = ["credential_stuffing", "sqli_probe", "misconfig_exposed_admin", "authorized_scan", "false_positive_monitor",
         "insider_exfil", "vuln_component", "dns_c2", "other"]
STEP_LABELS = {"source_ips": "IPs", "access_pattern": "HTTP", "admin_exposure": "admin"}
TECTONIC = Path("E:/tools/tectonic/tectonic.exe")


def episode():
    with tarfile.open(ARCHIVE) as tf:
        events = [json.loads(x) for x in tf.extractfile(f"{RUN}/events.jsonl").read().decode("utf-8").splitlines()]
    first = next(e for e in events if e["kind"] == "evidence_update")
    steps, obs = [("prior", first["evidence"]["before"])], None
    for e in events:
        if e["kind"] == "observation":
            obs = e["observation"]["action_id"]
        elif e["kind"] == "evidence_update":
            steps.append((STEP_LABELS.get(obs, obs), e["evidence"]["after"]))
    verdict = next(e for e in events if e["kind"] == "independent_verification")
    return steps, verdict


def posterior_strip(steps, winner, x0, y0, bw=0.074, gap=0.18, hmax=1.2):
    """Four groups of nine bars (one per hypothesis); bar height = posterior."""
    out = []
    for s, (label, scores) in enumerate(steps):
        gx = x0 + s * (9 * bw + gap)
        out.append(rf"\draw[axis] ({gx - 0.03:.3f},{y0:.3f}) -- ({gx + 9 * bw + 0.03:.3f},{y0:.3f});")
        for i, h in enumerate(ORDER):
            p, x = scores[h], gx + i * bw
            if p < 0.0015:
                out.append(rf"\fill[elim] ({x + 0.015:.3f},{y0:.3f}) rectangle ({x + bw - 0.015:.3f},{y0 + 0.03:.3f});")
            else:
                style = "win" if h == winner and s > 0 else "bar"
                out.append(rf"\fill[{style}] ({x + 0.01:.3f},{y0:.3f}) rectangle ({x + bw - 0.01:.3f},{y0 + p * hmax:.3f});")
        out.append(rf"\node[lab, anchor=north] at ({gx + 4.5 * bw:.3f},{y0 - 0.03:.3f}) {{{label}}};")
    last = steps[-1][1][winner]
    wx = x0 + 3 * (9 * bw + gap) + ORDER.index(winner) * bw
    out.append(rf"\node[lab, text=hesp, anchor=east] at ({wx - 0.02:.3f},{y0 + last * hmax - 0.12:.3f}) {{$p{{=}}{last:.2f}$}};")
    return "\n".join(out)


PREAMBLE = r"""\documentclass[border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{tikz}
\usetikzlibrary{arrows.meta}
\definecolor{hesp}{HTML}{4C72B0}
\definecolor{llm}{HTML}{DD8452}
\definecolor{env}{HTML}{8C8C8C}
\definecolor{ver}{HTML}{55A868}
\begin{document}
\begin{tikzpicture}[font=\footnotesize,
  box/.style={draw=#1, line width=0.7pt, fill=white, rounded corners=2pt, align=flush left, inner sep=4pt},
  lab/.style={font=\scriptsize, text=black!70, inner sep=1pt},
  flow/.style={-{Stealth[length=5pt]}, line width=0.8pt, draw=#1},
  step/.style={circle, fill=#1, text=white, font=\scriptsize\bfseries, inner sep=0pt, minimum size=10pt},
  axis/.style={draw=black!35, line width=0.4pt},
  bar/.style={fill=black!55}, win/.style={fill=hesp}, elim/.style={fill=black!25}]
"""

BODY = r"""
% ---- controller region (x 6.0..13.4)
\fill[hesp!7] (6.0,0.75) rectangle (13.4,5.55);
\fill[hesp] (6.0,0.75) rectangle (6.12,5.55);
\node[font=\small\bfseries, text=hesp, anchor=north west] at (6.3,5.47) {HESP controller};
\node[lab, anchor=north east] at (13.3,5.44) {owns state, probe choice, and acceptance};

% ledger (x 6.3..10.0) with one real episode
\draw[hesp, line width=0.7pt, fill=white, rounded corners=2pt] (6.3,1.0) rectangle (10.0,4.95);
\node[anchor=north west, align=flush left, text width=3.45cm, inner sep=0pt] at (6.45,4.8)
  {\textbf{Hypothesis ledger}\\[2pt] posterior $p(h)$ over 8 causes and \textit{other}, updated by Bayes' rule from $P(o\mid h,a)$};
STRIP
\node[lab, anchor=south west, align=flush left] at (6.42,1.08) {\textit{one real episode:}\\ \textit{9 causes $\to$ 1 in 3 probes}};

% selection and acceptance (x 10.25..13.15)
\node[box=hesp, anchor=north west, text width=2.78cm] at (10.25,4.95)
  {\textbf{Probe selection}\\[2pt] rank legal probes by $\mathrm{EIG}(a)/c(a)$ and run the best};
\node[box=hesp, anchor=north west, text width=2.78cm] (acc) at (10.25,3.05)
  {\textbf{Acceptance and stop}\\[2pt] verdict needs $p\ge0.8$\\ and current support;\\ the controller may\\ also stop by itself};

% ---- alert, planner, probes, verifier
\node[box=black!70, text width=1.45cm, align=center] (alert) at (0.85,3.15) {\textbf{Alert}\\[2pt] one incident};
\node[box=llm, text width=2.3cm] (plan) at (3.75,3.15)
  {\textbf{Planner}\\[2pt] local LLM (7B--72B)\\ returns \textit{action},\\ \textit{finish}, or \textit{stop}};
\node[box=env, anchor=north west, text width=2.55cm] (probe) at (14.3,4.95)
  {\textbf{Read-only probes}\\[2pt] auth, HTTP, sources, DNS, egress, config, inventory, tickets, threat intel};
\node[box=ver, anchor=north west, text width=2.55cm] (verif) at (14.3,2.3)
  {\textbf{Verifier}\\[2pt] correct cause and a cited signature unique to it};

% ---- journal across the whole pipeline
\draw[black!45, dashed, line width=0.6pt, rounded corners=2pt] (2.4,-0.4) rectangle (17.2,0.3);
\node[font=\scriptsize, text=black!75] at (9.8,-0.05)
  {\textbf{Journal and audit}: every prediction is written before the observation it predicts; every episode is replayed};
\draw[black!45, -{Stealth[length=4pt]}, line width=0.6pt, dashed] (9.7,0.75) -- (9.7,0.32);

% ---- flows with numbered steps
\draw[flow=black!60] (alert.east) -- (plan.west);
\draw[flow=hesp] (6.0,3.6) -- node[step=hesp, above=3pt] {1} (plan.east |- 0,3.6);
\draw[flow=llm] (plan.east |- 0,2.7) -- node[step=llm, below=3pt] {2} (6.0,2.7);
\draw[flow=hesp] (13.4,4.35) -- node[step=hesp, above=3pt] {3} (14.3,4.35);
\draw[flow=env] (14.3,3.35) -- node[step=env, below=3pt] {4} (13.4,3.35);
\draw[flow=ver] (13.4,1.55) -- node[step=ver, above=3pt] {5} (14.3,1.55);
\end{tikzpicture}
\end{document}
"""


def main():
    steps, verdict = episode()
    strip = posterior_strip(steps, verdict["hypothesis"], 6.55, 2.05)
    tex = HERE / "fig_overview.tex"
    tex.write_text(PREAMBLE + BODY.replace("STRIP", strip), encoding="utf-8")
    subprocess.run([str(TECTONIC), "-X", "compile", str(tex), "--outdir", str(HERE)], check=True)
    print(HERE / "fig_overview.pdf")
    for label, scores in steps:
        print(label, {h: round(scores[h], 3) for h in ORDER})


if __name__ == "__main__":
    main()
