# SolutionTerminal 工业级重构 Spec

## Why
当前 SolutionTerminal 采用一次性渲染全部日志的方式，性能低下且缺乏交互性。需要引入流式渲染提升感知性能，增加人工干预机制让用户能覆盖 AI 分配决策，并加入结算看板呈现最终优化效果指标。

## What Changes
- 重构 `src/components/SolutionTerminal.jsx`：流式渲染（displayCount 增量）+ TerminalRow 子组件 + 结算看板
- 修改 `src/App.jsx`：恢复 SolutionTerminal 在卡片区域的独占显示（替代 TacticalMap + ReflectionConsole）

## Impact
- Affected specs: 前端组件接口（SolutionTerminal props 保持不变：apiBase, onReset）
- Affected code: `src/components/SolutionTerminal.jsx`、`src/App.jsx`

## ADDED Requirements

### Requirement: 性能优化与流式渲染
系统 SHALL 在 SolutionTerminal 中实现流式渲染：
- 状态：`const [displayCount, setDisplayCount] = useState(0);` 和 `const [isFinished, setIsFinished] = useState(false);`
- `useEffect` 使用 `setInterval` 每隔 20ms 让 `displayCount` 加 1
- 当 `displayCount >= solutions.length` 时清除定时器，设置 `setIsFinished(true)`
- 列表区域 div 有 ref，随 `displayCount` 增加自动 `scrollTop` 到底部

### Requirement: TerminalRow 子组件
系统 SHALL 在同一文件内抽离 `<TerminalRow />` 子组件：

**内部状态**：`const [isOverridden, setIsOverridden] = useState(false);`

**UI 表现**：
- 默认状态：文字为 AI 蓝/绿色，前缀为 `[OPTIMIZED]`
- 鼠标悬停：行尾出现 `Settings2` 图标（透明度从 0 变 100）
- 点击触发：点击图标后 `isOverridden = true`，整行文字变为警告橙 `#ff6b35`，前缀变为 `[MANUAL_OVERRIDE]`，并伴随一次轻微的背景闪烁动画

### Requirement: 结算看板 (Summary Overlay)
系统 SHALL 在 SolutionTerminal 最外层（relative 容器）内部添加绝对定位的 `<AnimatePresence>`：

**触发条件**：`isFinished === true` 时在正中心弹出

**卡片样式**：
```
absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
z-50 bg-black/80 backdrop-blur-xl
border-2 border-[#00d4ff]/50 rounded-lg p-6
shadow-[0_0_30px_rgba(0,212,255,0.2)]
```

**卡片内容**：
- 顶部 Header：`<CheckCircle2 /> OPERATION_COMPLETE`
- 数据列：EFFICIENCY_GAIN / COMPLETION_RATE / LATENCY
- 底部 `[ACKNOWLEDGE]` 按钮，点击后隐藏面板（`setShowSummary(false)`）

### Requirement: 视觉规范
- 外层容器：`overflow-hidden`
- 内层列表容器：`overflow-auto`，隐藏原生滚动条
- 字体：`font-mono`
- 背景：`bg-black/30` 隐约透出底层视频

## MODIFIED Requirements
- App.jsx 恢复 SolutionTerminal 独占显示（替代 TacticalMap + ReflectionConsole）

## REMOVED Requirements
- TacticalMap + ReflectionConsole 的卡片区域并列布局（改由 SolutionTerminal 替代）
