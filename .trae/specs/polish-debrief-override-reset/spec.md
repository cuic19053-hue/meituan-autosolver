# 全链路闭环：复盘看板重构与终端交互深度优化 Spec

## Why
算法推演完成后缺少震撼的"视觉收尾"，终端人工干预交互不够精致，自动滚动丝滑度不足，系统缺少完整的状态复位能力。需要在现有基础上进行最后点睛，确保演示时前后端全链路闭环体验流畅。

## What Changes
- **SolutionTerminal.jsx**：Summary 弹窗升级为全屏毛玻璃复盘看板（含数字滚动动画 + 进度条）；TerminalRow [站长接管] 状态视觉升级（橙色背景 + 边框）；自动滚动改为 smooth 行为
- **useSolverEngine.js**：reset 函数增强为清空 dataset 状态
- **App.jsx**：handleReset 联动 datasetLoaded 状态复位
- 纯 UI 增强 + 微交互逻辑，不改动数据流架构

## Impact
- Affected specs: `bind-api-streaming-terminal`（流式渲染 + Summary 后续增强）
- Affected code:
  - `d:\美团\src\components\SolutionTerminal.jsx`
  - `d:\美团\src\hooks\useSolverEngine.js`
  - `d:\美团\src\App.jsx`

## MODIFIED Requirements

### Requirement 1: 调度效果评估报告视觉升级 (Utility Debrief Report)
系统 SHALL 在流式渲染完成（`isFinished === true`）后延迟 800ms 弹出复盘看板。

看板视觉规格：
- 全屏毛玻璃遮罩 `backdrop-blur-md` + `bg-black/60` 锁定背景
- 看板容器：`bg-black/60 border border-[#FFD000]/30 rounded-3xl shadow-[0_0_100px_rgba(255,208,0,0.1)]`
- 标题："全局效用归因报告"（保留现有文案）
- 三个核心指标使用 Animated Numbers（数字从 0 滚动到目标值）：
  - 调度完成率：荧光黄大字 `text-[#FFD000]`，easing: `cubic-bezier(0.16, 1, 0.3, 1)`
  - 锚点覆盖率：带进度条 `<div>` 宽度百分比过渡动画
  - 算力耗时：显示 latency 值
- 底部两个按钮：
  - `[ 导出派单清单 ]`（预留，控制台打印 solutions JSON）
  - `[ 结束本次推演 ]`（调用 onReset，触发全系统复位）

#### Scenario: 复盘看板弹出
- **WHEN** `displayCount >= logs.length` 且 800ms 延迟到达
- **THEN** 全屏毛玻璃遮罩 + 复盘看板以 AnimatePresence 弹出
- **AND** 三个指标从 0 动画过渡到真实值
- **AND** Easing 使用 `cubic-bezier(0.16, 1, 0.3, 1)`

### Requirement 2: 站长接管视觉升级 (Manual Override Polish)
系统 SHALL 在点击 TerminalRow 行末的 `[ 站长接管 ]` 后：
- 该行背景变为 `bg-orange-500/10`，边框变为 `border border-orange-500/30`
- 前缀从 `[AI 派单]` 切换为 `[MANUAL_OVERRIDE]`
- 保留现有的 flash 动画（400ms 闪烁效果）

#### Scenario: 终端行人工干预
- **WHEN** 用户 hover TerminalRow 并点击行末齿轮图标
- **THEN** 该行进入 overridden 状态
- **AND** 背景变为橙色半透明 + 橙色边框
- **AND** 前缀变为 `[MANUAL_OVERRIDE]`

### Requirement 3: 终端自动滚动优化 (Smooth Auto-Scroll)
系统 SHALL 在每次 displayCount 变化时触发 `scrollIntoView({ behavior: 'smooth' })` 滚动到底部。
系统 SHALL 使用 `useRef` 锚定列表底部的一个空 div 作为滚动目标。

#### Scenario: 流式刷屏自动滚动
- **WHEN** 终端以 30ms/行 速度新增日志行
- **THEN** 容器平滑滚动至最新行
- **AND** 滚动行为使用 `behavior: 'smooth'`

### Requirement 4: 系统复位闭环 (System Reset)
系统 SHALL 提供 `resetSystem()` 函数：
- 清除所有 `logs`、`solutions`、`result` 状态
- 重置 `datasetLoaded` 为 false
- 重置终端 `displayCount` 为 0
- 关闭 Summary 弹窗
- 界面回到"待接驳"初始状态

#### Scenario: 点击 [ 结束本次推演 ]
- **WHEN** 用户在复盘看板点击 `[ 结束本次推演 ]`
- **THEN** 全系统状态复位
- **AND** 终端清空，数据集上传器恢复待上传状态
- **AND** LiveTelemetry 面板恢复默认值

### Requirement 5: 约束保证
系统 MUST NOT 修改任何 Tailwind CSS 类名（仅在现有模式上添加新类）。
系统 MUST NOT 修改 API 调用逻辑或数据流路径。
系统 MUST 保留所有现有 framer-motion 动效。