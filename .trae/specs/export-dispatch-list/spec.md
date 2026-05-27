# 导出派单清单功能 Spec

## Why
当前导出按钮只是 console.log 打印数据，用户无法真实下载文件。需要实现完整的导出功能。

## What Changes
- **`SolutionTerminal.jsx`**：实现 JSON 和 CSV 双格式导出功能，支持下载文件到本地

## Impact
- Affected code: `d:\美团\src\components\SolutionTerminal.jsx`

## ADDED Requirements

### Requirement 1: JSON 格式导出
系统 SHALL 提供 JSON 格式导出功能，将 `solutions` 数组以格式化 JSON 下载到本地，文件名包含时间戳。

#### Scenario: JSON 导出
- **WHEN** 用户点击 `[ 导出派单清单 ]`
- **THEN** 文件下载到本地，文件名类似：`dispatch-list-2026-05-10-14-30-22.json`
- **AND** 文件内容包含完整的 solutions 数据

### Requirement 2: CSV 格式导出
系统 SHALL 提供 CSV 格式导出功能，将每个任务-运力对拆分为独立行，包含 CourierID、Tasks、Utility。

#### Scenario: CSV 导出
- **WHEN** 用户选择 CSV 格式导出
- **THEN** 文件下载到本地，文件名类似：`dispatch-list-2026-05-10-14-30-22.csv`
- **AND** CSV 包含表头：`CourierID,Tasks,Utility`

### Requirement 3: 双格式选择
系统 SHALL 提供双格式选择按钮，用户可选择 JSON 或 CSV。

#### Scenario: 格式选择
- **WHEN** 用户点击 `[ 导出派单清单 ]`
- **THEN** 显示 JSON / CSV 两个选项按钮供用户选择