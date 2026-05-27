"""
FastAPI Main Server v2.0 — 统一API入口
====================================================
P1修复: 删除与赛道四无关的 AgentEngine/RouterAgent/InventoryAgent/SPATIAL_NODES/PART_CATALOG
保留配送分配求解相关的API路由
"""
import os
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from backend.minimax_client import minimax_chat
from backend.data_processor import build_graph_data
from backend.solver_engine import execute_solve, solve as solver_solve
from backend.data_service import get_map_init, solve as data_solve

app = FastAPI(title="AutoSolver API", version="2.0.0")

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_seed_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "large_seed301.txt")
_raw_data_cache: dict | None = None


def _load_raw_data() -> dict:
    global _raw_data_cache
    if _raw_data_cache is not None:
        return _raw_data_cache
    try:
        _raw_data_cache = build_graph_data(_seed_file_path)
        print(f"[INFO] Raw data cached successfully from: {_seed_file_path}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        _raw_data_cache = None
    return _raw_data_cache or {}


@app.get("/api/raw_data")
async def get_raw_data():
    data = _load_raw_data()
    if not data:
        return {"error": f"数据文件未找到: {_seed_file_path}"}
    return data


@app.get("/api/map_init")
async def map_init():
    try:
        data = get_map_init()
        return data
    except FileNotFoundError as e:
        return {"error": f"数据文件未找到: {_seed_file_path}"}


@app.get("/api/solver")
async def solver():
    try:
        result = data_solve()
        return result
    except FileNotFoundError as e:
        return {"error": f"数据文件未找到: {_seed_file_path}"}


@app.get("/api/execute_solve")
async def execute_solve_api():
    try:
        result = execute_solve()
        print(f"[INFO] Solver executed: {len(result['solutions'])} solutions, completion_rate: {result['kpi']['completion_rate']}, efficiency: {result['kpi']['efficiency_gain']}")
        return result
    except Exception as e:
        print(f"[ERROR] Solver failed: {e}")
        return {"error": str(e)}


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    reply: str


class ReportRequest(BaseModel):
    optimization_result: Optional[dict] = None


class ReportResponse(BaseModel):
    report: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    system_prompt = (
        "你是 AutoSolver 配送分配系统的智能助手。你可以回答关于配送分配、调度优化、策略选择等问题。"
        "你的语言风格：专业、简洁、赛博工业风。用中文回答。"
        "系统使用多种策略（conflict_aware_greedy, greedy_min_cost, greedy_max_willingness, "
        "utility_density_greedy, hybrid_greedy, local_search_2opt, beam_search）求解配送分配问题。"
        "评分函数: Score = Σ(score × (2.0 - willingness)) + penalty × n_rejected，Score越低越好。"
    )
    if request.context:
        system_prompt += f"\n当前调度上下文：{json.dumps(request.context, ensure_ascii=False)}"

    try:
        reply = await minimax_chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
            temperature=0.7,
            max_tokens=512,
        )
    except Exception as e:
        reply = f"[系统错误] AI助手暂时不可用：{str(e)}"

    return ChatResponse(reply=reply)


@app.post("/api/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    opt_data = request.optimization_result or {}
    context = json.dumps(opt_data, ensure_ascii=False) if opt_data else "无调度数据"

    try:
        report = await minimax_chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是 AutoSolver 配送分配系统的报告生成器。根据调度结果数据，生成一份结构化的调度报告。\n"
                        "报告格式：\n"
                        "## 调度执行报告\n"
                        "### 1. 执行摘要\n（一句话总结）\n"
                        "### 2. 关键指标\n（总成本、覆盖率、延迟、策略选择）\n"
                        "### 3. 策略分析\n（使用了什么策略，效果如何）\n"
                        "### 4. 风险提示\n（潜在问题）\n"
                        "### 5. 优化建议\n（下一步行动）\n"
                        "用中文输出，风格专业简洁。"
                    ),
                },
                {"role": "user", "content": f"请根据以下调度数据生成报告：\n{context}"},
            ],
            temperature=0.5,
            max_tokens=1024,
        )
    except Exception as e:
        report = f"报告生成失败：{str(e)}"

    return ReportResponse(report=report)


class ExecuteSolveRequest(BaseModel):
    use_llm: bool = False
    filename: Optional[str] = None
    nodeCount: Optional[int] = None
    rawData: Optional[str] = None


class ExecuteSolveResponse(BaseModel):
    status: str
    solutions: List[dict]
    kpi: dict
    logs: List[str]


@app.post("/api/execute_solve", response_model=ExecuteSolveResponse)
async def execute_solve_post(request: ExecuteSolveRequest):
    from backend.solver_engine import execute_solve as run_solver
    result = run_solver(input_text_override=request.rawData, use_llm=request.use_llm)
    return ExecuteSolveResponse(**result)


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
