"""
Multi-Scenario Stability Test Harness
============================================================================
Meituan AI Hackathon Track 4 — AutoSolver (delivery assignment problem)

Provides:
  - 8 predefined test scenarios with data generation parameters
  - generate_test_data(): deterministic tab-separated test data generation
  - run_stability_test(): multi-seed, multi-scenario solver evaluation
  - print_report(): formatted stability report table

Scoring: Score = Sum(score * (2.0 - willingness)) + penalty * n_rejected
         penalty defaults to 100, lower Score is better.
"""
import math
import random
import time

from backend.primitives import (
    _extract_all_task_ids,
    _parse_to_candidates_streaming,
    compute_penalty_score,
)
from backend.solver_engine import solve

SCENARIOS = {
    "small_sparse": {
        "candidates": (10, 50),
        "max_couriers": 5,
        "will_range": (0.2, 0.9),
    },
    "medium_standard": {
        "candidates": (100, 500),
        "max_couriers": 20,
        "will_range": (0.3, 0.8),
    },
    "large_dense": {
        "candidates": (5000, 10000),
        "max_couriers": 50,
        "will_range": (0.1, 0.9),
    },
    "low_willingness": {
        "candidates": (100, 500),
        "max_couriers": 20,
        "will_range": (0.01, 0.15),
    },
    "high_density": {
        "candidates": (500, 2000),
        "max_couriers": 10,
        "will_range": (0.3, 0.8),
    },
    "all_conflict": {
        "candidates": (50, 200),
        "max_couriers": 1,
        "will_range": (0.3, 0.8),
    },
    "single_courier": {
        "candidates": (20, 100),
        "max_couriers": 1,
        "will_range": (0.3, 0.8),
    },
    "empty_or_malformed": {
        "candidates": (0, 0),
        "max_couriers": 0,
        "will_range": (0.0, 0.0),
    },
}

PENALTY = 100


def generate_test_data(scenario: str, seed: int = 42) -> str:
    """
    Generate deterministic tab-separated test data for a given scenario.

    Args:
        scenario: One of the 8 predefined scenario names (see SCENARIOS dict).
        seed: Random seed for reproducible generation.

    Returns:
        Tab-separated string with header "task_id_list\\tcourier_id\\tscore\\twillingness"
        followed by data rows.  For "empty_or_malformed" the return value alternates
        between an empty string and a deliberately malformed payload.

    Raises:
        KeyError: If scenario is not one of the predefined names.
    """
    rng = random.Random(seed)
    params = SCENARIOS[scenario]

    if scenario == "empty_or_malformed":
        if seed % 2 == 0:
            return ""
        return "task_id_list\tcourier_id\tscore\twillingness\nbad,line,missing,fields"

    min_cand, max_cand = params["candidates"]
    max_couriers = params["max_couriers"]
    will_min, will_max = params["will_range"]

    n_candidates = rng.randint(min_cand, max_cand)
    n_couriers = rng.randint(1, max(1, max_couriers))

    lines = ["task_id_list\tcourier_id\tscore\twillingness"]

    for i in range(n_candidates):
        task_id = f"t{i}"
        courier_id = f"c{rng.randint(0, n_couriers - 1)}"
        score = round(rng.uniform(1.0, 100.0), 2)
        willingness = round(rng.uniform(will_min, will_max), 4)
        lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")

    return "\n".join(lines)


def _run_single_trial(input_text: str) -> tuple:
    """
    Execute one solver trial and return (score, latency_s, success).

    Args:
        input_text: Tab-separated candidate data string.

    Returns:
        Tuple of (score: float | None, latency: float | None, success: bool).
    """
    t_start = time.perf_counter()
    try:
        solutions = solve(input_text)
    except Exception:
        return None, None, False

    latency = time.perf_counter() - t_start

    try:
        candidates = _parse_to_candidates_streaming(input_text)
        all_task_count = len(_extract_all_task_ids(candidates))
        score = compute_penalty_score(solutions, candidates, all_task_count, PENALTY)
    except Exception:
        return None, latency, False

    return score, latency, True


