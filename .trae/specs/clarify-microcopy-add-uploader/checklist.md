# Checklist

## 微文案替换
- [x] 品牌栏：AutoSolver | 智能配送调度中枢
- [x] Slogan：运力聚合 · 智能派单
- [x] 副标题：多智能体协同 · 为即时配送而生的 AI 调度引擎
- [x] 副描述：毫秒级决策 · 千单级并发 · 全链路可追溯
- [x] 数据面板标题：// 实时调度大盘
- [x] 指标1：待派发订单
- [x] 指标2：在线骑手运力
- [x] 指标2单位：骑手
- [x] 指标3：算法运算耗时
- [x] 终端初始化：> [系统] 正在连接 AI 调度引擎...
- [x] 终端覆盖前缀：[站长接管]
- [x] 终端确认前缀：[AI 派单]
- [x] 结算标题：调度效果评估报告
- [x] 结算指标：预估效用提升 / 派单完成率 / 算法运算耗时
- [x] CTA 按钮：[ 启动 AI 调度 ]
- [x] CTA loading：[ 调度执行中... ]
- [x] 副按钮：调度算法说明 ›
- [x] 终端行格式：订单 T0037 → 骑手 C028
- [x] 终端底栏：派单行 / 效用值 / 派单率 / 执行进度
- [x] 终端状态：派单中 / 派单完成
- [x] 导航：调度概览 / 运力监控 / 效能分析
- [x] 状态栏：调度系统 · 运行中
- [x] 结算状态：调度系统 · 正常
- [x] 终端重置：[重置日志]
- [x] 结算确认：[确认报告]

## DataUploader 组件
- [x] 虚线边框 border-dashed border-white/20
- [x] 背景 bg-white/5 backdrop-blur-sm rounded-lg
- [x] 默认态文字：[ 拖拽或点击上传测试数据集 (.txt / .csv) ]
- [x] 云端上传图标 (Upload from lucide-react)
- [x] 成功态：绿色边框 + 成功文字
- [x] 成功文字：[系统] 成功读取：large_seed301.txt (识别到 301 条待派单数据)
- [x] onClick 触发 setDatasetLoaded(true)

## 按钮防呆锁定
- [x] datasetLoaded=false → 按钮灰色 disabled
- [x] datasetLoaded=true → 按钮美团黄 #FFD000 可点击
- [x] App.jsx 新增 datasetLoaded 状态
- [x] MissionBrief 接收 datasetLoaded prop

## 验证
- [x] npm run build 无错误（exit code 0, 348KB JS + 21KB CSS）
