# 修复推演全链路运行时错误 Spec

## Why
前端推演流程存在 3 个关键状态管理 Bug，导致：
1. 复盘看板在预设日志阶段就弹出（KPI 全为 0）
2. 真实 API 数据到达后复盘看板立即弹出（流式渲染未完成）
3. 系统复位后终端仍残留旧数据

## What Changes
- **`SolutionTerminal.jsx`**：修复 `isFinished` 不随 `externalResult` 重置的 Bug；修复 `externalResult=null` 时状态不清理的 Bug；修复 `handleReset` 不重置内部状态的 Bug

## Impact
- Affected code: `d:\美团\src\components\SolutionTerminal.jsx`

## MODIFIED Requirements

### Requirement 1: isFinished 必须随 externalResult 变化重置
系统 SHALL 在每次 `externalResult` 变化时将 `isFinished` 重置为 `false`。

#### Scenario: 预设日志 → 真实数据
- **WHEN** `externalResult` 从预设日志变为真实 API 数据
- **THEN** `isFinished` 被重置为 `false`
- **AND** 流式渲染从 0 开始重新计数
- **AND** 复盘看板不弹出直到新的流式渲染完成

### Requirement 2: externalResult 为 null 时清理所有状态
系统 SHALL 在 `externalResult` 变为 null 时重置 `data`、`displayCount`、`isFinished`、`showDebrief`。

#### Scenario: 点击结束本次推演
- **WHEN** 用户点击 `[ 结束本次推演 ]`
- **THEN** `externalResult` 变为 null
- **AND** 终端显示空状态 `> [SYS] 正在接入云端调度引擎...`

### Requirement 3: handleReset 重置所有内部状态
系统 SHALL 在 `handleReset` 中重置 `data`、`displayCount`、`isFinished`、`showDebrief`。

#### Scenario: 重置按钮
- **WHEN** 用户点击 `[ 重置日志 ]`
- **THEN** 终端完全清空回到初始状态