import React, { useState } from 'react';
import AnimatedHeading from '../atoms/AnimatedHeading';
import FadeIn from '../atoms/FadeIn';
import DataUploader from '../DataUploader';

function AlgorithmModal({ open, onClose }) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-2xl max-h-[80vh] overflow-y-auto rounded-xl border border-white/15 bg-[#0a0a0a]/95 p-6 md:p-8 shadow-2xl"
        style={{ boxShadow: "0 0 40px rgba(255,208,0,0.08)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-medium text-[#FFD000] tracking-wide">
            ◈ 调度算法说明
          </h2>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white transition-colors text-lg"
          >
            ✕
          </button>
        </div>

        <div className="space-y-5 text-sm text-white/70 leading-relaxed">
          <section>
            <h3 className="text-white font-medium mb-2 text-base">1. 核心调度算法</h3>
            <p>
              本引擎采用 <span className="text-[#FFD000]">贪心启发式 + 局部搜索 + OR-Tools CP-SAT</span> 三层递进求解策略：
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/60">
              <li><b className="text-white/80">贪心阶段</b>：基于最短配送距离优先分配订单，快速生成可行解</li>
              <li><b className="text-white/80">局部搜索</b>：通过 2-opt、订单交换、路径重组等邻域操作迭代优化</li>
              <li><b className="text-white/80">CP-SAT 精算</b>：当问题规模较小时，调用 Google OR-Tools 求解全局最优</li>
            </ul>
          </section>

          <section>
            <h3 className="text-white font-medium mb-2 text-base">2. 多智能体协同框架</h3>
            <p>
              系统由 <span className="text-[#FFD000]">5 个专业 Agent</span> 协同工作：
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/60">
              <li><b className="text-white/80">路由 Agent</b>：负责订单-骑手匹配与路径规划</li>
              <li><b className="text-white/80">库存 Agent</b>：监控商家出餐状态与餐品可用性</li>
              <li><b className="text-white/80">调度 Agent</b>：全局运力平衡与动态再调度</li>
              <li><b className="text-white/80">安全 Agent</b>：超时风险预警与异常订单拦截</li>
              <li><b className="text-white/80">稳定 Agent</b>：配送时效稳定性保障与回退策略</li>
            </ul>
          </section>

          <section>
            <h3 className="text-white font-medium mb-2 text-base">3. 求解引擎工作流程</h3>
            <ol className="list-decimal list-inside mt-2 space-y-1 text-white/60">
              <li>解析 Seed301 数据 → 构建骑手-订单-商家三元图</li>
              <li>元 Agent 分析订单特征 → 生成调度策略建议</li>
              <li>求解引擎执行贪心 + 局部搜索 → 生成初始方案</li>
              <li>若启用 LLM → 调用 DeepSeek/MiniMax 进行策略增强</li>
              <li>输出派单序列 → 可视化战术地图呈现</li>
            </ol>
          </section>

          <section>
            <h3 className="text-white font-medium mb-2 text-base">4. 性能指标</h3>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-[#FFD000] text-lg font-medium">~50ms</div>
                <div className="text-white/50 text-xs">单次求解延迟</div>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-[#FFD000] text-lg font-medium">1000+</div>
                <div className="text-white/50 text-xs">并发订单处理</div>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-[#FFD000] text-lg font-medium">&lt;3%</div>
                <div className="text-white/50 text-xs">超时率控制</div>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-[#FFD000] text-lg font-medium">15%</div>
                <div className="text-white/50 text-xs">平均路径优化</div>
              </div>
            </div>
          </section>
        </div>

        <div className="mt-6 pt-4 border-t border-white/10 text-center">
          <button
            onClick={onClose}
            className="rounded-lg border border-[#FFD000]/50 bg-[#FFD000]/10 px-6 py-2 text-sm font-medium text-[#FFD000] transition-colors hover:bg-[#FFD000]/20"
          >
            了解完毕 ›
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MissionBrief({ onInitiate, executing, datasetLoaded, onDatasetLoaded }) {
  const canStart = datasetLoaded && !executing;
  const [showAlgoModal, setShowAlgoModal] = useState(false);

  return (
    <div>
      <AnimatedHeading
        text={"云网协同推演 · 空间运力聚合引擎"}
        className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4"
        style={{ letterSpacing: "-0.04em" }}
      />

      <FadeIn delay={800} duration={1000}>
        <p className="text-base md:text-lg text-white/60 mb-2 max-w-xl">
          多智能体协同 · 为即时配送而生的 AI 调度引擎
        </p>
        <p className="text-sm md:text-base text-white/40 mb-6 max-w-xl">
          毫秒级决策 · 千单级并发 · 全链路可追溯
        </p>
      </FadeIn>

      <FadeIn delay={1200} duration={1000}>
        <div className="inline-flex flex-col gap-4">
          <DataUploader onLoaded={onDatasetLoaded} />

          <div className="flex flex-wrap gap-4">
            <button
              onClick={onInitiate}
              disabled={!canStart}
              className={`rounded-lg border px-7 py-3 text-sm font-medium transition-all duration-300 ${
                canStart
                  ? "border-[#FFD000] bg-transparent text-[#FFD000] hover:bg-[#FFD000]/20"
                  : "border-white/15 bg-white/5 text-white/30 cursor-not-allowed"
              }`}
              style={{
                boxShadow: canStart ? "0 0 20px rgba(255,208,0,0.1), 0 0 40px rgba(255,208,0,0.05)" : "none"
              }}
            >
              {executing ? "[ 全息推演中... ]" : "[ 启动云端全息推演 ]"}
            </button>
            <button
              onClick={() => setShowAlgoModal(true)}
              className="rounded-lg border border-white/15 bg-white/5 px-7 py-3 text-sm font-medium text-white/70 transition-colors hover:text-white hover:border-white/30"
            >
              调度算法说明  ›
            </button>
          </div>
        </div>
      </FadeIn>

      <AlgorithmModal open={showAlgoModal} onClose={() => setShowAlgoModal(false)} />
    </div>
  );
}
