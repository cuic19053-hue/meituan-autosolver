# Checklist - 修复后全功能回归测试

## 后端 API 修复验证
- [x] POST /api/execute_solve 返回 kpi.total_score（数值类型：800761.48）
- [x] CORS 允许 localhost:5175 端口（OPTIONS 返回 200）
- [x] GET /api/map_init 返回 200 + { nodes, links }
- [x] GET /api/solver 返回 200 + { selected, logs }
- [x] POST /api/run_optimization — 后端未注册此路由（404），前端未调用，不影响功能

## useSolverEngine 修复验证
- [x] AbortController：abortRef.current 在 initiate 中创建并赋值
- [x] timerRef：setTimeout 引用保存到 timerRef.current
- [x] initiate(payload)：函数签名接受可选 payload 参数
- [x] fetch signal：请求配置包含 signal: controller.signal
- [x] abort 检查：.then 回调中检查 controller.signal.aborted
- [x] AbortError 忽略：.catch 中 err.name === 'AbortError' 时 return
- [x] reset 清理：reset() 中调用 abortRef.current.abort() + clearTimeout(timerRef.current)
- [x] ERROR_RESULT：包含 error: true 字段

## App.jsx 数据链路修复验证
- [x] uploadedData state 存在（useState(null)）
- [x] handleInitiate 调用 initiate(uploadedData)
- [x] handleDatasetLoaded 调用 setDatasetLoaded(true) + setUploadedData(data)
- [x] handleReset 调用 setDatasetLoaded(true) + setUploadedData(null) + reset()
- [x] MissionBrief 接收 onInitiate={handleInitiate}
- [x] MissionBrief 接收 onDatasetLoaded={handleDatasetLoaded}
- [x] OrchestrationNav 接收 isError={isError}

## SolutionTerminal 修复验证
- [x] apiBase prop 已从函数签名中移除
- [x] AnimatedNumber useEffect return 中调用 cancelAnimationFrame(rafRef.current)
- [x] setDisplayCount updater 中无 setIsFinished 或 clearInterval 调用
- [x] 独立 useEffect 监听 displayCount >= totalRows 时 setIsFinished(true)
- [x] handleRetry 调用 clearInterval + setData(null) + setDisplayCount(0) + setIsFinished(false) + onReset()
- [x] escapeCSV 函数处理含逗号/引号/换行的字段
- [x] URL.revokeObjectURL 在 setTimeout 中延迟执行
- [x] useEffect 依赖数组为 [externalResult]（不含 apiBase）

## DataUploader 修复验证
- [x] loaded 状态下渲染 [重新上传] 按钮
- [x] [重新上传] onClick 调用 setLoaded(false) + setFilename('') + setNodeCount(0)
- [x] 错误状态 onClick 调用 setError(null) + setLoaded(false) + setTimeout(() => fileInputRef.current?.click(), 100)

## 其他组件修复验证
- [x] LiveTelemetry kpi 为 null 时显示 "--" 占位符（非假数据）
- [x] LiveTelemetry 标签为"效用增益"/"调度完成率"/"运算耗时"
- [x] OrchestrationNav isError=true 时 StatusDot 颜色为 "#FF4444"
- [x] OrchestrationNav isError=true 时文案为 "引擎离线 · 等待重连"
- [x] OrchestrationNav 导航链接 href="javascript:void(0)"
- [x] CityGrid 水平线 y2={i * 50}（非 y2="600"）
- [x] TacticalMap 去重 key 使用 .sort((a, b) => a - b)
- [x] ReflectionConsole useEffect 中 logs 增量追加（不调用 setDisplayedLogs([])）

## 构建验证
- [x] vite build 成功（exit code 0，2152 modules transformed）
- [x] 浏览器预览无 JS 运行时错误
