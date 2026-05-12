# Test Set Review Notes

## Review Process
Manually reviewed 15 out of 50 questions (30%) from `testset_v1.csv`.

## Reviewed Questions

### Simple Questions (8 reviewed)

| # | Question | Verdict | Notes |
|---|----------|---------|-------|
| 1 | "What is the minimum initial deposit..." | ✅ Good | Clear, single-hop, answer directly in chunk |
| 2 | "What is the annual interest rate for Standard Savings..." | ✅ Good | Factual, easy to verify |
| 3 | "How many physical branches does VietBank..." | ✏️ **Edited** | Original: "How many branches does VietBank operate nationwide?" → Rephrased to "How many physical branches does VietBank currently operate across Vietnam?" for clarity (distinguishes from ATM network) |
| 5 | "What is the session timeout duration..." | ✅ Good | Direct factual answer |
| 7 | "What is the minimum payment required..." | ✅ Good | Involves "whichever is higher" clause - tests comprehension |
| 10 | "What is the annual fee for Gold card..." | ✅ Good | Table lookup question |
| 14 | "What are VietBank branch operating hours..." | ✅ Good | Practical question users would ask |
| 17 | "How many failed login attempts..." | ✅ Good | Security-relevant, clear answer |

### Reasoning Questions (4 reviewed)

| # | Question | Verdict | Notes |
|---|----------|---------|-------|
| 26 | "If a customer has Grade A credit score..." | ✅ Good | Requires combining base rate + discount info |
| 27 | "A customer makes 10M VND purchase..." | ✅ Good | Multi-step math reasoning |
| 28 | "Why would a customer with 400M VND..." | ✅ Good | Requires connecting AML + EDD policies |
| 31 | "A customer wants to restructure 5-year loan..." | ✅ Good | Calculation + policy knowledge |

### Multi-Context Questions (3 reviewed)

| # | Question | Verdict | Notes |
|---|----------|---------|-------|
| 38 | "Compare security measures with data privacy..." | ✅ Good | Requires synthesizing 2 different chapters |
| 39 | "How does KYC interact with loan process..." | ✅ Good | Cross-referencing policies and procedures |
| 44 | "How does VietBank handle cross-border transactions..." | ✅ Good | Combines product, regulatory, and operational info |

## Edits Made
1. **Question #3** (simple): Rephrased from "How many branches does VietBank operate nationwide?" to "How many physical branches does VietBank currently operate across Vietnam?" — the original was ambiguous (could include ATMs or digital branches). Added "physical" and "currently" for precision.

2. **Ground truth #3**: Enhanced from "VietBank operates 250+ branches nationwide" to "VietBank currently operates more than 250 branches across Vietnam nationwide" — added temporal context.

## Quality Assessment
- **Overall quality**: Good. Questions are relevant to the banking domain and test different cognitive levels.
- **Simple questions**: Well-formed, each answerable from a single chunk.
- **Reasoning questions**: Require inference or calculation, not just lookup.
- **Multi-context questions**: Successfully require information from multiple document sections.
- **Potential issues**: Some reasoning questions have long ground truths that may be hard for a RAG system to fully match, which could lower context_recall scores.

## Distribution Verification
- Simple: 25/50 (50%) ✅
- Reasoning: 12/50 (24%) ≈ 25% ✅
- Multi-context: 13/50 (26%) ≈ 25% ✅
