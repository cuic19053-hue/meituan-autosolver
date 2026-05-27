# Tasks

- [x] Task 1: 重写 solver_engine.py 为 Meta-Agent + ST-HAF 两层架构
  - [x] 实现 MetaAgent 类：大盘分析 + 动态权重决策 + 元认知日志
  - [x] 实现 STHAFEngine 类：接收权重 + 新效用公式 + 降序排列 + O(1) 冲突检测
  - [x] 新效用公式：`Utility = (100 - score) × w_score + (willingness × 100) × w_will`
  - [x] 动态权重：avg_will < 0.3 → w_will=0.6, w_score=0.4；否则 w_will=0.3, w_score=0.7
  - [x] 元认知日志：[META_AGENT] + [META_REFLECTION]
  - [x] 保留 parse_seed_file() 函数签名不变
  - [x] 保留 execute_solve() 函数签名不变
  - [x] 保留 API 返回结构 { status, kpi, logs, solutions }
  - [x] KPI 差异化：efficiency_gain ≠ completion_rate
  - [x] latency 使用 time.perf_counter() 真实计时

- [x] Task 2: 适配 SolutionTerminal.jsx 新日志前缀
  - [x] 确保 [META_AGENT] 前缀正常渲染
  - [x] 确保 [META_REFLECTION] 前缀正常渲染（可选高亮）
  - [x] 不修改 TerminalRow 核心逻辑

# Task Dependencies
- 所有 Task 已完成