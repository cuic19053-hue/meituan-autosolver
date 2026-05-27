# B 端工业级微文案语态重构 Spec

## Why
当前前端 UI 文本存在机器翻译风格，缺乏物流运筹、云端架构与时空数据领域的专业术语，不符合大厂 B 端产品的文案标准。需要全局替换为专业语态，提升产品工业感与可信度。

## What Changes
- App.jsx：品牌名、Hero 标题、HUD 标签、终端标题、Summary 弹窗、按钮文本全部替换
- SolutionTerminal.jsx：状态标签、流式输出行格式、hover 干预提示文本替换
- OrchestrationNav.jsx：品牌版本号、导航链接、状态栏文本替换
- MissionBrief.jsx：Hero 标题、描述文案、CTA 按钮文本替换
- LiveTelemetry.jsx：数据面板标题、指标标签替换
- DataUploader.jsx：上传提示文本替换
- **纯文本替换，零逻辑变更，零样式变更**

## Impact
- Affected specs: N/A（新增独立 Spec，与已有 Spec 无冲突）
- Affected code:
  - `d:\美团\src\App.jsx`
  - `d:\美团\src\components\SolutionTerminal.jsx`
  - `d:\美团\src\components\layout\OrchestrationNav.jsx`
  - `d:\美团\src\components\layout\MissionBrief.jsx`
  - `d:\美团\src\components\layout\LiveTelemetry.jsx`
  - `d:\美团\src\components\DataUploader.jsx`

## MODIFIED Requirements

### Requirement 1: 品牌与 Header 层文案
系统 SHALL 在导航栏展示"AutoSolver"品牌名及"云端智能运筹中枢"版本标签。
系统 SHALL 在 Hero 区域展示"云网协同推演 · 空间运力聚合引擎"主标题。

#### Scenario: 页面加载时展示品牌
- **WHEN** 用户打开首页
- **THEN** 导航栏显示"AutoSolver | 云端智能运筹中枢"
- **AND** Hero 标题显示"云网协同推演 · 空间运力聚合引擎"

### Requirement 2: 统计卡片与指标层文案
系统 SHALL 在 HUD 数据面板使用"时空拓扑遥测矩阵"作为面板标题。
系统 SHALL 将任务数标签替换为"全域待分配锚点"，运力标签替换为"云端在线运力"，分数标签替换为"全局效用峰值"。

#### Scenario: 数据面板展示专业术语
- **WHEN** 用户查看右下角 HUD 面板
- **THEN** 面板标题显示"时空拓扑遥测矩阵"
- **AND** 指标行分别显示"全局效用峰值"、"云端在线运力"、"算法运算耗时"

### Requirement 3: 终端与输出层文案
系统 SHALL 将终端标题替换为"多智能体决策终端"。
系统 SHALL 在终端无数据时展示"> [SYS] 正在接入云端调度引擎..."初始化提示。
系统 SHALL 将流式输出行格式统一为"> [ALLOTMENT_OVERRIDE] 任务拓扑节点 {task_id} 已锚定至运力 {courier_id}"。
系统 SHALL 将结算弹窗标题替换为"全局效用归因报告"。

#### Scenario: 终端初始化
- **WHEN** 终端组件挂载且无数据
- **THEN** 显示"> [SYS] 正在接入云端调度引擎..."

#### Scenario: 流式输出行渲染
- **WHEN** 终端逐行渲染分配方案
- **THEN** 每行格式为"> [ALLOTMENT_OVERRIDE] 任务拓扑节点 T0037 已锚定至运力 C028"

### Requirement 4: 核心交互按钮文案
系统 SHALL 将所有名为"启蒙"的按钮替换为"[ 启动云端全息推演 ]"。
系统 SHALL 将终端行 hover 干预提示替换为"[ 边缘异常接管 ]"。

#### Scenario: 按钮显示正确的 CTA 文案
- **WHEN** 页面加载完成且数据集已就绪
- **THEN** 主按钮显示"[ 启动云端全息推演 ]"

#### Scenario: 执行中按钮状态
- **WHEN** 用户点击按钮后调度正在执行
- **THEN** 按钮显示"[ 全息推演中... ]"

### Requirement 5: 约束保证
系统 MUST NOT 修改任何 onClick 逻辑、useState 变量名、组件传参或 Tailwind CSS 类名。
系统 MUST 仅替换纯文本字符串内容。

#### Scenario: 重构后功能不变
- **WHEN** 微文案替换完成后
- **THEN** 所有按钮点击行为与原版本一致
- **AND** 所有 API 调用参数与原版本一致
- **AND** 所有 CSS 视觉效果与原版本一致