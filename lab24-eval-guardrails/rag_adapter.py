"""
RAG Adapter — wraps Lab18 pipeline cho Lab 24.

Usage:
    from rag_adapter import run_query, run_query_llm, LAB18_DATA_DIR

    answer, contexts = run_query("Mã số thuế là gì?")
    answer_llm, contexts = run_query_llm("Mã số thuế là gì?")
"""

import os
import sys

LAB18_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lab18-C401-B1'))
LAB18_DATA_DIR = os.path.join(LAB18_PATH, 'data')

if LAB18_PATH not in sys.path:
    sys.path.insert(0, LAB18_PATH)

_search = None
_reranker = None


def get_pipeline():
    global _search, _reranker
    if _search is None:
        import src.pipeline as _pipe
        _pipe.enrich_chunks = lambda chunks, **kw: []  # skip expensive LLM enrichment
        _search, _reranker = _pipe.build_pipeline()
    return _search, _reranker


def run_query(question: str) -> tuple[str, list[str]]:
    """Version A: trả về context[0] làm answer (naive)."""
    search, reranker = get_pipeline()
    from src.pipeline import run_query as _run_query
    return _run_query(question, search, reranker)


def run_query_llm(question: str) -> tuple[str, list[str]]:
    """Version B: dùng GPT-4o-mini để generate answer từ contexts."""
    from openai import OpenAI
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())

    _, contexts = run_query(question)
    context_str = "\n\n".join(contexts)

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Trả lời CHỈ dựa trên context được cung cấp. Nếu không có thông tin → nói 'Không tìm thấy thông tin.'"},
            {"role": "user", "content": f"Context:\n{context_str}\n\nCâu hỏi: {question}"},
        ],
        temperature=0,
        max_tokens=300,
    )
    answer = resp.choices[0].message.content
    return answer, contexts
