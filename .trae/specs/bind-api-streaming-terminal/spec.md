# 前后端神经联调与流式渲染 Spec

## Why
后端 `solver_engine.py` 已输出标准 JSON (`status` / `kpi` / `logs` / `solutions`)，但前端存在三层数据断层：
1. `useSolverEngine.js` 的 `kpi` 提取引用了旧字段名 (`total_score`)
2. `SolutionTerminal.jsx` 仅流式渲染 `solutions` 数组，未渲染 `logs` 流
3. `LiveTelemetry.jsx` 的 KPI 显示引用了 `kpi?.total_score`（已不存在）
需要打通完整数据链路，并实现终端日志的 30ms 间隔流式刷屏效果。

## What Changes
- **`useSolverEngine.js`**：状态机增强；新增预设日志推送；错误态终端文本注入
- **`SolutionTerminal.jsx`**：改为流式渲染 `logs` 数组（30ms/行）；修复 KPI 字段引用；更新错误文本；修复预设加载提示
- **`LiveTelemetry.jsx`**：修复 KPI 字段引用，对齐新 solver_engine 输出
- 纯数据层面改动，不修改 UI 动效、布局和交互逻辑

## Impact
- Affected specs: `refactor-solver-engine-v2`（下游消费者）
- Affected code:
  - `d:\美团\src\hooks\useSolverEngine.js`
  - `d:\美团\src\components\SolutionTerminal.jsx`
  - `d:\美团\src\components\layout\LiveTelemetry.jsx`

## MODIFIED Requirements

### Requirement 1: 全局状态机增强 (State Machine)
系统 SHALL 在 `useSolverEngine` hook 中管理以下状态流转：
- `IDLE` → 用户点击按钮 → `FETCHING`
- `FETCHING` → API 成功 → `IDLE`（result 已注入）
- `FETCHING` → API 失败 → `ERROR` → 5s 后自动恢复 `IDLE`

系统 SHALL 在进入 `FETCHING` 状态时立即注入 3 条预设日志到 result：
```
> [SYS] 正在建立加密云端链路...
> [SYS] 云端调度引擎握手成功，正在下发推演指令...
> [SYS] 时空拓扑数据已注入，效用矩阵启动计算...
```

#### Scenario: 按钮点击触发完整状态流转
- **WHEN** 用户点击 `[ 启动云端全息推演 ]` 且 API 返回成功
- **THEN** 状态依次为 IDLE → FETCHING → IDLE
- **AND** `result` 在 FETCHING 期间包含预设日志
- **AND** API 成功后 `result` 被真实数据覆盖

### Requirement 2: 终端日志流式渲染 (Stream Log Rendering)
系统 SHALL 将后端返回的 `logs` 数组以每 30ms 一行的速度逐行渲染到终端。
系统 SHALL 保持对 `solutions` 数组的并行流式渲染（仅为兼容旧逻辑，优先渲染 logs）。
系统 SHALL 在每行推入时自动滚动到终端底部 (`scrollTop = scrollHeight`)。

#### Scenario: logs 数组逐行刷屏
- **WHEN** API 返回 `logs: ["> [SYS] ...", "> [ALLOCATION] ...", ...]`（175+ 行）
- **THEN** 终端以 30ms/行 的速度逐行显示日志
- **AND** 容器自动滚动跟随最新行

### Requirement 3: KPI 数据精准注入 (Data Injection)
系统 SHALL 将 `kpi` 对象注入 `LiveTelemetry` 面板：
- `efficiency_gain` → 显示为"全局效用峰值"
- `completion_rate` → 显示为"云端在线运力"
- `latency` → 显示为"运算耗时"

#### Scenario: KPI 面板实时更新
- **WHEN** API 返回 `kpi: { efficiency_gain: "+72.5%", completion_rate: "72.5%", latency: "0.08s" }`
- **THEN** LiveTelemetry 三行指标分别显示对应值

### Requirement 4: 错误态终端文本 (Error Boundary)
系统 SHALL 在 API 调用失败时在终端显示红色高亮文本：
```
> [SYS_ERROR] 核心引擎离线，请检查云端算力节点。
```
系统 SHALL 提供重试按钮，文本为 `[ 边缘异常接管 ]`。

#### Scenario: API 500 错误
- **WHEN** fetch 抛出异常
- **THEN** 状态进入 ERROR
- **AND** 终端显示红色 `> [SYS_ERROR]` 日志
- **AND** 5 秒后自动恢复 IDLE

### Requirement 5: 约束保证
系统 MUST NOT 修改任何 Tailwind CSS 类名、组件传参结构或按钮 onClick 逻辑。
系统 MUST 仅修改数据字段名、状态值和纯文本字符串。