"""
Task C.5 — Full Stack Integration & Latency Benchmark
Async pipeline: L1 (PII + Topic) → L2 (RAG) → L3 (Llama Guard) → L4 (Audit log)

Run:
    python phase-c/full_pipeline.py

Output: phase-c/latency_benchmark.csv
"""

import asyncio
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import numpy as np
import pandas as pd

from input_guard import InputGuard, TopicGuard
from output_guard import OutputGuardAPI
from rag_adapter import run_query_llm


BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), 'latency_benchmark.csv')
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), 'audit_log.jsonl')

REFUSE_RESPONSE = "Xin lỗi, tôi không thể trả lời câu hỏi này. Hệ thống chỉ hỗ trợ các câu hỏi về kế toán, thuế và tài chính doanh nghiệp."

# Lazy-initialized singletons
_input_guard: InputGuard = None
_topic_guard: TopicGuard = None
_output_guard: OutputGuardAPI = None


def get_guards():
    global _input_guard, _topic_guard, _output_guard
    if _input_guard is None:
        _input_guard = InputGuard()
    if _topic_guard is None:
        _topic_guard = TopicGuard()
    if _output_guard is None:
        _output_guard = OutputGuardAPI()
    return _input_guard, _topic_guard, _output_guard


async def audit_log(user_input: str, answer: str, timings: dict) -> None:
    entry = {
        "ts": time.time(),
        "input": user_input[:200],
        "answer": answer[:200],
        "timings": timings,
    }
    with open(AUDIT_LOG_PATH, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


async def guarded_pipeline(user_input: str) -> tuple[str, dict]:
    timings = {}
    input_guard, topic_guard, output_guard = get_guards()

    # L1: input guards (parallel)
    t0 = time.perf_counter()
    pii_task = asyncio.create_task(input_guard.sanitize_async(user_input))
    topic_task = asyncio.create_task(topic_guard.check_async(user_input))

    sanitized, _ = await pii_task
    topic_ok, topic_reason = await topic_task
    timings['L1'] = (time.perf_counter() - t0) * 1000

    if not topic_ok:
        asyncio.create_task(audit_log(user_input, REFUSE_RESPONSE, timings))
        return REFUSE_RESPONSE, timings

    # L2: RAG LLM
    t0 = time.perf_counter()
    answer, _ = await asyncio.to_thread(run_query_llm, sanitized)
    timings['L2'] = (time.perf_counter() - t0) * 1000

    # L3: output guard
    t0 = time.perf_counter()
    safe, _, _ = await output_guard.check_async(sanitized, answer)
    timings['L3'] = (time.perf_counter() - t0) * 1000

    if not safe:
        asyncio.create_task(audit_log(user_input, REFUSE_RESPONSE, timings))
        return REFUSE_RESPONSE, timings

    # L4: audit (fire-and-forget)
    asyncio.create_task(audit_log(user_input, answer, timings))

    return answer, timings


def load_test_queries() -> list[str]:
    from phase_c_test_queries import TEST_QUERIES
    return TEST_QUERIES


TEST_QUERIES = [
    "Mã số thuế của DHA Surfaces là gì?",
    "Thuế GTGT đầu vào kỳ này là bao nhiêu?",
    "Doanh thu bán hàng trong kỳ tính thuế Q4/2024?",
    "Chỉ tiêu 36 trong tờ khai nghĩa là gì?",
    "Nghị định 13/2023 quy định về dữ liệu nhạy cảm?",
    "Hạn nộp thuế GTGT theo quý là khi nào?",
    "Cách tính thuế phát sinh trong kỳ?",
    "DHA Surfaces có được hoàn thuế không?",
    "Điều kiện khấu trừ thuế đầu vào theo Luật thuế GTGT?",
    "Báo cáo tài chính gồm những phần nào?",
    "Tổng giá trị hàng hóa mua vào của DHA là bao nhiêu?",
    "Thuế GTGT đầu ra của DHA kỳ Q4/2024?",
    "Mức phạt chậm nộp thuế GTGT?",
    "Quy trình kiểm tra thuế GTGT của cơ quan thuế?",
    "Hóa đơn điện tử có bắt buộc không?",
    "Dữ liệu cá nhân cơ bản theo Nghị định 13 gồm gì?",
    "Ai chịu trách nhiệm bảo vệ dữ liệu trong doanh nghiệp?",
    "DHA Surfaces nộp thuế GTGT bao nhiêu kỳ này?",
    "Báo cáo lưu chuyển tiền tệ dùng phương pháp nào?",
    "Chỉ tiêu 23 trong tờ khai thuế GTGT là gì?",
    "Mã số thuế có bao nhiêu chữ số?",
    "Thuế GTGT áp dụng mức thuế suất nào?",
    "Kỳ tính thuế theo quý áp dụng cho doanh nghiệp nào?",
    "DHA Surfaces kinh doanh ngành gì?",
    "Nghị định 13 có hiệu lực từ ngày nào?",
]

# Pad to 100 by repeating
TEST_QUERIES_100 = (TEST_QUERIES * 4)[:100]


async def benchmark(n: int = 100) -> list[dict]:
    queries = TEST_QUERIES_100[:n]
    all_timings = []
    print(f"Benchmarking {n} requests...")
    for i, q in enumerate(queries):
        _, t = await guarded_pipeline(q)
        all_timings.append(t)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{n} done")
    return all_timings


def report_latencies(all_timings: list[dict]) -> None:
    print("\n--- Latency Report ---")
    for layer in ['L1', 'L2', 'L3']:
        vals = [t[layer] for t in all_timings if layer in t]
        if not vals:
            continue
        p50 = np.percentile(vals, 50)
        p95 = np.percentile(vals, 95)
        p99 = np.percentile(vals, 99)
        status_l1 = " (✓ < 50ms)" if layer == 'L1' and p95 < 50 else (" (✗ > 50ms)" if layer == 'L1' else "")
        status_l3 = " (✓ < 100ms)" if layer == 'L3' and p95 < 100 else (" (✗ > 100ms)" if layer == 'L3' else "")
        print(f"  {layer}: P50={p50:.0f}ms  P95={p95:.0f}ms  P99={p99:.0f}ms{status_l1}{status_l3}")


def save_benchmark(all_timings: list[dict]) -> None:
    rows = []
    for i, t in enumerate(all_timings):
        rows.append({'request_id': i + 1, **t})
    df = pd.DataFrame(rows)
    df.to_csv(BENCHMARK_PATH, index=False)
    print(f"\nSaved {len(df)} rows to {BENCHMARK_PATH}")


async def main_async():
    print("=== Task C.5: Full Stack Latency Benchmark ===")
    all_timings = await benchmark(n=100)
    report_latencies(all_timings)
    save_benchmark(all_timings)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
