# Tasks

- [x] Task 1: 在 features.py 中新增 cohesiveness_score 特征提取
  - [x] SubTask 1.1: 在 extract_features 中构建任务-运力二部图邻接表
  - [x] SubTask 1.2: 实现 BFS/DFS 最大连通分量计算
  - [x] SubTask 1.3: 计算 cohesiveness_score = max_component_nodes / total_nodes 并加入返回 dict

- [x] Task 2: 在 agent.py 中新增 _build_system_prompt 方法
  - [x] SubTask 2.1: 编写固定的 system prompt 文本（Role / Philosophy / Arsenal / Protocol / Output Format）
  - [x] SubTask 2.2: 每个策略标注预估耗时范围

- [x] Task 3: 重构 _build_prompt 为生存状态报告格式
  - [x] SubTask 3.1: 注入 remaining_time_budget（调用 self._time_budget_remaining()）
  - [x] SubTask 3.2: 注入 LLM Circuit Breaker 状态
  - [x] SubTask 3.3: 注入 cohesiveness_score
  - [x] SubTask 3.4: 保留 history / golden / summary / weight_window 信息

- [x] Task 4: 升级 _call_deepseek 为双消息结构
  - [x] SubTask 4.1: payload.messages 改为 [system, user] 双条
  - [x] SubTask 4.2: 调用 _build_system_prompt() 生成 system content
  - [x] SubTask 4.3: 调用 _build_prompt(state) 生成 user content

- [x] Task 5: 实现 LLM 熔断器机制
  - [x] SubTask 5.1: __init__ 中新增 self._llm_circuit_breaker = False 和 self._llm_timeout_count = 0
  - [x] SubTask 5.2: _call_deepseek 超时时递增 _llm_timeout_count，>=2 时触发熔断
  - [x] SubTask 5.3: make_decision 中检查熔断状态，跳过 LLM 直接降级
  - [x] SubTask 5.4: run_evolution_cycle 结束时重置熔断状态

- [x] Task 6: 升级 _call_llm_summarizer 为双消息结构
  - [x] SubTask 6.1: 新增 system message 定义摘要角色和约束
  - [x] SubTask 6.2: 原 prompt 改为 user message

- [x] Task 7: 验证完整流程可运行
  - [x] SubTask 7.1: python -c "from backend.solver_engine import execute_solve; execute_solve()" 无报错
  - [x] SubTask 7.2: 验证 logs 中包含 [META_AGENT] DeepSeek 策略决策 或 规则降级 日志

# Task Dependencies
- Task 2 depends on Task 1（system prompt 引用 cohesiveness_score）
- Task 3 depends on Task 1（user prompt 引用 cohesiveness_score）
- Task 4 depends on Task 2 + Task 3（需要两个 prompt 构建方法就绪）
- Task 5 depends on Task 4（熔断器需要拦截 _call_deepseek）
- Task 6 depends on Task 2（复用 system prompt 模式）
- Task 7 depends on Task 4 + Task 5 + Task 6
