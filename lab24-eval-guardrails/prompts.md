# Prompts Log — Lab 24

Theo yêu cầu academic integrity, mọi AI prompts sử dụng trong lab được ghi lại ở đây.

---

## Phase A

**A.1 — generate_testset.py**
> "Viết script Python dùng RAGAS TestsetGenerator để tạo 50 câu hỏi từ PDF documents, phân phối 50% simple / 25% reasoning / 25% multi_context. Lưu ra testset_v1.csv."

**A.2 — run_ragas.py**
> "Viết script chạy RAGAS 4 metrics (faithfulness, answer_relevancy, context_precision, context_recall) trên testset, tích hợp với RAG pipeline từ Lab18. Lưu ragas_results.csv và ragas_summary.json."

**A.3 — failure_analysis.md**
> "Viết template failure_analysis.md với bottom 10 questions và phân tích failure clusters."

**A.4 — eval-gate.yml**
> "Viết GitHub Actions workflow chạy RAGAS evaluation với threshold gate, upload artifact."

---

## Phase B

**B.1 + B.2 — judge.py**
> "Implement pairwise_judge_with_swap() với position bias mitigation (chạy 2 lần, đổi order), và absolute_score() với 4-point rubric. Lưu pairwise_results.csv và absolute_scores.csv."

**B.3 — kappa_analysis.py**
> "Compute Cohen's kappa giữa human labels và judge labels, in interpretation theo bảng scale."

**B.4 — judge_bias_report.md**
> "Phân tích position bias và length bias từ pairwise_results.csv với charts."

---

## Phase C

**C.1 + C.2 — input_guard.py**
> "Implement InputGuard (Presidio + VN regex) và TopicGuard (embedding similarity). Test với 10 PII inputs và 20 topic inputs."

**C.3 — adversarial testing**
> "Build test set 20 adversarial inputs (DAN, roleplay, payload split, encoding, injection). Measure detection rate."

**C.4 — output_guard.py**
> "Implement OutputGuardAPI dùng Groq API với llama-guard-3-8b. Test với 10 unsafe + 10 safe outputs."

**C.5 — full_pipeline.py**
> "Integrate full guardrail stack async (L1 parallel, L2 RAG, L3 parallel, L4 audit). Benchmark 100 requests, report P50/P95/P99."

---

## Phase D

**blueprint.md**
> "Viết blueprint document với SLO table, Mermaid architecture diagram, alert playbook 3 incidents, cost analysis."
