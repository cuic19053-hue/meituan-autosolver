***

name: "autosolver"
description: "AI 配送调  度驾驶舱开发技能。处理 AutoSolver 项目的架构设计、Elite Fluidity 视觉规范、冲突规避算法实现。当开发新功能、添加组件或优化界面时调用。"
-------------------------------------------------------------------------------------------------------

# AutoSolver - AI 配送调度驾驶舱

本技能文档定义了 AutoSolver 项目的开发规范、架构标准和设计语言。

## 项目概述

**项目定位**：解决即时配送场景中"最后一公里"的效率博弈，处理 301 条候选方案并输出最优执行指令。

**技术架构**：

- **前端**：Streamlit（主应用）+ React/Vite（高级可视化组件）
- **后端**：FastAPI + Python 调度引擎
- **AI 集成**：MiniMax API（AI Agent 决策）+ Gemini/Trae（Vibe Coding）

**核心数据流**：

```
large_seed301.txt → 数据处理器 → 调度引擎 → AI Agent → 最优方案 → 前端展示
```

## 设计哲学：Elite Fluidity

### 核心理念

"成熟、工业、冷静" —— 将沉重的工业数据包装成丝滑的交互体验。

### 视觉语言

**毛玻璃效果**：

```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
```

**边框规范**：

```css
border: 1px solid rgba(255, 255, 255, 0.1);
```

**渐变背景**：

```css
background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
```

**字体层级**：

- 标题：`font-weight: 700`，字间距 `0.05em`
- 正文：`font-weight: 400`，行高 `1.6`
- 数据显示：`font-family: 'JetBrains Mono', monospace`

### 动画规范

**流式输出**（Agent Terminal）：

- 行间隔：20ms/行
- 缓动函数：`ease-out`
- 最大缓冲区：100 行

**状态转换**：

- 持续时间：300ms
- 缓动函数：`cubic-bezier(0.4, 0, 0.2, 1)`

## 四大核心模块

### 1. 顶部系统栏 (Top Bar)

**职能**：权限锚定，系统模式切换

**交互规范**：

- 模式切换：全自动 ↔ AI 副驾驶
- 健康度指示器：实时脉冲动画
- 状态持久化：localStorage + sessionStorage

**代码模板**：

```jsx
<div className="top-bar">
  <ModeToggle 
    auto={systemMode === 'auto'}
    onToggle={handleModeSwitch}
  />
  <HealthIndicator 
    score={systemHealth}
    pulse={true}
  />
</div>
```

### 2. AI 副驾驶 (Copilot)

**职能**：策略博弈，背景逻辑展示

**交互规范**：

- 对话式干预：支持自然语言偏好设置
- 推理透明度：显示算法推导过程
- 实时反馈：权重调整即时生效

**代码模板**：

```jsx
<CopilotPanel>
  <StrategyDisplay>
    {agentReasoning.map((step, i) => (
      <ReasoningStep 
        key={i}
        step={step}
        confidence={step.confidence}
      />
    ))}
  </StrategyDisplay>
  <InterventionInput
    onSubmit={handlePreferenceOverride}
    placeholder="调整骑手偏好权重..."
  />
</CopilotPanel>
```

### 3. 中心态势区 (Matrix)

**职能**：空间感知，调度压力可视化

**组件结构**：

- Node 01-04：核心指标卡片
- 实时数据：使用 useEffect + setInterval 更新
- 状态映射：颜色编码（绿→黄→红）

**代码模板**：

```jsx
<div className="matrix-grid">
  {['Node 01', 'Node 02', 'Node 03', 'Node 04'].map(node => (
    <MetricCard 
      key={node}
      title={node}
      value={metrics[node]}
      trend={trends[node]}
      color={getStatusColor(metrics[node])}
    />
  ))}
</div>
```

### 4. Agent 终端 (Terminal)

**职能**：逻辑黑匣，流式日志

**交互规范**：

- 流式输出：模拟高并发指令下发
- 语法高亮：任务 / 骑手 / 时间戳 分色显示
- 缓冲区管理：自动滚动 + 手动锁定

**代码模板**：

```jsx
<StreamingTerminal
  streamData={agentLogs}
  lineInterval={20}
  maxBuffer={100}
  syntaxHighlighting={{
    task: '#00ff88',
    courier: '#00bfff',
    timestamp: '#666'
  }}
/>
```

