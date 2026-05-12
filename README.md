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
- **Failure clusters:** 2 primary clusters identified — multi-document synthesis failures (C1, 6 questions) and multi-step reasoning with retrieval gaps (C2, 4 questions)
- Observation: Context Precision (0.65) is the weakest metric overall, dropping to 0.34 average for bottom-10 questions — retriever is the primary bottleneck

### Phase B — LLM-as-Judge (25 pts)
- **Cohen's kappa vs human:** 0.531 (moderate agreement — usable for monitoring)
- **Root cause for disagreements:** 3 out of 10 pairs differ — judge defaults to decisive winners while human annotators call "tie" when both answers are poor; conversely, human prefers concise direct answers (A) for simple questions while judge rates them "tie"
- **Position bias:** A wins as first position 26.7% (mitigated by swap-and-average)
- **Length bias:** B wins 11.5% when longer (Answer B averages 374 chars vs A's 273 chars)

### Phase C — Guardrails (35 pts)
- **PII detection rate:** 100% (7/7 inputs with PII detected), P95 latency 1.05ms
- **Topic validator accuracy:** 100% (20/20), refuse rate 50% (10 off-topic correctly refused)
- **Adversarial defense:** 100% (20/20 attacks blocked, 0% false positives on 10 legitimate queries)
- **Output guard (Llama Guard keyword fallback):** 100% unsafe detection, 0% false positives
- **Full pipeline latency:** L1 P95=0.1ms, L2 P95=0.2ms, L3 P95=0.0ms, Total P95=0.4ms
- **Guardrail overhead:** +0.1ms P50, +0.2ms P95 — well within all targets

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

Building an end-to-end evaluation and guardrail system revealed that measuring RAG quality is only the beginning — the real challenge is maintaining quality in production. RAGAS metrics showed that multi-context questions are the weakest point in our pipeline (context precision drops to 0.34 for the bottom 10), pointing to a need for better retrieval strategies like query decomposition, increased top_k, and cross-encoder re-ranking.

The LLM-as-Judge experiments demonstrated how subtle biases (position, length) can compromise evaluation reliability. The swap-and-average technique effectively neutralizes position bias (A wins only 26.7% as first position, well below the 50% bias threshold). Human calibration achieved a Cohen's kappa of 0.531 (moderate agreement), with disagreements concentrated on edge cases where both answers were poor — the judge defaults to a winner while humans call ties. For production use, a larger calibration set (50+ samples) and explicit conciseness criteria would improve reliability.

On the guardrails side, the multi-layered defense approach (injection detection + content safety + PII redaction + topic validation) achieved 100% adversarial detection with 0% false positives. The keyword-based output guard provides excellent latency (<1ms) but should be supplemented with Llama Guard 3 via Groq API for production to handle novel unsafe patterns. The full pipeline adds only 0.2ms P95 overhead — negligible compared to the LLM generation step.

## Demo Video
[To be recorded — will include: RAGAS live run, LLM-Judge comparison, adversarial attack demo, and latency benchmark output]
