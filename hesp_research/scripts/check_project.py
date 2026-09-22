"""Save actual unittest results, including the full test transcript."""

import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hesp.controller import source_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    transcript = stream.getvalue()
    (output / "unittest.txt").write_text(transcript, encoding="utf-8")
    report = {
        "kind": "software_verification_not_research_results",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "source_sha256": source_hash(),
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
    }
    (output / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(transcript)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
