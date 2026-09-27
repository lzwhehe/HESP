"""Load OTRF Security-Datasets host recordings (zip of JSON lines or a JSON array) into dicts.

The recordings stay under external/otrf/ (git-ignored); nothing here executes their content.
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "external" / "otrf"


def events(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            raw = zf.read(name).decode("utf-8", "replace").strip()
            if not raw:
                continue
            if raw.startswith("["):
                items = json.loads(raw)
            else:
                items = []
                for line in raw.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            items.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            for item in items:
                if isinstance(item, dict):
                    yield item


def manifest():
    return json.loads((ROOT / "manifest.json").read_text())
