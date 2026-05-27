import os
import glob


def check_compliance(project_root: str) -> dict:
    """
    检查项目提交是否符合 Track 4 规范要求。

    参数:
        project_root: 项目根目录的绝对路径

    返回值:
        dict: 包含每项检查结果的字典，结构如下：
            {
                "requirement_name": {
                    "status": "PASS" | "FAIL" | "PARTIAL",
                    "detail": str,
                    "items": list | None
                },
                ...
                "overall": "PASS" | "FAIL"
            }
    """
    results = {}

    results["source_code"] = _check_source_code(project_root)
    results["report_pdf"] = _check_report_pdf(project_root)
    results["demo_video"] = _check_demo_video(project_root)
    results["agent_traces"] = _check_agent_traces(project_root)
    results["test_suite"] = _check_test_suite(project_root)

    all_statuses = [v["status"] for k, v in results.items()]
    results["overall"] = "PASS" if all(s == "PASS" for s in all_statuses) else "FAIL"

    return results


def _check_source_code(project_root: str) -> dict:
    """
    检查源代码目录是否存在。
    优先检查 source_code/，若不存在则检查 backend/ 是否包含关键文件。
    """
    source_code_path = os.path.join(project_root, "source_code")
    backend_path = os.path.join(project_root, "backend")

    key_files = [
        "agent.py",
        "features.py",
        os.path.join("primitives", "__init__.py"),
        "solver_engine.py",
        "main.py",
    ]

    if os.path.isdir(source_code_path):
        return {
            "status": "PASS",
            "detail": "source_code/ 目录存在",
            "items": [source_code_path],
        }

    if not os.path.isdir(backend_path):
        return {
            "status": "FAIL",
            "detail": "source_code/ 和 backend/ 目录均不存在",
            "items": [],
        }

    found = []
    missing = []
    for fname in key_files:
        fpath = os.path.join(backend_path, fname)
        if os.path.isfile(fpath):
            found.append(fname)
        else:
            missing.append(fname)

    if len(missing) == 0:
        return {
            "status": "PASS",
            "detail": "backend/ 目录存在且包含全部关键 Python 文件",
            "items": found,
        }
    elif len(found) >= 3:
        return {
            "status": "PARTIAL",
            "detail": f"backend/ 目录存在，但缺少关键文件: {', '.join(missing)}",
            "items": found,
        }
    else:
        return {
            "status": "FAIL",
            "detail": f"backend/ 目录存在，但关键文件大量缺失: {', '.join(missing)}",
            "items": found,
        }


def _check_report_pdf(project_root: str) -> dict:
    """
    递归搜索 report.pdf 文件。
    """
    pattern = os.path.join(project_root, "**", "report.pdf")
    matches = glob.glob(pattern, recursive=True)

    if matches:
        return {
            "status": "PASS",
            "detail": f"找到 {len(matches)} 个 report.pdf",
            "items": matches,
        }
    else:
        return {
            "status": "FAIL",
            "detail": "未找到 report.pdf（可在提交前创建）",
            "items": [],
        }


def _check_demo_video(project_root: str) -> dict:
    """
    递归搜索 demo.mp4 文件。
    """
    pattern = os.path.join(project_root, "**", "demo.mp4")
    matches = glob.glob(pattern, recursive=True)

    if matches:
        return {
            "status": "PASS",
            "detail": f"找到 {len(matches)} 个 demo.mp4",
            "items": matches,
        }
    else:
        return {
            "status": "FAIL",
            "detail": "未找到 demo.mp4（可在提交前创建）",
            "items": [],
        }


def _check_agent_traces(project_root: str) -> dict:
    """
    检查 agent_traces/ 目录是否存在并包含至少 2 个日志文件。
    若目录不存在，则检查 backend/ 下的轨迹类文件作为替代。
    """
    traces_path = os.path.join(project_root, "agent_traces")

    if os.path.isdir(traces_path):
        log_files = glob.glob(os.path.join(traces_path, "*"))
        accepted_exts = {".log", ".txt", ".json", ".jsonl", ".csv", ".yaml", ".yml"}
        trace_logs = [
            f for f in log_files
            if os.path.splitext(f)[1].lower() in accepted_exts
        ]
        if len(trace_logs) >= 2:
            return {
                "status": "PASS",
                "detail": f"agent_traces/ 包含 {len(trace_logs)} 个轨迹文件",
                "items": trace_logs,
            }
        else:
            return {
                "status": "FAIL",
                "detail": f"agent_traces/ 目录存在但仅包含 {len(trace_logs)} 个轨迹文件（需要 ≥2）",
                "items": trace_logs,
            }

    backend_path = os.path.join(project_root, "backend")
    surrogate_files = [
        "memory.json",
        "golden.json",
        "evolution_metrics.json",
        "experience_summary.txt",
    ]

    if not os.path.isdir(backend_path):
        return {
            "status": "FAIL",
            "detail": "agent_traces/ 目录和 backend/ 目录均不存在",
            "items": [],
        }

    found = []
    for fname in surrogate_files:
        fpath = os.path.join(backend_path, fname)
        if os.path.isfile(fpath):
            found.append(fname)

    if len(found) >= 2:
        return {
            "status": "PASS",
            "detail": f"agent_traces/ 目录不存在，但在 backend/ 中找到 {len(found)} 个替代轨迹文件",
            "items": found,
        }
    elif len(found) == 1:
        return {
            "status": "FAIL",
            "detail": f"agent_traces/ 目录不存在，backend/ 中仅找到 {len(found)} 个替代轨迹文件（需要 ≥2）",
            "items": found,
        }
    else:
        return {
            "status": "FAIL",
            "detail": "agent_traces/ 目录不存在，backend/ 中也未找到替代轨迹文件",
            "items": [],
        }


