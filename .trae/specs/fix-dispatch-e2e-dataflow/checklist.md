# Checklist

- [x] SolutionTerminal.jsx: `apiBase` 默认值为 `null`（非 `'http://localhost:8080'`）
- [x] SolutionTerminal.jsx: `externalResult` 为 null 且 `apiBase` 为 null 时不发起 fetch
- [x] SolutionTerminal.jsx: 初始状态显示 `> [SYS] 正在接入云端调度引擎...`
- [x] SolutionTerminal.jsx: 点击按钮后通过 externalResult 接收数据正常流式渲染
- [x] SolutionTerminal.jsx: 复盘看板在流式完成后 800ms 弹出
- [x] SolutionTerminal.jsx: LiveTelemetry KPI 数据正确更新
- [x] 后端 API `POST /api/execute_solve` 返回 status=success
- [x] 后端 API 返回 solutions 数组长度 >= 10
- [x] 后端 API 返回 logs 数组长度 >= 100
- [x] 端到端数据链路完整无断裂