# Lab 24 — Full Evaluation & Guardrail System

## Overview

Hệ thống evaluation và guardrail production-ready cho RAG pipeline về tài chính/thuế tiếng Việt (từ Lab 18). Bao gồm RAGAS automated evaluation với 4 metrics, LLM-as-Judge với bias mitigation, input guardrails (PII redaction + topic validation), output guardrail (Llama Guard 3 via Groq), và async full-stack integration với latency benchmark.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

Tạo `.env` với các API keys:

```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

## Chạy từng Phase

```bash
# Phase A
python phase-a/generate_testset.py      # sinh testset_v1.csv
python phase-a/run_ragas.py             # sinh ragas_results.csv + ragas_summary.json

# Phase B
python phase-b/judge.py                 # sinh pairwise_results.csv + absolute_scores.csv
# → mở to_label.csv, label thủ công 10 cặp → save phase-b/human_labels.csv
python phase-b/kappa_analysis.py        # tính Cohen's kappa

# Phase C
python phase-c/input_guard.py           # test PII + topic + adversarial
python phase-c/output_guard.py          # test Llama Guard
python phase-c/full_pipeline.py         # full stack benchmark

# CI/CD gate
python scripts/run_eval.py --threshold faithfulness=0.70
```

## Results Summary

### Phase A (RAGAS)

- Test set: 50 questions (50% simple, 25% reasoning, 25% multi-context)
- Faithfulness: *(fill)* | AR: *(fill)* | CP: *(fill)* | CR: *(fill)*
- Total eval cost: $*(fill)*
- Identified 3 failure clusters (see phase-a/failure_analysis.md)

### Phase B (LLM-Judge)

- Cohen's kappa vs human: *(fill)* — *(interpretation)*
- Position bias mitigated via swap-and-average (2 runs per pair)
- Length bias: *(fill)* (B wins when longer)

### Phase C (Guardrails)

- PII detection rate: *(fill)*% (10/10 EN, VN inputs)
- Topic validator: *(fill)*% accuracy (20 inputs)
- Adversarial defense: *(fill)*% (x/20)
- Llama Guard latency P95: *(fill)*ms

### Phase D (Blueprint)

See [phase-d/blueprint.md](phase-d/blueprint.md) — SLOs, architecture diagram, alert playbook, cost analysis.

## Lessons Learned

*(Fill sau khi chạy xong — 2-3 đoạn về những gì học được)*

## Demo Video

*(Fill link YouTube hoặc path file)*
