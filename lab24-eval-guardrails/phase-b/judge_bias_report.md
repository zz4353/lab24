# Judge Bias Observations Report — Task B.4

Phân tích position bias và length bias từ `pairwise_results.csv`.

---

## Setup

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('pairwise_results.csv')
```

---

## Bias 1: Position Bias

**Hypothesis:** Judge có xu hướng chọn answer được liệt kê first (Answer A) do position bias.

```python
run1_a_wins = (df['run1_winner'] == 'A').sum()
total = len(df)
print(f"A wins as first: {run1_a_wins} / {total} = {run1_a_wins / total:.1%}")
# Expected ~50% if no bias. >55% suggests position bias.
```

**Result:**

| Metric | Value |
|---|---|
| A wins when listed first (run1) | 8 / 30 = 27% |
| B wins when listed first (run2, flipped) | 22 / 30 = 73% |
| Expected (no bias) | ~50% |

**Observation:** Judge KHÔNG có position bias theo nghĩa thông thường — judge nhất quán chọn B (GPT-4o-mini answer) bất kể vị trí (27% vs 73%). Đây là quality bias: B answers thực sự tốt hơn A (context[0]).

---

## Bias 2: Length Bias

**Hypothesis:** Judge có xu hướng chọn answer dài hơn (mistaking length for quality).

```python
df['len_a'] = df['answer_a'].str.len()
df['len_b'] = df['answer_b'].str.len()
df['len_diff'] = df['len_b'] - df['len_a']

b_wins_when_longer = ((df['winner_after_swap'] == 'B') & (df['len_diff'] > 0)).sum()
b_total_longer = (df['len_diff'] > 0).sum()
print(f"B wins when B is longer: {b_wins_when_longer} / {b_total_longer}")
```

**Result:**

| Metric | Value |
|---|---|
| Cases where B is longer | 10 / 30 |
| B wins when B is longer | 10 / 10 = **100%** |
| Expected (no bias) | ~50% |

**Observation:** Rất mạnh — khi B dài hơn A, B thắng 100% (10/10). Đây là length bias rõ ràng.

---

## Chart: Win Rate by Answer Length Quartile

*(Generated after running judge.py — paste chart here)*

```python
df['length_group'] = pd.qcut(df['len_b'] - df['len_a'], q=4, labels=['shorter', 'slightly shorter', 'slightly longer', 'longer'])
win_rate = df.groupby('length_group')['winner_after_swap'].apply(lambda x: (x == 'B').mean())

fig, ax = plt.subplots(figsize=(8, 4))
win_rate.plot(kind='bar', ax=ax, color='steelblue')
ax.axhline(0.5, color='red', linestyle='--', label='Expected (no bias)')
ax.set_ylabel('B Win Rate')
ax.set_title('Length Bias: B Win Rate by Relative Length')
ax.legend()
plt.tight_layout()
plt.savefig('length_bias_chart.png')
```

---

## Conclusion & Mitigation Strategy

| Bias | Detected | Severity | Mitigation Applied |
|---|---|---|---|
| Position bias | Không rõ (quality dominates) | Low | Swap-and-average (2 runs) ✓ |
| Length bias | B wins 100% khi B dài hơn | **High** | Add length normalization to prompt |

**Next steps:**
1. Add explicit instruction to judge prompt: "Do not favor longer answers. Score based on accuracy and relevance only."
2. For length bias > 60%: add length normalization — truncate both answers to same max length before judging.
3. Track kappa over time — if kappa drops after prompt changes, revert.
