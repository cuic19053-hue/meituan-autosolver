# Tasks

- [x] Task 1: 验证后端 API 修复
  - [x] SubTask 1.1: POST /api/execute_solve 返回 kpi.total_score（800761.48，数值类型）
  - [x] SubTask 1.2: CORS 允许 localhost:5175 端口（OPTIONS 返回 200）
  - [x] SubTask 1.3: GET /api/map_init 返回 200 + { nodes, links }
  - [x] SubTask 1.4: GET /api/solver 返回 200 + { selected, logs }
  - [x] SubTask 1.5: POST /api/run_optimization — 后端未注册此路由（404），但前端未调用此端点，不影响功能

- [x] Task 2: 验证 useSolverEngine 修复（8/8 PASS）
  - [x] SubTask 2.1: AbortController 存在：abortRef.current 被使用
  - [x] SubTask 2.2: timerRef 存在：setTimeout 引用被保存
  - [x] SubTask 2.3: initiate(payload) 接受可选参数
  - [x] SubTask 2.4: fetch signal 绑定 controller.signal
  - [x] SubTask 2.5: .then 中检查 controller.signal.aborted
  - [x] SubTask 2.6: .catch 中忽略 AbortError
  - [x] SubTask 2.7: reset() 中 abort + clearTimeout
  - [x] SubTask 2.8: ERROR_RESULT 包含 error: true 字段

- [x] Task 3: 验证 App.jsx 数据链路修复（6/6 PASS）
  - [x] SubTask 3.1: uploadedData state 存在
  - [x] SubTask 3.2: handleInitiate 调用 initiate(uploadedData)
  - [x] SubTask 3.3: handleDatasetLoaded 保存上传数据到 setUploadedData
  - [x] SubTask 3.4: handleReset 清除 uploadedData
  - [x] SubTask 3.5: MissionBrief 接收 onInitiate={handleInitiate} 和 onDatasetLoaded={handleDatasetLoaded}
  - [x] SubTask 3.6: OrchestrationNav 接收 isError={isError}

- [x] Task 4: 验证 SolutionTerminal 修复（8/8 PASS）
  - [x] SubTask 4.1: apiBase prop 已移除
  - [x] SubTask 4.2: AnimatedNumber rAF 在 cleanup 中 cancelAnimationFrame
  - [x] SubTask 4.3: setInterval 内 setDisplayCount updater 中无 setIsFinished/clearInterval
  - [x] SubTask 4.4: 独立 useEffect 监听 displayCount 达到上限时 setIsFinished(true)
  - [x] SubTask 4.5: handleRetry 重置所有状态 + 调用 onReset()
  - [x] SubTask 4.6: escapeCSV 函数存在且处理逗号/引号/换行
  - [x] SubTask 4.7: URL.revokeObjectURL 延迟执行（setTimeout）
  - [x] SubTask 4.8: useEffect 依赖数组为 [externalResult]（不含 apiBase）

- [x] Task 5: 验证 DataUploader 修复（3/3 PASS）
  - [x] SubTask 5.1: loaded 状态下存在 [重新上传] 按钮
  - [x] SubTask 5.2: [重新上传] 点击后 setLoaded(false) + setFilename('') + setNodeCount(0)
  - [x] SubTask 5.3: 错误状态点击后触发文件选择器（setTimeout + fileInputRef.current?.click()）

- [x] Task 6: 验证其他组件修复（8/8 PASS）
  - [x] SubTask 6.1: LiveTelemetry kpi 为 null 时显示 "--" 而非假数据
  - [x] SubTask 6.2: LiveTelemetry UI 标签与数据语义对齐（效用增益/调度完成率/运算耗时）
  - [x] SubTask 6.3: OrchestrationNav isError=true 时 StatusDot 红色 + "引擎离线 · 等待重连"
  - [x] SubTask 6.4: OrchestrationNav 导航链接 href="javascript:void(0)"
  - [x] SubTask 6.5: CityGrid 水平线 y2={i * 50}
  - [x] SubTask 6.6: TacticalMap 去重 key 使用 .sort((a, b) => a - b)
  - [x] SubTask 6.7: ReflectionConsole logs 增量追加（不重置 displayedLogs）

- [x] Task 7: 构建验证
  - [x] SubTask 7.1: vite build 成功无错误（exit code 0）
  - [x] SubTask 7.2: 浏览器预览无 JS 错误

# Task Dependencies
- Task 1 独立执行（后端测试）
- Task 2-6 可并行执行（前端代码审查）
- Task 7 依赖于 Task 1-6 的完成
