# 终极版 Meta-Agent System Prompt 重构 Spec

## Why
当前 `_call_deepseek` 仅传 `user` 消息，无 `system` 角色指令，LLM 缺乏时间观念和安全意识。`_build_prompt` 不传递 `remaining_time_budget`、策略耗时估算、图凝聚度等关键生存数据，导致 LLM 可能在剩余 0.3s 时仍选择耗时 2s 的 `local_search_2opt`，直接超时判零。需要将 LLM 调用升级为"战区指挥官"模式：system prompt 定义角色哲学与执行协议，user prompt 注入实时生存数据。

## What Changes
- **`_call_deepseek`**：从单条 `user` 消息改为 `system` + `user` 双消息结构
- **新增 `_build_system_prompt`**：生成固定的角色定义、安全哲学、策略武器库、执行协议、输出格式约束
- **`_build_prompt`**：从"通用运筹专家"改为"生存状态报告"格式，注入 `remaining_time_budget`、`cohesiveness_score`、策略耗时标注、LLM 熔断状态
- **`_call_llm_summarizer`**：同步升级为双消息结构
- **`features.py`**：新增 `cohesiveness_score` 特征提取（图连通分量占比）
- **`agent.py`**：新增 `_llm_circuit_breaker` 标志，连续 N 次 LLM 超时后触发熔断

## Impact
- Affected specs: `implement-meta-agent-engine`（prompt 层升级）
- Affected code:
  - `d:\美团\backend\agent.py`（`_build_prompt`, `_call_deepseek`, `_call_llm_summarizer`, 新增 `_build_system_prompt`）
  - `d:\美团\backend\features.py`（新增 `cohesiveness_score`）

## ADDED Requirements

### Requirement 1: System Prompt 角色定义
系统 SHALL 在每次 DeepSeek 调用中注入 `system` 角色 message，包含以下固定内容：
- **Role**：精英运筹科学家 + Meta-Agent 大脑，唯一目标是在 5s 硬限制下最大化效用
- **Core Philosophy**：安全第一（超时=0分）、动态策略路由、防御纵深（系统有熔断器兜底）
- **Available Arsenal**：每个策略标注预估耗时（conflict_aware_greedy ~0.05s, utility_density_greedy ~0.1s, local_search_2opt ~1.0s+, beam_search ~0.5s-2.0s）
- **Execution Protocol**：感知→看钟→反思历史→决策
- **Strict Output Format**：仅输出 JSON，无 markdown 代码块，无解释文字

#### Scenario: system message 结构
- **WHEN** `_call_deepseek` 被调用
- **THEN** payload.messages 包含两条：`{"role": "system", "content": <system_prompt>}` + `{"role": "user", "content": <user_prompt>}`

### Requirement 2: User Prompt 生存状态注入
系统 SHALL 在 `_build_prompt` 中注入以下实时生存数据：
- `Remaining Time Budget`：调用 `self._time_budget_remaining()` 获取，精确到 0.01s
- `LLM Circuit Breaker`：显示当前熔断状态
- `Graph Cohesiveness`：从 state 中读取 `cohesiveness_score`
- 策略武器库中每个策略标注耗时范围
- 保留原有的 history / golden / summary / weight_window 信息

#### Scenario: 时间不足时 LLM 自动避险
- **WHEN** remaining_time_budget < 1.0s
- **THEN** user prompt 中明确标注 "CRITICAL: Less than 1.0s remaining"，LLM 被 system prompt 约束禁止选择 local_search_2opt

#### Scenario: 正常时间预算
- **WHEN** remaining_time_budget >= 2.0s
- **THEN** user prompt 显示正常状态，LLM 可自由选择任意策略

### Requirement 3: 图凝聚度特征
系统 SHALL 在 `features.py` 的 `extract_features` 中新增 `cohesiveness_score` 计算：
- 基于任务-运力二部图的最大连通分量占比
- 公式：`cohesiveness_score = max_component_nodes / total_nodes`
- 值域 [0, 1]，>0.7 表示图高度连通（分解策略无效）

#### Scenario: 高凝聚度图
- **WHEN** cohesiveness_score > 0.7
- **THEN** LLM 在 prompt 中看到此值，system prompt 约束其不选择 decompose 策略

### Requirement 4: LLM 熔断器
系统 SHALL 实现 `_llm_circuit_breaker` 机制：
- 连续 2 次 LLM 调用超时（>8s）后触发熔断
- 熔断状态下，`make_decision` 跳过 LLM 直接走规则降级链路
- 熔断状态在 `run_evolution_cycle` 结束时重置
- 熔断状态通过 `_build_prompt` 传递给 LLM（如 LLM 仍被调用）

#### Scenario: 连续超时触发熔断
- **WHEN** `_call_deepseek` 连续 2 次抛出 timeout 异常
- **THEN** `self._llm_circuit_breaker = True`，后续 `make_decision` 不再尝试 LLM

#### Scenario: 熔断恢复
- **WHEN** `run_evolution_cycle` 完成
- **THEN** `self._llm_circuit_breaker = False`

### Requirement 5: Summarizer 双消息结构
系统 SHALL 将 `_call_llm_summarizer` 升级为 `system` + `user` 双消息结构：
- system message：定义"你是调度策略分析专家，输出 200 字以内纯文本摘要"
- user message：保持原有的 top/worst 记录 + 窗口信息

## MODIFIED Requirements

### Requirement: _call_deepseek 消息结构（原为单条 user）
payload.messages 从 `[{"role": "user", "content": prompt}]` 改为 `[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]`

### Requirement: _build_prompt 输出格式（原为通用运筹专家风格）
从"你是运筹学调度策略专家"改为"Current Survival Status"格式，注入时间预算和熔断状态
