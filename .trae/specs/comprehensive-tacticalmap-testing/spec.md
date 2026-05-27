# TacticalMap 全面测试规格

## Why
用户报告 TacticalMap 组件存在功能异常，需要对该组件进行全面的功能测试，以确保所有功能正常工作，满足既定的规格要求。

## What Changes
- 对 TacticalMap 组件进行全面的功能测试
- 验证 API 集成功能
- 验证用户交互功能
- 验证视觉渲染功能
- 验证状态管理功能
- 验证错误处理机制

## Impact
- Affected specs: `improve-tactical-map-visual`（需验证该规格的所有功能点）
- Affected code: `src/components/TacticalMap.jsx`、`backend/api` 端点

## ADDED Requirements

### Requirement: 地图初始化功能测试
系统 SHALL 在组件挂载时正确获取并显示地图拓扑数据。

#### Scenario: 初始加载成功
- **WHEN** 组件首次挂载
- **THEN** 应向 `${apiBase}/api/map_init` 发送 GET 请求
- **THEN** 应正确解析并设置 nodes 和 links 状态
- **THEN** Loading 状态应从 true 变为 false

#### Scenario: 初始加载失败
- **WHEN** 组件挂载时 API 请求失败
- **THEN** 应捕获错误并设置 loading 为 false
- **THEN** 不应导致应用崩溃

### Requirement: 节点去重功能测试
系统 SHALL 正确对节点数据进行去重处理。

#### Scenario: 节点 ID 去重
- **WHEN** API 返回包含重复 ID 的节点数据
- **THEN** 应使用 Map 按 ID 唯一化节点
- **THEN** 每个节点 ID 仅渲染一次

#### Scenario: Task 节点过滤
- **WHEN** 获取到节点数据
- **THEN** 应正确过滤出 type === 'task' 的节点
- **THEN** Task 节点应显示为实心圆点

#### Scenario: Courier 节点过滤
- **WHEN** 获取到节点数据
- **THEN** 应正确过滤出 type === 'courier' 的节点
- **THEN** Courier 节点应显示为空心方块

### Requirement: Solver 执行功能测试
系统 SHALL 正确调用 solver 并处理返回结果。

#### Scenario: Solver 执行成功
- **WHEN** 用户点击 EXECUTE SOLVER 按钮
- **THEN** 应向 `${apiBase}/api/solver` 发送请求
- **THEN** 应设置 solving 状态为 true
- **THEN** 应正确解析 selected 和 logs 数据
- **THEN** 应设置 solved 状态为 true
- **THEN** 应更新 selectedLinks 和 solverLogs 状态

#### Scenario: Solver 执行失败
- **WHEN** Solver API 请求失败
- **THEN** 应设置 solverLogs 为 ['[ERROR] Solver request failed']
- **THEN** 应设置 solving 状态为 false
- **THEN** 不应导致应用崩溃

### Requirement: 重置功能测试
系统 SHALL 正确重置所有状态和视图。

#### Scenario: Reset 操作
- **WHEN** 用户点击 RESET 按钮（solved 为 true 时）
- **THEN** 应将 solved 设置为 false
- **THEN** 应清空 selectedLinks
- **THEN** 应清空 solverLogs
- **THEN** 应重置 focusedCourier 为 null

### Requirement: 链路聚焦功能测试
系统 SHALL 实现点击 Courier 节点的链路聚焦交互。

#### Scenario: 点击 Courier 节点
- **WHEN** 用户点击 Courier 节点
- **THEN** 应更新 focusedCourier 状态为该 Courier ID
- **THEN** 该 Courier 的所有链路应以蓝色高亮显示
- **THEN** 其他链路应隐藏

#### Scenario: 再次点击同一 Courier
- **WHEN** 用户再次点击已聚焦的 Courier 节点
- **THEN** 应重置 focusedCourier 为 null
- **THEN** 所有链路应恢复显示

### Requirement: 悬停交互功能测试
系统 SHALL 实现节点悬停时的信息显示。

#### Scenario: Task 节点悬停
- **WHEN** 用户悬停在 Task 节点上
- **THEN** 应显示节点 ID 标签
- **THEN** 标签位置应在节点右侧偏移

#### Scenario: Courier 节点悬停
- **WHEN** 用户悬停在 Courier 节点上
- **THEN** 应显示节点 ID 标签
- **THEN** 标签位置应在节点右侧偏移

#### Scenario: 移出节点
- **WHEN** 用户将鼠标移出节点
- **THEN** 应清除 hoveredId 状态
- **THEN** 不应显示标签

### Requirement: 视觉渲染功能测试
系统 SHALL 正确渲染所有视觉元素。

#### Scenario: viewBox 计算
- **WHEN** 节点数据加载完成
- **THEN** 应根据节点坐标范围计算 viewBox
- **THEN** viewBox 应包含 10% 的 padding

#### Scenario: 链路渲染（未选中）
- **WHEN** solved 状态为 false
- **THEN** 所有链路应以背景样式显示
- **THEN** stroke-width 应为 0.5
- **THEN** stroke-opacity 应为 0.02

#### Scenario: 链路渲染（已选中）
- **WHEN** solved 状态为 true 且链路被选中
- **THEN** 链路应以高亮样式显示
- **THEN** stroke 应为 #FFD000
- **THEN** stroke-width 应为 2
- **THEN** 应应用 drop-shadow 滤镜

#### Scenario: 链路动画
- **WHEN** solved 状态变为 true
- **THEN** 背景链路应在 800ms 内淡出
- **THEN** 高亮链路应在 600ms 内淡入
- **THEN** 高亮链路动画应延迟 200ms 开始

### Requirement: 按钮状态测试
系统 SHALL 正确管理按钮的可用状态。

#### Scenario: 执行中按钮状态
- **WHEN** solving 状态为 true
- **THEN** EXECUTE SOLVER 按钮应被禁用
- **THEN** 按钮应显示 "SOLVING..."

#### Scenario: 加载中按钮状态
- **WHEN** loading 状态为 true
- **THEN** EXECUTE SOLVER 按钮应被禁用

#### Scenario: 执行完成按钮切换
- **WHEN** solved 状态变为 true
- **THEN** 应显示 RESET 按钮替代 EXECUTE SOLVER 按钮

### Requirement: 错误处理测试
系统 SHALL 正确处理各种错误场景。

#### Scenario: 网络错误处理
- **WHEN** API 请求因网络错误失败
- **THEN** 应使用 try-catch 捕获错误
- **THEN** 应设置适当的错误状态
- **THEN** 不应导致 React 崩溃

#### Scenario: 数据格式错误处理
- **WHEN** API 返回的数据格式异常
- **THEN** 应使用安全的方式访问嵌套属性
- **THEN** 不应抛出未捕获的异常

### Requirement: 依赖注入测试
系统 SHALL 支持通过 props 自定义 API 端点。

#### Scenario: 自定义 apiBase
- **WHEN** 传入自定义的 apiBase prop
- **THEN** 所有 API 请求应使用该自定义端点
- **THEN** 默认值应为 'http://localhost:8080'

#### Scenario: onBack 回调
- **WHEN** 传入 onBack prop
- **THEN** 应显示返回按钮
- **WHEN** 不传入 onBack prop
- **THEN** 不应显示返回按钮

## MODIFIED Requirements
（无）

## REMOVED Requirements
（无）

## 测试方法
- 手动功能测试
- 代码审查
- API 集成测试
- 交互测试
- 视觉渲染测试
