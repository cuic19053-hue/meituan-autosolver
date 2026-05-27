# Tasks

- [x] Task 1: 创建 `backend/solver_engine.py` 贪心求解器
  - [x] SubTask 1.1: 实现 `parse_seed_file()` 解析 large_seed301.txt
  - [x] SubTask 1.2: 实现 `greedy_solve()` 贪心分配算法（composite_score = score*0.7 + willingness*0.3，降序选取）
  - [x] SubTask 1.3: 实现冲突处理（每个 Task 和 Courier 只出现一次）
  - [x] SubTask 1.4: 实现带时间戳的日志生成（[HH:MM:SS.ss] 格式）
  - [x] SubTask 1.5: 实现 `execute_solve()` 主函数，返回 solutions/total_score/match_rate/avg_willingness/logs

- [x] Task 2: 修改 `backend/main.py`，新增 `/api/execute_solve` 路由
  - [x] SubTask 2.1: 导入 `execute_solve` 函数
  - [x] SubTask 2.2: 实现 `GET /api/execute_solve` 路由，调用 `execute_solve()` 并返回 JSON

- [x] Task 3: 创建 `src/components/SolutionTerminal.jsx` 终端组件
  - [x] SubTask 3.1: 创建组件框架（props: solutions, logs, onReset）
  - [x] SubTask 3.2: 实现逐行打字机效果（useEffect + setTimeout，每行 50ms 延迟）
  - [x] SubTask 3.3: 实现顶部状态栏（TERMINAL_READY / SOLVING_COMPLETE）
  - [x] SubTask 3.4: 实现 RESET 按钮
  - [x] SubTask 3.5: 美团工业风格样式（bg-black/90, border-yellow-500/20, font-mono）

- [x] Task 4: 修改 `src/App.jsx` 集成 SolutionTerminal
  - [x] SubTask 4.1: isExecuting=true 时显示 SolutionTerminal（替代 TacticalMap）
  - [x] SubTask 4.2: SolutionTerminal 调用 `/api/execute_solve` 获取数据
  - [x] SubTask 4.3: SolutionTerminal 的 onReset 恢复卡片视图

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 independent
- Task 4 depends on Task 3
