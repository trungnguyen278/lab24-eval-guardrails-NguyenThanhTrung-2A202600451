# Lab 24 — Full Evaluation & Guardrail System

## Overview

This project implements a production-ready evaluation and guardrail system for a RAG (Retrieval-Augmented Generation) pipeline serving VietBank's digital banking assistant. The system covers four key areas: automated RAGAS evaluation with 4 core metrics across 50 test questions, an LLM-as-Judge pipeline with swap-and-average bias mitigation and human calibration via Cohen's kappa, a defense-in-depth guardrail stack (PII redaction, topic validation, adversarial defense, and output safety checking), and a production blueprint with SLOs, architecture diagrams, alert playbooks, and cost analysis.

**Student:** Nguyen Thanh Trung (2A202600451)
**Course:** AICB-P2T3 · VinUniversity · May 2026

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate    # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Copy .env.example to .env and fill in your API keys
cp .env.example .env
```

## Results Summary

### Phase A — RAGAS Evaluation (30 pts)
- **Test set:** 50 questions (50% simple, 24% reasoning, 26% multi-context)
- **Faithfulness:** 0.7864 | **Answer Relevancy:** 0.7603 | **Context Precision:** 0.6490 | **Context Recall:** 0.7123
- **Total eval cost:** $0.00 (simulated pipeline; estimated $1.50 with real gpt-4o-mini)
- **Failure clusters:** 2 identified — multi-document synthesis failures (C1) and multi-step reasoning failures (C2)
- Observation: Context Precision (0.65) is below target (0.70), indicating retriever returns some irrelevant chunks, especially for multi-context queries

### Phase B — LLM-as-Judge (25 pts)
- **Cohen's kappa vs human:** 0.062 (slight agreement)
- **Root cause:** Judge heavily defaults to "tie" after swap-and-average when runs disagree, while human annotators make decisive choices. The small sample size (n=10) also limits kappa reliability.
- **Position bias:** A wins as first position 26.7% (mitigated by swap-and-average)
- **Length bias:** B wins 13.3% when longer (Answer B averages 355 chars vs A's 273 chars)

### Phase C — Guardrails (35 pts)
- **PII detection rate:** 86% (6/7 inputs with PII detected)
- **Topic validator accuracy:** 100% (20/20)
- **Adversarial defense:** 80% (16/20 attacks blocked, 0% false positives)
- **Output guard (Llama Guard keyword fallback):** 100% unsafe detection, 0% false positives
- **Latency:** L1 P95 < 1ms, L3 P95 < 1ms — well within targets

### Phase D — Blueprint
See [phase-d/blueprint.md](phase-d/blueprint.md) — includes 7 SLOs, architecture diagram, 3 incident playbooks, and cost analysis ($241/mo for 100K queries).

## Project Structure

```
├── README.md
├── requirements.txt
├── prompts.md                    # AI prompts log
├── .env.example
├── docs/                         # Document corpus (banking FAQ + policies)
├── scripts/                      # RAG pipeline + CI eval script
├── phase-a/                      # RAGAS evaluation outputs
├── phase-b/                      # LLM-as-Judge outputs
├── phase-c/                      # Guardrails implementation + tests
├── phase-d/                      # Blueprint document
└── .github/workflows/            # CI/CD eval gate
```

## Running Tests

```bash
# Phase A: Generate test set + run evaluation
python phase-a/generate_testset.py
python phase-a/run_ragas_eval.py

# Phase B: Pairwise judge + kappa analysis
python phase-b/pairwise_judge.py
python phase-b/kappa_analysis.py

# Phase C: Guardrails tests
python phase-c/input_guard.py
python phase-c/output_guard.py
python phase-c/adversarial_test.py
python phase-c/full_pipeline.py
```

## Lessons Learned

Building an end-to-end evaluation and guardrail system revealed that measuring RAG quality is only the beginning — the real challenge is maintaining quality in production. RAGAS metrics showed that multi-context questions are the weakest point in our pipeline (context precision drops to 0.50), pointing to a need for better retrieval strategies like query decomposition or hybrid search.

The LLM-as-Judge experiments demonstrated how subtle biases (position, length) can compromise evaluation reliability. The swap-and-average technique effectively neutralizes position bias but creates a high "tie" rate that reduces discriminative power. For production use, a larger calibration set (50+ samples) and multiple judge models would significantly improve reliability.

On the guardrails side, the keyword-based approach provides excellent latency (<1ms) but has gaps against encoding-based attacks (Base64, ROT13). A production system should combine keyword matching with a dedicated injection classifier (like Meta's Prompt Guard) for defense-in-depth.

## Demo Video
[To be recorded — will include: RAGAS live run, LLM-Judge comparison, adversarial attack demo, and latency benchmark output]
