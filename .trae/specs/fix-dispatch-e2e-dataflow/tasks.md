# Tasks

- [x] Task 1: 修复 SolutionTerminal.jsx 双重数据源冲突
  - [x] 将 `apiBase` 默认值从 `'http://localhost:8080'` 改为 `null`
  - [x] 在 useEffect 中，当 `externalResult` 为 null 且 `apiBase` 为 null 时，不发起任何 fetch
  - [x] 仅在 `apiBase` 非 null 时启用独立 fetch 模式
  - [x] 当 `externalResult` 为 null 且无数据时，显示空状态 `> [SYS] 正在接入云端调度引擎...`
  - [x] 保留所有其他逻辑不变（流式渲染、复盘看板、TerminalRow、autoscroll）

- [x] Task 2: 端到端验证
  - [x] 启动后端 `uvicorn backend.main:app --port 8080`
  - [x] 确认 `POST /api/execute_solve` 返回正确数据
  - [x] 确认前端初始状态不发起 API 请求
  - [x] 确认点击按钮后完整数据链路正常

# Task Dependencies
- 所有 Task 已完成