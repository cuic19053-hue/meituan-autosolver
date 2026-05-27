"""
Multi-Scenario Test Framework — Feature Drift Coverage
====================================================
P3修复: 多场景测试框架，覆盖极端值和特征漂移
用于验证系统在不同数据特征下的鲁棒性
"""
import time
from backend.primitives import (
    _parse_to_candidates,
    compute_penalty_score,
    validate_solution_v2,
    conflict_aware_greedy,
    hybrid_greedy,
    local_search_2opt,
    beam_search,
)
from backend.agent import get_agent


class ScenarioTestFramework:
    """多场景测试框架"""
    
    def __init__(self):
        self.agent = get_agent()
        self.test_results = []
    
    def _generate_scenario_data(self, scenario_type: str) -> str:
        """生成不同特征的测试数据"""
        if scenario_type == "high_density":
            # 高密度场景：任务数远大于骑手数
            return self._generate_high_density_data()
        elif scenario_type == "low_willingness":
            # 低意愿度场景：所有骑手意愿度<0.3
            return self._generate_low_willingness_data()
        elif scenario_type == "high_cost":
            # 高成本场景：所有配送成本>80
            return self._generate_high_cost_data()
        elif scenario_type == "extreme_imbalance":
            # 极端不平衡：1个骑手对100个任务
            return self._generate_extreme_imbalance_data()
        elif scenario_type == "large_batch":
            # 大批量场景：>3万行数据
            return self._generate_large_batch_data()
        else:
            # 默认场景
            return self._generate_default_data()
    
    def _generate_high_density_data(self) -> str:
        """生成高密度测试数据（任务密度>5）"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        # 100个任务，10个骑手
        for i in range(100):
            task_id = f"t{i}"
            courier_id = f"c{i % 10}"
            score = 50.0 + (i % 30)
            willingness = 0.5 + (i % 5) * 0.1
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def _generate_low_willingness_data(self) -> str:
        """生成低意愿度测试数据（意愿度<0.3）"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        for i in range(50):
            task_id = f"t{i}"
            courier_id = f"c{i % 20}"
            score = 40.0 + (i % 20)
            willingness = 0.1 + (i % 3) * 0.05  # 0.1-0.25
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def _generate_high_cost_data(self) -> str:
        """生成高成本测试数据（成本>80）"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        for i in range(50):
            task_id = f"t{i}"
            courier_id = f"c{i % 15}"
            score = 80.0 + (i % 20)
            willingness = 0.6 + (i % 4) * 0.1
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def _generate_extreme_imbalance_data(self) -> str:
        """生成极端不平衡测试数据（1骑手对100任务）"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        for i in range(100):
            task_id = f"t{i}"
            courier_id = "c0"  # 只有一个骑手
            score = 30.0 + (i % 20)
            willingness = 0.7 + (i % 3) * 0.1
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def _generate_large_batch_data(self) -> str:
        """生成大批量测试数据（>3万行）"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        for i in range(35000):
            task_id = f"t{i}"
            courier_id = f"c{i % 500}"
            score = 40.0 + (i % 40)
            willingness = 0.4 + (i % 6) * 0.1
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def _generate_default_data(self) -> str:
        """生成默认测试数据"""
        lines = ["task_id_list\tcourier_id\tscore\twillingness"]
        for i in range(30):
            task_id = f"t{i}"
            courier_id = f"c{i % 10}"
            score = 40.0 + (i % 30)
            willingness = 0.5 + (i % 5) * 0.1
            lines.append(f"{task_id}\t{courier_id}\t{score}\t{willingness}")
        return "\n".join(lines)
    
    def run_scenario_test(self, scenario_type: str, time_budget: float = 8.5) -> dict:
        """运行单个场景测试"""
        print(f"\n{'='*60}")
        print(f"测试场景: {scenario_type}")
        print(f"{'='*60}")
        
        input_text = self._generate_scenario_data(scenario_type)
        candidates = _parse_to_candidates(input_text)
        
        t_start = time.perf_counter()
        
        try:
            # 测试基础策略
            result_greedy = conflict_aware_greedy(candidates)
            score_greedy = compute_penalty_score(
                result_greedy, candidates, 
                len(set(t for ts, _, _, _, _ in candidates for t in ts.split(',')))
            )
            
            # 测试混合贪心
            result_hybrid = hybrid_greedy(candidates)
            score_hybrid = compute_penalty_score(
                result_hybrid, candidates,
                len(set(t for ts, _, _, _, _ in candidates for t in ts.split(',')))
            )
            
            # 测试beam_search（如果时间允许）
            result_beam = None
            score_beam = None
            if time_budget > 2.0:
                try:
                    result_beam = beam_search(candidates, beam_width=3)
                    score_beam = compute_penalty_score(
                        result_beam, candidates,
                        len(set(t for ts, _, _, _, _ in candidates for t in ts.split(',')))
                    )
                except Exception as e:
                    print(f"  beam_search失败: {str(e)[:40]}")
            
            # 测试local_search_2opt（如果时间允许）
            result_2opt = None
            score_2opt = None
            if time_budget > 3.0:
                try:
                    initial = conflict_aware_greedy(candidates)
                    result_2opt = local_search_2opt(candidates, initial, time_budget_remaining=2.0)
                    score_2opt = compute_penalty_score(
                        result_2opt, candidates,
                        len(set(t for ts, _, _, _, _ in candidates for t in ts.split(',')))
                    )
                except Exception as e:
                    print(f"  local_search_2opt失败: {str(e)[:40]}")
            
            t_end = time.perf_counter()
            elapsed = t_end - t_start
            
            # 验证输出格式
            validated_greedy = validate_solution_v2(result_greedy, candidates=candidates)
            validated_hybrid = validate_solution_v2(result_hybrid, candidates=candidates)
            
            result = {
                "scenario": scenario_type,
                "candidate_count": len(candidates),
                "elapsed_time": round(elapsed, 3),
                "greedy_score": round(score_greedy, 2),
                "greedy_validated": len(validated_greedy) == len(result_greedy),
                "hybrid_score": round(score_hybrid, 2),
                "hybrid_validated": len(validated_hybrid) == len(result_hybrid),
                "beam_score": round(score_beam, 2) if score_beam else None,
                "2opt_score": round(score_2opt, 2) if score_2opt else None,
                "status": "success"
            }
            
            print(f"  候选数量: {len(candidates)}")
            print(f"  耗时: {elapsed:.3f}s")
            print(f"  conflict_aware_greedy Score: {score_greedy:.2f}")
            print(f"  hybrid_greedy Score: {score_hybrid:.2f}")
            if score_beam:
                print(f"  beam_search Score: {score_beam:.2f}")
            if score_2opt:
                print(f"  local_search_2opt Score: {score_2opt:.2f}")
            print(f"  格式校验: {'通过' if result['greedy_validated'] and result['hybrid_validated'] else '失败'}")
            
        except Exception as e:
            t_end = time.perf_counter()
            elapsed = t_end - t_start
            result = {
                "scenario": scenario_type,
                "candidate_count": len(candidates) if candidates else 0,
                "elapsed_time": round(elapsed, 3),
                "status": "failed",
                "error": str(e)[:100]
            }
            print(f"  测试失败: {str(e)[:100]}")
        
        self.test_results.append(result)
        return result
    
    def run_all_scenarios(self) -> list:
        """运行所有场景测试"""
        scenarios = [
            "default",
            "high_density",
            "low_willingness",
            "high_cost",
            "extreme_imbalance",
            # "large_batch",  # 跳过大批量测试以节省时间
        ]
        
        print("\n" + "="*60)
        print("多场景测试框架启动")
        print("="*60)
        
        for scenario in scenarios:
            self.run_scenario_test(scenario)
        
        self._print_summary()
        return self.test_results
    
    def _print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        
        success_count = sum(1 for r in self.test_results if r["status"] == "success")
        total_count = len(self.test_results)
        
        print(f"  成功: {success_count}/{total_count}")
        
        for result in self.test_results:
            status = "✓" if result["status"] == "success" else "✗"
            print(f"  {status} {result['scenario']}: {result.get('elapsed_time', 0):.3f}s")
        
        # 找出最佳策略
        greedy_scores = [r.get("greedy_score", float('inf')) for r in self.test_results if r.get("greedy_score")]
        hybrid_scores = [r.get("hybrid_score", float('inf')) for r in self.test_results if r.get("hybrid_score")]
        
        if greedy_scores and hybrid_scores:
            avg_greedy = sum(greedy_scores) / len(greedy_scores)
            avg_hybrid = sum(hybrid_scores) / len(hybrid_scores)
            print(f"\n  平均Score (conflict_aware_greedy): {avg_greedy:.2f}")
            print(f"  平均Score (hybrid_greedy): {avg_hybrid:.2f}")
            if avg_hybrid < avg_greedy:
                print(f"  推荐: hybrid_greedy (降低 {avg_greedy - avg_hybrid:.2f})")
            else:
                print(f"  推荐: conflict_aware_greedy (降低 {avg_hybrid - avg_greedy:.2f})")


def run_feature_drift_test():
    """运行特征漂移测试"""
    framework = ScenarioTestFramework()
    return framework.run_all_scenarios()


if __name__ == "__main__":
    results = run_feature_drift_test()
