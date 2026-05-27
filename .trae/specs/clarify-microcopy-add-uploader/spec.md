# UI 微文案清晰化 + 数据集上传组件 Spec

## Why
当前 UI 文案仍残留"工业级运筹"术语，不够贴近外卖调度场景。同时缺少数据集上传前置步骤，用户可直接点击执行按钮，缺少防呆机制。需要将文案统一为"大厂 SaaS / 外卖调度系统"风格，并新增 DataUploader 组件实现上传锁定逻辑。

## What Changes
- 全局替换前端 UI 显示文本为外卖调度场景术语
- 新增 `src/components/DataUploader.jsx` 拖拽上传组件
- 修改 `MissionBrief.jsx`：集成 DataUploader + datasetLoaded 锁定按钮
- 修改 `App.jsx`：新增 `datasetLoaded` 状态并传递给 MissionBrief

## Impact
- Affected code: `OrchestrationNav.jsx`、`MissionBrief.jsx`、`LiveTelemetry.jsx`、`SolutionTerminal.jsx`、`App.jsx`、新增 `DataUploader.jsx`

## ADDED Requirements

### Requirement: UI 微文案全面清晰化
系统 SHALL 将所有前端显示文本替换为外卖调度场景术语：

| 位置 | 原文 | 替换为 |
|------|------|--------|
| 品牌栏 | AutoSolver / 云端智能运筹中枢 | **AutoSolver \| 智能配送调度中枢** |
| Slogan | 云网协同推演 / 空间运力聚合引擎 | **运力聚合 · 智能派单** |
| 副标题 | 云原生多智能体运筹引擎... | **多智能体协同 · 为即时配送而生的 AI 调度引擎** |
| 副描述 | 多智能体协同推演 · 重新定义时空运筹范式 | **毫秒级决策 · 千单级并发 · 全链路可追溯** |
| 数据面板标题 | // 时空拓扑遥测矩阵 | **// 实时调度大盘** |
| 指标1 | 全局效用峰值 | **待派发订单** |
| 指标2 | 全域待分配锚点 | **在线骑手运力** |
| 指标2单位 | 云端在线运力 | **骑手** |
| 指标3 | 推演延迟 | **算法运算耗时** |
| 终端初始化 | > [SYS] 正在接入云端调度引擎... | **> [系统] 正在连接 AI 调度引擎...** |
| 终端覆盖 | [ALLOTMENT_OVERRIDE] | **[站长接管]** |
| 终端确认 | [ALLOTMENT_CONFIRMED] | **[AI 派单]** |
| 结算标题 | 全局效用归因报告 | **调度效果评估报告** |
| 结算指标 | 效用增量 / 全域锚定率 / 推演延迟 | **预估效用提升 / 派单完成率 / 算法运算耗时** |
| CTA 按钮 | ▶ 启动云端全息推演 | **[ 启动 AI 调度 ]** |
| CTA loading | ▶ 推演进行中... | **[ 调度执行中... ]** |
| 副按钮 | 技术白皮书 › | **调度算法说明 ›** |
| 终端重试 | [边缘异常接管] | **[站长接管]** |
| 终端行格式 | 任务拓扑节点 T0037 已锚定至运力 C028 | **订单 T0037 → 骑手 C028** |
| 终端底栏 | 推演行 / 全局效用 / 锚定率 / 推演进度 | **派单行 / 效用值 / 派单率 / 执行进度** |
| 终端状态 | 推演中 / 归因完成 | **派单中 / 派单完成** |
| 导航 | 全域态势 / 运力情报 / 效能指标 | **调度概览 / 运力监控 / 效能分析** |
| 状态栏 | 全域系统 · 在线 | **调度系统 · 运行中** |
| 结算状态 | 全域系统 · 稳态运行 | **调度系统 · 正常** |
| 终端重置 | [重置终端] | **[重置日志]** |
| 结算确认 | [确认归因] | **[确认报告]** |

### Requirement: DataUploader 组件
系统 SHALL 提供拖拽上传组件：

- 位置：MissionBrief 中 [ 启动 AI 调度 ] 按钮正上方
- 视觉：`border-dashed border-white/20 bg-white/5 backdrop-blur-sm rounded-lg`
- 默认态：居中文字 `[ 拖拽或点击上传测试数据集 (.txt / .csv) ]` + 云端上传图标
- 成功态：绿色边框，文字变为 `[系统] 成功读取：large_seed301.txt (识别到 301 条待派单数据)`
- 状态：`datasetLoaded` (boolean)

### Requirement: 按钮防呆锁定
- `datasetLoaded === false` → [ 启动 AI 调度 ] 按钮灰色 + disabled
- `datasetLoaded === true` → 按钮亮起美团黄 (#FFD000) + 可点击

## MODIFIED Requirements
- MissionBrief 新增 `datasetLoaded` prop 控制按钮可用性
- App.jsx 新增 `datasetLoaded` 状态并传递

## REMOVED Requirements
- 无
