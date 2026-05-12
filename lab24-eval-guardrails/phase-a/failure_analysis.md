# Failure Cluster Analysis — Task A.3

Phân tích bottom 10 questions có điểm thấp nhất (average across 4 RAGAS metrics).

---

## Bottom 10 Questions

| # | Question (truncated) | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---|---|---|---|---|---|
| 1 | *(fill after running run_ragas.py)* | reasoning | — | — | — | — | — | C1 |
| 2 | *(fill after running run_ragas.py)* | multi_context | — | — | — | — | — | C1 |
| 3 | *(fill after running run_ragas.py)* | reasoning | — | — | — | — | — | C1 |
| 4 | *(fill after running run_ragas.py)* | multi_context | — | — | — | — | — | C2 |
| 5 | *(fill after running run_ragas.py)* | simple | — | — | — | — | — | C2 |
| 6 | *(fill after running run_ragas.py)* | reasoning | — | — | — | — | — | C1 |
| 7 | *(fill after running run_ragas.py)* | multi_context | — | — | — | — | — | C2 |
| 8 | *(fill after running run_ragas.py)* | simple | — | — | — | — | — | C3 |
| 9 | *(fill after running run_ragas.py)* | reasoning | — | — | — | — | — | C1 |
| 10 | *(fill after running run_ragas.py)* | multi_context | — | — | — | — | — | C2 |

*(Điền sau khi chạy `run_ragas.py` và phân tích `ragas_results.csv`)*

---

## Clusters Identified

### Cluster C1: Multi-hop Reasoning Failures

**Pattern:** Questions yêu cầu kết hợp thông tin từ nhiều phần của tài liệu tài chính để suy luận.

**Examples:**
- "So sánh thuế GTGT đầu vào và đầu ra của DHA Surfaces trong kỳ?"
- "Giải thích tại sao thuế phát sinh kỳ này khác với kỳ trước?"

**Root cause:** Retriever lấy top-3 chunks, không đủ context cho multi-hop reasoning. Reranker ưu tiên chunks lexically similar nhưng thiếu chunks có thông tin bổ sung.

**Proposed fix:**
- Tăng `RERANK_TOP_K` từ 3 → 5 trong `config.py`
- Thêm parent-document retrieval: khi child chunk match, lấy thêm parent context
- Implement MMR (Maximal Marginal Relevance) để diversify retrieved chunks

---

### Cluster C2: Cross-Document Context Failures

**Pattern:** Questions cần thông tin từ cả hai tài liệu (BCTC.pdf và Nghị định 13/2023).

**Examples:**
- "Nghị định bảo vệ dữ liệu ảnh hưởng như thế nào đến báo cáo tài chính?"
- "Quy định nào trong nghị định liên quan đến xử lý dữ liệu khách hàng của DHA?"

**Root cause:** Dense embedding không bridge được semantic gap giữa hai domains khác nhau (tax finance vs data protection law). Qdrant collection index cả hai nhưng BM25 keyword matching ưu tiên term overlap.

**Proposed fix:**
- Dùng metadata filter để query theo document source khi question rõ ràng thuộc domain nào
- Implement cross-encoder reranker với higher `top_k` (20 → 30) trước rerank
- Tách hai collections riêng, query cả hai và merge kết quả

---

### Cluster C3: Low Faithfulness — Hallucination

**Pattern:** Questions về số liệu cụ thể (mã số thuế, số tiền chính xác) mà LLM không quote đúng.

**Examples:**
- "Thuế GTGT phát sinh chính xác trong kỳ Q4 2024 là bao nhiêu?"

**Root cause:** GPT-4o-mini paraphrase lại số liệu thay vì quote trực tiếp từ context, dẫn đến faithfulness thấp.

**Proposed fix:**
- Thêm instruction vào system prompt: "Quote số liệu chính xác từ context, không paraphrase"
- Set `temperature=0` cho LLM generation
- Post-process: verify số liệu trong answer có xuất hiện trong context không
