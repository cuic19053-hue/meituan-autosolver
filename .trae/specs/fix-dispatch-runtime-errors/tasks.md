# Tasks

- [x] Task 1: 修复 SolutionTerminal.jsx 三个状态管理 Bug
  - [x] Bug 1: 在 useEffect 开头（`if (externalResult)` 分支内）添加 `setIsFinished(false)` 和 `setDisplayCount(0)`
  - [x] Bug 2: 在 useEffect 中添加 `else` 分支，当 `externalResult` 为 null 且 `apiBase` 为 null 时，重置 `setData(null)`、`setDisplayCount(0)`、`setIsFinished(false)`、`setShowDebrief(false)`
  - [x] Bug 3: 在 `handleReset` 函数中添加 `setData(null)`、`setDisplayCount(0)`、`setIsFinished(false)`

# Task Dependencies
- 无依赖，单文件修复