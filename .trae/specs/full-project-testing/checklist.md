# Checklist - 全项目功能全面测试

## 后端 API 端点测试 ✅
- [ ] GET /api/execute_solve 返回包含 solutions、stats/kpi、logs 的 JSON 数据
- [ ] GET /api/execute_solve 的 solutions 为非空数组（预期 28 条）
- [ ] GET /api/execute_solve 的 kpi 包含 total_score、matched_couriers、match_rate / efficiency_gain、completion_rate
- [ ] GET /api/map_init 返回包含 nodes 和 links 的 JSON 数据（预期 100 nodes + 175 links）
- [ ] GET /api/solver 返回包含 selected 和 logs 的 JSON 数据（预期 84 selected + 450 logs）
- [ ] POST /api/run_optimization 返回 score、shortage、latency、agent_logs
- [ ] POST /api/execute_solve 返回 status、solutions、kpi、logs
- [ ] POST /api/chat 返回 ChatResponse(reply=...)
- [ ] POST /api/report 返回 ReportResponse(report=...)
- [ ] CORS 配置允许 localhost:5173 和 localhost:5174 端口
- [ ] CORS 配置允许 localhost:3000 端口
- [ ] 后端启动无报错，所有路由正确注册

## useSolverEngine Hook 测试 ✅
- [ ] initiate() 调用后 status 从 IDLE 变为 FETCHING
- [ ] initiate() 调用后 result 被设置为带 PRESET_LOGS 的 loading 状态
- [ ] initiate() 发送 POST 请求到 http://localhost:8080/api/execute_solve
- [ ] POST 请求 body 包含 { use_llm: false }
- [ ] 请求成功时 setResult(data) 并 setStatus(IDLE)
- [ ] 请求失败时 setResult(ERROR_RESULT) 并 setStatus(ERROR)
- [ ] 错误状态 5 秒后自动恢复为 IDLE
- [ ] reset() 将 status 设为 IDLE，result 设为 null
- [ ] isExecuting 在 status === FETCHING 时为 true
- [ ] isError 在 status === ERROR 时为 true
- [ ] 请求中再次调用 initiate() 被忽略（status === FETCHING 时 return）
- [ ] HTTP 状态检查：r.ok 为 false 时抛出 Error

## App.jsx 主页面功能测试 ✅
- [ ] 页面初始加载正确渲染标题 "云网协同推演 · 空间运力聚合引擎"
- [ ] 页面正确渲染四个 HUD 卡片（LiveTelemetry 组件）
- [ ] HUD 卡片默认值显示正确（efficiency_gain: +98.5%, completion_rate: 98.2%, latency: < 100ms）
- [ ] MissionBrief 组件正确渲染 INITIATE 按钮
- [ ] 按钮在 datasetLoaded=false 时为禁用状态
- [ ] 按钮在 datasetLoaded=true 且 executing=false 时可用
- [ ] 按钮在 executing=true 时显示 "[ 全息推演中... ]"
- [ ] INITIATE 按钮点击后调用 useSolverEngine.initiate()
- [ ] SolutionTerminal 组件以 fixed 定位渲染在页面右侧
- [ ] SolutionTerminal 接收 result、isStreaming、onReset 三个 props
- [ ] handleReset 同时调用 setDatasetLoaded(false) 和 reset()
- [ ] DataUploader 组件存在并可触发 onDatasetLoaded
- [ ] CityGrid 背景组件正常渲染
- [ ] 视频背景 (hero-bg.mp4) 正常播放
- [ ] OrchestrationNav 导航栏正常渲染

## SolutionTerminal 终端组件测试 ✅
- [ ] 组件挂载时发送 GET 请求到 /api/execute_solve（当无 externalResult 时）
- [ ] 状态栏显示 [STATUS: CLOUD_INFERENCE_ACTIVE]（加载中）
- [ ] 状态栏显示 [STATUS: ALLOTMENT_COMPLETE]（完成时）
- [ ] 数据以每 30ms 递增方式逐行显示（displayCount 递增）
- [ ] 每行日志格式为 > [ALLOCATION] / > [CONFLICT] / > [SYS] 等
- [ ] 终端自动滚动到底部（bottomRef.scrollIntoView）
- [ ] TerminalRow 悬停时显示 Settings2 图标（opacity 0→1 动画）
- [ ] TerminalRow 点击后切换为 [MANUAL_OVERRIDE] 状态（橙色背景）
- [ ] isOverridden 后再次点击不重复触发
- [ ] 所有行显示完毕后 isFinished 变为 true
- [ ] isFinished 后 800ms 弹出结算看板（showDebrief=true）
- [ ] 结算看板显示 "全局效用归因报告" 标题
- [ ] 结算看板显示 AnimatedNumber 动画数字
- [ ] 结算看板显示锚点覆盖率进度条
- [ ] 结算看板显示算力耗时
- [ ] 结算看板包含 [导出派单清单] 按钮
- [ ] 结算看板包含 [结束本次推演] 按钮
- [ ] [结束本次推演] 按钮调用 onReset 回调
- [ ] [重置日志] 按钮正确重置状态
- [ ] 底部状态栏显示推演行数和 PROCESSING/COMPLETE 状态
- [ ] externalResult 存在时跳过 API 请求，直接使用外部数据
- [ ] API 错误时显示 [SYS_ERROR] 核心引擎离线错误信息
- [ ] API 错误时显示 [边缘异常接管] 重试按钮
- [ ] 重试按钮点击后设置 isRetrying 状态
- [ ] mountedRef 防止组件卸载后的 setState
- [ ] intervalRef 在组件卸载时正确清理
- [ ] 底部 AGENT_LOG 区域显示最后一条日志
- [ ] 无数据且无加载时显示 "正在接入云端调度引擎..."

