# Tasks

- [x] Task 1: 重构 `src/components/SolutionTerminal.jsx`
  - [x] SubTask 1.1: 导入依赖（useState, useEffect, useRef, motion, AnimatePresence, lucide-react 图标）
  - [x] SubTask 1.2: 实现流式渲染（displayCount 状态 + setInterval 每 20ms 递增）
  - [x] SubTask 1.3: 实现 TerminalRow 子组件（isOverridden 状态、Settings2 悬停/点击交互）
  - [x] SubTask 1.4: 实现结算看板（isFinished 触发、AnimatePresence 动画、[ACKNOWLEDGE] 按钮）
  - [x] SubTask 1.5: 视觉规范（overflow-hidden/auto、font-mono、bg-black/30）

- [x] Task 2: 修改 `src/App.jsx` 恢复 SolutionTerminal 独占显示
  - [x] SubTask 2.1: 移除 TacticalMap + ReflectionConsole 布局
  - [x] SubTask 2.2: 恢复 SolutionTerminal 独占卡片区域显示
  - [x] SubTask 2.3: 清理 solverData 相关状态和逻辑

- [x] Task 3: 验证与调试
  - [x] SubTask 3.1: Vite 编译无错误
  - [x] SubTask 3.2: 流式渲染正常工作（逐行递增显示）
  - [x] SubTask 3.3: TerminalRow 悬停/点击交互正常
  - [x] SubTask 3.4: 结算看板正常弹出和关闭

# Task Dependencies
- Task 1 independent
- Task 2 independent (Task 1 can proceed in parallel)
- Task 3 depends on Task 1 and Task 2
