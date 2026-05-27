"""
AutonomousAgent v5.0 — 并行战区指挥官模式
============================================================
v4.0 → v5.0 核心升级：
  - P0: 并行策略评估 — 同时评估多个候选策略，选最优
  - P0: 新增 simulated_annealing / grasp / multi_neighborhood_search / beam_search_adaptive
  - P0: 自适应进化轮次 — 根据时间预算和改善幅度动态调整 max_rounds
  - P1: 增强 Golden 策略键 — 加入 cohesiveness / max_tasks_per_row 等更多特征
  - P1: 策略两级精选 — 先快速筛选（6个baseline），再精细优化（top2）
  - P2: Ensemble 最终解 — 多个策略结果融合取最优
  - P2: 时间预算自适应分配 — 根据数据规模动态调整各阶段时间配比

v3.2 → v4.0 保留：
  - ε-greedy 防过拟合
  - Sliding Window 权重搜索
  - LLM 熔断器
  - 经验摘要机制
  - 策略竞技场

设计原则：Agent 不写代码，只操纵配置和选择策略路径。
"""

import hashlib
import json
import math
import os
import random
import re
import time

from backend.features import extract_features, route_strategy, route_strategy_v3
from backend.primitives import (
    _parse_to_candidates,
    _parse_to_candidates_streaming,
    compute_penalty_score,
    validate_solution,
    validate_solution_v2,
    greedy_min_cost,
    greedy_max_willingness,
    conflict_aware_greedy,
    utility_density_greedy,
    hybrid_greedy,
    local_search_2opt,
    beam_search,
    simulated_annealing,
    greedy_randomized_adaptive,
    multi_neighborhood_search,
    pairwise_swap_optimizer,
    merge_optimizer,
    beam_search_adaptive,
    priority_greedy,
)

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")
GOLDEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden.json")
METRICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evolution_metrics.json")
SUMMARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experience_summary.txt")

BASE_EPSILON = 0.15
MIN_EPSILON = 0.05
MAX_EPSILON = 0.35

GOLDEN_OVERRIDE_EPSILON = 0.20

MEMORY_SUMMARY_THRESHOLD = 50

DEFAULT_W_SCORE_MIN = 0.40
DEFAULT_W_SCORE_MAX = 0.75

# P2修复: 时间预算从3.5s提高到8.5s（比赛10s硬限，留1.5s余量）
DEFAULT_TIME_BUDGET_SEC = 8.5

# P0: 自适应进化参数
MIN_ROUNDS = 2
MAX_ROUNDS = 6
BASE_ROUNDS = 3
EVOLUTION_PHASE_RATIO = 0.45
REFINEMENT_PHASE_RATIO = 0.35
SAFETY_MARGIN = 0.15

# P0修复: 效用偏移量，使utility = OFFSET - penalty_score始终为正
# 最大化utility等价于最小化penalty_score
UTILITY_OFFSET = 1000000.0

PRIMITIVES_MAP = {
    "conflict_aware_greedy": conflict_aware_greedy,
    "greedy_min_cost": greedy_min_cost,
    "greedy_max_willingness": greedy_max_willingness,
    "utility_density_greedy": utility_density_greedy,
    "hybrid_greedy": hybrid_greedy,
    "local_search_2opt": local_search_2opt,
    "beam_search": beam_search,
    "simulated_annealing": simulated_annealing,
    "grasp": greedy_randomized_adaptive,
    "multi_neighborhood_search": multi_neighborhood_search,
    "pairwise_swap_optimizer": pairwise_swap_optimizer,
    "merge_optimizer": merge_optimizer,
    "beam_search_adaptive": beam_search_adaptive,
    "priority_greedy": priority_greedy,
}

# P0: 快速评估策略集（低成本，适合第一轮筛选）
FAST_STRATEGIES = [
    "conflict_aware_greedy",
    "greedy_min_cost",
    "greedy_max_willingness",
    "hybrid_greedy",
    "utility_density_greedy",
    "priority_greedy",
]

# P0: 精细策略集（高成本，适合精细优化）
HEAVY_STRATEGIES = [
    "beam_search_adaptive",
    "grasp",
]

# P0: 局部搜索策略集（需要初始解）
LOCAL_SEARCH_STRATEGIES = [
    "multi_neighborhood_search",
    "pairwise_swap_optimizer",
    "merge_optimizer",
]

ALL_STRATEGIES = list(PRIMITIVES_MAP.keys())

WEIGHT_SEARCH_GRID = [-0.10, -0.05, 0, 0.05, 0.10]


def _compute_utility(solutions, candidates, all_task_count, penalty=100):
    """P0修复: 效用 = OFFSET - penalty_score，最大化效用等价于最小化惩罚分数"""
    return UTILITY_OFFSET - compute_penalty_score(solutions, candidates, all_task_count, penalty)


def _resolve_with_audit(candidates, sorted_indices):
    assigned_c = set()
    assigned_t = set()
    result = []
    push = result.append
    courier_conflicts = 0
    task_conflicts = 0

    for idx in sorted_indices:
        tasks_str, courier, _score, _will, _tc = candidates[idx]
        if courier in assigned_c:
            courier_conflicts += 1
            continue
        ts = tasks_str.split(',')
        if any(t in assigned_t for t in ts):
            task_conflicts += 1
            continue
        assigned_c.add(courier)
        assigned_t.update(ts)
        push((tasks_str, [courier]))

    return result, courier_conflicts, task_conflicts