def _check_test_suite(project_root: str) -> dict:
    """
    检查自建测试套件是否包含至少 5 个测试用例。
    策略:
        1. 优先查找 test_harness.py，统计其中定义的场景/测试数
        2. 若不存在，查找 test_scenarios.py 等测试文件
        3. 若不存在，检查 test_data/ 目录
    """
    test_harness_path = os.path.join(project_root, "test_harness.py")
    if os.path.isfile(test_harness_path):
        scenario_count = _count_scenarios_in_file(test_harness_path)
        if scenario_count >= 5:
            return {
                "status": "PASS",
                "detail": f"test_harness.py 包含 {scenario_count} 个场景",
                "items": [test_harness_path],
            }
        else:
            return {
                "status": "FAIL",
                "detail": f"test_harness.py 仅包含 {scenario_count} 个场景（需要 ≥5）",
                "items": [test_harness_path],
            }

    backend_test_scenarios = os.path.join(project_root, "backend", "test_scenarios.py")
    if os.path.isfile(backend_test_scenarios):
        scenario_count = _count_scenarios_in_file(backend_test_scenarios)
        if scenario_count >= 5:
            return {
                "status": "PASS",
                "detail": f"backend/test_scenarios.py 包含 {scenario_count} 个场景",
                "items": [backend_test_scenarios],
            }
        else:
            return {
                "status": "FAIL",
                "detail": f"backend/test_scenarios.py 仅包含 {scenario_count} 个场景（需要 ≥5）",
                "items": [backend_test_scenarios],
            }

    test_data_path = os.path.join(project_root, "test_data")
    if os.path.isdir(test_data_path):
        test_files = glob.glob(os.path.join(test_data_path, "*"))
        if len(test_files) >= 5:
            return {
                "status": "PASS",
                "detail": f"test_data/ 目录包含 {len(test_files)} 个测试文件",
                "items": test_files,
            }
        else:
            return {
                "status": "FAIL",
                "detail": f"test_data/ 目录仅包含 {len(test_files)} 个测试文件（需要 ≥5）",
                "items": test_files,
            }

    return {
        "status": "FAIL",
        "detail": "未找到 test_harness.py、test_scenarios.py 或 test_data/ 目录",
        "items": [],
    }


def _count_scenarios_in_file(filepath: str) -> int:
    """
    统计 Python 测试文件中定义的 scenario/scene 数量。
    通过匹配 scenario_type 或 scenarios 列表中的字符串字面量来估算。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return 0

    count = 0

    import re

    scenario_list_match = re.search(
        r'scenarios\s*=\s*\[(.*?)\]', content, re.DOTALL
    )

    if scenario_list_match:
        body = scenario_list_match.group(1)
        strings = re.findall(r'[\"\']([^\"\']+)[\"\']', body)
        count = max(count, len(strings))

    if "scenario_type" in content or "scenario" in content.lower():
        string_literals = re.findall(
            r'[\"\']([a-z_]+)[\"\']\s*[:|,|\)|=]', content
        )
        scenario_keywords = [
            "default", "high_density", "low_willingness",
            "high_cost", "extreme_imbalance", "large_batch",
        ]
        matched = [s for s in string_literals if s in scenario_keywords]
        count = max(count, len(matched))

    return count


def print_compliance_report(results: dict):
    """
    格式化打印合规检查报告。

    参数:
        results: check_compliance() 返回的检查结果字典
    """
    SEPARATOR = "=" * 64
    SUB_SEP = "-" * 64

    print(SEPARATOR)
    print("  Track 4 项目提交合规检查报告")
    print(SEPARATOR)

    requirements = [
        ("source_code",  "1. 源代码目录"),
        ("report_pdf",   "2. 项目报告 (report.pdf)"),
        ("demo_video",   "3. 演示视频 (demo.mp4)"),
        ("agent_traces", "4. 智能体轨迹 (agent_traces/)"),
        ("test_suite",   "5. 自建测试套件 (≥5 用例)"),
    ]

    for key, label in requirements:
        entry = results.get(key, {})
        status = entry.get("status", "UNKNOWN")
        detail = entry.get("detail", "")
        items = entry.get("items", [])

        icon = _status_icon(status)

        print(f"\n  {icon} {label}")
        print(f"     状态: {status}")
        print(f"     说明: {detail}")

        if items:
            print(f"     相关文件 ({len(items)}):")
            for item in items:
                rel = _to_relative(item)
                print(f"       - {rel}")

    print(f"\n{SUB_SEP}")
    overall = results.get("overall", "FAIL")
    overall_icon = _status_icon(overall)
    print(f"  {overall_icon} 总体评估: {overall}")
    print(SEPARATOR)

    if overall == "FAIL":
        print("\n  [!] 存在未满足项，请在提交前完成以下操作：")
        for key, label in requirements:
            if results.get(key, {}).get("status") == "FAIL":
                print(f"       - {label}")
    else:
        print("\n  [OK] 所有检查项通过，项目符合 Track 4 提交规范。")


def _status_icon(status: str) -> str:
    mapping = {
        "PASS":    "[PASS]",
        "FAIL":    "[FAIL]",
        "PARTIAL": "[WARN]",
    }
    return mapping.get(status, "[????]")


def _to_relative(path: str) -> str:
    try:
        return os.path.relpath(path, os.getcwd())
    except ValueError:
        return path


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    report = check_compliance(project_root)
    print_compliance_report(report)