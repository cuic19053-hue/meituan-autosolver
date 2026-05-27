# Tasks

- [x] Task 1: 升级 `backend/data_service.py` 的 `solve()` 函数
  - [x] SubTask 1.1: 为所有日志添加 `[HH:MM:SS]` 时间戳前缀
  - [x] SubTask 1.2: 增加 `[CONFLICT #N]` 格式标签（N 为冲突序号）
  - [x] SubTask 1.3: 增加 `[REFLECTION]` 标签用于描述重分配决策
  - [x] SubTask 1.4: 增加 `[EFFICIENCY]` 标签用于描述效率评估
  - [x] SubTask 1.5: 增加 `[WARN]` 标签用于低分方案跳过

- [x] Task 2: 升级 `src/components/TacticalMap.jsx` 视觉效果
  - [x] SubTask 2.1: 将网格从 10px 改为 50px 间距，添加渐变边缘暗化效果
  - [x] SubTask 2.2: 任务节点改为圆环（stroke circle，fill transparent）
  - [x] SubTask 2.3: 骑手节点改为三角形 + CSS 呼吸灯动画（2s 周期 opacity 0.4~1.0）
  - [x] SubTask 2.4: 初始链路 opacity 改为 0.1（原 0.02）
  - [x] SubTask 2.5: 高亮链路添加 CSS `@keyframes` 流光动画（stroke-dashoffset 循环）

- [x] Task 3: 新建 `src/components/ReflectionConsole.jsx`
  - [x] SubTask 3.1: 创建组件框架（props: logs, onClose, stats）
  - [x] SubTask 3.2: 实现日志行颜色分类（ASSIGN/CONFLICT/REFLECTION/SKIP/WARN）
  - [x] SubTask 3.3: 实现 50ms 间隔 typewriter 逐行展示效果
  - [x] SubTask 3.4: 实现底部统计栏（已分配/冲突数/总得分）
  - [x] SubTask 3.5: 美团工业风格样式（bg-black/70, border-[#262626], backdrop-blur）

- [x] Task 4: 修改 `src/App.jsx` 集成 TacticalMap + ReflectionConsole
  - [x] SubTask 4.1: 移除 SolutionTerminal 独占显示逻辑
  - [x] SubTask 4.2: 卡片区域改为水平布局：左侧 TacticalMap，右侧 ReflectionConsole
  - [x] SubTask 4.3: TacticalMap 执行后 ReflectionConsole 接收并展示 solver 日志
  - [x] SubTask 4.4: TacticalMap 执行后 ReflectionConsole 接收并展示 solver 日志

- [x] Task 5: 验证与调试
  - [x] SubTask 5.1: 运行 Vite 编译，确认无错误
  - [x] SubTask 5.2: 启动后端服务，确认 `/api/map_init` 返回正确数据
  - [x] SubTask 5.3: 启动前端，确认 TacticalMap 正常加载
  - [x] SubTask 5.4: 点击 EXECUTE SOLVER，确认 ReflectionConsole 显示日志，TacticalMap 高亮链路

# Task Dependencies
- Task 1 independent
- Task 2 independent
- Task 3 independent
- Task 4 depends on Task 2 and Task 3
- Task 5 depends on Task 4
