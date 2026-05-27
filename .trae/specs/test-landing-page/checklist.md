# Checklist - Landing 页面全功能测试

## 后端 API 端点
- [x] POST /api/execute_solve 返回 { status, solutions, kpi, logs } 格式数据
- [x] POST /api/execute_solve 的 solutions 为非空数组
- [x] POST /api/execute_solve 的 kpi 包含 total_score、efficiency_gain、completion_rate、latency
- [x] GET /api/map_init 返回 { nodes, links }
- [x] GET /api/solver 返回 { selected, logs }
- [x] POST /api/run_optimization 返回 { score, shortage, latency, agent_logs }
- [x] CORS 配置允许 localhost:5173、5174、5175 端口

## useSolverEngine Hook
- [x] initiate() 发送 POST /api/execute_solve（body: { use_llm: false }）
- [x] initiate() 成功时 result 被设置，status 回到 IDLE
- [x] initiate() 失败时 result 为 ERROR_RESULT，status 为 ERROR
- [x] ERROR 状态 5 秒后自动恢复 IDLE
- [x] FETCHING 状态下再次 initiate() 被忽略
- [x] reset() 将 status 设为 IDLE，result 设为 null
- [x] isExecuting 在 FETCHING 时为 true
- [x] isError 在 ERROR 时为 true
- [x] kpi 从 result.kpi 提取（result 为 null 时 kpi 为 null）
- [x] HTTP 状态检查：r.ok 为 false 时抛出 Error

## Landing 页面渲染
- [x] 视频背景（hero-bg.mp4）渲染
- [x] CityGrid SVG 覆盖层渲染
- [x] OrchestrationNav 渲染品牌名 "AutoSolver" 和版本 "云端智能运筹中枢"
- [x] OrchestrationNav 渲染导航链接（时空拓扑、运力矩阵、效用归因）
- [x] OrchestrationNav 渲染 StatusDot（绿色 + "云网协同 · 全息推演中"）
- [x] AnimatedHeading 标题渐入动画正常
- [x] FadeIn 渐入动画支持自定义延迟
- [x] MissionBrief 渲染标题、描述、INITIATE 按钮、DataUploader
- [x] INITIATE 按钮在 datasetLoaded=true 且 executing=false 时可用
- [x] INITIATE 按钮在 executing=true 时显示 "[ 全息推演中... ]"
- [x] LiveTelemetry 渲染 KPI 数据（efficiency_gain、completion_rate、latency）
- [x] LiveTelemetry 渲染 Sparkline 和同步时间
- [x] 右侧 SolutionTerminal 面板 fixed 定位渲染

## DataUploader 文件上传
- [x] 默认状态显示上传提示（虚线边框 + Upload 图标 + 文字）
- [x] 拖拽文件时边框高亮（黄色实线边框）
- [x] 上传有效 .txt 文件后显示成功状态（绿色边框 + 文件名 + 节点数）
- [x] 上传不支持格式显示错误状态（红色边框 + 错误信息）
- [x] 上传超大文件（>5MB）显示错误状态
- [x] 错误状态可点击重试
- [x] onLoaded 回调正确触发

## SolutionTerminal 外部数据模式
- [x] externalResult 传入时跳过 API 请求
- [x] logs 逐行递增显示（每 30ms 一行）
- [x] solutions 在 logs 完成后显示
- [x] 终端自动滚动到底部（bottomRef.scrollIntoView）
- [x] TerminalRow 悬停显示 Settings2 图标
- [x] TerminalRow 点击切换为 [MANUAL_OVERRIDE]（橙色背景）
- [x] 完成后弹出结算看板（全局效用归因报告）
- [x] 结算看板显示 AnimatedNumber 动画数字
- [x] 结算看板显示锚点覆盖率进度条
- [x] 结算看板显示算力耗时
- [x] 导出按钮支持 JSON 和 CSV 格式
- [x] [重置日志] 按钮重置终端状态并调用 onReset
- [x] API 错误时显示 [SYS_ERROR] 和 [边缘异常接管] 重试按钮
- [x] 无数据时显示 "正在接入云端调度引擎..."
- [x] 状态栏显示 [STATUS: CLOUD_INFERENCE_ACTIVE] / [STATUS: ALLOTMENT_COMPLETE]
- [x] mountedRef 防止组件卸载后的 setState
- [x] intervalRef 在组件卸载时正确清理

## App.jsx 完整用户流程
- [x] 页面加载 → datasetLoaded=true → INITIATE 按钮可用
- [x] 点击 INITIATE → isExecuting=true → 终端显示加载状态
- [x] API 返回数据 → 终端逐行显示 logs + solutions → 弹出结算看板
- [x] 点击 [结束本次推演] → handleReset → datasetLoaded=false + reset()
- [x] 后端未启动时前端不崩溃，终端显示错误信息
- [x] 前后端 CORS 请求不被拦截

## atoms 组件
- [x] CityGrid SVG 包含同心圆（5个）、射线（6条）、网格线、黄色虚线（5条）
- [x] AnimatedHeading 300ms 延迟后渐入（opacity 0→1, translateY 20px→0）
- [x] FadeIn 支持自定义 delay 和 duration 参数
- [x] StatusDot active=true 时显示 ping 动画，active=false 时灰色
- [x] Sparkline 渲染绿色 SVG 折线图（12个数据点）
