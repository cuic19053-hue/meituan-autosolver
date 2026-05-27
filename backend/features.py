"""
特征提取器 v3.0 & 策略路由器
====================================================
v2.0 → v3.0 核心升级：
  - 新增特征：task_courier_ratio, avg_tasks_per_courier, willingness_variance, score_variance
  - 路由决策树增强：更细粒度的场景分类
  - 新增 route_strategy_v3(): 基于更多维度的决策
  - 路由产出 STRATEGY_ID 和新策略名称的映射

设计原则：
- 路由器极轻量 < 0.1s
- 根据输入密度、意愿分布、冲突图结构选择最优策略模板
"""
import math


def extract_features(input_text: str) -> dict:
    """
    通用特征提取 — 从原始文本中计算数据密度、意愿分布、冲突图结构
    耗时目标: < 0.1s，全 Tuple 流式处理
    """
    lines = input_text.split('\n')
    start = 1 if lines and lines[0].startswith("task_id_list") else 0

    total_lines = 0
    total_score = 0.0
    total_will = 0.0
    min_score = float('inf')
    max_score = float('-inf')
    min_will = float('inf')
    max_will = float('-inf')
    task_set = set()
    courier_set = set()
    max_tasks_per_row = 0
    score_sum = 0.0
    will_sum = 0.0
    task_to_couriers = {}
    courier_to_tasks = {}

    for line in lines[start:]:
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 3:
            continue

        total_lines += 1
        tasks_str = parts[0]
        try:
            score = float(parts[2])
        except ValueError:
            continue

        willingness = float(parts[3]) if len(parts) >= 4 else 0.0
        tc = tasks_str.count(',') + 1

        task_set.update(tasks_str.split(','))
        courier_set.add(parts[1])
        courier_id = parts[1]
        for tid in tasks_str.split(','):
            task_to_couriers.setdefault(tid, set()).add(courier_id)
            courier_to_tasks.setdefault(courier_id, set()).add(tid)
        score_sum += score
        will_sum += willingness

        if score < min_score:
            min_score = score
        if score > max_score:
            max_score = score
        if willingness < min_will:
            min_will = willingness
        if willingness > max_will:
            max_will = willingness
        if tc > max_tasks_per_row:
            max_tasks_per_row = tc

    if total_lines == 0:
        return {
            "density": 0,
            "avg_will": 0,
            "avg_score": 0,
            "courier_count": 0,
            "task_count": 0,
            "max_tasks_per_row": 0,
            "total_lines": 0,
            "score_range": 0,
            "cohesiveness_score": 0,
        }

    avg_score = score_sum / total_lines
    avg_will = will_sum / total_lines
    task_count = len(task_set)
    courier_count = len(courier_set)
    density = total_lines / max(task_count, 1)

    visited = set()
    max_component_nodes = 0
    for node in list(task_set) + list(courier_set):
        if node in visited:
            continue
        queue = [node]
        visited.add(node)
        component_size = 0
        while queue:
            cur = queue.pop(0)
            component_size += 1
            neighbors = set()
            if cur in task_to_couriers:
                neighbors.update(task_to_couriers[cur])
            if cur in courier_to_tasks:
                neighbors.update(courier_to_tasks[cur])
            for nb in neighbors:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        if component_size > max_component_nodes:
            max_component_nodes = component_size

    total_nodes = task_count + courier_count
    cohesiveness_score = round(max_component_nodes / total_nodes, 3) if total_nodes > 0 else 0

    task_courier_ratio = round(courier_count / max(task_count, 1), 3)
    avg_tasks_per_courier = round(sum(len(v) for v in courier_to_tasks.values()) / max(courier_count, 1), 2)

    scores_list = []
    wills_list = []
    for line in lines[start:]:
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        try:
            scores_list.append(float(parts[2]))
            wills_list.append(float(parts[3]) if len(parts) >= 4 else 0.0)
        except ValueError:
            continue

    score_mean = sum(scores_list) / len(scores_list) if scores_list else 0
    score_variance = sum((s - score_mean) ** 2 for s in scores_list) / len(scores_list) if scores_list else 0
    will_mean = sum(wills_list) / len(wills_list) if wills_list else 0
    willingness_variance = sum((w - will_mean) ** 2 for w in wills_list) / len(wills_list) if wills_list else 0

    return {
        "density": round(density, 2),
        "avg_will": round(avg_will, 3),
        "avg_score": round(avg_score, 2),
        "courier_count": courier_count,
        "task_count": task_count,
        "max_tasks_per_row": max_tasks_per_row,
        "total_lines": total_lines,
        "score_range": round(max_score - min_score, 2),
        "will_range": round(max_will - min_will, 3),
        "cohesiveness_score": cohesiveness_score,
        "task_courier_ratio": task_courier_ratio,
        "avg_tasks_per_courier": avg_tasks_per_courier,
        "score_variance": round(score_variance, 2),
        "willingness_variance": round(willingness_variance, 4),
    }


def _feature_distance(state_a: dict, state_b: dict) -> float:
    keys = ["density", "avg_will", "avg_score", "task_count", "courier_count"]
    distances = []
    for k in keys:
        va = state_a.get(k, 0)
        vb = state_b.get(k, 0)
        denom = max(abs(va), abs(vb), 1.0)
        distances.append(abs(va - vb) / denom)
    return sum(distances) / len(distances)


def _find_closest_golden(features: dict, golden_strategies: dict) -> dict:
    if not golden_strategies:
        return None
    import json
    best = None
    best_dist = float('inf')
    for state_key, golden in golden_strategies.items():
        state = json.loads(state_key)
        dist = _feature_distance(features, state)
        if dist < best_dist:
            best_dist = dist
            best = {"distance": dist, "action": golden["action"], "utility": golden["utility"]}
    return best


