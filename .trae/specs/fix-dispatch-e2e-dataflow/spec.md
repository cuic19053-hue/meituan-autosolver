# 修复调度功能端到端数据流 Spec

## Why
后端算法引擎 `solver_engine.py` 和 API 端点 `/api/execute_solve` 已验证正常（18 solutions, 178 logs, 87.5% completion），但前端调度功能存在数据流断裂：
1. `SolutionTerminal.jsx` 在 `externalResult` 为 null 时自动用 `apiBase` 发起独立 fetch，与 `useSolverEngine` 状态机冲突，导致终端在用户点击按钮前就开始刷屏
2. `apiBase` 默认值为 `'http://localhost:8080'`，即使 App.jsx 未传该 prop 也会触发独立 fetch
3. 两个数据源（useSolverEngine vs SolutionTerminal 内部 fetch）同时写入 `data` 状态，产生竞态

## What Changes
- **`SolutionTerminal.jsx`**：移除 `apiBase` 默认值；当 `externalResult` 未传入时不再发起独立 fetch；仅保留受控模式
- **`useSolverEngine.js`**：无修改（已验证正确）
- **`App.jsx`**：无修改（已验证正确）

## Impact
- Affected specs: `bind-api-streaming-terminal`（数据流修复）
- Affected code:
  - `d:\美团\src\components\SolutionTerminal.jsx`

## MODIFIED Requirements

### Requirement 1: SolutionTerminal 受控模式唯一数据源
系统 SHALL 仅通过 `externalResult` prop 接收数据，不再发起独立 API 请求。
系统 SHALL 将 `apiBase` prop 默认值从 `'http://localhost:8080'` 改为 `null`。
系统 SHALL 仅在 `apiBase` 非 null 时启用独立 fetch 模式（向后兼容）。

#### Scenario: 用户点击按钮触发调度
- **WHEN** 用户点击 `[ 启动云端全息推演 ]`
- **THEN** `useSolverEngine.initiate()` 发起 API 请求
- **AND** SolutionTerminal 通过 `externalResult` prop 接收数据
- **AND** SolutionTerminal 不发起任何独立 fetch 请求

#### Scenario: 初始状态（用户未点击按钮）
- **WHEN** 页面加载完成，用户尚未点击按钮
- **THEN** `externalResult` 为 null
- **AND** SolutionTerminal 显示空状态 `> [SYS] 正在接入云端调度引擎...`
- **AND** SolutionTerminal 不发起任何 API 请求

### Requirement 2: 端到端数据流验证
系统 SHALL 确保以下完整数据链路正常工作：
1. 用户点击按钮 → `initiate()` → `POST /api/execute_solve`
2. 预设日志注入 → 终端显示 3 条预设日志
3. API 响应 → `result` 覆盖为真实数据
4. 终端流式渲染 `logs` 数组（30ms/行）
5. 流式完成 → 800ms 延迟 → 复盘看板弹出
6. KPI 数据注入 LiveTelemetry 面板

#### Scenario: 完整调度流程
- **WHEN** 后端运行在 `localhost:8080` 且前端发起调度
- **THEN** 终端显示预设日志 → 真实日志流式刷屏 → 复盘看板弹出
- **AND** LiveTelemetry 三行指标更新
- **AND** KPI 值与后端计算一致