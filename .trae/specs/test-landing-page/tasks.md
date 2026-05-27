# Tasks

- [x] Task 1: 测试后端 API 端点
  - [x] SubTask 1.1: POST /api/execute_solve 返回 { status, solutions, kpi, logs }
  - [x] SubTask 1.2: GET /api/map_init 返回 { nodes, links }
  - [x] SubTask 1.3: GET /api/solver 返回 { selected, logs }
  - [x] SubTask 1.4: POST /api/run_optimization 返回 { score, shortage, latency, agent_logs }
  - [x] SubTask 1.5: CORS 配置允许 5173/5174/5175 端口

- [x] Task 2: 测试 useSolverEngine Hook
  - [x] SubTask 2.1: initiate() 发送 POST /api/execute_solve 请求
  - [x] SubTask 2.2: initiate() 成功时 result 被设置，status 回到 IDLE
  - [x] SubTask 2.3: initiate() 失败时 result 为 ERROR_RESULT，status 为 ERROR
  - [x] SubTask 2.4: ERROR 状态 5 秒后自动恢复 IDLE
  - [x] SubTask 2.5: FETCHING 状态下再次 initiate() 被忽略
  - [x] SubTask 2.6: reset() 将 status 设为 IDLE，result 设为 null
  - [x] SubTask 2.7: isExecuting 在 FETCHING 时为 true
  - [x] SubTask 2.8: isError 在 ERROR 时为 true
  - [x] SubTask 2.9: kpi 从 result.kpi 提取

- [x] Task 3: 测试 Landing 页面渲染
  - [x] SubTask 3.1: 视频背景渲染（hero-bg.mp4）
  - [x] SubTask 3.2: CityGrid SVG 覆盖层渲染
  - [x] SubTask 3.3: OrchestrationNav 导航栏渲染（品牌名 + 链接 + 状态点）
  - [x] SubTask 3.4: AnimatedHeading 标题动画（渐入 + 上滑）
  - [x] SubTask 3.5: FadeIn 渐入动画（延迟 + 持续时间）
  - [x] SubTask 3.6: MissionBrief 区域渲染（标题 + 描述 + 按钮 + DataUploader）
  - [x] SubTask 3.7: LiveTelemetry 卡片渲染（KPI 数据 + Sparkline + 同步时间）
  - [x] SubTask 3.8: 右侧 SolutionTerminal 面板渲染（fixed 定位）

- [x] Task 4: 测试 DataUploader 文件上传
  - [x] SubTask 4.1: 默认状态显示上传提示（虚线边框 + Upload 图标）
  - [x] SubTask 4.2: 拖拽文件时边框高亮
  - [x] SubTask 4.3: 上传有效 .txt 文件后显示成功状态
  - [x] SubTask 4.4: 上传不支持格式显示错误状态
  - [x] SubTask 4.5: 上传超大文件显示错误状态
  - [x] SubTask 4.6: 错误状态可点击重试

- [x] Task 5: 测试 SolutionTerminal 外部数据模式
  - [x] SubTask 5.1: externalResult 传入时跳过 API 请求
  - [x] SubTask 5.2: logs 逐行递增显示（每 30ms 一行）
  - [x] SubTask 5.3: solutions 在 logs 完成后显示
  - [x] SubTask 5.4: 终端自动滚动到底部
  - [x] SubTask 5.5: TerminalRow 悬停显示 Settings2 图标
  - [x] SubTask 5.6: TerminalRow 点击切换为 [MANUAL_OVERRIDE]
  - [x] SubTask 5.7: 完成后弹出结算看板（全局效用归因报告）
  - [x] SubTask 5.8: 结算看板显示 AnimatedNumber 动画
  - [x] SubTask 5.9: 结算看板显示导出按钮（JSON/CSV）
  - [x] SubTask 5.10: [重置日志] 按钮重置终端状态
  - [x] SubTask 5.11: API 错误时显示 [SYS_ERROR] 和重试按钮
  - [x] SubTask 5.12: 无数据时显示 "正在接入云端调度引擎..."

- [x] Task 6: 测试 App.jsx 完整用户流程
  - [x] SubTask 6.1: 页面加载 → datasetLoaded=true → INITIATE 按钮可用
  - [x] SubTask 6.2: 点击 INITIATE → isExecuting=true → 终端显示加载状态
  - [x] SubTask 6.3: API 返回数据 → 终端逐行显示 → 弹出结算看板
  - [x] SubTask 6.4: 点击 [结束本次推演] → handleReset → datasetLoaded=false + reset()
  - [x] SubTask 6.5: 后端未启动时前端不崩溃，显示错误信息

- [x] Task 7: 测试 atoms 组件
  - [x] SubTask 7.1: CityGrid SVG 包含同心圆、射线、网格线、黄色虚线
  - [x] SubTask 7.2: AnimatedHeading 渐入动画（300ms 延迟 + 1000ms 过渡）
  - [x] SubTask 7.3: FadeIn 支持自定义 delay 和 duration
  - [x] SubTask 7.4: StatusDot 支持 active/inactive 状态和自定义颜色
  - [x] SubTask 7.5: Sparkline SVG 渲染绿色折线图

# Task Dependencies
- Task 1 独立执行（后端测试）
- Task 2 独立执行（Hook 逻辑测试）
- Task 3, 4, 5, 7 可并行执行（前端组件测试）
- Task 6 依赖于 Task 1-5 的完成（端到端流程）
