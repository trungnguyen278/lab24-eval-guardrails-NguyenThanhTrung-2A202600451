"""
CI/CD Evaluation Gate Script
Used by .github/workflows/eval-gate.yml to enforce quality thresholds.
Exit code 1 if any metric falls below its threshold.
"""

import argparse
import json
import sys


def parse_thresholds(threshold_str: str) -> dict:
    thresholds = {}
    for item in threshold_str.split(","):
        key, value = item.strip().split("=")
        thresholds[key.strip()] = float(value.strip())
    return thresholds


def main():
    parser = argparse.ArgumentParser(description="RAG Eval Gate")
    parser.add_argument(
        "--threshold",
        type=str,
        default="faithfulness=0.85,answer_relevancy=0.80,context_precision=0.70,context_recall=0.75",
        help="Comma-separated metric=threshold pairs"
    )
    parser.add_argument(
        "--results",
        type=str,
        default="phase-a/ragas_summary.json",
        help="Path to RAGAS summary JSON"
    )
    args = parser.parse_args()

    thresholds = parse_thresholds(args.threshold)

    with open(args.results) as f:
        results = json.load(f)

    print("=" * 50)
    print("RAG Evaluation Gate Check")
    print("=" * 50)

    all_passed = True
    for metric, threshold in thresholds.items():
        actual = results.get(metric, 0)
        passed = actual >= threshold
        status = "PASS" if passed else "FAIL"
        print(f"  {metric}: {actual:.4f} (threshold: {threshold:.2f}) [{status}]")
        if not passed:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("Result: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print("Result: SOME CHECKS FAILED - blocking merge")
        sys.exit(1)


if __name__ == "__main__":
    main()
