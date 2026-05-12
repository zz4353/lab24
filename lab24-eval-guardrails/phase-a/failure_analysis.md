# Failure Cluster Analysis — Task A.3

Phân tích bottom 10 questions có điểm thấp nhất (average across 4 RAGAS metrics).

---

## Bottom 10 Questions

| # | Question (truncated) | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---|---|---|---|---|---|
| 1 | What measures are required for the processing of sensit... | reasoning | 0.0 | 0.0 | 0.0 | 0.0 | 0.00 | C1 |
| 2 | What are the responsibilities of data controllers in en... | reasoning | 0.0 | 0.0 | 0.0 | 0.0 | 0.00 | C1 |
| 3 | What are the requirements for obtaining consent from th... | reasoning | 0.0 | 0.0 | 0.0 | 0.0 | 0.00 | C1 |
| 4 | What measures are in place to ensure the protection of... | multi_context | 0.0 | 0.0 | 0.0 | 0.25 | 0.06 | C2 |
| 5 | What are the necessary steps for ensuring compliance wh... | multi_context | 0.0 | 0.0 | 0.0 | 0.33 | 0.08 | C2 |
| 6 | How does the responsibility for protecting personal dat... | reasoning | 0.0 | 0.0 | 0.0 | 0.50 | 0.12 | C1 |
| 7 | What is the significance of the Bộ luật Dân sự in relat... | simple | 0.0 | 0.0 | 0.58 | 0.0 | 0.15 | C3 |
| 8 | What commitments do organizations have regarding the pr... | multi_context | 0.0 | 0.0 | 0.0 | 0.67 | 0.17 | C2 |
| 9 | What responsibilities does the data controller have reg... | reasoning | 0.0 | 0.0 | 0.0 | 0.67 | 0.17 | C1 |
| 10 | Mục đích xử lý dữ liệu cá nhân là gì? | simple | 0.0 | 0.0 | 1.0 | 0.0 | 0.25 | C3 |

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
