# Lab 24 — Kế hoạch & Checklist

## Cấu trúc repo cần tạo

```
lab24-eval-guardrails/
├── README.md
├── requirements.txt
├── prompts.md
├── phase-a/
│   ├── generate_testset.py
│   ├── testset_v1.csv          (output)
│   ├── testset_review_notes.md
│   ├── run_ragas.py
│   ├── ragas_results.csv       (output)
│   ├── ragas_summary.json      (output)
│   └── failure_analysis.md
├── phase-b/
│   ├── judge.py
│   ├── pairwise_results.csv    (output)
│   ├── absolute_scores.csv     (output)
│   ├── human_labels.csv        (manual)
│   ├── kappa_analysis.py
│   └── judge_bias_report.md
├── phase-c/
│   ├── input_guard.py
│   ├── output_guard.py
│   ├── full_pipeline.py
│   ├── pii_test_results.csv    (output)
│   ├── adversarial_test_results.csv (output)
│   └── latency_benchmark.csv   (output)
├── phase-d/
│   └── blueprint.md
├── scripts/
│   └── run_eval.py
└── .github/workflows/
    └── eval-gate.yml
```

---

## Phase A — RAGAS Evaluation (30đ)

### A.1 — Synthetic Test Set Generation (8đ)
- [x] `phase-a/generate_testset.py` — dùng `TestsetGenerator`, 50 questions, phân phối 50/25/25
- [x] Output `testset_v1.csv` có ≥ 50 rows, 4 cột: `question, ground_truth, contexts, evolution_type`
- [x] `testset_review_notes.md` — manual review ≥ 10 questions, ≥ 1 câu được chỉnh sửa

### A.2 — Run RAGAS 4 Metrics (10đ)
- [x] `phase-a/run_ragas.py` — chạy 4 metrics: faithfulness, answer_relevancy, context_precision, context_recall
- [x] Output `ragas_results.csv` — 4 metric columns, 50 rows
- [x] Output `ragas_summary.json` — 4 aggregate scores
- [ ] Ghi total cost vào README *(điền sau khi chạy)*

### A.3 — Failure Cluster Analysis (8đ)
- [x] `phase-a/failure_analysis.md` — bảng bottom 10 questions + template
- [x] ≥ 2 clusters identified, mỗi cluster ≥ 2 examples, proposed fix kỹ thuật cụ thể
- [ ] Điền số liệu thực vào bảng sau khi chạy `run_ragas.py`

### A.4 — CI/CD Integration Plan (4đ)
- [x] `.github/workflows/eval-gate.yml` — valid YAML, threshold gate, artifact upload
- [x] `scripts/run_eval.py` — exit code 1 nếu metric < threshold

---

## Phase B — LLM-as-Judge & Calibration (25đ)

### B.1 — Pairwise Judge Pipeline (10đ)
- [x] `phase-b/judge.py` — `pairwise_judge_with_swap()` chạy 2 lần với order đổi
- [x] Chạy ≥ 30 questions
- [x] Output `pairwise_results.csv` — columns: `question, run1_winner, run2_winner, winner_after_swap`

### B.2 — Absolute Scoring (5đ)
- [x] `absolute_score()` trong `judge.py` — 4 dimensions (accuracy, relevance, conciseness, helpfulness), overall = average
- [x] Output `absolute_scores.csv` — 30 questions

### B.3 — Human Calibration (8đ)
- [x] `human_labels.csv` — 10 labels thủ công với cột `confidence` và `notes`
- [x] `phase-b/kappa_analysis.py` — compute Cohen's kappa, in interpretation
- [x] Root cause analysis nếu kappa < 0.6
- [ ] Cập nhật `human_labels.csv` với labels thực sau khi chạy `judge.py`

### B.4 — Bias Observations Report (2đ)
- [x] `judge_bias_report.md` — ≥ 2 biases quantified với số, ≥ 1 chart/table, mitigation strategy
- [ ] Điền số liệu thực vào bảng sau khi chạy `judge.py`

---

## Phase C — Guardrails Stack (35đ)

### C.1 — Input Guardrail: PII Redaction (8đ)
- [x] `phase-c/input_guard.py` — `InputGuard` class: VN regex + Presidio NER
- [x] Test 10 inputs (mix EN + VN), detection ≥ 80%, latency P95 < 50ms
- [x] Output `pii_test_results.csv` — columns: `input, output, pii_found, latency_ms`

### C.2 — Topic Scope Validator (6đ)
- [x] `TopicGuard` trong `input_guard.py` — dùng Option 1 (embedding similarity)
- [x] Test 20 inputs (10 on-topic, 10 off-topic), accuracy ≥ 75%
- [x] Graceful fallback message khi off-topic

### C.3 — Adversarial Testing (6đ)
- [x] 20 adversarial inputs (DAN x5, roleplay x5, split x3, encoding x3, injection x4)
- [x] Detection rate ≥ 70%, false positive ≤ 10% trên 10 legit queries
- [x] Output `adversarial_test_results.csv`

### C.4 — Output Guardrail: Llama Guard 3 (8đ)
- [x] `phase-c/output_guard.py` — dùng Option B (Groq API)
- [x] Test 10 unsafe + 10 safe outputs, detection ≥ 80%, FP ≤ 20%
- [x] Latency P95 measured

### C.5 — Full Stack Integration & Latency Benchmark (7đ)
- [x] `phase-c/full_pipeline.py` — async pipeline L1 → L2 → L3 → L4
- [x] Benchmark ≥ 100 requests, report P50/P95/P99
- [x] L1 P95 < 50ms, L3 P95 < 100ms
- [x] Output `latency_benchmark.csv`

---

## Phase D — Blueprint Document (10đ)

- [x] `phase-d/blueprint.md` — ≥ 5 SLOs với alert thresholds (Section 1)
- [x] Architecture diagram Mermaid, 4 layers labeled (Section 2)
- [x] ≥ 3 incidents trong alert playbook (Section 3)
- [x] Cost breakdown với monthly projection (Section 4)

---

## Submission files

- [x] `README.md` — 200–300 từ overview + results summary
- [x] `requirements.txt` — pinned versions
- [x] `prompts.md` — log AI prompts đã dùng

---

## Lưu ý khi triển khai
- Không thêm tính năng ngoài yêu cầu
- RAG pipeline Day 18: dùng mock đơn giản nếu chưa có
- Llama Guard: dùng Groq API (Option B), không cần GPU
- Topic validator: dùng Option 1 (embedding similarity)
