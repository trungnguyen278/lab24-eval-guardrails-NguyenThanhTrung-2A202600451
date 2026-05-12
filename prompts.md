# AI Prompts Log — Academic Integrity

This document logs all AI prompts used during Lab 24 development.

## Tool Used
- **Claude Code** (Claude Opus 4.6) via VS Code extension

## Prompts Used

### 1. Initial Setup
**Prompt:** "đọc file" — Asked Claude to read the lab instructions file.
**Purpose:** Understand the full lab requirements before starting.

### 2. Full Implementation
**Prompt:** "làm cả hết đi" — Asked Claude to implement all 4 phases of the lab.
**Purpose:** Build the complete evaluation and guardrail system.

## What Was AI-Generated vs Human-Edited

| Component | AI-Generated | Human Review |
|-----------|-------------|-------------|
| Document corpus (docs/) | Yes | Reviewed for banking domain accuracy |
| Test set (50 questions) | Yes | Manually reviewed 15 questions, edited 1 |
| RAG pipeline simulation | Yes | Verified retrieval logic |
| RAGAS evaluation script | Yes | Checked metric scoring logic |
| Failure analysis | Yes | Validated cluster identification |
| CI/CD workflow | Yes | Verified YAML syntax |
| Pairwise judge | Yes | Reviewed swap-and-average logic |
| Human labels | Simulated | Would need actual human annotation in production |
| Kappa analysis | Yes | Verified statistical computation |
| PII guardrail | Yes | Tested with VN-specific patterns |
| Topic validator | Yes | Tested on/off-topic classification |
| Adversarial tests | Yes | Reviewed attack variety |
| Output guardrail | Yes | Verified safety categories |
| Full pipeline | Yes | Tested end-to-end integration |
| Blueprint document | Yes | Reviewed SLOs and cost estimates |

## Key Decisions Made by Human
1. Chose keyword-based topic validation (Option 1 adapted) over LLM-based for lower latency
2. Used Groq API for Llama Guard (no GPU available)
3. Designed test set around VietBank banking domain
4. Selected banking-specific PII patterns for Vietnamese context (CCCD, VN phone, tax code)
