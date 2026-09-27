#!/usr/bin/env python3
"""Generate the HESP overview diagram with Gemini image generation (academic-plotting skill,
Workflow 1). Three attempts per run, as the skill prescribes; pick the best by its rubric.

The API key is read from the GEMINI_API_KEY environment variable, or else from the file
~/.config/hesp/gemini_api_key (one line). It is never printed, logged, or written anywhere.
Only the diagram description below is sent to Google; no data, logs, or manuscript text.

    python paper/figures/gen_fig_overview_gemini.py [--style minimal|academic] [--model NAME]
Output: paper/figures/gemini/fig_overview_<style>_attempt{1,2,3}.png (git-ignored)
"""
import argparse
import base64
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
OUT = HERE / "gemini"
KEY_FILE = Path.home() / ".config" / "hesp" / "gemini_api_key"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

FRAMING = """Create an ultra-clean, modern technical architecture diagram for a top security conference paper
(USENIX Security / IEEE S&P style). It will be printed as Figure 1 at full page width (7 inches) in a
two-column paper, so every label must be readable at that size. The diagram should feel confident,
precise, and authoritative: a premium design system, like the best systems-paper figures. Wide
landscape canvas, aspect ratio about 3:1."""

STYLES = {
    "minimal": """VISUAL STYLE - MODERN MINIMAL:
- Ultra-clean geometric shapes with crisp edges
- Section backgrounds are soft desaturated fills: slate blue (#E8EDF2) for the controller region,
  warm sand (#F5F0E8) for the planner, cool mint (#E8F2EE) for the verifier
- Component boxes have rounded corners (12px radius), no visible border, and float on the section
  background with a very subtle shadow (1px, 4px blur, rgba(0,0,0,0.06))
- One accent color per section used sparingly on key elements: deep blue (#2563EB) for the
  controller, amber (#D97706) for the planner, emerald (#059669) for the verifier, slate (#6B7280)
  for the probes
- Arrows are thin (1.5px), dark gray (#6B7280), with a small filled circle at the source and a clean
  arrowhead at the target
- Typography: clean sans-serif (Inter or Helvetica), titles semibold, body regular, all text dark
  charcoal (#1F2937)
- Labels inside boxes, not beside them; generous whitespace, at least 24px between elements
- No decorative elements, no icons: the structure speaks""",
    "academic": """VISUAL STYLE - CLASSIC ACCENT BAR:
- Pale gray (#F7F7F5) section panels, each with a thick colored LEFT ACCENT BAR (8px)
- Content boxes: white fill, thin #DDDDDD border, 4px rounded corners
- Section palette: blue #4A90D9 (controller), amber #D4A252 (planner), teal #5BA58B (verifier),
  slate #7B8794 (probes)
- Serif typography like Times for all labels, bold titles, regular body
- Arrows colored like their source section, 1.5px, simple filled arrowheads
- Clean, flat, zero decoration, reads correctly in grayscale""",
}

LAYOUT = """LAYOUT (left to right, one horizontal row, then one band along the bottom):

1. Far left, small box: title "Alert", subtitle "one incident".

2. Box "Planner" with subtitle "local LLM (7B-72B)" and one line "returns action, finish, or stop".

3. Center, the largest region, titled "HESP controller" with a small caption at its top right
   "owns state, probe choice, and acceptance". Inside it, three boxes:
   a. Left, tall box "Hypothesis ledger", text "posterior p(h) over 8 causes + other".
      Inside it, a tiny bar chart with four groups of nine thin vertical bars, labeled under each
      group "prior", "IPs", "HTTP", "admin". In "prior" all nine bars are equal and short. In "IPs"
      four bars are medium height. In "HTTP" three bars are medium height. In "admin" exactly one
      bar is tall and blue and the others are nearly flat. Above the tall bar, small text "p = 0.97".
      Under the chart, small italic text "one real episode: 9 causes -> 1 in 3 probes".
   b. Right top box "Probe selection", text "rank legal probes by EIG(a)/c(a); run the best".
   c. Right bottom box "Acceptance and stop", text "verdict needs p >= 0.8 and current support;
      the controller may also stop".

4. Right of the controller, box "Read-only probes", text "auth, HTTP, sources, DNS, egress, config,
   inventory, tickets, threat intel".

5. Below "Read-only probes", box "Verifier", text "correct cause and a cited signature unique to it".

6. A thin dashed band along the whole bottom of the figure, text "Journal and audit: every prediction
   is written before the observation it predicts; every episode is replayed".

CRITICAL: spell every label EXACTLY as written above. Do not add any other words."""

CONNECTIONS = """CONNECTIONS (each arrow carries a small numbered circle badge):
- Alert -> Planner (no badge)
- Controller -> Planner, badge "1", label "request"
- Planner -> Controller, badge "2", label "decision"
- Probe selection -> Read-only probes, badge "3", label "run"
- Read-only probes -> Hypothesis ledger, badge "4", label "outcome"
- Acceptance and stop -> Verifier, badge "5", label "verdict"
- A short dashed arrow from the controller region down to the Journal band (no badge)"""

CONSTRAINTS = """CONSTRAINTS:
- NO icons, clip art, illustrations, emoji, 3D, gradients, or textures
- NO figure number, NO caption, NO title above the diagram, NO watermark
- Pure white page background (#FFFFFF) outside the section panels
- Every text label spelled EXACTLY as specified; no invented labels, no lorem ipsum
- All text horizontal and legible at 7 inches wide; nothing overlaps, nothing is cut off
- Publication quality for a top security venue"""


def api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    for path in (KEY_FILE, KEY_FILE.with_suffix(".txt")):   # Notepad appends .txt
        if not key and path.exists():
            key = path.read_text(encoding="utf-8-sig").strip()
    if not key:
        sys.exit(f"No key: set GEMINI_API_KEY or write it to {KEY_FILE} (never into the repository).")
    return key


def generate(key, model, prompt, path):
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}}).encode()
    req = urllib.request.Request(ENDPOINT.format(model=model), data=body, method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:   # report the API's message, never the request headers
        detail = exc.read().decode("utf-8", "replace")[:500]
        print(f"HTTP {exc.code}: {detail}")
        return None
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline:
                path.write_bytes(base64.b64decode(inline["data"]))
                return path
            if part.get("text"):
                print("model text:", part["text"][:300])
    print("no image in response")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--style", choices=sorted(STYLES), default="minimal")
    ap.add_argument("--model", default="gemini-3-pro-image-preview")
    ap.add_argument("--attempts", type=int, default=3)
    args = ap.parse_args()
    key = api_key()
    prompt = "\n\n".join([FRAMING, STYLES[args.style], LAYOUT, CONNECTIONS, CONSTRAINTS])
    OUT.mkdir(exist_ok=True)
    (OUT / f"prompt_{args.style}.txt").write_text(prompt, encoding="utf-8")   # reproducibility; no key
    made = []
    for i in range(1, args.attempts + 1):
        if i > 1:
            time.sleep(2)
        path = generate(key, args.model, prompt, OUT / f"fig_overview_{args.style}_attempt{i}.png")
        print(f"attempt {i}: {path or 'failed'}")
        if path:
            made.append(path)
    if not made:
        sys.exit(1)


if __name__ == "__main__":
    main()
