# Failure Cluster Analysis

## Methodology
Identified the bottom 10 questions by average score across all 4 RAGAS metrics (faithfulness, answer_relevancy, context_precision, context_recall).

## Bottom 10 Questions

| # | Question (truncated) | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---|---|---|---|---|---|
| 1 | "Compare all the insurance and protection features..." | multi_context | 0.42 | 0.45 | 0.28 | 0.35 | 0.38 | C1 |
| 2 | "What are the end-to-end steps and timeline for..." | multi_context | 0.48 | 0.40 | 0.32 | 0.38 | 0.40 | C1 |
| 3 | "How does VietBank's complaint resolution connect..." | multi_context | 0.50 | 0.52 | 0.30 | 0.42 | 0.44 | C1 |
| 4 | "If a loan becomes 100 days overdue, what classification..." | reasoning | 0.55 | 0.48 | 0.38 | 0.45 | 0.47 | C2 |
| 5 | "A customer makes 10M VND purchase, only pays minimum..." | reasoning | 0.52 | 0.55 | 0.40 | 0.42 | 0.47 | C2 |
| 6 | "How does VietBank's loan default management connect..." | multi_context | 0.58 | 0.50 | 0.35 | 0.48 | 0.48 | C1 |
| 7 | "What happens to a suspicious transaction report if..." | reasoning | 0.60 | 0.45 | 0.42 | 0.50 | 0.49 | C2 |
| 8 | "Compare the risk mitigation strategies across..." | multi_context | 0.55 | 0.58 | 0.38 | 0.48 | 0.50 | C1 |
| 9 | "A transaction of 60,000,000 VND is attempted..." | reasoning | 0.62 | 0.55 | 0.40 | 0.48 | 0.51 | C2 |
| 10 | "Why would a customer with over 400M VND face..." | reasoning | 0.58 | 0.60 | 0.45 | 0.45 | 0.52 | C2 |

## Clusters Identified

### Cluster C1: Multi-document synthesis failures
**Pattern:** Questions requiring information from 3+ distinct document sections to form a comprehensive answer.

**Examples:**
- "Compare all the insurance and protection features available across VietBank's credit cards, bancassurance products, and investment products."
- "What are the end-to-end steps and timeline for a customer who wants to dispute a fraudulent transaction, considering the complaint resolution, security incident, and AML processes?"
- "How does VietBank's complaint resolution process connect with its data privacy rights and the incident response procedure?"
- "How does VietBank's loan default management connect with its AML monitoring and customer data retention policies?"
- "Compare the risk mitigation strategies across VietBank's digital security, investment products, and insurance offerings."

**Root cause:** The retriever uses top-k=3 chunks, which is insufficient for questions spanning 4-5 different document sections. Context precision drops to 0.28-0.38 because retrieved chunks only cover 1-2 of the needed topics, leaving gaps in the answer.

**Proposed fix:**
- Increase `top_k` from 3 to 6-8 for detected multi-hop queries
- Implement query decomposition: split complex questions into sub-queries, retrieve for each, then merge contexts
- Add a re-ranker (Cohere Rerank or cross-encoder) to improve precision at higher recall
- Consider hybrid search (BM25 + dense vector) to catch keyword-specific chunks that vector search misses

### Cluster C2: Multi-step reasoning failures
**Pattern:** Questions requiring numerical calculation, conditional logic, or policy chain reasoning.

**Examples:**
- "If a loan becomes 100 days overdue, what classification would it receive and what is the bank's provision rate and collection action?"
- "A customer makes a credit card purchase of 10,000,000 VND and only pays the minimum. What is the minimum payment amount and what interest would accrue?"
- "What happens to a suspicious transaction report if a bank staff member informs the customer about it?"
- "A transaction of 60,000,000 VND is attempted through the mobile app. What security measures will be triggered?"
- "Why would a customer with over 400,000,000 VND in transactions face additional scrutiny?"

**Root cause:** The LLM generates partial answers that address the first part of the question but miss secondary implications. Faithfulness suffers because the model sometimes adds plausible but unsupported details when it lacks sufficient context for the full reasoning chain.

**Proposed fix:**
- Implement chain-of-thought prompting in the RAG generation step
- Add a "reasoning verification" post-processing step that checks if all parts of a multi-part question are addressed
- Use structured output format (JSON with required fields) for multi-part questions
- Consider few-shot examples in the system prompt for calculation-type questions

### Cluster C3: Terminology mismatch (minor)
**Pattern:** Some questions use alternate phrasings not matching document keywords, causing retrieval misses.

**Examples:**
- Using "fraud dispute" instead of "complaint resolution"
- Using "risk management" instead of specific product names

**Root cause:** Pure keyword overlap scoring misses semantic similarity.

**Proposed fix:**
- Switch from keyword-based to embedding-based retrieval (already planned)
- Add synonym expansion in the query preprocessing step
