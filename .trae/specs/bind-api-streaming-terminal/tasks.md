# Tasks

- [x] Task 1: 重构 useSolverEngine.js 状态机与预设日志
  - [x] 保留现有 IDLE / FETCHING / ERROR 三态状态机
  - [x] 在 `initiate()` 进入 FETCHING 时，立即设置 `result` 包含 3 条预设日志的 `logs` 数组和空的 `solutions`
  - [x] API 成功后，用真实 `data` 覆盖 `result`
  - [x] API 失败后，设置 `result` 包含错误日志 `> [SYS_ERROR] 核心引擎离线，请检查云端算力节点。`
  - [x] 保留 `reset()` 清除所有状态
  - [x] `kpi` 从 `result?.kpi` 提取，保持现有返回结构

- [x] Task 2: 重构 SolutionTerminal.jsx 日志流式渲染 + KPI 字段修复
  - [x] 将流式渲染目标从 `solutions` 改为 `logs` 数组（30ms 间隔）
  - [x] 预处理：提取后端 `logs` 中带 `> ` 前缀的行用于流式渲染
  - [x] 保留 `solutions` 的并行流式渲染（兼容旧逻辑，作为分配结果行）
  - [x] 修复 KPI 字段引用：`totalScore` → 从 `data?.kpi?.efficiency_gain` 提取数值；`matchRate` → 从 `completion_rate` 提取
  - [x] 修复 Summary 弹窗中 efficiencyGain 的计算逻辑，改用 `data?.kpi?.efficiency_gain`
  - [x] 更新预设加载文本：`> [系统] 正在连接 AI 调度引擎...` → `> [SYS] 正在建立加密云端链路...`
  - [x] 更新错误显示文本：`[FAULT] AI 调度引擎连接中断` → `> [SYS_ERROR] 核心引擎离线，请检查云端算力节点。`
  - [x] 保留 autoscroll（scrollTop）、TerminalRow、hover override、AnimatePresence Summary 全部动效

- [x] Task 3: 修复 LiveTelemetry.jsx KPI 字段对齐
  - [x] 第一行"全域待分配锚点"：`kpi?.total_score` → 改为显示 `kpi?.efficiency_gain`
  - [x] 第二行"云端在线运力"：修复重复百分号问题
  - [x] 第三行"运算耗时"：`kpi?.latency` 兼容现有

# Task Dependencies
- 所有 Task 已完成