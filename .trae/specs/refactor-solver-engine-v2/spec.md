# 后端运筹调度算法引擎 (Solver Engine v2) 深度重构 Spec

## Why
当前 `solver_engine.py` 的贪心算法骨架已就绪，但日志语态为机器翻译风格（`[ASSIGN #1]`、`U=xxx`），KPI 中的 `latency` 使用随机数 Mock，API 响应缺少 `status` 字段，且 `main.py` 中存在 `result['stats']` 引用不存在的 key 的 bug。本次重构将算法引擎升级为"时空约束下的多目标优化模型"，日志语态对齐前端的"多智能体决策终端"风格。

## What Changes
- **`solver_engine.py`**：日志格式全面升级为拓扑节点锚定语态；KPI 改为动态计算（真实算法耗时 + 覆盖率）；新增 `status` 字段；移除合成 Padding 至 301 的逻辑
- **`main.py`**：修复 `execute_solve_api` 中引用 `result['stats']` 不存在的 bug；对齐响应结构
- **BREAKING**：API 响应结构新增 `status` 字段，前端如有依赖需适配

## Impact
- Affected specs: `implement-solver-terminal`（终端日志流格式变更）
- Affected code:
  - `d:\美团\backend\solver_engine.py`
  - `d:\美团\backend\main.py`
  - `d:\美团\src\components\SolutionTerminal.jsx`（可能需要微调日志渲染）

## MODIFIED Requirements

### Requirement 1: 数据解析层 (Spatial-Temporal Data Parsing)
系统 SHALL 从 `large_seed301.txt` 解析提取结构化对象，每个对象包含：
- `task_id_list`：任务 ID 列表（支持组合任务）
- `courier_id`：运力/骑手 ID
- `score`：基础收益（float）
- `willingness`：骑手意愿度（float）
- `utility`：综合效用值 = score × 0.7 + willingness × 0.3

系统 SHALL 支持 UTF-8 / GBK / Latin-1 多编码自动回退解析。

#### Scenario: 正常解析 175 行数据
- **WHEN** 调用 `parse_seed_file()`
- **THEN** 返回包含 175 条结构化记录的列表
- **AND** 每条记录包含 `task_id_list`（列表）、`courier_id`（字符串）、`score`（浮点）、`willingness`（浮点）、`utility`（浮点）

### Requirement 2: 时空冲突贪心调度引擎 (Constrained Multi-Objective Greedy)
系统 SHALL 按以下步骤执行调度：
1. 计算每条候选方案的效用值 `Utility = Score × 0.7 + Willingness × 0.3`
2. 按 Utility 降序排序
3. 维护 `locked_tasks: Set[str]` 和 `locked_couriers: Set[str]`
4. 遍历排序后方案：仅当所有 `task_id_list` 中的任务均不在 `locked_tasks` 中，且 `courier_id` 不在 `locked_couriers` 中时，判定为合法分配
5. 合法分配立即将任务和运力打入锁定集合

系统 SHALL 确保每个任务最多分配给一个运力，每个运力最多接一组任务。

#### Scenario: 无冲突分配
- **WHEN** 存在候选 `{tasks: ["T0001"], courier: "C001", utility: 85.0}` 且 T0001 和 C001 均未锁定
- **THEN** 该方案被接受，T0001 和 C001 加入锁定集合

#### Scenario: 任务已锁定
- **WHEN** 候选方案中 `tasks` 包含已锁定的 T0001
- **THEN** 该方案被丢弃，生成冲突日志

#### Scenario: 运力已锁定
- **WHEN** 候选方案中 `courier` 为已锁定的 C001
- **THEN** 该方案被丢弃，生成冲突日志

### Requirement 3: 智能体终端日志流 (Agent Log Simulation)
系统 SHALL 在调度过程中生成伴随日志列表，格式如下：

- 合法分配：`> [ALLOCATION] 拓扑节点 {task_ids} 成功锚定至运力 {courier_id} (效用值: {utility:.2f})`
- 冲突丢弃：`> [CONFLICT] 丢弃分配: 运力 {courier_id} 发生时空重叠，跳过。`
- 初始化：`> [SYS] 时空拓扑数据加载完成，共 {count} 条候选方案`
- 排序完成：`> [SYS] 效用矩阵构建完成，已按多目标权重降序排列`
- 汇总：`> [SYS] 推演完毕 | 锚定任务 {n} 项 | 激活运力 {m} 个 | 全局效用峰值 {score}`

#### Scenario: 终端日志流生成
- **WHEN** `execute_solve()` 执行完成
- **THEN** 返回的 `logs` 列表包含完整的推演过程日志
- **AND** 每条合法分配日志以 `> [ALLOCATION]` 开头
- **AND** 每条冲突日志以 `> [CONFLICT]` 开头

### Requirement 4: 标准化 API 响应结构 (Response Payload)
系统 SHALL 返回以下严格格式的 JSON：

```json
{
  "status": "success",
  "kpi": {
    "efficiency_gain": "+24.8%",
    "completion_rate": "98.5%",
    "latency": "1.02s"
  },
  "logs": ["...", "..."],
  "solutions": [
    {"courier": "C028", "tasks": ["T0037", "T0039"]},
    ...
  ]
}
```

- `status`：固定 `"success"`（无异常时）
- `kpi.efficiency_gain`：根据实际匹配率动态计算（匹配率 × 100%）
- `kpi.completion_rate`：匹配任务数 / 总任务数 × 100%
- `kpi.latency`：算法实际执行耗时（秒，保留两位小数）
- `solutions`：仅包含合法分配方案，不包含 Padding 合成数据

#### Scenario: 完整 API 响应
- **WHEN** 调用 `GET /api/execute_solve`
- **THEN** 返回包含 `status`、`kpi`、`logs`、`solutions` 四个顶级字段的 JSON

### Requirement 5: 性能保障
系统 SHALL 确保在处理 175 条数据时总耗时 < 0.5 秒。
系统 SHALL 使用 Set 数据结构确保 O(1) 冲突查找。

#### Scenario: 性能验证
- **WHEN** 执行 `execute_solve()` 处理 175 条候选方案
- **THEN** 算法逻辑部分耗时 < 100ms
- **AND** `kpi.latency` 反映真实执行耗时

### Requirement 6: main.py 适配
系统 SHALL 修复 `execute_solve_api` 中对 `result['stats']` 的无效引用。
系统 SHALL 确保 API 返回结构与 solver_engine 输出一致。

#### Scenario: API 调用无异常
- **WHEN** 前端调用 `GET /api/execute_solve`
- **THEN** 返回 200 状态码
- **AND** 响应 JSON 包含 `status`、`kpi`、`logs`、`solutions` 四个字段