## 冲突规避算法规范

### 贪心匹配逻辑

```python
def greedy_match(tasks: List[Task], couriers: List[Courier]) -> List[Assignment]:
    """
    确保每个任务不重叠，每个骑手不分身
    
    Args:
        tasks: 候选任务列表
        couriers: 可用骑手列表
    
    Returns:
        最优分配方案
    """
    assignments = []
    used_tasks = set()
    used_couriers = set()
    
    # 按优先级排序
    sorted_tasks = sort_by_priority(tasks)
    
    for task in sorted_tasks:
        if task.id in used_tasks:
            continue
            
        # 贪心选择最优骑手
        best_courier = find_best_courier(task, couriers, used_couriers)
        
        if best_courier:
            assignments.append(Assignment(task, best_courier))
            used_tasks.add(task.id)
            used_couriers.add(best_courier.id)
    
    return assignments
```

### 约束条件

- 时间窗口：任务必须在骑手的可用时段内
- 距离限制：单次配送距离 ≤ 5km
- 负载均衡：单个骑手最大任务数 = 8
- 优先级继承：紧急任务优先分配

## 组件开发规范

### 命名约定

- 文件名：PascalCase（例：`MetricCard.tsx`）
- 组件名：PascalCase
- 函数/变量：camelCase
- 常量：UPPER\_SNAKE\_CASE

### 样式规范

- 使用 Tailwind CSS 原子化样式
- 自定义样式写在 `styles.css` 或 `index.css`
- 避免内联样式，优先使用类名
- CSS 变量定义在 `:root` 中

### Props 定义

```typescript
interface ComponentProps {
  title: string;
  value: number | string;
  trend?: 'up' | 'down' | 'stable';
  color?: 'green' | 'yellow' | 'red';
  onClick?: () => void;
}
```

## 数据接口规范

### 后端 API

```python
# FastAPI 端点
POST /api/solve
GET /api/status
POST /api/override
WS /api/stream
```

### 数据格式

```json
{
  "tasks": [
    {
      "id": "T001",
      "pickup": {"lat": 39.9, "lng": 116.4},
      "dropoff": {"lat": 39.95, "lng": 116.45},
      "time_window": ["09:00", "10:00"],
      "priority": 1
    }
  ],
  "couriers": [
    {
      "id": "C001",
      "location": {"lat": 39.9, "lng": 116.4},
      "capacity": 8
    }
  ]
}
```

## MANUAL\_OVERRIDE 接口

提供人机协作的即时接管能力：

```python
@app.post("/api/override")
async def manual_override(assignment: Assignment):
    """
    允许调度员手动调整分配方案
    
    触发场景：
    - 骑手爆胎
    - 突发恶劣天气
    - 客户临时变更地址
    """
    return {"status": "applied", "assignment_id": assignment.id}
```

## 代码审查清单

新增功能必须满足：

- [ ] 遵循 Elite Fluidity 设计规范
- [ ] 支持暗色主题切换
- [ ] 流式输出场景使用 requestAnimationFrame 优化
- [ ] 敏感操作有确认机制
- [ ] 响应式布局适配（1920px / 1440px / 1280px）
- [ ] 无控制台错误和警告

## 示例：新增 Node 指标卡片

```jsx
import { motion } from 'framer-motion';

export const NodeCard = ({ title, value, color }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
    className="metric-card"
    style={{
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}
  >
    <div className="text-sm text-gray-400">{title}</div>
    <div 
      className="text-3xl font-bold mt-2"
      style={{ color }}
    >
      {value}
    </div>
  </motion.div>
);
```

## 技术债务与优化方向

**短期**：

- 完善单元测试覆盖率（目标：80%）
- 优化流式输出的内存占用

**中期**：

- 引入 Web Worker 处理复杂计算
- 实现离线缓存机制

**长期**：

- 支持多站点协同调度
- 集成实时地图可视化

## 参考资料

- 设计系统：`tailwind.config.js` 中的自定义配置
- 种子数据：`large_seed301.txt`（301 条候选方案）
- 核心算法：`backend/solver_engine.py`
- AI 集成：`backend/minimax_client.py`

