"""
美团项目 - 端到端 API 功能测试 + 边界场景测试
测试目标: http://localhost:8080
"""
import requests
import json
import time
import concurrent.futures
import sys

BASE_URL = 'http://localhost:8080'
PASS = 'PASS'
FAIL = 'FAIL'
SKIP = 'SKIP'

results = []

def record(test_id, name, status, detail=''):
    results.append({'id': test_id, 'name': name, 'status': status, 'detail': detail})
    tag = '[PASS]' if status == PASS else '[FAIL]' if status == FAIL else '[SKIP]'
    print(f"  {tag} {test_id}: {name} - {detail}")

# ============================================================
# Part 1.1: 完整求解流程
# ============================================================
print("\n" + "="*60)
print("Part 1.1: 完整求解流程 (map_init + execute_solve)")
print("="*60)

# Step 1: 获取地图数据
try:
    r1 = requests.get(f'{BASE_URL}/api/map_init', timeout=10)
    map_data = r1.json()
    nodes_count = len(map_data.get('nodes', []))
    links_count = len(map_data.get('links', []))
    record('1.1.1', 'GET /api/map_init 返回200', PASS if r1.status_code == 200 else FAIL, f'status={r1.status_code}')
    record('1.1.2', '地图数据包含 nodes', PASS if nodes_count > 0 else FAIL, f'nodes={nodes_count}')
    record('1.1.3', '地图数据包含 links', PASS if links_count > 0 else FAIL, f'links={links_count}')
    print(f"  [INFO] 地图节点: {nodes_count}, 链接: {links_count}")
except Exception as e:
    record('1.1.1', 'GET /api/map_init', FAIL, str(e))

# Step 2: 执行求解
try:
    r2 = requests.post(f'{BASE_URL}/api/execute_solve', json={'use_llm': False}, timeout=30)
    solve_data = r2.json()
    solve_status = solve_data.get('status')
    solutions = solve_data.get('solutions', [])
    kpi = solve_data.get('kpi', {})
    logs = solve_data.get('logs', [])

    record('1.1.4', 'POST /api/execute_solve 返回200', PASS if r2.status_code == 200 else FAIL, f'status={r2.status_code}')
    record('1.1.5', '求解状态为 success', PASS if solve_status == 'success' else FAIL, f'status={solve_status}')
    record('1.1.6', '返回方案数 > 0', PASS if len(solutions) > 0 else FAIL, f'solutions={len(solutions)}')
    record('1.1.7', '返回日志数 > 0', PASS if len(logs) > 0 else FAIL, f'logs={len(logs)}')

    # Step 3: 验证 solutions 格式
    for i, sol in enumerate(solutions[:3]):
        has_courier = 'courier' in sol
        has_tasks = 'tasks' in sol
        has_utility = 'utility' in sol
        record(f'1.1.8.{i}', f'方案{i}字段完整性', PASS if (has_courier and has_tasks and has_utility) else FAIL,
               f'courier={has_courier}, tasks={has_tasks}, utility={has_utility}')
        print(f"    方案{i}: courier={sol.get('courier')}, tasks={sol.get('tasks')}, utility={sol.get('utility')}")

    # Step 4: 验证 KPI 完整性
    kpi_checks = {
        'total_score': isinstance(kpi.get('total_score'), (int, float)),
        'efficiency_gain': kpi.get('efficiency_gain') is not None,
        'completion_rate': kpi.get('completion_rate') is not None,
        'latency': kpi.get('latency') is not None,
    }
    for key, ok in kpi_checks.items():
        record(f'1.1.9.{key}', f'KPI包含 {key}', PASS if ok else FAIL, f'value={kpi.get(key)}')

    if all(kpi_checks.values()):
        print(f"  [INFO] KPI验证通过: total_score={kpi['total_score']}, efficiency={kpi['efficiency_gain']}, completion={kpi['completion_rate']}, latency={kpi['latency']}")

except Exception as e:
    record('1.1.4', 'POST /api/execute_solve', FAIL, str(e))

# ============================================================
# Part 1.2: Solver 流程
# ============================================================
print("\n" + "="*60)
print("Part 1.2: Solver 流程")
print("="*60)

