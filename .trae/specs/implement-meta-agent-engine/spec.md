# AutoSolver Meta-Agent 两层调度引擎重构 Spec

## Why
当前 solver_engine.py 是单层贪心架构，效用公式 `Utility = score × 0.7 + willingness × 0.3` 存在两个致命问题：
1. score 在官方数据中是"成本"语义（越低越好），直接乘权重会导致高成本方案被优先选择
2. 权重固定为 0.7/0.3，无法根据大盘数据动态调整策略

需要重构为 Meta-Agent + ST-HAF 两层架构，实现动态权重决策和正确的成本反转效用计算。

## What Changes
- **`solver_engine.py`**：全面重写为 OOP 架构（MetaAgent 类 + STHAFEngine 类）
- **效用公式**：从 `score × 0.7 + willingness × 0.3` 改为 `(100 - score) × w_score + (willingness × 100) × w_will`
- **动态权重**：Meta-Agent 根据平均意愿度自动调整 w_score/w_will
- **元认知日志**：新增 [META_AGENT] / [META_REFLECTION] 前缀日志

## Impact
- Affected specs: `implement-st-haf-engine`（升级为 Meta-Agent 架构）
- Affected code:
  - `d:\美团\backend\solver_engine.py`
  - `d:\美团\src\components\SolutionTerminal.jsx`（需适配新日志前缀）
  - `d:\美团\backend\main.py`（需确认 execute_solve 调用兼容）

## ADDED Requirements

### Requirement 1: MetaAgent 元控制器类
系统 SHALL 实现 `MetaAgent` 类，负责大盘分析和动态策略生成。
系统 SHALL 计算平均 willingness，当 avg_will < 0.3 时设 w_will=0.6, w_score=0.4；否则设 w_will=0.3, w_score=0.7。
系统 SHALL 生成元认知日志：
- `> [META_AGENT] 挂载算例成功，检测到候选拓扑方案 {N} 条。`
- `> [META_AGENT] 大盘运力意愿度均值诊断：{avg_will:.2f}`
- `> [META_REFLECTION] 动态调整效用函数权重 -> Score: {w_score}, Willingness: {w_will}`

#### Scenario: 低意愿度场景
- **WHEN** 平均 willingness < 0.3
- **THEN** w_will = 0.6, w_score = 0.4（提高意愿度权重，保障骑手体验）

#### Scenario: 正常意愿度场景
- **WHEN** 平均 willingness >= 0.3
- **THEN** w_will = 0.3, w_score = 0.7（优先平台效率）

### Requirement 2: STHAFEngine 执行引擎类
系统 SHALL 实现 `STHAFEngine` 类，接收 MetaAgent 下发的权重参数。
系统 SHALL 使用新效用公式：`Utility = (100 - score) × w_score + (willingness × 100) × w_will`
系统 SHALL 按 Utility 降序排列候选方案。
系统 SHALL 维护 assigned_couriers 和 assigned_tasks 两个 Set 进行 O(1) 冲突检测。
系统 SHALL 生成 [AI_ALLOTMENT] / [系统拦截] / [节点冲突] 日志。

#### Scenario: 效用计算
- **WHEN** score=52.016, willingness=0.582, w_score=0.7, w_will=0.3
- **THEN** Utility = (100-52.016)×0.7 + (0.582×100)×0.3 = 33.59 + 17.46 = 51.05

### Requirement 3: API 返回结构兼容
系统 SHALL 保持 { status, kpi, logs, solutions } 四个顶层字段不变。
系统 SHALL 保持 solutions 中每个对象包含 courier/tasks 字段。
系统 SHALL 保持 parse_seed_file() 函数签名不变。
execute_solve() 函数签名 SHALL 保持不变。

### Requirement 4: 前端终端适配
系统 SHALL 确保 SolutionTerminal.jsx 正确渲染新的日志前缀：
- `[META_AGENT]` → 正常行
- `[META_REFLECTION]` → 高亮行（策略决策）

### Requirement 5: 约束保证
系统 MUST NOT 修改 main.py 中的 API 路由结构。
系统 MUST 保持 OOP 设计模式（MetaAgent + STHAFEngine 两个类）。