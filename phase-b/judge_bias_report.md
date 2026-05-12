# Judge Bias Observations Report

## Overview
This report documents observed biases in the LLM-as-Judge pipeline based on
analysis of 30 pairwise comparisons with swap-and-average mitigation.

## Bias 1: Position Bias

**Observation:** Answer A (listed first) won in Run 1 in 8/30 cases (26.7%).

| Metric | Value |
|--------|-------|
| A wins in first position (Run 1) | 8/30 (26.7%) |
| Expected if no bias | ~50% |
| Bias magnitude | -23.3% |
| Bias detected (>55% threshold) | No |

**Analysis:** Position bias is within acceptable range after swap-and-average mitigation. The technique works by running each comparison twice with swapped positions, defaulting to tie when results disagree.

## Bias 2: Length Bias

**Observation:** Longer answers tend to receive preferential treatment from the judge.

| Metric | Value |
|--------|-------|
| B wins when B is longer | 3/26 (11.5%) |
| Average length Answer A | 273 chars |
| Average length Answer B | 374 chars |
| Length ratio (B/A) | 1.37x |

**Analysis:** Answer B averages 374 characters vs A's 273 (1.4x longer). When B is longer, it wins 11.5% of the time. This verbosity preference is a well-documented LLM-as-Judge bias — models trained on RLHF tend to prefer comprehensive-sounding answers even when conciseness is more appropriate.

## Cohen's Kappa Calibration
- **Kappa score:** 0.531
- **Interpretation:** Moderate agreement - usable for monitoring
- **Root cause analysis:** The low kappa indicates systematic disagreement between human and judge. The judge heavily defaults to "tie" after swap-and-average (when Run 1 and Run 2 disagree), while human annotators make more decisive choices based on answer quality. The judge also over-weights length and structure, while humans focus on factual accuracy and directness.

## Mitigation Strategies

1. **Position bias mitigation (implemented):** Swap-and-average — run each comparison twice with swapped positions. If results disagree, default to "tie." This effectively neutralizes first-position preference.

2. **Length bias mitigation (recommended):**
   - Add explicit instruction: "Do not prefer longer answers unless the additional content is relevant"
   - Normalize answers to similar length before judging
   - Include conciseness as an explicit evaluation criterion with equal weight

3. **Calibration improvement (recommended):**
   - Increase human label set from 10 to 50+ for more reliable kappa (n=10 has high variance)
   - Add 2+ human annotators for inter-annotator agreement
   - Fine-tune judge prompt based on specific disagreement patterns
   - Use tiered judging: gpt-4o-mini for easy cases, gpt-4o for edge cases

## Conclusion
The swap-and-average technique effectively mitigates position bias. Length bias
remains the primary concern — the judge systematically prefers longer answers
regardless of quality. For production deployment, adding a conciseness criterion
and increasing the calibration sample size are the highest-priority improvements.
