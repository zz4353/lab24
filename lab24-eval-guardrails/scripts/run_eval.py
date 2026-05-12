"""
CI/CD Eval Gate Script — Task A.4
Đọc ragas_summary.json, exit code 1 nếu bất kỳ metric nào < threshold.

Usage:
    python scripts/run_eval.py --threshold faithfulness=0.70
    python scripts/run_eval.py  # dùng default thresholds
"""

import argparse
import json
import os
import sys


DEFAULT_THRESHOLDS = {
    'faithfulness': 0.70,
    'answer_relevancy': 0.65,
    'context_precision': 0.60,
    'context_recall': 0.65,
}

SUMMARY_PATH = os.path.join(os.path.dirname(__file__), '..', 'phase-a', 'ragas_summary.json')


def parse_thresholds(threshold_args: list[str]) -> dict:
    thresholds = DEFAULT_THRESHOLDS.copy()
    for arg in threshold_args:
        metric, value = arg.split('=')
        thresholds[metric.strip()] = float(value.strip())
    return thresholds


def main():
    parser = argparse.ArgumentParser(description='RAGAS eval gate for CI/CD')
    parser.add_argument('--threshold', action='append', default=[], metavar='METRIC=VALUE',
                        help='Override threshold, e.g. faithfulness=0.80')
    parser.add_argument('--summary', default=SUMMARY_PATH, help='Path to ragas_summary.json')
    args = parser.parse_args()

    thresholds = parse_thresholds(args.threshold)

    if not os.path.exists(args.summary):
        print(f"ERROR: {args.summary} not found. Run phase-a/run_ragas.py first.")
        sys.exit(1)

    with open(args.summary) as f:
        summary = json.load(f)

    print("=== RAGAS Eval Gate ===")
    failed = []
    for metric, threshold in thresholds.items():
        score = summary.get(metric, 0.0)
        passed = score >= threshold
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {metric}: {score:.4f} (threshold: {threshold})")
        if not passed:
            failed.append(metric)

    if failed:
        print(f"\nFAILED metrics: {failed}")
        print("Gate BLOCKED — merge prevented.")
        sys.exit(1)
    else:
        print("\nAll metrics passed. Gate OK.")
        sys.exit(0)


if __name__ == "__main__":
    main()
