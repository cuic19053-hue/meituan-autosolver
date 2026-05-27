# Tasks

- [x] Task 1: 重构 TacticalMap.jsx 链路渲染逻辑
  - [x] SubTask 1.1: 将链路分为背景层（stroke-width=0.5, opacity=0.02）和高亮层（#FFD000, stroke-width=2, drop-shadow）
  - [x] SubTask 1.2: 实现背景链路在 solver 后淡出（opacity 0.02→0，800ms）
  - [x] SubTask 1.3: 实现高亮链路"生长"动画（opacity 0→1，600ms，delay=200ms）

- [x] Task 2: 重构节点渲染逻辑
  - [x] SubTask 2.1: 使用 Map 对节点按 ID 去重
  - [x] SubTask 2.2: Task 节点改为实心圆点（r=5, fill=#EDEDED）
  - [x] SubTask 2.3: Courier 节点改为空心方块（rect 8×8, fill=none, stroke=#737373）
  - [x] SubTask 2.4: 悬停时显示 ID 标签（保持现有行为）

- [x] Task 3: 实现空间自适应 viewBox
  - [x] SubTask 3.1: 计算所有节点的 Xmin/Xmax/Ymin/Ymax
  - [x] SubTask 3.2: 根据范围计算动态 viewBox（加 10% padding）
  - [x] SubTask 3.3: SVG width/height 由 CSS 固定 600×600，viewBox 动态

- [x] Task 4: 实现点击骑手链路线性聚焦
  - [x] SubTask 4.1: 添加 focusedCourier state 追踪当前点击的 CourierID
  - [x] SubTask 4.2: 点击 Courier 节点时，filteredLinks 只显示该 Courier 的链路（#60A5FA, opacity=0.3），其余隐藏
  - [x] SubTask 4.3: 再次点击同一 Courier 或空白区域时，恢复显示所有背景链路

# Task Dependencies
- Task 2, 3, 4 可并行执行（均基于 TacticalMap 重构）
- Task 1 可与 Task 2, 3, 4 并行执行
