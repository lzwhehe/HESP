import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.audit import audit_run


def main():
    parser = argparse.ArgumentParser(description="Audit one completed HESP run")
    parser.add_argument("directory")
    args = parser.parse_args()
    result = audit_run(args.directory)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
