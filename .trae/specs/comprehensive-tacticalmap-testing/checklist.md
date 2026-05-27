# Checklist - TacticalMap 全面功能测试

## 地图初始化功能 ⚠️
- [x] 组件挂载时发送 GET 请求到 `${apiBase}/api/map_init`
- [x] 正确解析并设置 nodes 状态（使用 Map 去重）
- [x] 正确解析并设置 links 状态
- [x] Loading 状态正确从 true 变为 false
- [x] API 失败时正确捕获错误，loading 设为 false
- [x] API 失败不导致应用崩溃
- [ ] **HTTP 状态检查缺失** ⚠️ - 未检查 r.ok 或 r.status

## 节点去重和过滤 ✅
- [x] 使用 Map 按 ID 唯一化节点
- [x] 每个节点 ID 仅渲染一次
- [x] 正确过滤 type === 'task' 的节点
- [x] Task 节点显示为实心圆点（circle, r=5, fill=#EDEDED）
- [x] 正确过滤 type === 'courier' 的节点
- [x] Courier 节点显示为空心方块（rect 8×8, fill=none, stroke=#737373）

## Solver 执行功能 ⚠️
- [x] 点击 EXECUTE SOLVER 按钮发送请求到 `${apiBase}/api/solver`
- [x] 请求期间 solving 状态为 true
- [x] 正确解析 selected 和 logs 数据
- [x] 执行成功后 solved 状态为 true
- [x] selectedLinks 状态正确更新
- [x] solverLogs 状态正确更新
- [x] Solver 请求失败时设置错误日志 ['[ERROR] Solver request failed']
- [x] Solver 请求失败后 solving 状态为 false
- [x] Solver 请求失败不导致崩溃
- [ ] **HTTP 状态检查缺失** ⚠️ - 未检查 r.ok 或 r.status

## 重置功能 ⚠️
- [x] 点击 RESET 按钮后 solved 状态为 false
- [x] selectedLinks 数组被清空
- [x] solverLogs 数组被清空
- [x] focusedCourier 状态为 null
- [ ] **loading 状态未重置** ❌ - 如果初始化失败无法重新加载地图

## 链路聚焦功能 ✅
- [x] 点击 Courier 节点时 focusedCourier 状态更新
- [x] 点击的 Courier 节点所有链路显示为蓝色（#60A5FA）
- [x] 其他链路在聚焦时隐藏或降低透明度
- [x] 再次点击同一 Courier 节点时聚焦取消
- [x] focusedCourier 重置为 null

## 悬停交互 ✅
- [x] Task 节点悬停时显示 ID 标签
- [x] 标签位置正确（右侧偏移）
- [x] Courier 节点悬停时显示 ID 标签
- [x] 移出节点后 hoveredId 状态清除
- [x] 标签正确隐藏
- [ ] **建议**: Courier 悬停时可显示更多信息（如 assigned 任务数量）💡

## 视觉渲染 ⚠️
- [x] viewBox 根据节点坐标动态计算
- [x] viewBox 包含 10% 的 padding
- [x] 未选中链路 stroke-width 为 0.5
- [x] 未选中链路 stroke-opacity 为 0.02
- [x] 未选中链路颜色为 #737373
- [x] 选中链路 stroke 为 #FFD000
- [x] 选中链路 stroke-width 为 2
- [x] 选中链路应用 drop-shadow 滤镜
- [x] 背景链路淡出动画（800ms ease-out）
- [x] 高亮链路淡入动画（600ms ease-out, delay=200ms）
- [ ] **hlOpacity 动画缺陷** ⚠️ - solved=true 时 hlOpacity 固定为 1，动画无法产生视觉效果

## 按钮状态 ⚠️
- [x] 执行中（solving=true）时 EXECUTE SOLVER 按钮禁用
- [x] 加载中（loading=true）时 EXECUTE SOLVER 按钮禁用
- [x] 执行中按钮显示 "SOLVING..."
- [x] 执行完成后显示 RESET 按钮
- [x] 按钮样式符合设计规范
- [ ] **RESET 按钮缺少 disabled** ⚠️ - 用户可在 solving=true 时点击 RESET

