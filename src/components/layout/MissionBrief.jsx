import React from 'react';
import AnimatedHeading from '../atoms/AnimatedHeading';
import FadeIn from '../atoms/FadeIn';
import DataUploader from '../DataUploader';

export default function MissionBrief({ onInitiate, executing, datasetLoaded, onDatasetLoaded }) {
  const canStart = datasetLoaded && !executing;

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
            <button className="rounded-lg border border-white/15 bg-white/5 px-7 py-3 text-sm font-medium text-white/70 transition-colors hover:text-white hover:border-white/30">
              调度算法说明  ›
            </button>
          </div>
        </div>
      </FadeIn>
    </div>
  );
}