try:
    r3 = requests.get(f'{BASE_URL}/api/solver', timeout=10)
    solver_data = r3.json()
    selected = solver_data.get('selected', [])
    assigned = [s for s in selected if s.get('assigned')]

    record('1.2.1', 'GET /api/solver 返回200', PASS if r3.status_code == 200 else FAIL, f'status={r3.status_code}')
    record('1.2.2', '返回 selected 列表', PASS if isinstance(selected, list) else FAIL, f'type={type(selected).__name__}')
    record('1.2.3', 'selected 非空', PASS if len(selected) > 0 else FAIL, f'count={len(selected)}')
    record('1.2.4', '存在已分配条目', PASS if len(assigned) > 0 else FAIL, f'assigned={len(assigned)}')
    print(f"  [INFO] Solver: {len(selected)} 条选中, {len(assigned)} 条已分配")
except Exception as e:
    record('1.2.1', 'GET /api/solver', FAIL, str(e))

# ============================================================
# Part 1.3: 带上传数据的求解
# ============================================================
print("\n" + "="*60)
print("Part 1.3: 带上传数据的求解")
print("="*60)

try:
    payload = {
        'use_llm': False,
        'filename': 'test_data.txt',
        'nodeCount': 100,
        'rawData': 'sample data'
    }
    r4 = requests.post(f'{BASE_URL}/api/execute_solve', json=payload, timeout=30)
    record('1.3.1', '带数据求解返回200', PASS if r4.status_code == 200 else FAIL, f'status={r4.status_code}')
    if r4.status_code == 200:
        d4 = r4.json()
        sol_count = len(d4.get('solutions', []))
        record('1.3.2', '带数据求解返回方案', PASS if sol_count > 0 else FAIL, f'solutions={sol_count}')
        print(f"  [INFO] 带数据求解: 方案数={sol_count}")
except Exception as e:
    record('1.3.1', '带数据求解', FAIL, str(e))

# ============================================================
# Part 2.1: 后端错误处理
# ============================================================
print("\n" + "="*60)
print("Part 2.1: 后端错误处理 (边界测试)")
print("="*60)

# 无效 JSON body
try:
    r5 = requests.post(f'{BASE_URL}/api/execute_solve', data='invalid json', headers={'Content-Type': 'application/json'}, timeout=10)
    record('2.1.1', '无效JSON - 非500错误', PASS if r5.status_code < 500 else FAIL, f'status={r5.status_code}')
    print(f"  [INFO] 无效JSON: status={r5.status_code}")
except Exception as e:
    record('2.1.1', '无效JSON请求', FAIL, str(e))

# 空 body
try:
    r6 = requests.post(f'{BASE_URL}/api/execute_solve', json={}, timeout=30)
    record('2.1.2', '空body - 返回200或4xx', PASS if r6.status_code in [200, 400, 422] else FAIL, f'status={r6.status_code}')
    if r6.status_code == 200:
        d6 = r6.json()
        sol_count = len(d6.get('solutions', []))
        record('2.1.3', '空body - 仍返回方案(兼容默认)', PASS if sol_count > 0 else FAIL, f'solutions={sol_count}')
    print(f"  [INFO] 空body: status={r6.status_code}")
except Exception as e:
    record('2.1.2', '空body请求', FAIL, str(e))

# 不存在的端点
try:
    r7 = requests.get(f'{BASE_URL}/api/nonexistent', timeout=10)
    record('2.1.4', '不存在端点 - 返回404', PASS if r7.status_code == 404 else FAIL, f'status={r7.status_code}')
    print(f"  [INFO] 不存在端点: status={r7.status_code}")
except Exception as e:
    record('2.1.4', '不存在端点请求', FAIL, str(e))

# 缺少 Content-Type
try:
    r8 = requests.post(f'{BASE_URL}/api/execute_solve', data='{"use_llm": false}', timeout=30)
    record('2.1.5', '缺少Content-Type - 非崩溃', PASS if r8.status_code < 500 else FAIL, f'status={r8.status_code}')
    print(f"  [INFO] 缺少Content-Type: status={r8.status_code}")
except Exception as e:
    record('2.1.5', '缺少Content-Type请求', FAIL, str(e))

# 超大 payload
try:
    big_payload = {'use_llm': False, 'rawData': 'A' * 100000}
    r9 = requests.post(f'{BASE_URL}/api/execute_solve', json=big_payload, timeout=30)
    record('2.1.6', '超大payload - 非崩溃', PASS if r9.status_code < 500 else FAIL, f'status={r9.status_code}')
    print(f"  [INFO] 超大payload: status={r9.status_code}")
except Exception as e:
    record('2.1.6', '超大payload请求', FAIL, str(e))

# ============================================================
# Part 2.2: CORS 预检测试
# ============================================================
print("\n" + "="*60)
print("Part 2.2: CORS 预检测试")
print("="*60)

