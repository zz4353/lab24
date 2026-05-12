"""
Task B.1 + B.2 — LLM-as-Judge Pipeline
- B.1: Pairwise judge với swap-and-average (position bias mitigation)
- B.2: Absolute scoring với 4-point rubric

Version A: Lab18 naive answer (context[0])
Version B: GPT-4o-mini generated answer

Output: phase-b/pairwise_results.csv, phase-b/absolute_scores.csv
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from rag_adapter import run_query, run_query_llm


JUDGE_PROMPT = PromptTemplate.from_template("""
You are an impartial evaluator. Compare two answers to the same question.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Rate based on:
- Factual accuracy
- Relevance to question
- Conciseness

Output JSON only:
{{"winner": "A" or "B" or "tie", "reason": "..."}}
""")

ABSOLUTE_PROMPT = PromptTemplate.from_template("""
Score the answer on 4 dimensions, each 1-5 scale:

1. Factual accuracy (1=many errors, 5=fully accurate)
2. Relevance (1=off-topic, 5=directly answers)
3. Conciseness (1=verbose, 5=appropriately brief)
4. Helpfulness (1=unclear, 5=actionable)

Question: {question}
Answer: {answer}

Output JSON only:
{{"accuracy": int, "relevance": int, "conciseness": int, "helpfulness": int, "overall": float}}
""")

PAIRWISE_PATH = os.path.join(os.path.dirname(__file__), 'pairwise_results.csv')
ABSOLUTE_PATH = os.path.join(os.path.dirname(__file__), 'absolute_scores.csv')
LABEL_PATH = os.path.join(os.path.dirname(__file__), 'to_label.csv')
TESTSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'phase-a', 'testset_v1.csv')


def parse_judge_output(text: str) -> dict:
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {"winner": "tie", "reason": "Parse error"}


def pairwise_judge_with_swap(question: str, ans1: str, ans2: str, judge_llm) -> tuple[str, str, str]:
    """Swap-and-average for position bias mitigation. Returns (final, run1, run2)."""
    # Run 1: ans1=A, ans2=B
    prompt = JUDGE_PROMPT.format(question=question, answer_a=ans1, answer_b=ans2)
    out = judge_llm.invoke(prompt)
    r1 = parse_judge_output(out.content)

    # Run 2: swap order
    prompt = JUDGE_PROMPT.format(question=question, answer_a=ans2, answer_b=ans1)
    out = judge_llm.invoke(prompt)
    r2 = parse_judge_output(out.content)
    # Flip winner because order was swapped
    if r2['winner'] == 'A':
        r2['winner'] = 'B'
    elif r2['winner'] == 'B':
        r2['winner'] = 'A'

    run1_winner = r1.get('winner', 'tie')
    run2_winner = r2.get('winner', 'tie')

    # Aggregate: both agree → that; disagree → tie
    if run1_winner == run2_winner:
        final = run1_winner
    else:
        final = 'tie'

    return final, run1_winner, run2_winner


def absolute_score(question: str, answer: str, judge_llm) -> dict:
    prompt = ABSOLUTE_PROMPT.format(question=question, answer=answer)
    out = judge_llm.invoke(prompt)
    parsed = parse_judge_output(out.content)
    if 'overall' not in parsed:
        dims = ['accuracy', 'relevance', 'conciseness', 'helpfulness']
        parsed['overall'] = sum(parsed.get(d, 3) for d in dims) / 4
    return parsed


def run_pairwise(questions: list[str], judge_llm) -> list[dict]:
    results = []
    for i, q in enumerate(questions):
        print(f"  Pairwise [{i+1}/{len(questions)}]: {q[:55]}...")
        ans_a, _ = run_query(q)
        ans_b, _ = run_query_llm(q)
        final, r1, r2 = pairwise_judge_with_swap(q, ans_a, ans_b, judge_llm)
        results.append({
            'question': q,
            'answer_a': ans_a,
            'answer_b': ans_b,
            'run1_winner': r1,
            'run2_winner': r2,
            'winner_after_swap': final,
        })
    return results


def run_absolute(questions: list[str], judge_llm) -> list[dict]:
    results = []
    for i, q in enumerate(questions):
        print(f"  Absolute [{i+1}/{len(questions)}]: {q[:55]}...")
        ans_b, _ = run_query_llm(q)
        scores = absolute_score(q, ans_b, judge_llm)
        results.append({'question': q, 'answer': ans_b, **scores})
    return results


def main():
    print("=== Task B.1 + B.2: LLM-as-Judge ===")

    if not os.path.exists(TESTSET_PATH):
        print(f"ERROR: testset_v1.csv not found. Run phase-a/generate_testset.py first.")
        sys.exit(1)

    testset = pd.read_csv(TESTSET_PATH)
    questions = testset['question'].dropna().tolist()[:30]
    print(f"Using first 30 questions from testset ({len(questions)} loaded)")

    judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # B.1 — Pairwise
    print("\n[B.1] Pairwise judge with swap-and-average...")
    pairwise_rows = run_pairwise(questions, judge_llm)
    pairwise_df = pd.DataFrame(pairwise_rows)
    pairwise_df.to_csv(PAIRWISE_PATH, index=False)
    print(f"Saved {len(pairwise_df)} rows to {PAIRWISE_PATH}")

    winners = pairwise_df['winner_after_swap'].value_counts()
    print(f"Winners: {winners.to_dict()}")

    # Save 10 rows for human labeling
    to_label = pairwise_df[['question', 'answer_a', 'answer_b']].sample(10, random_state=42)
    to_label.to_csv(LABEL_PATH, index=False)
    print(f"Saved 10 questions to label → {LABEL_PATH}")
    print("→ Open to_label.csv, judge each pair manually, save as human_labels.csv")

    # B.2 — Absolute
    print("\n[B.2] Absolute scoring...")
    absolute_rows = run_absolute(questions, judge_llm)
    absolute_df = pd.DataFrame(absolute_rows)
    absolute_df.to_csv(ABSOLUTE_PATH, index=False)
    print(f"Saved {len(absolute_df)} rows to {ABSOLUTE_PATH}")

    print(f"\nMean overall score: {absolute_df['overall'].mean():.2f}")


if __name__ == "__main__":
    main()
