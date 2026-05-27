# 动态战术地图 + 反思机制可视化 Spec

## Why
当前 TacticalMap.jsx 视觉较为基础，缺少渐变网格、骑手三角呼吸灯、链路流光动画等高级可视化元素。同时，算法决策过程（冲突处理、反思重分配）没有独立的侧边面板实时展示，导致用户无法直观理解 AI 调度逻辑。需要将战术地图升级为工业级可视化，并新增 ReflectionConsole 组件实时呈现算法思考过程。

## What Changes
- 升级 `src/components/TacticalMap.jsx`：渐变网格（50px）、任务圆环节点、三角骑手节点（呼吸灯）、流光链路动画
- 新增 `src/components/ReflectionConsole.jsx`：半透明侧边面板，实时滚动展示算法决策日志
- 修改 `src/App.jsx`：将 TacticalMap + ReflectionConsole 并列集成到卡片区域（替代现有 SolutionTerminal 独占方案）
- 修改 `backend/data_service.py`：`solve()` 增加更丰富的反思日志（CONFLICT、REFLECTION 等标签）
- `backend/main.py` `/api/solver` 接口返回格式保持不变

## Impact
- Affected specs: 前后端通信契约（`/api/map_init`、`/api/solver` 接口不变）
- Affected code: `src/components/TacticalMap.jsx`、`src/components/ReflectionConsole.jsx`（新增）、`src/App.jsx`、`backend/data_service.py`

## ADDED Requirements

### Requirement: 战术地图视觉增强
系统 SHALL 在 TacticalMap.jsx 中实现以下可视化增强：

#### Sub-Requirement: 渐变网格背景
- 背景色 `#0A0A0A`
- SVG `<pattern>` 定义网格，每 50px 一格
- 网格线颜色：`rgba(237,237,237,0.03)`（细线）
- 叠加一层渐变色：从透明到 `rgba(10,10,10,0.8)`（边缘暗化效果）

#### Sub-Requirement: 任务节点
- 渲染为圆环（stroke circle），填充透明
- 颜色 `#EDEDED`，线宽 1px
- 悬停时显示 ID 标签

#### Sub-Requirement: 骑手节点
- 渲染为等腰三角形（polygon SVG），朝上
- 颜色 `#737373`
- 呼吸灯动画：CSS `@keyframes` 控制 `opacity` 在 0.4 ~ 1.0 之间，周期 2s

#### Sub-Requirement: 动态链路
- 初始状态：所有 301 条链路显示为灰色细线，`opacity: 0.1`
- 激活状态：选中链路变为美团黄 `#FFD000`，线宽 2px，`stroke-dasharray="8 4"`
- 流光动画：CSS `@keyframes` 控制 `stroke-dashoffset` 循环递减，周期 1.2s

#### Scenario: 地图加载
- **WHEN** TacticalMap 组件挂载
- **THEN** 从 `/api/map_init` 获取拓扑数据，渲染节点和链路

#### Scenario: 求解执行
- **WHEN** 用户点击 "EXECUTE SOLVER"
- **THEN** 调用 `/api/solver`，链路从灰色变为美团黄并带有流光动画

### Requirement: ReflectionConsole 组件
系统 SHALL 提供 `ReflectionConsole.jsx` 组件。

- 位置：TacticalMap 右侧侧边栏，宽度约 280px
- 外观：`bg-black/70`，`border border-[#262626]`，`backdrop-blur-md`
- 字体：`font-mono`，`text-[11px]`，行高 1.6
- 功能：实时滚动展示算法决策日志，格式如：
  - `[CONFLICT] C037 node re-assigned due to efficiency threshold...`
  - `[REFLECTION] Optimizer evaluating alternative courier for T0051...`
  - `[ASSIGN] C028 -> ["T0037","T0039"] | Score: 52.02 | Willingness: 0.582`
- 日志行颜色分类：
  - ASSIGN: `#34D399`（绿色）
  - CONFLICT: `#FFD000`（黄色）
  - REFLECTION: `#C084FC`（紫色）
  - SKIP: `#737373`（灰色）
  - WARN: `#F87171`（红色）
- 底部统计栏：显示已分配数、冲突数、总得分

#### Scenario: 实时日志滚动
- **WHEN** TacticalMap 执行 solver 时
- **THEN** ReflectionConsole 实时接收并逐行显示日志（50ms 间隔 typewriter）

### Requirement: App 集成
系统 SHALL 在 App.jsx 的卡片区域同时展示 TacticalMap 和 ReflectionConsole：
- 水平布局：左侧 TacticalMap（flex-1），右侧 ReflectionConsole（w-72）
- TacticalMap 底部保留执行按钮
- 点击 "EXECUTE SOLVER" 时，ReflectionConsole 开始滚动日志，TacticalMap 高亮链路

## MODIFIED Requirements

### Requirement: data_service.py solve() 日志增强
**原有**：`solve()` 返回 `selected`、`logs`、`total_score`、`assigned_count`
**修改**：`logs` 数组中增加更多反思类标签：
- `[REFLECTION]` 标签用于描述重分配决策
- `[CONFLICT #N]` 标签用于标记第 N 次冲突
- `[EFFICIENCY]` 标签用于描述效率评估
- 所有日志带时间戳 `[HH:MM:SS]`

## REMOVED Requirements
- 移除 App.jsx 中 SolutionTerminal 的独占显示逻辑（改由 TacticalMap + ReflectionConsole 并列展示替代）
