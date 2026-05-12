"""
Task B.3 — Human Calibration với Cohen's Kappa
Compute kappa giữa human labels và judge labels.

Prerequisites:
    - pairwise_results.csv (từ judge.py)
    - human_labels.csv (manual labels)

Output: in kappa score + interpretation
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from sklearn.metrics import cohen_kappa_score


PAIRWISE_PATH = os.path.join(os.path.dirname(__file__), 'pairwise_results.csv')
HUMAN_PATH = os.path.join(os.path.dirname(__file__), 'human_labels.csv')


def interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "WORSE than chance — judge sai hệ thống"
    elif kappa < 0.2:
        return "Slight agreement — không tin được"
    elif kappa < 0.4:
        return "Fair agreement — vẫn yếu"
    elif kappa < 0.6:
        return "Moderate agreement — có thể dùng cho monitoring"
    elif kappa < 0.8:
        return "Substantial agreement — production-ready ✓"
    else:
        return "Almost perfect agreement — hiếm gặp"


def main():
    print("=== Task B.3: Cohen's Kappa ===")

    for path in [PAIRWISE_PATH, HUMAN_PATH]:
        if not os.path.exists(path):
            print(f"ERROR: {path} not found.")
            sys.exit(1)

    human_df = pd.read_csv(HUMAN_PATH)
    pairwise_df = pd.read_csv(PAIRWISE_PATH)

    human_labels = human_df['human_winner'].str.lower().tolist()
    judge_labels = pairwise_df.head(len(human_labels))['winner_after_swap'].str.lower().tolist()

    if len(human_labels) != len(judge_labels):
        print(f"WARNING: human has {len(human_labels)} labels, judge has {len(judge_labels)}. Using min.")
        n = min(len(human_labels), len(judge_labels))
        human_labels = human_labels[:n]
        judge_labels = judge_labels[:n]

    print(f"\nComparing {len(human_labels)} labels:")
    print(f"  Human:  {human_labels}")
    print(f"  Judge:  {judge_labels}")

    kappa = cohen_kappa_score(human_labels, judge_labels)
    print(f"\nCohen's kappa: {kappa:.3f}")
    print(f"Interpretation: {interpret_kappa(kappa)}")

    # Agreement breakdown
    agreements = sum(h == j for h, j in zip(human_labels, judge_labels))
    print(f"\nRaw agreement: {agreements}/{len(human_labels)} = {agreements/len(human_labels):.1%}")

    if kappa < 0.6:
        print("\n--- Root Cause Analysis (kappa < 0.6) ---")
        disagreements = [(h, j) for h, j in zip(human_labels, judge_labels) if h != j]
        print(f"Disagreements: {disagreements}")
        print("Possible causes:")
        print("  - Length bias: judge prefers longer answers")
        print("  - Position bias: judge favors Answer A when listed first")
        print("  - Style bias: judge favors formal/structured answers")
        print("  - Domain gap: judge unfamiliar with Vietnamese tax terminology")


if __name__ == "__main__":
    main()
