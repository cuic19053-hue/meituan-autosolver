# Tasks

- [x] Task 1: 重写 solver_engine.py 实现 ST-HAF 两阶段架构
  - [x] 保留 `parse_seed_file()` 函数不变
  - [x] 阶段一：竞标阶段 — 计算 Utility + 降序排列
  - [x] 阶段二：冲突排查 — 区分运力冲突 `[系统拦截]` 和任务冲突 `[节点冲突]`
  - [x] 合法匹配日志前缀改为 `[AI_ALLOTMENT]`
  - [x] 差异化 KPI：efficiency_gain = 实际总效用/理论最大效用×100%，completion_rate = 已匹配任务/总任务×100%
  - [x] latency 使用 time.perf_counter() 真实计时
  - [x] solutions 输出保留 courier/tasks 字段
  - [x] 推演完毕汇总日志包含：锚定任务数、激活运力数、全局效用峰值

- [x] Task 2: 适配 SolutionTerminal.jsx 新日志前缀
  - [x] 确保 `[AI_ALLOTMENT]` 前缀正常渲染（绿色行）
  - [x] 确保 `[系统拦截]` 和 `[节点冲突]` 前缀正常渲染
  - [x] 不修改 TerminalRow 组件的核心逻辑

# Task Dependencies
- 所有 Task 已完成