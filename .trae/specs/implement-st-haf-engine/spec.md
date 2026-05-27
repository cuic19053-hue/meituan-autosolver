# ST-HAF 时空多智能体协同博弈调度引擎 Spec

## Why
当前 solver_engine.py 存在三个核心问题：
1. 冲突日志不区分类型（运力冲突 vs 任务冲突），无法体现算法的"思考过程"
2. efficiency_gain 与 completion_rate 完全相同（都是 87.5%），两个指标没有差异化语义
3. 日志前缀不符合 ST-HAF 命名规范（[ALLOCATION]→[AI_ALLOTMENT]，[CONFLICT]→[系统拦截]/[节点冲突]）

## What Changes
- **`solver_engine.py`**：重写核心算法，实现 ST-HAF 两阶段架构（竞标阶段 + 拓扑冲突排查），区分冲突类型日志，差异化 KPI 计算

## Impact
- Affected specs: `refactor-solver-engine-v2`（升级为 ST-HAF）
- Affected code:
  - `d:\美团\backend\solver_engine.py`
  - `d:\美团\src\components\SolutionTerminal.jsx`（需适配新日志前缀）

## MODIFIED Requirements

### Requirement 1: ST-HAF 阶段一 — Agent 意愿度竞标 (Bidding Phase)
系统 SHALL 为每个潜在匹配计算综合效用值：`Utility = score × 0.7 + willingness × 0.3`
系统 SHALL 按 Utility 降序排列所有候选方案。
系统 SHALL 在日志中记录竞标阶段完成信息。

#### Scenario: 竞标阶段
- **WHEN** 数据解析完成
- **THEN** 所有候选方案按 Utility 降序排列
- **AND** 日志输出 `> [SYS] 效用矩阵构建完成，已按多目标权重降序排列`

### Requirement 2: ST-HAF 阶段二 — 空间拓扑冲突排查 (Topology Conflict Resolution)
系统 SHALL 维护 `locked_tasks` 和 `locked_couriers` 两个全局集合。
系统 SHALL 区分三种冲突类型并输出不同日志：
- **运力冲突**：`> [系统拦截] 运力 {courier_id} 发生时空重叠，拒绝派单。`
- **任务冲突**：`> [节点冲突] 任务节点已被抢占，拦截派发。`
- **合法匹配**：`> [AI_ALLOTMENT] 智能体 {courier_id} 成功锚定任务拓扑 {task_ids} (效用: {Utility:.2f})`

系统 SHALL 优先检查运力冲突，其次检查任务冲突。

#### Scenario: 运力冲突
- **WHEN** courier_id 已在 locked_couriers 中
- **THEN** 输出 `[系统拦截]` 日志
- **AND** 跳过该方案

#### Scenario: 任务冲突
- **WHEN** courier_id 可用但某个 task_id 已在 locked_tasks 中
- **THEN** 输出 `[节点冲突]` 日志
- **AND** 跳过该方案

#### Scenario: 合法匹配
- **WHEN** courier_id 和所有 task_id 均可用
- **THEN** 输出 `[AI_ALLOTMENT]` 日志
- **AND** 将匹配加入 final_solutions

### Requirement 3: 差异化 KPI 计算
系统 SHALL 计算 `efficiency_gain` 为全局效用峰值占理论最大效用的百分比。
系统 SHALL 计算 `completion_rate` 为已匹配任务数占总任务数的百分比。
两个指标必须不同。

#### Scenario: KPI 计算
- **WHEN** 算法执行完成
- **THEN** `efficiency_gain` = `(实际总效用 / 理论最大效用) × 100%`
- **AND** `completion_rate` = `(已匹配任务数 / 总任务数) × 100%`
- **AND** `latency` = 真实计算耗时

### Requirement 4: 前端终端适配新日志前缀
系统 SHALL 确保 SolutionTerminal.jsx 正确渲染新的日志前缀：
- `[AI_ALLOTMENT]` → 绿色正常行
- `[系统拦截]` → 可选橙色冲突行
- `[节点冲突]` → 可选橙色冲突行

### Requirement 5: 约束保证
系统 MUST NOT 修改 API 返回结构（status/kpi/logs/solutions 四个顶层字段不变）。
系统 MUST NOT 修改 solutions 中每个对象的 courier/tasks 字段名。
系统 MUST 保持 `parse_seed_file()` 函数签名不变。