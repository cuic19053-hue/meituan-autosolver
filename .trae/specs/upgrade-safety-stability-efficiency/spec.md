# AutoSolver v5.0 — 安全·稳定·高效·合规 全面升级 Spec

## Why
系统已完成P0/P1核心修复（评分对齐、真实2-opt、beam_search分数修复、熔断器、三重兜底），但缺少**多场景稳定性验证、基准对比量化、输入安全防护、零LLM独立推理**四大关键能力。这直接关系到决赛现场能否稳定运行、报告能否提供量化评测数据、以及赛道四"分析深度与报告质量(30%)"的评分要求。

## What Changes
- **新增 `backend/test_harness.py`**：多场景自动化测试框架（8种场景类型，每场景5次重复，报告均值/方差/成功率）
- **新增 `backend/benchmark.py`**：基准对比模块（对比random/greedy/ortools等baseline，输出对比报告）
- **修改 `backend/primitives/__init__.py`**：`local_search_2opt` 增加跨骑手 Exchange 操作
- **修改 `backend/features.py`**：`route_strategy()` 增加 Golden策略检索融合
- **新增 `backend/compliance_check.py`**：提交合规检查（验证文件结构、报告完整性）
- **修改 `backend/agent.py`**：新增 `run_cycle_no_llm()` 零LLM推理模式 + 确定性保障
- **修改 `backend/solver_engine.py`**：`solve()` 入口增加输入安全校验
- **修改 `backend/primitives/__init__.py`**：`validate_solution` 增加存在性校验
- **修改 `backend/agent.py`**：LLM熔断器改为时间窗口+自动恢复 + 响应长度/内容校验

## Impact
- Affected specs: 
  - `refactor-solver-engine-v2`（solver_engine输入校验增强）
  - `upgrade-meta-agent-llm-prompt`（LLM调用路径加固）
  - `implement-meta-agent-engine`（零LLM推理模式）
  - `polish-debrief-override-reset`（UI不变，后端输出格式保持兼容）
- Affected code:
  - `d:\美团\backend\test_harness.py`（**新增**）
  - `d:\美团\backend\benchmark.py`（**新增**）
  - `d:\美团\backend\compliance_check.py`（**新增**）
  - `d:\美团\backend\primitives\__init__.py`（local_search增强 + validate_solution增强）
  - `d:\美团\backend\features.py`（route_strategy_v2）
  - `d:\美团\backend\agent.py`（零LLM推理 + 确定性 + 熔断器优化）
  - `d:\美团\backend\solver_engine.py`（输入安全校验）

---

## ADDED Requirements

### Requirement 1: 多场景稳定性测试框架
系统 SHALL 提供 `backend/test_harness.py`，支持8种预定义场景类型的自动化测试。

场景类型：
- `small_sparse`：小型稀疏（10-50行，≤5骑手）
- `medium_standard`：中型标准（100-500行，≤20骑手）
- `large_dense`：大型密集（5000-10000行，≤50骑手）
- `low_willingness`：极端低意愿（avg_will < 0.15）
- `high_density`：极端高密度（density > 10）
- `all_conflict`：全冲突（仅1个骑手，所有候选竞争同一骑手）
- `single_courier`：单骑手退化
- `empty_or_malformed`：空输入/格式错误

每个场景重复5次，报告：均值Score、标准差、最大/最小耗时、成功率。

#### Scenario: 运行全场景测试
- **WHEN** 执行 `python backend/test_harness.py`
- **THEN** 输出8个场景的测试结果表格
- **AND** 成功率 < 100% 的场景标记为 FAIL
- **AND** 平均耗时 > 9.5s 的场景标记为 TIMEOUT_WARNING

#### Scenario: 空输入测试
- **WHEN** 输入为空字符串或仅含表头的文本
- **THEN** solve() 返回 `[]` 且不抛出异常

---

### Requirement 2: 基准对比模块
系统 SHALL 提供 `backend/benchmark.py`，对同一个测试数据集同时运行AutoSolver和多个baseline，输出对比报告。

Baseline列表：
- `random_assignment`：随机分配（性能下界）
- `greedy_min_cost`：纯成本贪心
- `greedy_max_willingness`：纯意愿度贪心
- `conflict_aware_greedy`：冲突感知贪心（当前兜底策略）
- `hybrid_greedy`：混合贪心

对比指标：Score值、相对AutoSolver的改善百分比。

#### Scenario: 运行基准对比
- **WHEN** 执行 `python backend/benchmark.py`
- **THEN** 输出对比表格，列出每个baseline的Score和相对改善率
- **AND** AutoSolver的Score必须 ≤ 所有baseline的Score

---

### Requirement 3: local_search_2opt 跨骑手Exchange
系统 SHALL 在 `local_search_2opt` 中增加跨骑手任务交换操作（Exchange）。

当前实现：仅在同一骑手的候选方案中尝试替换（Relocate）。
新增操作：尝试将骑手A的分配与骑手B的分配交换（Exchange），若总体Score降低则接受。

最大迭代次数500，每次swap后检查时间预算。

#### Scenario: 跨骑手Exchange改善解质量
- **WHEN** local_search_2opt 在已有解上运行
- **THEN** 尝试任意两个不同骑手的分配交换
- **AND** 若交换后Score降低，接受新解
- **AND** 若时间预算耗尽，返回当前最优解

---

