# 全项目功能全面测试规格

## Why
项目经历了多次重构（TacticalMap 视觉增强、SolutionTerminal 终端重构、错误修复等），需要全面测试所有组件的功能是否正常工作，包括前后端集成。

## What Changes
- 对 App.jsx 主页面所有交互功能进行测试
- 对 SolutionTerminal 终端组件进行全面测试
- 对 TacticalMap 组件进行回归测试
- 对后端 API 端点进行集成测试
- 对前后端联调进行端到端测试

## Impact
- Affected specs: `comprehensive-tacticalmap-testing`、`fix-tacticalmap-issues`、`implement-solver-terminal`、`refactor-solution-terminal`
- Affected code: `src/App.jsx`、`src/components/SolutionTerminal.jsx`、`src/components/TacticalMap.jsx`、`backend/main.py`、`backend/solver_engine.py`

## ADDED Requirements

### Requirement: App.jsx 主页面功能测试
系统 SHALL 正确渲染主页面并响应所有用户交互。

#### Scenario: 页面初始加载
- **WHEN** 用户访问 http://localhost:5174/
- **THEN** 页面应正确渲染标题、HUD 卡片、INITIATE 按钮、Agent Terminal、Spatial Agent Nodes 卡片

#### Scenario: HUD 卡片数据展示
- **WHEN** 页面加载完成
- **THEN** 四个 HUD 卡片应显示默认值（score: --, shortage: --, latency: --, reflection: --）

#### Scenario: INITIATE 按钮点击
- **WHEN** 用户点击 INITIATE 按钮
- **THEN** isExecuting 应变为 true
- **THEN** Spatial Agent Nodes 区域应切换为 SolutionTerminal 组件

#### Scenario: Node 卡片交互
- **WHEN** 用户点击某个 Node 卡片
- **THEN** 该卡片应显示选中状态（ring-1 ring-[#404040]）
- **WHEN** 用户悬停某个 Node 卡片
- **THEN** 卡片应上移 2px 并改变边框颜色

### Requirement: SolutionTerminal 终端组件测试
系统 SHALL 正确调用后端 API 并展示优化结果。

#### Scenario: 终端初始化
- **WHEN** SolutionTerminal 组件挂载
- **THEN** 应发送 GET 请求到 /api/execute_solve
- **THEN** 状态栏应显示 [STATUS: COMPUTING_OPTIMAL_PATH]

#### Scenario: 数据流式渲染
- **WHEN** API 返回 solutions 数据
- **THEN** 应以每 20ms 递增的方式逐行显示方案
- **THEN** 每行格式应为 > [ALLOCATED] ("Txxxx", ["Cxxxx"])
- **THEN** 终端应自动滚动到底部

#### Scenario: TerminalRow 交互
- **WHEN** 用户悬停某一行
- **THEN** 应显示 Settings2 图标
- **WHEN** 用户点击某一行
- **THEN** 该行应切换为 [MANUAL_OVERRIDE] 状态，背景变为橙色

#### Scenario: 结算看板
- **WHEN** 所有方案显示完毕（isFinished=true）
- **THEN** 应弹出结算看板，显示统计数据
- **THEN** 应有 [ACKNOWLEDGE] 按钮关闭看板

#### Scenario: RESET 按钮
- **WHEN** 用户点击 [RESET] 按钮
- **THEN** 应调用 onReset 回调
- **THEN** 主页面应恢复为卡片视图

#### Scenario: API 错误处理
- **WHEN** /api/execute_solve 请求失败
- **THEN** 应显示错误信息 [ERROR] No solution data received from solver engine

### Requirement: TacticalMap 组件回归测试
系统 SHALL 正确渲染战术地图并响应交互。

#### Scenario: 地图初始化
- **WHEN** TacticalMap 组件挂载
- **THEN** 应发送 GET 请求到 /api/map_init
- **THEN** 应正确渲染节点和链路

#### Scenario: Solver 执行
- **WHEN** 用户点击 EXECUTE SOLVER 按钮
- **THEN** 应发送 GET 请求到 /api/solver
- **THEN** 应高亮显示选中链路

#### Scenario: 链路聚焦
- **WHEN** 用户点击 Courier 节点
- **THEN** 该 Courier 的链路应以蓝色高亮

#### Scenario: 重置功能
- **WHEN** 用户点击 RESET 按钮
- **THEN** 应重置所有状态（solved, selectedLinks, solverLogs, focusedCourier, loading）

### Requirement: 后端 API 端点测试
系统 SHALL 正确响应所有 API 请求。

#### Scenario: GET /api/execute_solve
- **WHEN** 发送 GET 请求到 /api/execute_solve
- **THEN** 应返回包含 solutions、stats、logs 的 JSON 数据
- **THEN** solutions 应为非空数组
- **THEN** stats 应包含 total_score、matched_couriers、match_rate

#### Scenario: GET /api/map_init
- **WHEN** 发送 GET 请求到 /api/map_init
- **THEN** 应返回包含 nodes 和 links 的 JSON 数据

#### Scenario: GET /api/solver
- **WHEN** 发送 GET 请求到 /api/solver
- **THEN** 应返回包含 selected 和 logs 的 JSON 数据

#### Scenario: POST /api/run_optimization
- **WHEN** 发送 POST 请求到 /api/run_optimization
- **THEN** 应返回包含 score、shortage、latency、agent_logs 的 JSON 数据

### Requirement: 前后端联调端到端测试
系统 SHALL 在前后端联调时正常工作。

#### Scenario: 完整用户流程
- **WHEN** 用户访问页面 → 点击 INITIATE → 查看终端输出 → 点击 RESET
- **THEN** 所有步骤应顺利完成，无错误

#### Scenario: CORS 配置
- **WHEN** 前端从 localhost:5173 或 localhost:5174 发起请求
- **THEN** 后端应正确响应，不拒绝跨域请求

## MODIFIED Requirements
（无）

## REMOVED Requirements
（无）
