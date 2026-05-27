# 战术地图视觉重构 Spec

## Why
当前 TacticalMap 存在三个严重的视觉问题：
1. **链路噪音严重**：175 条链路全部以相同透明度显示，背景层和激活层没有层级感，用户无法区分哪些是候选连接、哪些是最优解
2. **节点重复渲染**：相同 ID 的 Task/Courier 被重复渲染（原始数据中存在多行相同的 courier_id→task_ids 组合）
3. **空间布局拥挤**：节点坐标分布在 [0,100] 区间，但 SVG 固定 800×600，导致点集中在左上角

## What Changes
- 修改 `src/components/TacticalMap.jsx` 的链路渲染逻辑（背景层 vs 高亮层）
- 修改节点渲染逻辑（去重 + 新形状）
- 实现空间自适应 viewBox 计算
- 实现点击骑手的链路聚焦交互
- 实现 EXECUTE 后链路"淡出→生长"的动画效果

## Impact
- Affected specs: 无（新增视觉增强，不影响 API 契约）
- Affected code: `src/components/TacticalMap.jsx`（核心重写）、`backend/data_service.py`（solver 返回结果格式）

## ADDED Requirements

### Requirement: 链路去噪
系统 SHALL 实现链路的两层视觉设计。

- **背景层**：所有原始链路，stroke-width 为 0.5px，stroke-opacity 为 0.02，颜色为 `#737373`，始终显示
- **高亮层**：仅当 `isSelected === true`（算法选中的方案）时，连线显示为 `#FFD000`，stroke-width 为 2px，并添加 `drop-shadow` 发光滤镜

#### Scenario: Solver 执行前
- **WHEN** 用户尚未点击 EXECUTE SOLVER
- **THEN** 所有链路以背景层样式显示（极淡细线）

#### Scenario: Solver 执行后
- **WHEN** 用户点击 EXECUTE SOLVER，solver 返回 selected 数组
- **THEN** 背景链路淡出（opacity → 0），高亮链路从骑手端点向任务端点"生长"出来

### Requirement: 节点去重与形状区分
系统 SHALL 对节点进行去重，并以不同形状区分类型。

- **去重**：使用 `Map<string, Node>` 按 ID 唯一化节点，每个 ID 仅渲染一次
- **Task 节点**：实心圆点，半径 5px，填充色 `#EDEDED`，悬停时显示 ID 标签
- **Courier 节点**：空心方块，边长 8px，边框色 `#737373`，悬停时显示 ID 标签

#### Scenario: 节点去重验证
- **WHEN** 原始数据中存在重复的 TaskID（如 `T0037` 出现在多行）
- **THEN** 该 Task 节点仅渲染一个

### Requirement: 空间自适应 viewBox
系统 SHALL 根据节点坐标范围自动调整 SVG viewBox。

- 计算所有节点的 Xmin、Xmax、Ymin、Ymax
- viewBox 范围 = [Xmin - padding, Xmax + padding]，其中 padding = (max - min) × 10%
- SVG 尺寸固定为 800×600（由容器 CSS 控制），但 viewBox 动态计算

#### Scenario: 坐标范围计算
- **WHEN** TaskID 坐标在 [20, 80]，CourierID 坐标在 [0, 100]
- **THEN** Xmin=0, Xmax=100, Ymin=0, Ymax=100，viewBox 动态调整为适合该范围的宽高比

### Requirement: 动态链路聚焦
系统 SHALL 实现点击骑手时的链路聚焦交互。

- **WHEN** 用户点击 Courier 节点
- **THEN** 该 Courier 对应的所有候选链路以 opacity-30 的蓝色 `#60A5FA` 高亮，其余链路隐藏（opacity-0）
- **WHEN** 用户再次点击同一 Courier 节点或空白区域
- **THEN** 恢复显示所有背景链路

#### Scenario: 点击骑手节点
- **WHEN** Courier `C037` 被点击
- **THEN** `C037` 的所有候选链路（无论是否被 solver 选中）以蓝色高亮

### Requirement: 链路生长动画
系统 SHALL 在 solver 执行后实现链路"生长"动画。

- **WHEN** solver 返回结果，solving → solved
- **THEN** 背景链路在 800ms 内 opacity 从 0.02 过渡到 0
- **THEN** 高亮链路从 0 生长到完整长度，持续 600ms，延迟 200ms 开始

## MODIFIED Requirements

### Requirement: TacticalMap props
- 新增 `onBack` prop（可选）：返回按钮回调，不传则不显示返回按钮

### Requirement: Solver API 格式
solver 返回格式不变，但前端需正确使用 `selected` 数组中的 `source` 和 `target` 字段判断链路是否被选中。

## REMOVED Requirements
（无）