### Requirement 4: 策略路由器V2（融合Golden检索）
系统 SHALL 在 `route_strategy()` 中增加Golden策略检索融合：

1. 先在Golden策略库中按特征距离查找最相似场景
2. 若距离 < 0.15，直接用Golden策略（高置信度）
3. 若找不到，回退到现有硬编码决策树规则

返回格式：`(strategy_decision, confidence: float)`

#### Scenario: Golden策略命中
- **WHEN** 输入数据特征与某Golden策略的特征距离 < 0.15
- **THEN** 直接返回该Golden策略，置信度 0.9
- **AND** 不进行LLM调用

#### Scenario: Golden策略未命中
- **WHEN** 无相似Golden策略
- **THEN** 使用硬编码决策树规则选择策略，置信度 0.5

---

### Requirement 5: 零LLM推理模式
系统 SHALL 在 `AutonomousAgent` 中新增 `run_cycle_no_llm(input_text)` 方法：

执行流程：
1. 感知层：提取特征 + 解析candidates
2. 路由层：使用V2路由器（含Golden检索）选择初始策略
3. 优化层：对utility_density_greedy做快速梯度搜索（[-0.05, 0.05]）
4. 精炼层：若剩余时间 > 1.5s，执行local_search_2opt改进
5. 输出层：validate_solution校验

全程不调用任何LLM API。

#### Scenario: 零LLM模式正常执行
- **WHEN** 调用 `agent.run_cycle_no_llm(input_text)`
- **THEN** 在8.5s内完成求解
- **AND** 输出的解经过validate_solution校验
- **AND** 无任何LLM API调用发生

#### Scenario: 零LLM模式时间不足
- **WHEN** 路由+执行阶段耗时超过7.0s
- **THEN** 跳过local_search_2opt步骤
- **AND** 直接返回路由阶段的结果

---

### Requirement 6: 输入安全校验
系统 SHALL 在 `solver_engine.py` 的 `solve()` 入口新增 `_validate_input()` 安全层：

- 空输入 → 返回 `[]`
- 非Tab分隔格式 → 返回 `[]` 并记录告警
- 单行数据（仅表头） → 返回 `[]`
- 正常输入 → 继续执行

#### Scenario: 空输入保护
- **WHEN** `solve("")` 被调用
- **THEN** 返回 `[]`，不抛出任何异常

#### Scenario: 格式异常保护
- **WHEN** 输入为逗号分隔或JSON格式而非Tab分隔
- **THEN** 返回 `[]`，不崩溃

---

### Requirement 7: 输出校验增强
系统 SHALL 在 `validate_solution()` 中增加存在性校验：

- 检查每个分配的task_id是否存在于原始candidates中
- 检查每个分配的courier_id是否存在于原始candidates中
- 发现的异常分配自动剔除

#### Scenario: 存在性校验
- **WHEN** 解中包含不存在于原始数据中的task_id或courier_id
- **THEN** 该条分配被剔除
- **AND** 不影响其他有效分配的保留

---

### Requirement 8: LLM熔断器优化
系统 SHALL 将LLM熔断器从简单计数改为时间窗口+自动恢复机制：

- 30秒滑动窗口内超时 ≥ 3次 → 触发熔断
- 熔断后60秒自动恢复尝试
- 增加响应内容校验：长度 < 10字符 或 不含"strategy"关键词 → 视为无效，不计入成功调用

#### Scenario: 熔断触发
- **WHEN** 30秒内连续3次LLM调用超时
- **THEN** 熔断器激活，后续 `make_decision` 跳过LLM

#### Scenario: 熔断自动恢复
- **WHEN** 熔断器激活后经过60秒
- **THEN** 熔断器自动重置，下次 `make_decision` 重新尝试LLM

---

### Requirement 9: 确定性保障
系统 SHALL 在 `make_decision()` 中新增 `deterministic_mode` 参数：

- `deterministic_mode=True` 时：跳过 ε-greedy 随机探索，直接走最佳决策路径
- 相同输入 + deterministic_mode → 相同输出
- Golden策略命中时不触发 ε-override

#### Scenario: 确定性模式
- **WHEN** `agent.make_decision(state, deterministic_mode=True)`
- **THEN** 相同state总是返回相同策略选择
- **AND** 无随机探索行为

---

### Requirement 10: 提交合规检查
系统 SHALL 提供 `backend/compliance_check.py`，验证提交包是否满足赛道四要求：

- `source_code/` 目录存在且含所有源码
- `report.pdf` 存在
- `demo.mp4` 存在
- `agent_traces/` 目录存在且含 ≥2个日志文件
- 自建测试集 ≥5个测试文件

#### Scenario: 合规检查通过
- **WHEN** 所有提交文件齐全且符合格式
- **THEN** 输出 "COMPLIANCE OK" 和各文件统计

#### Scenario: 合规检查失败
- **WHEN** 缺少任一必需文件
- **THEN** 输出 "COMPLIANCE FAIL" 和缺失项列表

---

## MODIFIED Requirements

### Requirement: solve() 函数行为
原：`solve(input_text)` 直接进三重兜底
新：先执行 `_validate_input()` 输入校验，无效输入直接返回 `[]`，有效输入再进入三重兜底

### Requirement: validate_solution() 行为
原：仅校验格式和去重
新：增加存在性校验（检查task_id/courier_id是否存在于原始数据中）