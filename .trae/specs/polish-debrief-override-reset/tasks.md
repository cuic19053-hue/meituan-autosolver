# Tasks

- [x] Task 1: 重构 SolutionTerminal.jsx Summary 弹窗为全屏复盘看板
  - [x] 添加 `showDebrief` 状态：`isFinished` 后 800ms 延迟置为 true
  - [x] 全屏毛玻璃遮罩：`fixed inset-0 z-40 bg-black/60 backdrop-blur-md`
  - [x] 看板容器：`bg-black/80 border border-[#FFD000]/30 rounded-3xl shadow-[0_0_100px_rgba(255,208,0,0.1)]`
  - [x] 标题保持"全局效用归因报告"
  - [x] 实现 `AnimatedNumber` 子组件：easeOutCubic, 1200ms, requestAnimationFrame
  - [x] 调度完成率使用 AnimatedNumber 渲染（荧光黄 `text-[#FFD000]`）
  - [x] 锚点覆盖率使用进度条宽度过渡动画
  - [x] 算力耗时显示 latency 值
  - [x] 底部两个按钮：`[ 导出派单清单 ]` + `[ 结束本次推演 ]`
  - [x] AnimatePresence 动画曲线 `cubic-bezier(0.16, 1, 0.3, 1)`

- [x] Task 2: 升级 TerminalRow 站长接管视觉效果
  - [x] overridden 状态：`bg-orange-500/10` + `border border-orange-500/30`
  - [x] 前缀从 `[站长接管]` → `[MANUAL_OVERRIDE]`
  - [x] 文字颜色 `text-orange-300`
  - [x] 保留 flash 动画（400ms）

- [x] Task 3: 优化自动滚动为 smooth 行为
  - [x] 列表底部 `<div ref={bottomRef} />` 锚点
  - [x] `bottomRef.current?.scrollIntoView({ behavior: 'smooth' })`

- [x] Task 4: 实现全系统复位闭环
  - [x] App.jsx `handleReset` 联动 `setDatasetLoaded(false)` + `reset()`
  - [x] 复位后终端空状态、LiveTelemetry、DataUploader 全部恢复初始态

# Task Dependencies
- 所有 Task 已完成