def route_strategy_v2(features: dict, golden_strategies: dict = None) -> tuple:
    import json

    strategy_name_map = {
        0: "conflict_aware_greedy",
        1: "greedy_min_cost",
        2: "utility_density_greedy",
        3: "beam_search",
        4: "local_search_2opt",
    }

    if golden_strategies:
        closest = _find_closest_golden(features, golden_strategies)
        if closest is not None and closest["distance"] < 0.15:
            action = closest["action"]
            strategy_id = action.get("strategy_id", 0)
            decision_dict = {
                "strategy": strategy_name_map.get(strategy_id, "conflict_aware_greedy"),
            }
            if strategy_id == 2:
                decision_dict["params"] = {"w_score": 0.7, "w_will": 0.3}
            elif strategy_id == 3:
                decision_dict["params"] = {"beam_width": 3}
            else:
                decision_dict["params"] = {}
            return (decision_dict, 0.9)

    strategy_id = route_strategy(features)
    decision_dict = {
        "strategy": strategy_name_map.get(strategy_id, "conflict_aware_greedy"),
    }
    if strategy_id == 2:
        decision_dict["params"] = {"w_score": 0.7, "w_will": 0.3}
    elif strategy_id == 3:
        decision_dict["params"] = {"beam_width": 3}
    else:
        decision_dict["params"] = {}
    return (decision_dict, 0.5)


def route_strategy(features: dict) -> int:
    """
    策略路由器 — 离线训练得到的决策树（规则化）
    返回 strategy_id:
      0 = ConflictAwareGreedy (通用最强)
      1 = GreedyMinCost (低意愿场景：优先降低成本)
      2 = UtilityDensityGreedy (高密度场景：每任务效率最高)
      3 = BeamSearch (小规模精细场景)
      4 = LocalSearch_2opt (中等规模改进起点)
    """
    density = features["density"]
    avg_will = features["avg_will"]
    total_lines = features["total_lines"]
    max_tasks = features["max_tasks_per_row"]

    if total_lines <= 30:
        return 3

    if avg_will < 0.25:
        return 1

    if density > 5.0 and max_tasks >= 3:
        return 2

    if total_lines <= 80 and density > 3.0:
        return 4

    return 0


def route_strategy_v3(features: dict, golden_strategies: dict = None) -> tuple:
    """
    v3.0: 增强路由 — 使用更多特征维度做精准策略匹配
    输出: (decision_dict, confidence)
    
    策略映射（扩展）:
      0 = conflict_aware_greedy (通用安全)
      1 = greedy_min_cost (成本优先)
      2 = utility_density_greedy (效用密度)
      3 = beam_search_adaptive (自适应束搜索)
      4 = multi_neighborhood_search (多邻域搜索)
      5 = hybrid_greedy (混合贪心)
      6 = priority_greedy (优先级贪心)
      7 = grasp (GRASP多次重启)
      8 = simulated_annealing (模拟退火)
    """
    import json

    strategy_name_map = {
        0: "conflict_aware_greedy",
        1: "greedy_min_cost",
        2: "utility_density_greedy",
        3: "beam_search_adaptive",
        4: "multi_neighborhood_search",
        5: "hybrid_greedy",
        6: "priority_greedy",
        7: "grasp",
        8: "simulated_annealing",
    }

    if golden_strategies:
        closest = _find_closest_golden(features, golden_strategies)
        if closest is not None and closest["distance"] < 0.15:
            action = closest["action"]
            strategy_name = action.get("strategy", "conflict_aware_greedy")
            decision_dict = {"strategy": strategy_name}
            if strategy_name == "utility_density_greedy":
                decision_dict["params"] = {"w_score": 0.7, "w_will": 0.3}
            elif strategy_name in ("beam_search_adaptive",):
                decision_dict["params"] = {"beam_width_base": 3}
            else:
                decision_dict["params"] = {}
            return (decision_dict, 0.9)

    density = features["density"]
    avg_will = features["avg_will"]
    total_lines = features["total_lines"]
    max_tasks = features["max_tasks_per_row"]
    task_count = features["task_count"]
    courier_count = features["courier_count"]
    cohesiveness = features.get("cohesiveness_score", 0)
    score_var = features.get("score_variance", 0)
    will_var = features.get("willingness_variance", 0)
    task_courier_ratio = features.get("task_courier_ratio", 1.0)

    if total_lines <= 20:
        strategy_id = 8
        confidence = 0.85
    elif total_lines <= 50:
        if cohesiveness > 0.7:
            strategy_id = 3
            confidence = 0.8
        else:
            strategy_id = 7
            confidence = 0.75
    elif avg_will < 0.2 and will_var < 0.05:
        strategy_id = 1
        confidence = 0.85
    elif avg_will < 0.35 and density > 4.0:
        strategy_id = 6
        confidence = 0.75
    elif density > 6.0 and max_tasks >= 3:
        strategy_id = 2
        confidence = 0.8
    elif task_courier_ratio > 2.0 and task_count > 40:
        strategy_id = 5
        confidence = 0.7
    elif total_lines <= 150 and cohesiveness > 0.6:
        strategy_id = 4
        confidence = 0.7
    elif score_var < 10:
        strategy_id = 0
        confidence = 0.8
    else:
        strategy_id = 0
        confidence = 0.6

    decision_dict = {
        "strategy": strategy_name_map.get(strategy_id, "conflict_aware_greedy"),
    }

    if strategy_id == 2:
        decision_dict["params"] = {"w_score": 0.7, "w_will": 0.3}
    elif strategy_id == 3:
        decision_dict["params"] = {"beam_width_base": 3}
    else:
        decision_dict["params"] = {}

    return (decision_dict, confidence)