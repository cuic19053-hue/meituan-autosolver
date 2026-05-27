# Tasks

- [x] Task 1: 新增多场景稳定性测试框架 `backend/test_harness.py`
  - [x] 实现 `generate_test_data(scenario, seed)` — 根据场景参数生成合成测试数据
  - [x] 实现 `run_stability_test(agent, repeat=5)` — 8场景×5重复，报告均值/方差/成功率
  - [x] 实现 `print_report(results)` — 格式化输出测试报告表格
  - [x] 验证：`python backend/test_harness.py` 可独立运行并输出8场景结果

- [x] Task 2: 新增基准对比模块 `backend/benchmark.py`
  - [x] 实现 `_random_baseline(candidates)` — 随机分配基准
  - [x] 实现 `run_benchmark(input_text, solutions)` — 运行全部baseline
  - [x] 实现 `print_benchmark_report(report)` — 格式化输出对比表格
  - [x] 验证：AutoSolver Score ≤ 所有baseline Score

- [x] Task 3: 增强 local_search_2opt 跨骑手Exchange
  - [x] 修改 `backend/primitives/__init__.py` 中的 `local_search_2opt`
  - [x] 新增跨骑手Exchange逻辑：遍历所有骑手对(i,j)，尝试交换分配
  - [x] 每次swap后用 `compute_penalty_score` 评估，Score降低则接受
  - [x] 验证：对比Exchange前后的Score确实有改善

- [x] Task 4: 升级策略路由器为V2（Golden检索融合）
  - [x] 修改 `backend/features.py` 的 `route_strategy()`
  - [x] 新增 `_find_closest_golden(features, golden_strategies)` — 特征距离计算
  - [x] 新增 `route_strategy_v2(features, golden_strategies)` — 融合检索+规则
  - [x] 返回 `(decision_dict, confidence)` 元组
  - [x] 原 `route_strategy()` 保持向后兼容

- [x] Task 5: 新增零LLM推理模式 `run_cycle_no_llm()`
  - [x] 在 `backend/agent.py` 的 `AutonomousAgent` 类中新增方法
  - [x] 执行流程：感知→路由(V2)→快速梯度搜索→(可选)local_search→校验
  - [x] 全程不调用 `_call_deepseek` 或 `_llm_decision`
  - [x] 验证：与LLM模式的Score差距 < 10%

- [x] Task 6: 增加输入安全校验
  - [x] 在 `backend/solver_engine.py` 新增 `_validate_input(input_text)` 函数
  - [x] 修改 `solve()` 入口：先校验再执行
  - [x] 验证：空输入/格式错误输入不崩溃

- [x] Task 7: 增强输出校验（存在性校验）
  - [x] 修改 `backend/primitives/__init__.py` 中的 `validate_solution()`
  - [x] 新增 `all_tasks` 和 `all_couriers` 参数（可选）
  - [x] 校验每个分配的task_id和courier_id存在于原始数据中
  - [x] 兼容原有不传这两个参数的调用方式

- [x] Task 8: 优化LLM熔断器（时间窗口+自动恢复）
  - [x] 修改 `backend/agent.py` 中 `AutonomousAgent.__init__`
  - [x] 新增 `_llm_timeout_timestamps: list` 和 `_llm_circuit_triggered_at: float`
  - [x] 新增 `_check_circuit_breaker()` 方法
  - [x] 修改 `_call_deepseek`：增加响应内容校验（长度≥10 + 含"strategy"）
  - [x] 验证：手动模拟超时触发熔断 + 60秒后自动恢复

- [x] Task 9: 增加确定性保障
  - [x] 修改 `backend/agent.py` 的 `make_decision()` 新增 `deterministic_mode` 参数
  - [x] deterministic_mode=True时跳过ε-random和随机探索
  - [x] 验证：相同输入+确定性模式→相同输出

- [x] Task 10: 新增提交合规检查 `backend/compliance_check.py`
  - [x] 实现 `check_compliance(project_root)` 检查5项提交要求
  - [x] 输出通过/失败状态和缺失项列表
  - [x] 验证：指向项目根目录可运行

# Task Dependencies

- Task 5（零LLM推理）依赖 Task 4（路由器V2）—— 需要V2路由器才能零LLM路由
- Task 3（跨骑手Exchange）独立，可并行
- Task 1/2/6/7/8/9/10 互相独立，可并行