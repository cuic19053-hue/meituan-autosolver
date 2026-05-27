# Landing 页面全功能测试 Spec

## Why
App.jsx 已从 Command Center 重构为 Landing 页面（VexHero 风格），组件架构完全变化（新增 useSolverEngine hook、OrchestrationNav、MissionBrief、LiveTelemetry、DataUploader、atoms 组件族），需要全面验证新架构下所有功能是否正常工作。

## What Changes
- 新增 useSolverEngine hook 管理求解器状态
- App.jsx 重构为 Landing 页面布局（视频背景 + CityGrid + 导航栏 + MissionBrief + LiveTelemetry + 右侧终端）
- 新增组件：OrchestrationNav、MissionBrief、LiveTelemetry、DataUploader
- 新增 atoms 组件：CityGrid、AnimatedHeading、FadeIn、StatusDot、Sparkline
- SolutionTerminal 支持 externalResult 模式（由 useSolverEngine 驱动）
- 后端 POST /api/execute_solve 接口（替代 GET）

## Impact
- Affected specs: full-project-testing（已过时，需重新测试）
- Affected code: App.jsx, useSolverEngine.js, SolutionTerminal.jsx, MissionBrief.jsx, LiveTelemetry.jsx, DataUploader.jsx, OrchestrationNav.jsx, 所有 atoms 组件, backend/main.py

## ADDED Requirements

### Requirement: Landing 页面渲染
系统 SHALL 在初始加载时正确渲染 Landing 页面，包含视频背景、CityGrid 覆盖层、OrchestrationNav 导航栏、MissionBrief 区域、LiveTelemetry 卡片、右侧 SolutionTerminal。

#### Scenario: 页面初始加载
- **WHEN** 用户访问首页
- **THEN** 页面渲染视频背景、CityGrid SVG、导航栏（含品牌名和导航链接）、标题动画、INITIATE 按钮、遥测卡片、右侧终端

### Requirement: useSolverEngine Hook
系统 SHALL 提供 useSolverEngine hook 管理 IDLE/FETCHING/ERROR 三种状态，支持 initiate() 和 reset() 操作。

#### Scenario: initiate 成功
- **WHEN** 调用 initiate()
- **THEN** status 变为 FETCHING，发送 POST /api/execute_solve，成功后 result 被设置，status 回到 IDLE

#### Scenario: initiate 失败
- **WHEN** API 请求失败
- **THEN** result 被设置为 ERROR_RESULT，status 变为 ERROR，5 秒后自动恢复 IDLE

#### Scenario: 防重复请求
- **WHEN** status 为 FETCHING 时再次调用 initiate()
- **THEN** 请求被忽略

### Requirement: DataUploader 文件上传
系统 SHALL 支持拖拽或点击上传 .txt/.csv 文件，上传成功后触发 onLoaded 回调。

#### Scenario: 上传成功
- **WHEN** 用户上传有效文件
- **THEN** 显示成功状态（绿色边框 + 文件名 + 节点数），触发 onDatasetLoaded

#### Scenario: 上传失败
- **WHEN** 用户上传不支持的格式或超大文件
- **THEN** 显示错误状态（红色边框 + 错误信息），可点击重试

### Requirement: SolutionTerminal 外部数据模式
系统 SHALL 在接收 externalResult 时跳过 API 请求，直接使用外部数据渲染终端。

#### Scenario: 外部数据渲染
- **WHEN** externalResult 被传入
- **THEN** 终端逐行显示 logs，完成后显示 solutions，弹出结算看板

### Requirement: 后端 API 兼容性
系统 SHALL 确保后端所有 API 端点正常工作，包括 POST /api/execute_solve。

#### Scenario: POST /api/execute_solve
- **WHEN** 前端发送 POST 请求
- **THEN** 返回 { status, solutions, kpi, logs } 格式数据

## MODIFIED Requirements

### Requirement: 页面布局
从 Command Center 四卡片布局变更为 Landing 页面全屏布局，右侧固定终端面板。

## REMOVED Requirements

### Requirement: Command Center 四卡片布局
**Reason**: App.jsx 已重构为 Landing 页面
**Migration**: 旧布局代码已移除，TacticalMap 组件保留但未被 App.jsx 使用
