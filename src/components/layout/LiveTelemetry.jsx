import React from 'react';
import Sparkline from '../atoms/Sparkline';

export default function LiveTelemetry({ kpi }) {
  const syncTime = new Date().toLocaleTimeString("en-GB", { hour12: false });

  return (
    <div
      className="rounded-xl border border-white/10 bg-white/5 px-5 py-4 w-full max-w-sm"
      style={{ backdropFilter: "blur(14px)", WebkitBackdropFilter: "blur(14px)" }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/40">
            时空拓扑遥测矩阵
          </span>
          <span className="font-mono text-[9px] uppercase tracking-wider text-white/30">
            已同步 {syncTime}
          </span>
        </div>
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00FF41] opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#00FF41]" />
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex items-baseline justify-between border-b border-white/10 pb-2">
          <span className="text-xs text-white/60">效用增益</span>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-2xl font-semibold tabular-nums" style={{ color: "#FFD000" }}>
              {kpi?.efficiency_gain ?? "--"}
            </span>
            <span className="self-end mb-1"><Sparkline /></span>
            <span className="font-mono text-[10px] tabular-nums" style={{ color: "#00FF41" }}>
              {kpi?.completion_rate ? `${kpi.completion_rate} ↑` : "--"}
            </span>
          </div>
        </div>
        <div className="flex items-baseline justify-between border-b border-white/10 pb-2">
          <span className="text-xs text-white/60">调度完成率</span>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-lg font-medium text-white tabular-nums">
              {kpi?.completion_rate ?? "--"}
            </span>
            <span className="font-mono text-[10px] text-white/40 tabular-nums">完成率</span>
          </div>
        </div>
        <div className="flex items-baseline justify-between">
          <span className="text-xs text-white/60">运算耗时</span>
          <span className="font-mono text-sm tabular-nums" style={{ color: "#00FF41" }}>
            {kpi?.latency ?? "--"}
          </span>
        </div>
      </div>
    </div>
  );
}