allowed_origins = [5173, 5174, 5175, 3000]
for port in allowed_origins:
    try:
        r = requests.options(f'{BASE_URL}/api/execute_solve',
            headers={'Origin': f'http://localhost:{port}', 'Access-Control-Request-Method': 'POST'},
            timeout=10)
        origin = r.headers.get('access-control-allow-origin', 'NONE')
        allowed = origin == f'http://localhost:{port}' or origin == '*'
        record(f'2.2.1.{port}', f'CORS localhost:{port}', PASS if allowed else FAIL, f'origin={origin}')
        print(f"  [INFO] CORS localhost:{port}: status={r.status_code}, allow-origin={origin}")
    except Exception as e:
        record(f'2.2.1.{port}', f'CORS localhost:{port}', FAIL, str(e))

# 不允许的 Origin
try:
    r10 = requests.options(f'{BASE_URL}/api/execute_solve',
        headers={'Origin': 'http://evil.com', 'Access-Control-Request-Method': 'POST'},
        timeout=10)
    evil_origin = r10.headers.get('access-control-allow-origin', 'NONE')
    blocked = evil_origin != 'http://evil.com' and evil_origin != '*'
    record('2.2.2', 'CORS evil.com 被拒绝', PASS if blocked else FAIL, f'origin={evil_origin}')
    print(f"  [INFO] CORS evil.com: status={r10.status_code}, allow-origin={evil_origin}")
except Exception as e:
    record('2.2.2', 'CORS evil.com', FAIL, str(e))

# CORS 预检 - 允许的方法
try:
    r11 = requests.options(f'{BASE_URL}/api/execute_solve',
        headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'},
        timeout=10)
    methods = r11.headers.get('access-control-allow-methods', 'NONE')
    record('2.2.3', 'CORS Allow-Methods 包含 POST', PASS if 'POST' in methods else FAIL, f'methods={methods}')
    print(f"  [INFO] CORS Allow-Methods: {methods}")
except Exception as e:
    record('2.2.3', 'CORS Allow-Methods', FAIL, str(e))

# CORS 预检 - 允许的 Headers
try:
    r12 = requests.options(f'{BASE_URL}/api/execute_solve',
        headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Content-Type'},
        timeout=10)
    allow_headers = r12.headers.get('access-control-allow-headers', 'NONE')
    record('2.2.4', 'CORS Allow-Headers 包含 Content-Type', PASS if 'content-type' in allow_headers.lower() else FAIL, f'headers={allow_headers}')
    print(f"  [INFO] CORS Allow-Headers: {allow_headers}")
except Exception as e:
    record('2.2.4', 'CORS Allow-Headers', FAIL, str(e))

# ============================================================
# Part 2.3: 并发请求测试
# ============================================================
print("\n" + "="*60)
print("Part 2.3: 并发请求测试")
print("="*60)

def make_request(i):
    try:
        r = requests.post(f'{BASE_URL}/api/execute_solve', json={'use_llm': False}, timeout=60)
        data = r.json()
        return i, r.status_code, len(data.get('solutions', [])), None
    except Exception as e:
        return i, -1, 0, str(e)

try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request, i) for i in range(3)]
        all_ok = True
        for f in concurrent.futures.as_completed(futures):
            i, status, count, err = f.result()
            ok = status == 200 and count > 0
            if not ok:
                all_ok = False
            record(f'2.3.1.{i}', f'并发请求 {i}', PASS if ok else FAIL, f'status={status}, solutions={count}, err={err}')
            print(f"  [INFO] 并发请求 {i}: status={status}, solutions={count}")

    record('2.3.2', '所有并发请求均成功', PASS if all_ok else FAIL, '')
except Exception as e:
    record('2.3.2', '并发请求测试', FAIL, str(e))

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60)
print("测试汇总")
print("="*60)

total = len(results)
passed = sum(1 for r in results if r['status'] == PASS)
failed = sum(1 for r in results if r['status'] == FAIL)
skipped = sum(1 for r in results if r['status'] == SKIP)

print(f"  总计: {total}")
print(f"  通过: {passed}")
print(f"  失败: {failed}")
print(f"  跳过: {skipped}")
print(f"  通过率: {passed/total*100:.1f}%")

if failed > 0:
    print("\n  失败用例详情:")
    for r in results:
        if r['status'] == FAIL:
            print(f"    [FAIL] {r['id']}: {r['name']} - {r['detail']}")

# 输出 JSON 结果
with open('d:/美团/test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n  详细结果已保存至: d:/美团/test_results.json")