## 错误处理 ❌
- [x] 网络错误被正确捕获 ⚠️ - 捕获了错误但未检查 HTTP 状态
- [x] 数据格式异常被安全处理 ⚠️ - 使用了可选链但仍可能抛出异常
- [x] 不抛出未捕获的异常 ⚠️ - 基础异常被捕获但缺少详细错误信息
- [x] try-catch 块正确使用 ⚠️ - try-catch 存在但错误处理不够完善
- [ ] **缺少详细的错误日志** ❌ - 错误信息不够详细，无法定位问题
- [ ] **缺少用户界面错误提示** ❌ - 用户完全不知道发生了什么

## 依赖注入 ✅
- [x] 自定义 apiBase prop 生效
- [x] 默认 apiBase 为 'http://localhost:8080'
- [x] 传入 onBack prop 时显示返回按钮
- [x] 未传入 onBack prop 时不显示返回按钮

## 集成测试 ⚠️
- [x] 完整流程：加载 → 执行 Solver → 查看结果 → 重置 ⚠️
  - **发现**: TacticalMap 组件当前未被 App.jsx 使用
- [x] App 组件正确使用 TacticalMap 组件 ❌
  - **问题**: App.jsx 使用的是 SolutionTerminal 组件，而非 TacticalMap
- [ ] 状态在组件间正确传递 ⚠️
  - TacticalMap 独立测试通过，但未集成到主应用
- [ ] 无运行时错误 ⚠️
  - TacticalMap 代码本身无运行时错误，但未在主应用中测试
- [ ] 无控制台错误 ⚠️
  - TacticalMap 代码本身无控制台错误，但未在主应用中测试

## 视觉和交互 ⚠️
- [x] 网格背景正确渲染
- [x] 坐标系正确显示
- [ ] 动画流畅无卡顿 ⚠️ - hlOpacity 动画逻辑有问题
- [x] 响应式布局正常
- [x] 加载状态正确显示

## 测试结果汇总
- ✅ 完全通过: 6 项
  - 节点去重和过滤
  - 链路聚焦功能
  - 悬停交互
  - 依赖注入功能
  - 网格背景渲染
  - 坐标系显示
- ⚠️ 部分通过（含缺陷）: 5 项
  - 地图初始化功能（缺少 HTTP 状态检查）
  - Solver 执行功能（缺少 HTTP 状态检查）
  - 重置功能（未重置 loading 状态）
  - 视觉渲染（hlOpacity 动画缺陷）
  - 按钮状态（RESET 按钮缺少 disabled）
- ❌ 未通过: 1 项
  - 错误处理机制（问题严重）
- ⚠️ 集成测试: TacticalMap 组件未被主应用使用

## 发现的问题
### 🔴 高优先级问题（必须修复）
1. **缺少 HTTP 状态检查** - fetchMap 和 runSolver 函数未检查 r.ok 或 r.status
2. **reset 函数未重置 loading 状态** - 如果初始化失败无法重新加载地图
3. **错误处理不完善** - 缺少用户提示，错误信息不够详细

### 🟡 中优先级问题（建议修复）
4. **hlOpacity 动画逻辑缺陷** - solved=true 时 hlOpacity 固定为 1，动画无法产生视觉效果
5. **RESET 按钮缺少 disabled 属性** - 用户可在 solving=true 时点击 RESET
6. **link.target.sort() 副作用** - 直接修改原数组，可能影响数据完整性

### 💡 优化建议
7. **组件集成问题** - TacticalMap 组件未被 App.jsx 使用，当前使用的是 SolutionTerminal 组件
8. **扩展信息显示** - Courier 悬停时可显示更多信息（如 assigned 任务数量）
9. **添加用户界面错误提示** - Toast/Snackbar 等组件

