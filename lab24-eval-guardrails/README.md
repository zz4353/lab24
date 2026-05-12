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

- Test set: 51 questions (mixed simple/reasoning/multi-context)
- Faithfulness: 0.5358 | AR: 0.4087 | CP: 0.6895 | CR: 0.5350
- Total eval cost: ~$0.50 (gpt-4o-mini, 204 metric evaluations)
- Identified failure clusters: low faithfulness (naive context[0] answer), poor answer relevancy (no LLM generation), see phase-a/failure_analysis.md

### Phase B (LLM-Judge)

- Cohen's kappa vs human: -0.167 — WORSE than chance (judge has strong domain/position bias)
- Position bias mitigated via swap-and-average (2 runs per pair)
- Mean absolute score (GPT-4o-mini answers): 3.54/5.0

### Phase C (Guardrails)

- PII detection rate: 70% (7/10)
- Topic validator: 50% accuracy (10/20 — on-topic 100%, off-topic 0%)
- Adversarial defense: 0% (rule-based approach insufficient)
- Output guard (OpenAI Moderation): detection 80%, FP 0%, P95 977ms
- Full pipeline P95: L1=742ms, L2=7239ms, L3=792ms

### Phase D (Blueprint)

See [phase-d/blueprint.md](phase-d/blueprint.md) — SLOs, architecture diagram, alert playbook, cost analysis.

## Lessons Learned

*(Fill sau khi chạy xong — 2-3 đoạn về những gì học được)*

## Demo Video

[video.mp4](../video.mp4)
