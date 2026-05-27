source_code/
├── agent.py              # AutonomousAgent v4.0 - 战区指挥官(元Agent)
│                         #   感知→决策→执行→进化 四层闭环
│                         #   策略竞技场(stategy_bakeoff) 4策略对比
│                         #   权重梯度微搜索 + Sliding Window自适应
│                         #   LLM熔断器 + ε-greedy防过拟合 + Golden策略库
│                         #   DeepSeek API决策 + 规则降级链路
│
├── features.py           # 特征提取 + 策略路由器V2
│                         #   extract_features(): Tuple流式, < 0.1s
│                         #   route_strategy(): 决策树路由(5种场景)
│                         #   route_strategy_v2(): Golden优先 + 规则兜底
│                         #   _feature_distance(): 状态相似度度量
│
├── solver_engine.py      # 求解引擎 - 三重兜底
│                         #   第一重: 完整进化引擎(3轮)
│                         #   第二重: conflict_aware_greedy兜底
│                         #   第三重: 空列表返回
│                         #   execute_solve(): Web API入口
│
├── primitives.py         # 策略原语库(7种求解算法)
│                         #   greedy_min_cost: 成本优先
│                         #   greedy_max_willingness: 意愿优先
│                         #   conflict_aware_greedy: 大包裹优先
│                         #   utility_density_greedy: 效用密度(可调权重)
│                         #   hybrid_greedy: 混合贪心(成本+覆盖)
│                         #   local_search_2opt: 2-opt局部搜索
│                         #   beam_search: 束搜索(beam_width可调)
│
├── main.py               # FastAPI后端服务
│                         #   /solve 端点: 接收输入文本, 返回调度方案
│                         #   /health 健康检查
│                         #   CORS支持 + 静态文件服务
│
├── test_harness.py       # 多场景稳定性测试框架
│                         #   自动化回归测试 + 性能基准
│                         #   stress_test 压力测试
│
├── benchmark.py          # 基准对比模块
│                         #   与baseline算法对比: Greedy/LP/GNN
│                         #   KPI: 成本节省率 / 任务完成率 / 延迟
│
├── compliance_check.py   # 提交合规检查
│                         #   格式校验 + 冲突检测
│                         #   确保输出符合judge评分要求
│
├── minimax_client.py     # MiniMax API客户端
│                         #   备用LLM决策(DeepSeek不可用时)
│
├── data_processor.py     # 数据预处理与校验
│
├── data_service.py       # 数据服务层
│
├── engine.py             # 基础引擎(早期版本)
│
├── agents/               # 子Agent模块
│   ├── inventory_agent.py
│   └── router_agent.py
│
├── .env                  # 环境变量 (DEEPSEEK_API_KEY等)
├── .env.example          # 环境变量模板
├── requirements.txt      # Python依赖
├── memory.json           # 进化记忆库(运行时生成)
├── golden.json           # Golden策略库(运行时生成)
├── evolution_metrics.json # 进化指标(运行时生成)
└── experience_summary.txt # LLM经验摘要(运行时生成)

安装依赖: pip install -r requirements.txt
运行后端: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
前端界面: 浏览器打开 http://localhost:8000

========== Agent架构速览 ==========

┌─────────────────────────────────────────────────┐
│                 感知层 (Perceive)                 │
│  extract_features() → density/avg_will/avg_score │
│  Tuple流式解析, O(N), < 0.1s                     │
├─────────────────────────────────────────────────┤
│                 决策层 (Decide)                   │
│  Golden策略库 → LLM决策 → 规则路由 → 竞技场      │
│  ε-greedy探索 + 熔断器 + 降级链路                │
├─────────────────────────────────────────────────┤
│                 执行层 (Execute)                  │
│  7种策略原语 + 冲突审计                          │
│  O(1) Set冲突排查, 三重兜底                       │
├─────────────────────────────────────────────────┤
│                 进化层 (Evolve)                   │
│  权重梯度搜索 + Sliding Window                   │
│  记忆库 → 经验摘要 → Golden策略固化               │
│  LLM超时熔断 → 自动恢复                          │
└─────────────────────────────────────────────────┘

评分函数: Score = Σ(score × (2.0 - will)) + 100 × n_rejected
效用函数: Utility = 1,000,000 - Score
目标: 最大化Utility = 最小化Score