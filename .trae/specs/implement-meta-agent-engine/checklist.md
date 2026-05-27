# Checklist

- [x] solver_engine.py: MetaAgent 类存在且包含 analyze + decide_weights 方法
- [x] solver_engine.py: STHAFEngine 类存在且包含 execute 方法
- [x] solver_engine.py: 效用公式为 (100 - score) × w_score + (willingness × 100) × w_will
- [x] solver_engine.py: avg_will < 0.3 时 w_will=0.6, w_score=0.4
- [x] solver_engine.py: avg_will >= 0.3 时 w_will=0.3, w_score=0.7
- [x] solver_engine.py: [META_AGENT] 日志生成
- [x] solver_engine.py: [META_REFLECTION] 日志生成
- [x] solver_engine.py: [AI_ALLOTMENT] 日志生成
- [x] solver_engine.py: [系统拦截] 日志生成
- [x] solver_engine.py: [节点冲突] 日志生成
- [x] solver_engine.py: efficiency_gain ≠ completion_rate (+33.3% vs 82.5%)
- [x] solver_engine.py: API 返回结构包含 status/kpi/logs/solutions
- [x] solver_engine.py: solutions 每项包含 courier/tasks 字段
- [x] solver_engine.py: parse_seed_file() 签名不变
- [x] solver_engine.py: execute_solve() 签名不变
- [x] SolutionTerminal.jsx: [META_AGENT] 前缀正常渲染
- [x] SolutionTerminal.jsx: [META_REFLECTION] 前缀正常渲染
- [x] 端到端测试：API 返回正确数据