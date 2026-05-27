# Checklist

- [x] SolutionTerminal.jsx: 复盘看板在 `isFinished` 后 800ms 弹出
- [x] SolutionTerminal.jsx: 全屏毛玻璃遮罩 + 看板容器使用指定样式
- [x] SolutionTerminal.jsx: AnimatedNumber 子组件实现数字滚动动画（0→目标值，1200ms）
- [x] SolutionTerminal.jsx: 调度完成率使用 AnimatedNumber 荧光黄大字
- [x] SolutionTerminal.jsx: 锚点覆盖率使用进度条宽度过渡动画
- [x] SolutionTerminal.jsx: 算力耗时正确显示 latency
- [x] SolutionTerminal.jsx: [ 导出派单清单 ] 按钮 console.log solutions
- [x] SolutionTerminal.jsx: [ 结束本次推演 ] 调用 onReset
- [x] SolutionTerminal.jsx: 所有过渡动画使用 cubic-bezier(0.16, 1, 0.3, 1)
- [x] SolutionTerminal.jsx: TerminalRow overridden 状态背景为 bg-orange-500/10 + 橙色边框
- [x] SolutionTerminal.jsx: TerminalRow overridden 前缀为 [MANUAL_OVERRIDE]
- [x] SolutionTerminal.jsx: 自动滚动使用 scrollIntoView({ behavior: 'smooth' })
- [x] useSolverEngine.js: reset 函数支持系统复位
- [x] App.jsx: handleReset 联动 setDatasetLoaded(false)
- [x] 复位后界面回到"待接驳"初始状态
- [x] 所有 Tailwind CSS 类名保持兼容
- [x] API 调用逻辑未被修改
- [x] framer-motion 动效全部保留