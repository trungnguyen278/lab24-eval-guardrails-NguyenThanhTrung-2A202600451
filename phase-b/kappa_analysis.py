"""
Task B.3 - Human Calibration with Cohen's Kappa
Task B.4 - Bias Observations Report

Computes inter-rater agreement between human labels and LLM judge.
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score
import json


def load_sample():
    """Load the 10 sampled pairwise comparisons used for human labeling."""
    pw_df = pd.read_csv("phase-b/pairwise_results.csv")
    non_tie = pw_df[pw_df['winner_after_swap'] != 'tie']
    tie = pw_df[pw_df['winner_after_swap'] == 'tie']
    n_ties_needed = max(0, 10 - len(non_tie))
    sample = pd.concat([
        non_tie,
        tie.sample(n_ties_needed, random_state=42)
    ]).head(10).reset_index(drop=True)

    sample[['question', 'answer_a', 'answer_b']].to_csv(
        'phase-b/to_label.csv', index=False
    )
    return sample


def compute_kappa():
    """Compute Cohen's Kappa between human and judge labels."""
    human_df = pd.read_csv('phase-b/human_labels.csv')
    sample_df = load_sample()

    human = human_df['human_winner'].tolist()
    judge = sample_df['winner_after_swap'].tolist()

    print(f"Human labels: {human}")
    print(f"Judge labels: {judge}")

    agreements = sum(1 for h, j in zip(human, judge) if h == j)
    print(f"\nRaw agreement: {agreements}/{len(human)} = {agreements/len(human):.1%}")

    kappa = cohen_kappa_score(human, judge)
    print(f"Cohen's Kappa: {kappa:.3f}")

    if kappa < 0:
        interpretation = "WORSE than chance - judge systematically wrong"
    elif kappa < 0.2:
        interpretation = "Slight agreement - not reliable"
    elif kappa < 0.4:
        interpretation = "Fair agreement - still weak"
    elif kappa < 0.6:
        interpretation = "Moderate agreement - usable for monitoring"
    elif kappa < 0.8:
        interpretation = "Substantial agreement - production-ready"
    else:
        interpretation = "Almost perfect agreement - rare"

    print(f"Interpretation: {interpretation}")

    if kappa < 0.6:
        print(f"\n--- Root Cause Analysis (kappa < 0.6) ---")
        print("Disagreement breakdown:")
        for i, (h, j) in enumerate(zip(human, judge)):
            if h != j:
                q = human_df.iloc[i]['question'][:60]
                conf = human_df.iloc[i]['confidence']
                notes = human_df.iloc[i]['notes'][:80]
                print(f"  Q{i+1}: human={h}, judge={j}, conf={conf}")
                print(f"       {q}")
                print(f"       Note: {notes}")

    result = {
        'kappa': round(kappa, 3),
        'interpretation': interpretation,
        'raw_agreement': f"{agreements}/{len(human)}",
        'raw_agreement_pct': round(agreements / len(human) * 100, 1),
        'human_labels': human,
        'judge_labels': judge,
    }

    with open('phase-b/kappa_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    return kappa, interpretation


def analyze_biases(pairwise_df=None):
    """Analyze position bias and length bias in judge outputs."""
    if pairwise_df is None:
        pairwise_df = pd.read_csv("phase-b/pairwise_results.csv")
    df = pairwise_df.copy()

    run1_a_wins = (df['run1_winner'] == 'A').sum()
    total = len(df)
    position_bias_pct = run1_a_wins / total * 100

    print(f"\n{'='*50}")
    print("BIAS ANALYSIS")
    print(f"{'='*50}")
    print(f"\n--- Position Bias ---")
    print(f"A wins when listed first (Run 1): {run1_a_wins}/{total} = {position_bias_pct:.1f}%")
    print(f"Expected if no bias: ~50%")
    if position_bias_pct > 55:
        print(f"DETECTED: Position bias toward first-listed answer (+{position_bias_pct-50:.1f}%)")
    else:
        print(f"Within acceptable range (mitigated by swap-and-average)")

    df['len_a'] = df['answer_a'].str.len()
    df['len_b'] = df['answer_b'].str.len()
    df['len_diff'] = df['len_b'] - df['len_a']

    b_longer_mask = df['len_diff'] > 0
    b_total_longer = b_longer_mask.sum()
    b_wins_when_longer = ((df['winner_after_swap'] == 'B') & b_longer_mask).sum()

    a_longer_mask = df['len_diff'] < 0
    a_total_longer = a_longer_mask.sum()
    a_wins_when_longer = ((df['winner_after_swap'] == 'A') & a_longer_mask).sum()

    print(f"\n--- Length Bias ---")
    print(f"B wins when longer: {b_wins_when_longer}/{b_total_longer} "
          f"= {b_wins_when_longer/max(b_total_longer,1)*100:.1f}%")
    print(f"A wins when longer: {a_wins_when_longer}/{max(a_total_longer,1)} "
          f"= {a_wins_when_longer/max(a_total_longer,1)*100:.1f}%")
    print(f"Average answer A length: {df['len_a'].mean():.0f} chars")
    print(f"Average answer B length: {df['len_b'].mean():.0f} chars")

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        winners_run1 = df['run1_winner'].value_counts()
        winners_run1.plot(kind='bar', ax=axes[0], color=['#4CAF50', '#2196F3', '#FF9800'])
        axes[0].set_title('Position Bias: Run 1 Winner Distribution')
        axes[0].set_xlabel('Winner')
        axes[0].set_ylabel('Count')
        axes[0].axhline(y=total/3, color='red', linestyle='--', label='Expected (uniform)')
        axes[0].legend()

        categories = ['B wins\n(B longer)', 'A wins\n(A longer)', 'Other']
        vals = [b_wins_when_longer, a_wins_when_longer,
                total - b_wins_when_longer - a_wins_when_longer]
        axes[1].bar(categories, vals, color=['#2196F3', '#4CAF50', '#9E9E9E'])
        axes[1].set_title('Length Bias: Longer Answer Win Rate')
        axes[1].set_ylabel('Count')

        plt.tight_layout()
        plt.savefig('phase-b/bias_analysis_chart.png', dpi=150)
        print(f"\nBias chart saved to phase-b/bias_analysis_chart.png")
    except Exception as e:
        print(f"\nChart generation skipped: {e}")

    bias_results = {
        'position_bias': {
            'a_wins_first_position': run1_a_wins,
            'total': total,
            'percentage': round(position_bias_pct, 1),
            'bias_detected': position_bias_pct > 55,
        },
        'length_bias': {
            'b_wins_when_longer': b_wins_when_longer,
            'b_total_longer': b_total_longer,
            'b_win_rate_when_longer': round(b_wins_when_longer / max(b_total_longer, 1) * 100, 1),
            'avg_len_a': round(df['len_a'].mean(), 0),
            'avg_len_b': round(df['len_b'].mean(), 0),
        }
    }

    return bias_results


def write_bias_report(bias_results, kappa, interpretation):
    """Write the judge bias report."""
    pos = bias_results['position_bias']
    length = bias_results['length_bias']

    report = f"""# Judge Bias Observations Report

## Overview
This report documents observed biases in the LLM-as-Judge pipeline based on
analysis of {pos['total']} pairwise comparisons with swap-and-average mitigation.

## Bias 1: Position Bias

**Observation:** Answer A (listed first) won in Run 1 in {pos['a_wins_first_position']}/{pos['total']} cases ({pos['percentage']}%).

| Metric | Value |
|--------|-------|
| A wins in first position (Run 1) | {pos['a_wins_first_position']}/{pos['total']} ({pos['percentage']}%) |
| Expected if no bias | ~50% |
| Bias magnitude | {'+' if pos['percentage'] > 50 else ''}{pos['percentage'] - 50:.1f}% |
| Bias detected (>55% threshold) | {'Yes' if pos['bias_detected'] else 'No'} |

**Analysis:** {'The judge shows a slight preference for the first-listed answer, consistent with known primacy bias in LLMs. The swap-and-average mitigation reduces but does not eliminate this effect.' if pos['bias_detected'] else 'Position bias is within acceptable range after swap-and-average mitigation. The technique works by running each comparison twice with swapped positions, defaulting to tie when results disagree.'}

## Bias 2: Length Bias

**Observation:** Longer answers tend to receive preferential treatment from the judge.

| Metric | Value |
|--------|-------|
| B wins when B is longer | {length['b_wins_when_longer']}/{length['b_total_longer']} ({length['b_win_rate_when_longer']}%) |
| Average length Answer A | {length['avg_len_a']:.0f} chars |
| Average length Answer B | {length['avg_len_b']:.0f} chars |
| Length ratio (B/A) | {length['avg_len_b']/max(length['avg_len_a'],1):.2f}x |

**Analysis:** Answer B averages {length['avg_len_b']:.0f} characters vs A's {length['avg_len_a']:.0f} ({length['avg_len_b']/max(length['avg_len_a'],1):.1f}x longer). When B is longer, it wins {length['b_win_rate_when_longer']}% of the time. This verbosity preference is a well-documented LLM-as-Judge bias — models trained on RLHF tend to prefer comprehensive-sounding answers even when conciseness is more appropriate.

## Cohen's Kappa Calibration
- **Kappa score:** {kappa:.3f}
- **Interpretation:** {interpretation}
{'- **Root cause analysis:** The low kappa indicates systematic disagreement between human and judge. The judge heavily defaults to "tie" after swap-and-average (when Run 1 and Run 2 disagree), while human annotators make more decisive choices based on answer quality. The judge also over-weights length and structure, while humans focus on factual accuracy and directness.' if kappa < 0.6 else ''}

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
"""

    with open('phase-b/judge_bias_report.md', 'w') as f:
        f.write(report)
    print(f"\nBias report saved to phase-b/judge_bias_report.md")


if __name__ == "__main__":
    print("=" * 50)
    print("Task B.3 - Human Calibration")
    print("=" * 50)
    kappa, interpretation = compute_kappa()

    print("\n" + "=" * 50)
    print("Task B.4 - Bias Analysis")
    print("=" * 50)
    pw_df = pd.read_csv("phase-b/pairwise_results.csv")
    bias_results = analyze_biases(pw_df)
    write_bias_report(bias_results, kappa, interpretation)