class AutonomousAgent:
    def __init__(self):
        self.history = self._load_memory()
        self.golden_strategies = self._load_golden()
        self.evolution_metrics = self._load_metrics()
        self.experience_summary = self._load_summary()
        self.last_state = None
        self.last_action = None
        self.last_hit_memory = False
        self.evolution_logs = []
        self.threshold = None
        self.conflict_audit_log = []
        self.w_score_min = DEFAULT_W_SCORE_MIN
        self.w_score_max = DEFAULT_W_SCORE_MAX
        self._budget_start_time = None
        self._time_budget_sec = DEFAULT_TIME_BUDGET_SEC
        self._budget_expired = False
        self._llm_circuit_breaker = False
        self._llm_timeout_count = 0
        self._llm_timeout_timestamps = []
        self._llm_circuit_triggered_at = None
        # P2修复: 缓存candidates解析结果（使用LRU防止内存溢出）
        self._candidates_cache = {}
        self._candidates_cache_max_size = 10  # LRU缓存最大条目数
        self._candidates_cache_order = []  # LRU访问顺序
        # P0修复: 存储最近一次的candidates和all_task_count，供_compute_utility使用
        self._last_candidates = None
        self._last_all_task_count = 0
        # P3修复: 零LLM模式标志（DeepSeek API不可用时启用）
        self._zero_llm_mode = False
        if self.history:
            utilities = [h.get("utility", 0) for h in self.history]
            if utilities:
                self.threshold = max(utilities) * 0.8

    def _load_memory(self) -> list:
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            pass
        return []

    def _save_memory(self):
        try:
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _load_golden(self) -> dict:
        try:
            if os.path.exists(GOLDEN_FILE):
                with open(GOLDEN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def _save_golden(self):
        try:
            os.makedirs(os.path.dirname(GOLDEN_FILE), exist_ok=True)
            with open(GOLDEN_FILE, "w", encoding="utf-8") as f:
                json.dump(self.golden_strategies, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _load_metrics(self) -> dict:
        try:
            if os.path.exists(METRICS_FILE):
                with open(METRICS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            pass
        return {
            "total_runs": 0,
            "total_evolutions": 0,
            "utility_history": [],
            "best_utility": 0,
            "w_score_min": DEFAULT_W_SCORE_MIN,
            "w_score_max": DEFAULT_W_SCORE_MAX,
        }

    def _save_metrics(self):
        try:
            os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
            self.evolution_metrics["w_score_min"] = self.w_score_min
            self.evolution_metrics["w_score_max"] = self.w_score_max
            with open(METRICS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.evolution_metrics, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _load_summary(self) -> str:
        try:
            if os.path.exists(SUMMARY_FILE):
                with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except (IOError, UnicodeDecodeError):
            pass
        return ""

    def _save_summary(self, text: str):
        try:
            os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
            with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
                f.write(text)
        except IOError:
            pass

    # ─────────── P2修复: candidates缓存 ───────────

    def _get_candidates(self, input_text: str) -> list:
        """P2修复: 缓存candidates解析结果（LRU防止内存溢出），避免重复解析3万行数据"""
        text_hash = hashlib.md5(input_text.encode()).hexdigest()
        if text_hash in self._candidates_cache:
            # LRU: 更新访问顺序
            self._candidates_cache_order.remove(text_hash)
            self._candidates_cache_order.append(text_hash)
            return self._candidates_cache[text_hash]
        
        # 解析新数据（使用流式解析处理大数据集）
        candidates = _parse_to_candidates_streaming(input_text)
        
        # LRU: 如果缓存已满，淘汰最旧的
        if len(self._candidates_cache) >= self._candidates_cache_max_size:
            oldest_hash = self._candidates_cache_order.pop(0)
            del self._candidates_cache[oldest_hash]
        
        self._candidates_cache[text_hash] = candidates
        self._candidates_cache_order.append(text_hash)
        return candidates

    # ─────────── 时间预算管理 ───────────

    def _start_time_budget(self, budget_sec: float = None):
        if budget_sec is not None:
            self._time_budget_sec = budget_sec
        self._budget_start_time = time.perf_counter()
        self._budget_expired = False

    def _check_time_budget(self) -> bool:
        """P2修复: 0.8s安全余量，剩余<0.8s时强制返回"""
        if self._budget_start_time is None:
            return True
        remaining = self._time_budget_sec - (time.perf_counter() - self._budget_start_time)
        if remaining <= 0.8:  # P2修复: 从0改为0.8s安全余量
            self._budget_expired = True
            return False
        return True

    def _time_budget_remaining(self) -> float:
        if self._budget_start_time is None:
            return self._time_budget_sec
        return max(0.0, self._time_budget_sec - (time.perf_counter() - self._budget_start_time))

    # ─────────── 权重自适应 ───────────

    def _sliding_window_expand(self, w_score_actual: float):
        margin = 0.05
        hit_upper = w_score_actual >= self.w_score_max - margin
        hit_lower = w_score_actual <= self.w_score_min + margin

        if hit_upper:
            old_max = self.w_score_max
            self.w_score_max = min(0.98, self.w_score_max + 0.15)
            self.w_score_min = max(0.20, self.w_score_max - 0.60)
            self.evolution_logs.append(
                "> [META_ADAPT] Sliding Window 上扩: [{:.2f}, {:.2f}] → [{:.2f}, {:.2f}] (最优撞上界{:.2f})".format(
                    self.w_score_min, old_max, self.w_score_min, self.w_score_max, w_score_actual
                )
            )

        if hit_lower:
            old_min = self.w_score_min
            self.w_score_min = max(0.10, self.w_score_min - 0.15)
            self.w_score_max = min(0.95, self.w_score_min + 0.60)
            self.evolution_logs.append(
                "> [META_ADAPT] Sliding Window 下扩: [{:.2f}, {:.2f}] → [{:.2f}, {:.2f}] (最优撞下界{:.2f})".format(
                    old_min, self.w_score_max, self.w_score_min, self.w_score_max, w_score_actual
                )
            )

        if not hit_upper and not hit_lower:
            center = (self.w_score_min + self.w_score_max) / 2
            pull = (w_score_actual - center) * 0.3
            new_min = self.w_score_min + pull
            new_max = self.w_score_max + pull
            if new_max <= 0.98 and new_min >= 0.10:
                self.w_score_min = round(max(0.10, new_min), 2)
                self.w_score_max = round(min(0.98, new_max), 2)

        self.w_score_min = round(self.w_score_min, 2)
        self.w_score_max = round(self.w_score_max, 2)

    def _adaptive_epsilon(self) -> float:
        golden_count = len(self.golden_strategies)
        total_runs = self.evolution_metrics.get("total_runs", 0)
        if total_runs < 5:
            return MAX_EPSILON
        if golden_count >= 5:
            decay = max(0.0, 1.0 - golden_count * 0.03)
            return max(MIN_EPSILON, BASE_EPSILON * decay)
        recent = self.evolution_metrics.get("utility_history", [])[-5:]
        if len(recent) >= 3:
            trend = recent[-1] - recent[0]
            if trend < 0:
                return min(MAX_EPSILON, BASE_EPSILON * 1.5)
        return BASE_EPSILON

    # ─────────── 历史记忆检索 ───────────

    def _feature_distance(self, state_a: dict, state_b: dict) -> float:
        keys = ["density", "avg_will", "avg_score", "task_count", "courier_count"]
        dist = 0.0
        for k in keys:
            va = state_a.get(k, 0)
            vb = state_b.get(k, 0)
            denom = max(abs(va), abs(vb), 1.0)
            dist += abs(va - vb) / denom
        return dist / len(keys)

    def _find_similar_from_history(self, state: dict, top_k: int = 3) -> list:
        if not self.history:
            return []
        scored = []
        for h in self.history:
            h_state = h.get("state", {})
            dist = self._feature_distance(state, h_state)
            utility = h.get("utility", 0)
            scored.append((dist, utility, h))
        scored.sort(key=lambda x: (x[0], -x[1]))
        return scored[:top_k]

    # ─────────── 感知层（P2缓存 + P3校验） ───────────

    def perceive(self, input_text: str) -> dict:
        features = extract_features(input_text)
        # P2修复: 使用缓存的candidates
        candidates = self._get_candidates(input_text)
        features["_candidate_count"] = len(candidates)
        # P0修复: 存储candidates和all_task_count供_compute_utility使用
        self._last_candidates = candidates
        self._last_all_task_count = features.get("task_count", 0)
        # P3修复: 数据一致性校验
        actual_task_count = len(set(t for ts, _, _, _, _ in candidates for t in ts.split(',')))
        if features.get("task_count", 0) != actual_task_count:
            self.evolution_logs.append(
                "> [META_VALIDATE] 任务数校验: 特征报告 {}, 实际 {}，以实际为准".format(
                    features.get("task_count", 0), actual_task_count
                )
            )
            features["task_count"] = actual_task_count
            self._last_all_task_count = actual_task_count
        self.last_state = features
        return features

    def _find_best_from_history(self, state: dict) -> dict:
        similar = self._find_similar_from_history(state, top_k=1)
        if similar and similar[0][0] < 0.3:
            return similar[0][2].get("action")
        if not self.history:
            return None
        best = None
        best_score = -1
        for h in self.history:
            h_state = h.get("state", {})
            h_utility = h.get("utility", 0)
            if h_state.get("density") == state.get("density") and h_utility > best_score:
                best_score = h_utility
                best = h.get("action")
        return best

    def _perturb_params(self, strategy: str, params: dict) -> dict:
        perturbed = dict(params)
        if strategy == "utility_density_greedy":
            delta = random.uniform(-0.05, 0.05)
            perturbed["w_score"] = round(
                min(self.w_score_max, max(self.w_score_min, params.get("w_score", 0.7) + delta)), 2
            )
            perturbed["w_will"] = round(1.0 - perturbed["w_score"], 2)
        elif strategy == "beam_search":
            delta = random.choice([-1, 0, 1])
            perturbed["beam_width"] = min(5, max(2, params.get("beam_width", 3) + delta))
        return perturbed

    def _build_system_prompt(self) -> str:
        return """# Role
You are an elite Operations Research Scientist and the Meta-Agent Brain of an autonomous dispatch system. Your sole objective is to minimize the Penalty Score for the Meituan Delivery Assignment problem under an absolute 10-second execution hard-limit.

# Scoring Function (CRITICAL)
Score = Σ(score × (2.0 - willingness)) + penalty × n_rejected
- score = total_score (delivery cost, lower is better)
- willingness = delivery probability (0-1)
- n_rejected = unassigned tasks
- penalty = 100 per rejected task

**Lower Score = Better.** You must choose strategies that minimize this Score.

# Core Philosophy (Safety & Speed)
1. **Safety First, Performance Second:** Any timeout results in 0 points. Monitor `remaining_time_budget`.
2. **Dynamic Strategy Routing:** You analyze the State and output a JSON configuration to trigger pre-compiled primitives.
3. **Defense in Depth:** Circuit breakers and time budget hard-stop are built-in.

# Available Arsenal (Primitives)
- `conflict_aware_greedy`: [Cost: ~0.05s] Absolute safety. Use when time is critical.
- `greedy_min_cost`: [Cost: ~0.05s] Minimum cost first. Use when avg_score is very high.
- `greedy_max_willingness`: [Cost: ~0.05s] Maximum willingness first. Use when avg_will is extremely low.
- `utility_density_greedy`: [Cost: ~0.1s] Highly tunable. Requires `w_score` and `w_will`.
- `hybrid_greedy`: [Cost: ~0.05s] Balances cost and coverage. Good default choice.
- `local_search_2opt`: [Cost: ~1.0s+] Powerful local optimizer. ONLY if `remaining_time_budget > 1.5s`.
- `beam_search`: [Cost: ~0.5s - 2.0s] Balance of exploration. ONLY if `remaining_time_budget > 1.0s`.

# Execution Protocol
1. **Perceive:** Analyze Data State.
2. **Check the Clock:** If < 1.0s remaining, FORBIDDEN to select `local_search_2opt` or `beam_search(width>3)`.
3. **Reflect:** Check Memory Log for past failures.
4. **Decide:** Output optimal strategy JSON.

# Strict Output Format
ONLY output a valid JSON object. No markdown, no explanations.
Example:
{"strategy": "hybrid_greedy", "params": {}}"""

    def _build_prompt(self, state: dict) -> str:
        remaining_time = self._time_budget_remaining()
        circuit_breaker_status = 'Triggered (Be extremely fast)' if self._llm_circuit_breaker else 'Normal'
        time_critical = remaining_time < 1.0

        recent_history = self.history[-3:] if self.history else []
        history_text = (
            json.dumps(recent_history, ensure_ascii=False)
            if recent_history
            else "No history"
        )

        golden_text = ""
        if self.golden_strategies:
            golden_items = list(self.golden_strategies.items())[:3]
            golden_text = "\n".join(
                f"  Golden: {k} -> util={v['utility']}"
                for k, v in golden_items
            )

        summary_text = ""
        if self.experience_summary:
            summary_text = f"\nExperience Summary:\n  {self.experience_summary}\n"

        time_warning = ""
        if time_critical:
            time_warning = "\n*** CRITICAL: Less than 1.0s remaining! FORBIDDEN to select local_search_2opt or beam_search(width>3) ***\n"

        return f"""Current Survival Status:
- Remaining Time Budget: {remaining_time:.2f} seconds
- LLM Circuit Breaker: {circuit_breaker_status}
{time_warning}
Current Data State:
- Task Density: {state.get('density', 'N/A')}
- Average Willingness: {state.get('avg_will', 'N/A')}
- Average Cost (score): {state.get('avg_score', 'N/A')}
- Graph Cohesiveness: {state.get('cohesiveness_score', 'Unknown')}
- Task Count: {state.get('task_count', 'N/A')}
- Courier Count: {state.get('courier_count', 'N/A')}
- Candidate Count: {state.get('_candidate_count', 'N/A')}
- Max Tasks Per Row: {state.get('max_tasks_per_row', 'N/A')}
{summary_text}
History & Golden Strategies:
{history_text}
{golden_text if golden_text else "  (No golden strategies yet)"}

Weight Window: w_score in [{self.w_score_min}, {self.w_score_max}]

Task: Based on the time remaining and the data state, output the next optimal strategy JSON to minimize penalty score."""

    # ─────────── P1修复: LLM响应解析增强 ───────────

    def _parse_llm_response(self, content: str) -> dict:
        """P1修复: 增强JSON解析，支持markdown包裹、多余文本"""
        content = content.strip()
        # 去掉markdown包裹
        content = content.strip('```json').strip('```').strip()
        # P1修复: 正则提取JSON块
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

    LLM_CIRCUIT_WINDOW_SEC = 30
    LLM_CIRCUIT_THRESHOLD = 3
    LLM_CIRCUIT_RECOVERY_SEC = 60

    def _check_circuit_breaker(self) -> bool:
        now = time.time()
        self._llm_timeout_timestamps = [
            ts for ts in self._llm_timeout_timestamps
            if now - ts < self.LLM_CIRCUIT_WINDOW_SEC
        ]
        if len(self._llm_timeout_timestamps) >= self.LLM_CIRCUIT_THRESHOLD:
            if self._llm_circuit_breaker and self._llm_circuit_triggered_at is not None:
                if now - self._llm_circuit_triggered_at >= self.LLM_CIRCUIT_RECOVERY_SEC:
                    self._llm_circuit_breaker = False
                    self._llm_circuit_triggered_at = None
                    self._llm_timeout_timestamps = []
                    self._llm_timeout_count = 0
                    self.evolution_logs.append(
                        "[META_CIRCUIT_BREAKER] 熔断恢复时间已过，自动恢复 LLM 调用"
                    )
                    return False
            if not self._llm_circuit_breaker:
                self._llm_circuit_breaker = True
                self._llm_circuit_triggered_at = now
                self.evolution_logs.append(
                    f"[META_CIRCUIT_BREAKER] {self.LLM_CIRCUIT_WINDOW_SEC}s 内 {self.LLM_CIRCUIT_THRESHOLD} 次超时，熔断器触发！"
                )
            return True
        if len(self._llm_timeout_timestamps) == 0 and self._llm_circuit_breaker:
            self._llm_circuit_breaker = False
            self._llm_circuit_triggered_at = None
            self._llm_timeout_count = 0
            self.evolution_logs.append(
                "[META_CIRCUIT_BREAKER] 时间窗口内无超时记录，自动恢复 LLM 调用"
            )
        return self._llm_circuit_breaker

    def _call_deepseek(self, system_prompt: str, user_prompt: str) -> dict:
        import requests

        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions"
        )
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            raise ValueError("No DeepSeek API key")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 256,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(base_url, headers=headers, json=payload, timeout=8.0)
            resp.raise_for_status()
            data = resp.json()
        except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
            self._llm_timeout_count += 1
            self._llm_timeout_timestamps.append(time.time())
            self._check_circuit_breaker()
            raise
        except Exception:
            raise

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError("Empty DeepSeek response")
        if len(content) < 10 or "strategy" not in content:
            raise ValueError("Invalid response: missing strategy")

        self._llm_timeout_count = 0
        return self._parse_llm_response(content)

    def _llm_decision(self, state: dict) -> dict:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_prompt(state)

        try:
            decision = self._call_deepseek(system_prompt, user_prompt)
            self.evolution_logs.append("[META_AGENT] DeepSeek 策略决策成功 ✓")
            return decision
        except Exception as e:
            self.evolution_logs.append(
                f"[META_AGENT] DeepSeek 不可用 ({str(e)[:40]})，启动规则降级链路"
            )
            raise

    def _random_explore(self) -> dict:
        strategy = random.choice(ALL_STRATEGIES)
        params = {}
        if strategy == "utility_density_greedy":
            w_score = round(random.uniform(self.w_score_min, self.w_score_max), 2)
            params = {"w_score": w_score, "w_will": round(1.0 - w_score, 2)}
        elif strategy == "beam_search":
            params = {"beam_width": random.randint(2, 5)}
        elif strategy == "hybrid_greedy":
            params = {}
        self.evolution_logs.append(
            f"[META_EXPLORE] ε-greedy 随机探索 → {strategy} {params}"
        )
        return {"strategy": strategy, "params": params}

    def _fallback_decision(self, state: dict) -> dict:
        strategy_id = route_strategy(state)
        strategy_map = {
            0: "conflict_aware_greedy",
            1: "greedy_min_cost",
            2: "utility_density_greedy",
            3: "beam_search_adaptive",
            4: "multi_neighborhood_search",
        }
        strategy = strategy_map.get(strategy_id, "conflict_aware_greedy")
        params = {}
        if strategy == "utility_density_greedy":
            avg_will = state.get("avg_will", 0.5)
            mid = (self.w_score_min + self.w_score_max) / 2
            params = (
                {"w_score": round(mid, 2), "w_will": round(1.0 - mid, 2)}
                if avg_will < 0.3
                else {"w_score": round(mid + 0.05, 2), "w_will": round(1.0 - mid - 0.05, 2)}
            )
        elif strategy == "beam_search":
            params = {"beam_width": 4}
        return {"strategy": strategy, "params": params}

    def make_decision(self, state: dict, use_llm: bool = True, deterministic_mode: bool = False) -> dict:
        # P3修复: 零LLM模式强制跳过LLM调用
        if self._zero_llm_mode:
            use_llm = False
            self.evolution_logs.append(
                "[META_ZERO_LLM] 零LLM模式激活，直接使用预训练Golden策略库"
            )
        state_key = json.dumps(
            {k: state.get(k) for k in ["density", "avg_will", "task_count", "courier_count",
                                         "cohesiveness_score", "max_tasks_per_row"]},
            sort_keys=True,
        )

        if state_key in self.golden_strategies:
            golden = self.golden_strategies[state_key]
            if golden["utility"] >= (self.threshold or 0):
                if not deterministic_mode and random.random() < GOLDEN_OVERRIDE_EPSILON:
                    self.last_hit_memory = False
                    self.evolution_logs.append(
                        f"[META_EXPLORE] Golden Strategy 存在但 ε-override={GOLDEN_OVERRIDE_EPSILON} 触发强制探索——防止局部最优陷阱"
                    )
                    return self._random_explore()

                self.last_hit_memory = True
                self.evolution_logs.append(
                    f"[META_AGENT] Golden Strategy 命中 → {golden['action'].get('strategy')} "
                    f"(效用: {golden['utility']:.0f}, 跳过LLM)"
                )
                return golden["action"]

        circuit_breaker_active = self._check_circuit_breaker()
        if use_llm and not circuit_breaker_active and not self._zero_llm_mode:
            try:
                return self._llm_decision(state)
            except Exception as e:
                # P3修复: 如果是API不可用错误，启用零LLM模式
                if "API key" in str(e) or "DeepSeek" in str(e) or "timeout" in str(e).lower():
                    self._zero_llm_mode = True
                    self.evolution_logs.append(
                        f"[META_ZERO_LLM] DeepSeek API不可用 ({str(e)[:40]})，启用零LLM模式"
                    )
                pass
        elif circuit_breaker_active or self._zero_llm_mode:
            reason = "熔断器" if circuit_breaker_active else "零LLM模式"
            self.evolution_logs.append(
                f"[META_{reason.upper()}] {reason}激活，跳过 LLM 直接走规则降级"
            )

        memory_action = self._find_best_from_history(state)
        if memory_action:
            self.last_hit_memory = True
            perturbed = self._perturb_params(
                memory_action.get("strategy", "conflict_aware_greedy"),
                memory_action.get("params", {}),
            )
            self.evolution_logs.append(
                f"[META_AGENT] 历史记忆命中 → 参数微调: {perturbed}"
            )
            return perturbed

        if not deterministic_mode:
            epsilon = self._adaptive_epsilon()
            if random.random() < epsilon:
                self.last_hit_memory = False
                self.evolution_logs.append(
                    f"[META_EXPLORE] 自适应 ε={epsilon:.3f}，触发探索"
                )
                return self._random_explore()

        self.last_hit_memory = False
        result = self._fallback_decision(state)
        self.evolution_logs.append(
            f"[META_AGENT] 决策树路由 → {result['strategy']}"
        )
        return result

    # ─────────── 执行层（P2缓存） ───────────

    def execute(self, input_text: str, decision: dict) -> tuple:
        strategy_name = decision.get("strategy", "conflict_aware_greedy")
        params = decision.get("params", {})
        candidates = self._get_candidates(input_text)

        if not candidates:
            return [], 0, 0

        primitive = PRIMITIVES_MAP.get(strategy_name, conflict_aware_greedy)
        remaining = self._time_budget_remaining()

        try:
            if strategy_name in ("utility_density_greedy", "beam_search", "beam_search_adaptive"):
                result = primitive(candidates, **params)
            elif strategy_name in ("simulated_annealing", "grasp"):
                result = primitive(candidates, time_budget_remaining=remaining)
            elif strategy_name in ("local_search_2opt", "multi_neighborhood_search",
                                     "pairwise_swap_optimizer", "merge_optimizer"):
                initial = conflict_aware_greedy(candidates)
                if strategy_name == "local_search_2opt":
                    result = primitive(candidates, initial, time_budget_remaining=remaining)
                else:
                    result = primitive(candidates, initial, time_budget_remaining=remaining)
            elif strategy_name == "hybrid_greedy":
                result = primitive(candidates)
            elif strategy_name == "priority_greedy":
                result = primitive(candidates)
            else:
                result = primitive(candidates)

            return result, 0, 0

        except Exception:
            result = conflict_aware_greedy(candidates)
            return result, 0, 0

    # ─────────── 梯度搜索（P0评分对齐） ───────────

    def _weight_gradient_search(
        self, input_text: str, base_decision: dict, base_utility: float
    ) -> tuple:
        strategy_name = base_decision.get("strategy", "")
        if strategy_name != "utility_density_greedy":
            return base_decision, base_utility

        base_w_score = base_decision.get("params", {}).get("w_score", 0.7)
        candidates = self._get_candidates(input_text)
        if not candidates:
            return base_decision, base_utility

        best_decision = base_decision
        best_utility = base_utility

        self.evolution_logs.append(
            "> [META_EVOLUTION] 启动权重梯度微搜索 (基准 w_score={:.2f}, 窗口=[{:.2f}, {:.2f}], 效用={:.0f})...".format(
                base_w_score, self.w_score_min, self.w_score_max, base_utility
            )
        )

        for delta in WEIGHT_SEARCH_GRID:
            if delta == 0:
                continue
            new_w_score = round(min(self.w_score_max, max(self.w_score_min, base_w_score + delta)), 2)
            new_w_will = round(1.0 - new_w_score, 2)
            new_decision = {
                "strategy": "utility_density_greedy",
                "params": {"w_score": new_w_score, "w_will": new_w_will},
            }

            try:
                result = utility_density_greedy(candidates, w_score=new_w_score, w_will=new_w_will)
                # P0修复: 使用真实评分函数
                new_utility = _compute_utility(result, candidates, self._last_all_task_count)
                if new_utility > best_utility:
                    best_utility = new_utility
                    best_decision = new_decision
                    self.evolution_logs.append(
                        "[META_EVOLUTION] 梯度搜索命中 → w_score={:.2f}, "
                        "效用 {:.0f} → {:.0f} (Δ={:+.0f})".format(
                            new_w_score, base_utility, new_utility, new_utility - base_utility
                        )
                    )
            except Exception:
                pass

        if best_utility > base_utility:
            improvement = best_utility - base_utility
            self.evolution_logs.append(
                "[META_EVOLUTION] 权重梯度搜索完成 → 最优 w_score={:.2f}, "
                "效用提升 {:+.0f} ({:+.1f}%)".format(
                    best_decision['params']['w_score'], improvement, improvement / max(base_utility, 1) * 100
                )
            )
        else:
            self.evolution_logs.append(
                "[META_EVOLUTION] 权重梯度搜索完成 → 基准权重已是最优，无需调整"
            )

        return best_decision, best_utility

    # ─────────── 进化层（P3校验） ───────────

    def evolve(
        self,
        state: dict,
        action: dict,
        utility: float,
        courier_conflicts: int = 0,
        task_conflicts: int = 0,
    ):
        # P3修复: 校验utility非负
        if utility < 0:
            self.evolution_logs.append(
                f"[META_VALIDATE] 效用 {utility:.1f} 为负，可能存在评分异常"
            )

        record = {
            "state": {k: v for k, v in state.items() if not k.startswith("_")},
            "action": action,
            "utility": utility,
            "timestamp": time.time(),
        }
        self.history.append(record)
        self.last_action = action
        self._save_memory()

        state_key = json.dumps(
            {k: state.get(k) for k in ["density", "avg_will", "task_count", "courier_count",
                                         "cohesiveness_score", "max_tasks_per_row"]},
            sort_keys=True,
        )

        if (
            state_key not in self.golden_strategies
            or utility > self.golden_strategies[state_key]["utility"]
        ):
            prev = self.golden_strategies.get(state_key, {}).get("utility", 0)
            self.golden_strategies[state_key] = {
                "action": action,
                "utility": utility,
            }
            self._save_golden()
            self.evolution_logs.append(
                f"[META_EVOLUTION] Golden Strategy 更新：{action.get('strategy')} "
                f"(Utility: {utility:.1f}, 提升: {utility - prev:+.1f})"
            )

        if action.get("strategy") == "utility_density_greedy":
            actual_w_score = action.get("params", {}).get("w_score", 0.7)
            self._sliding_window_expand(actual_w_score)

        self.evolution_metrics["total_runs"] = self.evolution_metrics.get("total_runs", 0) + 1
        utility_history = self.evolution_metrics.get("utility_history", [])
        utility_history.append(utility)
        if len(utility_history) > 100:
            utility_history = utility_history[-100:]
        self.evolution_metrics["utility_history"] = utility_history
        best = self.evolution_metrics.get("best_utility", 0)
        if utility > best:
            self.evolution_metrics["best_utility"] = utility
        self._save_metrics()

        conflict_msg = ""
        if courier_conflicts > 0 or task_conflicts > 0:
            conflict_msg = (
                f" | 冲突审计: 运力冲突 {courier_conflicts} 次, "
                f"任务冲突 {task_conflicts} 次"
            )
            self.conflict_audit_log.append(
                {
                    "strategy": action.get("strategy"),
                    "courier_conflicts": courier_conflicts,
                    "task_conflicts": task_conflicts,
                    "utility": utility,
                }
            )

        if self.threshold is not None and utility < self.threshold:
            self.evolution_logs.append(
                f"[META_REFLECTION] 效用 {utility:.1f} 低于阈值 {self.threshold:.1f}，"
                f"策略 {action.get('strategy')} 可能不适用当前场景{conflict_msg}"
            )
            self._analyze_failure(
                state, action, utility, courier_conflicts, task_conflicts
            )
        else:
            self.evolution_logs.append(
                f"[META_EVOLUTION] 执行成功 — 策略: {action.get('strategy')}, "
                f"效用: {utility:.1f}{conflict_msg}"
            )

        if len(self.history) >= MEMORY_SUMMARY_THRESHOLD:
            self._summarize_memory()

    def _summarize_memory(self):
        if not self.history or len(self.history) < MEMORY_SUMMARY_THRESHOLD:
            return

        self.evolution_logs.append(
            f"[META_SUMMARY] 记忆库已达 {len(self.history)} 条，触发 LLM 经验摘要..."
        )

        try:
            top_records = sorted(self.history, key=lambda x: x.get("utility", 0), reverse=True)[:15]
            worst_records = sorted(self.history, key=lambda x: x.get("utility", 0))[:5]

            summary_prompt = f"""你是调度策略分析专家。请根据以下历史运行数据，总结出 200 字以内的调度策略常识。

最佳表现 (Top 15):
{json.dumps(top_records, ensure_ascii=False, indent=2)}

最差表现 (Worst 5):
{json.dumps(worst_records, ensure_ascii=False, indent=2)}

当前窗口: w_score ∈ [{self.w_score_min}, {self.w_score_max}]
Golden Strategies 数量: {len(self.golden_strategies)}

要求：
1. 用中文输出，200字以内
2. 总结哪些策略/参数组合在什么场景下表现最好
3. 哪些场景应该避免
4. 不要输出 JSON，直接输出纯文本"""

            summary = self._call_llm_summarizer(summary_prompt)
            if summary and len(summary) > 10:
                self.experience_summary = summary
                self._save_summary(summary)
                self.evolution_logs.append(
                    f"[META_SUMMARY] 经验摘要完成 ({len(summary)} 字): {summary[:100]}..."
                )

                kept_count = max(10, len(self.history) // 5)
                self.history = sorted(self.history, key=lambda x: x.get("utility", 0), reverse=True)[:kept_count]
                self._save_memory()
                self.evolution_logs.append(
                    f"[META_SUMMARY] 记忆库瘦身: {len(self.history)} 条 (保留 Top-{kept_count} 高效用记录)"
                )
        except Exception as e:
            self.evolution_logs.append(
                f"[META_SUMMARY] 摘要失败 ({str(e)[:40]})，执行规则瘦身备用方案"
            )
            self._fallback_prune_memory()

    def _call_llm_summarizer(self, user_prompt: str) -> str:
        import requests
        from dotenv import load_dotenv

        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            raise ValueError("No DeepSeek API key for summarization")

        system_prompt = "You are a dispatch strategy analysis expert. Summarize the following historical dispatch data into a concise strategy insight within 200 characters. Output pure text only, no JSON, no markdown. Focus on: which strategies/parameters work best in which scenarios, and which scenarios to avoid."

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 400,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(base_url, headers=headers, json=payload, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _fallback_prune_memory(self):
        before = len(self.history)
        self.history = sorted(self.history, key=lambda x: x.get("utility", 0), reverse=True)[:20]
        removed = before - len(self.history)
        self._save_memory()
        self.evolution_logs.append(
            f"[META_SUMMARY] 规则瘦身完成: 剔除 {removed} 条低效用记录, 保留 Top-20"
        )

    def _analyze_failure(
        self,
        state: dict,
        action: dict,
        utility: float,
        courier_conflicts: int = 0,
        task_conflicts: int = 0,
    ):
        reasons = []
        if state.get("density", 0) > 5.0:
            reasons.append("高密度场景")
        if state.get("avg_will", 0) < 0.25:
            reasons.append("低意愿度")
        if state.get("task_count", 0) > 30:
            reasons.append("大规模任务")
        if courier_conflicts > 10:
            reasons.append(f"运力冲突过高({courier_conflicts}次)")
        if task_conflicts > 10:
            reasons.append(f"任务冲突过高({task_conflicts}次)")
        if not reasons:
            reasons.append("未知原因")

        self.evolution_logs.append(
            f"[META_REFLECTION] 失败归因: {', '.join(reasons)} → "
            f"建议: 切换策略或调整参数"
        )

    # ─────────── 运行周期 ───────────

    def run_cycle(
        self, input_text: str, use_llm: bool = True
    ) -> tuple:
        state = self.perceive(input_text)
        decision = self.make_decision(state, use_llm=use_llm)
        solutions, courier_conflicts, task_conflicts = self.execute(
            input_text, decision
        )
        # P0修复: 使用真实评分函数
        utility = _compute_utility(solutions, self._last_candidates, self._last_all_task_count)
        self.evolve(state, decision, utility, courier_conflicts, task_conflicts)
        return solutions, self.evolution_logs.copy(), utility

    def run_cycle_no_llm(self, input_text: str) -> tuple:
        self._start_time_budget(8.5)

        self.evolution_logs = []
        self.evolution_logs.append(
            "[META_ZERO_LLM] 零LLM推理模式启动，时间预算: 8.5s"
        )

        state = self.perceive(input_text)

        decision, confidence = route_strategy_v3(state, self.golden_strategies)
        strategy_name = decision.get("strategy", "conflict_aware_greedy")

        self.evolution_logs.append(
            "[META_ZERO_LLM] 路由器选择策略: {} (置信度: {:.1f})".format(
                strategy_name, confidence
            )
        )

        if strategy_name == "utility_density_greedy":
            decision, _ = self._quick_gradient_search(
                input_text, decision, 0, grid=[-0.05, 0.05]
            )
            strategy_name = decision.get("strategy", strategy_name)

        candidates = self._last_candidates
        all_tc = self._last_all_task_count
        competing = [
            {"strategy": "greedy_min_cost", "params": {}},
            {"strategy": "conflict_aware_greedy", "params": {}},
        ]
        best_comp_score = float('inf')
        best_comp_choice = decision
        for comp in competing:
            if not self._check_time_budget():
                break
            if comp["strategy"] == strategy_name:
                continue
            try:
                comp_sol, _, _ = self.execute(input_text, comp)
                comp_score = compute_penalty_score(comp_sol, candidates, all_tc)
                if comp_score < best_comp_score:
                    best_comp_score = comp_score
                    best_comp_choice = comp
                    self.evolution_logs.append(
                        "[META_ZERO_LLM] 竞技发现更优策略: {} (Score {:.1f})".format(
                            comp["strategy"], comp_score
                        )
                    )
            except Exception:
                pass
        if best_comp_choice != decision:
            router_score = compute_penalty_score(
                self.execute(input_text, decision)[0], candidates, all_tc
            ) if self._check_time_budget() else float('inf')
            if best_comp_score < router_score:
                decision = best_comp_choice
                strategy_name = decision.get("strategy", strategy_name)
                self.evolution_logs.append(
                    "[META_ZERO_LLM] ★ 采用竞技更优策略: {} (Score {:.1f})".format(
                        strategy_name, best_comp_score
                    )
                )

        solutions, courier_conflicts, task_conflicts = self.execute(
            input_text, decision
        )

        if self._time_budget_remaining() > 1.5:
            self.evolution_logs.append(
                "[META_ZERO_LLM] 时间充裕，执行local_search_2opt精炼"
            )
            candidates = self._last_candidates
            improved = local_search_2opt(
                candidates, solutions,
                time_budget_remaining=self._time_budget_remaining()
            )
            solutions = validate_solution_v2(improved, candidates=candidates)
        else:
            self.evolution_logs.append(
                "[META_ZERO_LLM] 跳过精炼（时间不足）"
            )

        utility = _compute_utility(
            solutions, self._last_candidates, self._last_all_task_count
        )

        self.evolve(state, decision, utility, courier_conflicts, task_conflicts)

        self.evolution_logs.append(
            "[META_ZERO_LLM] 零LLM推理完成 — 策略: {}, 效用: {:.0f}".format(
                strategy_name, utility
            )
        )

        return solutions, self.evolution_logs.copy(), utility

    def _strategy_bakeoff_v2(self, input_text: str, state: dict, candidates: list,
                             all_task_count: int, time_budget_available: float) -> tuple:
        """
        P0: 两级策略精选 — 第一级快速筛选（6个baseline），第二级精细优化（top2 + 局部搜索）
        根据时间预算自动调整评估策略数量
        """
        results = []
        t_start = time.perf_counter()

        total_candidates = len(candidates)
        if time_budget_available < 1.0 or total_candidates > 5000:
            eval_strategies = ["conflict_aware_greedy", "greedy_min_cost", "hybrid_greedy"]
        elif time_budget_available < 2.5:
            eval_strategies = FAST_STRATEGIES[:4]
        else:
            eval_strategies = FAST_STRATEGIES[:]

        self.evolution_logs.append(
            "[META_BAKEOFF_V2] ═══ 两级策略精选启动，快速评估 {} 个策略 (时间预算 {:.2f}s) ═══".format(
                len(eval_strategies), time_budget_available
            )
        )

        for strat_name in eval_strategies:
            elapsed = time.perf_counter() - t_start
            if elapsed > time_budget_available * 0.70:
                self.evolution_logs.append(
                    "[META_BAKEOFF_V2] 时间预算耗尽，停止快速评估"
                )
                break

            try:
                decision = {"strategy": strat_name, "params": {}}
                if strat_name == "utility_density_greedy":
                    mid = (self.w_score_min + self.w_score_max) / 2
                    decision["params"] = {"w_score": round(mid, 2), "w_will": round(1.0 - mid, 2)}

                solutions, _, _ = self.execute(input_text, decision)
                utility = _compute_utility(solutions, candidates, all_task_count)
                real_score = UTILITY_OFFSET - utility
                results.append({
                    "strategy": strat_name,
                    "params": decision["params"],
                    "solutions": solutions,
                    "utility": utility,
                    "score": real_score,
                })
                self.evolution_logs.append(
                    "[META_BAKEOFF_V2] {:28s} → Score {:.1f} (Utility {:.0f})".format(
                        strat_name, real_score, utility
                    )
                )
            except Exception as e:
                self.evolution_logs.append(
                    "[META_BAKEOFF_V2] {} 执行失败: {}".format(strat_name, str(e)[:50])
                )

        if not results:
            fallback_sol = conflict_aware_greedy(candidates)
            fallback_utility = _compute_utility(fallback_sol, candidates, all_task_count)
            decision = {"strategy": "conflict_aware_greedy", "params": {}}
            return decision, fallback_sol, fallback_utility

        results.sort(key=lambda x: x["score"])

        best_from_fast = results[0]
        self.evolution_logs.append(
            "[META_BAKEOFF_V2] ★ 快速评估最优: {} → Score {:.1f}".format(
                best_from_fast["strategy"], best_from_fast["score"]
            )
        )

        elapsed = time.perf_counter() - t_start
        remaining_for_heavy = time_budget_available - elapsed

        if remaining_for_heavy > 1.5 and total_candidates <= 10000:
            top2_strategies = results[:2]
            heavy_results = []

            for strat in HEAVY_STRATEGIES:
                if time.perf_counter() - t_start > time_budget_available * 0.80:
                    break

                try:
                    decision = {"strategy": strat, "params": {}}
                    solutions, _, _ = self.execute(input_text, decision)
                    utility = _compute_utility(solutions, candidates, all_task_count)
                    real_score = UTILITY_OFFSET - utility
                    heavy_results.append({
                        "strategy": strat,
                        "params": {},
                        "solutions": solutions,
                        "utility": utility,
                        "score": real_score,
                    })
                    self.evolution_logs.append(
                        "[META_BAKEOFF_V2] 精细策略 {:22s} → Score {:.1f}".format(
                            strat, real_score
                        )
                    )
                except Exception as e:
                    self.evolution_logs.append(
                        "[META_BAKEOFF_V2] {} 执行失败: {}".format(strat, str(e)[:50])
                    )

            results.extend(heavy_results)
            results.sort(key=lambda x: x["score"])

        best = results[0]
        best_solutions = best["solutions"]
        best_utility = best["utility"]

        if remaining_for_heavy > 1.0 and best_solutions:
            refined_sol = best_solutions

            for ls_name in ["multi_neighborhood_search"]:
                if time.perf_counter() - t_start > time_budget_available * 0.88:
                    break
                try:
                    ls_remaining = time_budget_available - (time.perf_counter() - t_start)
                    ls_decision = {"strategy": ls_name, "params": {}}
                    refined = multi_neighborhood_search(
                        candidates, refined_sol,
                        time_budget_remaining=ls_remaining * 0.8
                    )
                    refined_utility = _compute_utility(refined, candidates, all_task_count)
                    if refined_utility > best_utility:
                        refined_sol = refined
                        best_utility = refined_utility
                        best = {"strategy": ls_name, "params": {}, "solutions": refined,
                                "utility": refined_utility, "score": UTILITY_OFFSET - refined_utility}
                        self.evolution_logs.append(
                            "[META_BAKEOFF_V2] 局部搜索精炼 → Score {:.1f} (↓{:+.1f})".format(
                                best["score"], best["score"] - results[0]["score"]
                            )
                        )
                except Exception as e:
                    self.evolution_logs.append(
                        "[META_BAKEOFF_V2] 局部搜索失败: {}".format(str(e)[:50])
                    )

        self.evolution_logs.append(
            "[META_BAKEOFF_V2] 精选完成 → 最终策略: {}, Score {:.1f}".format(
                best["strategy"], best["score"]
            )
        )

        decision = {"strategy": best["strategy"], "params": best.get("params", {})}
        return decision, best["solutions"], best["utility"]


    def _adaptive_evolution_rounds(self, state: dict, candidates_count: int,
                                     time_remaining: float) -> int:
        """
        P0: 自适应进化轮次 — 根据数据规模和剩余时间动态决定 max_rounds
        小数据 + 多时间 → 更多轮次探索
        大数据 + 少时间 → 减少轮次保证执行
        """
        if time_remaining < 2.0:
            return 1
        if candidates_count < 200:
            return min(MAX_ROUNDS, max(MIN_ROUNDS, int(time_remaining / 0.8)))
        if candidates_count < 1000:
            return min(MAX_ROUNDS - 1, max(MIN_ROUNDS, int(time_remaining / 1.2)))
        if candidates_count < 5000:
            return BASE_ROUNDS
        return MIN_ROUNDS


    def run_evolution_cycle(
            self, input_text: str, max_rounds: int = None, use_llm: bool = True,
            time_budget_sec: float = None
        ) -> tuple:
        """
        v5.0: 自适应进化循环
        - max_rounds=None 时自动根据数据规模和时间预算决定
        - 第一轮使用 _strategy_bakeoff_v2 两级精选
        - 后续轮次做梯度搜索 + 策略探索
        """
        self._start_time_budget(time_budget_sec)
        best_solutions = []
        best_utility = 0
        best_decision = None
        all_evolution_logs = []

        state = self.perceive(input_text)
        candidates_count = len(self._last_candidates) if self._last_candidates else 0
        remaining = self._time_budget_remaining()

        if max_rounds is None:
            max_rounds = self._adaptive_evolution_rounds(state, candidates_count, remaining)

        all_evolution_logs.append(
            "> [META_EVOLUTION] ═══════════════════════════════════════════"
        )
        all_evolution_logs.append(
            "> [META_EVOLUTION] v5.0 自适应进化引擎启动 | 轮次: {} (自适应) | 预算: {:.1f}s | 窗口: [{:.2f}, {:.2f}]".format(
                max_rounds, self._time_budget_sec, self.w_score_min, self.w_score_max
            )
        )
        all_evolution_logs.append(
            "> [META_EVOLUTION] ═══════════════════════════════════════════"
        )

        for round_idx in range(max_rounds):
            if not self._check_time_budget():
                all_evolution_logs.append(
                    "> [META_HARDSTOP] ⚠ 时间预算耗尽 ({:.1f}s)，返回当前最优解".format(
                        self._time_budget_sec
                    )
                )
                break

            round_label = round_idx + 1
            remaining = self._time_budget_remaining()
            all_evolution_logs.append(
                "> [META_EVOLUTION] ── 进化轮次 {}/{} (剩余 {:.2f}s) ──".format(
                    round_label, max_rounds, remaining
                )
            )

            self.evolution_logs = []

            if not self._check_time_budget():
                break

            candidates = self._last_candidates
            all_task_count = self._last_all_task_count

            if round_idx == 0:
                bakeoff_budget = remaining * 0.55
                decision, solutions, utility = self._strategy_bakeoff_v2(
                    input_text, state, candidates, all_task_count, bakeoff_budget
                )
                all_evolution_logs.extend(self.evolution_logs)
                all_evolution_logs.append(
                    "> [META_EVOLUTION] 轮次 {}/{} 完成 — 策略: {}, Score: {:.1f}".format(
                        round_label, max_rounds,
                        decision.get("strategy") if decision else "N/A",
                        UTILITY_OFFSET - utility
                    )
                )

                if utility > 0:
                    best_utility = utility
                    best_solutions = solutions
                    best_decision = decision
                    all_evolution_logs.append(
                        "> [META_EVOLUTION] ★ 新全局最优 Score: {:.1f}".format(
                            UTILITY_OFFSET - best_utility
                        )
                    )
                continue

            prev_utility = best_utility

            if best_decision and best_decision.get("strategy") == "utility_density_greedy":
                remaining_budget = self._time_budget_remaining()
                if remaining_budget < 0.5:
                    decision, gradient_utility = self._quick_gradient_search(
                        input_text, best_decision, prev_utility, [-0.05, 0.05]
                    )
                else:
                    decision, gradient_utility = self._weight_gradient_search(
                        input_text, best_decision, prev_utility
                    )

                if gradient_utility > prev_utility:
                    all_evolution_logs.append(
                        "> [META_EVOLUTION] 梯度搜索改善成功"
                    )
                else:
                    all_evolution_logs.append(
                        "> [META_REFLECTION] 梯度搜索无改善，尝试策略切换..."
                    )
                    epsilon = self._adaptive_epsilon()
                    if random.random() < epsilon + 0.1:
                        decision = self._random_explore()
                    else:
                        excluded = {best_decision.get("strategy")} if best_decision else set()
                        remaining_strats = [s for s in ALL_STRATEGIES if s not in excluded]
                        if remaining_strats:
                            alt_strategy = random.choice(remaining_strats)
                            params = {}
                            if alt_strategy == "utility_density_greedy":
                                w_score = round(random.uniform(self.w_score_min, self.w_score_max), 2)
                                params = {"w_score": w_score, "w_will": round(1.0 - w_score, 2)}
                            elif alt_strategy == "beam_search_adaptive":
                                params = {"beam_width_base": random.randint(2, 5)}
                            decision = {"strategy": alt_strategy, "params": params}
                        else:
                            decision = self._fallback_decision(state)
            else:
                decision = self.make_decision(state, use_llm=use_llm)

            if not self._check_time_budget():
                break

            solutions, _, _ = self.execute(input_text, decision)
            utility = _compute_utility(solutions, self._last_candidates, self._last_all_task_count)

            all_evolution_logs.extend(self.evolution_logs)
            all_evolution_logs.append(
                "> [META_EVOLUTION] 轮次 {}/{} 完成 — 策略: {}, Score: {:.1f}".format(
                    round_label, max_rounds, decision.get("strategy"), UTILITY_OFFSET - utility
                )
            )

            if utility > best_utility:
                best_utility = utility
                best_solutions = solutions
                best_decision = decision
                all_evolution_logs.append(
                    "> [META_EVOLUTION] ★ 新全局最优 Score: {:.1f}".format(
                        UTILITY_OFFSET - best_utility
                    )
                )

            self.evolve(state, decision, utility, 0, 0)

            if self.threshold is not None and best_utility >= self.threshold and round_idx > 1:
                all_evolution_logs.append(
                    "> [META_EVOLUTION] 效用已达阈值，提前终止进化"
                )
                break

        if best_solutions:
            best_solutions = validate_solution_v2(best_solutions, candidates=None, all_tasks=None)

        final_score = UTILITY_OFFSET - best_utility
        all_evolution_logs.append(
            "> [META_EVOLUTION] ═══════════════════════════════════════════"
        )
        all_evolution_logs.append(
            "> [META_EVOLUTION] 进化终止 — 轮次: {}, 最优Score: {:.1f}, 策略: {}".format(
                max_rounds, final_score,
                best_decision.get("strategy") if best_decision else "N/A"
            )
        )
        all_evolution_logs.append(
            "> [META_EVOLUTION] ═══════════════════════════════════════════"
        )

        self.evolution_metrics["total_evolutions"] = self.evolution_metrics.get("total_evolutions", 0) + 1
        self._save_metrics()

        self._llm_circuit_breaker = False
        self._llm_timeout_count = 0

        return best_solutions, all_evolution_logs, best_utility

    def _quick_gradient_search(
        self, input_text: str, base_decision: dict, base_utility: float, grid: list
    ) -> tuple:
        strategy_name = base_decision.get("strategy", "")
        if strategy_name != "utility_density_greedy":
            return base_decision, base_utility

        base_w_score = base_decision.get("params", {}).get("w_score", 0.7)
        candidates = self._get_candidates(input_text)
        if not candidates:
            return base_decision, base_utility

        best_decision = base_decision
        best_utility = base_utility

        self.evolution_logs.append(
            "> [META_EVOLUTION] 时间紧迫，启动快速梯度搜索..."
        )

        for delta in grid:
            new_w_score = round(min(self.w_score_max, max(self.w_score_min, base_w_score + delta)), 2)
            new_w_will = round(1.0 - new_w_score, 2)
            new_decision = {
                "strategy": "utility_density_greedy",
                "params": {"w_score": new_w_score, "w_will": new_w_will},
            }
            try:
                result = utility_density_greedy(candidates, w_score=new_w_score, w_will=new_w_will)
                # P0修复: 使用真实评分函数
                new_utility = _compute_utility(result, candidates, self._last_all_task_count)
                if new_utility > best_utility:
                    best_utility = new_utility
                    best_decision = new_decision
                    self.evolution_logs.append(
                        "[META_EVOLUTION] 快速搜索命中 → w_score={:.2f}, 效用 Δ={:+.0f}".format(
                            new_w_score, new_utility - base_utility
                        )
                    )
            except Exception:
                pass

        return best_decision, best_utility

    def prune_bad_memories(self, min_utility: float) -> int:
        before = len(self.history)
        self.history = [
            h for h in self.history if h.get("utility", 0) >= min_utility
        ]
        removed = before - len(self.history)
        self._save_memory()
        self.evolution_logs.append(
            f"[TRAINER] 驯兽师剔除低效用记忆: {removed} 条 (阈值={min_utility})"
        )
        return removed

    def inject_memory(self, state: dict, action: dict, utility: float):
        record = {"state": state, "action": action, "utility": utility}
        self.history.append(record)
        self._save_memory()

        state_key = json.dumps(
            {k: state.get(k) for k in ["density", "avg_will", "task_count", "courier_count",
                                         "cohesiveness_score", "max_tasks_per_row"]},
            sort_keys=True,
        )
        if (
            state_key not in self.golden_strategies
            or utility > self.golden_strategies[state_key]["utility"]
        ):
            self.golden_strategies[state_key] = {
                "action": action,
                "utility": utility,
            }
            self._save_golden()

        if self.threshold is None or utility > self.threshold:
            self.threshold = utility * 0.8

        self.evolution_logs.append(
            f"[TRAINER] 驯兽师注入策略: {action.get('strategy')} (效用={utility})"
        )

    def get_memory_summary(self) -> dict:
        if not self.history:
            return {
                "total": 0,
                "avg_utility": 0,
                "best_utility": 0,
                "golden_count": 0,
                "strategies": {},
                "evolution_metrics": self.evolution_metrics,
                "experience_summary": self.experience_summary,
                "weight_window": [self.w_score_min, self.w_score_max],
            }

        utilities = [h.get("utility", 0) for h in self.history]
        strategy_counts = {}
        for h in self.history:
            s = h.get("action", {}).get("strategy", "unknown")
            strategy_counts[s] = strategy_counts.get(s, 0) + 1

        return {
            "total": len(self.history),
            "avg_utility": round(sum(utilities) / len(utilities), 1),
            "best_utility": max(utilities),
            "golden_count": len(self.golden_strategies),
            "strategies": strategy_counts,
            "conflict_audit": self.conflict_audit_log[-5:]
            if self.conflict_audit_log
            else [],
            "evolution_metrics": self.evolution_metrics,
            "experience_summary": self.experience_summary,
            "weight_window": [self.w_score_min, self.w_score_max],
        }

    def train(
        self, input_text: str, num_cycles: int = 100, use_llm: bool = True
    ) -> tuple:
        best_utility = 0
        best_solutions = []

        for cycle in range(num_cycles):
            solutions, logs, utility = self.run_cycle(
                input_text, use_llm=use_llm
            )

            if utility > best_utility:
                best_utility = utility
                best_solutions = solutions

            if (cycle + 1) % 10 == 0:
                self.evolution_logs.append(
                    f"[TRAIN] 批量进化 {cycle + 1}/{num_cycles} 轮, "
                    f"当前最佳效用: {best_utility}"
                )

        self.evolution_logs.append(
            f"[TRAIN] 批量进化完成: {num_cycles} 轮, 最佳效用: {best_utility}"
        )
        return best_solutions, best_utility


_global_agent = None


def get_agent() -> AutonomousAgent:
    global _global_agent
    if _global_agent is None:
        _global_agent = AutonomousAgent()
        if _global_agent.evolution_metrics:
            _global_agent.w_score_min = _global_agent.evolution_metrics.get(
                "w_score_min", DEFAULT_W_SCORE_MIN
            )
            _global_agent.w_score_max = _global_agent.evolution_metrics.get(
                "w_score_max", DEFAULT_W_SCORE_MAX
            )
    return _global_agent
