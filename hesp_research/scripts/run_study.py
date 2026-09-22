"""Run offline paired fixture validation, not a real-model benchmark."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hesp.study import run_study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    report = run_study(args.output, args.repeats, args.seed)
    print("Paired fixture study saved. No real-model efficacy claim.")
    return 0 if all(r["verified_fraction"] == 1 for r in report["modes"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
