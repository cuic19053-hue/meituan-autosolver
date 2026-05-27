# 求解器引擎与解决方案终端 Spec

## Why
当前后端使用 `data_service.py` 中的简化 `solve()` 函数，缺乏真正的优化算法和冲突处理。前端也缺少一个能逐行展示求解结果的终端组件来体现"实时调度系统"的工业感。

## What Changes
- 新增 `backend/solver_engine.py`：实现贪心分配算法 + 冲突处理
- 修改 `backend/main.py`：新增 `/api/execute_solve` 接口（不替换现有的 `/api/solver`）
- 新增 `src/components/SolutionTerminal.jsx`：逐行打字机效果的终端组件
- 修改 `src/App.jsx`：集成 SolutionTerminal

## Impact
- Affected specs: 前后端通信契约（新增 `/api/execute_solve` 接口）
- Affected code: 新增 `backend/solver_engine.py`、`src/components/SolutionTerminal.jsx`；修改 `backend/main.py`、`src/App.jsx`

## ADDED Requirements

### Requirement: 贪心分配算法
系统 SHALL 在 `solver_engine.py` 中实现以下逻辑：
1. 解析 `large_seed301.txt`，提取每行的 `task_id_list`、`courier_id`、`score`、`willingness`
2. 计算综合得分：`composite_score = score * 0.7 + willingness * 0.3`
3. 按综合得分降序排列所有方案
4. 依次选取方案，确保每个 Task 和每个 Courier 在最终结果中只出现一次（冲突处理）
5. 贪心策略：如果某 Task 已被占用，跳过该方案；如果某 Courier 已被占用，跳过该方案

#### Scenario: 正常求解
- **WHEN** API 调用 `/api/execute_solve`
- **THEN** 返回最优分配方案，每个 Task 和 Courier 仅出现一次

#### Scenario: 冲突处理
- **WHEN** 综合得分最高的方案中某个 Task 已被占用
- **THEN** 跳过该方案，继续尝试得分次高的方案

### Requirement: execute_solve API 接口
系统 SHALL 在 `main.py` 中新增 `GET /api/execute_solve` 接口。

返回 JSON 格式：
```json
{
  "solutions": [
    {"tasks": "T0037,T0039", "courier": "C028", "score": 52.016, "willingness": 0.582},
    ...
  ],
  "total_score": 1234.56,
  "match_rate": 0.85,
  "avg_willingness": 0.42,
  "logs": [
    "[HH:MM:SS.ss] INIT_SOLVER -> Loading seed data",
    "[HH:MM:SS.ss] MATCH_SUCCESS -> (\"T0037,T0039\", [\"C028\"])",
    "[HH:MM:SS.ss] SKIP_CONFLICT -> (\"T0007,T0037\", [\"C044\"]) Task T0037 already assigned"
  ]
}
```

#### Scenario: API 调用成功
- **WHEN** 客户端发送 `GET /api/execute_solve`
- **THEN** 返回 HTTP 200 和上述 JSON

### Requirement: SolutionTerminal 组件
系统 SHALL 提供 `SolutionTerminal.jsx` 组件。

- 外观：`bg-black/90`，高度与卡片区域一致，`border border-yellow-500/20`，`overflow-y-auto`
- 字体：`font-mono`
- 每行显示格式：`[HH:MM:SS.ss] MATCH_SUCCESS -> ("T0037,T0039", ["C028"])`
- 动画：逐行打字机效果，每行延迟 50ms（0.05s）出现
- 顶部状态栏：显示 `[TERMINAL_READY]` 或 `[SOLVING_COMPLETE]`
- 右上角 RESET 按钮

#### Scenario: 逐行展示
- **WHEN** 父组件传入 `solutions` 数组和 `logs` 数组
- **THEN** 组件在 50ms 间隔内逐行显示每条日志，使用 typewriter 效果

### Requirement: 视图集成
系统 SHALL 将 SolutionTerminal 集成到 App.jsx 中：
- `isExecuting` 状态为 `true` 时，卡片区显示 SolutionTerminal（替代 TacticalMap）
- SolutionTerminal 从 `/api/execute_solve` 获取数据
- RESET 按钮恢复卡片视图

## MODIFIED Requirements
（无）

## REMOVED Requirements
（无）
