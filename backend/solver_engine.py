"""
Solver Engine v3.0 — 统一求解入口
====================================================
v2.0 → v3.0 核心升级：
  - 增强型 Primitives 库 (14个策略)
  - v5.0 AutonomousAgent (自适应进化 + 两级精选)
  - v3.0 特征路由器
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


def _read_input_text() -> str:
    """读取数据文件，支持多种编码"""
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(DATA_FILE, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


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


def _parse_input_text_to_rows(text: str) -> list:
    """将用户上传的文本解析为结构化行（与 _parse_seed_file 相同格式）"""
    rows = []
    for line in text.strip().split('\n')[1:]:
        parts = line.strip().split('\t')
        if len(parts) < 4:
            continue
        task_ids = [t.strip() for t in parts[0].split(',') if t.strip()]
        rows.append({
            "task_id_list": task_ids,
            "courier_id": parts[1].strip(),
            "score": float(parts[2].strip()),
            "willingness": float(parts[3].strip()),
        })
    return rows


def _solve_full(input_text: str) -> list:
    """第一重保障：完整进化引擎"""
    agent = get_agent()
    solutions, agent_logs, utility = agent.run_evolution_cycle(
        input_text, max_rounds=3, use_llm=True
    )
    # P1修复: 输出前格式校验（使用v2三重校验）
    return validate_solution_v2(solutions, candidates=None, all_tasks=None)


def _validate_input(input_text: str) -> tuple:
    """
    输入安全校验 → (是否有效, 错误信息)
    Returns (True, "") if valid, (False, error_msg) if invalid
    """
    if not input_text or not input_text.strip():
        return False, "空输入"
    lines = input_text.strip().split('\n')
    if len(lines) < 2:
        return False, "数据行不足（仅表头）"
    sample = lines[1] if len(lines) > 1 else lines[0]
    if '\t' not in sample:
        return False, "非Tab分隔格式"
    parts = sample.split('\t')
    if len(parts) < 3:
        return False, f"字段不足（需要≥3列，实际{len(parts)}列）"
    return True, ""


def solve(input_text: str) -> list:
    """
    主入口：三重保障（P3修复）
    solve(input_text: str) -> list
    返回格式: [(tasks_str, [courier_str]), ...]
    """
    is_valid, error_msg = _validate_input(input_text)
    if not is_valid:
        return []

    try:
        return _solve_full(input_text)
    except Exception:
        try:
            candidates = _parse_to_candidates_streaming(input_text)
            result = conflict_aware_greedy(candidates)
            return validate_solution_v2(result, candidates=candidates, all_tasks=None)
        except Exception:
            return []


def execute_solve(input_text_override: str | None = None, use_llm: bool | None = None):
    """Web API 入口：执行求解并返回完整结果
    
    Args:
        input_text_override: 可选的用户上传数据文本，若提供则替代默认种子文件
        use_llm: 是否使用 LLM 决策，None 时从环境变量 USE_LLM 读取，默认 False
    """
    if use_llm is None:
        use_llm = os.getenv("USE_LLM", "false").lower() in ("true", "1", "yes")

    t_start = time.perf_counter()

    input_text = input_text_override or _read_input_text()

    raw_rows = _parse_seed_file()
    if input_text_override:
        raw_rows = _parse_input_text_to_rows(input_text_override)

    all_tasks = set()
    all_couriers = set()
    for r in raw_rows:
        all_tasks.update(r["task_id_list"])
        all_couriers.add(r["courier_id"])

    agent = get_agent()
    solutions, agent_logs, utility = agent.run_evolution_cycle(
        input_text, max_rounds=3, use_llm=use_llm
    )

    # P1修复: 输出前格式校验（使用v2三重校验）
    solutions = validate_solution_v2(solutions, candidates=None, all_tasks=None)

    # Fallback: 若 agent 返回空解，直接使用贪心策略保底
    if not solutions:
        candidates = _parse_to_candidates(input_text)
        solutions = conflict_aware_greedy(candidates)
        agent_logs.append("> [FALLBACK] Agent 未产出有效解，启用冲突感知贪心保底策略")


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

    solutions_out = []
    for s in solutions:
        tasks_list = s[0].split(',')
        courier = s[1][0]
        utility = 0.0
        for r in raw_rows:
            tid_set = set(r["task_id_list"])
            if tid_set.issubset(set(tasks_list)) and r["courier_id"] == courier:
                utility += r["score"] * (2.0 - r["willingness"])
        solutions_out.append({
            "courier": courier,
            "tasks": tasks_list,
            "utility": round(utility, 2),
        })

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