def run_stability_test(repeat: int = 5) -> dict:
    """
    Run stability tests across all 8 scenarios using multiple seeds.

    Args:
        repeat: Number of trials per scenario (seeds 0 .. repeat-1).

    Returns:
        Nested dict keyed by scenario name, each containing:
            mean_score, std_score, mean_latency, max_latency, success_rate.
        Values are None when no trials succeeded.
    """
    results = {}

    for scenario_name in SCENARIOS:
        scores = []
        latencies = []
        success_count = 0

        for seed in range(repeat):
            input_text = generate_test_data(scenario_name, seed=seed)
            score, latency, success = _run_single_trial(input_text)

            if success:
                success_count += 1
                scores.append(score)
                latencies.append(latency)

        n = len(scores)
        if n > 0:
            mean_score = sum(scores) / n
            variance = sum((s - mean_score) ** 2 for s in scores) / n
            std_score = math.sqrt(variance)
            mean_latency = sum(latencies) / n
            max_latency = max(latencies)
            success_rate = n / repeat
        else:
            mean_score = None
            std_score = None
            mean_latency = None
            max_latency = None
            success_rate = 0.0

        results[scenario_name] = {
            "mean_score": mean_score,
            "std_score": std_score,
            "mean_latency": mean_latency,
            "max_latency": max_latency,
            "success_rate": success_rate,
        }

    return results


def _fmt(val, template, fallback="     N/A"):
    """Format a numeric value with the given template; return fallback if None."""
    if val is None:
        return fallback
    return template.format(val)


def print_report(results: dict):
    """
    Print a formatted stability-test report table to stdout.

    Args:
        results: Nested dict as returned by run_stability_test().
    """
    header = (
        f"{'Scenario':<22s} | {'Mean Score':>12s} | {'Std Score':>10s} | "
        f"{'Mean Lat':>10s} | {'Max Lat':>10s} | {'Success':>8s}"
    )
    sep = "-" * len(header)

    print("\n" + "=" * len(header))
    print("STABILITY TEST REPORT")
    print("=" * len(header))
    print(header)
    print(sep)

    for name in SCENARIOS:
        r = results.get(name, {})
        mean_score = _fmt(r.get("mean_score"), "{:>12.2f}")
        std_score = _fmt(r.get("std_score"), "{:>10.2f}")
        mean_lat = _fmt(r.get("mean_latency"), "{:>9.3f}s") if r.get("mean_latency") is not None else "     N/A"
        max_lat = _fmt(r.get("max_latency"), "{:>9.3f}s") if r.get("max_latency") is not None else "     N/A"
        raw_rate = r.get("success_rate")
        if raw_rate is None:
            rate = "   0.0%"
        else:
            rate = f"{raw_rate * 100:>7.1f}%"

        print(
            f"{name:<22s} | {mean_score} | {std_score} | "
            f"{mean_lat} | {max_lat} | {rate}"
        )

    print(sep)

    total_success = sum(
        1 for r in results.values() if r.get("success_rate", 0) >= 1.0
    )
    total_scenarios = len(SCENARIOS)
    print(f"\nFully-stable scenarios: {total_success}/{total_scenarios}")


if __name__ == "__main__":
    print("Multi-Scenario Stability Test Harness")
    print("Track 4 — AutoSolver (delivery assignment)")
    print("=" * 80)

    print("\n[1/3] Generating test data for all scenarios ...")
    for name in SCENARIOS:
        sample = generate_test_data(name, seed=0)
        sample_lines = sample.count("\n")
        print(f"       {name:<25s}  seed=0  ->  {sample_lines} data lines")

    print("\n[2/3] Running stability tests (5 repeats per scenario) ...")
    t0 = time.perf_counter()
    results = run_stability_test(repeat=5)
    elapsed = time.perf_counter() - t0
    print(f"       Completed in {elapsed:.1f}s")

    print("\n[3/3] Report")
    print_report(results)