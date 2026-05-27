# Checklist

- [x] useSolverEngine.js: `initiate()` 进入 FETCHING 时立即注入预设日志 result
- [x] useSolverEngine.js: 预设日志包含 3 条加密链路建立文本
- [x] useSolverEngine.js: API 成功后 result 被真实数据覆盖
- [x] useSolverEngine.js: API 失败后 result 包含 `> [SYS_ERROR]` 日志
- [x] useSolverEngine.js: 5 秒后 ERROR 状态自动恢复 IDLE
- [x] SolutionTerminal.jsx: 流式渲染 logs 数组，30ms/行间隔
- [x] SolutionTerminal.jsx: 自动滚动跟随最新行 (scrollTop = scrollHeight)
- [x] SolutionTerminal.jsx: 加载中文本为 `> [SYS] 正在建立加密云端链路...`
- [x] SolutionTerminal.jsx: 错误文本为 `> [SYS_ERROR] 核心引擎离线，请检查云端算力节点。`
- [x] SolutionTerminal.jsx: KPI 字段不再引用已废弃的 `total_score`、`match_rate`
- [x] SolutionTerminal.jsx: Summary 弹窗 efficiencyGain / completionRate 正确读取 kpi
- [x] LiveTelemetry.jsx: 第一行不再引用 `kpi?.total_score`
- [x] LiveTelemetry.jsx: 三行指标正确显示 efficiency_gain / completion_rate / latency
- [x] MissionBrief.jsx: 按钮 onClick 逻辑未修改
- [x] 所有 Tailwind CSS 类名未修改
- [x] 所有 framer-motion 动效未受影响
- [x] `useSolverEngine` 导出的 `initiate` / `reset` / `isExecuting` / `kpi` 接口不变
- [x] 应用可正常编译运行