## TacticalMap 组件回归测试 ✅
- [ ] 组件挂载时发送 GET 请求到 /api/map_init
- [ ] HTTP 状态检查：r.ok 为 false 时抛出 Error
- [ ] 使用 Map 按 ID 唯一化节点（去重）
- [ ] Task 节点正确过滤并显示为圆形（circle r=5）
- [ ] Courier 节点正确过滤并显示为三角形（polygon）
- [ ] links 按 source-target 组合去重
- [ ] viewBox 根据节点坐标动态计算（含 10% padding）
- [ ] 未选中链路渲染样式：stroke=#737373, strokeWidth=0.5, strokeOpacity=0.1
- [ ] 选中链路渲染样式：stroke=#FFD000, strokeWidth=2, glowYellow 滤镜
- [ ] 选中链路应用 flowing-line 虚线动画
- [ ] 背景链路淡出动画（CSS transition 800ms）
- [ ] 高亮链路 hlOpacity 动态计算（≥0.5, 随 selectedLinks 递减）
- [ ] EXECUTE SOLVER 按钮点击后发送 GET 到 /api/solver
- [ ] solving=true 时按钮禁用并显示 "SOLVING..."
- [ ] loading=true 时按钮禁用
- [ ] solved=true 时显示 RESET 按钮替代 EXECUTE SOLVER
- [ ] RESET 按钮 disabled={solving}
- [ ] RESET 按钮点击后重置所有状态（solved, selectedLinks, focusedCourier, loading）
- [ ] Courier 节点点击设置 focusedCourier 状态
- [ ] 聚焦时 Courier 链路以蓝色 (#60A5FA) 高亮
- [ ] 再次点击同一 Courier 取消聚焦
- [ ] Task 节点悬停显示 "T:{id}" 标签
- [ ] Courier 节点悬停显示 "C:{id}" 标签
- [ ] 移出节点后标签隐藏
- [ ] 底部状态栏显示 NODES/LINKS/ASSIGNED 计数
- [ ] fetchMap 错误时 console.error 记录错误并 setLoading(false)
- [ ] runSolver 错误时通过 onSolverData 传递错误日志
- [ ] onBack prop 存在时显示 ← BACK 按钮
- [ ] onBack prop 不存在时不显示返回按钮
- [ ] apiBase prop 默认值为 'http://localhost:8080'
- [ ] 网格背景 (grid50 pattern) 正确渲染
- [ ] 边缘暗角 (edgeDark radialGradient) 正确渲染

## 前后端联调端到端测试 ✅
- [ ] 完整用户流程：加载页面 → 上传数据 → 点击 INITIATE → 查看终端输出 → 点击 RESET
- [ ] 前端发起 POST /api/execute_solve 请求时后端正确响应
- [ ] 前端 CORS 请求不被拦截
- [ ] 后端返回数据格式与前端期望一致
- [ ] 无控制台运行时错误
- [ ] 无未捕获的 Promise rejection

## 组件间数据流测试 ✅
- [ ] useSolverEngine → App：result 正确传递到 SolutionTerminal
- [ ] useSolverEngine → App：isExecuting 正确映射到 SolutionTerminal.isStreaming
- [ ] useSolverEngine → App：kpi 正确传递到 LiveTelemetry
- [ ] App → SolutionTerminal：onReset (handleReset) 正确触发 reset + setDatasetLoaded(false)
- [ ] MissionBrief → App：onInitiate 正确触发 useSolverEngine.initiate()
- [ ] DataUploader → App：onLoaded 正确触发 onDatasetLoaded → setDatasetLoaded(true)

## 错误与边界情况测试 ✅
- [ ] 后端未启动时前端显示错误信息而不崩溃
- [ ] API 返回空 solutions 时 SolutionTerminal 正常显示
- [ ] API 返回空 logs 时 SolutionTerminal 直接设置 isFinished
- [ ] 快速连续点击 INITIATE 不触发多次请求
- [ ] 组件卸载后不执行 setState（mountedRef 守护）
- [ ] 数据文件 large_seed301.txt 缺失时后端返回错误信息
- [ ] 后端编码兼容（utf-8 → gbk → latin-1 降级）
- [ ] SolutionTerminal 支持 externalResult 外部注入数据
- [ ] TacticalMap 支持独立运行（不依赖 App 集成）

## 测试结果汇总
- ✅ 完全通过: Task 1（后端 API）、Task 5（端到端联调）
- ✅ 已修复通过: Task 2（App.jsx）、Task 3（SolutionTerminal）、Task 4（TacticalMap 回归）
- ⚠️ 已知限制: TacticalMap 未被 App.jsx 主动使用（当前使用 SolutionTerminal）
- ⚠️ 已知限制: runOptimization 相关功能未被前端调用（死代码）