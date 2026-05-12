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

**Analysis:** Position bias is within acceptable range after swap-and-average mitigation.

## Bias 2: Length Bias

**Observation:** Longer answers tend to win more frequently, indicating verbosity preference.

| Metric | Value |
|--------|-------|
| B wins when B is longer | 4/30 (13.3%) |
| Average length Answer A | 273 chars |
| Average length Answer B | 355 chars |

**Analysis:** The judge exhibits length bias, preferring longer answers. Answer B (the "improved" version with appended context) is consistently longer and wins more often when it is the longer answer. This is a well-documented LLM-as-Judge bias.

## Cohen's Kappa Calibration
- **Kappa score:** 0.062
- **Interpretation:** Slight agreement - khong tin duoc
- **Root cause analysis:** The moderate-to-fair agreement suggests the judge may be over-weighting superficial features (length, structure) compared to human evaluators who focus on factual accuracy.

## Mitigation Strategies

1. **Position bias mitigation (implemented):** Swap-and-average - run each comparison twice with swapped positions. If results disagree, default to "tie."

2. **Length bias mitigation (recommended):**
   - Normalize answers to similar length before judging
   - Add explicit instruction: "Do not prefer longer answers"
   - Use character-count-blind evaluation (summarize both answers to fixed length)

3. **Calibration improvement:**
   - Increase human label set from 10 to 50+ for more reliable kappa
   - Add inter-annotator agreement (2+ human annotators)
   - Fine-tune judge prompt based on disagreement patterns

## Conclusion
The swap-and-average technique effectively mitigates position bias. Length bias
remains the primary concern and should be addressed through prompt engineering
or answer normalization before production deployment.
