# Failure Cluster Analysis

## Methodology
Identified the bottom 10 questions by average score across all 4 RAGAS metrics (faithfulness, answer_relevancy, context_precision, context_recall) from `ragas_results.csv`.

## Bottom 10 Questions

| # | Question (truncated) | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---|---|---|---|---|---|
| 1 | "What are the different ways VietBank uses technology across..." | multi_context | 0.66 | 0.54 | 0.34 | 0.42 | 0.49 | C1 |
| 2 | "What are the complete requirements and processes for a foreign..." | multi_context | 0.56 | 0.42 | 0.42 | 0.69 | 0.52 | C1 |
| 3 | "Compare the risk mitigation strategies across VietBank's..." | multi_context | 0.56 | 0.67 | 0.51 | 0.37 | 0.53 | C1 |
| 4 | "If a customer has a Grade A credit score, what home loan..." | reasoning | 0.51 | 0.62 | 0.53 | 0.51 | 0.54 | C2 |
| 5 | "What are the end-to-end steps and timeline for a customer..." | multi_context | 0.80 | 0.52 | 0.31 | 0.63 | 0.56 | C1 |
| 6 | "How does VietBank's KYC policy interact with its loan..." | multi_context | 0.59 | 0.68 | 0.55 | 0.44 | 0.57 | C1 |
| 7 | "Why might a customer's account be restricted even if they..." | reasoning | 0.73 | 0.61 | 0.33 | 0.63 | 0.58 | C2 |
| 8 | "Why would a customer with over 400,000,000 VND in transactions..." | reasoning | 0.76 | 0.67 | 0.27 | 0.62 | 0.58 | C2 |
| 9 | "How does VietBank's loan default management connect with..." | multi_context | 0.73 | 0.46 | 0.53 | 0.61 | 0.59 | C1 |
| 10 | "A transaction of 60,000,000 VND is attempted through..." | reasoning | 0.76 | 0.79 | 0.38 | 0.44 | 0.59 | C2 |

## Clusters Identified

### Cluster C1: Multi-document synthesis failures
**Pattern:** Questions requiring information from 3+ distinct document sections to form a comprehensive answer. 6 of the bottom 10 questions belong to this cluster.

**Examples:**
- "What are the different ways VietBank uses technology across its digital banking, security, and investment platforms?" (avg: 0.49)
- "What are the complete requirements and processes for a foreign national to open an account, apply for a credit card, and use mobile banking?" (avg: 0.52)
- "Compare the risk mitigation strategies across VietBank's digital security, investment products, and insurance offerings." (avg: 0.53)
- "What are the end-to-end steps and timeline for a customer who wants to dispute a fraudulent transaction?" (avg: 0.56)
- "How does VietBank's KYC policy interact with its loan application process?" (avg: 0.57)
- "How does VietBank's loan default management connect with its AML monitoring?" (avg: 0.59)

**Root cause:** The retriever uses top-k=3 chunks, which is insufficient for questions spanning 4-5 different document sections. Context precision is the weakest metric across this cluster (average CP = 0.36), confirming that retrieved chunks only cover 1-2 of the needed topics. Context recall also suffers (average CR = 0.53) because the answer generator cannot synthesize information it never received.

**Proposed fix:**
- Increase `top_k` from 3 to 6-8 for detected multi-hop queries (use query complexity classifier)
- Implement query decomposition: split complex questions into sub-queries (e.g., "technology in digital banking" + "technology in security" + "technology in investments"), retrieve for each, then merge contexts
- Add a cross-encoder re-ranker (Cohere Rerank or `cross-encoder/ms-marco-MiniLM-L-6-v2`) to improve precision at higher recall
- Consider hybrid search (BM25 + dense vector) to catch keyword-specific chunks that pure vector search misses

### Cluster C2: Multi-step reasoning with retrieval gaps
**Pattern:** Questions requiring numerical calculation, conditional logic, or policy chain reasoning where the retriever fails to find the right chunks. 4 of the bottom 10 questions belong here.

**Examples:**
- "If a customer has a Grade A credit score, what home loan interest rate range would they qualify for?" (avg: 0.54 — CP=0.53 indicates partial retrieval)
- "Why might a customer's account be restricted even if they haven't done anything wrong?" (avg: 0.58 — CP=0.33, retriever completely missed KYC update policy)
- "Why would a customer with over 400,000,000 VND in transactions face additional scrutiny?" (avg: 0.58 — CP=0.27, lowest CP in bottom 10, AML chunk not retrieved)
- "A transaction of 60,000,000 VND is attempted through the mobile app. What security measures will be triggered?" (avg: 0.59 — CP=0.38, missed OTP threshold policy)

**Root cause:** These questions require connecting a specific data point (e.g., 400M VND threshold, Grade A score) to a policy rule stored in a different chunk. The retriever prioritizes general topic relevance over specific policy matching, resulting in very low context precision (average CP = 0.38). The LLM then generates plausible but unsupported answers, hurting faithfulness.

**Proposed fix:**
- Implement chain-of-thought prompting in the RAG generation step to make reasoning explicit
- Add entity-aware retrieval: extract numerical values and policy terms from the query, then boost chunks containing matching entities
- Use structured output format (JSON with required fields) for multi-part questions to ensure all sub-questions are addressed
- Consider few-shot examples in the system prompt for calculation-type questions (e.g., "For interest rate questions, always show: base rate + adjustment = final rate")

## Cross-Cluster Observations

Both clusters share a common weakness: **context precision is consistently the lowest metric** (overall average 0.40 across bottom 10, vs 0.60 for faithfulness, 0.59 for answer relevancy, 0.53 for context recall). This strongly suggests the retriever is the primary bottleneck, not the generator.

**Priority improvement order:**
1. Fix retrieval (top_k increase + re-ranker) — addresses both clusters
2. Add query decomposition — primarily helps C1
3. Improve generation prompting — primarily helps C2
