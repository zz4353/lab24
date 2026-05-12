"""
Task A.2 — Run RAGAS 4 Metrics
Chạy RAG pipeline trên testset_v1.csv, evaluate với 4 RAGAS metrics.

Prerequisites:
    - Qdrant running on localhost:6333
    - Lab18 documents indexed (chạy Lab18/main.py trước)
    - testset_v1.csv đã được generate (chạy generate_testset.py trước)

Output: phase-a/ragas_results.csv, phase-a/ragas_summary.json
"""

import os
import sys
import json
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import pandas as pd
from openai import OpenAI
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from datasets import Dataset

from rag_adapter import run_query_llm


TESTSET_PATH = os.path.join(os.path.dirname(__file__), 'testset_v1.csv')
RESULTS_PATH = os.path.join(os.path.dirname(__file__), 'ragas_results.csv')
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), 'ragas_summary.json')


def main():
    print("=== Task A.2: RAGAS Evaluation ===")

    if not os.path.exists(TESTSET_PATH):
        print(f"ERROR: {TESTSET_PATH} not found. Run generate_testset.py first.")
        sys.exit(1)

    testset = pd.read_csv(TESTSET_PATH)
    print(f"Loaded {len(testset)} questions from testset_v1.csv")

    CACHE_PATH = os.path.join(os.path.dirname(__file__), 'rag_answers_cache.csv')

    if os.path.exists(CACHE_PATH):
        print(f"  Loading cached RAG answers from {CACHE_PATH}")
        cache_df = pd.read_csv(CACHE_PATH)
        results_data = []
        for _, r in cache_df.iterrows():
            ctx = r['retrieved_contexts']
            if isinstance(ctx, str):
                import ast
                try:
                    ctx = ast.literal_eval(ctx)
                except Exception:
                    ctx = [ctx]
            results_data.append({**r.to_dict(), 'retrieved_contexts': ctx})
    else:
        results_data = []
        for i, row in testset.iterrows():
            print(f"  [{i+1}/{len(testset)}] {str(row.get('question') or row.get('user_input', ''))[:60]}...")
            question = row.get('question') or row.get('user_input', '')
            ground_truth = row.get('ground_truth') or row.get('reference', '')
            answer, contexts = run_query_llm(question)
            results_data.append({
                'user_input': question,
                'response': answer,
                'retrieved_contexts': str(contexts),
                'reference': ground_truth,
            })
        pd.DataFrame(results_data).to_csv(CACHE_PATH, index=False)
        print(f"  Saved RAG answers cache to {CACHE_PATH}")

    print("\nRunning RAGAS evaluation...")
    dataset = Dataset.from_list(results_data)
    llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
    scores = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm,
    )

    scores_df = scores.to_pandas()
    scores_df.to_csv(RESULTS_PATH, index=False)
    print(f"Saved per-question results to {RESULTS_PATH}")

    scores_df = pd.read_csv(RESULTS_PATH)
    summary = {m: float(scores_df[m].mean()) if m in scores_df.columns else 0.0
               for m in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']}
    with open(SUMMARY_PATH, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary to {SUMMARY_PATH}")

    print("\n--- RAGAS Scores ---")
    targets = {'faithfulness': 0.85, 'answer_relevancy': 0.80, 'context_precision': 0.70, 'context_recall': 0.75}
    for metric, score in summary.items():
        target = targets[metric]
        status = "✓" if score >= target else "✗"
        print(f"  {status} {metric}: {score:.4f} (target: {target})")

    print("\nNext: run failure analysis → see generate_failure_analysis.py or fill failure_analysis.md manually")


if __name__ == "__main__":
    main()
