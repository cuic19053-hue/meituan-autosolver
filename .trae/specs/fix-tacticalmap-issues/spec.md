# 修复 TacticalMap 组件问题规格

## Why
在全面测试 TacticalMap 组件后，发现多个高优先级和中优先级的功能缺陷和错误处理问题，需要立即修复以确保组件的稳定性和用户体验。

## What Changes
- 修复 HTTP 状态检查缺失问题（fetchMap 和 runSolver）
- 修复 reset 函数未重置 loading 状态的问题
- 增强错误处理机制和用户提示
- 修复 hlOpacity 动画逻辑缺陷
- 为 RESET 按钮添加 disabled 属性
- 修复 link.target.sort() 副作用

## Impact
- Affected specs: `comprehensive-tacticalmap-testing`、`improve-tactical-map-visual`
- Affected code: `src/components/TacticalMap.jsx`

## ADDED Requirements

### Requirement: HTTP 状态检查
系统 SHALL 在所有 API 请求中检查 HTTP 响应状态。

#### Scenario: fetchMap HTTP 错误
- **WHEN** `/api/map_init` 返回非 200 状态码
- **THEN** 应抛出包含 HTTP 状态码和状态文本的错误
- **THEN** 错误应被 catch 块捕获并设置 loading 为 false
- **THEN** 应设置详细的错误日志

#### Scenario: runSolver HTTP 错误
- **WHEN** `/api/solver` 返回非 200 状态码
- **THEN** 应抛出包含 HTTP 状态码和状态文本的错误
- **THEN** 错误应被 catch 块捕获
- **THEN** 应设置 solverLogs 为详细的错误信息

### Requirement: 完整的重置功能
系统 SHALL 在重置时清空所有相关状态。

#### Scenario: Reset 操作包含 loading 重置
- **WHEN** 用户点击 RESET 按钮
- **THEN** 应将 loading 设置为 false
- **THEN** 应重置 solved、selectedLinks、solverLogs、focusedCourier

### Requirement: 增强的错误处理
系统 SHALL 提供详细且用户友好的错误信息。

#### Scenario: 网络错误
- **WHEN** API 请求因网络错误失败
- **THEN** 应设置包含具体错误类型的日志（如 "Network Error"、"Timeout"）
- **THEN** 应在用户界面上显示友好的错误提示

#### Scenario: 服务器错误
- **WHEN** API 返回 5xx 状态码
- **THEN** 应设置包含服务器错误信息的日志
- **THEN** 应提示用户稍后重试

## MODIFIED Requirements

### Requirement: hlOpacity 动画逻辑
**修改前**: hlOpacity 在 solved=true 时固定为 1
**修改后**: hlOpacity 应基于 selectedLinks.length 动态计算，支持平滑过渡

### Requirement: RESET 按钮状态
**修改前**: 按钮无 disabled 属性
**修改后**: 应添加 disabled={solving} 属性

### Requirement: link.target 去重逻辑
**修改前**: 直接调用 link.target.sort() 修改原数组
**修改后**: 使用 [...link.target].sort() 创建副本后再排序

## REMOVED Requirements
（无）

## 技术实现方案

### 修复 1: HTTP 状态检查
```javascript
const r = await fetch(`${apiBase}/api/map_init`);
if (!r.ok) {
  throw new Error(`HTTP ${r.status}: ${r.statusText}`);
}
const data = await r.json();
```

### 修复 2: 完整的 reset 函数
```javascript
const reset = () => {
  setSolved(false);
  setSelectedLinks([]);
  setSolverLogs([]);
  setFocusedCourier(null);
  setLoading(false); // 添加此行
};
```

### 修复 3: hlOpacity 动画
```javascript
const { bgOpacity, hlOpacity, animDelay } = useMemo(() => ({
  bgOpacity: solved ? 0 : 0.02,
  hlOpacity: selectedLinks.length > 0 ? 1 : 0, // 改为基于选中链路
  animDelay: solved && selectedLinks.length > 0 ? '200ms' : '0ms',
}), [solved, selectedLinks]);
```

### 修复 4: RESET 按钮
```javascript
<button onClick={reset} disabled={solving} ...>
```

### 修复 5: link.target 去重
```javascript
const key = `${link.source}-${[...link.target].sort().join(',')}`;
```
