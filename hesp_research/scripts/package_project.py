"""Package source, docs, and recorded checks, excluding caches and local runs."""

import argparse
import hashlib
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = Path(args.output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    included = []
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root)
            if not path.is_file() or any(p in {"__pycache__", ".git", "runs", ".venv"} for p in rel.parts):
                continue
            if path.suffix not in {".py", ".md", ".txt", ".json", ".jsonl"}:
                continue
            if rel.parts[0] not in {"hesp", "tests", "scripts", "docs", "results", "README.md"}:
                continue
            archive.write(path, "hesp_research/" + rel.as_posix())
            included.append(rel.as_posix())
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP integrity check failed")
    print(f"Packaged {len(included)} files: {target}")
    print("SHA256 " + hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
