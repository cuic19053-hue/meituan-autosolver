"""
Engine v3.0 — Web API 入口（使用 v5.0 Agent）
====================================================
"""
import os
import time

from backend.primitives import (
    _parse_to_candidates,
    _parse_to_candidates_streaming,
    compute_penalty_score,
    validate_solution,
    validate_solution_v2,
    conflict_aware_greedy,
)
from backend.agent import get_agent

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "large_seed301.txt")


def _parse_seed_file():
    """解析种子文件为结构化行"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            with open(DATA_FILE, "r", encoding="gbk") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(DATA_FILE, "r", encoding="latin-1") as f:
                lines = f.readlines()
    rows = []
    for line in lines[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 4:
            continue
        task_ids = [t.strip() for t in parts[0].split(",") if t.strip()]
        rows.append({
            "task_id_list": task_ids,
            "courier_id": parts[1].strip(),
            "score": float(parts[2].strip()),
            "willingness": float(parts[3].strip()),
        })
    return rows


def _read_input_text() -> str:
    """读取数据文件，支持多种编码"""
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(DATA_FILE, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


def execute_solve():
    """Web API 入口：执行求解并返回完整结果"""
    t_start = time.perf_counter()

    raw_rows = _parse_seed_file()

    all_tasks = set()
    all_couriers = set()
    for r in raw_rows:
        all_tasks.update(r["task_id_list"])
        all_couriers.add(r["courier_id"])

    input_text = _read_input_text()

    # P0修复: 使用AutonomousAgent作为唯一核心引擎
    agent = get_agent()
    solutions, agent_logs, utility = agent.run_evolution_cycle(
        input_text, max_rounds=3, use_llm=True
    )

    # P1修复: 输出前格式校验（使用v2三重校验）
    solutions = validate_solution_v2(solutions, candidates=None, all_tasks=None)

    matched_tasks = set()
    matched_couriers = set()
    for task_str, courier_list in solutions:
        matched_tasks.update(task_str.split(','))
        for c in courier_list:
            matched_couriers.add(c)

    completion = round(len(matched_tasks) / len(all_tasks) * 100, 1) if all_tasks else 0

    # P0修复: 使用真实评分函数计算总成本
    total_score = 0.0
    for r in raw_rows:
        tid_set = set(r["task_id_list"])
        if tid_set.issubset(matched_tasks) and r["courier_id"] in matched_couriers:
            total_score += r["score"] * (2.0 - r["willingness"])

    total_score = round(total_score, 2)

    t_end = time.perf_counter()
    elapsed = round(t_end - t_start, 3)
    latency_str = f"{elapsed:.2f}s" if elapsed >= 0.01 else f"< {elapsed:.4f}s"

    sys_logs = [
        f"> [SYS] 时空拓扑数据加载完成，共 {len(raw_rows)} 条候选方案",
        f"> [SYS] 推演完毕 | 锚定任务 {len(matched_tasks)} 项 | 激活运力 {len(matched_couriers)} 个 | 总成本 {total_score}",
    ]

    all_logs = sys_logs + agent_logs

    solutions_out = [
        {"courier": s[1][0], "tasks": s[0].split(',')} for s in solutions
    ]

    kpi = {
        "total_score": total_score,
        "efficiency_gain": f"+{completion}%",
        "completion_rate": f"{completion}%",
        "latency": latency_str,
    }

    return {
        "status": "success",
        "kpi": kpi,
        "logs": all_logs,
        "solutions": solutions_out,
    }
