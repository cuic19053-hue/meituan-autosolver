# 修复后全功能回归测试 Spec

## Why
项目经过 19 个 Bug 修复（含 8 个严重、7 个中等、4 个轻微），涉及 useSolverEngine 竞态修复、SolutionTerminal 副作用修复、DataUploader 数据链路贯通、CityGrid 渲染修正等，需要回归测试确保所有修复正确生效且未引入新问题。

## What Changes
- useSolverEngine 新增 AbortController + timerRef + initiate(payload) 参数
- App.jsx 新增 uploadedData state + handleInitiate/handleDatasetLoaded
- SolutionTerminal 移除 apiBase 死代码 + AnimatedNumber rAF 清理 + 副作用移出 updater + handleRetry 真重试 + escapeCSV + revokeObjectURL 延迟
- DataUploader 新增 [重新上传] 按钮 + 错误状态触发文件选择器
- LiveTelemetry KPI 语义对齐 + null 时显示 "--"
- OrchestrationNav 新增 isError prop + 动态状态文案
- CityGrid 水平线 y2 修正
- TacticalMap 数值排序
- ReflectionConsole 增量日志追加
- 后端 solver_engine.py kpi 新增 total_score
- 后端 main.py CORS 新增 5175 端口

## Impact
- Affected specs: test-landing-page（已过时，需重新验证修复后的代码）
- Affected code: 所有前端组件 + 后端 API

## ADDED Requirements

### Requirement: 修复后回归测试
系统 SHALL 通过全面回归测试，确保所有修复正确生效且未引入新回归问题。

#### Scenario: 修复验证
- **WHEN** 执行回归测试
- **THEN** 所有修复点验证通过，原有功能不受影响

### Requirement: 数据链路贯通验证
系统 SHALL 确保从 DataUploader 上传到 useSolverEngine 发送请求的完整数据链路正常工作。

#### Scenario: 上传数据传递
- **WHEN** 用户上传文件后点击 INITIATE
- **THEN** uploadedData 通过 initiate(payload) 传递到 fetch body

### Requirement: 竞态条件修复验证
系统 SHALL 确保快速操作（initiate → reset → initiate）不会导致状态混乱。

#### Scenario: 快速操作
- **WHEN** 用户快速点击 INITIATE 后立即点击重置
- **THEN** 旧请求被 abort，新状态正确设置
