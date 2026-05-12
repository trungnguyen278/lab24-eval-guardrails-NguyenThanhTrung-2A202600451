"""
Task C.5 - Full Stack Integration & Latency Benchmark
Integrates input guardrails + RAG pipeline + output guardrails.
Measures end-to-end latency with P50/P95/P99 benchmarks.
"""

import asyncio
import time
import csv
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phase-c"))

from scripts.rag_pipeline import my_rag_pipeline
from input_guard import InputGuard, TopicGuard
from output_guard import OutputGuardAPI


input_guard = InputGuard()
topic_guard = TopicGuard()
output_guard = OutputGuardAPI()


def refuse_response():
    return "I'm sorry, I cannot process this request. Please ask a banking-related question."


def guarded_pipeline_sync(user_input: str) -> tuple[str, dict]:
    timings = {}

    t0 = time.perf_counter()
    sanitized, pii_latency = input_guard.sanitize(user_input)
    topic_ok, topic_reason = topic_guard.check(sanitized)
    timings['L1'] = (time.perf_counter() - t0) * 1000
    timings['L1_pii'] = pii_latency

    if not topic_ok:
        return refuse_response(), timings

    t0 = time.perf_counter()
    answer, contexts = my_rag_pipeline(sanitized)
    timings['L2'] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    is_safe, guard_result, guard_latency = output_guard.check(sanitized, answer)
    timings['L3'] = (time.perf_counter() - t0) * 1000

    if not is_safe:
        return refuse_response(), timings

    timings['total'] = timings['L1'] + timings['L2'] + timings['L3']

    return answer, timings


def baseline_pipeline(user_input: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    answer, contexts = my_rag_pipeline(user_input)
    latency = (time.perf_counter() - t0) * 1000
    return answer, latency


def load_test_queries(n: int = 100) -> list[str]:
    import pandas as pd
    testset = pd.read_csv("phase-a/testset_v1.csv")
    queries = testset['question'].tolist()
    while len(queries) < n:
        queries = queries + queries
    return queries[:n]


def run_benchmark(n: int = 100):
    queries = load_test_queries(n)

    print(f"\n{'='*60}")
    print(f"Full Stack Latency Benchmark ({n} requests)")
    print(f"{'='*60}")

    all_timings = []
    baseline_latencies = []
    refused = 0

    for i, q in enumerate(queries):
        answer, timings = guarded_pipeline_sync(q)
        all_timings.append(timings)

        if answer == refuse_response():
            refused += 1

        _, baseline_lat = baseline_pipeline(q)
        baseline_latencies.append(baseline_lat)

        if (i + 1) % 25 == 0:
            print(f"  Progress: {i+1}/{n} requests completed")

    print(f"\n{'='*60}")
    print("LAYER LATENCY REPORT")
    print(f"{'='*60}")

    for layer in ['L1', 'L2', 'L3', 'total']:
        vals = [t[layer] for t in all_timings if layer in t]
        if vals:
            p50 = np.percentile(vals, 50)
            p95 = np.percentile(vals, 95)
            p99 = np.percentile(vals, 99)
            mean = np.mean(vals)
            print(f"  {layer:>5s}: P50={p50:6.1f}ms  P95={p95:6.1f}ms  P99={p99:6.1f}ms  Mean={mean:6.1f}ms")

    baseline_p50 = np.percentile(baseline_latencies, 50)
    baseline_p95 = np.percentile(baseline_latencies, 95)
    baseline_p99 = np.percentile(baseline_latencies, 99)
    print(f"\n  Baseline (no guardrails):")
    print(f"  {'base':>5s}: P50={baseline_p50:6.1f}ms  P95={baseline_p95:6.1f}ms  P99={baseline_p99:6.1f}ms")

    total_vals = [t.get('total', 0) for t in all_timings if 'total' in t]
    if total_vals:
        overhead_p50 = np.percentile(total_vals, 50) - baseline_p50
        overhead_p95 = np.percentile(total_vals, 95) - baseline_p95
        print(f"\n  Guardrail overhead:")
        print(f"  P50 overhead: {overhead_p50:+.1f}ms")
        print(f"  P95 overhead: {overhead_p95:+.1f}ms")

    print(f"\n  Refused queries: {refused}/{n} ({refused/n*100:.1f}%)")

    l1_vals = [t['L1'] for t in all_timings if 'L1' in t]
    l3_vals = [t['L3'] for t in all_timings if 'L3' in t]
    l1_p95 = np.percentile(l1_vals, 95) if l1_vals else 0
    l3_p95 = np.percentile(l3_vals, 95) if l3_vals else 0

    print(f"\n  Target checks:")
    print(f"  L1 P95 < 50ms: {'PASS' if l1_p95 < 50 else 'FAIL'} ({l1_p95:.1f}ms)")
    print(f"  L3 P95 < 100ms: {'PASS' if l3_p95 < 100 else 'FAIL'} ({l3_p95:.1f}ms)")

    rows = []
    for i, t in enumerate(all_timings):
        rows.append({
            'request_id': i + 1,
            'L1_ms': round(t.get('L1', 0), 2),
            'L2_ms': round(t.get('L2', 0), 2),
            'L3_ms': round(t.get('L3', 0), 2),
            'total_ms': round(t.get('total', 0), 2),
            'baseline_ms': round(baseline_latencies[i], 2),
        })

    with open('phase-c/latency_benchmark.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['request_id', 'L1_ms', 'L2_ms', 'L3_ms', 'total_ms', 'baseline_ms'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nBenchmark data saved to phase-c/latency_benchmark.csv")
    return all_timings, baseline_latencies


if __name__ == "__main__":
    run_benchmark(100)
