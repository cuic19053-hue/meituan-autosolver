# Checklist

- [x] solver_engine.py: 竞标阶段正确计算 Utility 并降序排列
- [x] solver_engine.py: 运力冲突输出 `[系统拦截]` 日志
- [x] solver_engine.py: 任务冲突输出 `[节点冲突]` 日志
- [x] solver_engine.py: 合法匹配输出 `[AI_ALLOTMENT]` 日志
- [x] solver_engine.py: efficiency_gain ≠ completion_rate
- [x] solver_engine.py: efficiency_gain = 实际总效用/理论最大效用×100%
- [x] solver_engine.py: completion_rate = 已匹配任务/总任务×100%
- [x] solver_engine.py: latency 为真实计算耗时
- [x] solver_engine.py: API 返回结构包含 status/kpi/logs/solutions
- [x] solver_engine.py: solutions 每项包含 courier/tasks 字段
- [x] SolutionTerminal.jsx: 新日志前缀正常渲染
- [x] 端到端测试：API 返回正确数据