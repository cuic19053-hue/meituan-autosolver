# AutoSolver 赛道四 — 系统升级指令

## 任务概述
你是美团AI Hackathon赛道四参赛系统的核心开发者。系统当前存在严重缺陷，需要在保持架构优势的前提下，进行安全、稳定、高效的重构升级。

## 评分函数（必须严格遵守）
比赛的真实评分函数为：
```
Score = Σ(costs[i][j] × (2.0 - probs[i][j])) + penalty × n_rejected
```
其中：
- `costs[i][j]` = total_score（配送成本）
- `probs[i][j]` = willingness（接单意愿/准时概率）
- `n_rejected` = 未被分配的订单数
- `penalty` = 拒单惩罚系数（默认100，即未分配订单每个扣100分）

**目标：最小化 Score，Score越低越好。**

## 关键修改要求

### P0 — 致命修复（必须立即完成）

#### 1. 修复评分函数
- 当前 `_compute_utility()` 仅计算 `assigned_tasks × 10`，与真实评分完全不一致
- 新评分函数实现：
```python
def compute_penalty_score(solutions, candidates, all_task_count, penalty=100):
    """
    真实评分：Score = Σ(score × (2.0 - willingness)) + penalty × n_rejected
    """
    assigned_tasks = set()
    total_cost = 0.0
    for task_str, courier_list in solutions:
        tasks = task_str.split(',')
        assigned_tasks.update(tasks)
        # 从candidates中找到对应的score和willingness
        for cand_tasks_str, cand_courier, score, will, _ in candidates:
            if cand_tasks_str == task_str and cand_courier in courier_list:
                total_cost += score * (2.0 - will)
                break
    n_rejected = all_task_count - len(assigned_tasks)
    return total_cost + penalty * n_rejected
```
- 所有使用 `_compute_utility()` 的地方必须替换为 `compute_penalty_score()`
- 注意：**Score越低越好**，因此优化方向从"最大化效用"变为"最小化惩罚分数"

#### 2. 重写 local_search_2opt
- 当前实现只是贪心追加，不是2-opt
- 真正的2-opt应：
  1. 遍历当前解中的每个已分配方案
  2. 尝试移除该分配（释放骑手和订单）
  3. 在释放的资源上尝试更优的替换
  4. 如果总体Score降低则接受交换
- 设置最大迭代次数（如500次）防止超时
- 每次swap后检查时间预算

#### 3. 修复 beam_search 效用
- 将 `new_util = _util + 1` 替换为真实的效用增量计算
- 目标函数是最小化Score，因此束搜索应该朝Score降低的方向搜索
- 每次扩展时计算加入该候选后的增量Score增量

### P1 — 严重修复

#### 4. 统一引擎架构
- 删除 `main.py` 中的 `AgentEngine`（零件路由，与赛道四无关）
- 删除 `engine.py` 中的 `STHAFEngine`（冗余）
- 只保留 `agent.py` 中的 `AutonomousAgent` 作为唯一核心引擎
- `solver_engine.py` 的 `solve()` 直接调用 `AutonomousAgent`

#### 5. 添加输出格式验证
```python
def validate_solution(solutions, candidates, all_tasks) -> list:
    """校验输出格式，确保不会因格式错误被judge判0"""
    if not isinstance(solutions, list):
        return []
    valid = []
    seen_couriers = set()
    seen_tasks = set()
    for item in solutions:
        if not isinstance(item, tuple) or len(item) != 2:
            continue
        task_str, courier_list = item
        if not isinstance(task_str, str) or not isinstance(courier_list, list):
            continue
        if not courier_list:
            continue
        courier = courier_list[0]
        if courier in seen_couriers:
            continue
        tasks = task_str.split(',')
        if any(t in seen_tasks for t in tasks):
            continue
        seen_couriers.add(courier)
        seen_tasks.update(tasks)
        valid.append((task_str, courier_list))
    return valid
```

#### 6. 强化 LLM 响应解析
```python
def _parse_llm_response(self, content: str) -> dict:
    """增强JSON解析，支持markdown包裹、多余文本"""
    content = content.strip()
    # 尝试提取JSON块
    import re
    json_match = re.search(r'\{[^{}]+\}', content)
    if json_match:
        content = json_match.group(0)
    try:
        decision = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"无法解析LLM响应: {content[:100]}")
    strategy = decision.get("strategy", "")
    if strategy not in PRIMITIVES_MAP:
        raise ValueError(f"未知策略: {strategy}")
    return decision
```

### P2 — 性能优化

#### 7. 缓存 candidates 解析结果
```python
class AutonomousAgent:
    def __init__(self):
        # ...
        self._candidates_cache = {}  # input_hash -> candidates
    
    def perceive(self, input_text: str) -> dict:
        import hashlib
        text_hash = hashlib.md5(input_text.encode()).hexdigest()
        if text_hash not in self._candidates_cache:
            self._candidates_cache[text_hash] = _parse_to_candidates(input_text)
        candidates = self._candidates_cache[text_hash]
        features = extract_features(input_text)
        features["_candidate_count"] = len(candidates)
        self.last_state = features
        return features
```

#### 8. 时间预算安全余量
- 将 `DEFAULT_TIME_BUDGET_SEC` 从 3.5s 提高到 8.5s（比赛10s硬限）
- beam_search 和 local_search 在每次迭代前检查剩余时间
- 最终0.8s时强制返回当前最优解

#### 9. 新增快速混合策略
```python
def hybrid_greedy(candidates, all_task_count, penalty=100):
    """混合贪心：同时考虑成本和覆盖率"""
    n = len(candidates)
    # 排序：按 penalty_score 贡献排序
    # 每个候选的"价值" = 不选它的惩罚 - 选它的成本
    indices = sorted(range(n), key=lambda i: 
        penalty * candidates[i][4] - candidates[i][2] * (2.0 - candidates[i][3])
    )
    return _resolve(candidates, indices)
```

### P3 — 稳定性加固

#### 10. 异常兜底三重保障
```python
def solve(input_text: str) -> list:
    """主入口：三重保障"""
    try:
        # 第一重：完整进化引擎
        return _solve_full(input_text)
    except Exception:
        try:
            # 第二重：简化贪心
            candidates = _parse_to_candidates(input_text)
            return conflict_aware_greedy(candidates)
        except Exception:
            # 第三重：最基础返回
            return []
```

#### 11. 数据一致性校验
- 在 `perceive()` 后验证 `total_tasks` 与实际数据一致
- 在 `evolve()` 中校验 `utility` 非负
- 在输出前验证所有 `courier_id` 不重复、所有 `task_id` 不重复

## 质量标准
- 所有修改必须保持向后兼容
- 每个修改点添加中文注释说明改动原因
- 修改后运行 `python -c "from backend.solver_engine import solve; print('OK')"` 验证模块可导入
- 确保 solve() 函数在10秒内完成3万行数据求解

## 不要做的事
- 不要删除现有的 primitives 库，只修改有缺陷的
- 不要删除 LLM 决策链路，只增强鲁棒性
- 不要改变 solve() 函数签名
- 不要引入新的外部依赖（除了 re 和 hashlib，它们是标准库）
