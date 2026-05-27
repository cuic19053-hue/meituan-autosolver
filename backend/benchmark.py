import random
import os

from backend.primitives import (
    _parse_to_candidates_streaming,
    compute_penalty_score,
    greedy_min_cost,
    greedy_max_willingness,
    conflict_aware_greedy,
    hybrid_greedy,
)


def _read_input_text(filepath: str) -> str:
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


def _extract_all_task_ids(candidates):
    all_tasks = set()
    for tasks_str, _, _, _, _ in candidates:
        all_tasks.update(tasks_str.split(','))
    return all_tasks


def _random_baseline(candidates: list) -> list:
    n = len(candidates)
    indices = list(range(n))
    random.shuffle(indices)

    assigned_c = set()
    assigned_t = set()
    result = []

    for idx in indices:
        tasks_str, courier, _score, _will, _tc = candidates[idx]
        if courier in assigned_c:
            continue
        ts = tasks_str.split(',')
        if any(t in assigned_t for t in ts):
            continue
        assigned_c.add(courier)
        assigned_t.update(ts)
        result.append((tasks_str, [courier]))

    return result


def run_benchmark(input_text: str) -> dict:
    from backend.solver_engine import solve

    candidates = _parse_to_candidates_streaming(input_text)
    all_task_ids = _extract_all_task_ids(candidates)
    all_task_count = len(all_task_ids)

    our_solution = solve(input_text)
    our_score = compute_penalty_score(our_solution, candidates, all_task_count)

    baselines = {
        "random_assignment": _random_baseline,
        "greedy_min_cost": greedy_min_cost,
        "greedy_max_willingness": greedy_max_willingness,
        "conflict_aware_greedy": conflict_aware_greedy,
        "hybrid_greedy": hybrid_greedy,
    }

    baseline_scores = {}
    improvements = {}

    for name, func in baselines.items():
        solution = func(candidates)
        score = compute_penalty_score(solution, candidates, all_task_count)
        baseline_scores[name] = score
        if score != 0:
            improvements[name] = (score - our_score) / score * 100
        else:
            improvements[name] = 0.0

    return {
        "our_score": our_score,
        "baseline_scores": baseline_scores,
        "improvements": improvements,
    }


def print_benchmark_report(report: dict):
    our_score = report["our_score"]
    baseline_scores = report["baseline_scores"]
    improvements = report["improvements"]

    print("=" * 70)
    print("BENCHMARK REPORT — Meituan AI Hackathon Track 4")
    print("=" * 70)
    print(f"{'Strategy':<28} {'Score':>12} {'Improvement':>14}")
    print("-" * 70)

    for name, score in baseline_scores.items():
        imp = improvements[name]
        sign = "+" if imp > 0 else ""
        print(f"{name:<28} {score:>12.2f} {sign}{imp:>13.2f}%")

    print("-" * 70)
    print(f"{'OUR SOLUTION':<28} {our_score:>12.2f}")
    print("=" * 70)

    best_baseline = min(baseline_scores, key=baseline_scores.get)
    best_baseline_score = baseline_scores[best_baseline]
    best_imp = improvements[best_baseline]
    print(f"\nBest baseline: {best_baseline} ({best_baseline_score:.2f})")
    print(f"Our improvement over best baseline: {best_imp:+.2f}%")


def run_benchmark_from_file(filepath: str) -> dict:
    input_text = _read_input_text(filepath)
    return run_benchmark(input_text)


if __name__ == "__main__":
    DATA_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "large_seed301.txt",
    )
    report = run_benchmark_from_file(DATA_FILE)
    print_benchmark_report(report)